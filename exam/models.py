from django.db import models
from students.models import Student, Teacher
from students.models import SUBJECTS, CLASSES

class Exam(models.Model):
    name = models.CharField("Exam Name", max_length=50, help_text="Name of the exam, excluding the session.")
    session = models.CharField("Exam Session", max_length=10, help_text="Session of the exam. like 2021-22")
    cls = models.CharField("Exam of Class", max_length=4, choices=CLASSES, help_text="The class of which the exam is held. \
                                                                                    This will be pre-filled with your class if you are a class teacher.")

    def __str__(self) -> str:
        return f"{self.name} ({self.session}) Class {self.cls}"

class Result(models.Model):
    exam = models.ForeignKey(to=Exam, null=True, on_delete=models.CASCADE)
    student = models.ForeignKey(to=Student, on_delete=models.CASCADE)#, limit_choices_to={'cls': exam.related_model.cls})

    def __str__(self) -> str:
        return f"{self.student.student_name} (Roll: {self.student.roll})"

class Marks(models.Model):
    class Meta:
        verbose_name = "Mark"
        verbose_name_plural = "Marks"

    subject = models.CharField("Subject", max_length=20, choices=SUBJECTS)
    marks_ob = models.IntegerField("Marks Obtained", help_text="Marks obtained in the subject")
    marks_mx = models.IntegerField("Maximum Marks", help_text="Maximum marks in the subject")

    result = models.ForeignKey(to=Result, null=True, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.subject}: {self.marks_ob} / {self.marks_mx}"