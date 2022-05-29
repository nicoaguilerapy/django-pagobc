# Generated by Django 3.1 on 2022-05-29 22:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '__first__'),
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ref_code', models.CharField(blank=True, max_length=20, null=True, verbose_name='Codigo de Referencia')),
                ('concept', models.CharField(max_length=255, verbose_name='Concepto')),
                ('mount', models.IntegerField(verbose_name='Monto')),
                ('status', models.CharField(choices=[('PP', 'Pago Pendiente'), ('PC', 'Pago Completado'), ('PA', 'Pago Anulado'), ('CA', 'Cancelado')], default='PE', max_length=2, verbose_name='Estado')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Fecha Creación')),
                ('date_expiration', models.DateTimeField(blank=True, null=True, verbose_name='Fecha Vencimiento')),
                ('type', models.CharField(default='Servidor Propio', max_length=255, verbose_name='Origen')),
                ('hash_code', models.CharField(blank=True, max_length=64, null=True, verbose_name='Hash Pago')),
                ('visibility', models.BooleanField(default=True, verbose_name='Visible')),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='clients.client')),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='profiles.empresa')),
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
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='profiles.empresa')),
            ],
        ),
        migrations.CreateModel(
            name='Checkout',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('mount', models.IntegerField(blank=True, null=True, verbose_name='Monto')),
                ('transaction', models.CharField(blank=True, max_length=255, null=True, verbose_name='Nº Transacción')),
                ('transaction_anulate', models.CharField(blank=True, max_length=255, null=True, verbose_name='Nº Transacción de Anulación')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('commission', models.IntegerField(default=3, verbose_name='Comisión')),
                ('type', models.CharField(blank=True, max_length=255, null=True, verbose_name='Origen')),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='profiles.empresa')),
                ('payment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.payment')),
            ],
            options={
                'verbose_name': 'Transacción',
                'verbose_name_plural': 'Transacciones',
                'ordering': ['id'],
            },
        ),
    ]
