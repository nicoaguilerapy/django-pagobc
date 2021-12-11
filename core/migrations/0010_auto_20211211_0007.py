# Generated by Django 3.1 on 2021-12-11 03:07

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20211210_2319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='date_expiration',
            field=models.DateTimeField(default=datetime.datetime(2021, 12, 14, 3, 6, 57, 877149, tzinfo=utc), verbose_name='Fecha Vencimiento'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('PP', 'Pago Pendiente'), ('PC', 'Pago Completado'), ('PR', 'Pago Revertido'), ('PA', 'Pago Anulado'), ('CA', 'Cancelado'), ('RE', 'Recibido'), ('EM', 'Empaquetado'), ('EC', 'En Camino'), ('LR', 'Listo Para Retiro'), ('PL', 'Problemas Logísticos'), ('RE', 'Retirado')], default='PE', max_length=2, verbose_name='Estado'),
        ),
    ]