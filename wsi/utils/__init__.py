import base64
from logging import info as i
import random
from uuid import uuid4
from django.conf import settings
from django.utils.timezone import utc, datetime

from wsi.settings import APN_CERT, APN_KEY, APN_SANDBOX

from apns import APNs, Payload, Frame


def datetime_to_seconds(date):
    return (date.replace(tzinfo=utc) - datetime(1970, 1, 1).replace(tzinfo=utc)).total_seconds()


def date_to_timestamp(dt):
    if not dt:
        return None
    return (dt - datetime(1970, 1, 1).replace(tzinfo=utc)).total_seconds()


def key_from_jsonparam(key):
    # return ndb.Key(encoded=base64.urlsafe_b64decode(str(param)))
    return base64.urlsafe_b64decode(str(key))


def key_to_jsonparam(key):
    # return key.urlsafe()
    return base64.urlsafe_b64encode(str(key))


def check_credential_session_key_rotation(auth_obj):
    """"
	# Return True in case new session key have been generated, False otherwise
	"""
    ## check if key rotation is needed
    session_created = auth_obj.session_created
    ## current session start time in seconds
    current_session_started = datetime_to_seconds(session_created)
    current_time = datetime_to_seconds(datetime.now())
    time_diff = current_time - current_session_started
    i("")
    i("Session keys timedifference in seconds : " + str(time_diff) +
      " session key rotation time interval : " + str(settings.SESSION_KEY_ROTATION_TIME_INTERVAL))
    i("")
    if time_diff > settings.SESSION_KEY_ROTATION_TIME_INTERVAL:
        i("")
        i(" Rotating session key for username : " + auth_obj.name)
        i("")
        ## generate new session key
        auth_obj.session_key = generate_session_key()
        auth_obj.challenge = generate_challenge()
        auth_obj.session_created = datetime.now()
        auth_obj.save()
        return True
    else:
        return False


def generate_challenge():
    return '%030x' % random.randrange(16 ** 30)


def generate_session_key():
    return str(uuid4())


def load_apn():
    return APNs(use_sandbox=APN_SANDBOX, cert_file=APN_CERT, key_file=APN_KEY)
