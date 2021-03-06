# Generated by Django 4.0.1 on 2022-03-19 08:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0005_alter_marks_marks_mx_alter_marks_marks_ob'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject_name', models.CharField(choices=[('MATH', 'Mathematics'), ('PHY', 'Physics'), ('CHEM', 'Chemistry'), ('BIO', 'Biology'), ('CS', 'Computer Science'), ('ENG', 'English'), ('HIN', 'Hindi'), ('SANS', 'Sanskrit'), ('PHE', 'Physical Education')], max_length=20, verbose_name='Subject')),
            ],
        ),
        migrations.RemoveField(
            model_name='marks',
            name='marks_mx',
        ),
        migrations.AlterField(
            model_name='marks',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.subject', verbose_name='Subject'),
        ),
    ]
