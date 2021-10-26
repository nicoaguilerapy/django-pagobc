from django.contrib import admin
from .models import Payment, Checkout, Fee
from django.urls import reverse
from django.utils.html import format_html

class PaymentAdmin(admin.ModelAdmin):
	search_fields = ['status', 'plataform']
	list_display = ('id', 'client', 'mount', 'status', 'plataform', 'link_to_checkout')

	def link_to_checkout(self, obj):
		checkout = Checkout.objects.get(payment = obj.pk)
		link = reverse("admin:core_checkout_change", args=[checkout.pk])
		return format_html('<a href="{}">Ver {}</a>', link, checkout.transaction)
	link_to_checkout.short_description = 'Ver Transaccion'
	
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
	list_display = ( 'transaction' , 'transaction_anulate', 'link_to_payment',)

	def link_to_payment(self, obj):
		payment = Payment.objects.get(pk = obj.payment.pk)
		link = reverse("admin:core_payment_change", args=[obj.payment.pk])
		return format_html('<a href="{}">Ver {}</a>', link, obj.payment.pk)
	link_to_payment.short_description = 'Ver Pago'

class FeeAdmin(admin.ModelAdmin):
	readonly_fields = ('date_created','months_paid',)
	list_display = ( 'client', 'amount_payable', 'months_paid', 'amount_fees',)
	


admin.site.register(Checkout, CheckoutAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Fee, FeeAdmin)
