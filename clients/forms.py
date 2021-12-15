from django import forms
from .models import *
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['document','first_name', 'last_name', 'region', 'city', 'phone1', 'phone2','email', 'business_name']

        widgets = {
            'document': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese el Documento',
                    'id': 'document'
                }
            ),
            'first_name': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese el Nombre',
                    'id': 'first_name'
                }
            ),
            'last_name': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese el Apellido',
                    'id': 'last_name'
                }
            ),
            'phone1': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese el Número',
                    'id': 'last_name'
                }
            ),
            'phone2': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese el Número Auxiliar',
                    'id': 'phone2'
                }
            ),
            'email': forms.EmailInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese el correo',
                    'id': 'email'
                }
            ),
            'business_name': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese Razón Social',
                    'id': 'email'
                }
            ),
           
        }