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

class Ciudad(models.Model):
    id = models.AutoField(primary_key = True)
    nombre = models.CharField('Nombre', max_length = 220, blank = True, null = True)
    cod_departamento = models.SmallIntegerField('Departamento', blank = True, null = True)
    delivery = models.BooleanField('Disponible/No Disponible', default = False)
    delivery_price = models.IntegerField('Precio', blank = False, null = False, default=0)

    class Meta:
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
        ordering = ['nombre']

    def get_departamento(self):
        return "{}".format( Departamento.objects.get( id = self.cod_departamento).nombre )
    get_departamento.short_description = 'Departamento'

class Profile(models.Model):
    id = models.AutoField(primary_key = True)
    user = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    image = models.ImageField(upload_to = 'profile', null = True, blank = True)
    document = models.IntegerField('Documento', blank = True, null = True)
    first_name = models.CharField('Nombres', max_length = 200, blank = True, null = True)
    last_name = models.CharField('Apellidos', max_length = 220, blank = True, null = True)
    street_address = models.CharField('Dirección', max_length=255, null = True, blank = True)
    ref_address = models.CharField('Nº Casa/Departamento', max_length=255, null = True, blank = True)
    region = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null=True)
    phone = models.CharField('Celular:', max_length= 10, null = True, blank = True)
    date_created = models.DateTimeField(auto_now_add = True, null=True, blank=True)
    token = models.CharField(max_length = 64, default = _createHash)
    
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
        ordering = ['-document']
    
    def __str__(self):
        return "{}, {}".format(self.first_name, self.last_name)

@receiver(post_save, sender=CustomUser)
def ensure_profile_exists(sender, instance, **kwargs):
    if kwargs.get('created', False):
        new_profile, created = Profile.objects.get_or_create(user=instance)
        print("Se acaba de crear un usuario y su perfil enlazado")

