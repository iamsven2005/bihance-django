# Generated by Django 5.2 on 2025-06-16 03:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0002_alter_application_employee_id_and_more'),
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobrequirement',
            name='job_id',
            field=models.ForeignKey(db_column='jobId', on_delete=django.db.models.deletion.CASCADE, to='applications.job'),
        ),
    ]
