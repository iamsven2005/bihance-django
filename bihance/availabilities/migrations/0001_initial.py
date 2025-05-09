# Generated by Django 5.2 on 2025-05-03 06:11

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Timings',
            fields=[
                ('time_id', models.TextField(db_column='timeId', default=uuid.uuid4, max_length=36, primary_key=True, serialize=False)),
                ('start_time', models.DateTimeField(db_column='Starttime')),
                ('end_time', models.DateTimeField(db_column='Endtime')),
                ('title', models.TextField(blank=True, db_column='Title', null=True)),
                ('employee_id', models.ForeignKey(db_column='id', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'timings',
                'indexes': [models.Index(fields=['employee_id'], name='timings_id_3474e9_idx')],
            },
        ),
    ]
