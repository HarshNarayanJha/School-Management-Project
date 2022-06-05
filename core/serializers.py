from rest_framework import serializers

from .models import Subject, Class, Teacher
from .constants import SUBJECTS

class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = '__all__'

    def to_representation(self, instance: Subject):
        rep = super().to_representation(instance)
        del rep['subject_name']
        rep['subject_code'] = instance.subject_name
        rep['subject_name'] = instance.get_subject_name_display()

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

        rev_subjects = {v: k for k, v in SUBJECTS.items()}
        for sub in cls_subjects:
            sub_code = dict(rev_subjects)[sub]
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