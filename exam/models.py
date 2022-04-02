import django
from django.db import models
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

from students.models import Student, Teacher, Class

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
    cls = models.ForeignKey(to=Class, verbose_name="Class", on_delete=models.CASCADE, blank=False, null=False, help_text="The class of which the exam is held. This will be pre-filled with your class if you are a class teacher.")

    def __str__(self) -> str:
        return f"{self.exam_name} Examination ({self.session}) Class {self.cls}"

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
        return f"Result: {self.student.student_name} (Class: {self.student.cls}, Roll: {self.student.roll}) [{self.exam.exam_name} {self.exam.session}]"

class Marks(models.Model):
    class Meta:
        verbose_name = "Mark"
        verbose_name_plural = "Marks"

    subject = models.ForeignKey(to="Subject", verbose_name="Subject", on_delete=models.CASCADE)
    marks_ob = models.IntegerField("Marks Obtained", help_text="Marks obtained in the subject", null=True, blank=True)
    # marks_mx = models.IntegerField("Maximum Marks", help_text="Maximum marks in the subject", null=True, blank=True)

    result = models.ForeignKey(to=Result, null=True, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Marks: {self.subject}: ({self.marks_ob} / {40}) [{self.result.__str__().replace('Result: ', '')}]"

    # Temprorarily!
    @property
    def marks_mx(self):
        return 40

class Subject(models.Model):
    SUBJECTS = (("ENG", "English"),
                ("HIN", "Hindi"),
                ("SANS", "Sanskrit"),
                ("MATH", "Mathematics"),
                ("EVS", "Environmental Studies"),
                ("SCI", "Science"),
                ("SST", "Social Science"),

                ("PHY", "Physics"),
                ("CHEM", "Chemistry"),
                ("BIO", "Biology"),

                ("CS", "Computer Science"),
                ("PHE", "Physical Education"),
            )

    subject_name = models.CharField(verbose_name="Subject", max_length=20, blank=False, null=False, choices=SUBJECTS, unique=True)

    def __str__(self) -> str:
        return dict(self.SUBJECTS)[self.subject_name]

    def get_subject_name_display(self) -> str:
        return dict(self.SUBJECTS)[self.subject_name]

# (Default) Mapping of Classes to Subjects
CLASS_SUBJECTS: "dict[str: 'list[str]']" = {
    "I": ["ENG", "HIN", "MATH", "EVS"],
    "II": ["ENG", "HIN", "MATH", "EVS"],
    "III": ["ENG", "HIN", "MATH", "EVS"],
    "IV": ["ENG", "HIN", "MATH", "EVS"],
    "V": ["ENG", "HIN", "MATH", "EVS"],

    "VI": ["ENG", "HIN", "SANS", "MATH", "SCI", "SST"],
    "VII": ["ENG", "HIN", "SANS", "MATH", "SCI", "SST"],
    "VIII": ["ENG", "HIN", "SANS", "MATH", "SCI", "SST"],

    "IX": ["ENG", "HIN", "SANS", "MATH", "SCI", "SST"],
    "X": ["ENG", "HIN", "SANS", "MATH", "SCI", "SST"],
    "XI": ["ENG", "HIN", "SANS", "CS", "MATH", "PHY", "CHEM", "BIO", "PHE"],
    "XII": ["ENG", "HIN", "SANS", "CS", "MATH", "PHY", "CHEM", "BIO", "PHE"],
}

@receiver(post_save, sender=Student)
def student_created(sender, instance: Student, created, **kwargs):
    if created:
        exams = Exam.objects.filter(cls=instance.cls)
        for exam in exams:
            result: Result = exam.result_set.create(student=instance)
            for subject in instance.cls.cls_subjects.all():
                mark: Marks = result.marks_set.create(subject=subject)