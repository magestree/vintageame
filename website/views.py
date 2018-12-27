from django.shortcuts import render
from productos.models import Categoria, Sub_Categoria, Producto
import datetime

def index(request):

    horas_nuevo = 336
    fecha_nuevo = datetime.datetime.now() - datetime.timedelta(hours = horas_nuevo)

    categorias = Categoria.objects.order_by('nombre')
    categorias_menu = categorias[:10]
    productos = Producto.objects.all()
    productos_descuento = productos.filter(ahorro_porciento__gt = 0).order_by('-ahorro_porciento')
    productos_mejor_valorados = productos.filter(opiniones__gt = 0).order_by('-evaluacion')
    productos_nuevos = productos.filter(fecha_registro__gt = fecha_nuevo).order_by('-fecha_registro')

    context = {
        'categorias': categorias,
        'categorias_menu': categorias_menu,
        'productos':productos,
        'productos_descuento': productos_descuento,
        'productos_mejor_valorados': productos_mejor_valorados,
        'productos_nuevos': productos_nuevos,
    }
    return render(request, 'website/index.html', context)

def prueba(request):
    context = {
        'text': 'La redirección funciona OK',
    }
    return render(request, 'website/prueba.html', context)

def handler400(request, exception):
    return render(request, 'website/400.html', locals())

def handler403(request, exception):
    return render(request, 'website/403.html', locals())

def handler404(request, exception):
    return render(request, 'website/404.html', locals())

def handler500(request, exception):
    return render(request, 'website/500.html', locals())
