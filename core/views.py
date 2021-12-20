from django.db.models.query_utils import PathInfo
from django.utils.timezone import now, localtime
from datetime import *
from django.shortcuts import redirect, render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from core.forms import FeeForm, PaymentForm
from pagopar.models import FormaPago
from .models import Fee, Payment, Checkout, STATUS_CHOICES
from clients.models import Client
from profiles.models import Empresa, Profile
import json
from django.http import HttpResponse
from django.utils import formats
from datetime import datetime, timedelta
from datetime import date
from django.utils import timezone        
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage, send_mail
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse, reverse_lazy
import urllib.request
import requests
from django.core import serializers
from django.utils.timezone import make_aware
from django.contrib.sites.models import Site
from django.utils import timezone
import pytz
          
class StaffRequired(object):
    
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StaffRequired, self).dispatch(request, *args, **kwargs)

def _makeDate(date1):
    new_date = make_aware(datetime.strptime(date1, '%d/%m/%Y'))
    new_date = localtime(new_date).replace(hour=23, minute=59, second=59, microsecond=0)
    return new_date

def _getLocalDate(date1):
    date_string = timezone.localtime(date1, pytz.timezone('America/Asuncion'))
    return date_string.strftime('%d/%m/%Y')

def _sendEmail(payment_id, client_email, cod, status_display):
    dato_email_asunto = 'Pedido [{}] en estado: {}'.format(payment_id, status_display)
    try:
        send_mail(
                dato_email_asunto,
                "Su Pedido [{}] cambió al estado de {}\nCodido de la Transacción: {}\nEste es solo un correo informativo.".format(payment_id, status_display, cod),
                client_email,
                [client_email],
                fail_silently=False,
                )

        print("Mensaje Enviado")
    except:
        print("Mensaje No Enviado")

def _sendEmailPagoPar(client_email, link):
    dato_email_asunto = 'Pago generado para PagoPar'
    try:
        send_mail(
                dato_email_asunto,
                "Se generó un método de Pago en PagoPar, puede realizar el pago en el siguiente enlace\n{}".format(link),
                client_email,
                [client_email],
                fail_silently=False,
                )

        print("Mensaje Enviado")
    except:
        print("Mensaje No Enviado")

def _payment_save(received_json_data, payment_obj, profile):
    response_data = {}
    error_messages = []

    try:
        client= int(received_json_data['client'])
        type_document = received_json_data['type_document']
        document = received_json_data['document']
        concept = received_json_data['concept']
        mount = int(received_json_data['mount'])
        status = received_json_data['status']
        type_payment = int(received_json_data['type_payment'])
        identificador = int(received_json_data['identificador'])
        datepicker = received_json_data['datepicker']
    except:
        response_data['cod'] = '909'
        error_messages.append('Error de Request')
        response_data['message'] = error_messages
        return response_data

    if client < 1 or client == None:
        response_data['cod'] = '999'
        error_messages.append('Ingrese un Cliente')
    elif concept == '' or concept == None:
        response_data['cod'] = '999'
        error_messages.append('Ingrese un Concepto')
    elif mount <= 0 or mount == None:
        response_data['cod'] = '999'
        error_messages.append('Ingrese un Monto')
    elif status == '' or status == None or status != 'PP':
        response_data['cod'] = '999'
        error_messages.append('Ingrese un Estado')
    elif type_payment < 0 or type_payment == None:
        response_data['cod'] = '999'
        error_messages.append('Ingrese un Tipo de Pago')
    elif (identificador < -1 or identificador == None and identificador == 0) and type_payment == 2:
        response_data['cod'] = '999'
        error_messages.append('Ingrese un Tipo de PagoPar')

    

    try:
        date_expiration = _makeDate(datepicker)
    except:
        response_data['cod'] = '999'
        error_messages.append('Ingrese un Tipo de Fecha Válida')

    today = now()

    if today > date_expiration:
        response_data['cod'] = '999'
        error_messages.append('Ingrese un Tipo de Fecha Válida')

    if not response_data:
        payment_obj.concept = concept
        payment_obj.client = Client.objects.get(id = client)
        payment_obj.mount = mount
        payment_obj.status = status
        payment_obj.date_expiration = date_expiration
        payment_obj.company = profile.company
        id = payment_obj.save()

        if type_payment == 2 and not 'Pagopar' in payment_obj.type:
            payment_obj.type = 'Pagopar - {}'.format(FormaPago.objects.get(identificador = identificador).forma_pago)
            payment_obj.save()

            domain = Site.objects.get_current().domain
            company = Empresa.objects.get(id = payment_obj.company.id).id
            url = '{}/pagopar/payment/{}/'.format(domain, company)

            r = requests.post(url, data = json.dumps({"id_client":payment_obj.client.id, "id_payment":payment_obj.pk, "id_company":payment_obj.company.id, "id_identificador": identificador}))

            if r.json()['cod'] == '000':
                link = 'https://www.pagopar.com/pagos/{}?forma_pago={}'.format(r.json()['token_pagopar'], identificador)
                _sendEmailPagoPar(payment_obj.client.email, link)
                payment_obj.hash_code = r.json()['token_pagopar']
                payment_obj.save()
                
            else:
                response_data['cod'] = r.json()['cod']
                response_data['message'] = r.json()['message']
                return response_data

        response_data['cod'] = '000'
        response_data['message'] = 'Ingresado'
        return response_data
    else:
        response_data['message'] = error_messages
        return response_data


@method_decorator(login_required, name='dispatch')
class BlankPage(TemplateView):
    template_name = 'core/blank_page.html'

@login_required()
def home(request):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')
    template_name = 'core/index.html'

    context = {}
    context['profile'] = profile

    # payments = Payment.objects.filter(status = 'PP', company = profile.company)
    # sum1 = 0
    # cant1 = 0
    # today = now()
    # for x in payments:
    #     if today.month == x.date_expiration.month:
    #         sum1 = sum1 + x.mount
    #         cant1 = cant1 + 1

    # context['pagos_pendientes_monto'] = sum1
    # context['pagos_pendientes_cantidad'] = cant1
    # sum1 = 0
    # cant1 = 0
    # com = 0

    # checkouts = Checkout.objects.all()
    # for x in checkouts:
    #     if x.date_created.month == today.month and x.transaction_anulate == None:
    #         sum1 = sum1 + x.mount
    #         com = com + (x.mount/100)*x.commission 
    #         cant1 = cant1 + 1


    
    # context['pagos_pagados_monto'] = sum1
    # context['pagos_pagados_comision'] = int(com)
    # context['ingreso_real'] = int(sum1 - com)
    # context['pagos_pagados_cantidad'] = cant1
    
    return render(request, template_name, context)


#payment
@login_required()
def payment_create(request):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    template_name = 'core/payment_form.html'

    #renderizar template
    if request.method == "GET" :
        context = {}
        context['profile'] = profile
        context['status_list'] = STATUS_CHOICES
        context['formapago_list'] = FormaPago.objects.all()
        
        client_list = []
        for i in Client.objects.filter(company = profile.company):
            client_list.append(i.toJSON())

        context['date_expiration'] =  localtime().strftime('%d/%m/%Y')
        context['client_list'] = json.dumps(client_list)

        return render(request, template_name, context)

    #crear objeto
    if request.method == "POST" and request.is_ajax():
        
        payment_obj = Payment.objects.create(mount = 0)

        received_json_data=json.loads(request.body)
        print(received_json_data)

        response_data = _payment_save(received_json_data, payment_obj, profile)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    return redirect('payment_list')

@login_required()
def payment_list(request):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    if request.method == "GET":
        template_name = 'core/payment_list.html'
        payment_list = Payment.objects.filter(company = profile.company, visibility = True)

        context = {}
        context['profile'] = profile
        context['payment_list'] = payment_list

        return render(request, template_name, context)

@login_required()
def payment_update(request, *args, **kwargs):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    template_name = 'core/payment_form.html'
    payment_obj = Payment.objects.get(id=kwargs.get('id'))
    client_obj = payment_obj.client

    if payment_obj.company != profile.company:
        return redirect('home')

    if request.method == "GET":

        context = {}
        context['profile'] = profile
        context['status_list'] = STATUS_CHOICES
        context['formapago_list'] = FormaPago.objects.all()
        context['client_obj'] = client_obj
        context['payment_obj'] = payment_obj
        if payment_obj.type != 'Servidor Propio':
            aux = payment_obj.type.replace('Pagopar - ', '')
            context['identificador'] = FormaPago.objects.get(forma_pago__icontains = aux)
        context['date_expiration'] = (_getLocalDate(payment_obj.date_expiration))
        

        return render(request, template_name, context)

    if request.method == "POST":
        received_json_data=json.loads(request.body)

        response_data = _payment_save(received_json_data, payment_obj, profile)
        return HttpResponse(json.dumps(response_data), content_type="application/json")
        
    return redirect('payment_list')

@login_required()
def payment_hide(request):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    if request.method == "POST":
        received_json_data=json.loads(request.body)
        payment_obj = Payment.objects.get(id= received_json_data['payment_id'])

        if payment_obj.company != profile.company:
            return HttpResponse(json.dumps({"cod":"901","message":"Error de request"}), content_type="application/json")

        payment_obj.visibility = False
        payment_obj.save()
        return HttpResponse(json.dumps({"cod":"000","message":"Ocultado con éxito"}), content_type="application/json")
        
    return redirect('payment_list')

#fee
@login_required()
def fee_create(request):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    template_name = 'core/fee_form.html'
    client_list = []
    context = {}
   

    
    if request.method == "GET":
        for i in Client.objects.filter(company = profile.company):
            client_list.append(i.toJSON())

        context['profile'] = profile
        context['date_expiration'] =  localtime().strftime('%d/%m/%Y')
        context['client_list'] = json.dumps(client_list)

        return render(request, template_name, context)

    if request.method == "POST":
        received_json_data=json.loads(request.body)
        print(received_json_data)

        response_data = {}
        error_messages = []

        try:
            client= int(received_json_data['client'])
            type_document = received_json_data['type_document']
            document = received_json_data['document']
            concept = received_json_data['concept']
            amount_payable = int(received_json_data['amount_payable'])
            mouamount_feesnt = int(received_json_data['amount_fees'])
            datepicker = received_json_data['datepicker']
        except:
            response_data['cod'] = '909'
            error_messages.append('Error de Request')
            response_data['message'] = error_messages
            return response_data

        try:
            date_expiration = _makeDate(datepicker)
        except:
            response_data['cod'] = '999'
            error_messages.append('Ingrese un Tipo de Fecha Válida')

        today = now()

        if today > date_expiration:
            response_data['cod'] = '999'
            error_messages.append('Ingrese un Tipo de Fecha Válida')
            
            fee_obj = Fee.objects.create(client__id = client)

            for c in range(fee_obj.amount_fees):
                c = c + 1
                pay = Payment.objects.create(mount = fee_obj.amount_payable)
                pay.concept = 'Cuota ID: {} | {} ({}/{})'.format(fee_obj.id, document, c, fee_obj.amount_fees)
                pay.client = fee_obj.client
                pay.company = profile.company
                pay.status = 'PP'
                if c > 1:
                    pay.date_expiration = (now() + timedelta(days=c*30))
                else:
                    pay.date_expiration = date_expiration
                pay.save()
                print(pay)

        return redirect('fee_list')

@login_required()
def fee_list(request):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    if request.method == "GET":
        template_name = 'core/fee_list.html'
        fee_list = Fee.objects.filter(company = profile.company)
        context = {}
        context['fee_list'] = fee_list
        context['profile'] = profile

        return render(request, template_name, context)

#checkout
@login_required()
def checkout_list(request):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    if request.method == "GET":
        template_name = 'core/checkout_list.html'
        checkout_list = Checkout.objects.filter(company = profile.company)
        context = {}
        context['checkout_list'] = checkout_list
        context['profile'] = profile

        return render(request, template_name, context)


