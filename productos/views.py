from django.shortcuts import render
from productos.models import Producto, Categoria, Sub_Categoria

def producto(request, url_amigable):
    producto = Producto.objects.get(url_amigable = url_amigable)

    context = {
        'producto': producto,
    }

    return render(request, 'productos/producto.html', context)

def categoria(request, url_amigable):
    categoria = Categoria.objects.get(url_amigable = url_amigable)

    context = {
        'categoria': categoria,
    }

    return render(request, 'productos/categoria.html', context)

def sub_categoria(request, url_amigable):
    sub_categoria = Sub_Categoria.objects.get(url_amigable = url_amigable)

    context = {
        'sub_categoria': sub_categoria,
    }

    return render(request, 'productos/sub_categoria.html', context)
