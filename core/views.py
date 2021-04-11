from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from .models import Payment, Checkout
from clients.models import Client
import json
from django.http import HttpResponse
from django.utils import formats
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from datetime import date
from django.utils import timezone        
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage


class StaffRequired(object):
    
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StaffRequired, self).dispatch(request, *args, **kwargs)

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
                pay.date_expiration = datetime.now() + relativedelta(months=+c)
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
                    
        