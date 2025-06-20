from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('landing.urls')),             # Rutas de tu app principal
    path('accounts/', include('allauth.urls')),    # Rutas de django-allauth (registro, login social)
    path('admin/', admin.site.urls),               # Admin de Django
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)