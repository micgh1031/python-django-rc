from apps.message.models import MessageUsersAction, Messages
from django.conf import settings
from wsi.utils import datetime_to_seconds
from django.utils.timezone import datetime


def is_deleted(message, reply_id, user):
    message_action = MessageUsersAction.objects.filter(message=message, replies=-1, modifier=user).first()
    if message_action:
        return True
    else:
        if reply_id is not -1:
            message_action = MessageUsersAction.objects.filter(message=message, replies=reply_id, modifier=user).first()
            if message_action:
                return True
        return False


def is_spam(plate, place_id, user):
    int_limits = settings.SPAM_RESTRICTS.get(user.plan, 5)
    message = Messages.objects.filter(sender=user).order_by('-created')[int_limits-1:int_limits]
    if message.__len__() > 0:
        current_session_started = datetime_to_seconds(message[0].created)
        current_time = datetime_to_seconds(datetime.now())
        time_diff = current_time - current_session_started
        if time_diff <= settings.SPAM_FILTER_INTERVAL:
            return 1    # sender reaches limitation

    message = Messages.objects.filter(place_id=place_id, plate=plate).order_by('-created')[int_limits-1:int_limits]
    if message.__len__() > 0:
        current_session_started = datetime_to_seconds(message[0].created)
        current_time = datetime_to_seconds(datetime.now())
        time_diff = current_time - current_session_started
        if time_diff <= settings.SPAM_FILTER_INTERVAL:
            return 2    # Plate owner reaches limitation
    return 0
