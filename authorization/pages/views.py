from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView, UpdateView

from users.utils import create_user_or_confirm_cod

from .forms import ConfirmCodeForm, PhoneLoginForm, UpdateUserForm

User = get_user_model()


class AuthorizationFormView(FormView):
    template_name = 'pages/authorization_from.html'
    form_class = PhoneLoginForm
    success_url = reverse_lazy('pages:confirm_form')

    def form_valid(self, form):
        region, phone_number = form.cleaned_data
        sms = create_user_or_confirm_cod(phone_number, region)
        self.request.session['phone_number'] = phone_number
        self.request.session['sms'] = sms
        return super().form_valid(form)


class ConfirmFormView(FormView):
    template_name = 'pages/confirm_form.html'
    form_class = ConfirmCodeForm
    success_url = reverse_lazy('pages:success')

    def get_initial(self):
        initial = super().get_initial()
        initial['phone_number'] = self.request.session.get('phone_number', '')
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.initial['phone_number'] = self.request.session.get(
            'phone_number', '')
        return form

    def form_valid(self, form):
        user = form.cleaned_data['user']
        login(self.request, user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sms'] = self.request.session.get('sms')
        return context


class SuccessView(UpdateView):
    template_name = 'pages/success.html'
    model = User
    form_class = UpdateUserForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('pages:auth_form'))
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        invited = User.objects.filter(invite_code=user.referal_code)
        context['invited'] = invited
        context['user'] = self.request.user
        return context

    def get_success_url(self) -> str:
        return reverse_lazy('pages:success')


class LogoutView(RedirectView):
    url = reverse_lazy('pages:auth_form')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)
