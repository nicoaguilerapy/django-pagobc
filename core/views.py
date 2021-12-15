from django.db.models.query_utils import PathInfo
from django.utils.timezone import now
from datetime import *
from datetime import timedelta
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
from django.utils.timezone import make_aware
            
class StaffRequired(object):
    
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StaffRequired, self).dispatch(request, *args, **kwargs)


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

    form = PaymentForm()
    template_name = 'core/payment_form.html'
    client_list = Client.objects.filter(company = profile.company)
    formapago_list = FormaPago.objects.all()

    context = {}
    context['profile'] = profile
    context['form'] = form
    context['status'] = STATUS_CHOICES


    if request.method == "GET" :
        
        context['date_expiration'] = now() + timedelta(hours=72)
        context['client_list'] = client_list
        context['formapago_list'] = formapago_list
        return render(request, template_name, context)

    if request.method == "POST" and request.is_ajax():
        payment_obj = Payment.objects.create(mount = 0)

        received_json_data=json.loads(request.body)
        print(received_json_data)

        response_data = {}
        error_messages = []

        try:
            client= int(received_json_data['client'])
            concept = received_json_data['concept']
            mount = int(received_json_data['mount'])
            status = received_json_data['status']
            type_payment = int(received_json_data['type_payment'])
            identificador = int(received_json_data['identificador'])
            datepicker = received_json_data['datepicker']
        except:
            response_data['cod'] = '909'
            response_data['message'] = 'Error de Request'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

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
           date_expiration = make_aware(datetime.strptime(datepicker, '%d/%m/%Y'))
        except:
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

            if type_payment == 2:
                payment_obj.type = 'Pagopar - {}'.format(FormaPago.objects.get(identificador = identificador).forma_pago)
                payment_obj.save()

                r = requests.post('http://127.0.0.1:8000/pagopar/payment/', data = json.dumps({"id_client":payment_obj.client.id, "id_payment":payment_obj.pk, "id_identificador": identificador}))

                if r.json()['cod'] == '000':
                    link = 'https://www.pagopar.com/pagos/{}?forma_pago={}'.format(r.json()['token_pagopar'], identificador)
                    _sendEmailPagoPar(payment_obj.client.email, link)
                    payment_obj.hash_code = r.json()['token_pagopar']
                    payment_obj.save()
                    
                else:
                    response_data['cod'] = '909'
                    response_data['message'] = 'Error de pagopar'

            response_data['cod'] = '000'
            response_data['message'] = 'Ingresado'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            response_data['message'] = error_messages
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        # if form.is_valid():
        #     payment_obj = form.save(commit=False)
        #     payment_obj.owner = request.user
        #     payment_obj.company = profile.company
        #     if data['id_type_payment'] == '2':
        #         identificador = data['id_identificador']
        #         payment_obj.type = 'Pagopar - {}'.format(FormaPago.objects.get(identificador = identificador).forma_pago)
        #         payment_obj.save()
        #         print()
        #         print(payment_obj)
        #         print(data['id_identificador'])
        #         print(payment_obj.client.id)
        #         print()


        #         r = requests.post('http://127.0.0.1:8000/pagopar/payment/', data = json.dumps({"id_client":payment_obj.client.id, "id_payment":payment_obj.id, "id_identificador": identificador}))

        #         if r.json()['cod'] == '000':
        #             link = 'https://www.pagopar.com/pagos/{}?forma_pago={}'.format(r.json()['token_pagopar'], identificador)
        #             _sendEmailPagoPar(payment_obj.client.email, link)
        #             payment_obj.hash_code = r.json()['token_pagopar']
        #             payment_obj.save()
        #             return redirect('payment_list')
        #         else:
        #             return redirect('payment_list')

        #     else:
        #         payment_obj = form.save(commit=False)
        #         payment_obj.owner = request.user
        #         payment_obj.company = profile.company
        #         payment_obj.save()
                


    return redirect('payment_list')

@login_required()
def payment_list(request):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    if request.method == "GET":
        template_name = 'core/payment_list.html'
        payment_list = Payment.objects.filter(company = profile.company)

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
    form = PaymentForm(request.POST or None)
    payment_obj = Payment.objects.get(id=kwargs.get('id'))
    context = {}
    client_obj = payment_obj.client

    if payment_obj.company != profile.company:
        return redirect('home')

    if request.method == "GET":
        form.fields['status'].initial = payment_obj.status
        
        context['form'] = form
        context['payment_obj'] = payment_obj
        context['client_obj'] = client_obj
        context['profile'] = profile

        return render(request, template_name, context)

    if request.method == "POST":
        form = PaymentForm(request.POST)
        print(form.data)
        if form.is_valid():
            payment_obj.status = form.data['status']
            payment_obj.save()

        return redirect('payment_list')

#fee
@login_required()
def fee_create(request):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    template_name = 'core/fee_form.html'
    form = FeeForm(request.POST or None)
    client_list = Client.objects.filter(company = profile.company)

    if request.method == "GET":
        context = {}
        context['client_list'] = client_list
        context['form'] = form
        context['profile'] = profile

        return render(request, template_name, context)

    if request.method == "POST":
        print(form.data)
        if form.is_valid():
            print('is valid')
            fee_obj = form.save(commit=False)
            fee_obj.owner = request.user
            fee_obj.company = profile.company
            fee_obj.save()

            for c in range(fee_obj.amount_fees):
                c = c + 1
                pay = Payment.objects.create(mount = fee_obj.amount_payable)
                pay.concept = 'Cuota ID: {} | {} ({}/{})'.format(fee_obj.id, form.data['concept'], c, fee_obj.amount_fees)
                pay.client = fee_obj.client
                pay.owner = request.user
                pay.company = profile.company
                pay.status = 'PP'
                if c > 1:
                    pay.date_expiration = (now() + timedelta(days=c*30))
                else:
                    pay.date_expiration = (now() + timedelta(days=3))
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


