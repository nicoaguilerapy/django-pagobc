from django.contrib import admin
from .models import Pago, FormaPago
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class PagoAdmin(admin.ModelAdmin):
    search_fields = ('id', 'pagado', 'forma_pago', 'numero_pedido', 'hash_pedido', 'get_order')
    list_display = ( 'id', 'pagado', 'forma_pago', 'numero_pedido', 'hash_pedido', 'get_order')

admin.site.register(Pago, PagoAdmin)

class FormaPagoResource(resources.ModelResource):
    class Meta:
        model = FormaPago

class FormaPagoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ('id', 'identificador', 'forma_pago', )
    list_display = ('id', 'identificador', 'forma_pago',)
    resourse_class = FormaPagoResource

admin.site.register(FormaPago, FormaPagoAdmin)

