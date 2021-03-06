# Generated by Django 4.0.1 on 2022-03-12 10:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0003_alter_marks_options_alter_marks_result_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exam',
            name='name',
        ),
        migrations.AddField(
            model_name='exam',
            name='exam_name',
            field=models.CharField(choices=[('PT-1', 'Periodic Test - 1'), ('T-1', 'Term - 1 Examination'), ('PT-2', 'Periodic Test - 2'), ('T-2', 'Term - 2 Examination')], default='Exam', help_text='Select the type of exam from the dropdown.', max_length=50, verbose_name='Exam Name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='exam',
            name='cls',
            field=models.CharField(choices=[('I', 'I'), ('II', 'II'), ('III', 'III'), ('IV', 'IV'), ('V', 'V'), ('VI', 'VI'), ('VII', 'VII'), ('VIII', 'VIII'), ('IX', 'IX'), ('X', 'X'), ('XI', 'XI'), ('XII', 'XII')], help_text='The class of which the exam is held.                                                                                     This will be pre-filled with your class if you are a class teacher.', max_length=4, verbose_name='Exam of Class'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='session',
            field=models.CharField(help_text='Session of the exam. like 2021-2022', max_length=10, validators=[django.core.validators.RegexValidator('^20\\d{2}-20\\d{2}$', 'should be in the format 20XX-20XX')], verbose_name='Exam Session'),
        ),
        migrations.AlterField(
            model_name='marks',
            name='marks_mx',
            field=models.IntegerField(help_text='Maximum marks in the subject', verbose_name='Maximum Marks'),
        ),
        migrations.AlterField(
            model_name='marks',
            name='marks_ob',
            field=models.IntegerField(help_text='Marks obtained in the subject', verbose_name='Marks Obtained'),
        ),
    ]
