from PIL import Image

def crop_from_center(image_path, width, height, save=False):
    image_file = Image.open(image_path)
    # 1 - Detectar el mayor de los lados para adaptarlo al marco deseado
    w, h = image_file.size
    if w > h:
        r_factor = h / height
    else:
        r_factor = w / width

    # 2 - Redimensionar la imagen al marco
    resized_img = image_file.resize((int(round(w / r_factor, 0)), int(round(h / r_factor, 0))), Image.ANTIALIAS)

    # 3 - Seleccionar el fragmento de la imagen centrado deseado
    croped_img = resized_img.crop(
        (
            (resized_img.width / 2 - width / 2),
            (resized_img.height / 2 - height / 2),
            # Coordenadas de inicio de recorte (x, y)
            (resized_img.width / 2 - width / 2) + width,
            (resized_img.height / 2 - height / 2) + height
        )
    )# Coordenadas de fin de recorte (x, y)
    if save:
        croped_img.save(image_path)

    # 4 - Devolver la imagen modificada
    return croped_img

from support.globals__dev import *
from support.globals__prod import *