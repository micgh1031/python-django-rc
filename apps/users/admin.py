from django.contrib import admin
from apps.users.models import User, UserProfile, ClientSession, UserTerms, UserPushToken, UserPhoneVerify, UserBlocked

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(ClientSession)
admin.site.register(UserTerms)
admin.site.register(UserPushToken)
admin.site.register(UserPhoneVerify)
admin.site.register(UserBlocked)

