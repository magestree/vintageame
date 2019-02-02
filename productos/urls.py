from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<url_amigable>[\w-]+)/$', views.categoria, name = 'categoria'),
    url(r'^get-edge-prices/(?P<categoria_id>\d+)/$', views.get_edge_prices, name = 'get_edge_prices'),
]