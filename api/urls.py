from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^add/categoria/$', views.add_categoria, name = 'add_categoria'),
    url(r'^add/producto/$', views.add_producto, name = 'add_producto'),
]