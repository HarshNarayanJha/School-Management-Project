from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages

from .models import Class, Teacher
from exam.models import Subject, CLASS_SUBJECTS

from .constants import TeacherGroup, GROUPS

@receiver(post_save, sender=Class)
def class_created(sender, instance: Class, created, **kwargs):
    if created:
        _cls_subjects_raw: list[str] = CLASS_SUBJECTS[instance.cls]
        cls_subjects: list[Subject] = []

        for _sub in _cls_subjects_raw:
            cls_subjects.append(Subject.objects.get_or_create(subject_name=_sub)[0])

        instance.cls_subjects.set(cls_subjects)

@receiver(post_save, sender=Teacher)
def teacher_created(sender, instance: Teacher, created, **kwargs):
    if created:
        if not User.objects.filter(username=instance.user_name).exists():
            instance.user = User.objects.create_user(username=instance.user_name, password=TeacherGroup.PASSWORD, is_staff=True)
            teachers_gp, gp_created = Group.objects.get_or_create(name=TeacherGroup.GROUP_NAME)
            instance.user.groups.add(teachers_gp)

            # if the Group was created right now, it won't have permissions (django is not that smart!)
            # so we need to add permissions to it...
            if gp_created:
                for perm in GROUPS[TeacherGroup.GROUP_NAME]:
                    print(perm)
                    dj_perms = Permission.objects.filter(codename=perm.split(".")[1])
                    for each_perm in dj_perms:
                        print(each_perm)
                        teachers_gp.permissions.add(each_perm)

            instance.save(update_fields=['user'])
        else:
            # TODO: Somehow show error to user that username already exists,
            # probably before clicking the save button in admin site
            messages.error(instance.request, f"{instance.user_name} already exists")

@receiver(post_delete, sender=Teacher)
def teacher_deleted(sender, instance: Teacher, **kwargs):
    instance.user.delete()