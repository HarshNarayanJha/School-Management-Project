from django.db import models

from django.contrib.auth.models import User, Group, Permission
from django.core.validators import RegexValidator

TEACHERS_GROUP_NAME = "Teachers"
TEACHER_USER_DEFAULT_PASSWORD = "123456"
# Mapping of Group to Permissions
# Permissions are searched for using `icontains` lookup, 
# so `mark` will catch all of the add, view, delete, and change perms
GROUPS = {
    TEACHERS_GROUP_NAME: ["view user", 
                          "add exam", "change exam", "view exam", 
                          "mark", "result",
                          "add student", "change student", "view student",
                          "view teacher"],
}

class Class(models.Model):
    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    CLASSES = (
            ("I","I"),("II","II"),("III","III"),("IV","IV"),("V","V"),("VI","VI"),("VII","VII"),
            ("VIII","VIII"),("IX","IX"),("X","X"),("XI","XI"),("XII","XII")
        )

    cls = models.CharField(verbose_name="Class", max_length=4, blank=False, null=False, choices=CLASSES)#, editable=False)
    cls_subjects = models.ManyToManyField(to='exam.Subject', verbose_name="Subjects of the Class")

    def __str__(self) -> str:
        return self.cls

class StudentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("cls", "roll")

class Student(models.Model):
    ADMISSION_CATEGORIES = (("I","I"),("II","II"),("III","III"),("IV","IV"),("V","V"))
    SOCIAL_CATEGORIES = (("GEN","General"),("SC","SC"),("ST","ST"),("OBC","OBC"))
    GENDERS = (("Boy","Boy"),("Girl","Girl"))
    
    school_code = models.IntegerField(verbose_name="School Code", blank=False, null=False)

    student_name = models.CharField("Student's Name", max_length=30, null=False)
    fathers_name = models.CharField("Father's Name", max_length=30, null=False)
    mothers_name = models.CharField("Mother's Name", max_length=30, null=True, blank=True)

    admission_category = models.CharField("Admission Category",max_length=3, choices=ADMISSION_CATEGORIES, null=False)
    social_category = models.CharField("Social Category",max_length=7, choices=SOCIAL_CATEGORIES, null=False)
    gender = models.CharField("Gender",max_length=4,null=False,choices=GENDERS)
    uid_regex = RegexValidator(r'^\d{15,16}$', "UID should be of 15 digits")
    uid = models.CharField("Student's UID Number", primary_key=True, max_length=16, validators=[uid_regex], blank=False, null=False)
    dob = models.DateField("Date of Birth", blank=False, null=False)
    doa = models.DateField("Date of Admission", blank=False, null=False)

    aadhar_regex = RegexValidator(r'^\d{12}$', "Aadhar should be of 12 digits")
    aadhar_number = models.CharField("Aadhar Number", max_length=12, blank=True, null=True, validators=[aadhar_regex])
    phone_regex = RegexValidator(r'^\d{10}$', "Phone number should be of 10 digits")
    phone_number = models.CharField("Contact Number", max_length=10, blank=False, null=False, validators=[phone_regex])

    cls = models.ForeignKey(to=Class, verbose_name="Class", on_delete=models.CASCADE, blank=False, null=False)
    roll = models.IntegerField(verbose_name="Roll No.", blank=False, null=False)

    objects = StudentManager()

    def __str__(self) -> str:
        return f"{self.student_name}"

    def get_subjects_opted(self) -> str:
        cls: Class = Class.objects.get(cls=self.cls)
        return cls.cls_subjects.all()
        # if "Harsh" in self.student_name:
        #     return cls.cls_subjects.all().exclude(subject_name__in=["BIO", "HIN", "SANS"])
        # elif "Sakshi" in self.student_name:
        #     return cls.cls_subjects.all().exclude(subject_name__in=["MATH", "HIN", "SANS"])
        # elif "Vaibhav" in self.student_name:
        #     return cls.cls_subjects.all().exclude(subject_name__in=["BIO", "HIN", "SANS"])
        # elif "Adarsh" in self.student_name:
        #     return cls.cls_subjects.all().exclude(subject_name__in=["BIO", "HIN", "SANS"])

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