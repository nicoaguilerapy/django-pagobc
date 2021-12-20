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



x = FormaPago.objects.get(forma_pago__icontains = 'Bancard').identificador

z = x.replace("Bancard - ", "")
print(z)



