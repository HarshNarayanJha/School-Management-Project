# Generated by Django 4.0.1 on 2022-06-05 05:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_school_class_school_examadmin_school_teacher_school'),
        ('students', '0018_remove_teacher_subject_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='school_code',
        ),
        migrations.AddField(
            model_name='student',
            name='school',
            field=models.ForeignKey(default=1819, on_delete=django.db.models.deletion.CASCADE, to='core.school'),
            preserve_default=False,
        ),
    ]
