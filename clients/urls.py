from django.urls import path
from .views import *

urlpatterns = [

    path('create/', client_create, name='client_create'),
    path('update/<int:id>/', client_update, name='client_update'),
    path('list/', client_list, name='client_list'),

]