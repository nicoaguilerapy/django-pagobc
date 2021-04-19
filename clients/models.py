from django.db import models
from itertools import chain
from datetime import datetime
from datetime import timedelta

LABEL_CHOICES = (
    ('PY01', 'Concepcion'),
    ('PY02', 'San Pedro'),
    ('PY03', 'Cordillera'),
    ('PY04', 'Guaira'),
    ('PY05', 'Caaguazu'),
    ('PY06', 'Caazapa'),
    ('PY07', 'Itapua'),
    ('PY08', 'Misiones'),
    ('PY09', 'Paraguari'),
    ('PY10', 'Alto Parana'),
    ('PY11', 'Central'),
    ('PY12', 'Neembucu'),
    ('PY13', 'Amambay'),
    ('PY14', 'Canindeyu'),
    ('PY15', 'Presidente Hayes'),
    ('PY16', 'Boqueron'),
    ('PY17', 'Alto Paraguay'),
)

class Client(models.Model):
    id = models.AutoField(primary_key = True)
    document = models.IntegerField('Documento', blank = False, null = False)
    first_name = models.CharField('Nombres', max_length = 200, blank = False, null = False)
    last_name = models.CharField('Apellidos', max_length = 220, blank = False, null = False)
    region = models.CharField('Departamento', choices=LABEL_CHOICES, max_length=4)
    city = models.CharField('Ciudad', max_length = 220, blank = False, null = False)
    phone1 = models.CharField('Celular Principal', max_length = 10, blank = True, null = True)
    phone2 = models.CharField('Celular Secundario', max_length = 10, blank = True, null = True)
    email = models.EmailField('Correo Electrónico', blank = False, null = False)
    date_created = models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['document']

    def __str__(self):
        return "{}, {}".format(self.first_name, self.last_name)
