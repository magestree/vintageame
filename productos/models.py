from django.db import models
from support.urls_productos import urls_productos
from support.descripciones_categorias import categorias
from support.globals import API_URLS
import requests, time, json
from random import randint
import urllib3, os, shutil, math
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from django.core import files
from io import BytesIO
from support.globals import crop_from_center
from support import methods
from django.conf import settings
from django.template.defaultfilters import slugify

# FOTOS DE PRODUCTOS
def productos_photos_directory(instance, filename):
    return 'productos/{0}/photos/920_614/{1}'.format(
        instance.id,
        filename,
    )

# FOTOS DE PRODUCTOS
def productos_photos_920_614_directory(instance, filename):
    return 'productos/{0}/photos/920_614/{1}'.format(
        instance.id,
        filename,
    )

# FOTOS DE PRODUCTOS
def productos_photos_464_299_directory(instance, filename):
    return 'productos/{0}/photos/464_299/{1}'.format(
        instance.id,
        filename,
    )

# FOTOS DE PRODUCTOS
def productos_photos_320_320_directory(instance, filename):
    return 'productos/{0}/photos/320_320/{1}'.format(
        instance.id,
        filename,
    )

class Categoria(models.Model):
    nombre = models.TextField('Nombre', blank = False, null = False, max_length = 4096)
    nombre_corto = models.CharField('Nombre cort', max_length = 40 ,blank = True, null = True)
    url_amigable = models.SlugField('URL amigable', max_length = 512, blank = True, null = True)
    descripcion = models.TextField('Descripción', blank = True, null = True, max_length = 4096)

    def get_categoria_as_dict(self):
        # Devuelve el objeto Categoria como un diccionario, listo para ser enviado vía REST
        categoria_dict = {
            'nombre': self.nombre,
            'nombre_corto': self.nombre_corto,
            'url_amigable': self.url_amigable,
            'descripcion': self.descripcion,
        }
        return categoria_dict

    def actualizar_descripcion_categoria(self):
        for categoria in categorias:
            if categoria.get('nombre').lower() == self.nombre.lower():
                self.descripcion = categoria.get('descripcion')
                self.save()
                print('Se ha actualizado correctamente la descripción de la categoría: %s' %self.nombre)
                # Una vez hemos encontrado una categoría y actualizado su descripción salimos de la búsqueda
                break

    @classmethod
    def actualizar_descripciones_categorias(cls):
        for categoria in cls.objects.all():
            categoria.actualizar_descripcion_categoria()

    @classmethod
    def get_categoria_from_name(cls, categoria_name):
        categoria = cls.objects.filter(nombre = categoria_name)
        if not categoria:
            print('No existe ninguna categoría con nombre %s, así que la creamos' %categoria_name)
            categoria = Categoria.nueva_categoria(
                nombre = categoria_name,
                descripcion = None,
            )
            # Se actualiza la descripción de la categoría
            for c in categorias:
                if c.get('nombre').lower() == categoria.nombre.lower():
                    categoria.descripcion = c.get('descripcion')
                    categoria.save()
                    print('Se ha actualizado correctamente la descripción de la categoría: %s' % categoria.nombre)
                    # Una vez hemos encontrado una categoría y actualizado su descripción salimos de la búsqueda
                    break
            print('Creada la nueva categoría: %s' % categoria)
        else:
            categoria = categoria.first()
            print('Ya existe al menos una categoría con nombre %s, así que tomamos la existente (%s)' %(categoria_name, categoria))
        return categoria

    @classmethod
    def nueva_categoria(cls, nombre, descripcion):
        if not cls.objects.filter(nombre = nombre):
            n_categoria = cls.objects.create(
                nombre = nombre,
                nombre_corto = nombre[:39] + '...',
                url_amigable = slugify(nombre),
                descripcion = descripcion,
            )
            return n_categoria
        else:
            print('Ya existe una categoría con nombre %s así que no podemos crearla' %nombre)
            return None

    def modificar_categoria(self, nombre, descripcion):
        if not Categoria.objects.filter(nombre = nombre):
            if self.nombre != nombre:
                self.nombre = nombre
                self.url_amigable = slugify(nombre)
            if self.descripcion != descripcion:
                self.descripcion = descripcion
            self.save()
            return self
        else:
            return None

    def eliminar_categoria(self):
        # Antes de eliminar una categoría, se eliminan todos los productos relacionados con esta
        for producto in self.producto_set.all():
            producto.eliminar_producto()
        print('Eliminando categoría %s' %self.nombre)
        self.delete()

    @classmethod
    def eliminar_categorias(cls):
        for categoria in cls.objects.all():
            categoria.eliminar_categoria()

    class Meta():
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre

class Producto_Manager(models.Manager):
    def get_detalles_productos(self, proyecto, precio_minimo, precio_maximo):
        productos_todos = []
        productos_descuento = []
        productos_mejor_valorados = []
        productos = proyecto.producto_set.order_by('-ahorro_porciento')

        # Criterios de filtrado
        if precio_minimo:
            productos = productos.filter(precio_final__gte = precio_minimo)
        if precio_maximo:
            productos = productos.filter(precio_final__lte = precio_maximo)

        for producto in productos:
            detalles_producto = self.get_detalles_producto(producto)
            productos_todos.append(detalles_producto)
            if detalles_producto.descuento:
                productos_descuento.append(detalles_producto)
            if detalles_producto.evaluacion:
                if detalles_producto.evaluacion >= 3:
                    productos_mejor_valorados.append(detalles_producto)

        # Se ordenan los productos en productos_mejor_valorados, atendiendo a la evaluación
        if productos_mejor_valorados:
            productos_mejor_valorados.sort(key = lambda x: (x.evaluacion, x.opiniones), reverse = True)

        return {
            'productos_todos': productos_todos,
            'productos_descuento': productos_descuento,
            'productos_mejor_valorados': productos_mejor_valorados,
        }

    def get_detalles_producto(self, producto):
        # 1 - Descuento
        if producto.ahorro_porciento:
            if producto.ahorro_porciento > 0:
                producto.descuento = True
            else:
                producto.descuento = False
        else:
            producto.descuento = False

        # 2 - Estrellas de evaluación
        producto.star_classes = producto.get_star_classes()

        # 3 - Devolver el producto con la información adicional añadida
        return producto

class Producto(models.Model):
    nombre = models.TextField('Nombre', max_length = 4096, blank = True, null = True)
    nombre_corto = models.CharField('Nombre cort', max_length = 128, blank = True, null = True)
    url_amigable = models.SlugField('URL amigable', max_length = 512, blank = True, null = True)
    precio_antes = models.DecimalField('Precio Antes', max_digits = 8, decimal_places = 2, blank = True, null = True, unique = False)
    precio_final = models.DecimalField('Precio Final', max_digits = 8, decimal_places = 2, blank = True, null = True, unique = False)
    ahorro_euros = models.DecimalField('Ahorro Euros', max_digits = 8, decimal_places = 2, blank = True, null = True, unique = False)
    ahorro_porciento = models.DecimalField('Ahorro en %', max_digits = 8, decimal_places = 2, blank = True, null = True, unique = False)
    categoria = models.ForeignKey(Categoria, blank = True, null = True, unique = False, on_delete = models.CASCADE)
    url_afiliado = models.TextField('URL Amazon', max_length = 4096, blank = True, null = True)
    url_imagen_principal = models.TextField('URL Imagen principal', max_length = 4096, blank = True, null = True)
    asin = models.CharField('ASIN', max_length = 16, blank = True, null = True, unique = True)
    opiniones = models.IntegerField('Opiniones', blank = True, null = True, unique = False)
    evaluacion = models.DecimalField('Evaluación',  max_digits = 3, decimal_places = 2, blank = True, null = True, unique = False)
    fecha_registro = models.DateTimeField('Fecha de registro', blank = True, null = True, auto_now_add = True)

    # Fotos
    # foto_920_614 = models.ImageField('Foto 920 x 614', upload_to = productos_photos_920_614_directory, blank = True, null = True)
    # foto_464_299 = models.ImageField('Foto 464 x 299', upload_to = productos_photos_464_299_directory, blank = True, null = True)
    # foto_320_320 = models.ImageField('Foto 320 x 320', upload_to = productos_photos_320_320_directory, blank = True, null = True)

    @classmethod
    def add_remote_product(cls, api_url, producto_dict):
        return requests.post(
            url = '%sadd/producto/' %api_url,
            headers = {'Content-Type': 'application/json'},
            data = json.dumps(producto_dict),
        )

    @classmethod
    def get_remote_products(cls, api_url):
        return requests.get(
            url = '%sget/productos/' %api_url,
            headers = {'Content-Type': 'application/json'},
        )

    @classmethod
    def remove_remote_product(cls, api_url, url_amigable):
        headers = {'Content-Type': 'application/json'}
        url = '%sremove/producto/%s' %(api_url, url_amigable)
        return requests.delete(
            url = url,
            headers = headers,
        )

    @classmethod
    def sync_remote_products(cls):
        # Entornos a sincronizar: Preproducción y Producción
        API_URLS = ['https://prepro.productos-vintage.com/api/']
        for api_url in API_URLS:
            productos_url_amigables = []
            for producto_dict in Producto.get_productos_as_dict():
                productos_url_amigables.append(producto_dict.get('url_amigable'))
                r = cls.add_remote_product(api_url, producto_dict)
                # print(r.text, r.status_code)
                time.sleep(5)

            # Ya tenemos la lista de todos los Productos y Categorías que hemos sincronizado a partir de lo que hay en desarrollo
            # Ahora necesitamos comprobar si hay registros en remoto que deben ser eliminados porque no constan en los registros a sincronizar
            for producto_dict in json.loads(cls.get_remote_products(api_url).content).get('productos'):
                if producto_dict.get('url_amigable') not in productos_url_amigables:
                    r = cls.remove_remote_product(api_url, producto_dict.get('url_amigable'))

    def get_producto_as_dict(self):
        # Devuelve el Producto como un diccionario, listo para ser enviado vía REST

        # Es necesario obtener la categoria como diccionario
        categoria = self.categoria.get_categoria_as_dict()

        # Los posibles valores no serializables como Decimales, hay que convertirlos a string
        if self.precio_antes:
            self.precio_antes = str(self.precio_antes)
        if self.precio_final:
            self.precio_final = str(self.precio_final)
        if self.ahorro_euros:
            self.ahorro_euros = str(self.ahorro_euros)
        if self.ahorro_porciento:
            self.ahorro_porciento = str(self.ahorro_porciento)
        if self.evaluacion:
            self.evaluacion = str(self.evaluacion)
        if self.fecha_registro:
            self.fecha_registro = str(self.fecha_registro)

        producto_dict = {
            'nombre': self.nombre,
            'nombre_corto': self.nombre_corto,
            'url_amigable': self.url_amigable,
            'precio_antes': self.precio_antes,
            'precio_final': self.precio_final,
            'ahorro_euros': self.ahorro_euros,
            'ahorro_porciento': self.ahorro_porciento,
            'categoria': categoria,
            'url_afiliado': self.url_afiliado,
            'url_imagen_principal': self.url_imagen_principal,
            'asin': self.asin,
            'opiniones': self.opiniones,
            'evaluacion': self.evaluacion,
            'fecha_registro': self.fecha_registro,
        }
        return producto_dict

    @classmethod
    def get_productos_as_dict(cls):
        # Devuelve una lista de todos los productos en forma de diccionarios
        productos_dict = []
        for producto in cls.objects.all():
            productos_dict.append(producto.get_producto_as_dict())
        return productos_dict


    @classmethod
    def sincronizar_productos(cls):
        # Se sincronizan los productos a partir de las urls en support.url_productos
        for url_producto in urls_productos:
            print('Sincronizando %s' %url_producto)
            done = cls.sincronizar_producto_from_url(url_producto)
            if done == 'banned':
                # Si hemos sido baneados por Amazon, abandonamos el proceso para no empeorar la situación
                break

            # wait = randint(19, 20)
            wait = 19

            # Esperando para no estresar a Amazon
            print('Esperando %s segundos antes de sincronizar el próximo producto...' %wait)
            print('')

            time.sleep(wait)

        # Al terminar de sincronizar todos los productos, se eliminan aquellos que no tengan toda la información de manera correcta
        for producto in Producto.objects.all():
            producto.verificar_producto()

    @classmethod
    def get_edge_prices(cls, productos):
        # Devuelve el precio mínimo y máximo de todos los productos de un conjunto
        # productos debe ser una Queryset
        productos = productos.order_by('precio_final')
        min_price = math.floor(productos.first().precio_final)
        max_price = math.ceil(productos.last().precio_final)
        return [min_price, max_price]

    def verificar_producto(self):
        # Las pruebas a las que se somete un producto son:
        # 1 - Que tenga un nombre, una categoría y una foto de 320 x 320
        if self.nombre and self.categoria and self.foto_320_320:
            return True
        else:
            self.eliminar_producto()
            return None

    def get_star_classes(self):
        star_classes = []
        if not self.evaluacion or self.evaluacion == 0:
            star_classes = ['fa-star-o', 'fa-star-o', 'fa-star-o', 'fa-star-o', 'fa-star-o']
        else:
            entero = int(self.evaluacion)
            decimal = abs(self.evaluacion) - abs(entero)
            # Se añaden tantos "True" como unidades completas haya.
            for star in range(entero):
                star_classes.append('fa-star')
            # Para determinar si el sobrante decimal implica media, una o ninguna estrella, se sigue la sgte lógica:
            if decimal > 0.25 and decimal < 0.75:
                star_classes.append('fa-star-half-empty')
            elif decimal > 0.75:
                star_classes.append('fa-star')
            # Completamos con 5 estrellas la puntuación
            while len(star_classes) < 5:
                star_classes.append('fa-star-o')
        return star_classes

    @classmethod
    def nuevo_producto(
        cls, nombre, precio_antes, precio_final, ahorro_euros, ahorro_porciento, categoria, url_afiliado,
        url_imagen_principal, asin, opiniones, evaluacion
    ):
        # Solo creamos el producto si no hay otro con el mismo nombre, en caso ontrario lo modificamos
        if not cls.objects.filter(nombre = nombre):
            n_producto = cls.objects.create(
                nombre = nombre,
                nombre_corto = nombre[:83] + '...',
                url_amigable = slugify(nombre),
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
            # n_producto.set_formatos_imagen_principal()
            return n_producto
        else:
            producto = cls.objects.get(nombre = nombre)
            producto.modificar_producto(
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
            return producto

    def modificar_producto(
        self, nombre, precio_antes, precio_final, ahorro_euros, ahorro_porciento, categoria, url_afiliado,
        url_imagen_principal, asin, opiniones, evaluacion):
        if self.nombre != nombre:
            self.nombre = nombre
            self.url_amigable = slugify(nombre)
        if self.precio_antes != precio_antes:
            self.precio_antes = precio_antes
        if self.precio_final != precio_final:
            self.precio_final = precio_final
        if self.ahorro_euros != ahorro_euros:
            self.ahorro_euros = ahorro_euros
        if self.ahorro_porciento != ahorro_porciento:
            self.ahorro_porciento = ahorro_porciento
        if self.categoria != categoria:
            self.categoria = categoria
        if self.url_afiliado != url_afiliado:
            self.url_afiliado = url_afiliado
        if self.url_imagen_principal != url_imagen_principal:
            self.url_imagen_principal = url_imagen_principal
            self.save()
            # self.set_formatos_imagen_principal()
        if self.asin != asin:
            self.asin = asin
        if self.opiniones != opiniones:
            self.opiniones = opiniones
        if self.evaluacion != evaluacion:
            self.evaluacion = evaluacion
        self.save()

    @classmethod
    # Elimina todos los productos
    def eliminar_productos(cls):
        for producto in cls.objects.all():
            producto.eliminar_producto()

    def eliminar_producto(self):
        # Al eliminar un producto, debemos eliminar todas las imágenes relacionadas antes
        if self.foto_464_299:
            self.eliminar_foto_producto('464_299')
        if self.foto_920_614:
            self.eliminar_foto_producto('920_614')
        if self.foto_320_320:
            self.eliminar_foto_producto('320_320')
        print('Eliminando producto %s' %self.nombre)
        self.delete()

    def eliminar_foto_producto(self, size):
        # Elimina el fichero de imagen de una foto del Producto
        print('Eliminando foto de Producto %s' %self.nombre)
        if size == '920_614':
            self.foto_920_614.delete()
        elif size == '464_299':
            self.foto_464_299.delete()
        elif size == '320_320':
            self.foto_320_320.delete()

        # Comprobar si existen más fotos en el directorio definido para ello, y si no, eliminarlo
        producto_foto_path = '%s/productos/%s/photos/%s' % (settings.MEDIA_ROOT, self.id, size)

        if os.path.exists(producto_foto_path):
            if not os.listdir(producto_foto_path):
                shutil.rmtree(producto_foto_path)
                print('Eliminado el archivo de la foto del producto en %s' %producto_foto_path)
            else:
                print('Tenemos elementos dentro de %s' %producto_foto_path)
        else:
            print('No podemos eliminar el archivo de la foto porque no existe la ruta: %s' %producto_foto_path)

        # Luego comprueba si no hay nada más dentro de la carpeta del producto, y si es así la elimina también
        producto_path = '%s/productos/%s' %(settings.MEDIA_ROOT, self.id)
        if os.path.exists(producto_path):
            if not os.listdir(producto_path):
                shutil.rmtree(producto_path)

        # Se guarda cualquier cambio en el modelo Producto
        self.save()

    # def set_formatos_imagen_principal(self):
    #     # Con este método se guardan la imagen principal en varios tamaños
    #     if len(self.url_imagen_principal) > 20:
    #         resp = requests.get(self.url_imagen_principal)
    #         if resp.status_code != requests.codes.ok:
    #             # Error handling here
    #             print('Error here!')
    #             return
    #
    #         fp = BytesIO()
    #         fp.write(resp.content)
    #         file_name = self.url_imagen_principal.split("/")[-1]
    #
    #         # 1 - 920 x 614
    #         if self.foto_920_614:
    #             self.eliminar_foto_producto(size = '920_614')
    #         self.foto_920_614.save(file_name, files.File(fp))
    #         self.save()
    #         crop_from_center(
    #             image_path = self.foto_920_614.path,
    #             width = 920,
    #             height = 614,
    #             save = True,
    #         )
    #
    #         # 2 - 464 x 299
    #         if self.foto_464_299:
    #             self.eliminar_foto_producto(size = '464_299')
    #         self.foto_464_299.save(file_name, files.File(fp))
    #         self.save()
    #         crop_from_center(
    #             image_path = self.foto_464_299.path,
    #             width = 464,
    #             height = 299,
    #             save = True,
    #         )
    #
    #         # 2 - 320 x 320
    #         if self.foto_320_320:
    #             self.eliminar_foto_producto(size = '320_320')
    #         self.foto_320_320.save(file_name, files.File(fp))
    #         self.save()
    #         crop_from_center(
    #             image_path = self.foto_320_320.path,
    #             width = 320,
    #             height = 320,
    #             save = True,
    #         )

    @classmethod
    def sincronizar_producto_from_url(cls, url_producto):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}

        try:
            # Se realizan hasta 20 intentos de recuperación de información por producto,
            # por si Amazon detecta una y otra vez un acceso automatizado
            for attempt in range(20):
                print('Iniciando intento %s de obtención de datos...' %attempt)
                # Se realiza una petición GET a la url del producto en Amazon
                response = requests.get(url_producto, headers = headers, verify = False)
                print('Petición requests realizada...')
                # Si el código recibido es 200, la conexión ha sido exitosa y se procede con el parseo de información
                if response.status_code == 200:
                    print('Hemos recibido un código 200 de parte de Amazon, procedemos a intentar obtener la información del producto')
                    try:
                        # Se obtiene el código HTML de la respuesta del servidor de Amazon
                        html = response.text

                        # Una vez tenemos el código HTML, se comprueba si contiene la información deseada, o Amazon ha
                        # detectado nuestro acceso automatizado
                        if 'For automated access to price change or offer listing change events' in html:
                            print('Amazon ha detectado un acceso automático, lo intentaremos de nuevo en 18 segundos...')
                            time.sleep(18)
                            continue

                        # Si hemos superado la prueba anterior y Amazon nos ha devuelto información útil sobre el proyecto,
                        # entonces extraemos la información del mismo. Esta consta de:
                        # 1 - URL de la imagen principal:
                        url_imagen_principal = methods.parse_url_imagen_principal(html)
                        # Siempre al final de cada parámetro del producto, comprobamos si hemos obtenido correctamente la información
                        if not url_imagen_principal:
                            print('Ha habido un fallo en el parseo de datos, abandonamos el  producto')
                            break

                        # 2 - Precio:
                        detalles_precio = methods.parser_precio(html)
                        precio_antes = detalles_precio['precio_antes']
                        precio_final = detalles_precio['precio_final']
                        ahorro_euros = detalles_precio['ahorro_euros']
                        ahorro_porciento = detalles_precio['ahorro_porciento']
                        # El precio_final es requisito para que se considere correcta la información obtenida
                        if not precio_final:
                            print('Ha habido un fallo en el parseo de datos, abandonamos el  producto')
                            break

                        # 3 - Nombre:
                        nombre = methods.parse_nombre(html)
                        if not nombre:
                            print('Ha habido un fallo en el parseo de datos, abandonamos el  producto')
                            break

                        # 4 - Categoría:
                        categoria_name = methods.parse_categoria(html)
                        if categoria_name:
                            categoria = Categoria.get_categoria_from_name(categoria_name)
                        else:
                            print('Ha habido un fallo en el parseo de datos, abandonamos el  producto')
                            break

                        # 5 - ASIN
                        asin = methods.parse_asin(html)

                        # 6 - Cantidad de opiniones
                        opiniones = methods.parse_opiniones(html)

                        # 7 - Evaluación promedio
                        evaluacion = methods.parse_evaluacion(html)

                        n_producto = cls.nuevo_producto(
                            nombre = nombre,
                            precio_antes = precio_antes,
                            precio_final = precio_final,
                            ahorro_euros = ahorro_euros,
                            ahorro_porciento = ahorro_porciento,
                            categoria = categoria,
                            url_afiliado = url_producto,
                            url_imagen_principal = url_imagen_principal,
                            asin = asin,
                            opiniones = opiniones,
                            evaluacion = evaluacion,
                        )
                        if n_producto:
                            print('Se ha creado correctamente el nuevo Producto: %s' %n_producto)
                        else:
                            print('No se ha podido crear el nuevo Producto')

                        # Si logramos crear el producto, salimos del for de intentos
                        break

                    except Exception as e:
                        print(e)
                        print('Ha habido un fallo en el parseo de datos, abandonamos el  producto')
                        break

                elif response.status_code == 404:
                    print('Amazon ha respondido un código 404, abandonamos el  producto')
                    break
                elif response.status_code == 503:
                    print('Amazon ha baneado nuestra IP. Hay que esperar e intentarlo otro día')
                    break
                else:
                    print('Hemos obtenido un código %s por parte de Amazon, es imposible procesar la petición' %response.status_code)

        except Exception as e:
        # else:
            print(e)
            print('Ha habido un fallo en el parseo de datos, abandonamos el  producto')

    # Declaración del object manager
    objects = Producto_Manager()

    class Meta():
        verbose_name_plural = 'Productos'

    def __str__(self):
        if self.nombre:
            return self.nombre
        else:
            return 'Producto sin nombre'