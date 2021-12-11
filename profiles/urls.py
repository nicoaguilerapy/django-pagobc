from django.urls import path, include
from . import views
from .views import  ajax_address, create_user


urlpatterns = [
    path('ajax/address/', ajax_address, name='ajax_address'),
    path('create/', create_user, name='create_user'),
]