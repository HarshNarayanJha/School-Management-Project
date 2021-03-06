# Generated by Django 4.0.1 on 2022-01-30 10:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0006_student_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='aadhar_number',
            field=models.CharField(blank=True, max_length=12, null=True, validators=[django.core.validators.RegexValidator('^\\d{12}$', 'Aadhar should be of 12 digits')], verbose_name='Aadhar Number'),
        ),
        migrations.AlterField(
            model_name='student',
            name='social_category',
            field=models.CharField(choices=[('General', 'GEN'), ('SC', 'SC'), ('ST', 'ST'), ('OBC', 'OBC')], max_length=7, verbose_name='Social Category'),
        ),
    ]
