from wsi.utils.views import UserAuthView
from apps.vehicles.models import Vehicles
from apps.vehicles.forms import VehicleForm
from logging import error as e


class Vehicle(UserAuthView):
    http_method_names = ['GET', 'POST', 'DELETE']
    form_class = VehicleForm

    def dispatch(self, request, *args, **kwargs):
        super(Vehicle, self).dispatch(request, *args, **kwargs)

        auth = self.auth

        params = self.json_params
        vehicle_id = params.get('vid', None)
        if request.method == 'GET':
            if vehicle_id:
                vehicle = Vehicles.objects.get(pk=vehicle_id)
                if vehicle:
                    ret = {
                        '_id': vehicle.pk,
                        'vid': vehicle.pk,
                        'year': vehicle.year,
                        'make': vehicle.make,
                        'model': vehicle.model,
                        'make_id': vehicle.make_id,
                        'model_id': vehicle.model_id,
                        'plate': vehicle.to_plate,
                        'secondary_email': vehicle.secondary_email,
                        'vin': vehicle.vin,
                        'color': vehicle.color,
                        'state': vehicle.state,
                        'country': vehicle.country,
                        'place_id': vehicle.place_id,
                        'formatted_address': vehicle.formatted_address,
                        'is_fleeter': vehicle.is_fleeter,
                        'user_id': vehicle.user.challenge
                    }
                    return self.serve_result({'result': ret})
                else:
                    return self.serve_result({'result': {}})
            else:
                vehicles = Vehicles.objects.filter(user=auth).all()
                ret_data = list()
                for vehicle in vehicles:
                    ret_data.append({
                        '_id': vehicle.pk,
                        'vid': vehicle.pk,
                        'year': vehicle.year,
                        'make': vehicle.make,
                        'model': vehicle.model,
                        'make_id': vehicle.make_id,
                        'model_id': vehicle.model_id,
                        'plate': vehicle.to_plate,
                        'vin': vehicle.vin,
                        'color': vehicle.color,
                        'secondary_email': vehicle.secondary_email,
                        'state': vehicle.state,
                        'country': vehicle.country,
                        'place_id': vehicle.place_id,
                        'formatted_address': vehicle.formatted_address,
                        'is_fleeter': vehicle.is_fleeter,
                        'user_id': vehicle.user.challenge
                    })
                return self.serve_result({'result': ret_data})
        elif request.method == 'POST':
            form = self.form_class(params)
            if form.is_valid():
                vehicles = form.save(commit=False)
                if not vehicle_id:
                    cv = Vehicles.objects.filter(plate=vehicles.plate.upper()).filter(place_id=vehicles.place_id)
                    if cv:
                        return self.error('Plate exists already')
                else:
                    old_v = Vehicles.objects.get(pk=int(vehicle_id))
                    if not ((old_v.plate.upper() == vehicles.plate.upper()) and (old_v.place_id == vehicles.place_id)):
                        cv = Vehicles.objects.filter(plate=vehicles.plate).filter(place_id=vehicles.place_id)
                        if cv:
                            return self.error('Plate exists already')
                    vehicles.pk = int(vehicle_id)
                vehicles.user = auth
                vehicles.plate = vehicles.plate.upper()
                vehicles.save()

                # Check messages

                ret = {
                    '_id': vehicles.id,
                    'vid': vehicles.id,
                    'year': vehicles.year,
                    'make': vehicles.make,
                    'model': vehicles.model,
                    'make_id': vehicles.make_id,
                    'model_id': vehicles.model_id,
                    'plate': vehicles.to_plate,
                    'vin': vehicles.vin,
                    'secondary_email': vehicles.secondary_email,
                    'color': vehicles.color,
                    'state': vehicles.state,
                    'country': vehicles.country,
                    'place_id': vehicles.place_id,
                    'formatted_address': vehicles.formatted_address,
                    'is_fleeter': vehicles.is_fleeter,
                    'user_id': vehicles.user.challenge
                }
                return self.serve_result({'result': ret})
            else:
                return self.error('NOT APPLICABLE')
        elif request.method == 'DELETE':
            vehicles = Vehicles.objects.filter(pk=int(vehicle_id)).filter(user=auth).first()
            if vehicles:
                vehicles.delete()
                return self.ok()
            return self.error('NOT APPLICABLE')
        else:
            return self.error('Bad Request')


class VehicleVerify(UserAuthView):
    http_method_names = ['GET', 'POST']

    def dispatch(self, request, *args, **kwargs):
        super(VehicleVerify, self).dispatch(request, *args, **kwargs)

        auth = self.auth

        params = self.json_params

        plate = params.get('plate', '')
        place_id = params.get('place_id', '')
        if auth and plate and place_id:
            vehicle = Vehicles.objects.filter(plate=plate.upper()).filter(place_id=place_id).first()
            if vehicle:
                ret = {
                    '_id': vehicle.id,
                    'vid': vehicle.id,
                    'year': vehicle.year,
                    'make': vehicle.make,
                    'model': vehicle.model,
                    'make_id': vehicle.make_id,
                    'model_id': vehicle.model_id,
                    'plate': vehicle.to_plate,
                    'vin': vehicle.vin,
                    'secondary_email': vehicle.secondary_email,
                    'color': vehicle.color,
                    'state': vehicle.state,
                    'country': vehicle.country,
                    'place_id': vehicle.place_id,
                    'formatted_address': vehicle.formatted_address,
                    'is_fleeter': vehicle.is_fleeter,
                    'user_id': vehicle.user.challenge
                }

                return self.serve_result({'result': ret})
            else:
                return self.serve_result({'result': {}})

        return self.serve_result({'result': {}})
