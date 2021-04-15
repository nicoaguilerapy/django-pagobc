from django.contrib import admin
from .models import Payment, Checkout, Fee

class PaymentAdmin(admin.ModelAdmin):
	search_fields = ['status', 'plataform']
	list_display = ('id', 'client', 'mount', 'status', 'plataform', )
	
	def get_readonly_fields(self, request, obj = None):
		if request.user.groups.filter(name="Personal").exists() and obj is not None:
			if obj.status == 'pa':
				return ('client','concept', 'mount', 'status', 'plataform', 'fee', 'date_created','date_expiration', )
		
		return ('date_created','date_expiration', 'fee')
	
	def has_delete_permission(self, request, obj = None):
		return request.user.is_superuser	

class CheckoutAdmin(admin.ModelAdmin):
	readonly_fields = ('payment', 'mount','transaction',  'transaction_anulate' ,'date_created')
	search_fields = ['transaction', 'transaction_anulate', ]
	list_display = ( 'payment', 'transaction', 'transaction_anulate', )

class FeeAdmin(admin.ModelAdmin):
	readonly_fields = ('date_created','months_paid',)
	#search_fields = ['transaction_anulate', 'transaction']
	list_display = ( 'client', 'amount_payable', 'months_paid', 'amount_fees',)


admin.site.register(Checkout, CheckoutAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Fee, FeeAdmin)
