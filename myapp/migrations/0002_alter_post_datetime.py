# Generated by Django 4.0.5 on 2022-06-22 08:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='datetime',
            field=models.DateTimeField(default=datetime.date.today),
        ),
    ]
