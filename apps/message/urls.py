from django.conf.urls import url
from apps.message.views import MessagesView, RepliesView, MessageLocation

urlpatterns = [
    url(r'^messages', MessagesView.as_view(), name='messages_main'),
    url(r'^reply', RepliesView.as_view(), name='reply_main'),
    url(r'^location', MessageLocation.as_view(), name='message_location'),
]
