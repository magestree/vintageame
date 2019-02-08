from decimal import Decimal

def parse_url_imagen_principal(html):
    print('======== EXTRAYENDO URL IMAGEN PRINCIPAL =========')
    detalles_imagenes = {
        'url_imagen_principal': None,
    }
    if '<li class="image item itemNo0' in html:
        bloque1 = html.split('<li class="image item itemNo0')[1]
        if 'data-old-hires="' in bloque1:
            bloque2 = bloque1.split('data-old-hires="')[1]
            if '"' in bloque2:
                url_imagen_principal = bloque2.split('"')[0]
                if len(url_imagen_principal) > 20 and 'https://' in url_imagen_principal and '.jpg' in url_imagen_principal:
                    detalles_imagenes['url_imagen_principal'] = url_imagen_principal
                    print('Se ha obtenido la url_imagen_principal: %s' % url_imagen_principal)
                else:
                    print('El formato de la URL (%s) es incorrecto' %url_imagen_principal)
            else:
                print('No se ha encontrado " en el código html buscado')

            # Si no se ha podido obtener la url de la imagen con la primera estructura, se prueba con una segunda
            if not detalles_imagenes['url_imagen_principal']:
                if 'jpg' in bloque2:
                    bloque3 = bloque2.split('jpg')[0]
                    if 'https' in bloque3:
                        bloque4 = bloque3.split('https')[1]
                        url_imagen_principal = 'https%sjpg' % bloque4
                        if len(url_imagen_principal) > 20 and 'https://' in url_imagen_principal and '.jpg' in url_imagen_principal:
                            detalles_imagenes['url_imagen_principal'] = url_imagen_principal
                            print('Se ha obtenido la url_imagen_principal: %s' % url_imagen_principal)
                        else:
                            print('El formato de la URL (%s) es incorrecto' % url_imagen_principal)
                    else:
                        print('No se ha encontrado https en el código fuente')
                else:
                    print('No se ha encontrado jpg en el código html buscado')
        else:
            print('No se ha encontrado "data-old-hires" en el código html buscado')
    else:
        print('No se ha encontrado "<li class="image item itemNo0" en el código html buscado')

    if 'url_imagen_principal' in detalles_imagenes:
        return detalles_imagenes['url_imagen_principal']
    else:
        return None

def parse_nombre(texto):
    print('======== EXTRAYENDO NOMBRE =========')
    nombre = texto.split('<title>')[1].split('</title>')[0]
    if ': Amazon.es:' in nombre:
        nombre = nombre.split(': Amazon.es:')[0]
    else:
        return None
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
    if '&#xFF08;' in nombre:
        nombre = nombre.replace('&#xFF08;', '(')
    if '&#xFF09;' in nombre:
        nombre = nombre.replace('&#xFF09;', ')')
    if '&#39;' in nombre:
        nombre = nombre.replace('&#39;', "'")

    if len(nombre) > 512:
        print('El nombre es demasiado largo, está mal')
        return None

    # Si se obtiene un nombre que parece estar bien, solo nos quedamos con los primeros 60 caracteres para garantizar un tamaño
    # más o menos fijo en la vista previa del producto
    nombre = nombre[:90]

    print('Se ha obtenido satisfactoriamente el nombre del producto: %s' %nombre)
    return nombre

def parse_categoria(html):
    print('======== EXTRAYENDO CATEGORÍA =========')
    categoria_text = html.split('</title>')[0].split('Amazon.es: ')[-1]
    if len(categoria_text) > 64:
        print('No hemos podido obtener el nombre de la categoría del <title>, así que buscaremos por showing-breadcrumbs_div')
        if 'showing-breadcrumbs_div' in html:
            bloque1 = html.split('showing-breadcrumbs_div')[1]
            bloque2 = bloque1.split('<a class=')[1]
            bloque3 = bloque2.split('</a>')[0]
            # Eliminamos los saltos de línea
            bloque4 = bloque3.split('">')[-1].replace('\n', '')
            # Eliminamos los espacios en blanco el inicio y al final del string
            while bloque4[0] == ' ':
                bloque4 = bloque4[1:]
            while bloque4[-1] == ' ':
                bloque4 = bloque4[:-1]

            categoria_text = bloque4
            print('Obtenido satisfactoriamente el nombre de Categoría: %s' %categoria_text)
        else:
            print('Tampoco hemos encontrado showing-breadcrumbs_div en el código fuente.')
            return None
    else:
        print('Obtenido satisfactoriamente el nombre de Categoría: %s' %categoria_text)

    # Previniendo el caso de Categoría: Amazon.es
    if 'Amazon' in categoria_text:
        print('La categoría %s no es válida.' %categoria_text)
        return None
    else:
        # Solo llegando aquí habremos obtenido un nombre de categoría posiblemente válido
        return categoria_text

def parser_precio(text):
    print('======== EXTRAYENDO PRECIOS =========')
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
            print('Se ha encontrado un precio en rebaja')
            try:
                precio_antes = Decimal(div_precio.split('<span class="a-text-strike"> EUR ')[1].split('</span>')[0].replace(',', '.'))
                data_precio['precio_antes'] = precio_antes
                print('Se ha obtenido satisfactoriamente el precio anterior: %s €' %precio_antes)
            except:
                print('Error extrayendo el precio original del producto')
        else:
            print('No se han encontrado precios anteriores')

        # 2 - precio_final
        if '<span id="priceblock_ourprice" class="a-size-medium a-color-price">' in div_precio:
            try:
                precio_text = div_precio.split('<span id="priceblock_ourprice" class="a-size-medium a-color-price">EUR ')[1].split('</span>')[0].replace(',', '.')
                if ' - ' in precio_text:
                    precio_final = Decimal(precio_text.split(' - ')[0])
                else:
                    precio_final = Decimal(precio_text)
                data_precio['precio_final'] = precio_final
                print('Se ha obtenido satisfactoriamente el precio final: %s €' % precio_final)
            except:
                print('Error extrayendo el precio final del producto')
    else:
        print('No se ha encontrado <div id="price" así que buscamos <div id="unqualifiedBuyBox"')
        if '<div id="unqualifiedBuyBox"' in text:
            precio_final = Decimal(text.split('<div id="unqualifiedBuyBox"')[1].split('>EUR ')[1].split('</span>')[0].replace(',', '.'))
            if precio_final:
                data_precio['precio_final'] = precio_final
                print('Se ha obtenido correctamente el precio del producto: %s' %data_precio['precio_final'])
            else:
                print('No se ha podido obtener el precio filnal del producto')
        else:
            print('No se ha encontrado <div id="unqualifiedBuyBox" tampoco en el código fuente')

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

def parse_asin(texto):
    if '<input type="hidden" id="ASIN" name="ASIN" value="' in texto:
        asin = texto.split('<input type="hidden" id="ASIN" name="ASIN" value="')[1].split('"')[0]
    else:
        asin = None
    return asin

def parse_opiniones(texto):
    if '<span id="acrCustomerReviewText" class="a-size-base">' in texto:
        opiniones = int(texto.split('<span id="acrCustomerReviewText" class="a-size-base">')[1].split(' ')[0])
    else:
        opiniones = None
    return opiniones

def parse_evaluacion(texto):
    if '<span id="acrPopover" class="reviewCountTextLinkedHistogram noUnderline" title="' in texto:
        return Decimal(
            texto.split('<span id="acrPopover" class="reviewCountTextLinkedHistogram noUnderline" title="')[1].split(' ')[0])
    else:
        return None

# A partir de todas las urls de productos asociadas a un Proyecto, crea los Productos que no existan en relacion a cada URL
# def create_productos_from_urls():
#     # Se separan las urls almacenadas en el campo "urls_productos", por saltos de línea.
#     urls_productos = self.urls_productos.split('\n')
#     productos_proyecto = []
#     for url_producto in urls_productos:
#         # Debemos asegurarnos que la url no contiene comas o espacios
#         url_producto = url_producto.replace(',', '').replace(' ', '')
#
#         # Obtenemos o creamos un objeto Producto, asociado a cada url_producto
#         producto, created = Producto.objects.get_or_create(url_afiliado = url_producto)
#         productos_proyecto.append(producto)
#
#     # Se devuelve la lista de todos los productos relacionados con la url definida
#     return productos_proyecto