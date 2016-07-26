from django.conf.urls import url
from apps.vehicles.views import Vehicle, VehicleVerify

urlpatterns = [
    url(r'^vehicles', Vehicle.as_view(), name='vehicles_main'),
    url(r'^vehicle_verify', VehicleVerify.as_view(), name='vehicles_verify'),
]
