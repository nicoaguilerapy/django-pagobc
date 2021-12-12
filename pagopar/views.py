from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from datetime import date, datetime, timedelta
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import hashlib
from django.utils.timezone import now
import requests
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from core.models import *
from pagopar.models import FormaPago, Pago
from profiles.models import Ciudad, Departamento, Profile
from django.views import View
import json
from django.http import JsonResponse
import urllib.request

token_privado = 'b3a23b044e9de4f3740d2a4d552beea4'
token_publico = 'd25f1939a677b4dc9dc95426bf836f30'
time_compared = timedelta(hours=24)

@csrf_exempt
def create_payment(request):
    if request.method == 'POST':
        received_json_data=json.loads(request.body)
        print(received_json_data)

        client_obj = Client.objects.get(id = received_json_data['id_client'])
        payment_obj = Payment.objects.get(id = received_json_data['id_payment'])
        formapago_obj = FormaPago.objects.get(identificador = received_json_data['id_identificador'])

        #generar token
        text = "{}{}{}".format(token_privado, payment_obj.ref_code, payment_obj.mount)
        token_compra = hashlib.sha1(text.encode('utf-8')).hexdigest()

        #Json 
        response_data = {}
        comprador = {}
        compra_items = {}
        items = []

        response_data['token'] = token_compra

        comprador['ruc'] = ''
        comprador['email'] = client_obj.email
        comprador['ciudad'] = ''
        comprador['nombre'] = '{} {}'.format(client_obj.first_name, client_obj.last_name)
        comprador['telefono'] = client_obj.phone1
        comprador['direccion'] = ''
        comprador['documento'] = client_obj.document
        comprador['coordenadas'] = ''
        comprador['razon_social'] = '{} {}'.format(client_obj.first_name, client_obj.last_name)
        comprador['tipo_documento'] = 'CI'
        comprador['direccion_referencia'] = ''

        response_data['comprador'] = comprador

        response_data['public_key'] = token_publico
        response_data['monto_total'] = payment_obj.mount
        response_data['tipo_pedido'] = 'VENTA-COMERCIO'

        compra_items = {}
        compra_items['ciudad'] = 1
        compra_items['nombre'] = payment_obj.concept
        compra_items['cantidad'] = 1
        compra_items['categoria'] = "909"
        compra_items['public_key'] = token_publico
        compra_items['url_imagen'] = ''
        compra_items['descripcion'] = payment_obj.concept
        compra_items['id_producto'] = payment_obj.id
        compra_items['precio_total'] = payment_obj.mount
        compra_items['vendedor_telefono'] = ''
        compra_items['vendedor_direccion'] = ''
        compra_items['vendedor_direccion_referencia'] = ''
        compra_items['vendedor_direccion_coordenadas'] = ''
        items.append(compra_items)
        response_data['compras_items'] = items

        date_time = now() + time_compared

        response_data['fecha_maxima_pago'] = payment_obj.date_expiration.strftime("%Y-%m-%d %H:%M:%S")
        response_data['id_pedido_comercio'] = payment_obj.ref_code
        response_data['descripcion_resumen'] = ''

        r = requests.post('https://api.pagopar.com/api/comercios/1.1/iniciar-transaccion', data =json.dumps(response_data))

        if r.json()['respuesta'] == False:
            print(r.json()['resultado'])
            print(response_data)

            return JsonResponse({"cod": "500", "message": "Error en el Request"}, status=200, safe=False)
        else:
            #cambiar a pedido completado
            print()
            print("hash del pedido")
            print(r.json()['resultado'][0]['data'])
            print()

            return JsonResponse({"cod":"000","message": "Pago creado con éxito", "identificador": formapago_obj.identificador, "token_pagopar": r.json()['resultado'][0]['data']}, status=200, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class PagoparRequest(View):
    def post(self, request):
        received_json_data=json.loads(request.body)
        print(received_json_data['resultado'])
        
        hash_pedido = received_json_data['resultado'][0]['hash_pedido']
        try:
            payment_obj = Payment.objects.get(hash_code = hash_pedido)
        except:
            return JsonResponse(received_json_data['resultado'], status=200, safe=False)

        token_compra = payment_obj.hash_code

        text = "{}{}".format(token_privado, token_compra)
        token = hashlib.sha1(text.encode('utf-8')).hexdigest()

        token_consulta = received_json_data['resultado'][0]['token']
        if(token != token_consulta):
            return JsonResponse({"cod": "501", "message": "Error de Token"}, status=200)

        pago, pago_created = Pago.objects.get_or_create( hash_pedido = hash_pedido )
        checkout,  checkout_created = Checkout.objects.get_or_create( payment = payment_obj )

        if pago_created:
            pago.pagado = received_json_data['resultado'][0]['pagado']
            pago.forma_pago = received_json_data['resultado'][0]['forma_pago']
            pago.monto = received_json_data['resultado'][0]['monto']
            pago.fecha_maxima_pago = received_json_data['resultado'][0]['fecha_maxima_pago']
            pago.hash_pedido = received_json_data['resultado'][0]['hash_pedido']
            pago.numero_pedido = received_json_data['resultado'][0]['numero_pedido']
            pago.forma_pago_identificador = received_json_data['resultado'][0]['forma_pago_identificador']
            pago.payment = payment_obj
            pago.save()
            print()
            print(pago)
            print()

            if checkout_created:
                checkout.transaction = "000{}".format(pago.id)
                checkout.mount = int(float(pago.monto))
                checkout.owner = payment_obj.owner
                checkout.company = payment_obj.company 
                checkout.save()
                payment_obj.status = 'PC'
                payment_obj.save()
                print()
                print(checkout)
                print()

           
        else:
            pago.pagado = received_json_data['resultado'][0]['pagado']
            if not checkout_created:
                checkout.transaction = "000"+pago.id
                checkout.mount = int(pago.monto)
                checkout.owner = payment_obj.owner
                checkout.company = payment_obj.company 
                checkout.save()
                payment_obj.status = 'PA'
                payment_obj.save()


        

        text = "{}{}".format(token_privado, "CONSULTA")
        token_consulta = hashlib.sha1(text.encode('utf-8')).hexdigest()

        r2 = requests.post('https://api.pagopar.com/api/pedidos/1.1/traer', data =json.dumps({"hash_pedido": pago.hash_pedido, "token": token_consulta, "token_publico": token_publico}))
        
        print('Comprobar Pago')
        print(r2.json())
            
        return JsonResponse(received_json_data['resultado'], status=200, safe=False)
    
    def get(self, request, **kwargs):
        return redirect('my_cart')

class SuccessfulPayment(View):    
    def get(self, request, **kwargs):

        text = "{}{}".format(token_privado, "CONSULTA")
        token_consulta = hashlib.sha1(text.encode('utf-8')).hexdigest()

        r = requests.post('https://api.pagopar.com/api/pedidos/1.1/traer', data =json.dumps({"hash_pedido": request.GET.get('h'), "token": token_consulta, "token_publico": token_publico}))
        
        print(r.json())
        return render(request,'pagopar/successful_payment.html', {})

         



        

        


        

        


