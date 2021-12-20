from django.urls import path
from .views import BlankPage, home, checkout_list, fee_create, fee_list, payment_create, payment_hide, payment_list, payment_update

urlpatterns = [
    path('', home, name='home'),
    path('404/', BlankPage.as_view(), name='blank'),

    path('payment/create/', payment_create, name='payment_create'),
    path('payment/list/', payment_list, name='payment_list'),
    path('payment/update/<int:id>/', payment_update, name='payment_update'),
    path('payment/hide/', payment_hide, name='payment_hide'),

    path('fee/create/', fee_create, name='fee_create'),
    path('fee/list/', fee_list, name='fee_list'),

    path('checkout/list/', checkout_list, name='checkout_list'),
    path('checkout/list/', checkout_list, name='checkout_list'),

]