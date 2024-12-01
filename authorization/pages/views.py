from django.shortcuts import render
from django.views.generic import FormView, DetailView
from django.conf import settings
from .forms import PhoneLoginForm, ConfirmCodeForm
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from users.utils import create_user_or_confirm_cod

User = get_user_model()


class AuthorizationFormView(FormView):
    template_name = 'pages/authorization_from.html'
    form_class = PhoneLoginForm
    success_url = reverse_lazy('pages:confirm_form')

    def form_valid(self, form):
        region, phone_number = form.cleaned_data
        create_user_or_confirm_cod(phone_number, region)
        return super().form_valid(form)


class ConfirmFormView(FormView):
    template_name = 'pages/confirm_form.html'
    form_class = ConfirmCodeForm
    success_url = reverse_lazy('pages:success')
