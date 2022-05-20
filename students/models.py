from django.db import models
from django.db.models.signals import post_save

from django.contrib.auth.models import User, Group, Permission
from django.core.validators import RegexValidator

from .constants import CLASSES, CLASSES_NUMBER_MAP, SUBJECTS_OPTIONAL_OUT_OF
from .constants import TEACHERS_GROUP_NAME, TEACHER_USER_DEFAULT_PASSWORD, GROUPS

from exam.constants import SUBJECTS, CLASS_SUBJECTS

class Class(models.Model):
    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    cls = models.CharField(verbose_name="Class", max_length=4, blank=False, null=False, choices=CLASSES)#, editable=False)
    section = models.CharField(verbose_name="Section", max_length=1, blank=True, null=True, help_text="Section name like A, B, C, ...")
    cls_subjects = models.ManyToManyField(to='exam.Subject', verbose_name="Subjects of the Class")

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

class StudentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("cls", "roll")

class Student(models.Model):
    ADMISSION_CATEGORIES = (("I","I"),("II","II"),("III","III"),("IV","IV"),("V","V"))
    SOCIAL_CATEGORIES = (("GEN","General"),("SC","SC"),("ST","ST"),("OBC","OBC"))
    GENDERS = (("Boy","Boy"),("Girl","Girl"))
    BLOOD_GROUPS = (("A+","A+"),("A-","A-"),("B+","B+"),("B-","B-"),("O+","O+"),("O-","O-"),("AB+","AB+"),("AB-","AB-"))
    STUDENT_STATUSES = (("Active","Active"),("Deactive","Deactive"))
    YES_NO_CHOICES = (("YES","YES"),("NO","NO"))
    MINORITIES = (("NA","Not Applicable"),("Muslim","Muslim"))
    ADMISSION_FLAGS = (("Existing","Existing"),)
    
    school_code = models.IntegerField(verbose_name="School Code", blank=False, null=False)

    uid_regex = RegexValidator(r'^\d{15,16}$', "UID should be of 15 digits")
    uid = models.CharField("Student's UID Number", primary_key=True, max_length=16, validators=[uid_regex], blank=False, null=False)

    admission_year_regex = RegexValidator(r'^\d{4}$', "Admission Year should be format YYYY")
    admission_year = models.CharField(verbose_name="Admission Year", max_length=4, validators=[admission_year_regex], blank=False, null=False)

    admission_number_regex = RegexValidator(r'^\d{6}$', "Admission Year should be format XXXXXXX")
    admission_number = models.CharField(verbose_name="Admission Number", max_length=6, validators=[admission_number_regex], blank=False, null=False)

    student_name = models.CharField("Student's Name", max_length=30, null=False)
    cls = models.ForeignKey(to=Class, verbose_name="Class", on_delete=models.CASCADE, blank=False, null=False)
    roll = models.IntegerField(verbose_name="Roll No.", blank=False, null=False)

    fathers_name = models.CharField("Father's Name", max_length=30, null=False)
    mothers_name = models.CharField("Mother's Name", max_length=30, null=False)

    gender = models.CharField("Gender", max_length=4, null=False, choices=GENDERS)
    dob = models.DateField("Date of Birth", blank=False, null=False)

    admission_category = models.CharField("Admission Category", max_length=3, choices=ADMISSION_CATEGORIES, null=False)
    social_category = models.CharField("Social Category", max_length=7, choices=SOCIAL_CATEGORIES, null=False)
    minority = models.CharField("Minority", max_length=6, null=False, choices=MINORITIES)

    phone_regex = RegexValidator(r'^\d{10}$', "Phone number should be of 10 digits")
    phone_number = models.CharField("Contact Number", max_length=10, blank=False, null=False, validators=[phone_regex])
    email = models.EmailField(verbose_name="Email ID", blank=True, null=True)

    blood_group = models.CharField(verbose_name="Blood Group", max_length=3, choices=BLOOD_GROUPS, blank=True, null=True)
    aadhar_regex = RegexValidator(r'^\d{12}$', "Aadhar should be of 12 digits")
    aadhar_number = models.CharField("Aadhar Number", max_length=12, blank=True, null=True, validators=[aadhar_regex])

    student_status = models.CharField("Student Status", max_length=8, null=False, choices=STUDENT_STATUSES)
    tc_issued = models.CharField("TC Issued", max_length=3, null=False, choices=YES_NO_CHOICES)
    admission_flag = models.CharField("Admission Flag", max_length=8, null=False, choices=ADMISSION_FLAGS)
    bpl = models.CharField("BPL", max_length=3, null=False, choices=YES_NO_CHOICES)
    physically_disabled = models.CharField("Physically Disabled", max_length=3, null=False, choices=YES_NO_CHOICES)
    sibbling = models.CharField("Sibbling", max_length=3, null=False, choices=YES_NO_CHOICES)
    single_girl_child = models.CharField("Single Girl Child", max_length=3, null=False, choices=YES_NO_CHOICES)
    rte = models.CharField("RTE", max_length=3, null=False, choices=YES_NO_CHOICES)
    kvs_ward = models.CharField("KVS Ward", max_length=3, null=False, choices=YES_NO_CHOICES)

    optional_subjects_opted = models.ManyToManyField(to='exam.Subject', verbose_name="Extra Subjects Opted (if any)")

    objects = StudentManager()

    def __str__(self) -> str:
        return f"{self.student_name}"

    def get_subjects_opted(self):
        cls_subjects = dict(self.cls.cls_subjects.all().values_list()).values()
        ls = [dict(SUBJECTS)[sub].upper() for sub in cls_subjects if sub.upper() not in self.get_subjects_not_opted()]
        return ls

        # if "Harsh" in self.student_name:
        #     return cls.cls_subjects.all().exclude(subject_name__in=["BIO", "HIN", "SANS"])
        # elif "Sakshi" in self.student_name:
        #     return cls.cls_subjects.all().exclude(subject_name__in=["MATH", "HIN", "SANS"])
        # elif "Vaibhav" in self.student_name:
        #     return cls.cls_subjects.all().exclude(subject_name__in=["BIO", "HIN", "SANS"])
        # elif "Adarsh" in self.student_name:
        #     return cls.cls_subjects.all().exclude(subject_name__in=["BIO", "HIN", "SANS"])

    def get_subjects_not_opted(self):
        opt_subjects = dict(self.optional_subjects_opted.all().values_list()).values()
        ls = [dict(SUBJECTS)[sub].upper() for sub in self.cls.get_optional_subjects() if sub not in opt_subjects]
        return ls

class Teacher(models.Model):
    teacher_name = models.CharField("Teacher's Name", max_length=30)
    user_name = models.CharField("User Name", max_length=150, help_text="Enter an username that you will use for loging in.")
    # password = models.("Password", )

    user = models.OneToOneField(to=User, on_delete=models.CASCADE, editable=False)
    
    dob = models.DateField("Date of Birth", blank=False, null=False)
    doj = models.DateField("Date of Joining", blank=False, null=False)
    salary = models.DecimalField("Salary (in rupees)", decimal_places=2, max_digits=10, blank=False, null=False)

    # subject = models.CharField("Subject", max_length=20, blank=True, null=True, choices=SUBJECTS)
    subject = models.ForeignKey(to="exam.Subject", on_delete=models.CASCADE, verbose_name="Subject", related_name='subject_teachers')
    # teacher_of_class = models.CharField(verbose_name="Class Tecaher Of", max_length=4, blank=True, null=True, choices=Class.CLASSES)
    teacher_of_class = models.OneToOneField(to=Class, on_delete=models.CASCADE, verbose_name="Class Teacher Of", related_name='class_teacher', blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.teacher_name}"

    def save(self, *args, **kwargs):
        if not User.objects.filter(username=self.user_name).exists():
            self.user = User.objects.create_user(username=self.user_name, password=TEACHER_USER_DEFAULT_PASSWORD, is_staff=True)
            teachers_gp, created = Group.objects.get_or_create(name=TEACHERS_GROUP_NAME)
            self.user.groups.add(teachers_gp)

            # if the Group was created right now, it won't have permissions (django is not that smart!)
            # so we need to add permissions to it...
            if created:
                for perm in GROUPS[TEACHERS_GROUP_NAME]:
                    dj_perms = Permission.objects.filter(name__icontains=perm)
                    for each_perm in dj_perms:
                        teachers_gp.permissions.add(each_perm)
        else:
            # TODO: Somehow show error to user that username already exists,
            # probably before clicking the save button in admin site
            return None

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # TODO: this sometimes works and sometimes not..
        # This does works when the teacher is deleted from the change page
        # But not when from the checkbox and action `delete selected` on the list page.
        user = User.objects.get(username=self.user_name)
        user.delete()
        
        return super().delete(*args, **kwargs)