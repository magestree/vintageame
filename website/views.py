from django.shortcuts import render
from productos.models import Categoria
from productos.views import global_data

def index(request):
    # En esta vista mostramos texto para reforzar el SEO on page, y las categorías de los productos en venta
    categorias = Categoria.objects.order_by('nombre')
    categorias_menu = categorias[:10]

    context = {
        'categorias': categorias,
        'categorias_menu': categorias_menu
    }
    context.update(global_data(request))
    return render(request, 'website/index.html', context)

def handler400(request, exception):
    return render(request, 'website/400.html', locals())

def handler403(request, exception):
    return render(request, 'website/403.html', locals())

def handler404(request, exception):
    return render(request, 'website/404.html', locals())

def handler500(request, exception):
    return render(request, 'website/500.html', locals())
