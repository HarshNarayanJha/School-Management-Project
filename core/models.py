from django.db import models
from django.contrib.auth.models import User

from .constants import CLASSES, SUBJECTS_OPTIONAL_OUT_OF, SUBJECTS

class School(models.Model):
    school_code = models.CharField(verbose_name="School Code", max_length=4 , blank=False, null=False, unique=True)
    school_name = models.CharField(verbose_name="School Name", max_length=50, blank=False, null=False)
    school_name_short = models.CharField(verbose_name="School Name (Short)", max_length=25, blank=False, null=False)
    city = models.CharField(verbose_name="City", max_length=30, blank=False, null=False)

    def __str__(self) -> str:
        return f"[{self.school_code}] {self.school_name} - {self.city}"

    @classmethod
    def get_all_schools(self):
        return School.objects.all()

    @classmethod
    def get_classes(self):
        return Class.objects.filter(school__pk=self.pk)
    
    def get_teachers(self):
        return Teacher.objects.filter(school__pk=self.pk)

class Class(models.Model):
    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    cls = models.CharField(verbose_name="Class", max_length=4, blank=False, null=False, choices=CLASSES)#, editable=False)
    section = models.CharField(verbose_name="Section", max_length=1, blank=True, null=True, help_text="Section name like A, B, C, ...")
    cls_subjects = models.ManyToManyField(to='core.Subject', verbose_name="Subjects of the Class")

    stream = models.CharField("Stream", max_length=10, null=True, blank=True, help_text="Stream of the Class if class > XI")

    school = models.ForeignKey(to=School, on_delete=models.CASCADE, blank=False, null=False, editable=False)

    def __str__(self) -> str:
        return f"{self.cls} - {self.section}"

    def get_sections(self) -> "list[str]":
        sects = []
        for _cls in Class.objects.filter(cls=self.cls, school=self.school):
            sects.append(_cls.section)
        return sects

    @classmethod
    def get_classwise_sections(self, school_code: str) -> "dict[str, list[str]]":
        """
        Returns the mapping of all Classes and their sections of a given school
        """
        sections = {}
        for _cls in Class.objects.filter(school__school_code=school_code):
            sections[_cls.cls] = _cls.get_sections()
        return sections

    @classmethod
    def get_schoolwise_classes_sections(self, school_codes: "list[str]") -> "dict[str, dict[str, list[str]]]":
        """
        Returns a dict of school_codes as keys and `get_claswise_sections` as values.
        Takes an param `school_codes` to get only those schools. If None is passed, the the behaviour of
        Super User is assumed (all schools!)
        """
        schoolwise_classes = {}
        schools = School.objects.filter(school_code__in=school_codes) if school_codes else School.objects.all()
        for sc in schools:
            schoolwise_classes[sc.school_code] = Class.get_classwise_sections(sc.school_code)
        return schoolwise_classes

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

    school = models.ForeignKey(to=School, on_delete=models.CASCADE, blank=False, null=False)

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
    subject = models.ForeignKey(to=Subject, on_delete=models.RESTRICT, verbose_name="Subject", related_name='subject_teachers', null=False, blank=False)
    teacher_of_class = models.OneToOneField(to=Class, on_delete=models.SET_NULL, verbose_name="Class Teacher Of", related_name='class_teacher', blank=True, null=True)

    school = models.ForeignKey(to=School, on_delete=models.CASCADE, blank=False, null=False, editable=True)

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