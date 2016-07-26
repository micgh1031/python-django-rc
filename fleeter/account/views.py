from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView, View, FormView, RedirectView
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from fleeter.account.forms import CustomUserCreationForm, CustomUserLoginForm


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class UserCreateView(FormView):
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = '/business/choose_plan/'

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        context = self.get_context_data(**kwargs)
        context['form'] = form
        if form.is_valid():
            account = form.save(commit=False)
            account.is_active = True
            account.save()

            user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1']
            )

            login(self.request, user)
            # write_log(user, 'Registered user - {email}'.format(email=user.email))
            return HttpResponseRedirect(self.success_url)
        else:
            messages.error(self.request, 'Invalid form data!')
            return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        form = self.form_class
        return self.render_to_response({'form': form})


class LoginView(FormView):
    form_class = CustomUserLoginForm
    template_name = 'users/login.html'
    success_url = '/business/choose_plan/'

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context['page'] = 'login'
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        context = self.get_context_data(**kwargs)
        context['form'] = form

        if form.is_valid():
            account = authenticate(
                email=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )

            if account is not None:
                if account.is_active:
                    login(request, account)

                    # write_log(account, 'Logged in from {email}'.format(email=account.email))

                    return HttpResponseRedirect(self.success_url)
                else:
                    messages.error(self.request, 'Not activated account!')
                    return self.render_to_response(context)
            else:
                messages.error(self.request, 'Invalid email or password')
                return self.render_to_response(context)
        else:
            messages.error(self.request, 'Invalid form data')
            return self.render_to_response(context)


class LogoutView(LoginRequiredMixin, RedirectView):
    url = '/'

    def get(self, request, *args, **kwargs):
        # write_log(request.user, '{email} logged out'.format(email=request.user.email))
        logout(request)

        return super(LogoutView, self).get(request, *args, **kwargs)


class ProfileView(TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['page'] = 'settings'
        return context


class ChoosePlanView(TemplateView):
    template_name = 'users/pricing_table.html'

    def get_context_data(self, **kwargs):
        context = super(ChoosePlanView, self).get_context_data(**kwargs)
        context['page'] = 'settings'
        return context


class AddCustomerView(TemplateView):
    template_name = 'users/add.html'

    def get_context_data(self, **kwargs):
        context = super(AddCustomerView, self).get_context_data(**kwargs)
        context['page'] = 'settings'
        return context
