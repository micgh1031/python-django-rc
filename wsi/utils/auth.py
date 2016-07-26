import random
from uuid import uuid4
from django.conf import settings
from django.utils import timezone
from wsi.utils import datetime_to_seconds
from logging import error as e

from apps.users.models import UserBlocked
from apps.message.models import MessageUsersAction


def generate_challange():
    return '%030x' % random.randrange(16 ** 30)


def generate_session_key():
    return str(uuid4())


def generate_claim_camera_token():
    return str(uuid4())


def check_credential_session_key_rotation(auth):
    "Return True in case new session key have been generated, False otheerwise"
    session_created = auth.session_created
    current_session_started = datetime_to_seconds(session_created)
    current_time = datetime_to_seconds(timezone.now())
    time_diff = current_time - current_session_started
    e("check_credential_session_key_rotation - Start")
    e("Session keys timedifference in seconds : " + str(time_diff) +
      " session key rotation time interval : " + str(settings.SESSION_KEY_ROTATION_TIME_INTERVAL))
    e("" . auth.session_key)
    '''
    if (time_diff > settings.SESSION_KEY_ROTATION_TIME_INTERVAL):
        e("Token has been expired and needs to rotate")
        e(" Rotating session key for username : " + auth.name)
        e("")
        ## generate new session key
        # auth.session_key = generate_session_key()
        # auth.challange = generate_challange()
        # auth.session_created = timezone.now()
        # auth.save()
        return True
    else:
        return False
    '''
    if not auth.session_key:
        return False
    else:
        return True


def report_block(user):
    blocked = UserBlocked.objects.filter(user=user)
    if blocked.__len__() > 0:
        return True
    else:
        user.is_active = False
        user.save()

        blocked = UserBlocked(user=user)
        blocked.save()
        return True


def IsMessageDeleted(message):
    if message:
        message_deleted = MessageUsersAction.objects.filter(message=message)
        if message_deleted:
            return True
        else:
            return False
    else:
        return True


def reactive_user(user):
    user.is_active = True
    user.save()
    return True
