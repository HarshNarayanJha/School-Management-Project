# Generated by Django 4.0.1 on 2022-05-30 15:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cls', models.CharField(choices=[('I', 'I'), ('II', 'II'), ('III', 'III'), ('IV', 'IV'), ('V', 'V'), ('VI', 'VI'), ('VII', 'VII'), ('VIII', 'VIII'), ('IX', 'IX'), ('X', 'X'), ('XI', 'XI'), ('XII', 'XII')], max_length=4, verbose_name='Class')),
                ('section', models.CharField(blank=True, help_text='Section name like A, B, C, ...', max_length=1, null=True, verbose_name='Section')),
                ('stream', models.CharField(blank=True, help_text='Stream of the Class if class > XI', max_length=10, null=True, verbose_name='Stream')),
            ],
            options={
                'verbose_name': 'Class',
                'verbose_name_plural': 'Classes',
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject_name', models.CharField(choices=[('ENG', 'English'), ('HIN', 'Hindi'), ('SANS', 'Sanskrit'), ('MATH', 'Mathematics'), ('EVS', 'Environmental Studies'), ('SCI', 'Science'), ('SST', 'Social Science'), ('PHY', 'Physics'), ('CHEM', 'Chemistry'), ('BIO', 'Biology'), ('CS', 'Computer Science'), ('PHE', 'Physical Education')], max_length=20, unique=True, verbose_name='Subject')),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teacher_name', models.CharField(max_length=30, verbose_name="Teacher's Name")),
                ('user_name', models.CharField(help_text='Enter an username that you will use for logging in.', max_length=150, unique=True, verbose_name='User Name')),
                ('salary', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Salary (in rupees)')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subject_teachers', to='core.subject', verbose_name='Subject')),
                ('teacher_of_class', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='class_teacher', to='core.class', verbose_name='Class Teacher Of')),
                ('user', models.OneToOneField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ExamAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admin_name', models.CharField(max_length=30, verbose_name="Exam Admin's Name")),
                ('user_name', models.CharField(help_text='Enter an username that you will use for logging in.', max_length=150, unique=True, verbose_name='User Name')),
                ('user', models.OneToOneField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Exam Admin',
            },
        ),
        migrations.AddField(
            model_name='class',
            name='cls_subjects',
            field=models.ManyToManyField(to='core.Subject', verbose_name='Subjects of the Class'),
        ),
    ]