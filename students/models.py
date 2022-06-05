from django.db import models
from django.core.validators import RegexValidator

from .constants import ADMISSION_CATEGORIES, ADMISSION_FLAGS, BLOOD_GROUPS, GENDERS, MINORITIES,\
                SOCIAL_CATEGORIES, STUDENT_STATUSES, YES_NO_CHOICES
from core.constants import SUBJECTS

class StudentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("cls", "roll")

class Student(models.Model):
    
    school_code = models.IntegerField(verbose_name="School Code", blank=False, null=False)

    uid_regex = RegexValidator(r'^\d{15,16}$', "UID should be of 15 digits")
    uid = models.CharField("Student's UID Number", primary_key=True, max_length=16, validators=[uid_regex], blank=False, null=False)

    admission_year_regex = RegexValidator(r'^\d{4}$', "Admission Year should be format YYYY")
    admission_year = models.CharField(verbose_name="Admission Year", max_length=4, validators=[admission_year_regex], blank=False, null=False)

    admission_number_regex = RegexValidator(r'^\d{6}$', "Admission Year should be format XXXXXXX")
    admission_number = models.CharField(verbose_name="Admission Number", max_length=6, validators=[admission_number_regex], blank=False, null=False)

    student_name = models.CharField("Student's Name", max_length=30, null=False)
    cls = models.ForeignKey(to='core.Class', verbose_name="Class", on_delete=models.CASCADE, blank=False, null=False)
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

    optional_subjects_opted = models.ManyToManyField(to='core.Subject', verbose_name="Extra Subjects Opted (if any)")

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