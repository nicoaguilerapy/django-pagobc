
from django.http.response import HttpResponse
from django.utils.timezone import now
from datetime import *
from datetime import timedelta
from django.shortcuts import redirect, render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from clients.forms import ClientForm
from clients.models import Client
from profiles.models import Ciudad, Departamento, Profile
from django.db.models import Q
import json

def _client_save(received_json_data, client_obj, profile):
    response_data = {}
    error_messages = []

    try:
        type_document = received_json_data['type_document']
        document = received_json_data['document']
        first_name = received_json_data['first_name']
        last_name = received_json_data['last_name']
        id_region = int(received_json_data['id_region'])
        id_city = int(received_json_data['id_city'])
        phone1 = received_json_data['phone1']
        client_email = received_json_data['client_email']
    except:
        response_data['cod'] = '909'
        error_messages.append('Error de Request')
        response_data['message'] = error_messages
        return response_data

    if type_document == 'RU':
        try:
            business_name = received_json_data['business_name']
        except:
            response_data['cod'] = '909'
            error_messages.append('Ingrese una Razón Social')
            response_data['message'] = error_messages
            return response_data
    
    try:
        phone2 = received_json_data['phone2']
    except:
        phone2 = ""

    if type_document == '' or type_document == None:
        response_data['cod'] = '999'
        error_messages.append('Ingrese un Tipo de Documento')
    elif document == '' or document == None:
        response_data['cod'] = '999'
        error_messages.append('Ingrese un Documento')
    elif (business_name == '' or business_name == None) and type_document == 'RU':
        response_data['cod'] = '999'
        error_messages.append('Ingrese una Razón Social')
    elif first_name == '' or first_name == None:
        response_data['cod'] = '999'
        error_messages.append('Ingrese un Nombre')
    elif last_name == '' or last_name == None:
        response_data['cod'] = '999'
        error_messages.append('Ingrese un Apellido')
    elif client_email == '' or client_email == None:
        response_data['cod'] = '999'
        error_messages.append('Ingrese un Email')
    elif phone1 == '' or phone1 == None:
        response_data['cod'] = '999'
        error_messages.append('Ingrese un Número')
    elif id_city < 1:
        response_data['cod'] = '999'
        error_messages.append('Ingrese una Ciudad')
    elif id_region < 1:
        response_data['cod'] = '999'
        error_messages.append('Ingrese una Ciudad')

    if not response_data:
        client_obj.type_document = type_document
        client_obj.document = document
        client_obj.first_name = first_name
        client_obj.last_name = last_name
        client_obj.email = client_email
        client_obj.city = Ciudad.objects.get(id = id_city)
        client_obj.region = Departamento.objects.get(id = id_region)
        client_obj.phone1 = phone1
        client_obj.phone2 = phone2
        client_obj.company = profile.company
        client_obj.save()

        response_data['cod'] = '000'
        return response_data

    response_data['message'] = error_messages
    return response_data

@login_required()
def client_create(request):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    context = {}
    context['profile'] = profile
    template_name = 'clients/client_form.html'
    form = ClientForm(request.POST or None)

    #renderizar vista
    if request.method == "GET":
        context['form'] = form
        return render(request, template_name, context)

    #crear objeto
    if request.method == "POST" and request.is_ajax():
        client_obj = Client.objects.create()

        received_json_data=json.loads(request.body)
        print(received_json_data)

        response_data = _client_save(received_json_data, client_obj, profile)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    return redirect('client_list')

@login_required()
def client_list(request):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    context = {}
    context['profile'] = profile
    if request.method == "GET":
        client_list = Client.objects.filter(company = profile.company)
        template_name = 'clients/client_list.html'
        context['client_list'] = client_list

        return render(request, template_name, context)

    if request.method == "POST" and request.is_ajax():
        response_data = {}
        
        received_json_data=json.loads(request.body)
        print(received_json_data)

        client_obj = Client.objects.filter(company = profile.company, document = received_json_data['search_document']).first()

        if client_obj:
            client_data = []
            client_data.append(client_obj)

            response_data['cod'] = '000'
            response_data['client'] = client_data
            

        else:
            response_data['cod'] = '001'
            response_data['message'] = 'Cliente no Encontrado'

        return HttpResponse(json.dumps(response_data), content_type="application/json")

@login_required()
def client_update(request, *args, **kwargs):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    context = {}
    context['profile'] = profile

    template_name = 'clients/client_form.html'
    form = ClientForm(request.POST or None)
    client_obj = Client.objects.get(id=kwargs.get('id'))

    if client_obj.company != profile.company:
        return redirect('home')

    if request.method == "GET":
        form = ClientForm(instance=client_obj)
        context['form'] = form
        context['client_obj'] = client_obj
        print()
        print(context)
        print()
        return render(request, template_name, context)

    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            client_obj.document = form.data['document']
            client_obj.first_name = form.data['first_name']
            client_obj.last_name = form.data['last_name']
            client_obj.region = Departamento.objects.get(id = form.data['region'])
            client_obj.city = Ciudad.objects.get(id = form.data['city'])
            client_obj.email = form.data['email']
            client_obj.phone1 = form.data['phone1']
            client_obj.phone2 = form.data['phone2']
            try:
                visibility = request.POST['visibility']
                client_obj.visibility = True
            except:
                client_obj.visibility = False
            
            client_obj.save()
            

        return redirect('client_list')