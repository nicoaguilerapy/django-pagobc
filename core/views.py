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
from .models import Fee, Payment, Checkout
from clients.models import Client
import json
from django.http import HttpResponse
from django.utils import formats
from datetime import datetime, timedelta
from datetime import date
from django.utils import timezone        
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy


class StaffRequired(object):
    
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StaffRequired, self).dispatch(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class Index(TemplateView):
	template_name = 'core/index.html'

@method_decorator(csrf_exempt, name='dispatch')
class Fees(View):
    def get(self, request):
        
        cliente_pk = request.GET.get('cliente_pk')
        cliente_obj = Client.objects.get(pk=cliente_pk)
        amount_payable = request.GET.get('amount_payable')
        amount_fees = request.GET.get('amount_fees')
        date_created = request.GET.get('date_created')

        for c in range(int(amount_fees)):
            c = c + 1
            pay = Payment.create(amount_payable)
            pay.concept = 'Cuota de Producto Nº: '+str(c)
            pay.client = cliente_obj
            if c > 1:
                pay.date_expiration = now() + timedelta(months=+c)
            pay.save()


        return HttpResponse("")


@method_decorator(csrf_exempt, name='dispatch')
class Consult(View):
    def get(self, request):
        response_data = {}
        detail_data = {}
        today = timezone.now()
        user = "test"
        pwd = "*123*"
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

                    payments = Payment.objects.filter(status = 'Pendiente', client = cliente.pk)[:1]
                
                    if not payments:
                        response_data['codRetorno'] = '001'
                        response_data['desRetorno'] = 'No hay Ninguna deuda'
                        return HttpResponse(json.dumps(response_data), content_type="application/json")
                
                    for payment in payments:
                        if today < payment.date_expiration:
                            response_data['codRetorno'] = '000'
                            response_data['desRetorno'] = 'Aprobado'
                            response_data['nombreApellido'] = cliente.first_name + ' ' + cliente.last_name
                            response_data['cantDetalles'] = '1'
                            detail_data['nroFactura'] = payment.id
                            detail_data['concepto'] = payment.concept
                            detail_data['importe'] = payment.mount
                            detail_data['fechaVencimiento'] = payment.date_created.strftime('%d/%m/%Y')
                            detail_data['moneda'] = '1'
                            response_data['respConsultaDet'] = detail_data
                            return HttpResponse(json.dumps(response_data), content_type="application/json")
                        else:
                            response_data['codRetorno'] = '002'
                            response_data['desRetorno'] = 'Fecha Vencida'
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
        user = "test"
        pwd = "*123*"

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

                    
                        
                    payment = Payment.objects.get(id = nroFactura)
                    cliente = Client.objects.get(id = payment.client.id)
                    importeInt = int(importe)
                    codTransaccionInt = int(codTransaccion)
                    clienteNomApe = cliente.first_name + ' ' + cliente.last_name

                    if tipoTrx == '03' and payment.status == 'Pendiente':
                        if importeInt == payment.mount:
                            checkout,  created = Checkout.objects.get_or_create( payment = payment )

                            if created:
                                correo = None
                                checkout.transaction = codTransaccionInt
                                checkout.mount = importeInt
                                checkout.save()
                                payment.status = 'Pagado'
                                payment.save()
                                response_data['codServicio'] = codServicio
                                response_data['tipoTrx'] = '03'
                                response_data['codRetorno'] = '000'
                                response_data['desRetorno'] = 'APROBADO'
                                email = EmailMessage(
			                    "Pago de: {}".format(clienteNomApe),
			                    "Factura: {} \nCliente: {} \nCodTransaccion: {}".format(payment.id, clienteNomApe, codTransaccionInt),
			                    "no-responder@uverodev.com",
			                    ["contacto@uverodev.com"],
			                    reply_to=[correo]
                                )
                                try:
                                    email.send()
                                    print('Correo enviado')
                                except:
                                    print('Correo no enviado')

                                return HttpResponse(json.dumps(response_data), content_type="application/json")
                            else:
                                response_data['codRetorno'] = '004'
                                response_data['desRetorno'] = 'Ya Pagado'
                                return HttpResponse(json.dumps(response_data), content_type="application/json")
                    elif tipoTrx == '04' and payment.status == 'Pagado':
                        checkout,  created = Checkout.objects.get_or_create( payment = payment )

                        if created:
                            response_data['codRetorno'] = '999'
                            response_data['desRetorno'] = 'Error en el proceso'
                            checkout.delete()
                            return HttpResponse(json.dumps(response_data), content_type="application/json")
                        else:
                            if not checkout.transaction_anulate:
                                correo = None
                                checkout.transaction_anulate = int(received_json_data['codTransaccionAnular'])
                                checkout.save()
                                payment.status = 'Anulado'
                                payment.save()
                                response_data['codServicio'] = codServicio
                                response_data['tipoTrx'] = '04'
                                response_data['codRetorno'] = '000'
                                response_data['desRetorno'] = 'APROBADO'

                                email = EmailMessage(
                                "Anulación de: {}".format(clienteNomApe),
                                "Factura: {} \nCliente: {} \nCodTransaccion: {}\nCodAnulacion".format(payment.id, clienteNomApe, codTransaccionInt, received_json_data['codTransaccionAnular']),
                                "no-responder@uverodev.com",
                                ["contacto@uverodev.com"],
                                reply_to=[correo]
                                )
                                try:
                                    email.send()
                                    print('Correo enviado')
                                except:
                                    print('Correo no enviado')

                                return HttpResponse(json.dumps(response_data), content_type="application/json")
                    elif tipoTrx == '06' and payment.status == 'Anulado':
                        checkout,  created = Checkout.objects.get_or_create( payment = payment )

                        if created:
                            response_data['codRetorno'] = '999'
                            response_data['desRetorno'] = 'Error en el proceso'
                            checkout.delete()
                            return HttpResponse(json.dumps(response_data), content_type="application/json")
                        else:
                            if checkout.transaction_anulate == int(received_json_data['codTransaccionAnular']):
                                correo = None
                                checkout.transaction_anulate = None
                                checkout.save()
                                payment.status = 'Reversado'
                                payment.save()
                                response_data['codServicio'] = codServicio
                                response_data['tipoTrx'] = '04'
                                response_data['codRetorno'] = '000'
                                response_data['desRetorno'] = 'APROBADO'

                                email = EmailMessage(
                                "Reversión de: {}".format(clienteNomApe),
                                "Factura: {} \nCliente: {} \nCodTransaccion: {}\nCodAnulacion".format(payment.id, clienteNomApe, codTransaccionInt, received_json_data['codTransaccionAnular']),
                                "no-responder@uverodev.com",
                                ["contacto@uverodev.com"],
                                reply_to=[correo]
                                )
                                try:
                                    email.send()
                                    print('Correo enviado')
                                except:
                                    print('Correo no enviado')

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
def payment_create(request):
    template_name = 'core/payment_form.html'
    form = PaymentForm(request.POST or None)
    client_list = Client.objects.filter(owner = request.user)

    if request.method == "GET":
        context={ "form":form, "client_list":client_list }
        return render(request, template_name, context)

    if request.method == "POST":
        print(form.data)
        if form.is_valid():
            payment_obj = form.save(commit=False)
            payment_obj.owner = request.user
            payment_obj.save()

        return redirect('payment_list')

def payment_list(request):
    if request.method == "GET":
        template_name = 'core/payment_list.html'
        payment_list = Payment.objects.filter(owner = request.user)
        context={ "payment_list":payment_list }

        return render(request, template_name, context)

def payment_update(request, *args, **kwargs):
    template_name = 'core/payment_form.html'
    form = PaymentForm(request.POST or None)
    payment_obj = Payment.objects.get(id=kwargs.get('id'))

    client_obj = payment_obj.client

    if payment_obj.owner != request.user:
        return redirect('home')

    if request.method == "GET":
        form.fields['status'].initial = payment_obj.status
        context={ "client_obj":client_obj, "payment_obj":payment_obj, "form":form }
        print()
        print(context)
        print()
        return render(request, template_name, context)

    if request.method == "POST":
        form = PaymentForm(request.POST)
        print(form.data)
        if form.is_valid():
            payment_obj.status = form.data['status']
            payment_obj.save()

        return redirect('payment_list')

def fee_create(request):
    template_name = 'core/fee_form.html'
    form = FeeForm(request.POST or None)
    client_list = Client.objects.filter(owner = request.user)

    if request.method == "GET":
        context={ "form":form, "client_list":client_list }
        return render(request, template_name, context)

    if request.method == "POST":
        print(form.data)
        if form.is_valid():
            print('is valid')
            fee_obj = form.save(commit=False)
            fee_obj.owner = request.user
            fee_obj.save()

            for c in range(fee_obj.amount_fees):
                c = c + 1
                pay = Payment.objects.create(mount = fee_obj.amount_payable)
                pay.concept = 'Cuota ID: {} | {} ({}/{})'.format(fee_obj.id, form.data['concept'], c, fee_obj.amount_fees)
                pay.client = fee_obj.client
                pay.owner = request.user
                pay.status = 'PP'
                if c > 1:
                    pay.date_expiration = (now() + timedelta(days=c*30)).strftime("%d-%m-%Y")
                else:
                    pay.date_expiration = (now() + timedelta(days=3)).strftime("%d-%m-%Y")
                pay.save()
                print(pay)

        return redirect('fee_list')


def fee_list(request):
    if request.method == "GET":
        template_name = 'core/fee_list.html'
        fee_list = Fee.objects.filter(owner = request.user)
        context={ "fee_list":fee_list }

        return render(request, template_name, context)