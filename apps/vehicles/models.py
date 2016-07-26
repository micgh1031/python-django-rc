from django.db import models
from apps.users.models import User, UserProfile, UserPushToken
from apps.users.utils import send_mail_template
from apps.message.models import Messages
from apps.message.utils import is_deleted
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from logging import error as e
from django.conf import settings
from twilio.rest import TwilioRestClient
from gcm import *

from wsi.utils import load_apn

from apns import Payload


class Vehicles(models.Model):
    year = models.CharField(max_length=10, null=True, blank=True)
    make = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    make_id = models.CharField(max_length=100, null=True, blank=True)
    model_id = models.CharField(max_length=100, null=True, blank=True)
    plate = models.CharField(max_length=255, null=True, blank=True)
    vin = models.CharField(max_length=255, null=True, blank=True)
    color = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    place_id = models.CharField(max_length=255, null=True, blank=True)
    formatted_address = models.CharField(max_length=255, null=True, blank=True)
    secondary_email = models.CharField(max_length=100, null=True, blank=True)
    is_fleeter = models.BooleanField(default=True)
    user = models.ForeignKey(User, related_name='vehicle_owner')

    @property
    def to_plate(self):
        return self.plate.upper()


@receiver(post_save, sender=Vehicles, dispatch_uid="update_vehicle_message")
def update_message(sender, instance, **kwargs):
    messages = Messages.objects.filter(plate=instance.plate, place_id=instance.place_id).all()
    for message in messages:
        if message.vid == -1:
            message.vid = instance.pk
            message.save()


@receiver(pre_save, sender=Messages, dispatch_uid="before_add_new_message")
def set_vehicle_id(sender, instance, **kwargs):
    vehicle = Vehicles.objects.filter(plate=instance.plate, place_id=instance.place_id).first()
    if vehicle:
        instance.vid = vehicle.pk


@receiver(post_save, sender=Messages, dispatch_uid="after_add_new_message")
def notify_to_receiver(sender, instance, **kwargs):
    # send notification to the vehicle owner
    message = instance
    if message.vid > 0 and is_deleted(message=message, reply_id=-1, user=message.sender) is False:
        vehicle = Vehicles.objects.get(pk=message.vid)
        receipt = vehicle.user
        sender = message.sender
        # send SMS notification
        profile = UserProfile.objects.get(user=receipt)
        sender_profile = UserProfile.objects.get(user=sender)

        if profile:
            message_data = render_to_string('email_template/messages/license_sms.txt',
                                            {
                                                'message': "{message}".format(message=message.text),
                                                'plate': "{plate}".format(plate=message.plate),
                                                'signature': "{sign}".format(sign=sender_profile.signature) if sender_profile and sender_profile.signature and message.identify else ''
                                            })
            # send push notification
            try:
                if profile.send_push:
                    gcm = GCM(settings.GCM_TOKEN, debug=False)
                    user_push_tokens = UserPushToken.objects.filter(user=receipt).all()
                    data = {
                        'message': message.text,
                        'sender': sender.display_name,
                        'plate': message.plate,
                        'type': 'msg',
                        'msgid': message.id
                    }
                    try:
                        apn = load_apn()
                    except:
                        apn = None
                        e("apn is None")
                        pass

                    for user_push_token in user_push_tokens:
                        if user_push_token.device:
                            try:
                                response = gcm.plaintext_request(registration_id=user_push_token.push_token, data=data)
                            except:
                                e("Vehicle: GCM Fail to {email} - {token}".format(
                                    email=receipt.email,
                                    token=user_push_token.push_token
                                ))
                                pass
                        else:
                            try:
                                if apn:
                                    payload = Payload(alert='Windshieldink', custom=data)
                                    apn.gateway_server.send_notification(user_push_token.push_token, payload)
                            except:
                                e("Vehicle: APN Fail to {email} - {token}".format(
                                    email=receipt.email,
                                    token=user_push_token.push_token
                                ))
                                pass
            except:
                e("Failed to send GCM message")
                pass

            send_sms = profile.send_sms
            # valid_phone = rcpt_user_data.get('valid_phone')
            try:
                if send_sms and profile.valid_phone and receipt.phone_verified:
                    twilio_client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    twilio_client.messages.create(
                        to=profile.valid_phone,
                        from_=settings.TWILIO_DEFAULT_CALLERID,
                        body=message_data
                    )
            except:
                e("Failed to send SMS")
                pass
            # send email notification
            try:
                if profile.send_email:
                    subject = "Windshieldink: A New Message Has Been Sent To Your License Plate"
                    send_mail_template(
                        settings.ADMIN_MESSENGER_EMAIL,
                        receipt.email,
                        subject,
                        'email_template/messages/license_email',
                        {
                            'display_name': receipt.display_name,
                            'plate': message.plate,
                            'message': message.text,
                            'gps_coords': "http://{serv}/api/v2/location?latitude={lat}&longitude={lng}".format(
                                serv=settings.SERVER_HOST_NAME,
                                lat=message.latitude,
                                lng=message.longitude) if (message.latitude) and (message.longitude) and (message.location) else '',
                            'signature': "{sign}".format(sign=sender_profile.signature) if sender_profile and sender_profile.signature and message.identify else ''
                        })

                    if vehicle.secondary_email:
                        send_mail_template(
                            settings.ADMIN_MESSENGER_EMAIL,
                            vehicle.secondary_email,
                            subject,
                            'email_template/messages/license_email',
                            {
                                'display_name': receipt.display_name,
                                'plate': message.plate,
                                'message': message.text,
                                'gps_coords': "http://{serv}/api/v2/location?latitude={lat}&longitude={lng}".format(
                                    serv=settings.SERVER_HOST_NAME,
                                    lat=message.latitude,
                                    lng=message.longitude) if (message.latitude) and (message.longitude) and (message.location) else '',
                                'signature': "{sign}".format(sign=sender_profile.signature) if sender_profile and sender_profile.signature and message.identify else ''
                            })
            except:
                e("Failed to send message notification to Vehicle owner")
                pass
