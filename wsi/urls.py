"""wsi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
import os
from dashboard import views as DashboardViews

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v2/', include('apps.users.urls'), name="user"),
    url(r'^api/v2/', include('apps.vehicles.urls'), name="vehicles"),
    url(r'^api/v2/', include('apps.message.urls'), name="messages"),

    # Dashboard urls
    url(r'^login/$', DashboardViews.AdminLoginView.as_view(), name="dashboard.login"),
    url(r'^logout/$', DashboardViews.AdminLogoutView.as_view(), name="dashboard.logout"),
    url(r'^messages/', DashboardViews.AdminMessagesView.as_view(), name='dashboard.messages'),
    url(r'^users/', DashboardViews.AdminUsersView.as_view(), name='dashboard.users'),
    url(r'^blacklist/', DashboardViews.AdminBlacklistView.as_view(), name='dashboard.blacklist'),

    url(r'^dashboard/', include('dashboard.urls'), name='dashboard'),

    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': os.path.join(os.path.dirname(__file__), 'static')}),

    url(r'^$', DashboardViews.AdminIndexView.as_view(), name="dashboard.index"),
]
