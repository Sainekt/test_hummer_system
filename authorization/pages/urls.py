from django.urls import path
from .views import AuthorizationFormView, ConfirmFormView

app_name = 'pages'

urlpatterns = [
    path('', AuthorizationFormView.as_view(), name='auth_form'),
    path('confirm/', ConfirmFormView.as_view(), name='confirm_form')
]
