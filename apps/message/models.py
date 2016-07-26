from django.db import models
from apps.users.models import User
import time


class Messages(models.Model):
    country = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    location = models.BooleanField(blank=True, default=False)
    identify = models.BooleanField(blank=True, default=False)
    latitude = models.CharField(max_length=255, blank=True, null=True)
    longitude = models.CharField(max_length=255, blank=True, null=True)
    plate = models.CharField(max_length=255, null=True, blank=True)
    place_id = models.CharField(max_length=255, null=True, blank=True)
    vid = models.IntegerField(default=-1, blank=True)
    text = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    sender = models.ForeignKey(User, name="sender", null=True, blank=True)

    @property
    def date_created(self):
        return int(time.mktime(self.created.timetuple()))

    def set_vehicle(self, vid):
        self.vid = vid


class MessageReplies(models.Model):
    message = models.ForeignKey(Messages, related_name="message_id")
    text = models.TextField(null=True, blank=True)
    receipt = models.ForeignKey(User, name="receipt", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def date_created(self):
        return int(time.mktime(self.created.timetuple()))


class MessageUsersAction(models.Model):
    message = models.ForeignKey(Messages, null=True)
    replies = models.IntegerField(default=-1, blank=True)
    modifier = models.ForeignKey(User, name="modifier", null=True, blank=True)
    modified = models.DateTimeField(auto_now_add=True, blank=True)

    @property
    def date_modified(self):
        return int(time.mktime(self.modified.timetuple()))


class MessageHistory(models.Model):
    plate = models.CharField(max_length=255, blank=True, null=True)
    place_id = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, related_name="message_history_user")
    created = models.DateTimeField(auto_now_add=True, blank=True)

    @property
    def date_created(self):
        return int(time.mktime(self.created.timetuple()))


class AbusiveReport(models.Model):
    reporter = models.ForeignKey(User, null=True, related_name='abusive_reporter')
    created = models.DateTimeField(auto_now_add=True, blank=True)
    modified = models.DateTimeField(auto_now_add=True, blank=True)
    message = models.ForeignKey(Messages, null=True, blank=True)
    status = models.CharField(max_length=10, default='Pending', blank=True)
