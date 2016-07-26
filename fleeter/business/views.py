from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse
import csv
from logging import error as e


class DashboardView(TemplateView):
    template_name = 'pages/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['page'] = 'index'
        return context

    def dispatch(self, *args, **kwargs):
        return super(DashboardView, self).dispatch(*args, **kwargs)


class PlatesView(TemplateView):
    template_name = 'pages/plates/index.html'

    def get_context_data(self, **kwargs):
        context = super(PlatesView, self).get_context_data(**kwargs)
        context['page'] = 'plates'
        return context

    def dispatch(self, *args, **kwargs):
        return super(PlatesView, self).dispatch(*args, **kwargs)


class PlatesEditView(TemplateView):
    template_name = 'pages/plates/edit.html'

    def get_context_data(self, **kwargs):
        context = super(PlatesEditView, self).get_context_data(**kwargs)
        context['page'] = 'plates'
        return context

    def dispatch(self, *args, **kwargs):
        return super(PlatesEditView, self).dispatch(*args, **kwargs)


class PlatesUploadView(TemplateView):
    template_name = 'pages/plates/upload.html'

    def get_context_data(self, **kwargs):
        context = super(PlatesUploadView, self).get_context_data(**kwargs)
        context['page'] = 'plates'
        return context

    def dispatch(self, *args, **kwargs):
        return super(PlatesUploadView, self).dispatch(*args, **kwargs)


class CompanyView(TemplateView):
    template_name = 'pages/company/index.html'

    def get_context_data(self, **kwargs):
        context = super(CompanyView, self).get_context_data(**kwargs)
        context['page'] = 'company'
        return context

    def dispatch(self, *args, **kwargs):
        return super(CompanyView, self).dispatch(*args, **kwargs)


class CompanyBillingView(TemplateView):
    template_name = 'pages/company/billing.html'

    def get_context_data(self, **kwargs):
        context = super(CompanyBillingView, self).get_context_data(**kwargs)
        context['page'] = 'company'
        return context

    def dispatch(self, *args, **kwargs):
        return super(CompanyBillingView, self).dispatch(*args, **kwargs)
