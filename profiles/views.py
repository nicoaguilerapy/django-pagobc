from django.shortcuts import render, redirect
from .models import Ciudad, Departamento, Profile
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
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