import requests
import configparser
import time
import os
from urllib.parse import urlparse
from pixellib.tune_bg import alter_bg
import sys
import csv
from PIL import Image
import random

def generarfondo(file):
    png_image = Image.open(file)

    rgb_image = png_image.convert('RGB')

    rgb_image.save('imagenjpeg.jpg', 'JPEG')

    image = Image.open('imagenjpeg.jpg')

    cropped_image = image.crop((1073 + 250, 0, image.width - 550 - 200, image.height - 275))
    encabezado = cropped_image.crop((0, 0, cropped_image.width, 705))

    tabla = cropped_image.crop((0, 705, cropped_image.width, cropped_image.height))

    colorheader = (6, 105, 250)
    extension_color = (26, 114, 246)

    fondosuperior = Image.new('RGB', (cropped_image.width + 450 + 600, 705), colorheader)
    ImagenFondo = Image.new('RGB', (cropped_image.width + 450 + 600, cropped_image.height), extension_color)

    ImagenFondo.paste(fondosuperior, (0, 0))
    ImagenFondo.paste(encabezado, (600, 0))
    ImagenFondo.paste(tabla, (1045, 705))

    ImagenFondo.save('ImagenFondo.jpg')

def generar_imagen(imagen_fondo, imagen_presentador, imagen_resultante):
    try:
        change_bg = alter_bg(model_type = "pb")
        change_bg.load_pascalvoc_model("xception_pascalvoc.pb")
        change_bg.change_bg_img(f_image_path = imagen_presentador,
                                b_image_path = imagen_fondo, 
                                output_image_name = imagen_resultante)
        print("+--------------------------------------------+")
        print("|        Imagen generada con éxito!!!        |")
        print("+--------------------------------------------+")
    except:
        print("!!!!!!!!!ERROOOOOOOOOOOOOOOOOOR!!!!!!!!!")
        print("Se generó un problema al generar la imagen")

def leertabla(file):
    def redondeo(x):
        y = 100
        if x <= 14:
            y = 10
        elif x > 14 and x <= 24:
            y = 20
        elif x > 24 and x <= 34:
            y = 30
        elif x > 34 and x <= 44:
            y = 40
        elif x > 44 and x <= 54:
            y = 50
        elif x > 54 and x <= 64:
            y = 60 
        elif x > 64 and x <= 74:
            y = 70
        elif x > 74 and x <= 84:
            y = 80
        elif x > 84 and x <= 90:
            y = 90
        elif x > 90:
            y = 100
        return y

    def mapear_probs(tablacsv):
        with open(tablacsv, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            mapping = dict()
            for line in reader:
                if line[0] in ("ElCamal", "SanAntonio", "Tumbaco"):
                    pass
                elif line[0] == "Centro":
                    mapping["el centro"] = redondeo(float(line[-1]))
                elif line[0] == "Belisario":
                    mapping["la carolina"] = redondeo(float(line[-1]))
                elif line[0] == "LosChillos":
                    mapping["los chillos"] = redondeo(float(line[-1]))
                else:
                    mapping[line[0]] = redondeo(float(line[-1]))
        probs = dict()
        for zona in mapping:
            if mapping[zona] in probs:
                probs[mapping[zona]].append(zona)
            else:
                probs[mapping[zona]] = [zona]
        return probs
    FrasesSol = [
        ", por lo que deberías considerar usar protector solar. ",
        ", así que debes protegerte de la radiación. ",
        ", así que se espera un buen día soleado. ",
        ". "
    ]
    FrasesLluvia = [
        ", por lo que no deberías olvidar tu paraguas. ",
        ", así que es mejor que salgas con una buena chompa. ",
        ", así que piénsalo dos veces si planeas salir a caminar. ",
        ". "
    ]
    def generartexto(probs):
        mensaje = f"Hola con todos, les voy a presentar las probabilidades de lluvia para algunas de las zonas de Quito. "
        for proba in probs:
            if proba <= 10:
                frase = random.choice(FrasesSol)
            elif proba >= 80:
                frase = random.choice(FrasesLluvia)
            else:
                frase = ". "

            if len(probs[proba]) > 1:
                mensaje += "En "
                for zona in probs[proba][:-1]:
                    mensaje += f"{zona}, "
                mensaje += f"y {probs[proba][-1]}, la probabilidad de lluvia es del {proba:.0f} por ciento" + frase
            else:
                mensaje += f"En {probs[proba][0]}, la probabilidad de lluvia es del {proba:.0f} por ciento" + frase
        return mensaje

    probs = mapear_probs(file)
    return generartexto(probs)

def acceder_api(credenciales):
    try:
        config = configparser.ConfigParser()
        config.read(credenciales) # "api_video.ini"

        user = config['d-id']['user']
        password = config['d-id']['password']

        header = {
            'Authorization': f'Basic {user}:{password}'
        }

        headers = {
        "accept": "application/json",
        "authorization": f'Basic {user}:{password}'
        }
        print("+--------------------------------------------+")
        print("|        Acceso a la API con éxito!!!        |")
        print("+--------------------------------------------+")
    except:
        print("!!!!!!!!!ERROOOOOOOOOOOOOOOOOOR!!!!!!!!!")
        print("Se generó un problema al acceder a la API")
    return header, headers

def obtener_url_imagen(imagen, headers):
    urlimg = "https://api.d-id.com/images"
    files = { "image": (imagen, open(imagen, "rb"), "image/jpeg") }
    responseimg = requests.post(urlimg, files = files, headers = headers).json()
    return responseimg['url'], responseimg['id']

def download_video(url, save_directory):
    response = requests.get(url)
    filename = os.path.basename(urlparse(url).path) ###########
    save_path = os.path.join(save_directory, 'NuevoVideo.mp4')

    with open(save_path, 'wb') as f:
        f.write(response.content)
    return save_path

def generar_video(url_imagen, texto, header, voz):
    url = "https://api.d-id.com/talks"

    info_video = {
        "source_url": url_imagen,
        "script": {
            "type": "text",
            "input": texto,
            "provider": {
                "type": "microsoft",
                "voice_id": voz,
                "voice_config": {
                    "style": "Cheerful"
                }
            }
        },
        "config": {
            "stitch": True
        }
    }

    response_post = requests.post(url, json = info_video, headers = header).json()
    print(response_post)
    response_get = requests.get(url + f'/{response_post["id"]}', headers = header).json()

    while 'result_url' not in response_get:
        time.sleep(10)
        response_get = requests.get(url + f'/{response_post["id"]}', headers = header).json()

    video_url = response_get['result_url']
    save_directory = os.getcwd()

    video_path = download_video(video_url, save_directory)
    return video_path

def borrar_imagen(id_imagen, headers):
    urlimg = "https://api.d-id.com/images"
    url_delete_imagen = urlimg + '/' + id_imagen
    requests.delete(url_delete_imagen, headers = headers)

def main():
    if len(sys.argv) != 4: 
        sys.exit('El uso adecuado es: python video_talks.py "Prob_lluvia_bc.png" "api_video.ini" "PREC_Estaciones.csv"')

    generarfondo(sys.argv[1])
    #voces = ["es-BO-SofiaNeural", "es-CL-CatalinaNeural",
    #         "es-CR-MariaNeural", "es-BO-MarceloNeural",
    #         "es-CL-LorenzoNeural", "es-GT-AndresNeural"]
    voces = ["es-CL-CatalinaNeural", "es-GT-AndresNeural",
             "es-BO-MarceloNeural", "es-CR-MariaNeural",
             "es-BO-SofiaNeural", "es-CL-LorenzoNeural"]
    presentadores = [(presentador, voz) for (presentador, voz) in zip(os.listdir('presentadores'), voces)]
    presentador, voz = random.choice(presentadores)
    
    imagen_presentador = presentador

    imagen_fondo = sys.argv[1]
    credenciales = sys.argv[2]
    tabla = sys.argv[3]
    
    generar_imagen('ImagenFondo.jpg', 'presentadores/'+imagen_presentador, 'nueva_imagen.jpg')
    texto = leertabla(tabla)
    header, headers = acceder_api(credenciales)
    url_imagen_final, id_imagen = obtener_url_imagen('nueva_imagen.jpg', headers)
    video_path = generar_video(url_imagen_final, texto, header, voz)
    print(video_path)
    borrar_imagen(id_imagen, headers)

if __name__ == "__main__":
    main()