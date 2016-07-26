from django.conf.urls import url

from fleeter.account.views import ProfileView, UserCreateView, ChoosePlanView, AddCustomerView


urlpatterns = [
    url(r'^profile/$', ProfileView.as_view(), name="fleeter.user.profile"),
    url(r'^register/$', UserCreateView.as_view(), name="fleeter.user.signup"),
    url(r'^plans/$', ChoosePlanView.as_view(), name="fleeter.user.plans"),
    url(r'^add/$', AddCustomerView.as_view(), name="fleeter.user.addcustomer")
]
