from tkinter.tix import Tree
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Student(models.Model):
    first_name = models.CharField("Student's First Name", max_length=15, blank=False, null=False)
    last_name = models.CharField("Student's Last Name", max_length=15, blank=True)
    full_name = models.CharField("Student's Name", max_length=30, editable=False)
    
    uid_regex = RegexValidator(r'^\d{15}$', "UID should be of 15 digits")
    uid = models.CharField("Student's UID Number", primary_key=True, max_length=15, validators=[uid_regex], blank=False, null=False)
    dob = models.DateField("Date of Birth", blank=False, null=False)
    doa = models.DateField("Date of Admission", blank=False, null=False)

    aadhar_regex = RegexValidator(r'^\d{4}\s\d{4}\s\d{4}$', "Aadhar should be in the format XXXX-XXXX-XXXX")
    aadhar_number = models.CharField("Aadhar Number", max_length=14, blank=False, null=False, validators=[aadhar_regex])
    phone_regex = RegexValidator(r'^\d{10}$', "Phone number should be of 10 digits")
    phone_number = models.CharField("Contact Number", max_length=10, blank=False, null=False, validators=[phone_regex])

    cls = models.IntegerField(verbose_name="Class", blank=False, null=False)
    roll = models.IntegerField(verbose_name="Roll No.", blank=False, null=False)

    def __str__(self) -> str:
        return f"{self.full_name}"

    def save(self, *args, **kwargs):
        self.full_name = self.first_name.strip() + " " + self.last_name.strip()

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