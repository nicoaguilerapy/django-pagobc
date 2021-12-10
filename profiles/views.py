from django.shortcuts import render, redirect
from .models import Ciudad, Departamento, Profile
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

@method_decorator(login_required, name='dispatch')
class ProfileUpdate(UpdateView):
    template_name = 'profiles/profile_form.html'
    form_class = ProfileForm
    success_url = reverse_lazy('my_profile')
    
    def get_object(self):
        profile, status = Profile.objects.get_or_create(user = self.request.user)
        return profile


def ajax_address(request):
    if request.method == 'POST' and request.is_ajax():

        data1 = []
        data2 = []

        for x in Departamento.objects.all():
            record = {"id": x.id, "nombre": x.nombre}
            data1.append(record)

        for x in Ciudad.objects.all():
            record = {"id": x.id, "nombre": x.nombre, "cod_departamento": x.cod_departamento}
            data2.append(record)

        return JsonResponse({'departamentos': data1, 'ciudades': data2 }, status=200)

        

    return JsonResponse({"cod": "503", "message": "Error de Request"}, status=200)