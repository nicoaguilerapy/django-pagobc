from django.urls import path, include
from . import views
from .views import  ajax_address


urlpatterns = [
    path('ajax/address/', ajax_address, name='ajax_address'),
]