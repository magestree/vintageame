from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
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

        response['message'] = 'Se ha creado correctamente el producto: "%s"' %nombre

    else:
        response['message'] = 'El método HTTP de la petición debe ser POST'

    return HttpResponse(json.dumps(response))



