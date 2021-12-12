from django import forms
from django.forms import ModelForm
from .models import Profile, CustomUser

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name','last_name', 'type', 'active']

        widgets = {
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
                    'placeholder':'Ingrese el apellido',
                    'id': 'last_name'
                }
            ),
            'type': forms.Select(
                attrs = {
                    'class':'selectpicker form-control',
                    'id': 'type'
                }
            ),
            'active': forms.CheckboxInput(
                attrs = {
                    'class':'form-check-input',
                    'id': 'active'
                }
            ),
            
        }

