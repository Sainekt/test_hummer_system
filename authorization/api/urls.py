from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import UserViewSet, RequestSMSCodeView, VerifySMSCodeView

app_name = 'api_v1'

Router = DefaultRouter if settings.DEBUG else SimpleRouter

router_v1 = Router()
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'request-sms', RequestSMSCodeView, basename='request_sms')
router_v1.register(r'verify-sms', VerifySMSCodeView, basename='verify_sms')


urlpatterns = [
    path('', include(router_v1.urls), name='routers'),
    path('auth/', include('djoser.urls.authtoken'), name='auth'),
]
