from django.shortcuts import render
from productos.models import Categoria
from productos.views import global_data
from django.db.models import Count

def index(request):
    # En esta vista mostramos texto para reforzar el SEO on page, y las categorías de los productos en venta
    # categorias = Categoria.objects.order_by('nombre')
    categorias = Categoria.objects.prefetch_related('producto_set').annotate(count = Count('producto')).order_by('-count')
    # categorias_menu = categorias[:10]

    context = {
        'categorias': categorias,
        # 'categorias_menu': categorias_menu
    }
    context.update(global_data(request))
    return render(request, 'website/index.html', context)

def aviso_legal(request):
    return render(request, 'website/aviso_legal.html')

def politica_privacidad(request):
    return render(request, 'website/politica_privacidad.html')

def politica_cookies(request):
    return render(request, 'website/politica_cookies.html')

def handler400(request, exception):
    return render(request, 'website/400.html', locals())

def handler403(request, exception):
    return render(request, 'website/403.html', locals())

def handler404(request, exception):
    return render(request, 'website/404.html', locals())

def handler500(request, exception):
    return render(request, 'website/500.html', locals())
