# Generated by Django 4.2.3 on 2023-07-22 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_invoiceitem_date_created_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='home_service',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='invoice',
            name='home_service_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='home_service_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='test',
            name='home_service_available',
            field=models.FloatField(default=False),
        ),
        migrations.AlterField(
            model_name='invoiceitem',
            name='status',
            field=models.CharField(blank=True, choices=[('Pending', 'Pending'), ('Specimen Collected', 'Specimen Collected'), ('Report Ready', 'Report Ready')], default='Pending', max_length=100, null=True),
        ),
    ]
