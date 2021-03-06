# Generated by Django 3.2.7 on 2022-01-18 13:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('first_name', models.CharField(max_length=15, verbose_name="Student's First Name")),
                ('last_name', models.CharField(blank=True, max_length=15, verbose_name="Student's Last Name")),
                ('full_name', models.CharField(editable=False, max_length=30, verbose_name="Student's Name")),
                ('uid', models.CharField(max_length=15, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator('^\\d{15}$', 'UID should be of 15 digits')], verbose_name="Student's UID Number")),
                ('dob', models.DateField(verbose_name='Date of Birth')),
                ('doa', models.DateField(verbose_name='Date of Admission')),
                ('aadhar_number', models.CharField(max_length=14, validators=[django.core.validators.RegexValidator('^\\d{4}\\s\\d{4}\\s\\d{4}$', 'Aadhar should be in the format XXXX-XXXX-XXXX')], verbose_name='Aadhar Number')),
                ('phone_number', models.CharField(max_length=10, validators=[django.core.validators.RegexValidator('^\\d{10}$', 'Phone number should be of 10 digits')], verbose_name='Contact Number')),
                ('cls', models.IntegerField(verbose_name='Class')),
                ('roll', models.IntegerField(verbose_name='Roll No.')),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=15, verbose_name="Teacher's First Name")),
                ('last_name', models.CharField(blank=True, max_length=15, verbose_name="Teacher's Last Name")),
                ('full_name', models.CharField(editable=False, max_length=30, verbose_name="Teacher's Name")),
                ('dob', models.DateField(verbose_name='Date of Birth')),
                ('doj', models.DateField(verbose_name='Date of Joining')),
                ('salary', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Salary (in rupees)')),
                ('subject', models.CharField(blank=True, max_length=20, null=True, verbose_name='Subject')),
                ('teacher_of_class', models.IntegerField(blank=True, null=True, verbose_name='Class Tecaher Of')),
            ],
        ),
    ]
