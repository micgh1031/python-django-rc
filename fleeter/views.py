from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator


class FrontendViewMixin(TemplateView):
    template_name = 'fleeter/pages/dashboard.html'
    page = 'index'

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['page'] = self.page
        return context

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(FrontendViewMixin, self).dispatch(*args, **kwargs)


class IndexView(FrontendViewMixin):
    template_name = 'pages/onboard.html'
    page = 'index'
