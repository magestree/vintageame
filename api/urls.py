from django.conf.urls import url
from . import views

urlpatterns = [
    # Add
    url(r'^add/producto/$', views.add_producto, name = 'add_producto'),
    url(r'^add/categoria/$', views.add_categoria, name = 'add_categoria'),

    # Get
    url(r'^get/productos/$', views.get_productos, name = 'get_productos'),
    url(r'^get/producto/$', views.get_producto, name = 'get_producto'),
    url(r'^get/categorias/$', views.get_categorias, name = 'get_categorias'),
    url(r'^get/categoria/$', views.get_categoria, name = 'get_categoria'),

    # Remove
    url(r'^remove/producto/(?P<url_amigable>[\w-]+)/$', views.remove_producto, name = 'remove_producto'),
    url(r'^remove/categoria/(?P<url_amigable>[\w-]+)/$', views.remove_categoria, name = 'remove_categoria'),
]