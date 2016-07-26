from wsi.utils.views import UserAuthView, GeneralWSIViewMixin
from apps.message.models import Messages, MessageReplies, MessageUsersAction
from apps.vehicles.models import Vehicles
from apps.message.utils import is_deleted, is_spam
from django.views.generic import TemplateView
from django.shortcuts import render_to_response
from django.conf import settings
from gcm import *
from logging import error as e

from apps.users.models import UserProfile, UserPushToken

from apns import APNs, Frame, Payload

from wsi.utils import load_apn


class MessagesView(UserAuthView):
    http_method_names = ['POST', 'GET', 'PUT', 'DELETE']

    def dispatch(self, request, *args, **kwargs):
        super(MessagesView, self).dispatch(request, *args, **kwargs)

        auth = self.auth
        params = self.json_params
        mid = params.get('mid', '')

        if request.method == 'GET':
            if mid:
                message_data = Messages.objects.get(pk=mid)
                reply_dict = list()
                replies = MessageReplies.objects.filter(message=message_data)

                for reply in replies:
                    reply_dict.append({
                        'reply_id': reply.pk,
                        'user_id': reply.receipt.challenge,
                        'display_name': reply.receipt.display_name,
                        'text': reply.text,
                        'deleted': is_deleted(reply.message, reply.pk, auth),
                        'created': reply.date_created
                    })
                vehicle = Vehicles.objects.filter(plate=message_data.plate).filter(
                    place_id=message_data.place_id).first()
                data = {
                    'mid': message_data.id,
                    'user_id': message_data.sender.challenge,
                    'user_name': message_data.sender.display_name,
                    'recpt_id': vehicle.user.challenge if vehicle else '',
                    'recpt_name': vehicle.user.display_name if vehicle else '',
                    'vid': message_data.vid,
                    'text': message_data.text,
                    'user_plate': message_data.plate,
                    'country': message_data.country,
                    'state': message_data.state,
                    'location': message_data.location,
                    'identify': message_data.identify,
                    'latitude': message_data.latitude,
                    'longitude': message_data.longitude,
                    'created': message_data.date_created,
                    'deleted': is_deleted(message_data, -1, auth),
                    'replies': reply_dict
                }

                if message_data:
                    return self.serve_result({'result': data})
                else:
                    return self.serve_result({'result': {}})
            else:
                ret_dict = list()
                message_data = Messages.objects.all()
                for line in message_data:
                    replies = MessageReplies.objects.filter(message=line)
                    reply_dict = list()
                    for reply in replies:
                        reply_dict.append({
                            'reply_id': reply.pk,
                            'user_id': reply.receipt.challenge,
                            'display_name': reply.receipt.display_name,
                            'text': reply.text,
                            'created': reply.date_created,
                            'deleted': is_deleted(reply.message, reply.pk, auth),
                        })
                    vehicle = Vehicles.objects.filter(plate=line.plate).filter(place_id=line.place_id).first()
                    data = {
                        '_id': line.id,
                        'mid': line.id,
                        'user_id': line.sender.challenge,
                        'user_name': line.sender.display_name,
                        'recpt_id': vehicle.user.challenge if vehicle else '',
                        'recpt_name': vehicle.user.display_name if vehicle else '',
                        'vid': line.vid,
                        'text': line.text,
                        'user_plate': line.plate,
                        'country': line.country,
                        'state': line.state,
                        'location': line.location,
                        'identify': line.identify,
                        'latitude': line.latitude,
                        'longitude': line.longitude,
                        'created': line.date_created,
                        'replies': reply_dict,
                        'deleted': is_deleted(line, -1, auth),
                    }
                    ret_dict.append(data)
                return self.serve_result({'result': ret_dict})

        elif request.method == 'POST':
            message = Messages(sender=auth)

            user_plate = params.get('plate', '').upper()
            user_place_id = params.get('plate_place_id', '')

            if not user_place_id and not user_plate:
                return self.error('Invalid plate and place id')

            # Spam filter
            ispam = is_spam(user_plate, user_place_id, auth)
            if ispam == 1:  # sender reached message limit
                return self.error(
                    "You have reached your 5 messages per hour limit. Please wait around an hour before continuing. If you need more sending capacity, see Windshieldink's Pager business service for reference.")
            elif ispam == 2:  # plate owner reached message limit
                return self.error(
                    "The vehicle you are trying to message has reached its 5 messages per hour limit. Please wait around an hour before trying again.")

            message.plate = params.get('plate', '').upper()
            message.place_id = params.get('plate_place_id', '')
            message.country = params.get('country', '')
            message.state = params.get('state', '')
            message.location = params.get('user_sharelocation', False)
            message.identify = params.get('identify', False)
            message.longitude = params.get('user_longitude', '')
            message.latitude = params.get('user_latitude', '')
            message.text = params.get('text', '')
            message.save()
            message_reply = MessageReplies(message=message, text=message.text, receipt=auth)
            message_reply.save()

            vehicle = Vehicles.objects.filter(place_id=message.place_id).filter(plate=message.plate).first()

            data = {
                'user_id': str(auth.challenge),
                'user_name': auth.display_name,
                'user_plate': params.get('plate', '').upper(),
                'rcpt_id': str(vehicle.user.challenge) if vehicle else '',
                'rcpt_name': vehicle.user.display_name if vehicle else '',
                'rcpt_plate': params.get('plate', '').upper() if vehicle else '',
                'country': params.get('country', ''),
                'state': params.get('state', ''),
                'location': params.get('location', ''),
                'identify': params.get('identify', ''),
                'latitude': params.get('latitude', ''),
                'longitude': params.get('longitude', ''),
                'place_id': params.get('plate_place_id', ''),
                'text': message.text,
                'created': message.date_created,
                'deleted': False,
                'replies': [{
                    'reply_id': message_reply.pk,
                    'user_id': message_reply.receipt.challenge,
                    'display_name': message_reply.receipt.display_name,
                    'text': message_reply.text,
                    'deleted': False,
                    'created': message_reply.date_created
                }]
            }

            return self.serve_result({'result': data})

        elif request.method == 'DELETE':
            chat_id = params.get('mid')
            message = Messages.objects.filter(pk=int(chat_id)).first()
            if message:
                message_action = MessageUsersAction.objects.filter(modifier=auth, message=message, replies=-1).first()

                if not message_action:
                    message_action = MessageUsersAction(modifier=auth, message=message, replies=-1)
                    message_action.save()

            return self.ok()

        else:
            return self.error('Method not allowed', 405)


class RepliesView(UserAuthView):
    http_method_names = ['GET', 'POST', 'DELETE']

    def dispatch(self, request, *args, **kwargs):
        super(RepliesView, self).dispatch(request, *args, **kwargs)

        auth = self.auth
        params = self.json_params
        reply_id = params.get('reply_id', None)
        mid = params.get('mid', None)

        if request.method == 'POST':
            if mid:
                message = Messages.objects.get(pk=int(mid))
                message_reply = MessageReplies(message=message)
                message_reply.text = params.get('text', '')
                message_reply.receipt = auth
                message_reply.save()
                plate_owner = Vehicles.objects.filter(pk=message.vid).first().user

                # send push notification
                if message.sender.pk == auth.pk:
                    receipt = plate_owner
                    sender = auth
                else:
                    sender = auth
                    receipt = message.sender
                # send SMS notification
                profile = UserProfile.objects.get(user=receipt)
                sender_profile = UserProfile.objects.get(user=sender)

                e("{sender} replies to {receiver}".format(sender=sender.email, receiver=receipt.email))
                if profile:
                    try:
                        # if profile.send_push:
                        gcm = GCM(settings.GCM_TOKEN, debug=False)
                        user_push_tokens = UserPushToken.objects.filter(user=receipt).all()
                        data = {
                            'message': message_reply.text,
                            'sender': sender.display_name,
                            'plate': message.plate,
                            'type': 'chat',
                            'msgid': message.id
                        }
                        try:
                            apn = load_apn()
                        except:
                            apn = None
                            pass

                        for user_push_token in user_push_tokens:
                            if user_push_token.device:
                                try:
                                    response = gcm.plaintext_request(registration_id=user_push_token.push_token, data=data)
                                except:
                                    pass
                            else:
                                try:
                                    if apn:
                                        payload = Payload(alert='Windshieldink', custom=data)
                                        apn.gateway_server.send_notification(user_push_token.push_token, payload)
                                    else:
                                        e("APN Object is Null")
                                except:
                                    pass

                        e("{receipt} got a push notification".format(receipt=receipt.email))
                    except:
                        e("Failed to send GCM message {receipt}".format(receipt=receipt.email))
                        pass

                return self.serve_result({'result': {
                    'reply_id': message_reply.pk,
                    'user_id': message_reply.receipt.challenge,
                    'display_name': message_reply.receipt.display_name,
                    'text': message_reply.text,
                    'deleted': False,
                    'created': message_reply.date_created
                }})
            else:
                return self.error("Invalid arguments, please check mid")
        elif request.method == 'DELETE':
            if reply_id:
                reply = MessageReplies.objects.filter(pk=int(reply_id)).first()
                if reply:
                    message_action = MessageUsersAction.objects.filter(modifier=auth, message=reply.message,
                                                                       replies=reply.pk)
                    if not message_action:
                        message_action = MessageUsersAction(modifier=auth, message=reply.message, replies=reply.pk)
                        message_action.save()

                return self.ok()
            else:
                return self.error('Invalid reply id')
        elif request.method == 'GET':
            if reply_id:
                reply = MessageReplies.objects.get(pk=int(reply_id))
                message = reply.message

                vehicle = Vehicles.objects.filter(plate=message.plate).filter(place_id=message.place_id).first()
                data = {
                    'mid': message.id,
                    'user_id': message.sender.challenge,
                    'user_name': message.sender.display_name,
                    'recpt_id': vehicle.user.challenge if vehicle else '',
                    'recpt_name': vehicle.user.display_name if vehicle else '',
                    'vid': message.vid,
                    'text': message.text,
                    'user_plate': message.plate,
                    'country': message.country,
                    'state': message.state,
                    'location': message.location,
                    'identify': message.identify,
                    'latitude': message.latitude,
                    'longitude': message.longitude,
                    'created': message.date_created,
                    'deleted': is_deleted(message=message, user=auth, reply_id=-1),
                }

                reply_dict = {
                    'reply_id': reply.pk,
                    'user_id': reply.receipt.challenge,
                    'display_name': reply.receipt.display_name,
                    'text': reply.text,
                    'created': reply.date_created,
                    'deleted': is_deleted(message=message, user=auth, reply_id=reply.pk),
                    'message': data
                }

                return self.serve_result({'result': reply_dict})
            else:
                return self.error('Invalid reply_id')
        else:
            return self.error('Invalid http request')


class MessageLocation(TemplateView):
    template_name = "googlemap.html"

    def get(self, request, *args, **kwargs):
        return render_to_response(self.template_name, {
            'latitude': request.GET.get('latitude', ''),
            'longitude': request.GET.get('longitude', '')
        })
