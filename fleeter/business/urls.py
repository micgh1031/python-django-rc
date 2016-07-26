from django.conf.urls import url

from fleeter.business.views import DashboardView, PlatesView, CompanyView, \
    PlatesEditView, CompanyBillingView, PlatesUploadView


urlpatterns = [
    url(r'^dashboard/$', DashboardView.as_view(), name="biz.dashboard"),
    url(r'^plates/$', PlatesView.as_view(), name="biz.plates"),
    url(r'^plates/(?P<pk>[0-9]+)/$', PlatesEditView.as_view(), name="biz.plates.edit"),
    url(r'^plates/upload/$', PlatesUploadView.as_view(), name="biz.plates.upload"),
    url(r'^company/$', CompanyView.as_view(), name="biz.company"),
    url(r'^company/(?P<pk>[0-9]+)/$', CompanyBillingView.as_view(), name="biz.company.billing"),
]
