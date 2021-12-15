from django import forms
from .models import *

class DateInput(forms.DateInput):
    input_type = 'date'

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

    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )

    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )



    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )

class PaymentForm(forms.Form):
    class Meta:
        model = Payment
        fields = '__all__'
        widgets = {
            'date_expiration': DateInput(),
        }