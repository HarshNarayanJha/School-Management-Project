# Generated by Django 4.0.1 on 2022-05-30 15:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0018_remove_teacher_subject_and_more'),
        ('exam', '0011_alter_exam_cls_alter_marks_subject_delete_examadmin'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Subject',
        ),
    ]
