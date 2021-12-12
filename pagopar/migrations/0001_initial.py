# Generated by Django 3.1 on 2021-12-12 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0016_checkout_commission'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormaPago',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('forma_pago', models.CharField(blank=True, default='', max_length=80, null=True, verbose_name='Forma de pago')),
                ('identificador', models.CharField(blank=True, default='', max_length=2, null=True, verbose_name='Identificador')),
                ('descripcion', models.TextField(blank=True, default='', null=True, verbose_name='Descripcion')),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='pagopar/')),
            ],
            options={
                'verbose_name': 'Forma de Pago',
                'verbose_name_plural': 'Formas de Pago',
            },
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('pagado', models.BooleanField(default=False, verbose_name='Pagado')),
                ('forma_pago', models.CharField(default='', max_length=50, verbose_name='Forma de Pago')),
                ('fecha_pago', models.CharField(default='', max_length=10, verbose_name='Fecha de Pago')),
                ('monto', models.CharField(default='', max_length=20, verbose_name='Monto')),
                ('fecha_maxima_pago', models.CharField(default='', max_length=19, verbose_name='Fecha Limite de Pago')),
                ('hash_pedido', models.CharField(default='', max_length=64, verbose_name='Token del Pedido')),
                ('numero_pedido', models.CharField(default='', max_length=50, verbose_name='Numero de Pedido')),
                ('cancelado', models.BooleanField(default=False, verbose_name='Cancelado')),
                ('forma_pago_identificador', models.CharField(default='', max_length=2, verbose_name='Forma de Pago Codigo')),
                ('payment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.payment')),
            ],
            options={
                'verbose_name': 'Pago',
                'verbose_name_plural': 'Pagos',
            },
        ),
    ]
