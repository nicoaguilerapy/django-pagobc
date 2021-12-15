from core.models import Payment
import time
from django.utils.timezone import now
from datetime import *
from datetime import timedelta
from django.utils.timezone import make_aware


list = Payment.objects.all()
for x in  Payment.objects.all():
    x.date_created = now()
    x.date_expirtion = now()
    x.save()
    
date = '22-05-2018'
pay.date_created = make_aware(datetime.strptime(date, '%d-%m-%Y'))
print(pay.date_created.strftime("%d-%m-%Y"))
