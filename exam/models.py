from django.db import models
from students.models import Student, Teacher

class Exam(models.Model):
    name = models.CharField("Exam Name", max_length=50)
    session = models.CharField("Exam Session", max_length=10)
    cls = models.IntegerField("Exam of Class")

    def __str__(self) -> str:
        return f"{self.name} ({self.session}) Class {self.cls}"

class Result(models.Model):
    student = models.ForeignKey(to=Student, on_delete=models.CASCADE)

    exam = models.ForeignKey(to=Exam, null=True, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.student.full_name} (Roll: {self.student.roll})"

class Marks(models.Model):
    class Meta:
        verbose_name = "Mark"
        verbose_name_plural = "Marks"

    SUBJECTS = (("MATH", "Mathematics"),
                ("PHY", "Physics"),
                ("CHEM", "Chemistry"),
                ("BIO", "Biology"),
                ("CS", "Computer Science"),
                ("ENG", "English"),
                ("HIN", "Hindi"),
                ("SANS", "Sanskrit"),
                ("PHE", "Physical Education"),
            )
    subject = models.CharField("Subject", max_length=20, choices=SUBJECTS)
    marks_ob = models.IntegerField("Marks Obtained")
    marks_mx = models.IntegerField("Maximum Marks")

    result = models.ForeignKey(to=Result, null=True, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.subject}: {self.marks_ob} / {self.marks_mx}"