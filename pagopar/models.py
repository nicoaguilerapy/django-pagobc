from django.db import models
from core.models import Payment
from django.urls import reverse
from django.utils.html import format_html

class Pago(models.Model):
    id = models.AutoField(primary_key = True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    pagado =  models.BooleanField('Pagado', default=False)
    forma_pago = models.CharField('Forma de Pago', default="", max_length=50)
    fecha_pago = models.CharField('Fecha de Pago', default="", max_length=10)
    monto = models.CharField('Monto', default="", max_length=20)
    fecha_maxima_pago = models.CharField('Fecha Limite de Pago', default="", max_length=19)
    hash_pedido = models.CharField('Token del Pedido', default="", max_length=64)
    numero_pedido = models.CharField('Numero de Pedido', default="", max_length=50)
    cancelado =  models.BooleanField('Cancelado', default=False)
    forma_pago_identificador = models.CharField('Forma de Pago Codigo', default="", max_length=2)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
    
    def get_order(self):
        link = reverse("payment_update", kwargs={'id': self.payment.id})
        return format_html('<a href="{}">Ver Order</a>'.format(link))
    get_order.short_description = 'Pedido'

class FormaPago(models.Model):
    id = models.AutoField(primary_key = True)
    forma_pago = models.CharField('Forma de pago', default="", max_length=80, null = True, blank = True)
    identificador = models.CharField('Identificador', default="", max_length=2, null = True, blank = True)
    descripcion = models.TextField('Descripcion', default="", null = True, blank = True)
    imagen = models.ImageField(upload_to='pagopar/', null = True, blank = True)
    commission = models.IntegerField('Comisión', default = 6)

    class Meta:
        verbose_name = 'Forma de Pago'
        verbose_name_plural = 'Formas de Pago'
    
    def __str__(self):
        return self.forma_pago

