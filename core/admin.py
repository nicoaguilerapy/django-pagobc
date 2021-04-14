from django.contrib import admin
from .models import Payment, Checkout, Fee

class PaymentAdmin(admin.ModelAdmin):
	search_fields = ['status', 'plataform']
	list_display = ('id', 'client', 'mount', 'status', 'plataform', )
	
	def get_readonly_fields(self, request, obj = None):
		if request.user.groups.filter(name="Personal").exists() and obj is not None:
			if obj.status == 'pa':
				return ('date_created','date_expiration', 'status', 'plataform', 'mount', 'concept', 'client', 'fee')
		
		return ('date_created','date_expiration', 'fee')
	
	def has_delete_permission(self, request, obj = None):
		return request.user.is_superuser

	

class CheckoutAdmin(admin.ModelAdmin):
	readonly_fields = ('mount','transaction_anulate', 'transaction', 'payment')
	search_fields = ['transaction_anulate', 'transaction']
	list_display = ( 'payment', 'transaction', 'transaction_anulate',)


admin.site.register(Checkout, CheckoutAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Fee)
