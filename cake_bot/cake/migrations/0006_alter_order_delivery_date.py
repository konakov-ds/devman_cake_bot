# Generated by Django 3.2.8 on 2021-10-22 12:08

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('cake', '0005_auto_20211022_1207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 25, 12, 8, 39, 420081, tzinfo=utc)),
        ),
    ]
