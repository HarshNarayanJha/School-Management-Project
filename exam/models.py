import django
from django.db import models
from django.core.validators import RegexValidator

from students.models import Student
from core.models import Class, Subject

class ExamSet(models.Model):
    name = models.CharField("Exam Set Name", max_length=20, null=True, blank=True)
    cls = models.CharField("Class", max_length=5, blank=False, null=False)

    def __str__(self) -> str:
        return f"{self.name} [Class {self.cls}]"

class ExamType(models.Model):
    exam_name = models.CharField("Exam Name", max_length=50, null=False, blank=False)
    exam_code = models.CharField("Exam Code", max_length=10, null=False, blank=False)
    weightage = models.PositiveSmallIntegerField("Weightage", null=False, blank=False)

    exam_set = models.ForeignKey(to=ExamSet, verbose_name="Exam Set", on_delete=models.RESTRICT)

    def __str__(self) -> str:
        return f"[{self.exam_code}] {self.exam_name}"

    @classmethod
    def get_all_exam_types(self) -> "list[tuple[int, str]]":
        return [(i.pk, str(i)) for i in ExamType.objects.all()]

class ExamManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("session", "cls")

class Exam(models.Model):
    exam_type = models.ForeignKey(to=ExamType, on_delete=models.PROTECT, verbose_name="Exam Type", help_text="Select the type of exam from the dropdown.", related_name='+')
    session_regex = RegexValidator(r'^20\d{2}-20\d{2}$', "should be in the format 20XX-20XX")
    session = models.CharField("Exam Session", max_length=10, validators=[session_regex], help_text="Session of the exam. like 2021-2022")
    cls = models.ForeignKey(to=Class, verbose_name="Class", on_delete=models.PROTECT, blank=False, null=False, help_text="The class of which the exam is held. This will be pre-filled with your class if you are a class teacher.")

    edited_by_class_teacher = models.BooleanField("Edited by Class Teacher", default=False, editable=False)

    objects = ExamManager()

    def __str__(self) -> str:
        return f"{self.exam_type} Examination ({self.session}) Class {self.cls}"

    def display_exam_name(self) -> str:
        return self.exam_type

    def get_calculated_result(self) -> "dict[str, float]":
        """
        Returns a dict of results with keys being the Student
        and the values being the percentage result, by `Result.get_calculated_result()`
        """
        results = {}
        for res in self.result_set.get_queryset():
            results[res.student] = res.get_calculated_result()
        
        return results

class ResultManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("student__roll")

class Result(models.Model):
    exam = models.ForeignKey(to=Exam, null=True, on_delete=models.CASCADE)
    student = models.ForeignKey(to=Student, on_delete=models.CASCADE)

    objects = ResultManager()

    def __str__(self) -> str:
        return f"Result: {self.student.student_name} (Class: {self.student.cls}, Roll: {self.student.roll}) [{self.exam.exam_type.exam_code} {self.exam.session}]"

    def get_marks_obtained(self) -> int:
        marks_got = 0
        for mark in self.marks_set.get_queryset():
            if mark.marks_ob:
                marks_got += mark.marks_ob
        return marks_got

    def get_maximum_marks(self) -> int:
        total = 0
        for mark in self.marks_set.get_queryset():
            if mark.marks_ob is not None:
                total += mark.marks_mx
        return total

    def get_calculated_result(self) -> float:
        return (self.get_marks_obtained() / self.get_maximum_marks()) * 100

class Marks(models.Model):
    class Meta:
        verbose_name = "Mark"
        verbose_name_plural = "Marks"

    subject = models.ForeignKey(to=Subject, verbose_name="Subject", on_delete=models.CASCADE)
    marks_ob = models.IntegerField("Marks Obtained", help_text="Marks obtained in the subject", null=True, blank=True)
    # marks_mx = models.IntegerField("Maximum Marks", help_text="Maximum marks in the subject", null=True, blank=True)

    result = models.ForeignKey(to=Result, null=True, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Marks: {self.subject}: ({self.marks_ob} / {40}) [{self.result.__str__().replace('Result: ', '')}]"

    # Temprorarily!
    @property
    def marks_mx(self):
        return 40