from django.urls import path
from .views import Index, Consult, Fees

urlpatterns = [
    path('', Index.as_view(), name='home'),
    path('api/aquipago/', Consult.as_view(), name='consult'),
    path('make-fees/', Fees.as_view(), name='make_fees'),
]