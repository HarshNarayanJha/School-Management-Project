# Generated by Django 4.0.1 on 2022-01-30 06:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0002_auto_20220120_1418'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='marks',
            options={'verbose_name': 'Mark', 'verbose_name_plural': 'Marks'},
        ),
        migrations.AlterField(
            model_name='marks',
            name='result',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='exam.result'),
        ),
        migrations.AlterField(
            model_name='result',
            name='exam',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='exam.exam'),
        ),
    ]