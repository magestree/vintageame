from django.contrib import admin
from productos.models import Categoria, Producto, Sub_Categoria

admin.site.register(Categoria)
admin.site.register(Sub_Categoria)
admin.site.register(Producto)
