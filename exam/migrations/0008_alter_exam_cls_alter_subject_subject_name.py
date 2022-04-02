# Generated by Django 4.0.1 on 2022-03-30 06:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0014_alter_class_options'),
        ('exam', '0007_alter_exam_cls_alter_subject_subject_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='cls',
            field=models.ForeignKey(help_text='The class of which the exam is held. This will be pre-filled with your class if you are a class teacher.', on_delete=django.db.models.deletion.CASCADE, to='students.class', verbose_name='Class'),
        ),
        migrations.AlterField(
            model_name='subject',
            name='subject_name',
            field=models.CharField(choices=[('ENG', 'English'), ('HIN', 'Hindi'), ('SANS', 'Sanskrit'), ('MATH', 'Mathematics'), ('EVS', 'Environmental Studies'), ('SCI', 'Science'), ('SST', 'Social Science'), ('PHY', 'Physics'), ('CHEM', 'Chemistry'), ('BIO', 'Biology'), ('CS', 'Computer Science'), ('PHE', 'Physical Education')], max_length=20, unique=True, verbose_name='Subject'),
        ),
    ]
