# Generated by Django 4.0.1 on 2022-06-29 13:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_examadmin_school_alter_teacher_subject'),
        ('exam', '0014_examtype_remove_exam_exam_name_exam_exam_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='examtype',
            name='weightage',
            field=models.PositiveSmallIntegerField(default=100, verbose_name='Weightage'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='exam',
            name='exam_type',
            field=models.ForeignKey(help_text='Select the type of exam from the dropdown.', on_delete=django.db.models.deletion.PROTECT, related_name='+', to='exam.examtype', verbose_name='Exam Type'),
        ),
        migrations.CreateModel(
            name='ExamSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=20, null=True, verbose_name='Exam Set Name')),
                ('cls', models.CharField(max_length=5, null=False, verbose_name='Class')),
            ],
        ),
        migrations.AddField(
            model_name='examtype',
            name='exam_set',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.RESTRICT, to='exam.examset', verbose_name='Exam Set'),
            preserve_default=False,
        ),
    ]