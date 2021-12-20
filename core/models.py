from django.db import models
from itertools import chain
from django.db.models.signals import post_save
from django.dispatch import receiver
from clients.models import Client
from profiles.models import CustomUser, Empresa

STATUS_CHOICES = (
    ('PP', 'Pago Pendiente'),
    ('PC', 'Pago Completado'),
    ('PA', 'Pago Anulado'),
    ('CA', 'Cancelado'),
)

class Payment(models.Model):
    id = models.AutoField(primary_key = True)
    ref_code = models.CharField('Codigo de Referencia', max_length = 20, blank = True, null = True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    concept =  models.CharField('Concepto', max_length = 255, blank = False, null = False)
    mount = models.IntegerField('Monto', blank = False, null = False)
    status =  models.CharField('Estado', choices=STATUS_CHOICES, max_length=2, default='PE')
    date_created = models.DateTimeField('Fecha Creación', auto_now_add = True)
    date_expiration = models.DateTimeField('Fecha Vencimiento', null=True, blank=True)
    type =  models.CharField('Origen', max_length = 255, default = "Servidor Propio")
    hash_code = models.CharField('Hash Pago', max_length = 64, null=True, blank=True)
    company = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True)
    visibility = models.BooleanField('Visible', default = True)
    

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['date_created']

    def __str__(self):
        return "{}: {}, Monto: {}".format(self.id, self.client, self.mount)

    def getDateString(self):
        return self.date_expiration.strftime("%d-%m-%Y")
    
    def get_status_current(self):
        for i in STATUS_CHOICES:
            if self.status == i[0]:
                return i[1]
        
    
    def get_type(self):
        return self.type.replace("Pagopar - ","")

    def isFee(self):
        if 'Cuota ID:' in self.concept:
            return True
    
class Checkout(models.Model):
    id = models.AutoField(primary_key = True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    mount = models.IntegerField('Monto', blank = True, null = True)
    transaction = models.CharField('Nº Transacción', blank = True, null = True, max_length = 255,)
    transaction_anulate = models.CharField('Nº Transacción de Anulación', blank = True, null = True, max_length = 255,)
    date_created = models.DateTimeField(auto_now_add = True)
    commission = models.IntegerField('Comisión', default = 3)
    type =  models.CharField('Origen', max_length = 255, blank = True, null = True)
    company = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True)

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

    def amount_fees_paid(self):
        pay_list = Payment.objects.filter(concept__contains = 'Cuota ID: {}'.format(self.id), status = 'PC')
        print(pay_list)
        return pay_list.count()
    
    

@receiver(post_save, sender=Payment)
def ensure_payment_exists(sender, instance, **kwargs):
    if kwargs.get('created', False):
        instance.ref_code = "001{}".format(instance.id)
        instance.save()
        