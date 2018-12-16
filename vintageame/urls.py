from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    url(r'^', include('website.urls', namespace='website')),
    url(r'^manage/', admin.site.urls),  # URL para el admin web
    url(r'^productos/', include('productos.urls', namespace='productos')),
    url(r'^usuarios/', include('usuarios.urls', namespace='usuarios')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

# Errors
handler400 = 'website.views.handler400'
handler403 = 'website.views.handler403'
handler404 = 'website.views.handler404'
handler500 = 'website.views.handler500'