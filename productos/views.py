from django.shortcuts import render, HttpResponse
from django.http import Http404
from django.db.models import Count, Q
from productos.models import Producto, Categoria
from support.globals import GOOGLE_SITE_VERIFICATION, ENTORNO, GOOGLE_ANALYTICS, GOOGLE_ADSENSE, FB_PIXEL_ID, HOTJAR_ID
from decimal import Decimal
import json

# Estas son variables adicionales que deben pasarse a TODOS los templates
def global_data(request):
    return {
        'GOOGLE_SITE_VERIFICATION': GOOGLE_SITE_VERIFICATION,
        'GOOGLE_ANALYTICS': GOOGLE_ANALYTICS,
        'GOOGLE_ADSENSE': GOOGLE_ADSENSE,
        'ENTORNO': ENTORNO,
        'FB_PIXEL_ID': FB_PIXEL_ID,
        'HOTJAR_ID': HOTJAR_ID,
    }

def categoria(request, url_amigable):
    categorias = Categoria.objects.prefetch_related('producto_set').annotate(count = Count('producto')).order_by('-count')

    # Se determina la categoría a mostrar o en caso contrario devolvemos 404
    categoria = categorias.filter(url_amigable = url_amigable).first()
    if not categoria:
        raise Http404

    # Seleccionamos las primeras 5 categorías, excluyendo la actual si se encuentra entre estas
    categorias_footer = categorias.filter(~Q(url_amigable = url_amigable))[:5]

    order_by = '-opiniones' # Se define el criterio de ordenación de productos por defecto
    productos = categoria.producto_set.order_by(order_by, '-opiniones', '-evaluacion')
    productos_keywords = productos[:5]

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
            productos = productos.filter(precio_final__gte = precio_minimo, precio_final__lte = precio_maximo).order_by(order_by)

        elif 'order_by' in request.POST:
            precio_maximo = request.POST.get('precio_maximo')
            precio_minimo = request.POST.get('precio_minimo')
            productos = productos.filter(precio_final__gte = precio_minimo, precio_final__lte = precio_maximo).order_by(order_by, '-opiniones', '-evaluacion')

    else:
        # Si no se realiza un filtrado de precios, entonces se resetean los valores del input de precios del formulario
        if request.session.get('min_price_session'):
            del request.session['min_price_session']
        if request.session.get('max_price_session'):
            del request.session['max_price_session']

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
        'categorias_footer': categorias_footer,
        'productos': productos,
        'productos_keywords': productos_keywords,
        'order_by': order_by,
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