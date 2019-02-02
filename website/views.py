from django.shortcuts import render, redirect
# import datetime, pytz
from decimal import Decimal
from productos.models import Producto, Categoria

def index(request):
    # En esta vista mostramos texto para reforzar el SEO on page, y las categorías de los productos en venta
    categorias = Categoria.objects.order_by('nombre')
    categorias_menu = categorias[:10]

    context = {
        'categorias': categorias,
        'categorias_menu': categorias_menu
    }

    return render(request, 'website/index.html', context)


def descuentos(request):
    # Definición del criterio para considerar un producto como recién añadido a la BD
    # UTC = pytz.timezone('UTC')
    # horas_nuevo = 336
    # fecha_nuevo = datetime.datetime.now(UTC) - datetime.timedelta(hours = horas_nuevo)

    # Escenarios en que se recibe un POST
    if request.method == 'POST':
        # Se obtiene la información de precios del input del formulario
        precios = request.POST.get('precio')

        # Se formatea el string obtenido para obtener los precios mínimo y máximo
        min_price, max_price = precios.replace('€', '').replace(' ', '').split('-')

        # Se almacenan estos valores en la session para inicializar el formulario tras la nueva carga de página
        request.session['min_price_session'] = min_price
        request.session['max_price_session'] = max_price
        precio_minimo, precio_maximo = Decimal(min_price), Decimal(max_price)

    else:
        # Si no se realiza un filtrado de precios, entonces se resetean los valores del input de precios del formulario
        if request.session.get('min_price_session'):
            del request.session['min_price_session']
        if request.session.get('max_price_session'):
            del request.session['max_price_session']
        precio_minimo, precio_maximo = None, None

    # En el index se muestran los productos con descuentos
    # productos = Proyecto.objects.prefetch_related('descuento_set', 'producto_set__categoria').get(en_uso=True)
    productos = Producto.objects.order_by('-ahorro_porciento').filter(
        ahorro_euros__gt = 0,
        precio_final__gte = precio_minimo,
        precio_final__lte = precio_maximo,
    )

    print(productos, '===================')

    categorias = Categoria.objects.order_by('nombre')
    categorias_menu = categorias[:10]

    # productos_todos = productos['productos_todos']
    # productos_descuento = productos['productos_descuento']
    # productos_mejor_valorados = productos['productos_mejor_valorados']

    # productos = proyecto.producto_set.order_by('?')
    # productos_descuento = productos.filter(ahorro_porciento__gt = 0).order_by('-ahorro_porciento')
    # productos_mejor_valorados = productos.filter(opiniones__gt = 0).order_by('-evaluacion')
    # # productos_nuevos = productos.filter(fecha_registro__gt = fecha_nuevo).order_by('-fecha_registro')

    context = {
        'categorias': categorias,
        'categorias_menu': categorias_menu,
        'productos': productos,
        # 'productos_todos': productos_todos,
        # 'productos_descuento': productos_descuento,
        # 'productos_mejor_valorados': productos_mejor_valorados,
        # 'productos_nuevos': productos_nuevos,
    }
    return render(request, 'website/index.html', context)


def prueba(request):
    context = {
        'text': 'La redirección funciona OK',
    }
    return render(request, 'website/prueba.html', context)

def administrar_proyectos(request):
    context = {}
    return render(request, 'website/administrar_proyectos.html', context)

def handler400(request, exception):
    return render(request, 'website/400.html', locals())

def handler403(request, exception):
    return render(request, 'website/403.html', locals())

def handler404(request, exception):
    return render(request, 'website/404.html', locals())

def handler500(request, exception):
    return render(request, 'website/500.html', locals())
