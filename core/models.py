from django.db import models
from django.contrib.auth.models import User

from .constants import CLASSES, SUBJECTS_OPTIONAL_OUT_OF, SUBJECTS


class Class(models.Model):
    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    cls = models.CharField(verbose_name="Class", max_length=4, blank=False, null=False, choices=CLASSES)#, editable=False)
    section = models.CharField(verbose_name="Section", max_length=1, blank=True, null=True, help_text="Section name like A, B, C, ...")
    cls_subjects = models.ManyToManyField(to='core.Subject', verbose_name="Subjects of the Class")

    stream = models.CharField("Stream", max_length=10, null=True, blank=True, help_text="Stream of the Class if class > XI")

    def __str__(self) -> str:
        return f"{self.cls} - {self.section}"

    def get_sections(self) -> "list[str]":
        sects = []
        for _cls in Class.objects.filter(cls=self.cls):
            sects.append(_cls.section)
        return sects

    @classmethod
    def get_classwise_sections(self) -> "dict[str, list[str]]":
        """
        Returns the mapping of all Classes and their sections
        """
        sections = {}
        for _cls in Class.objects.all():
            sections[_cls.cls] = _cls.get_sections()

        return sections

    def get_optional_subjects(self):
        optional_subjects = []
        if self.cls in SUBJECTS_OPTIONAL_OUT_OF:
            for subs in SUBJECTS_OPTIONAL_OUT_OF[self.cls]:
                for sub in subs: optional_subjects.append(sub)

        return optional_subjects

class Subject(models.Model):

    subject_name = models.CharField(verbose_name="Subject", max_length=20, blank=False, null=False, choices=SUBJECTS, unique=True)

    def __str__(self) -> str:
        if self.subject_name in dict(SUBJECTS):
            return dict(SUBJECTS)[self.subject_name]
        else: return self.subject_name

    @classmethod
    def get_all_subjects(self):
        return Subject.objects.all()

    @classmethod
    def get_all_subjects_names(self) -> "list[str]":
        names = []
        for sub in Subject.objects.all():
            names.append(sub.get_subject_name_display())
        return names

    def get_subject_name_display(self) -> str:
        if self.subject_name in dict(SUBJECTS):
            return dict(SUBJECTS)[self.subject_name]
        else: return self.subject_name

class ExamAdmin(models.Model):
    class Meta:
        verbose_name = "Exam Admin"
        
    admin_name = models.CharField("Exam Admin's Name", max_length=30, null=False)
    user_name = models.CharField("User Name", max_length=150, help_text="Enter an username that you will use for logging in.", unique=True)
    # password = models.("Password", )

    user = models.OneToOneField(to=User, on_delete=models.CASCADE, editable=False, null=True)

    def __str__(self) -> str:
        return f"{self.admin_name}"
        
    def delete(self, *args, **kwargs):
        # TODO: this sometimes works and sometimes not..
        # This does works when the teacher is deleted from the change page
        # But not when from the checkbox and action `delete selected` on the list page.
        user = User.objects.get(username=self.user_name)
        user.delete()
        
        return super().delete(*args, **kwargs)

class Teacher(models.Model):
    teacher_name = models.CharField("Teacher's Name", max_length=30, null=False)
    user_name = models.CharField("User Name", max_length=150, help_text="Enter an username that you will use for logging in.", unique=True)
    # password = models.("Password", )

    user = models.OneToOneField(to=User, on_delete=models.CASCADE, editable=False, null=True)

    salary = models.DecimalField("Salary (in rupees)", decimal_places=2, max_digits=10, blank=False, null=False)
    subject = models.ForeignKey(to=Subject, on_delete=models.CASCADE, verbose_name="Subject", related_name='subject_teachers', null=False, blank=False)
    teacher_of_class = models.OneToOneField(to=Class, on_delete=models.SET_NULL, verbose_name="Class Teacher Of", related_name='class_teacher', blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.teacher_name}"
        
    def delete(self, *args, **kwargs):
        # TODO: this sometimes works and sometimes not..
        # This does works when the teacher is deleted from the change page
        # But not when from the checkbox and action `delete selected` on the list page.
        try:
            user = User.objects.get(username=self.user_name)
            user.delete()
        except:
            pass
        
        return super().delete(*args, **kwargs)