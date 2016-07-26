import mandrill
from django.conf import settings
import uuid
from django.template.loader import render_to_string
import mailchimp

import random

import logging


def mail_send(to, subject, message) :
    mandrill_client = mandrill.Mandrill(settings.MANDRILL_ACCOUNT)
    try :
        result = mandrill_client.messages.send({
            'from_name' : 'WindshieldInk',
            'from_email' : settings.ADMIN_NOREPLY_EMAIL,
            'to' : [{'email': to}],
            'bcc' : [{'email': settings.ADMIN_EMAIL}],
            'subject' : subject,
            'message' : message,
            'html' : message,
            'async' : True,
        })
    except mandrill.Error, e:
        print 'send failed %s - %s' % (e.__class__, e)
        pass

    return result


def send_mail_template(from_email, to, subject, temp, param):
    mandrill_client = mandrill.Mandrill(settings.MANDRILL_ACCOUNT)
    html_temp = "{0}.html".format(temp)
    text_temp = "{0}.txt".format(temp)

    if from_email is None:
        from_email = settings.FROM_EMAIL
    try:
        result = mandrill_client.messages.send({
            'from_name': 'WindshieldInk',
            'from_email': from_email,
            'to': [{'email': to}],
            'preserve_recipients': True,
            'cc': [{'email': settings.ADMIN_EMAIL}],
            'subject': subject,
            'message': render_to_string(text_temp, param),
            'html': render_to_string(html_temp, param),
            'async': True,
        })
    except mandrill.Error, e :
        print 'send failed %s - %s' % (e.__class__, e)
        pass

    return result


def generate_rand_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4())  # Convert UUID format to a Python string.
    random = random.upper()  # Make all characters uppercase.
    random = random.replace("-", "")  # Remove the UUID '-'.
    return random[0:string_length]  # Return the random string.


def generate_rand_number(size=6):
    return ''.join(random.choice('0123456789') for _ in range(size))


def newsletter_subscribe(user):
    b_subscribed = True
    try:
        lists = mailchimp.utils.get_connection().get_list_by_id(settings.MAILCHIMP_LISTID)
        lists.subscribe(user.email, {'EMAIL': user.email, 'FNAME': user.display_name})
    except:
        b_subscribed = False
        pass

    return b_subscribed


def newsletter_unscribe(user):
    b_ret = True
    try:
        lists = mailchimp.utils.get_connection().get_list_by_id(settings.MAILCHIMP_LISTID)
        lists.unsubscribe(user.email, {'EMAIL': user.email})
    except:
        b_ret = False
        pass

    return b_ret
