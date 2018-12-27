from django.db import models
from support import urls_productos
import requests, time
from decimal import Decimal
from random import randint
import urllib3, os, shutil
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from django.core import files
from io import BytesIO
from support.globals import crop_from_center
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
    nombre = models.TextField('Categoría', blank = False, null = False, max_length = 4096)
    url_amigable = models.SlugField('URL amigable', max_length = 512, blank = True, null = True)
    descripcion = models.TextField('Descripción', blank = True, null = True, max_length = 4096)

    @classmethod
    def nueva_categoria(cls, nombre, descripcion):
        if not cls.objects.filter(nombre = nombre):
            n_categoria = cls.objects.create(
                nombre = nombre,
                url_amigable = slugify(nombre),
                descripcion = descripcion,
            )
            return n_categoria
        else:
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
        self.delete()

    class Meta():
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre

class Sub_Categoria(models.Model):
    nombre = models.TextField('Sub Categoría', blank = False, null = False, max_length = 4096)
    url_amigable = models.SlugField('URL amigable', max_length = 512, blank = True, null = True)
    descripcion = models.TextField('Descripción', blank = True, null = True, max_length = 4096)
    categoria = models.ForeignKey(Categoria, blank = True, null = True, unique = False, on_delete = models.CASCADE)

    @classmethod
    def nueva_sub_categoria(cls, nombre, descripcion, categoria):
        if not cls.objects.filter(nombre = nombre, categoria = categoria):
            n_sub_categoria = cls.objects.create(
                nombre = nombre,
                url_amigable = slugify(nombre),
                descripcion = descripcion,
                categoria = categoria,
            )
            return n_sub_categoria
        else:
            return None

    def modificar_sub_categoria(self, nombre, descripcion, categoria):
        if not Sub_Categoria.objects.filter(nombre = nombre, categoria = categoria):
            if self.nombre != nombre:
                self.nombre = nombre
                self.url_amigable = slugify(nombre)
            if self.descripcion != descripcion:
                self.descripcion = descripcion
            if self.categoria != categoria:
                self.categoria = categoria
            self.save()
            return self
        else:
            return None

    def eliminar_sub_categoria(self):
        self.delete()

    class Meta():
        verbose_name_plural = 'Sub Categorías'

    def __str__(self):
        return '%s (%s)' %(self.nombre, self.categoria)

class Producto(models.Model):
    nombre = models.TextField('Nombre', max_length = 4096, blank = True, null = True)
    url_amigable = models.SlugField('URL amigable', max_length = 512, blank = True, null = True)
    precio_antes = models.DecimalField('Precio Antes', max_digits = 8, decimal_places = 2, blank = True, null = True, unique = False)
    precio_final = models.DecimalField('Precio Final', max_digits = 8, decimal_places = 2, blank = True, null = True, unique = False)
    ahorro_euros = models.DecimalField('Ahorro Euros', max_digits = 8, decimal_places = 2, blank = True, null = True, unique = False)
    ahorro_porciento = models.DecimalField('Ahorro en %', max_digits = 8, decimal_places = 2, blank = True, null = True, unique = False)
    categoria = models.ForeignKey(Categoria, blank = True, null = True, unique = False, on_delete = models.CASCADE)
    sub_categoria = models.ForeignKey(Sub_Categoria, blank = True, null = True, unique = False, on_delete = models.CASCADE)
    url_afiliado = models.TextField('URL Amazon', max_length = 4096, blank = True, null = True)
    url_imagen_principal = models.TextField('URL Imagen principal', max_length = 4096, blank = True, null = True)
    asin = models.CharField('ASIN', max_length = 16, blank = True, null = True, unique = True)
    opiniones = models.IntegerField('Opiniones', blank = True, null = True, unique = False)
    evaluacion = models.DecimalField('Evaluación',  max_digits = 3, decimal_places = 2, blank = True, null = True, unique = False)
    fecha_registro = models.DateTimeField('Fecha de registro', blank = True, null = True, auto_now_add = True)

    # Fotos
    foto_920_614 = models.ImageField('Foto 920 x 614', upload_to = productos_photos_920_614_directory, blank = True, null = True)
    foto_464_299 = models.ImageField('Foto 464 x 299', upload_to = productos_photos_464_299_directory, blank = True, null = True)
    foto_320_320 = models.ImageField('Foto 320 x 320', upload_to = productos_photos_320_320_directory, blank = True, null = True)

    @classmethod
    def nuevo_producto(
        cls, nombre, precio_antes, precio_final, ahorro_euros, ahorro_porciento, categoria, sub_categoria, url_afiliado,
        url_imagen_principal, asin, opiniones, evaluacion
    ):
        if not cls.objects.filter(nombre = nombre):
            n_producto = cls.objects.create(
                nombre = nombre,
                url_amigable = slugify(nombre),
                precio_antes = precio_antes,
                precio_final = precio_final,
                ahorro_euros = ahorro_euros,
                ahorro_porciento = ahorro_porciento,
                categoria = categoria,
                sub_categoria = sub_categoria,
                url_afiliado = url_afiliado,
                url_imagen_principal = url_imagen_principal,
                asin = asin,
                opiniones = opiniones,
                evaluacion = evaluacion,
            )
            n_producto.set_formatos_imagen_principal()
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
                sub_categoria = sub_categoria,
                url_afiliado = url_afiliado,
                url_imagen_principal = url_imagen_principal,
                asin = asin,
                opiniones = opiniones,
                evaluacion = evaluacion,
            )
            return producto

    def modificar_producto(
        self, nombre, precio_antes, precio_final, ahorro_euros, ahorro_porciento, categoria, sub_categoria, url_afiliado,
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
        if self.sub_categoria != sub_categoria:
            self.sub_categoria = sub_categoria
        if self.url_afiliado != url_afiliado:
            self.url_afiliado = url_afiliado
        if self.url_imagen_principal != url_imagen_principal:
            self.url_imagen_principal = url_imagen_principal
            self.save()
            self.set_formatos_imagen_principal()
        if self.asin != asin:
            self.asin = asin
        if self.opiniones != opiniones:
            self.opiniones = opiniones
        if self.evaluacion != evaluacion:
            self.evaluacion = evaluacion
        self.save()

    def eliminar_producto(self):
        self.delete()

    def eliminar_foto_producto(self, size):
        # Elimina el fichero de imagen de una foto del Producto
        if size == '920_614':
            self.foto_920_614.delete()
        elif size == '464_299':
            self.foto_464_299.delete()
        elif size == '320_320':
            self.foto_320_320.delete()

        # Comprobar si existen más fotos en el directorio definido para ello, y si no, eliminarlo
        producto_foto_path = '%s/productos/%s/fotos/%s' % (settings.MEDIA_ROOT, self.id, size)

        if os.path.exists(producto_foto_path):
            if not os.listdir(producto_foto_path):
                shutil.rmtree(producto_foto_path)
        # Luego comprueba si no hay nada más dentro de la carpeta del producto, y si es así la elimina también
        producto_path = '%s/productos/%s' % (settings.MEDIA_ROOT, self.id)
        if os.path.exists(producto_path):
            if not os.listdir(producto_path):
                shutil.rmtree(producto_path)

        # Se guarda cualquier cambio en el modelo Producto
        self.save()

    def set_formatos_imagen_principal(self):
        # Con este método se guardan la imagen principal en varios tamaños
        if len(self.url_imagen_principal) > 20:
            resp = requests.get(self.url_imagen_principal)
            if resp.status_code != requests.codes.ok:
                # Error handling here
                print('Error here!')
                return

            fp = BytesIO()
            fp.write(resp.content)
            file_name = self.url_imagen_principal.split("/")[-1]

            # 1 - 920 x 614
            if self.foto_920_614:
                self.eliminar_foto_producto(size = '920_614')
            self.foto_920_614.save(file_name, files.File(fp))
            self.save()
            crop_from_center(
                image_path = self.foto_920_614.path,
                width = 920,
                height = 614,
                save = True,
            )

            # 2 - 464 x 299
            if self.foto_464_299:
                self.eliminar_foto_producto(size = '464_299')
            self.foto_464_299.save(file_name, files.File(fp))
            self.save()
            crop_from_center(
                image_path = self.foto_464_299.path,
                width = 464,
                height = 299,
                save = True,
            )

            # 2 - 320 x 320
            if self.foto_320_320:
                self.eliminar_foto_producto(size = '320_320')
            self.foto_320_320.save(file_name, files.File(fp))
            self.save()
            crop_from_center(
                image_path=self.foto_320_320.path,
                width = 320,
                height = 320,
                save = True,
            )

    @classmethod
    def sincronizar_productos(cls):
        # Sincroniza todos los productos con Amazon a partir de la información en "support/url_productos.py"
        # Con este ciclo nos aseguramos de meter todos los productos que estén en la lista de urls de afiliado en nuestra BD
        for url in urls_productos.urls_productos:
            producto = cls.sincronizar_producto(url_afiliado = url)

            # Esperando para no estresar a Amazon
            wait = time.sleep(randint(9, 21))

    @classmethod
    def parser_precio(cls, text):
        # Devuelve un diccionario con toda la información posible del precio de un producto en Amazon.
        # Esta información se estructura de la siguiente manera:
        data_precio = {
            'precio_antes': None,
            'precio_final': None,
            'ahorro_euros': None,
            'ahorro_porciento': None,
        }

        if '<div id="price"' in text:
            # Si se encuentra el div que contiene la información del precio en el código html provisto, recoramos el texto a
            # analizar solamente al contenido de dicho div, para evitar ruido y acortar el trabajoj al procesador
            div_precio = text.split('<div id="price"')[1].split('</div>')[0]

            # 1 - precio_antes
            if '<span class="a-text-strike">' in div_precio:
                try:
                    precio_antes = Decimal(
                        div_precio.split('<span class="a-text-strike"> EUR ')[1].split('</span>')[0].replace(',', '.'))
                    data_precio['precio_antes'] = precio_antes
                except:
                    print('Error extrayendo el precio original del producto')

            # 2 - precio_final
            if '<span id="priceblock_ourprice" class="a-size-medium a-color-price">' in div_precio:
                try:
                    precio_final = Decimal(
                        div_precio.split('<span id="priceblock_ourprice" class="a-size-medium a-color-price">EUR ')[
                            1].split('</span>')[0].replace(',', '.'))
                    data_precio['precio_final'] = precio_final
                except:
                    print('Error extrayendo el precio final del producto')

            # 3 - ahorro_euros
            # Ya para los valores que faltan no es necesario parsear el html, directamente se puede calcular con los valores que tenemos
            if data_precio['precio_antes'] and data_precio['precio_final']:
                ahorro_euros = data_precio['precio_antes'] - data_precio['precio_final']
                data_precio['ahorro_euros'] = ahorro_euros

            # 4 - ahorro_porciento
            if data_precio['ahorro_euros']:
                ahorro_porciento = round(data_precio['ahorro_euros'] * 100 / data_precio['precio_antes'], 0)
                data_precio['ahorro_porciento'] = ahorro_porciento

        # Se devuelve el diccionario con la información del precio que se haya podido obtener del texto provisto
        return data_precio

    @classmethod
    def parser_imagenes(cls, texto):
        detalles_imagenes = {
            'url_imagen_principal': None,
            'urls_imagenes': [],
        }
        url_imagen_principal = texto.split('<li class="image item itemNo0')[1].split('data-old-hires="')[1].split('"')[0]
        if len(url_imagen_principal) < 20 or not 'https://' in url_imagen_principal or not '.jpg' in url_imagen_principal:

            url_imagen_principal = 'https%sjpg' %texto.split('<li class="image item itemNo0')[1].split('data-old-hires="')[1].split('jpg')[0].split('https')[1]
            if len(url_imagen_principal) < 20 or not 'https://' in url_imagen_principal or not '.jpg' in url_imagen_principal:
                print('Ha habido un problema con la URL de la imagen')
        detalles_imagenes['url_imagen_principal'] = url_imagen_principal
        return detalles_imagenes

    @classmethod
    def parse_nombre(cls, texto):
        if '"TURBO_CHECKOUT_HEADER":"Comprar ahora: ' in texto:
            nombre = texto.split('"TURBO_CHECKOUT_HEADER":"Comprar ahora: ')[1].split('","TURBO_LOADING_TEXT"')[0]
            if '&nbsp;' in nombre:
                nombre = nombre.replace('&nbsp;', ' ')
            if '&aacute;' in nombre:
                nombre = nombre.replace('&aacute;', 'á')
            if '&eacute;' in nombre:
                nombre = nombre.replace('&aacute;', 'é')
            if '&iacute;' in nombre:
                nombre = nombre.replace('&aacute;', 'í')
            if '&oacute;' in nombre:
                nombre = nombre.replace('&aacute;', 'ó')
            if '&uacute;' in nombre:
                nombre = nombre.replace('&aacute;', 'ú')
        else:
            nombre = None
        return nombre

    @classmethod
    def parse_categorias(cls, texto):
        if "<select aria-describedby='searchDropdownDescription'" in texto:
            segment = texto.split("<select aria-describedby='searchDropdownDescription'")[1].split('</select>')[0]
            categoria_text = segment.split("<option current='parent' selected='selected' value=")[1].split("</option>")[0].split('>')[1]
            categoria, created = Categoria.objects.get_or_create(
                nombre = categoria_text,
            )
        else:
            categoria = None

        if 'wayfinding-breadcrumbs_feature_div' in texto:
            sub_categoria_text = texto.split('wayfinding-breadcrumbs_feature_div')[1].split('<a class=')[1].split('</a>')[0].split('>')[1].replace('\n', '').replace('  ', '')
            sub_categoria, created = Sub_Categoria.objects.get_or_create(
                nombre = sub_categoria_text,
                categoria = categoria,
            )
        else:
            sub_categoria = None

        return categoria, sub_categoria

    @classmethod
    def parse_asin(cls, texto):
        if '<input type="hidden" id="ASIN" name="ASIN" value="' in texto:
            asin = texto.split('<input type="hidden" id="ASIN" name="ASIN" value="')[1].split('"')[0]
        else:
            asin = None
        return asin

    @classmethod
    def parse_opiniones(cls, texto):
        if '<span id="acrCustomerReviewText" class="a-size-base">' in texto:
            opiniones = int(texto.split('<span id="acrCustomerReviewText" class="a-size-base">')[1].split(' ')[0])
        else:
            opiniones = None
        return opiniones

    @classmethod
    def parse_evaluacion(cls, texto):
        if '<span id="acrPopover" class="reviewCountTextLinkedHistogram noUnderline" title="' in texto:
            return Decimal(
                texto.split('<span id="acrPopover" class="reviewCountTextLinkedHistogram noUnderline" title="')[1].split(' ')[0])
        else:
            return None

    @classmethod
    def sincronizar_producto(cls, url_afiliado):

        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}

        if True:
            # Retrying for failed requests
            for i in range(20):
                # Adding verify=False to avold ssl related issues
                response = requests.get(url_afiliado, headers = headers, verify = False)

                if response.status_code == 200:
                    r = response.text
                    # La información a extraer del Producto es:

                    # 1 - URL de la imagen principal:
                    detalles_imagenes = cls.parser_imagenes(r)
                    url_imagen_principal = detalles_imagenes['url_imagen_principal']
                    urls_imagenes = detalles_imagenes['urls_imagenes']

                    # 2 - Precio:
                    detalles_precio = cls.parser_precio(r)
                    precio_antes = detalles_precio['precio_antes']
                    precio_final = detalles_precio['precio_final']
                    ahorro_euros = detalles_precio['ahorro_euros']
                    ahorro_porciento = detalles_precio['ahorro_porciento']

                    # 3 - Nombre:
                    nombre = cls.parse_nombre(r)

                    # 4 - Categoría y Sub Categoría:
                    categoria, sub_categoria = cls.parse_categorias(r)

                    # 5 - ASIN
                    asin = cls.parse_asin(r)

                    # 6 - Cantidad de opiniones
                    opiniones = cls.parse_opiniones(r)

                    # 7 - Evaluación promedio
                    evaluacion = cls.parse_evaluacion(r)

                    n_producto = cls.nuevo_producto(
                        nombre = nombre,
                        precio_antes = precio_antes,
                        precio_final = precio_final,
                        ahorro_euros = ahorro_euros,
                        ahorro_porciento = ahorro_porciento,
                        categoria = categoria,
                        sub_categoria = sub_categoria,
                        url_afiliado = url_afiliado,
                        url_imagen_principal = url_imagen_principal,
                        asin = asin,
                        opiniones = opiniones,
                        evaluacion = evaluacion,
                    )

                    return n_producto

                elif response.status_code == 404:
                    break

        # except Exception as e:
        #     print(e)
        #     print('Ha habido un problema con %s' %url_afiliado)

    class Meta():
        verbose_name_plural = 'Productos'

    def __str__(self):
        if self.nombre:
            return self.nombre
        else:
            return 'Producto sin nombre'