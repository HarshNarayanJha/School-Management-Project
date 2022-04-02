# students serializers!

from rest_framework import serializers
from rest_framework import fields

from exam.models import Subject
from .models import Student, Class, Teacher

class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = '__all__'

    def __init__(self, instance=None, data=fields.empty, **kwargs):
        self.bulk = kwargs.pop('bulk') if 'bulk' in kwargs else False
        super().__init__(instance, data, **kwargs)

    def validate_empty_values(self, data):
        dat = super().validate_empty_values(data)

        errors = {}
        cls = None
        social_cat = None

        if self.bulk:
            if 'uid' not in data:
                raise serializers.ValidationError({'status': 400, 'message': 'Student data is missing uid'})

            if Student.objects.filter(uid=data['uid']).exists():
               self.instance = Student.objects.get(uid=data['uid'])
               self.partial = True

        try:
            if 'cls' in data:
                cls = Class.objects.get(cls=data['cls']).pk
        except:
            errors['cls'] = {
                'value': data['cls'],
                'message': 'Invalid Class value recieved',
                'choices': list(dict(Class.CLASSES).values())
            }

        if 'social_category' in data:
            if data['social_category'] not in dict(Student.SOCIAL_CATEGORIES).keys():
                if data['social_category'] in dict(Student.SOCIAL_CATEGORIES).values():
                    _social_categories = []
                    for cat in Student.SOCIAL_CATEGORIES:
                        _social_categories.append(tuple(sorted(cat, reverse=True)))
                    _social_categories = tuple(_social_categories)
                    social_cat = dict(_social_categories)[data['social_category']]
                else:
                    errors['social_category'] = {
                        'value': data['social_category'],
                        'message': f'Invalid Social Category value recieved',
                        'choices': list(set(list(dict(Student.SOCIAL_CATEGORIES).values()) + list(dict(Student.SOCIAL_CATEGORIES).keys())))
                    }
            else:
                social_cat = dict(Student.SOCIAL_CATEGORIES)[data['social_category']]

        if 'admission_category' in data:
            if data['admission_category'] not in dict(Student.ADMISSION_CATEGORIES).values():
                errors['admission_category'] = {
                        'value': data['admission_category'],
                        'message': f'Invalid Admission Category value recieved',
                        'choices': list(dict(Student.ADMISSION_CATEGORIES).values())
                }

        if errors:
            raise serializers.ValidationError({'status': 400, 'errors': errors})

        if 'cls' in data:
            dat[1]['cls'] = cls
        if 'social_category' in data:
            dat[1]['social_category'] = social_cat

        return dat

    def to_representation(self, instance: Student):
        rep = super().to_representation(instance)
        rep['cls'] = instance.cls.cls
        rep['social_category'] = dict(instance.SOCIAL_CATEGORIES)[instance.social_category]
        return rep

class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Teacher
        fields = '__all__'

class ClassSerializer(serializers.ModelSerializer):

    class Meta:
        model = Class
        fields = '__all__'

    def to_internal_value(self, data):
        cls_subjects = data['subjects']
        cls_subjects_pks = []

        _subjects = []
        for _sub in Subject.SUBJECTS:
            _subjects.append(tuple(sorted(_sub, reverse=True)))
        _subjects = tuple(_subjects)

        for sub in cls_subjects:
            sub_code = dict(_subjects)[sub]
            cls_subjects_pks.append(Subject.objects.get(subject_name=sub_code).pk)

        del data['subjects']
        data['cls_subjects'] = cls_subjects_pks
        
        rep = super().to_internal_value(data)
        return rep

    def validate_empty_values(self, data):
        dat = super().validate_empty_values(data)
        if "cls_subjects" in data:
            for sub in data["cls_subjects"]:
                if sub not in dict(Subject.SUBJECTS).values():
                    print(sub)
                    raise serializers.ValidationError({'cls_subjects': f"{sub} is not a valid subject!"})
        
        return dat

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        cls_subjects = []
        for index in range(len(rep['cls_subjects'])):
            subject_name = list(instance.cls_subjects.iterator())[index].subject_name
            cls_subjects.append(dict(Subject.SUBJECTS)[subject_name])

        del rep['cls_subjects']
        rep["subjects"] = cls_subjects

        return rep