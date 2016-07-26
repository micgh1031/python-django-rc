from django.contrib import admin
from apps.message.models import Messages, MessageReplies, AbusiveReport, MessageUsersAction

# Register your models here.
admin.site.register(Messages)
admin.site.register(MessageReplies)
admin.site.register(AbusiveReport)
admin.site.register(MessageUsersAction)
