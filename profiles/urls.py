from django.urls import path, include
from . import views
from .views import ProfileUpdate, ajax_address


urlpatterns = [
    path('me/', ProfileUpdate.as_view(), name='my_profile'),
    path('ajax/address/', ajax_address, name='ajax_address'),
]