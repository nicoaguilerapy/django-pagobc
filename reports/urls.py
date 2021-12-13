from django.urls import path, include
from . import views
from .views import *



urlpatterns = [
    path('checkout/', report_checkout, name='report_checkout'),
    path('payment/', report_payment, name='report_payment'),
]