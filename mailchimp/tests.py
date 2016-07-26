import urllib
import datetime
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from mailchimp.views import WebHook

class FakeConnection(object):
    def get_list_by_id(self, list_id):
        return None


class NoConnectionWebHook(WebHook):
    WEBHOOK_KEY = '1'
    connection = FakeConnection()


class WebhookTestCase(TestCase):
    fired_at = datetime.datetime(2009, 3, 26, 21, 35, 57)
    groups = ['Group1', 'Group2']
    data = {
        'subscribe': {
            "type": "subscribe",
            "fired_at": "2009-03-26 21:35:57",
            "data[id]": "8a25ff1d98",
            "data[list_id]": "a6b5da1054",
            "data[email]": "api@mailchimp.com",
            "data[email_type]": "html",
            "data[merges][EMAIL]": "api@mailchimp.com",
            "data[merges][FNAME]": "MailChimp",
            "data[merges][LNAME]": "API",
            "data[merges][INTERESTS]": ','.join(groups),
            "data[ip_opt]": "10.20.10.30",
            "data[ip_signup]": "10.20.10.30",
        },
        'unsubscribe': {
            "type": "unsubscribe",
            "fired_at": "2009-03-26 21:40:57",
            "data[action]": "unsub",
            "data[reason]": "manual",
            "data[id]": "8a25ff1d98",
            "data[list_id]": "a6b5da1054",
            "data[email]": "api+unsub@mailchimp.com",
            "data[email_type]": "html",
            "data[merges][EMAIL]": "api+unsub@mailchimp.com",
            "data[merges][FNAME]": "MailChimp",
            "data[merges][LNAME]": "API",
            "data[merges][INTERESTS]": "Group1,Group2",
            "data[ip_opt]": "10.20.10.30",
            "data[campaign_id]": "cb398d21d2",
            "data[reason]": "hard"
        },
        'profile': {
            "type": "profile",
            "fired_at": "2009-03-26 21:31:21",
            "data[id]": "8a25ff1d98",
            "data[list_id]": "a6b5da1054",
            "data[email]": "api@mailchimp.com",
            "data[email_type]": "html",
            "data[merges][EMAIL]": "api@mailchimp.com",
            "data[merges][FNAME]": "MailChimp",
            "data[merges][LNAME]": "API",
            "data[merges][INTERESTS]": "Group1,Group2",
            "data[ip_opt]": "10.20.10.30"
        },
        'upemail': {
            "type": "upemail",
            "fired_at": "2009-03-26\ 22:15:09",
            "data[list_id]": "a6b5da1054",
            "data[new_id]": "51da8c3259",
            "data[new_email]": "api+new@mailchimp.com",
            "data[old_email]": "api+old@mailchimp.com"
        },
        'cleaned': {
            "type": "cleaned",
            "fired_at": "2009-03-26 22:01:00",
            "data[list_id]": "a6b5da1054",
            "data[campaign_id]": "4fjk2ma9xd",
            "data[reason]": "hard",
            "data[email]": "api+cleaned@mailchimp.com"
        }
    }

    def setUp(self):
        self.webhook = NoConnectionWebHook()
        self.url = reverse('mailchimp_webhook', kwargs={'key': '1'})
        self.request_factory = RequestFactory()

    def test_subscribe(self):
        from mailchimp.signals import mc_subscribe
        handler, handler_kwargs = self._get_signal_handler()
        mc_subscribe.connect(handler)
        request = self.request_factory.post(self.url, self.data['subscribe'])
        self.webhook(request, key='1')
        self.assertEqual(handler_kwargs['type'], 'subscribe')
        self.assertEqual(handler_kwargs['fired_at'], self.fired_at)
        self.assertEqual(handler_kwargs['interests'], self.groups)

    def test_unsubscribe(self):
        from mailchimp.signals import mc_unsubscribe
        handler, handler_kwargs = self._get_signal_handler()
        mc_unsubscribe.connect(handler)
        request = self.request_factory.post(self.url, self.data['unsubscribe'])
        self.webhook(request, key='1')
        self.assertEqual(handler_kwargs['type'], 'subscribe')
        self.assertEqual(handler_kwargs['fired_at'], self.fired_at)
        self.assertEqual(handler_kwargs['interests'], self.groups)

    def _get_signal_handler(self):
        handler_kwargs = {}
        def handler(**kwargs):
            handler_kwargs.update(**kwargs)
        return handler, handler_kwargs


