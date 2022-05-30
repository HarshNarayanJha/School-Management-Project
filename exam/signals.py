from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages
from students.constants import ExamAdminGroup, GROUPS

from students.models import Student
from .models import Exam, Result, Marks, ExamAdmin

@receiver(post_save, sender=Student)
def student_created(sender, instance: Student, created, **kwargs):
    if created:
        exams = Exam.objects.filter(cls=instance.cls)
        for exam in exams:
            result: Result = exam.result_set.create(student=instance)
            for subject in instance.cls.cls_subjects.all():
                mark: Marks = result.marks_set.create(subject=subject)

@receiver(post_save, sender=ExamAdmin)
def examadmin_created(sender, instance: ExamAdmin, created, **kwargs):
    if created:
        if not User.objects.filter(username=instance.user_name).exists():
            instance.user = User.objects.create_user(username=instance.user_name, password=ExamAdminGroup.PASSWORD, is_staff=True)
            examadmins_gp, gp_created = Group.objects.get_or_create(name=ExamAdminGroup.GROUP_NAME)
            instance.user.groups.add(examadmins_gp)

            # if the Group was created right now, it won't have permissions (django is not that smart!)
            # so we need to add permissions to it...
            if gp_created:
                for perm in GROUPS[ExamAdminGroup.GROUP_NAME]:
                    dj_perms = Permission.objects.filter(codename=perm.split(".")[1])
                    for each_perm in dj_perms:
                        examadmins_gp.permissions.add(each_perm)

            instance.save(update_fields=['user'])
        else:
            # TODO: Somehow show error to user that username already exists,
            # probably before clicking the save button in admin site
            messages.error(instance.request, f"{instance.user_name} already exists")

@receiver(post_delete, sender=ExamAdmin)
def examadmin_deleted(sender, instance: ExamAdmin, **kwargs):
    instance.user.delete()