from django.db import models
from itertools import chain
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from datetime import date
from django.utils import timezone
from clients.models import Client
from django.db.models.signals import post_save
from django.dispatch import receiver

PLATAFORM_CHOICES = (
    ('va', 'Vacío'),
    ('om', 'Otros Métodos'),
    ('ap', 'Aqui Pago'),
    ('pe', 'Pago Express'),
)

STATUS_CHOICES = (
    ('pe', 'Pendiente'),
    ('pa', 'Pagado'),
    ('an', 'Anulado'),
)


class Fee(models.Model):
    id = models.AutoField(primary_key = True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, null=True)
    amount_payable = models.IntegerField('Monto Mensual a Pagar', blank = True, null = True)
    amount_fees = models.IntegerField('Meses a Pagar', blank = True, null = True)
    months_paid = models.IntegerField('Meses Pagados', blank = True, null = True, default = 0)
    date_created = models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name = 'Cuota'
        verbose_name_plural = 'Cuotas'
        ordering = ['id']

    def __str__(self):
        return "[{}] {} - Cuotas: {}/{}".format(self.id, self.client, self.months_paid, self.amount_fees)

class Payment(models.Model):
    id = models.AutoField(primary_key = True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, null=True)
    fee = models.ForeignKey(Fee, on_delete=models.PROTECT, null=True)
    concept =  models.CharField('Concepto', max_length = 20, blank = False, null = False, default="Pago de Producto")
    mount = models.IntegerField('Monto', blank = False, null = False)
    status =  models.CharField('Estado', choices=STATUS_CHOICES, max_length = 2, default = 'pe')
    plataform = models.CharField('Método de Pago', choices=PLATAFORM_CHOICES, max_length=2, default = 'va')
    date_created = models.DateTimeField('Fecha Creación', auto_now_add = True)
    date_expiration = models.DateTimeField('Fecha Vencimiento', default = datetime.now() + timedelta(hours = 72))

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['date_created']

    def __str__(self):
        return "{}: {}, Monto: {}".format(self.id, self.client, self.mount)

    def to_dict(instance):
        opts = instance._meta
        data = {}
        for f in chain(opts.concrete_fields, opts.private_fields):
            data[f.name] = f.value_from_object(instance)
        for f in opts.many_to_many:
            data[f.name] = [i.id for i in f.value_from_object(instance)]
        return data

    @classmethod
    def create(cls, mount):
        payment = cls(mount=mount)
        return payment
        
class Checkout(models.Model):
    id = models.AutoField(primary_key = True)
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, null=True)
    mount = models.IntegerField('Monto', blank = True, null = True)
    transaction = models.IntegerField('Nº Transacción', blank = True, null = True)
    transaction_anulate = models.IntegerField('Nº Transacción de Anulación', blank = True, null = True)
    date_created = models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        ordering = ['id']

    def __str__(self):
        return "[{}] {}".format(self.transaction, self.payment)



@receiver(post_save, sender=Fee, dispatch_uid="update_payment")
def update_stock(sender, instance, **kwargs):
    print('Entro en post_save')
    cliente_obj = Client.objects.get(pk=instance.client.pk)
    amount_payable = instance.amount_payable
    amount_fees = instance.amount_fees
    
    for c in range(int(amount_fees)):
        pay = Payment.create(amount_payable)
        pay.concept = 'Cuota de Producto Nº: '+str(c)
        pay.client = cliente_obj
        pay.fee = instance
        if c > 0:
            pay.date_expiration = datetime.now() + relativedelta(months=+c)
        pay.save()