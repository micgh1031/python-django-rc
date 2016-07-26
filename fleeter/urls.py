from django.conf.urls import include, url
import os
from fleeter.views import IndexView
from fleeter.account.views import LoginView, LogoutView

urlpatterns = [
    url(r'^biz/', include('fleeter.business.urls')),
    url(r'^account/', include('fleeter.account.urls')),

    url(r'^login/$', LoginView.as_view(), name='fleeter.login'),
    url(r'^logout/$', LogoutView.as_view(), name='fleeter.logout'),

    # url(r'^subscribe/', include('subscription.urls')),


    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': os.path.join(os.path.dirname(__file__), 'static')}),

    url('^.*$', IndexView.as_view(), name='fleeter.index'),
]
