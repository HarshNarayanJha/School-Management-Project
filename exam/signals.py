from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages

from students.models import Student
from .models import Exam, Result, Marks

@receiver(post_save, sender=Student)
def student_created(sender, instance: Student, created, **kwargs):
    if created:
        exams = Exam.objects.filter(cls=instance.cls)
        for exam in exams:
            result: Result = exam.result_set.create(student=instance)
            for subject in instance.cls.cls_subjects.all():
                mark: Marks = result.marks_set.create(subject=subject)