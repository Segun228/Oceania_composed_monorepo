from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)
from django.contrib import admin
from django.urls import path, include
from authentication.urls import urlpatterns as auth_urls
from api.urls import urlpatterns as api_urls
from photos.urls import urlpatterns as photos_urls
from reports.urls import urlpatterns as reports_urls
from .views import StatusView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urls), name="api-endpoint-group"),
    path("auth/", include(auth_urls), name="auth-endpoint-group"),
    path("photos/", include(photos_urls), name="photos-endpoint-group"),
    path("reports/", include(reports_urls), name="reports-endpoint-group"),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('', StatusView.as_view(), name="status")
]
