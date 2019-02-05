import json, requests

producto_prueba = {
    'nombre': 'Producto Nombre',
    'nombre_corto': 'Producto Nombre corto',
    'url_amigable': 'producto-nombre',
    'precio_antes': '40.52',
    'precio_final': '39.51',
    'ahorro_euros': '1.01',
    'ahorro_porciento': '2.49',
    'categoria': '',
    'url_afiliado': 'https://www.amazon.es/Madison-Freesound-VR30-Radio-vintage-Bluetooth/dp/B07DDR6SDF/ref=as_li_ss_tl?ie=UTF8&qid=1545989592&sr=8-57&keywords=vintage&linkCode=ll1&tag=erickmhq-21&linkId=b92c6f8aa262a5116cc44cfa792e4cd6&language=es_ES',
    'url_imagen_principal': 'https://images-na.ssl-images-amazon.com/images/I/71XPTEgGtyL._SL1264_.jpg',
    'asin': 'B07DDR6SDF',
    'opiniones': '5',
    'evaluacion': '4.2',
    'fecha_registro': '2018-02-03',
}

url_base = 'http://192.168.1.51:8002/api/'

def add_categoria(url_amigable):
    # url_base = 'https://prepro.productos-vintage.com/api/categoria'
    url = '%sadd/categoria/' %url_base
    headers = {'Content-Type': 'application/json'}
    payload = {
        'url_amigable': url_amigable,
    }

    r = requests.post(
        url = url,
        headers = headers,
        data = json.dumps(payload),
    )

    print(r.text, r.status_code)

def add_producto():
    url = '%sadd/producto/' %url_base
    headers = {'Content-Type': 'application/json'}
    payload = producto_prueba
    r = requests.post(
        url = url,
        headers = headers,
        data = json.dumps(payload),
    )
    print(r.text, r.status_code)