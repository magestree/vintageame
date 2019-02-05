from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    url(r'^manage/', admin.site.urls),  # URL para el admin web
    url(r'^', include('website.urls', namespace = 'website')),
    url(r'^', include('productos.urls', namespace = 'productos')),
    url(r'^', include('usuarios.urls', namespace = 'usuarios')),
    url(r'^api/', include('api.urls', namespace = 'api')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

# Errors
handler400 = 'website.views.handler400'
handler403 = 'website.views.handler403'
handler404 = 'website.views.handler404'
handler500 = 'website.views.handler500'