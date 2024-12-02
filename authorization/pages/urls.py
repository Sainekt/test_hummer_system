from django.urls import path
from .views import (
    AuthorizationFormView,
    ConfirmFormView,
    SuccessView,
    LogoutView
)

app_name = 'pages'

urlpatterns = [
    path('', AuthorizationFormView.as_view(), name='auth_form'),
    path('confirm/', ConfirmFormView.as_view(), name='confirm_form'),
    path('success/', SuccessView.as_view(), name='success'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
