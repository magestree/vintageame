from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^add/categoria/$', views.add_categoria, name = 'add_categoria'),
    url(r'^add/producto/$', views.add_producto, name = 'add_producto'),
    url(r'^get/productos/$', views.get_productos, name = 'get_productos'),
    url(r'^remove/producto/(?P<url_amigable>[\w-]+)/$', views.remove_producto, name = 'remove_producto'),
]