# Generated by Django 3.1 on 2021-12-10 01:58

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('concept', models.CharField(default='Pago de Producto', max_length=20, verbose_name='Concepto')),
                ('mount', models.IntegerField(verbose_name='Monto')),
                ('status', models.CharField(default='Pendiente', max_length=200, verbose_name='Estado')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Fecha Creación')),
                ('date_expiration', models.DateTimeField(default=datetime.datetime(2021, 12, 12, 22, 58, 39, 247522), verbose_name='Fecha Vencimiento')),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='clients.client')),
            ],
            options={
                'verbose_name': 'Pago',
                'verbose_name_plural': 'Pagos',
                'ordering': ['date_created'],
            },
        ),
        migrations.CreateModel(
            name='Fee',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount_payable', models.IntegerField(blank=True, null=True, verbose_name='Monto Mensual a Pagar')),
                ('amount_fees', models.IntegerField(blank=True, null=True, verbose_name='Cantidad de Meses')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='clients.client')),
            ],
        ),
        migrations.CreateModel(
            name='Checkout',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('mount', models.IntegerField(blank=True, null=True, verbose_name='Monto')),
                ('transaction', models.IntegerField(blank=True, null=True, verbose_name='Nº Transacción')),
                ('transaction_anulate', models.IntegerField(blank=True, null=True, verbose_name='Nº Transacción de Anulación')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('payment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.payment')),
            ],
            options={
                'verbose_name': 'Transacción',
                'verbose_name_plural': 'Transacciones',
                'ordering': ['id'],
            },
        ),
    ]
