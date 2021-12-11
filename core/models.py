from django.db import models
from itertools import chain
from django.utils.timezone import now
from datetime import *
from datetime import timedelta
from clients.models import Client
from profiles.models import CustomUser, Empresa

STATUS_CHOICES = (
    ('PP', 'Pago Pendiente'),
    ('PC', 'Pago Completado'),
    ('PR', 'Pago Revertido'),
    ('PA', 'Pago Anulado'),
    ('CA', 'Cancelado'),
    ('RE', 'Recibido'),
    ('EM', 'Empaquetado'),
    ('EC', 'En Camino'),
    ('LR', 'Listo Para Retiro'),
    ('PL', 'Problemas Logísticos'),
    ('RE', 'Retirado'),
)


class Payment(models.Model):
    id = models.AutoField(primary_key = True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    concept =  models.CharField('Concepto', max_length = 255, blank = False, null = False)
    mount = models.IntegerField('Monto', blank = False, null = False)
    status =  models.CharField('Estado', choices=STATUS_CHOICES, max_length=2, default='PE')
    date_created = models.DateTimeField('Fecha Creación', auto_now_add = True)
    date_expiration = models.DateTimeField('Fecha Vencimiento', default=(now() + timedelta(hours = 72)))
    company = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True)
    owner =  models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

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

    def getDateString(self):
        return self.date_expiration.strftime("%d-%m-%Y")
    
    def get_status_current(self):
        return self.status.get_status_display()
    
class Checkout(models.Model):
    id = models.AutoField(primary_key = True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    mount = models.IntegerField('Monto', blank = True, null = True)
    transaction = models.CharField('Nº Transacción', blank = True, null = True, max_length = 255,)
    transaction_anulate = models.CharField('Nº Transacción de Anulación', blank = True, null = True, max_length = 255,)
    date_created = models.DateTimeField(auto_now_add = True)
    company = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True)
    owner =  models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        ordering = ['id']

    def __str__(self):
        return "[{}] {}".format(self.transaction, self.payment)

class Fee(models.Model):
    id = models.AutoField(primary_key = True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    amount_payable = models.IntegerField('Monto Mensual a Pagar', blank = True, null = True)
    amount_fees = models.IntegerField('Cantidad de Meses', blank = True, null = True)
    date_created = models.DateTimeField(auto_now_add = True)
    company = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True)
    owner =  models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def amount_fees_paid(self):
        pay_list = Payment.objects.filter(concept__contains = 'Cuota ID: {}'.format(self.id), status = 'PC')
        print(pay_list)
        return pay_list.count()