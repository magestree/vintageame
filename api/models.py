from django.db import models
from random import choice
import json, requests

class API_Client(models.Model):
    nombre = models.CharField('Nombre', max_length = 128, blank = False, null = False, unique = True)
    base_url = models.CharField('Base URL', max_length = 255, blank = False, null = False, unique = True)

    @classmethod
    def nuevo_api_client(cls, nombre, base_url):
        n_api_client = cls.objects.create(
            nombre = nombre,
            base_url = base_url,
        )
        return n_api_client

    def modificar_api_client(self, nombre, base_url):
        self.nombre = nombre
        self.base_url = base_url
        self.save()
        return self

    def eliminar_api_client(self):
        self.delete()

    def __str__(self):
        return self.nombre

    class Meta():
        verbose_name_plural = 'API Clients'

class App(models.Model):
    api_client = models.ForeignKey(API_Client, blank = False, null = False, on_delete = models.CASCADE)
    nombre = models.CharField('App', max_length = 128, blank = False, null = False, unique = True)
    email = models.EmailField('Email', max_length = 128, blank = False, null = False, unique = False)
    api_key = models.CharField('API Key', max_length = 32, blank = False, null = False, unique = True)
    max_rate = models.IntegerField('Max. conexiones por hora', blank = False, null = False, unique = False, default = 3600)
    activo = models.BooleanField('Activo', blank = True, default = True)

    @classmethod
    def generate_api_key(cls):
        # Genera una API Key que no esté siendo usada por ninguna App
        valores = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ<=>@#%&+"
        api_key = ""
        api_key = api_key.join([choice(valores) for i in range(32)])
        while cls.objects.filter(api_key = api_key):
            cls.generate_api_key()
        # Una vez encontramos una API Key que no está siendo usada por ninguna App, la devolvemos para que sea usada
        return api_key

    @classmethod
    def nueva_app(cls, api_client, nombre, email):
        api_key = cls.generate_api_key()
        n_app = cls.objects.create(
            api_client = api_client,
            nombre = nombre,
            email = email,
            api_key = api_key,
            # Los valores de max_rate y activo están seteados por defecto.
        )
        return n_app

    def regenerar_apip_key(self):
        self.api_key = App.generate_api_key()
        self.save()
        return self

    def modificar_app(self, nombre):
        self.nombre = nombre
        self.save()
        return self

    def eliminar_app(self):
        self.delete()

    def __str__(self):
        return self.nombre

    class Meta():
        verbose_name_plural = 'Apps'

    # Métodos de la API
    # 1 - AUTH
    def authenticate(self, auth_data):
        # auth data es un diccionario con la combinación de API Key y email que identifican a un usuario
        return auth_data.get('api_key') == self.api_key and auth_data.get('email') == self.email

    # 2 - GET
    # 2.1 - Devuelve un producto a partir de su url_amigable
    def get_product(self, url_amigable):
        print('Obteniendo en %s el Producto: %s' % (self.api_client.base_url, url_amigable))
        url = '%sget/producto/' %self.api_client.base_url
        headers = {'Content-Type': 'application/json'}
        payload = {
            'url_amigable': url_amigable,
        }
        r = requests.get(
            url = url,
            headers = headers,
            data = json.dumps(payload)
        )
        return json.loads(r.content)

    # 2.2 - Devuelve todos los Productos
    def get_products(self):
        print('Obteniendo en %s todos los productos' %self.api_client.base_url)
        url = '%sget/productos/' %self.api_client.base_url
        headers = {'Content-Type': 'application/json'}
        r = requests.get(
            url = url,
            headers = headers,
        )
        return json.loads(r.content)

    # 2.3 - Devuelbe una Categoría a partir de su url_amigable
    def get_categoria(self, url_amigable):
        print('Obteniendo en %s la Categoría: %s' % (self.api_client.base_url, url_amigable))
        url = '%sget/categoria/' %self.api_client.base_url
        headers = {'Content-Type': 'application/json'}
        payload = {
            'url_amigable': url_amigable,
        }
        r = requests.get(
            url = url,
            headers = headers,
            data = json.dumps(payload)
        )
        return json.loads(r.content)

    # 2.3 - Devuelve todas las categorías
    def get_categorias(self):
        print('Obteniendo en %s todas las categorías' % self.api_client.base_url)
        url = '%sget/categorias/' % self.api_client.base_url
        headers = {'Content-Type': 'application/json'}
        print(url)
        r = requests.get(
            url = url,
            headers = headers,
        )
        return json.loads(r.content)

    # 3 - ADD
    # 3.1 - Add Producto
    def add_product(self, producto_dict):
        print('Añadiendo en %s el Producto: %s' %(self.api_client.base_url, producto_dict.get('url_amigable')))
        url = '%sadd/producto/' %self.api_client.base_url
        headers = {'Content-Type': 'application/json'}
        r = requests.post(
            url = url,
            headers = headers,
            data = json.dumps(producto_dict),
        )
        return json.loads(r.content)

    # 3.2 - Add Categoría
    def add_categoria(self, categoria_dict):
        print('Añadiendo en %s la Categoría: %s' % (self.api_client.base_url, categoria_dict.get('url_amigable')))
        url = '%sadd/categoria/' %self.api_client.base_url
        headers = {'Content-Type': 'application/json'}
        r = requests.post(
            url = url,
            headers = headers,
            data = json.dumps(categoria_dict),
        )
        return json.loads(r.content)

    # 4 - DELETE
    # 4.1 - Delete Producto
    def delete_product(self, url_amigable):
        print('Eliminando en %s el Producto: %s' %(self.api_client.base_url, url_amigable))
        url = '%sremove/producto/%s' % (self.api_client.base_url, url_amigable)
        headers = {'Content-Type': 'application/json'}
        r = requests.post(
            headers = headers,
            url = url,
        )
        return json.loads(r.content)

    # 4.2 - Delete Categoría
    def delete_categoria(self, url_amigable):
        print('Eliminando en %s la Categoría: %s' % (self.api_client.base_url, url_amigable))
        url = '%sremove/categoria/%s' % (self.api_client.base_url, url_amigable)
        headers = {'Content-Type': 'application/json'}
        r = requests.post(
            headers = headers,
            url = url,
        )
        return json.loads(r.content)