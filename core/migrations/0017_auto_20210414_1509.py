# Generated by Django 3.1 on 2021-04-14 19:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20210414_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fee',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='concept',
            field=models.CharField(default='Pago de Producto', max_length=255, verbose_name='Concepto'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='date_expiration',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 17, 15, 9, 29, 408103), verbose_name='Fecha Vencimiento'),
        ),
    ]