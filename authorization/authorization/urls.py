from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import include, path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('api/', include('api.urls'))
]

schema_view = get_schema_view(
    openapi.Info(
        title="Authorization API",
        default_version='v1',
        description="Документация для тестового задания.",
        contact=openapi.Contact(email="Xcision@ya.ru"),
    ), public=True, permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
