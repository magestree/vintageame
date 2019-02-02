from django.shortcuts import render, HttpResponse, redirect
from productos.models import Producto, Categoria
import json
from decimal import Decimal

def producto(request, url_amigable):
    # producto = Producto.objects.get(url_amigable = url_amigable)

    context = {
        # 'producto': producto,
        'url_amigable': url_amigable,
    }

    return render(request, 'productos/producto.html', context)

def ejemplo(request, url_amigable):
    # producto = Producto.objects.get(url_amigable = url_amigable)

    context = {
        # 'producto': producto,
        'url_amigable': url_amigable,
    }

    return render(request, 'productos/producto.html', context)

def categoria(request, url_amigable):
    # Se obtiene la Categoría de esta vista y el resto de categorías para el menú
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
            productos = productos.order_by(order_by, 'precio_final').filter(precio_final__gte = precio_minimo, precio_final__lte = precio_maximo)

        elif 'order_by' in request.POST:
            precio_maximo = request.POST.get('precio_maximo')
            precio_minimo = request.POST.get('precio_minimo')
            productos = productos.order_by(order_by, 'precio_final').filter(precio_final__gte = precio_minimo, precio_final__lte = precio_maximo)

    else:
        # Si no se realiza un filtrado de precios, entonces se resetean los valores del input de precios del formulario
        if request.session.get('min_price_session'):
            del request.session['min_price_session']
        if request.session.get('max_price_session'):
            del request.session['max_price_session']
        # precio_minimo, precio_maximo = None, None
        order_by = 'precio_final'
        productos = categoria.producto_set.order_by(order_by, 'precio_final')

    context = {
        'categoria': categoria,
        'categorias': categorias,
        'productos': productos,
        'order_by': order_by,
        # 'precio_minimo': precio_minimo,
        # 'precio_maximo': precio_maximo,
    }

    return render(request, 'productos/categoria.html', context)

def get_edge_prices(request, categoria_id):

    # 1 - Determinar los precios máximo y mínimo de todos los productos de la Categoría
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

# def mejor_valorados(request):
#     # Definición del criterio para considerar un producto como recién añadido a la BD
#     # UTC = pytz.timezone('UTC')
#     # horas_nuevo = 336
#     # fecha_nuevo = datetime.datetime.now(UTC) - datetime.timedelta(hours = horas_nuevo)
#
#     # Definición del Proyecto de la Tienda Online
#     if Proyecto.objects.filter(en_uso=True):
#         # Escenarios en que se recibe un POST
#         if request.method == 'POST':
#             # Se obtiene la información de precios del input del formulario
#             precios = request.POST.get('precio')
#
#             # Se formatea el string obtenido para obtener los precios mínimo y máximo
#             min_price, max_price = precios.replace('€', '').replace(' ', '').split('-')
#
#             # Se almacenan estos valores en la session para inicializar el formulario tras la nueva carga de página
#             request.session['min_price_session'] = min_price
#             request.session['max_price_session'] = max_price
#             precio_minimo, precio_maximo = Decimal(min_price), Decimal(max_price)
#
#         else:
#             # Si no se realiza un filtrado de precios, entonces se resetean los valores del input de precios del formulario
#             if request.session.get('min_price_session'):
#                 del request.session['min_price_session']
#             if request.session.get('max_price_session'):
#                 del request.session['max_price_session']
#             precio_minimo, precio_maximo = None, None
#
#         # 1 - Se obtiene el proyecto
#         proyecto = Proyecto.objects.prefetch_related('descuento_set', 'producto_set__categoria').get(en_uso=True)
#
#         # 2 - Se carga la información de la página de Descuentos del proyecto
#         mejor_valorados = proyecto.mejor_valorado_set.first()
#
#         # 3 - Se cargan las categorías y los productos asociados al proyecto
#         categorias = Categoria.objects.filter(producto__proyecto = proyecto).distinct().order_by('nombre')
#         categorias_menu = categorias[:10]
#
#         # 4 - Se cargan los productos asociados a las categorías asociadas al proyecto
#         productos = Producto.objects.get_detalles_productos(
#             proyecto = proyecto,
#             precio_minimo = precio_minimo,
#             precio_maximo = precio_maximo,
#         )
#
#         productos_todos = productos['productos_todos']
#         productos_descuento = productos['productos_descuento']
#         productos_mejor_valorados = productos['productos_mejor_valorados']
#
#         # productos = proyecto.producto_set.order_by('?')
#         # productos_descuento = productos.filter(ahorro_porciento__gt = 0).order_by('-ahorro_porciento')
#         # productos_mejor_valorados = productos.filter(opiniones__gt = 0).order_by('-evaluacion')
#         # # productos_nuevos = productos.filter(fecha_registro__gt = fecha_nuevo).order_by('-fecha_registro')
#
#         context = {
#             'categorias': categorias,
#             'categorias_menu': categorias_menu,
#             'productos_todos': productos_todos,
#             'productos_descuento': productos_descuento,
#             'productos_mejor_valorados': productos_mejor_valorados,
#             'proyecto': proyecto,
#             'mejor_valorados': mejor_valorados,
#         }
#         return render(request, 'productos/mejor_valorados.html', context)
#
#     else:
#         # Si no hay ningún proyecto creado, o de los proyectos creados, no hay ninguno en uso, se redirige al usuario a
#         # una interfaz donde puede administrar esto
#         return redirect('website:administrar_proyectos')