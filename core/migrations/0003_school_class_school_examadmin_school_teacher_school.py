# Generated by Django 4.0.1 on 2022-06-05 05:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_teacher_teacher_of_class'),
    ]

    operations = [
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school_code', models.CharField(max_length=4, unique=True, verbose_name='School Code')),
                ('school_name', models.CharField(max_length=50, verbose_name='School Name')),
                ('school_name_short', models.CharField(max_length=25, verbose_name='School Name (Short)')),
                ('city', models.CharField(max_length=30, verbose_name='City')),
            ],
        ),
        migrations.AddField(
            model_name='class',
            name='school',
            field=models.ForeignKey(default=1819, editable=False, on_delete=django.db.models.deletion.CASCADE, to='core.school'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='examadmin',
            name='school',
            field=models.ForeignKey(default=1819, editable=False, on_delete=django.db.models.deletion.CASCADE, to='core.school'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='teacher',
            name='school',
            field=models.ForeignKey(default=1819, on_delete=django.db.models.deletion.CASCADE, to='core.school'),
            preserve_default=False,
        ),
    ]
