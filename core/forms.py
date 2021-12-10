from django import forms
from .models import *
from clients.models import Client

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['client','concept', 'mount', 'status', 'date_expiration']

        widgets = {
            'client': forms.Select(
                attrs = {
                    'class':'selectpicker form-control',
                    'id': 'client'
                }
            ),
            'concept': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese un concepto',
                    'id': 'concept'
                }
            ),
            'mount': forms.NumberInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese el Monto Fijo',
                    'id': 'mount'
                }
            ),
            'status': forms.Select(
                attrs = {
                    'class':'selectpicker form-control',
                    'id': 'status'
                }
            ),
            'date_expiration': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'',
                    'id': 'date_expiration',
                    'readonly':"",
                    'aria-label':"Default select example"
                }
            ),
        }

class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ['client','amount_payable', 'amount_fees']

        widgets = {
            'client': forms.Select(
                attrs = {
                    'class':'selectpicker form-control',
                    'id': 'client'
                }
            ),
            'amount_payable': forms.NumberInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese el Monto Fijo',
                    'id': 'amount_payable'
                }
            ),
            'amount_fees': forms.NumberInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Cantidad de Cuotas',
                    'id': 'amount_fees'
                }
            ),
        }