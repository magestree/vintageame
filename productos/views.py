from django.shortcuts import render, HttpResponse
from django.http import Http404
from productos.models import Producto, Categoria
from support.globals import GOOGLE_SITE_VERIFICATION, ENTORNO, GOOGLE_ANALYTICS, FB_PIXEL_ID
from decimal import Decimal
import json

# Estas son variables adicionales que deben pasarse a TODOS los templates
def global_data(request):
    return {
        'GOOGLE_SITE_VERIFICATION': GOOGLE_SITE_VERIFICATION,
        'GOOGLE_ANALYTICS': GOOGLE_ANALYTICS,
        'ENTORNO': ENTORNO,
        'FB_PIXEL_ID': FB_PIXEL_ID,
    }

def categoria(request, url_amigable):
    # Se obtiene la Categoría de esta vista y el resto de categorías para el menú
    if not Categoria.objects.filter(url_amigable = url_amigable):
        raise Http404

    categoria = Categoria.objects.get(url_amigable = url_amigable)
    categorias = Categoria.objects.order_by('nombre')

    precio_maximo, precio_minimo = None, None
    productos = categoria.producto_set.all()

    if request.method == 'POST':
        order_by = request.POST.get('order_by')

        if 'precio' in request.POST:
            # Se obtiene la información de precios del input del formulario
            precios = request.POST.get('precio')

            # Se formatea el string obtenido para obtener los precios mínimo y máximo
            min_price, max_price = precios.replace('€', '').replace(' ', '').split('-')

            # Se almacenan estos valores en la session para inicializar el formulario tras la nueva carga de página
            request.session['min_price_session'] = min_price
            request.session['max_price_session'] = max_price
            precio_minimo, precio_maximo = Decimal(min_price), Decimal(max_price)
            productos = productos.order_by(order_by, '-opiniones', '-evaluacion', 'precio_final').filter(precio_final__gte = precio_minimo, precio_final__lte = precio_maximo)

        elif 'order_by' in request.POST:
            precio_maximo = request.POST.get('precio_maximo')
            precio_minimo = request.POST.get('precio_minimo')
            productos = productos.order_by(order_by, '-opiniones', '-evaluacion', 'precio_final').filter(precio_final__gte = precio_minimo, precio_final__lte = precio_maximo)

    else:
        # Si no se realiza un filtrado de precios, entonces se resetean los valores del input de precios del formulario
        if request.session.get('min_price_session'):
            del request.session['min_price_session']
        if request.session.get('max_price_session'):
            del request.session['max_price_session']
        # precio_minimo, precio_maximo = None, None
        order_by = '-ahorro_porciento'
        productos = categoria.producto_set.order_by(order_by, '-opiniones', '-evaluacion', 'precio_final')

    # Añadiendo información adicional a los productos
    for producto in productos:
        if producto.evaluacion:
            if producto.evaluacion - int(producto.evaluacion) == 0.5:
                rounded = round(producto.evaluacion + Decimal(0.1))
            else:
                rounded = round(producto.evaluacion)
            if rounded == 5:
                producto.evaluacion_int = 'five'
            elif rounded == 4:
                producto.evaluacion_int = 'four'
            elif rounded == 3:
                producto.evaluacion_int = 'three'
            elif rounded == 2:
                producto.evaluacion_int = 'two'
            elif rounded == 1:
                producto.evaluacion_int = 'one'
        else:
            producto.evaluacion_int = None

    context = {
        'categoria': categoria,
        'categorias': categorias,
        'productos': productos,
        'order_by': order_by,
        # 'precio_minimo': precio_minimo,
        # 'precio_maximo': precio_maximo,
    }

    context.update(global_data(request))
    return render(request, 'productos/productos.html', context)

def get_edge_prices(request, categoria_id):

    # 1 - Determinar los precios máximo y mínimo de todos los productos de la Categoría
    if not Categoria.objects.filter(id = categoria_id):
        raise Http404

    categoria = Categoria.objects.get(id = categoria_id)
    edge_prices = Producto.get_edge_prices(categoria.producto_set.all())
    min_price = edge_prices[0]
    max_price = edge_prices[1]

    # 2 - Determinar si existen criterios de búsqueda de precio en la session
    min_price_session = request.session.get('min_price_session')
    # min_price_session = 15
    max_price_session = request.session.get('max_price_session')
    # max_price_session = 30
    if not min_price_session:
        min_price_session = min_price
    if not max_price_session:
        max_price_session = max_price

    resultado = {
        'min_price': min_price,
        'max_price': max_price,
        'min_price_session': min_price_session,
        'max_price_session': max_price_session,
    }
    return HttpResponse(json.dumps(resultado), content_type = 'application/json')