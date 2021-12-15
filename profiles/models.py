from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from .managers import CustomUserManager
from django.conf import settings
from itertools import chain
from datetime import datetime, timedelta
import os
import time
import hashlib
from binascii import hexlify
from uuid import uuid4

TYPE_CHOICES = (
    ('VE', 'Vendedor'),
    ('TR', 'Transportador'),
    ('AD', 'Administrador'),
)

def _createHash():
    unique_token_found = False
    while not unique_token_found:
        token_new = uuid4()
    # This weird looking construction is a way to pass a value to a field with a dynamic name
        if Profile.objects.filter(token = token_new).count() is 0:
            unique_token_found = True

    return token_new

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    spouse_name = models.CharField(blank=True, max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    

    def __str__(self):
        return self.email

class Departamento(models.Model):
    id = models.AutoField(primary_key = True, db_index=True)
    nombre = models.CharField('Nombre', max_length = 220, blank = True, null = True)

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Ciudad(models.Model):
    id = models.AutoField(primary_key = True)
    nombre = models.CharField('Nombre', max_length = 220, blank = True, null = True)
    cod_departamento = models.SmallIntegerField('Departamento', blank = True, null = True)
    delivery = models.BooleanField('Disponible/No Disponible', default = False)
    delivery_price = models.IntegerField('Precio', blank = False, null = False, default=0)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
        ordering = ['nombre']

    def get_departamento(self):
        return "{}".format( Departamento.objects.get( id = self.cod_departamento).nombre )
    get_departamento.short_description = 'Departamento'

class Empresa(models.Model):
    id = models.AutoField(primary_key = True)
    nombre = models.CharField('Nombre', max_length = 220, blank = True, null = True)
    servidor_propio = models.BooleanField('Servidor Propio', default= True)
    admin = models.ForeignKey(CustomUser, on_delete = models.CASCADE, blank = True, null = True)
    cod_servicio = models.CharField('Código de Servicio', max_length = 220, blank = True, null = True)
    usuario = models.CharField('Usuario', max_length = 220, blank = True, null = True)
    password = models.CharField('Contraseña', max_length = 220, blank = True, null = True)
    servidor_pagopar = models.BooleanField('Servidor PagoPar', default= True)
    token_publico = models.CharField('token publico', max_length = 220, blank = True, null = True)
    token_privado = models.CharField('token privado', max_length = 220, blank = True, null = True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nombre']

class Profile(models.Model):
    id = models.AutoField(primary_key = True)
    user = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    first_name = models.CharField('Nombres', max_length = 200, blank = True, null = True)
    last_name = models.CharField('Apellidos', max_length = 220, blank = True, null = True)
    type =  models.CharField('Tipo', choices=TYPE_CHOICES, max_length=2, default='AD')
    company = models.ForeignKey(Empresa, on_delete = models.CASCADE, blank = True, null = True)
    active = models.BooleanField('Activado', default= True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
        ordering = ['-last_name']
    
    def __str__(self):
        return "{}, {}".format(self.first_name, self.last_name)

@receiver(post_save, sender=CustomUser)
def ensure_profile_exists(sender, instance, **kwargs):
    if kwargs.get('created', False):
        new_profile, created = Profile.objects.get_or_create(user=instance)
        print("Se acaba de crear un usuario y su perfil enlazado")

