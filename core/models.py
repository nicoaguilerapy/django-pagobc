from django.db import models
from itertools import chain
from datetime import datetime
from datetime import timedelta
from clients.models import Client

LABEL_CHOICES = (
    ('ap', 'Aqui Pago'),
    ('pe', 'Pago Express'),
)

class Payment(models.Model):
    id = models.AutoField(primary_key = True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    concept =  models.CharField('Concepto', max_length = 20, blank = False, null = False, default="Pago de Producto")
    mount = models.IntegerField('Monto', blank = False, null = False)
    status =  models.CharField('Estado', max_length = 200, blank = False, null = False, default="Pendiente")
    plataform = models.CharField('Método de Pago', choices=LABEL_CHOICES, max_length=2)
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
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
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

class Fee(models.Model):
    id = models.AutoField(primary_key = True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    amount_payable = models.IntegerField('Monto Mensual a Pagar', blank = True, null = True)
    amount_fees = models.IntegerField('Cantidad de Meses', blank = True, null = True)
    date_created = models.DateTimeField(auto_now_add = True)