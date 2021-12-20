import json
from django.contrib.sites.models import Site
from django.forms.forms import Form
from clients.models import Client
from core.models import Payment
from pagopar.models import *
import time
from django.utils.timezone import now, localtime
from datetime import *
from datetime import timedelta
from django.utils.timezone import make_aware
import requests
from profiles.models import Empresa
from django.utils import timezone
import pytz
from django.utils.timezone import make_aware


today = now()
m = today.month
y = today.year
for i in range(5):
    m = m + 1
    if m <= 12 :
        date1 = "{}/{}/{}".format(15, m, y)
        new_date = make_aware(datetime.strptime(date1, '%d/%m/%Y'))
        hoy = localtime(new_date).replace(hour=23, minute=59, second=59, microsecond=0)
        if m == 12:
            y = y + 1
    else:
        m = m - 12
        date1 = "{}/{}/{}".format(15, m, y)
        new_date = make_aware(datetime.strptime(date1, '%d/%m/%Y'))
        hoy = localtime(new_date).replace(hour=23, minute=59, second=59, microsecond=0)
    
    print(hoy)
