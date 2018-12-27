from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^producto/(?P<url_amigable>[\w-]+)/$', views.producto, name = 'producto'),
    url(r'^categoria/(?P<url_amigable>[\w-]+)/$', views.categoria, name = 'categoria'),
    url(r'^categorias/$', views.categorias, name = 'categorias'),
]