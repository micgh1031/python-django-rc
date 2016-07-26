from django.contrib.auth import get_user_model
from django.forms import ModelForm
from apps.vehicles.models import Vehicles


class VehicleForm(ModelForm):

    class Meta:
        model = Vehicles
        exclude = ('user',)
