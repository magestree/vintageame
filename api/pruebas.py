from support.globals import URL_VINTAGEAME_DESARROLLO
from productos.models import Producto, Categoria
import json, requests

p = Producto.objects.first()
producto_prueba = p.get_producto_as_dict()

def add_producto():
    # url_base = 'https://prepro.productos-vintage.com/api/categoria'
    url = '%sadd/producto/' %URL_VINTAGEAME_DESARROLLO
    headers = {'Content-Type': 'application/json'}

    r = requests.post(
        url = url,
        headers = headers,
        data = json.dumps(producto_prueba),
    )

    print(r.text, r.status_code)

def get_productos():
    url = '%sget/productos/' %URL_VINTAGEAME_DESARROLLO
    headers = {'Content-Type': 'application/json'}

    r = requests.get(
        url = url,
        headers = headers,
    )

    print(r.text, r.status_code)
    # print(json.loads(r.content).get('productos')[0].get('url_amigable'))

def get_producto():
    url = '%sget/producto/' %URL_VINTAGEAME_DESARROLLO
    headers = {'Content-Type': 'application/json'}
    payload = {
        'url_amigable': 'lauson-cl146-tocadiscos-bluetooth-de-madera',
    }

    r = requests.get(
        url = url,
        headers = headers,
        data = json.dumps(payload),
    )

    print(r.text, r.status_code)
    print(json.loads(r.content).get('producto'))

def get_categoria():
    url = '%sget/categoria/' %URL_VINTAGEAME_DESARROLLO
    headers = {'Content-Type': 'application/json'}
    payload = {
        'url_amigable': 'alimentacion-y-bebidas',
    }

    r = requests.get(
        url = url,
        headers = headers,
        data = json.dumps(payload),
    )

    print(r.text, r.status_code)

