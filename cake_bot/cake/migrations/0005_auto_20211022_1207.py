# Generated by Django 3.2.8 on 2021-10-22 12:07

import datetime
from django.db import migrations, models
from django.utils.timezone import utc
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('cake', '0004_auto_20211021_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 25, 12, 7, 14, 472286, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='profile',
            name='flat_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='house_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='last_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region='RU'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='street',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
