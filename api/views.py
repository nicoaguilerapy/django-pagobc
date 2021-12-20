from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage, send_mail
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import urllib.request
import requests
from django.utils.timezone import make_aware
from django.utils.timezone import now
from datetime import *
from datetime import timedelta
from django.shortcuts import redirect, render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from core.forms import FeeForm, PaymentForm
from core.views import payment_hide
from pagopar.models import FormaPago
from core.models import Fee, Payment, Checkout, STATUS_CHOICES
from clients.models import Client
from profiles.models import Empresa, Profile
import json

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

@csrf_exempt
def consult_pagoexpress(request, *args, **kwargs):
    response_data = {}
    today = now()

    if request.method == "POST":
        received_json_data=json.loads(request.body)
        print(received_json_data)

        empresa_obj = Empresa.objects.get(id=kwargs.get('id'))

        try:
            tipo_documento = received_json_data['tipo_documento']
            documento = received_json_data['documento']
            tipo = 'consulta'
        except:
            pass

        try:
            importe = received_json_data['importe']
            moneda = received_json_data['moneda']
            referencia = received_json_data['referencia']
            deuda_id = received_json_data['deuda_id']
            tipo = 'pago'
        except:
            pass
        

        if tipo == 'consulta':
            client_obj = Client.objects.filter(type_document = tipo_documento, document = documento, company = empresa_obj).first()

            if not client_obj:
                response_data['codigo_respuesta'] = '03'
                response_data['mensaje_respuesta'] = 'Cliente no registrado'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            payments_list = Payment.objects.filter(status = 'PP', client = client_obj, visibility = True)

            if not payments_list:
                    response_data['codigo_respuesta'] = '02'
                    response_data['mensaje_respuesta'] = 'No hay Ninguna deuda'
                    return HttpResponse(json.dumps(response_data), content_type="application/json")

                
            datos = []
            for payment in payments_list:
                if today <= payment.date_expiration:
                    print(payment)
                    detail_data = {}
                    detail_data['cliente'] = payment.client.getName()
                    detail_data['descripcion'] = payment.concept
                    detail_data['deuda_id'] = payment.ref_code
                    detail_data['cuota'] = '1'
                    detail_data['moneda'] = 'PYG'
                    detail_data['importe'] = '{}00'.format(payment.mount)
                    detail_data['vencimiento'] = payment.date_expiration.strftime('%d/%m/%Y')
                    datos.append(detail_data)

            response_data['codigo_respuesta'] = '00'
            response_data['mensaje_respuesta'] = 'CONSULTA APROBADA'
            response_data['datos'] = datos
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        elif tipo == 'pago':
            payment_obj = Payment.objects.get(ref_code = deuda_id)
            if importe != payment_obj.mount:
                response_data['codigo_respuesta'] = '04'
                response_data['mensaje_respuesta'] = 'El Importe debe ser igual a la Deuda'
                return HttpResponse(json.dumps(response_data), content_type="application/json")


            checkout,  created = Checkout.objects.get_or_create( payment = payment_obj )

            if created:
                importe_aux = int(float(importe)/100)
                
                checkout.transaction = referencia
                checkout.mount = importe_aux
                checkout.company = payment_obj.company 
                checkout.type = 'Pago Express'
                checkout.save()
                payment_obj.status = 'PC'
                payment_obj.save()

                response_data['codigo_respuesta'] = '00'
                response_data['mensaje_respuesta'] = 'PAGO APROBADO'
                response_data['autorizacion'] = '{}'.format(checkout.pk)
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                response_data['codigo_respuesta'] = '03'
                response_data['mensaje_respuesta'] = 'Error al Pagar'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

        else:
            response_data['codRetorno'] = '99'
            response_data['desRetorno'] = 'Error en el proceso'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    else:
        response_data['codRetorno'] = '99'
        response_data['desRetorno'] = 'Error en el proceso'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def consult_aquipago(request, *args, **kwargs):
    response_data = {}
    today = timezone.now()

    if request.method == "GET":

        empresa_obj = Empresa.objects.get(id=kwargs.get('id'))

        #capturar datos del negocio
        try:
            codServicio = request.GET.get('codServicio', '')
            usuario = request.GET.get('usuario', '')
            password = request.GET.get('password', '')
        except:
            response_data['codRetorno'] = '004'
            response_data['desRetorno'] = 'Error en credenciales'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        if usuario == empresa_obj.usuario and password == empresa_obj.password:
            
            #capturar el resto de datos
            tipoTrx = request.GET.get('tipoTrx', '')
            nroDocumento = request.GET.get('nroDocumento', '')
            moneda = request.GET.get('moneda', '')

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

    if request.method == "POST":
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
                    