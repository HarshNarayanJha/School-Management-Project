import django
from django.db import models
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

from students.models import Student, Teacher
from students.models import SUBJECTS, CLASSES

EXAM_TYPES = (
    ("PT-1", "Periodic Test - 1"),
    ("T-1", "Term - 1 Examination"),
    ("PT-2", "Periodic Test - 2"),
    ("T-2", "Term - 2 Examination"),
)

class Exam(models.Model):
    exam_name = models.CharField("Exam Name", max_length=50, choices=EXAM_TYPES, help_text="Select the type of exam from the dropdown.")
    session_regex = RegexValidator(r'^20\d{2}-20\d{2}$', "should be in the format 20XX-20XX")
    session = models.CharField("Exam Session", max_length=10, validators=[session_regex], help_text="Session of the exam. like 2021-2022")
    cls = models.CharField("Exam of Class", max_length=4, choices=CLASSES, help_text="The class of which the exam is held. \
                                                                                    This will be pre-filled with your class if you are a class teacher.")

    def __str__(self) -> str:
        return f"{self.exam_name} ({self.session}) Class {self.cls}"

    def display_exam_name(self) -> str:
        return dict(EXAM_TYPES)[self.exam_name]

class ResultManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("student__roll")

class Result(models.Model):
    exam = models.ForeignKey(to=Exam, null=True, on_delete=models.CASCADE)
    student = models.ForeignKey(to=Student, on_delete=models.CASCADE)#, limit_choices_to={'cls': exam.related_model.cls})

    objects = ResultManager()

    def __str__(self) -> str:
        return f"{self.student.student_name} (Roll: {self.student.roll})"

class Marks(models.Model):
    class Meta:
        verbose_name = "Mark"
        verbose_name_plural = "Marks"

    subject = models.CharField("Subject", max_length=20, choices=SUBJECTS)
    marks_ob = models.IntegerField("Marks Obtained", help_text="Marks obtained in the subject", null=True, blank=True)
    marks_mx = models.IntegerField("Maximum Marks", help_text="Maximum marks in the subject", null=True, blank=True)

    result = models.ForeignKey(to=Result, null=True, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.subject}: {self.marks_ob} / {self.marks_mx}"

    def display_subject_name(self) -> str:
        return dict(SUBJECTS)[self.subject]

@receiver(post_save, sender=Student)
def student_created(sender, instance, created, **kwargs):
    if created:
        exams = Exam.objects.filter(cls=instance.cls)
        for exam in exams:
            result: Result = exam.result_set.create(student=instance)
            for subject, subject_display in SUBJECTS:
                mark: Marks = result.marks_set.create(subject=subject)