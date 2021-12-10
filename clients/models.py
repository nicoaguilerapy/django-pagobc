from django.db import models
from itertools import chain
from datetime import datetime
from datetime import timedelta
from profiles.models import Ciudad, CustomUser, Departamento

class Client(models.Model):
    id = models.AutoField(primary_key = True)
    document = models.IntegerField('Documento', blank = False, null = False)
    first_name = models.CharField('Nombres', max_length = 200, blank = False, null = False)
    last_name = models.CharField('Apellidos', max_length = 220, blank = False, null = False)
    region = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null=True)
    phone1 = models.CharField('Celular Principal', max_length = 10, blank = True, null = True)
    phone2 = models.CharField('Celular Secundario', max_length = 10, blank = True, null = True)
    email = models.EmailField('Correo Electrónico', blank = True, null = True)
    date_created = models.DateTimeField(auto_now_add = True)
    user =  models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['document']

    def __str__(self):
        return "{}, {}".format(self.first_name, self.last_name)
