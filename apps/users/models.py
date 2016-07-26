import time
from annoying.fields import JSONField
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.users.utils import mail_send
from wsi.utils import datetime_to_seconds
from datetime import datetime


class User(AbstractUser):
    """
    Extending custom user EmailUser model
    """
    phone_number = models.CharField(max_length=20, blank=True)
    challenge = models.CharField(max_length=100, blank=True)
    deleted = models.BooleanField(default=False)
    abusive = models.BooleanField(default=False)
    display_name = models.CharField(max_length=64, null=True, blank=True)
    roles = models.CharField(max_length=127, null=True, blank=True)
    plan = models.CharField(max_length=30, null=True, blank=True, default='first')
    tos = models.CharField(max_length=32, default='1.0', blank=True)

    phone_verified = models.BooleanField(default=False, blank=True)

    is_admin = models.BooleanField(default=False, blank=True)

    fb_id = models.CharField(max_length=256, blank=True, null=True)
    fb_token = models.CharField(max_length=256, blank=True, null=True)

    session_key = models.CharField(max_length=100, blank=True)
    session_created = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def get_full_name(self):
        return self.display_name

    get_full_name.short_description = 'Full name'

    @property
    def name(self):
        return self.email

    @property
    def nounce(self):
        return self.challenge

    @property
    def date_created(self):
        if self.created:
            return int(time.mktime(self.created.timetuple()))
        else:
            return 0

    def is_blocked(self):
        blocked = UserBlocked.objects.filter(user=self).first()
        if blocked is not None:
            return True
        else:
            return False

    def send_email_to(self, subject, message):
        mail_send(self.email, subject, message)
        return True

    def get_profile(self):
        profile = UserProfile.objects.filter(user=self).first()
        return profile

    def to_json(self):
        profile = UserProfile.objects.filter(user=self).first()
        return {
            '_id': self.challenge,
            'email': self.email,
            'display_name': self.display_name,
            'active': self.is_active,
            'nonce': self.challenge,
            'token': self.session_key,
            'city': profile.city,
            'province': profile.province,
            'formatted_user_address': profile.formatted_user_address,
            'country': profile.country,
            'phone_verified': self.phone_verified,
            'is_active': self.is_active,
            'is_blocked': self.is_blocked(),
            'created': int(time.mktime(self.created.timetuple())),
            'recv_email': profile.send_email,
            'phone': profile.valid_phone,
            'recv_push': profile.send_push,
            'recv_sms': profile.send_sms,
            'signature': profile.signature
        }

    def to_fb_json(self):
        return dict(
            email=self.email,
            fb_id=self.fb_id,
            first_name=self.first_name,
            last_name=self.last_name,
            fb_token=self.fb_token,
            created=int(time.mktime(self.created.timetuple())),
            token=self.session_key,
            active=self.is_active
        )


class UserCommand(models.Model):
    user = models.ForeignKey(User, related_name='gcm_command')
    utc_expiry = models.DateTimeField()
    payload = JSONField(blank=True, null=True)


class UserProfile(models.Model):
    user = models.ForeignKey(User, related_name='owner')
    send_sms = models.BooleanField(default=False)
    send_email = models.BooleanField(default=False)
    send_newsletter = models.BooleanField(default=False)
    valid_phone = models.CharField(max_length=100, default='', blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    province = models.CharField(max_length=255, null=True, blank=True)
    formatted_user_address = models.CharField(max_length=255, null=True, blank=True)
    send_push = models.BooleanField(default=False)
    signature = models.CharField(max_length=255, null=True, blank=True, default='')
    user_place_id = models.CharField(max_length=255, null=True, blank=True)


class ClientSession(models.Model):
    owner = models.ForeignKey(User, related_name='client_session')
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    session_key = models.CharField(max_length=100, blank=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    logged_in = models.DateTimeField(blank=True, null=True)
    logged_out = models.DateTimeField(blank=True, null=True)


class UserTerms(models.Model):
    version = models.CharField(max_length=10, default='1.0', null=True, blank=True)
    modified = models.DateTimeField(auto_now_add=True, blank=True)


class UserPushToken(models.Model):
    user = models.ForeignKey(User, related_name="owner_device_token")
    push_token = models.CharField(max_length=1024, blank=True, null=True)
    device = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)

    @property
    def date_created(self):
        return int(time.mktime(self.created.timetuple()))


class UserPhoneVerify(models.Model):
    user = models.ForeignKey(User, null=True, related_name='phone_verify_user')
    verify_code = models.CharField(max_length=10, blank=True, null=True)
    last_time = models.DateTimeField(auto_now_add=True, blank=True)

    def has_expired(self):
        last_trytime = datetime_to_seconds(self.last_time)
        current_time = datetime_to_seconds(datetime.now())

        if (last_trytime - current_time) > settings.PHONE_VERIFY_INTERVAL:
            return True
        else:
            return False


class UserBlocked(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)


class UserAudit(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    audit_type = models.CharField(max_length=10, null=True, blank=True, default='Custom')
    detail = models.CharField(max_length=1024, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        ordering = ['-created']
