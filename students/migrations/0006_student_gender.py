# Generated by Django 4.0.1 on 2022-01-30 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0005_alter_student_mothers_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='gender',
            field=models.CharField(choices=[('Boy', 'Boy'), ('Girl', 'Girl')], default='Boy', max_length=4, verbose_name='Gender'),
            preserve_default=False,
        ),
    ]
