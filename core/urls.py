from django.urls import path
from .views import Index, AquiPago, Fees, AdminRequest

urlpatterns = [
    path('', Index.as_view(), name='home'),
    path('api/aquipago/', AquiPago.as_view(), name='aquipago'),
    path('api/admin-request/', AdminRequest.as_view(), name='admin_request'),
    path('make-fees/', Fees.as_view(), name='make_fees'),
]