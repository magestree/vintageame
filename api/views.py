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
        url_amigable = content.get('url_amigable')
        response['message'] = 'Se ha eliminado correctamente la categoría: "%s"' %url_amigable

    return HttpResponse(json.dumps(response))

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

        # print(nombre)
        # print(nombre_corto)
        # print(url_amigable)
        # print(precio_antes)
        # print(precio_final)
        # print(ahorro_euros)
        # print(ahorro_porciento)
        # print(categoria)
        # print(url_afiliado)
        # print(url_imagen_principal)
        # print(asin)
        # print(opiniones)
        # print(evaluacion)
        # print(fecha_registro)

        # Para crear un producto es imprescindible que tenga asociado una Categoría, así que definimos el objeto Categoría
        # a partir de la información recibida en forma de diccionario
        if Categoria.objects.filter(url_amigable = categoria.get('url_amigable')):
            existent_categoria = Categoria.objects.get(url_amigable = categoria.get('url_amigable'))
            existent_categoria.modificar_categoria(
                descripcion = categoria.get('descripcion'),
            )
            categoria = existent_categoria
        else:
            # Si no existe la categoría, entonces se crea
            categoria = Categoria.nueva_categoria(
                nombre = categoria.get('nombre'),
                descripcion = categoria.get('descripcion'),
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

    return HttpResponse(json.dumps(response))

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

    return HttpResponse(json.dumps(response))

@csrf_exempt
def remove_producto(request, url_amigable):
    response = {
        'success': True,
        'message': '',
    }

    producto = Producto.objects.get(url_amigable = url_amigable)
    # producto.eliminar_producto()
    print('Se ha eliminado el producto %s' %producto)

    return HttpResponse(json.dumps(response))


