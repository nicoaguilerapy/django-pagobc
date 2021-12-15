from django.urls import path
from .views import consult_aquipago, consult_pagoexpress

urlpatterns = [
    path('aquipago/<int:id>/', consult_aquipago, name='consult_aquipago'),
    path('pagoexpress/<int:id>/', consult_pagoexpress, name='consult_pagoexpress'),

]