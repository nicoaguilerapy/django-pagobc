from django.urls import path, include
from . import views
from .views import  ajax_address, profile_create, profile_list, profile_update


urlpatterns = [
    path('ajax/address/', ajax_address, name='ajax_address'),
    path('create/', profile_create, name='profile_create'),
    path('update/<int:id>/', profile_update, name='profile_update'),
    path('list/', profile_list, name='profile_list'),
]