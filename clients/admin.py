from django.contrib import admin
from .models import Client

class ClientAdmin(admin.ModelAdmin):
	search_fields = ['document', 'first_name', 'last_name', 'region', 'phone1', 'phone2', 'email']
	list_display = ( 'document', 'last_name', 'first_name','region', 'phone1')

admin.site.register(Client, ClientAdmin)
