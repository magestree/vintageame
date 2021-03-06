from django.db import models
from support.urls_productos import urls_productos
from support.descripciones_categorias import categorias
# from support.globals import API_URLS
import requests, time, json, shutil, random
import urllib3, os, shutil, math
from support import methods
from django.template.defaultfilters import slugify
from api.models import API_Client, App
from support.globals import proxies

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    nombre_corto = models.CharField('Nombre corto', max_length = 40 ,blank = True, null = True)
    url_amigable = models.SlugField('URL amigable', max_length = 512, blank = True, null = True)
    descripcion_breve = models.TextField('Descripción breve', blank = True, null = True, max_length = 2048)
    descripcion = models.TextField('Descripción', blank = True, null = True, max_length = 4096)
    texto_seo = models.TextField('Texto SEO', blank = True, null = True)

    def mejor_producto(self):
        # Devuelve el Producto que más revisiones y mejor valoración tiene
        return self.producto_set.order_by('-opiniones', '-evaluacion', 'precio_final').first()

    @classmethod
    # Elimina todas las categorías que no tengan al menos un Producto asociado
    def eliminar_categorias_sin_productos(cls):
        for categoria in cls.objects.all():
            if not categoria.producto_set.all():
                categoria.eliminar_categoria()

    @classmethod
    def get_categorias_as_dict(cls):
        # Devuelve una lista de todas las categorías en forma de diccionarios
        categorias_dict = []
        for categoria in cls.objects.all():
            categorias_dict.append(categoria.get_categoria_as_dict())
        return categorias_dict

    def get_categoria_as_dict(self):
        # Devuelve el objeto Categoria como un diccionario, listo para ser enviado vía REST
        categoria_dict = {
            'nombre': self.nombre,
            'nombre_corto': self.nombre_corto,
            'url_amigable': self.url_amigable,
            'descripcion_breve': self.descripcion_breve,
            'descripcion': self.descripcion,
            'texto_seo': self.texto_seo,
        }
        return categoria_dict

    def actualizar_descripcion_categoria(self):
        for categoria in categorias:
            if categoria.get('nombre').lower() == self.nombre.lower():
                self.descripcion = categoria.get('descripcion')
                self.descripcion_breve = categoria.get('descripcion_breve')
                self.save()
                print('Se ha actualizado correctamente la descripción de la categoría: %s' %self.nombre)
                # Una vez hemos encontrado una categoría y actualizado su descripción salimos de la búsqueda
                break

    def actualizar_texto_seo_categoria(self):
        for categoria in categorias:
            if categoria.get('nombre').lower() == self.nombre.lower():
                self.texto_seo = categoria.get('texto_seo')
                self.save()
                print('Se ha actualizado correctamente el texto SEO de la categoría: %s' %self.nombre)
                # Una vez hemos encontrado una categoría y actualizado su descripción salimos de la búsqueda
                break

    @classmethod
    def actualizar_textos_categorias(cls):
        for categoria in cls.objects.all():
            categoria.actualizar_descripcion_categoria()
            categoria.actualizar_texto_seo_categoria()

    @classmethod
    def get_categoria_from_name(cls, categoria_name):
        categoria = cls.objects.filter(nombre = categoria_name)
        if not categoria:
            print('No existe ninguna categoría con nombre %s, así que la creamos' %categoria_name)
            categoria = Categoria.nueva_categoria(
                nombre = categoria_name,
                descripcion = None,
                descripcion_breve = None,
                texto_seo = None,
            )
            # Se actualiza la descripción de la categoría
            for c in categorias:
                if c.get('nombre').lower() == categoria.nombre.lower():
                    categoria.descripcion = c.get('descripcion')
                    categoria.descripcion_breve = c.get('descripcion_breve')
                    categoria.texto_seo = c.get('texto_seo')
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
    def nueva_categoria(cls, nombre, descripcion, descripcion_breve, texto_seo):
        if not cls.objects.filter(nombre = nombre):
            n_categoria = cls.objects.create(
                nombre = nombre,
                nombre_corto = nombre[:39] + '...',
                url_amigable = slugify(nombre),
                descripcion = descripcion,
                descripcion_breve = descripcion_breve,
                texto_seo = texto_seo,
            )
            return n_categoria
        else:
            print('Ya existe una categoría con nombre %s así que no podemos crearla' %nombre)
            return None

    def modificar_categoria(self, nombre, descripcion, descripcion_breve, texto_seo):
        if self.nombre != nombre:
            self.nombre = nombre
            self.nombre_corto = nombre[:39] + '...'
            self.url_amigable = slugify(nombre)
        if self.descripcion != descripcion:
            self.descripcion = descripcion
        if self.descripcion_breve != descripcion_breve:
            self.descripcion_breve = descripcion_breve
        self.texto_seo = texto_seo
        self.save()
        return self

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
    asin = models.CharField('ASIN', max_length = 16, blank = False, null = False, unique = True)
    opiniones = models.IntegerField('Opiniones', blank = True, null = True, unique = False)
    evaluacion = models.DecimalField('Evaluación',  max_digits = 3, decimal_places = 2, blank = True, null = True, unique = False)
    fecha_registro = models.DateTimeField('Fecha de registro', blank = True, null = True, auto_now_add = True)

    @classmethod
    def clasificar_segun_existencia(cls, urls_productos):
        urls_productos_inexistentes, urls_productos_existentes = [], []
        for url_producto in urls_productos:
            if Producto.objects.filter(url_afiliado=url_producto):
                urls_productos_existentes.append(url_producto)
            else:
                urls_productos_inexistentes.append(url_producto)
        return urls_productos_inexistentes, urls_productos_existentes

    def partial_name(self):
        # Devuelve la primera parte del nombre de un producto
        return ' '.join(self.nombre.split(' ')[:4])

    @classmethod
    def sincronizar_productos(cls):
        # Esta sincronización consta de dos partes fundamentales:
        # 1 - Actualizar Productos y Categorías en la versión local a partir de Amazon

        # 1.1 - Eliminar aquellos productos de nuestra Base de Datos que no estén en la lista de referencia para sincronizar con Amazon
        cls.eliminar_productos_excluidos(urls_productos = urls_productos)

        # 1.2 - Sincronizar productos desde Amazon a nuestra versión local
        # Primero hacemos una lista de las urls de productos que no tenemos y que si tenemos para priorizar aquellos que no tenemos
        urls_productos_inexistentes, urls_productos_existentes = Producto.clasificar_segun_existencia(urls_productos)
        print('Iniciando registro de nuevos productos (%s)...' %(len(urls_productos_inexistentes)))
        cls.sincronizar_productos_from_amazon(urls_productos_inexistentes) # Se priorizan las URLS inexistentes

        print('')
        print('Iniciando la actualización de los productos existentes (%s)...' %(len(urls_productos_existentes)))
        cls.sincronizar_productos_from_amazon(urls_productos_existentes) # Luego se sincronizan las URLS existentes, es decir, se actualiza la información

        # 1.3 - Actualizar las textos (descripción, descripción breve y textos SEO) de las categorías y eliminar aquellas categorías que no tengan productos asociados
        Categoria.actualizar_textos_categorias()

        # 1.4 - Eliminar aquellas Categorías de nuestra BD que no tengan ningún Producto asociado
        Categoria.eliminar_categorias_sin_productos()

        # 2 - Actualizar las versiones de preproducción y producción del sitio a partir de los productos y categorías en nuestra versión de desarrollo
        # 2.1 - Añadir/Modificar todos aquellos productos que tengamos en nuestra versión de desarrollo
        cls.sync_remote_products()

    @classmethod
    # 1.1 - sincronizar productos from Amazon
    def sincronizar_productos_from_amazon(cls, urls_productos):
        # En caso de que entremos a este método sin urls que procesar, es como único saldremos de él
        if not urls_productos:
            print('Hemos concluído con la sincronización de este grupo de urls :)')
            print('')
            return

        available_proxies = random.sample(proxies, len(proxies))
        for proxy in available_proxies:

            if not urls_productos:
                return

            print('====== UTILIZANDO EL PROXY (%s de %s): %s ======' %(proxies.index(proxy), len(proxies), proxy))
            for url_producto in random.sample(urls_productos, len(urls_productos)):

                print('Sincronizando Producto (%s de %s): %s' %(urls_productos.index(url_producto) + 1, len(urls_productos), url_producto))
                done = cls.sincronizar_producto_from_url(url_producto)

                # done puese ser:
                # 1 - success --------> Se ha completado con éxito la extracción de datos
                # 2 - fail -----------> Ha fallado la extración de datos
                # 3 - banned ---------> Amazon ha baneado nuestra IP y nos devuelve 503
                # 4 - detectado ------> Amazon ha detectado el acceso automático y nos devuelve 200 pero sin información
                # 5 - not_found ------> El link no es correcto y Amazon nos devuelve 404

                # Si done es: banned o detectado, cambiamos de proxy
                if done == 'banned':
                    # En este caso NO eliminamos la url procesada de las urls_productos
                    print('Amazon ha bloqueado la IP: %s' %proxy)
                    break
                elif done == 'detectado':
                    # En este caso NO eliminamos la url procesada de las urls_productos
                    print('Amazon ha detctado que es un acceso automático y no nos ha dejado acceder a la información desde %s' %proxy)
                    print('')
                    break

                # Si done es: fail o not_found, pasamos al siguiente producto
                elif done == 'fail':
                    # En este caso eliminamos la url procesada de las urls_productos
                    urls_productos.remove(url_producto)
                    print('Ha habido un error en el parseo de datos para la URL: %s' %url_producto)
                    print('')
                    continue
                elif done == 'not_found':
                    # En este caso eliminamos la url procesada de las urls_productos
                    urls_productos.remove(url_producto)
                    print('Esta URL parece incorrecta: %s' %url_producto)
                    print('')
                    continue

                # Si done es success, pasamos al siguiente producto
                elif done == 'success':
                    # En este caso eliminamos la url procesada de las urls_productos
                    urls_productos.remove(url_producto)
                    print('Se ha terminado de actualizar con éxito la información del producto con la URL: %s' %url_producto)
                    print('')
                    continue

            # Llegar a este punto quiere decir que he terminado de repasar todas las URLS, en cuyo caso volvemos a
            # inicializar el método con la lista de urls actualizadas
            cls.sincronizar_productos_from_amazon(urls_productos = urls_productos)

        # Una vez llego a este punto, hemos utilizado todos los proxies disponibles, así que volvemos a
        # inicializar el método con la lista de urls actualizadas
        cls.sincronizar_productos_from_amazon(urls_productos=urls_productos)

    @classmethod
    # 1.2 - Eliminar aquellos productos de nuestra Base de Datos que no estén en la lista de referencia para sincronizar con Amazon
    def eliminar_productos_excluidos(cls, urls_productos):
        print('Eliminando Productos de nuestra BD que no estén en la lista de urls...')
        for producto in cls.objects.all():
            if not producto.url_afiliado in urls_productos:
                producto.eliminar_producto()
        print('')

    @classmethod
    # Descarga en un directorio del servidor todas las imágenes de los Productos en nuestra BD
    def download_products_images(cls):
        for url in cls.objects.values_list('url_imagen_principal', flat=True):
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open('/var/www/imagenes_productos/%s' %url.split('/')[-1], 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
            time.sleep(1)

    @classmethod
    def sync_remote_products(cls):
        # Con las descripciones de las Categorías actualizadas, se pasa a sincronizar todos los Productos de las versiones remotas
        api_clients = API_Client.objects.filter(activo = True)
        for api_client in api_clients:
            app = App.objects.get(api_client = api_client)
            print('Sincronizando productos en: %s' %api_client.nombre)
            urls_amigables = []
            for producto_dict in Producto.get_productos_as_dict():
                urls_amigables.append(producto_dict.get('url_amigable'))
                r = app.add_product(producto_dict)

            # Una vez añadidos o modificados en remoto todos los Productos que hay en local, eliminamos aquellos productos remotos que no estén en local
            for producto in app.get_products().get('productos'):
                if not producto.get('url_amigable') in urls_amigables:
                    app.delete_product(producto.get('url_amigable'))

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
    def get_edge_prices(cls, productos):
        # Devuelve el precio mínimo y máximo de todos los productos de un conjunto
        # productos debe ser una Queryset
        productos = productos.order_by('precio_final')
        min_price = math.floor(productos.first().precio_final)
        max_price = math.ceil(productos.last().precio_final)
        return [min_price, max_price]

    def verificar_producto(self):
        # Las pruebas a las que se somete un producto son:
        # 1 - Que tenga un nombre, una categoría y una foto
        if self.nombre and self.categoria and self.url_imagen_principal:
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
        if not cls.objects.filter(asin = asin):
            n_producto = cls.objects.create(
                nombre = nombre,
                nombre_corto = nombre[:90] + '...',
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
            producto = cls.objects.get(asin = asin)
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
        print('Eliminando producto %s' %self.nombre)
        categoria_url_amigable = self.categoria.url_amigable
        self.delete()

        # Siempre que se elimina un Producto, se comprueba si su Categoría se queda sin productos. En ese caso también se elimina
        if not Categoria.objects.get(url_amigable = categoria_url_amigable).producto_set.all():
            Categoria.objects.get(url_amigable = categoria_url_amigable).eliminar_categoria()

    @classmethod
    def sincronizar_producto_from_url(cls, url_producto, proxy = None):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}

        try:
        # if True:
            # Se realizan hasta 30 intentos de recuperación de información por producto,
            # por si Amazon detecta una y otra vez un acceso automatizado
            for attempt in range(30):
                # Se realiza una petición GET a la url del producto en Amazon
                if proxy:
                    response = requests.get(url_producto, headers = headers, verify = False, proxies = {'https': 'https://%s' %proxy})
                else:
                    response = requests.get(url_producto, headers = headers, verify = False)

                # Si el código recibido es 200, la conexión ha sido exitosa y se procede con el parseo de información
                if response.status_code == 200:
                    try:
                    # if True:
                        # Se obtiene el código HTML de la respuesta del servidor de Amazon
                        html = response.text

                        # Una vez tenemos el código HTML, se comprueba si contiene la información deseada, o Amazon ha
                        # detectado nuestro acceso automatizado
                        if 'For automated access to price change or offer listing change events' in html:
                            # w = random.randint(1, 3)
                            # print('Amazon ha detectado un acceso automático, lo intentaremos de nuevo en %s segundos...' %w)
                            # time.sleep(w)
                            continue

                        # Si hemos superado la prueba anterior y Amazon nos ha devuelto información útil sobre el proyecto,
                        # entonces extraemos la información del mismo. Esta consta de:
                        # 1 - URL de la imagen principal:
                        url_imagen_principal = methods.parse_url_imagen_principal(html)
                        # Siempre al final de cada parámetro del producto, comprobamos si hemos obtenido correctamente la información
                        if not url_imagen_principal:
                            print('Ha habido un fallo en el parseo de datos, abandonamos el  producto')
                            return 'fail'

                        # 2 - Precio:
                        detalles_precio = methods.parser_precio(html)
                        precio_antes = detalles_precio['precio_antes']
                        precio_final = detalles_precio['precio_final']
                        ahorro_euros = detalles_precio['ahorro_euros']
                        ahorro_porciento = detalles_precio['ahorro_porciento']
                        # El precio_final es requisito para que se considere correcta la información obtenida
                        if not precio_final:
                            print('Ha habido un fallo en el parseo de datos, abandonamos el  producto')
                            return 'fail'

                        # 3 - Nombre:
                        nombre = methods.parse_nombre(html)
                        if not nombre:
                            print('Ha habido un fallo en el parseo de datos, abandonamos el  producto')
                            return 'fail'

                        # 4 - Categoría:
                        categoria_name = methods.parse_categoria(html)
                        # Definimos algunas reglas para modificar posibles nombres de categorías:
                        # 4.1 - Hogar --> Hogar y cocina
                        if categoria_name == 'Hogar':
                            categoria_name = 'Hogar y cocina'
                        # 4.2 - Videojuegos --> Juguetes y juegos
                        if categoria_name == 'Videojuegos':
                            categoria_name = 'Juguetes y juegos'
                        # 4.3 - Bebé --> Juguetes y juegos
                        if categoria_name == 'Bebé':
                            categoria_name = 'Juguetes y juegos'
                        # 4.4 - Informática --> Electrónica e Informática
                        if categoria_name == 'Informática' or categoria_name == 'Electrónica':
                            categoria_name = 'Electrónica e Informática'
                        # 4.5 - Salud y cuidado personal --> Belleza
                        if categoria_name == 'Salud y cuidado personal':
                            categoria_name = 'Belleza'

                        if categoria_name:
                            categoria = Categoria.get_categoria_from_name(categoria_name)
                        else:
                            print('Ha habido un fallo en el parseo de datos, abandonamos el  producto')
                            return 'fail'

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
                        return 'success'

                    except Exception as e:
                    # else:
                        print(e)
                        print('Ha habido un fallo en el parseo de datos, abandonamos el  producto')
                        return 'fail'

                elif response.status_code == 404:
                    print('Amazon ha respondido un código 404, abandonamos el  producto')
                    return 'not_found'
                elif response.status_code == 503:
                    print('Amazon ha baneado nuestra IP. Hay que esperar e intentarlo otro día')
                    return 'banned'

                else:
                    print('Hemos obtenido un código %s por parte de Amazon, es imposible procesar la petición' %response.status_code)

            # Se llega aqui solo luego de 20 intentos fallidos de acceso, si Amazon detecta el acceso automático
            return 'detectado'


        except Exception as e:
        # else:
            print(e)
            print('Ha habido un fallo en el parseo de datos, abandonamos el  producto')
            return 'fail'

    @classmethod
    def sincronizar_producto_from_url_debug(cls, url_producto):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
        if True:
            for attempt in range(30):
                response = requests.get(url_producto, headers=headers, verify=False)
                if response.status_code == 200:
                    if True:
                        # Se obtiene el código HTML de la respuesta del servidor de Amazon
                        html = response.text

                        # Una vez tenemos el código HTML, se comprueba si contiene la información deseada, o Amazon ha
                        # detectado nuestro acceso automatizado
                        if 'For automated access to price change or offer listing change events' in html:
                            # w = random.randint(1, 3)
                            # print('Amazon ha detectado un acceso automático, lo intentaremos de nuevo en %s segundos...' %w)
                            # time.sleep(w)
                            continue

                        # Si hemos superado la prueba anterior y Amazon nos ha devuelto información útil sobre el proyecto,
                        # entonces extraemos la información del mismo. Esta consta de:
                        # 1 - URL de la imagen principal:
                        url_imagen_principal = methods.parse_url_imagen_principal(html)
                        # Siempre al final de cada parámetro del producto, comprobamos si hemos obtenido correctamente la información
                        if not url_imagen_principal:
                            print('Ha habido un fallo en el parseo de datos, abandonamos el  producto')
                            return 'fail'

                        # 2 - Precio:
                        detalles_precio = methods.parser_precio(html)
                        precio_antes = detalles_precio['precio_antes']
                        precio_final = detalles_precio['precio_final']
                        ahorro_euros = detalles_precio['ahorro_euros']
                        ahorro_porciento = detalles_precio['ahorro_porciento']
                        # El precio_final es requisito para que se considere correcta la información obtenida
                        if not precio_final:
                            print('Ha habido un fallo en el parseo de datos, abandonamos el  producto')
                            return 'fail'

                        # 3 - Nombre:
                        nombre = methods.parse_nombre(html)
                        if not nombre:
                            print('Ha habido un fallo en el parseo de datos, abandonamos el  producto')
                            return 'fail'

                        # 4 - Categoría:
                        categoria_name = methods.parse_categoria(html)
                        # Definimos algunas reglas para modificar posibles nombres de categorías:
                        # 4.1 - Hogar --> Hogar y cocina
                        if categoria_name == 'Hogar':
                            categoria_name = 'Hogar y cocina'
                        # 4.2 - Videojuegos --> Juguetes y juegos
                        if categoria_name == 'Videojuegos':
                            categoria_name = 'Juguetes y juegos'
                        # 4.3 - Bebé --> Juguetes y juegos
                        if categoria_name == 'Bebé':
                            categoria_name = 'Juguetes y juegos'
                        # 4.4 - Informática --> Electrónica e Informática
                        if categoria_name == 'Informática' or categoria_name == 'Electrónica':
                            categoria_name = 'Electrónica e Informática'
                        # 4.5 - Salud y cuidado personal --> Belleza
                        if categoria_name == 'Salud y cuidado personal':
                            categoria_name = 'Belleza'

                        if categoria_name:
                            categoria = Categoria.get_categoria_from_name(categoria_name)
                        else:
                            print('Ha habido un fallo en el parseo de datos, abandonamos el  producto')
                            return 'fail'

                        # 5 - ASIN
                        asin = methods.parse_asin(html)
                        if Producto.objects.filter(asin=asin):
                            print('El Producto con URL: "%s" ya existe en nuestra BD con la URL: "%s"' % (
                            url_producto, Producto.objects.get(asin=asin).url_afiliado))
                            return 'success'

                        # 6 - Cantidad de opiniones
                        opiniones = methods.parse_opiniones(html)

                        # 7 - Evaluación promedio
                        evaluacion = methods.parse_evaluacion(html)

                        # Si logramos crear el producto, salimos del for de intentos
                        return 'success'

                elif response.status_code == 404:
                    print('Amazon ha respondido un código 404, abandonamos el  producto')
                    return 'not_found'
                elif response.status_code == 503:
                    print('Amazon ha baneado nuestra IP. Hay que esperar e intentarlo otro día')
                    return 'banned'
                else:
                    print('Hemos obtenido un código %s por parte de Amazon, es imposible procesar la petición' % response.status_code)

            # Se llega aqui solo luego de 20 intentos fallidos de acceso, si Amazon detecta el acceso automático
            return 'detectado'

    # Declaración del object manager
    objects = Producto_Manager()

    class Meta():
        verbose_name_plural = 'Productos'

    def __str__(self):
        if self.nombre:
            return self.nombre
        else:
            return 'Producto sin nombre'