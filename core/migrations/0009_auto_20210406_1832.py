# Generated by Django 3.1 on 2021-04-06 22:32

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
        ('core', '0008_auto_20201113_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='clients.client'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='date_expiration',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 8, 18, 32, 53, 99802), verbose_name='Fecha Vencimiento'),
        ),
        migrations.DeleteModel(
            name='Client',
        ),
    ]
