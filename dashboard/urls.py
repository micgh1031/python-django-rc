from django.conf.urls import url
from dashboard import views as DashboardViews

urlpatterns = [
    url(r'^set_block/', DashboardViews.AdminMessagesView.as_view(), name='dashboard.set_block'),
    url(r'^abusive/', DashboardViews.AdminAbusiveView.as_view(), name='dashboard.abusive'),
    url(r'^license_plates/', DashboardViews.AdminLicensePlatesView.as_view(), name='dashboard.license_plates'),
    url(r'^notice/', DashboardViews.AdminNoticeView.as_view(), name='dashboard.notice'),
]
