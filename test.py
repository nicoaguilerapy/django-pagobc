from clients.models import Client
from core.models import Payment
import time
from django.utils.timezone import now
from datetime import *
from datetime import timedelta
from django.utils.timezone import make_aware

from profiles.models import Empresa


empresa_obj = Empresa.objects.get(id = 1)
client_obj = Client.objects.filter(type_document = 'CI', document = '43034s89', company = empresa_obj).first()
print(client_obj)
