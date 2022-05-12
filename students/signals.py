from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Class
from exam.models import Subject, CLASS_SUBJECTS

@receiver(post_save, sender=Class)
def class_created(sender, instance: Class, created, **kwargs):
    if created:
        _cls_subjects_raw: list[str] = CLASS_SUBJECTS[instance.cls]
        cls_subjects: list[Subject] = []

        for _sub in _cls_subjects_raw:
            cls_subjects.append(Subject.objects.get_or_create(subject_name=_sub)[0])

        instance.cls_subjects.set(cls_subjects)