# Generated by Django 4.2.3 on 2023-07-15 15:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_doctor_schedules'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctor',
            name='consultation',
        ),
    ]