# exams serializers!

from rest_framework import serializers
from .models import Exam, Result, Marks
from .constants import EXAM_TYPES

class ExamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Exam
        fields = '__all__'

    def to_representation(self, instance: Exam):
        rep = super().to_representation(instance)
        rep['exam_name'] = dict(EXAM_TYPES)[instance.exam_name]
        rep['cls'] = instance.cls.cls

        results = []
        for result in instance.result_set.get_queryset():
            results.append(ResultSerializer(result).data)

        rep['results'] = results

        return rep

class ResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = Result
        fields = '__all__'

    def to_representation(self, instance: Result):
        rep = super().to_representation(instance)

        del rep['exam']
        rep['exam_id'] = instance.exam.pk

        del rep['student']
        rep['student_name'] = instance.student.student_name
        rep['student_roll'] = instance.student.roll
        rep['student_uid'] = instance.student.uid

        marks = []
        for mark in instance.marks_set.get_queryset():
            marks.append(MarkSerializer(mark).data)

        rep['marks'] = marks
        
        return rep

class MarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Marks
        fields = '__all__'

    def to_representation(self, instance: Marks):
        rep = super().to_representation(instance)

        del rep['result']
        rep['result_id '] = instance.result.pk

        del rep['subject']
        rep['subject_id'] = instance.subject.pk
        rep['subject'] = instance.subject.get_subject_name_display()

        rep.move_to_end('marks_ob')

        return rep