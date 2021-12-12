from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('payment/', create_payment, name='create_payment'),
    path('api/result/', PagoparRequest.as_view(), name='pagopar_request'),
    path('api/result/hash/', SuccessfulPayment.as_view(), name='pagopar_success'),
]