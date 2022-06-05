# students serializers!

from rest_framework import serializers
from rest_framework import fields

from core.models import Subject
from core.constants import SUBJECTS
from .models import Student
from core.models import Class

class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        depth = 1
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
                    rev_social_catergories = {v: k for k, v in dict(Student.SOCIAL_CATEGORIES).items()}
                    social_cat = dict(rev_social_catergories)[data['social_category']]
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

        if 'minority' in data:
            if data['minority'] not in dict(Student.MINORITIES).keys():
                if data['minority'] in dict(Student.MINORITIES).values():
                    rev_minorities = {v: k for k, v in dict(Student.MINORITIES).items()}
                    minority = dict(rev_minorities)[data['minority']]
                else:
                    errors['minority'] = {
                        'value': data['minority'],
                        'message': f'Invalid Minority value recieved',
                        'choices': list(set(list(dict(Student.MINORITIES).values()) + list(dict(Student.MINORITIES).keys())))
                    }
            else:
                minority = dict(Student.MINORITIES)[data['minority']]

        clean_subjects = []
        if 'optional_subjects_opted' in data:
            for sub in data['optional_subjects_opted']:
                if sub not in dict(SUBJECTS).keys():
                    if sub in dict(SUBJECTS).values():
                        rev_subjects = {v: k for k, v in dict(Student.MINORITIES).items()}
                        _subject = rev_subjects[sub]
                        clean_subjects.append(Subject.objects.get(subject_name=_subject).pk)
                    else:
                        errors['optional_subjects_opted'] = {
                        'value': sub,
                        'message': f'Invalid Subject value recieved',
                        'choices': list(set(list(dict(SUBJECTS).values()) + list(dict(SUBJECTS).keys())))
                    }
                else:
                    clean_subjects.append(Subject.objects.get(subject_name=dict(SUBJECTS)[sub]).pk)

        if errors:
            raise serializers.ValidationError({'status': 400, 'errors': errors})

        if 'cls' in data:
            dat[1]['cls'] = cls
        if 'social_category' in data:
            dat[1]['social_category'] = social_cat
        if 'minority' in data:
            dat[1]['minority'] = minority
        if 'optional_subjects_opted' in data:
            dat[1]['optional_subjects_opted'] = clean_subjects

        return dat

    def to_representation(self, instance: Student):
        rep = super().to_representation(instance)
        rep['cls'] = instance.cls.cls
        rep['section'] = instance.cls.section
        rep['stream'] = instance.cls.stream
        rep['social_category'] = dict(instance.SOCIAL_CATEGORIES)[instance.social_category]
        rep['minorty'] = dict(instance.MINORITIES)[instance.minority]
        rep.move_to_end(key='optional_subjects_opted')
        return rep