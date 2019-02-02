from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^prueba/$', views.prueba, name = 'prueba'),
    url(r'^administrar_proyectos/$', views.administrar_proyectos, name = 'administrar_proyectos'),
]