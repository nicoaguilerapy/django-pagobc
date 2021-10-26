from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from .models import Payment, Checkout, Fee
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
from django.core.mail import send_mail
from micredito.settings import EMAIL_HOST_USER


class StaffRequired(object):
    
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StaffRequired, self).dispatch(request, *args, **kwargs)

class Index(TemplateView):
	template_name = 'core/index.html'


@method_decorator(csrf_exempt, name='dispatch')
class AdminRequest(View):

    def post(self, request):
        response_data = {}
        received_json_data=json.loads(request.body)
        password = received_json_data['password']
        action = received_json_data['action']
        table = received_json_data['table']

        if password == 'niconico123' and action == 'delete':
            if table == 'payment':
                Payment.objects.all().delete()
                response_data['action'] = action
                response_data['Message'] = 'Se fue todo a la puta de {}'.format(table)
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            elif table == 'checkout':
                Checkout.objects.all().delete()
                response_data['action'] = action
                response_data['Message'] = 'Se fue todo a la puta de {}'.format(table)
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            elif table == 'fee':
                Fee.objects.all().delete()
                response_data['action'] = action
                response_data['Message'] = 'Se fue todo a la puta de {}'.format(table)
                return HttpResponse(json.dumps(response_data), content_type="application/json")

        

        response_data['action'] = 'Nada'
        response_data['Message'] = 'Nada pasó xd'
        return HttpResponse(json.dumps(response_data), content_type="application/json")


@method_decorator(csrf_exempt, name='dispatch')
class Fees(View):

    def get(self, request):
        
        cliente_pk = request.GET.get('cliente_pk')
        cliente_obj = Client.objects.get(pk=cliente_pk)
        amount_payable = request.GET.get('amount_payable')
        amount_fees = request.GET.get('amount_fees')
        date_created = request.GET.get('date_created')

        for c in range(int(amount_fees)):
            pay = Payment.create(amount_payable)
            pay.concept = 'Cuota de Producto Nº: '+str(c+1)
            pay.client = cliente_obj
            pay.fee = instance
            if c > 0:
                pay.date_expiration = datetime.now() + relativedelta(months=+c)
            pay.save()

        return HttpResponse("")


@method_decorator(csrf_exempt, name='dispatch')
class AquiPago(View):

    def get(self, request):
        tr_consultar = '05'
        response_data = {}
        detail_data = {}
        detail_data_record = []
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

                if tipoTrx == tr_consultar:
                    cliente = Client.objects.filter(document=nroDocumento).first()

                    if not cliente:
                        response_data['codRetorno'] = '002'
                        response_data['desRetorno'] = 'Cliente no registrado'
                        return HttpResponse(json.dumps(response_data), content_type="application/json")

                    payments = Payment.objects.filter(status = 'pe', client = cliente.pk)[:6]
                
                    if not payments:
                        response_data['codRetorno'] = '001'
                        response_data['desRetorno'] = 'No hay Ninguna deuda'
                        return HttpResponse(json.dumps(response_data), content_type="application/json")
                
                    response_data['codRetorno'] = '000'
                    response_data['desRetorno'] = 'Aprobado'
                    response_data['nombreApellido'] = cliente.first_name + ' ' + cliente.last_name
                    response_data['cantDetalles'] = str(payments.count())

                    for payment in payments:

                        detail_data['nroFactura'] = payment.id
                        detail_data['concepto'] = payment.concept
                        detail_data['importe'] = payment.mount
                        detail_data['fechaVencimiento'] = payment.date_expiration.strftime('%d/%m/%Y')
                        detail_data['moneda'] = '1'
                        detail_data_record.append(detail_data)
                        detail_data = {}

                    response_data['respConsultaDet'] = detail_data_record
                    return HttpResponse(json.dumps(response_data), content_type="application/json")

                        #else:
                        #    response_data['codRetorno'] = '002'
                        #    response_data['desRetorno'] = 'Fecha Vencida'
                        #    return HttpResponse(json.dumps(response_data), content_type="application/json")   
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
        #Se definen los codigos de los tipos de transacción
        tr_pagar = '03'
        tr_anular = '06'
        tr_revertir = '04'

        user = "test"
        pwd = "*123*"

        response_data = {}
        detail_data = {}
        today = timezone.now()

        received_json_data=json.loads(request.body)

        print('--------------------------')
        print(received_json_data)
        print('--------------------------')

        usuario = received_json_data['usuario']
        password = received_json_data['password']

        if usuario != user or password != pwd:
            response_data['codRetorno'] = '004'
            response_data['desRetorno'] = 'Credenciales incorrectas'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        tipoTrx = received_json_data['tipoTrx']

        #Tipo de Transaccion para Pagar
        if tipoTrx == tr_pagar:

            try:
                codServicio = received_json_data['codServicio']
                codTransaccion = received_json_data['codTransaccion']
                nroFactura = received_json_data['nroFactura']
                importe = received_json_data['importe']
                moneda = received_json_data['moneda']
                medioPago = received_json_data['medioPago']
            except:
                response_data['codRetorno'] = '006'
                response_data['desRetorno'] = 'Error en los parametros'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            
            if moneda != '1' or medioPago != '01':
                response_data['codRetorno'] = '003'
                response_data['desRetorno'] = 'Solo se aceptan pagos en Guaranies'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            #Se mapean los objetos que se van a utilizar
            payment = Payment.objects.get(id = nroFactura)
            cliente = Client.objects.get(id = payment.client.id)
            importeInt = int(importe)
            codTransaccionInt = int(codTransaccion)
            clienteNomApe = cliente.first_name + ' ' + cliente.last_name

            print('--------------------------')       
            print(payment)
            print(cliente)
            print('--------------------------')
            
            if payment.status == 'pe':
                if importeInt == payment.mount:
                    checkout,  created = Checkout.objects.get_or_create( payment = payment )

                    if created:
                        checkout.transaction = codTransaccionInt
                        checkout.mount = importeInt
                        checkout.save()

                        payment.status = 'pa'
                        payment.plataform = 'ap'
                        payment.save()

                        try:
                            fee = Fee.objects.get(id = payment.fee.pk)
                            fee.months_paid =+ 1
                            fee.save()
                        except:
                            pass
                        
                        response_data['codServicio'] = codServicio
                        response_data['tipoTrx'] = tr_pagar
                        response_data['codRetorno'] = '000'
                        response_data['desRetorno'] = 'APROBADO'

                        email = EmailMessage(
			                        "Pago de: {}".format(clienteNomApe),
			                        "Factura: {} \nCliente: {} \nCodTransaccion: {}".format(payment.id, clienteNomApe, codTransaccionInt),
			                        "no-reply@gmail.com",
			                        ["uverodevpy@gmail.com"],
			                        reply_to=[cliente.email]
                                    )
                            
                        try:
                            email.send()
                        except:
                            print('Correo no enviado')

                        return HttpResponse(json.dumps(response_data), content_type="application/json")

                else:
                    response_data['codRetorno'] = '005'
                    response_data['desRetorno'] = 'Monto distinto al ser pagado'
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
                                
            elif payment.status == 'pa':
                response_data['codRetorno'] = '004'
                response_data['desRetorno'] = 'Ya Pagado'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

        #Tipo de Transaccion para Anular el pago
        if tipoTrx == tr_anular:

            try:
                codServicio = received_json_data['codServicio']
                codTransaccion = received_json_data['codTransaccion']
                nroFactura = received_json_data['nroFactura']
                codTransaccionAnular = received_json_data['codTransaccionAnular']
            except:
                response_data['codRetorno'] = '006'
                response_data['desRetorno'] = 'Error en los parametros'
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        
            #Se mapean los objetos que se van a utilizar
            payment = Payment.objects.get(id = nroFactura)
            cliente = Client.objects.get(id = payment.client.id)
            codTransaccionInt = int(codTransaccion)
            clienteNomApe = cliente.first_name + ' ' + cliente.last_name

            print('--------------------------')       
            print(payment)
            print(cliente)
            print('--------------------------')

            if payment.status == 'pa':
                checkout,  created = Checkout.objects.get_or_create( payment = payment )

                if not created and checkout.transaction_anulate == None:
                    
                    checkout.transaction_anulate = int(codTransaccionAnular)
                    checkout.save()

                    payment.status = 'an'
                    payment.save()

                    try:
                        fee = Fee.objects.get(id = payment.fee.pk)
                        fee.months_paid =- 1
                        fee.save()
                    except:
                        pass

                    response_data['codServicio'] = codServicio
                    response_data['tipoTrx'] = tr_anular
                    response_data['codRetorno'] = '000'
                    response_data['desRetorno'] = 'APROBADO'

                    email = EmailMessage(
                            "Anulación de: {}".format(clienteNomApe),
                            "Factura: {} \nCliente: {} \nCodTransaccion: {}\nCodAnulacion {}".format(payment.id, clienteNomApe, codTransaccionInt, codTransaccionAnular),
                            "no-responder@uverodev.com",
                            ["contacto@uverodev.com"],
                            reply_to=[cliente.email]
                    )
                        
                    try:
                        email.send()
                        print('Correo enviado')
                    except:
                        print('Correo no enviado')

                    return HttpResponse(json.dumps(response_data), content_type="application/json")

        #Tipo de Transaccion para Revertir el anulado
        if tipoTrx == tr_revertir:

            try:
                codServicio = received_json_data['codServicio']
                codTransaccion = received_json_data['codTransaccion']
                nroFactura = received_json_data['nroFactura']
                codTransaccionAnular = received_json_data['codTransaccionAnular']
            except:
                response_data['codRetorno'] = '006'
                response_data['desRetorno'] = 'Error en los parametros'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            #Se mapean los objetos que se van a utilizar
            payment = Payment.objects.get(id = nroFactura)
            cliente = Client.objects.get(id = payment.client.id)
            codTransaccionInt = int(codTransaccion)
            clienteNomApe = cliente.first_name + ' ' + cliente.last_name

            print('--------------------------')       
            print(payment)
            print(cliente)
            print('--------------------------')

            if payment.status == 'an':
                checkout,  created = Checkout.objects.get_or_create( payment = payment )

                if not created and checkout.transaction_anulate == int(codTransaccionAnular):   
                    correo = None
                    checkout.transaction_anulate = None
                    checkout.transaction = codTransaccion
                    checkout.save()

                    payment.status = 're'
                    payment.save()

                    try:
                        fee = Fee.objects.get(id = payment.fee.pk)
                        fee.months_paid =- 1
                        fee.save()
                    except:
                        pass

                    response_data['codServicio'] = codServicio
                    response_data['tipoTrx'] = tr_revertir
                    response_data['codRetorno'] = '000'
                    response_data['desRetorno'] = 'APROBADO'

                    email = EmailMessage(
                        "Reversión de: {}".format(clienteNomApe),
                        "Factura: {} \nCliente: {} \nCodTransaccion: {}\nCodAnulacion: {}".format(payment.id, clienteNomApe, codTransaccionInt, codTransaccionAnular),
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

        response_data['codRetorno'] = '999'
        response_data['desRetorno'] = 'Error en el proceso'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
                    
        