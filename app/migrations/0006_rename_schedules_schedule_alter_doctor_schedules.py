# Generated by Django 4.2.3 on 2023-07-15 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_doctor_date_joined'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Schedules',
            new_name='Schedule',
        ),
    ]