# Generated by Django 3.1 on 2021-12-12 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_payment_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='hash_code',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Hash Pago'),
        ),
    ]