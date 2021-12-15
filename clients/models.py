from django.db import models
from itertools import chain
from datetime import datetime
from datetime import timedelta
from profiles.models import Ciudad, CustomUser, Departamento, Empresa

STATUS_CHOICES = (
    ('CI', 'Cedula de Identidad'),
    ('RU', 'Registro Unico del Contribuyente'),
    ('PA', 'Pasaporte'),
    ('OT', 'Otros'),
)

class Client(models.Model):
    id = models.AutoField(primary_key = True)
    document = models.CharField('Documento',max_length = 20, blank = True, null = True)
    type_document = models.CharField('Estado', choices=STATUS_CHOICES, max_length=2, default='CI')
    first_name = models.CharField('Nombres', max_length = 200, blank = True, null = True)
    last_name = models.CharField('Apellidos', max_length = 220, blank = False, null = False)
    business_name =  models.CharField('Razón Social', max_length = 220, blank = True, null = True)
    region = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null=True)
    phone1 = models.CharField('Celular Principal', max_length = 10, blank = True, null = True)
    phone2 = models.CharField('Celular Secundario', max_length = 10, blank = True, null = True)
    email = models.EmailField('Correo Electrónico', blank = True, null = True)
    date_created = models.DateTimeField(auto_now_add = True)
    company = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True)
    visibility = models.BooleanField('Visible', default = True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['document']

    def __str__(self):
        return "{}, {}".format(self.first_name, self.last_name)

    def getName(self):
        return "{}, {}".format(self.first_name, self.last_name)

    def get_type_document(self):
        return self.type_document.get_status_display()
