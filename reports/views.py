from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage, send_mail
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from io import BytesIO
import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from core.models import Checkout, Payment
from profiles.models import Profile
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
from django.utils.timezone import now
from datetime import *
from datetime import timedelta

@login_required()
def report_checkout(request):
    template_path = 'reports/checkout.html'
    context = {}
    

    sum1 = 0
    cant1 = 0
    com = 0
    today = now()

    list = Checkout.objects.all()
    
    checkout_list = []

    for x in list:
        if x.date_created.month == today.month and x.transaction_anulate == None:
            checkout_list.append(x)
            sum1 = sum1 + x.mount
            com = com + (x.mount/100)*x.commission 
            cant1 = cant1 + 1

    context['checkout_list'] = checkout_list
    context['monto_total'] = sum1
    context['comision'] = com
    context['ingreso_real'] = sum1 - com

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report_checkout.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required()
def report_payment(request):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    template_path = 'reports/payment.html'
    context = {}


    list = Payment.objects.filter(status = 'PP', company = profile.company)

    payments = Payment.objects.filter(status = 'PP', company = profile.company)
    sum1 = 0
    cant1 = 0
    today = now()
    payment_list = []
    
    for x in list:
        if today.month == x.date_expiration.month:
            payment_list.append(x)
            sum1 = sum1 + x.mount
            cant1 = cant1 + 1

    context['payment_list'] = payment_list
    context['pagos_pendientes_monto'] = sum1
    context['pagos_pendientes_cantidad'] = cant1


    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report_payment.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response