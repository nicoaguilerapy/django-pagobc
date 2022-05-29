from django.shortcuts import render, redirect
from profiles.forms import ProfileForm
from .models import Ciudad, CustomUser, Departamento, Empresa, Profile
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

@login_required()
def profile_create(request):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    try:
        empresa = Empresa.objects.get(admin = request.user)
    except:
        return redirect('home')

    template_name = 'profiles/profile_form.html'
    form = ProfileForm(request.POST or None)
    context = {}
    context['form'] = form
    if request.method == 'GET':
        context['profile'] = profile
        return render(request, template_name, context)

    if request.method == 'POST':
        data = request.POST
        print(data)
        email = data.get('email')
        password1 = data.get('password1')
        password2 = data.get('password2')

        if(password1 != password2):
            context['error_message'] = "Las contraseñas deben ser iguales"
        else:
            new_user = CustomUser.objects.create_user(email = email, password = password1)
            new_profile = Profile.objects.get(user = new_user)
            new_profile.company = empresa
            new_profile.first_name = data.get('first_name')
            new_profile.last_name = data.get('last_name')
            new_profile.save()
            return redirect('profile_list')
        

        return render(request, template_name, context)

@login_required()
def profile_update(request, *args, **kwargs):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    try:
        empresa = Empresa.objects.get(admin = request.user)
    except:
        return redirect('home')
    
    profile_obj = Profile.objects.get(id=kwargs.get('id'))

    if profile.company == empresa and profile_obj.company == empresa:
        template_name = 'profiles/profile_form.html'
        form = ProfileForm(request.POST or None)
        context = {}
        context['form'] = form
        context['profile_obj'] = profile_obj
        context['profile'] = profile

        if request.method == 'GET':
            return render(request, template_name, context)

        if request.method == 'POST':
            data = request.POST
            print(data)
            profile_obj.company = empresa
            profile_obj.first_name = data.get('first_name')
            profile_obj.last_name = data.get('last_name')
            if data.get('active') == 'on':
                profile_obj.active = True
            else:
                profile_obj.active = False
            profile_obj.save()

            return redirect('profile_list')

    return redirect('home')

@login_required()
def profile_list(request):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    try:
        empresa = Empresa.objects.get(admin = request.user)
    except:
        return redirect('home')

    if request.method == "GET":
        context = {}
        template_name = 'profiles/profile_list.html'
        profile_list = Profile.objects.filter(company = profile.company)
        context['profile_list'] = profile_list
        context['profile'] = profile

        return render(request, template_name, context)