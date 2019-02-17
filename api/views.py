from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from productos.models import Producto, Categoria
import json

@csrf_exempt
def add_categoria(request):
    response = {
        'success': True,
        'message': '',
    }

    # En función del método HTTP definimos qué acciones llevar a Cabo
    if request.method == 'POST':
        # Nos aseguramos que la petición tenga el tipo de dato adecuado
        if request.META['CONTENT_TYPE'] != 'application/json':
            response['success'] = False,
            response['message'] = 'El contenido debe ser json con header application/json'
            return HttpResponse(json.dumps(response), content_type = 'application/json')

        content = json.loads(request.body)
        nombre = content.get('nombre')
        descripcion_breve = content.get('descripcion_breve')
        descripcion = content.get('descripcion')
        texto_seo = content.get('texto_seo')

        categoria = Categoria.objects.filter(nombre = nombre).first()
        if categoria:
            categoria.modificar_categoria(
                nombre = nombre,
                descripcion_breve = descripcion_breve,
                descripcion = descripcion,
                texto_seo = texto_seo,
            )
            response['categoria'] = categoria.get_categoria_as_dict()
            response['message'] = 'Se ha modificado correctamente la Categoría existente: "%s"' %nombre
        else:
            n_categoria = Categoria.nueva_categoria(
                nombre = nombre,
                descripcion_breve = descripcion_breve,
                descripcion = descripcion,
                texto_seo = texto_seo,
            )


    return HttpResponse(json.dumps(response), content_type = 'application/json')

@csrf_exempt
def add_producto(request):
    response = {
        'success': True,
        'message': '',
    }

    if request.method == 'POST':
        # Nos aseguramos que la petición tenga el tipo de dato adecuado
        if request.META['CONTENT_TYPE'] != 'application/json':
            response['success'] = False,
            response['message'] = 'El contenido debe ser json con header application/json'
            return HttpResponse(json.dumps(response), content_type = 'application/json')

        content = json.loads(request.body)
        nombre = content.get('nombre')
        nombre_corto = content.get('nombre_corto')
        url_amigable = content.get('url_amigable')
        precio_antes = content.get('precio_antes')
        precio_final = content.get('precio_final')
        ahorro_euros = content.get('ahorro_euros')
        ahorro_porciento = content.get('ahorro_porciento')
        categoria = content.get('categoria')
        url_afiliado = content.get('url_afiliado')
        url_imagen_principal = content.get('url_imagen_principal')
        asin = content.get('asin')
        opiniones = content.get('opiniones')
        evaluacion = content.get('evaluacion')
        fecha_registro = content.get('fecha_registro')

        # Para crear un producto es imprescindible que tenga asociado una Categoría, así que definimos el objeto Categoría
        # a partir de la información recibida en forma de diccionario
        if Categoria.objects.filter(url_amigable = categoria.get('url_amigable')):
            existent_categoria = Categoria.objects.get(url_amigable = categoria.get('url_amigable'))
            existent_categoria.modificar_categoria(
                nombre = categoria.get('nombre'),
                descripcion_breve = categoria.get('descripcion_breve'),
                descripcion = categoria.get('descripcion'),
                texto_seo = categoria.get('texto_seo'),
            )
            categoria = existent_categoria
        else:
            # Si no existe la categoría, entonces se crea
            categoria = Categoria.nueva_categoria(
                nombre = categoria.get('nombre'),
                descripcion_breve = categoria.get('descripcion_breve'),
                descripcion = categoria.get('descripcion'),
                texto_seo = categoria.get('texto_seo'),
            )

        # Con la categoría ya definida podemos crear el Producto si no existe ya de antes. El criterio de comparación es la url_amigable
        if Producto.objects.filter(url_amigable = url_amigable):
            existent_producto = Producto.objects.get(url_amigable = url_amigable)
            existent_producto.modificar_producto(
                nombre = nombre,
                precio_antes = precio_antes,
                precio_final = precio_final,
                ahorro_euros = ahorro_euros,
                ahorro_porciento = ahorro_porciento,
                categoria = categoria,
                url_afiliado = url_afiliado,
                url_imagen_principal = url_imagen_principal,
                asin = asin,
                opiniones = opiniones,
                evaluacion = evaluacion,
            )
            response['message'] = 'Se ha modificado correctamente el producto: "%s"' % nombre
        else:
            n_producto = Producto.nuevo_producto(
                nombre = nombre,
                precio_antes = precio_antes,
                precio_final = precio_final,
                ahorro_euros = ahorro_euros,
                ahorro_porciento = ahorro_porciento,
                categoria = categoria,
                url_afiliado = url_afiliado,
                url_imagen_principal = url_imagen_principal,
                asin = asin,
                opiniones = opiniones,
                evaluacion = evaluacion,
            )
            response['message'] = 'Se ha creado correctamente el producto: "%s"' %nombre

    else:
        response['message'] = 'El método HTTP de la petición debe ser POST'

    return HttpResponse(json.dumps(response), content_type = 'application/json')

@csrf_exempt
def get_productos(request):
    response = {
        'success': True,
        'message': '',
        'productos': None,
    }

    if request.method == 'GET':
        if request.META['CONTENT_TYPE'] != 'application/json':
            response['success'] = False,
            response['message'] = 'El contenido debe ser json con header application/json'
            return HttpResponse(json.dumps(response), content_type='application/json')

        response['productos'] = Producto.get_productos_as_dict()

    else:
        response['message'] = 'El método HTTP de la petición debe ser GET'
        response['success'] = False

    return HttpResponse(json.dumps(response), content_type = 'application/json')

@csrf_exempt
def get_producto(request):
    response = {
        'success': True,
        'message': '',
        'producto': None,
    }

    if request.method == 'GET':
        if request.META['CONTENT_TYPE'] != 'application/json':
            response['success'] = False,
            response['message'] = 'El contenido debe ser json con header application/json'
        else:
            content = json.loads(request.body)
            url_amigable = content.get('url_amigable')
            if url_amigable:
                producto = Producto.objects.filter(url_amigable = url_amigable).first()
                if producto:
                    response['producto'] = producto.get_producto_as_dict()
                else:
                    response['success'] = False
                    response['message'] = 'No existe un Producto registrado con la url_amigable: "%s"' %url_amigable
            else:
                response['success'] = False
                response['message'] = 'No se ha indicado un valor de url_amigable'
    else:
        response['success'] = False
        response['message'] = 'El método HTTP de la petición debe ser GET'

    # Sea cual sea el escenario se devuelve el resultado del procesamiento de la petición GET
    return HttpResponse(json.dumps(response), content_type = 'application/json')

@csrf_exempt
def get_categoria(request):
    response = {
        'success': True,
        'message': '',
        'categoria': None,
    }

    if request.method == 'GET':
        if request.META['CONTENT_TYPE'] != 'application/json':
            response['success'] = False,
            response['message'] = 'El contenido debe ser json con header application/json'
        else:
            content = json.loads(request.body)
            url_amigable = content.get('url_amigable')
            if url_amigable:
                categoria = Categoria.objects.filter(url_amigable = url_amigable).first()
                if categoria:
                    response['categoria'] = categoria.get_categoria_as_dict()
                else:
                    response['success'] = False
                    response['message'] = 'No existe una Categoría registrada con la url_amigable: "%s"' %url_amigable
            else:
                response['success'] = False
                response['message'] = 'No se ha indicado un valor de url_amigable'
    else:
        response['success'] = False
        response['message'] = 'El método HTTP de la petición debe ser GET'

    # Sea cual sea el escenario se devuelve el resultado del procesamiento de la petición GET
    return HttpResponse(json.dumps(response), content_type = 'application/json')

@csrf_exempt
def get_categorias(request):
    response = {
        'success': True,
        'message': '',
        'categorias': None,
    }

    if request.method == 'GET':
        if request.META['CONTENT_TYPE'] != 'application/json':
            response['success'] = False,
            response['message'] = 'El contenido debe ser json con header application/json'
            return HttpResponse(json.dumps(response), content_type = 'application/json')

        response['categorias'] = Categoria.get_categorias_as_dict()

    else:
        response['message'] = 'El método HTTP de la petición debe ser GET'
        response['success'] = False
    print(response)
    return HttpResponse(json.dumps(response), content_type = 'application/json')

@csrf_exempt
def remove_producto(request, url_amigable):
    response = {
        'success': True,
        'message': '',
    }

    producto = Producto.objects.get(url_amigable = url_amigable)
    producto.eliminar_producto()
    print('Se ha eliminado el producto %s' %producto)

    return HttpResponse(json.dumps(response), content_type = 'application/json')

@csrf_exempt
def remove_categoria(request, url_amigable):
    response = {
        'success': True,
        'message': '',
    }

    categoria = Categoria.objects.get(url_amigable = url_amigable)
    # producto.eliminar_producto()
    print('Se ha eliminado la categoria %s' %categoria)

    return HttpResponse(json.dumps(response), content_type = 'application/json')


