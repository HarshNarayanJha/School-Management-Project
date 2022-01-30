from tkinter.tix import Tree
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Student(models.Model):
    school_code = models.IntegerField(verbose_name="School Code", blank=False, null=False)

    student_name = models.CharField("Student's Name", max_length=30, null=False)
    fathers_name = models.CharField("Father's Name", max_length=30, null=False)
    mothers_name = models.CharField("Mother's Name", max_length=30, null=True, blank=True)

    admission_category = models.CharField("Admission Category",max_length=3, choices=(("I","I"),("II","II"),("III","III"),("IV","IV"),("V","V")), null=False)
    social_category = models.CharField("Social Category",max_length=7, choices=(("General","GEN"),("SC","SC"),("ST","ST"),("OBC","OBC")), null=False)
    gender = models.CharField("Gender",max_length=4,null=False,choices=(("Boy","Boy"),("Girl","Girl")))
    uid_regex = RegexValidator(r'^\d{15,16}$', "UID should be of 15 digits")
    uid = models.CharField("Student's UID Number", primary_key=True, max_length=16, validators=[uid_regex], blank=False, null=False)
    dob = models.DateField("Date of Birth", blank=False, null=False)
    doa = models.DateField("Date of Admission", blank=False, null=False)

    aadhar_regex = RegexValidator(r'^\d{12}$', "Aadhar should be of 12 digits")
    aadhar_number = models.CharField("Aadhar Number", max_length=12, blank=True, null=True, validators=[aadhar_regex])
    phone_regex = RegexValidator(r'^\d{10}$', "Phone number should be of 10 digits")
    phone_number = models.CharField("Contact Number", max_length=10, blank=False, null=False, validators=[phone_regex])

    cls = models.CharField(verbose_name="Class",max_length=4, blank=False, null=False,choices=(
        ("I","I"),("II","II"),("III","III"),("IV","IV"),("V","V"),("VI","VI"),("VII","VII"),
        ("VIII","VIII"),("IX","IX"),("X","X"),("XI","XI"),("XII","XII")
        ))
    roll = models.IntegerField(verbose_name="Roll No.", blank=False, null=False)

    def __str__(self) -> str:
        return f"{self.student_name}"

    def save(self, *args, **kwargs):
        #self.full_name = self.first_name.strip() + " " + self.last_name.strip()
        super().save(*args, **kwargs)

class Teacher(models.Model):
    first_name = models.CharField("Teacher's First Name", max_length=15, blank=False, null=False)
    last_name = models.CharField("Teacher's Last Name", max_length=15, blank=True)
    full_name = models.CharField("Teacher's Name", max_length=30, editable=False)
    
    dob = models.DateField("Date of Birth", blank=False, null=False)
    doj = models.DateField("Date of Joining", blank=False, null=False)
    salary = models.DecimalField("Salary (in rupees)", decimal_places=2, max_digits=10, blank=False, null=False)

    subject = models.CharField("Subject", max_length=20, blank=True, null=True)
    teacher_of_class = models.IntegerField("Class Tecaher Of", blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.full_name}"

    def save(self, *args, **kwargs):
        self.full_name = self.first_name.strip() + " " + self.last_name.strip()

        super().save(*args, **kwargs)