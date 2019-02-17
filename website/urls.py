from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^aviso-legal/$', views.aviso_legal, name = 'aviso_legal'),
    url(r'^politica-privacidad/$', views.politica_privacidad, name = 'politica_privacidad'),
    url(r'^politica-cookies/$', views.politica_cookies, name = 'politica_cookies'),
]