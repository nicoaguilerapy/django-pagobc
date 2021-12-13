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
from .models import Fee, Payment, Checkout
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
from django.urls import reverse, reverse_lazy
import urllib.request
import requests
            
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

    payments = Payment.objects.filter(status = 'PP', company = profile.company)
    sum1 = 0
    cant1 = 0
    today = now()
    for x in payments:
        if today.month == x.date_expiration.month:
            sum1 = sum1 + x.mount
            cant1 = cant1 + 1

    context['pagos_pendientes_monto'] = sum1
    context['pagos_pendientes_cantidad'] = cant1
    sum1 = 0
    cant1 = 0
    com = 0

    checkouts = Checkout.objects.all()
    for x in checkouts:
        if x.date_created.month == today.month and x.transaction_anulate == None:
            sum1 = sum1 + x.mount
            com = com + (x.mount/100)*x.commission 
            cant1 = cant1 + 1


    
    context['pagos_pagados_monto'] = sum1
    context['pagos_pagados_comision'] = int(com)
    context['ingreso_real'] = int(sum1 - com)
    context['pagos_pagados_cantidad'] = cant1
    
    return render(request, template_name, context)


@method_decorator(csrf_exempt, name='dispatch')
class Consult(View):
    def get(self, request):
        response_data = {}
        today = timezone.now()
        user = "admin"
        pwd = "H-ad37Gb>>66GX'$"
        if request.method == 'GET':                                                                                                                                                                                                           
            codServicio = request.GET.get('codServicio')
            usuario = request.GET.get('usuario')
            password = request.GET.get('password')
            tipoTrx = request.GET.get('tipoTrx')
            nroDocumento = request.GET.get('nroDocumento')
            moneda = request.GET.get('moneda')

            if usuario == user and password == pwd:
                if moneda != '1':
                    response_data['codRetorno'] = '003'
                    response_data['desRetorno'] = 'Solo se aceptan pagos en Guaranies'
                    return HttpResponse(json.dumps(response_data), content_type="application/json")

                if tipoTrx == '05':
                    cliente = Client.objects.filter(document=nroDocumento).first()

                    if not cliente:
                        response_data['codRetorno'] = '002'
                        response_data['desRetorno'] = 'Cliente no registrado'
                        return HttpResponse(json.dumps(response_data), content_type="application/json")

                    payments = Payment.objects.filter(status = 'PP', client = cliente.id)
                
                    if not payments:
                        response_data['codRetorno'] = '001'
                        response_data['desRetorno'] = 'No hay Ninguna deuda'
                        return HttpResponse(json.dumps(response_data), content_type="application/json")

                    
                    response_data_item = []

                    for payment in payments:
                        if today < payment.date_expiration:
                            print(payment)
                            detail_data = {}
                            detail_data['nroFactura'] = payment.id
                            detail_data['concepto'] = payment.concept
                            detail_data['importe'] = payment.mount
                            detail_data['fechaVencimiento'] = payment.date_created.strftime('%d/%m/%Y')
                            detail_data['moneda'] = '1'
                            response_data_item.append(detail_data)
                            

                    response_data['codRetorno'] = '000'
                    response_data['desRetorno'] = 'Aprobado'
                    response_data['nombreApellido'] = cliente.first_name + ' ' + cliente.last_name
                    response_data['cantDetalles'] = '{}'.format(payments.count())
                    response_data['detalles'] = response_data_item

                    return HttpResponse(json.dumps(response_data), content_type="application/json")

                else:
                    response_data['codRetorno'] = '999'
                    response_data['desRetorno'] = 'Error en el proceso'
                    return HttpResponse(json.dumps(response_data), content_type="application/json")

            else:
                response_data['codRetorno'] = '999'
                response_data['desRetorno'] = 'Error en el proceso'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

        response_data['codRetorno'] = '999'
        response_data['desRetorno'] = 'Error en el proceso'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def post(self, request):
        response_data = {}
        detail_data = {}
        today = timezone.now()
        user = "admin"
        pwd = "H-ad37Gb>>66GX'$"

        received_json_data=json.loads(request.body)
        print(received_json_data)

        if request.method == 'POST':
            codServicio = received_json_data['codServicio']
            usuario = received_json_data['usuario']
            password = received_json_data['password']
            tipoTrx = received_json_data['tipoTrx']
            nroFactura = received_json_data['nroFactura']
            importe = received_json_data['importe']
            moneda = received_json_data['moneda']
            medioPago = received_json_data['medioPago']
            codTransaccion = received_json_data['codTransaccion']
            

            if usuario == user and password == pwd:
                if nroFactura and importe and moneda and medioPago and codTransaccion and tipoTrx:
                    if moneda != '1':
                        response_data['codRetorno'] = '003'
                        response_data['desRetorno'] = 'Solo se aceptan pagos en Guaranies'
                        return HttpResponse(json.dumps(response_data), content_type="application/json")
  
                    try:
                        payment_obj = Payment.objects.get(id = nroFactura)
                        cliente = Client.objects.get(id = payment_obj.client.id)
                    except:
                        response_data['codRetorno'] = '999'
                        response_data['desRetorno'] = 'Error en el proceso'

                        return HttpResponse(json.dumps(response_data), content_type="application/json")

                    importeInt = int(importe)
                    print()
                    print(payment_obj)
                    print(cliente)
                    print()

                    if tipoTrx == '03' and payment_obj.status == 'PP':
                        if importeInt == payment_obj.mount:
                            checkout,  created = Checkout.objects.get_or_create( payment = payment_obj )

                            if created:
                                checkout.transaction = codTransaccion
                                checkout.mount = importeInt
                                checkout.owner = payment_obj.owner
                                checkout.company = payment_obj.company 
                                checkout.save()
                                payment_obj.status = 'PC'
                                payment_obj.save()
                                print()
                                print(payment_obj)
                                print()
                                
                                response_data['codServicio'] = codServicio
                                response_data['tipoTrx'] = '03'
                                response_data['codRetorno'] = '000'
                                response_data['desRetorno'] = 'APROBADO'
                                _sendEmail(payment_obj.id, cliente.email, codTransaccion, payment_obj.get_status_display())

                                return HttpResponse(json.dumps(response_data), content_type="application/json")
                            else:
                                response_data['codRetorno'] = '004'
                                response_data['desRetorno'] = 'Ya Pagado'
                                return HttpResponse(json.dumps(response_data), content_type="application/json")
                    elif tipoTrx == '04' and payment_obj.status == 'PC':
                        checkout,  created = Checkout.objects.get_or_create( payment = payment_obj )

                        if created:
                            response_data['codRetorno'] = '999'
                            response_data['desRetorno'] = 'Error en el proceso'
                            checkout.delete()
                            return HttpResponse(json.dumps(response_data), content_type="application/json")
                        else:
                            if not checkout.transaction_anulate:
                                checkout.transaction_anulate = received_json_data['codTransaccionAnular']
                                checkout.owner = payment_obj.owner
                                checkout.company = payment_obj.company 
                                checkout.save()
                                payment_obj.status = 'PA'
                                payment_obj.save()
                                response_data['codServicio'] = codServicio
                                response_data['tipoTrx'] = '04'
                                response_data['codRetorno'] = '000'
                                response_data['desRetorno'] = 'APROBADO'

                                _sendEmail(payment_obj.id, cliente.email, checkout.transaction_anulate, payment_obj.get_status_display())

                                return HttpResponse(json.dumps(response_data), content_type="application/json")
                    elif tipoTrx == '06' and payment_obj.status == 'PA':
                        print()
                        print('Anular')
                        print()
                        checkout,  created = Checkout.objects.get_or_create( payment = payment_obj )

                        if created:
                            response_data['codRetorno'] = '999'
                            response_data['desRetorno'] = 'Error en el proceso'
                            checkout.delete()
                            return HttpResponse(json.dumps(response_data), content_type="application/json")
                        else:
                            if checkout.transaction_anulate == received_json_data['codTransaccionAnular']:
                                checkout.transaction_anulate = None
                                checkout.owner = payment_obj.owner
                                checkout.company = payment_obj.company 
                                checkout.save()
                                payment_obj.status = 'PC'
                                payment_obj.save()
                                response_data['codServicio'] = codServicio
                                response_data['tipoTrx'] = '04'
                                response_data['codRetorno'] = '000'
                                response_data['desRetorno'] = 'APROBADO'

                                _sendEmail(payment_obj.id, cliente.email, checkout.transaction, payment_obj.get_status_display())

                                return HttpResponse(json.dumps(response_data), content_type="application/json")

                            
                else:
                    response_data['codRetorno'] = '999'
                    response_data['desRetorno'] = 'Error en el proceso'
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                response_data['codRetorno'] = '999'
                response_data['desRetorno'] = 'Error en el proceso'
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            
            response_data['codRetorno'] = '999'
            response_data['desRetorno'] = 'Error en el proceso'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
                    
#payment
@login_required()
def payment_create(request):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    template_name = 'core/payment_form.html'
    form = PaymentForm(request.POST or None)
    client_list = Client.objects.filter(company = profile.company)
    formapago_list = FormaPago.objects.all()

    context = {}
    context['profile'] = profile

    if request.method == "GET":
        context['client_list'] = client_list
        context['formapago_list'] = formapago_list
        context['form'] = form
        return render(request, template_name, context)

    if request.method == "POST":
        data = request.POST
        print(data)
        if form.is_valid():
            payment_obj = form.save(commit=False)
            payment_obj.owner = request.user
            payment_obj.company = profile.company

            if data['id_type_payment'] == '2':
                identificador = data['id_identificador']
                payment_obj.type = 'Pagopar - {}'.format(FormaPago.objects.get(identificador = identificador).forma_pago)
                payment_obj.save()
                print()
                print(payment_obj)
                print(data['id_identificador'])
                print(payment_obj.client.id)
                print()


                r = requests.post('http://127.0.0.1:8000/pagopar/payment/', data = json.dumps({"id_client":payment_obj.client.id, "id_payment":payment_obj.id, "id_identificador": identificador}))

                if r.json()['cod'] == '000':
                    link = 'https://www.pagopar.com/pagos/{}?forma_pago={}'.format(r.json()['token_pagopar'], identificador)
                    _sendEmailPagoPar(payment_obj.client.email, link)
                    payment_obj.hash_code = r.json()['token_pagopar']
                    payment_obj.save()
                    return redirect('payment_list')
                else:
                    return redirect('payment_list')

            else:
                payment_obj = form.save(commit=False)
                payment_obj.owner = request.user
                payment_obj.company = profile.company
                payment_obj.save()
                


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


