import requests
import configparser 
import time
import os
from urllib.parse import urlparse
from pixellib.tune_bg import alter_bg
import sys
import csv
from PIL import Image, ImageDraw
import random
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx 
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

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

def generarfondo(Tabla_probs_csv, Tabla_probs_imagen, Imagen_ecuador):
    pichincha = gpd.read_file('Quito/quito_urbano.shp')
    marcadores = {
        10: "iconos_clima/soleado.png",
        20: "iconos_clima/parcialm_nublado.png",
        30: "iconos_clima/parcialm_nublado2.png",
        40: "iconos_clima/nublado.png",
        50: "iconos_clima/nublado.png",
        60: "iconos_clima/chubascos.png",
        70: "iconos_clima/lluvia.png",
        80: "iconos_clima/lluvia.png",
        90: "iconos_clima/lluvia_tormenta_electrica.png",
        100: "iconos_clima/tormenta_electrica.png"
    }
    def mapear_probs(tablacsv):
        with open(tablacsv, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            mapping = dict()
            for line in reader:
                if line[0] in ("ElCamal", "SanAntonio", "Tumbaco"):
                    pass
                elif line[0] == "Centro":
                    mapping["Centro"] = redondeo(float(line[-1]))
                elif line[0] == "Belisario":
                    mapping["Belisario"] = redondeo(float(line[-1]))
                elif line[0] == "LosChillos":
                    mapping["LosChillos"] = redondeo(float(line[-1]))
                else:
                    mapping[line[0]] = redondeo(float(line[-1]))
        return mapping

    stations_latlon = {
        'Belisario': (-0.18, -78.49, -65, 10),
        'Carapungo': (-0.098333, -78.447222, 20, -25),
        'Centro': (-0.22, -78.51, -50, 5),
        'Cotocollao': (-0.107778, -78.497222, -40, -25),
        'ElCamal': (-0.25, -78.51, -40, -25),
        'Guamani': (-0.330833, -78.551389, 20, -25),
        'LosChillos': (-0.3, -78.46, 30, -25),
        'SanAntonio': (0.001502, -78.447314, -60, -25),
        'Tumbaco': (-0.209999, -78.399996, -30, -25)
    }

    fig, ax = plt.subplots(figsize=(8, 8))

    pichincha.plot(ax=ax, alpha=0.3, edgecolor='k', color='grey')

    ctx.add_basemap(ax, crs=pichincha.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik, alpha=0.8)

    probs = mapear_probs(Tabla_probs_csv) 

    for (station, latlon) in stations_latlon.items():
        if station in ("ElCamal", "SanAntonio", "Tumbaco"):
            continue
        marcador = marcadores[probs[station]] 
        imagen_marcador = plt.imread(marcador)
        img = OffsetImage(imagen_marcador, zoom=0.18)  
        ab = AnnotationBbox(img, (latlon[1], latlon[0]), xycoords='data', frameon=False, xybox=(0, 9), boxcoords="offset points") 
        ax.add_artist(ab)
        ax.annotate(
            station + f" {probs[station]}%",
            xy=(latlon[1], latlon[0]),
            xytext=(latlon[2], latlon[3]),
            textcoords='offset points',
            fontsize=10,
            ha='center',
            bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.8),
            arrowprops=dict(arrowstyle='->', color='black')
        )

    plt.xlabel('')
    plt.ylabel('')
    plt.title('')
    plt.grid(False)
    plt.xticks([])
    plt.yticks([])

    plt.savefig('mapa.png', bbox_inches='tight', pad_inches=0, facecolor='#EBFAFA')

    mapa = Image.open("mapa.png")
    mapa = mapa.crop((5, 5, mapa.size[0], mapa.size[1] - 5))
    mapa.save("mapa.png")

    # Paths de las imágenes
    mapa = "mapa.png"
    ecuador = Imagen_ecuador
    encabezado = Tabla_probs_imagen

    # Cargamos imágenes 
    mapa = Image.open(mapa)
    ancho_mapa, alto_mapa = mapa.size

    ecuador = Image.open(ecuador)
    ancho_ecuador, alto_ecuador = ecuador.size

    encabezado = Image.open(encabezado)
    ancho_encabezado, alto_encabezado = encabezado.size

    # Recortamos el encabezado
    encabezado = encabezado.crop((0, 250, ancho_encabezado, 700))
    ancho_encabezado, alto_encabezado = encabezado.size

    # Recortamos la barra de los colores
    barra = ecuador.crop((20, alto_ecuador - 90, 
                          ancho_ecuador - 105, alto_ecuador))
    ancho_barra, alto_barra = barra.size

    # Recortamos la gráfica del ecuador
    lluvia = ecuador.crop((20, 48, 
                           ancho_ecuador - 105, alto_ecuador - 110))
    ancho_lluvia, alto_lluvia = lluvia.size

    # Hacemos el mapa de quito del mismo largo que el otro mapa
    ancho_deseado = int((ancho_mapa / alto_mapa) * alto_lluvia)
    mapa = mapa.resize((ancho_deseado, alto_lluvia))
    ancho_mapa, alto_mapa = mapa.size

    # Creamos nuevo canvas y pegamos las imágenes recortadas
    nuevo_canvas = Image.new('RGB', 
                             (ancho_lluvia + ancho_mapa, 
                              alto_lluvia + alto_barra),
                             color = "#EBFBFB")
    ancho_canvas, alto_canvas = nuevo_canvas.size
    nuevo_canvas.paste(barra, (0, alto_mapa))
    nuevo_canvas.paste(lluvia, (ancho_mapa, 0))
    nuevo_canvas.paste(mapa, (0, 0))

    # Definimos un dibujante para señalar a Quito en el mapa
    dibujante = ImageDraw.Draw(nuevo_canvas)

    # Definimos las coordenadas para las líneas (x0, y0, x1, y1)
    coordenadas_linea1 = (ancho_deseado, 1, 
                          530 + 2, 140 + 2)
    coordenadas_linea2 = (ancho_deseado, alto_lluvia - 1, 
                          530 + 2, 190 - 2)

    # Coordenadas de los vértices del rectángulo
    vertices = [(530, 140), (560, 140), (560, 190), (530, 190)]

    # Dibujar rectángulo y las líneas con las coordenadas
    dibujante.polygon(vertices, outline='#2E66EF', width=3)
    dibujante.line(coordenadas_linea1, fill='#2E66EF', width=4) 
    dibujante.line(coordenadas_linea2, fill='#2E66EF', width=3) 

    # Modificar el encabezado para que cuadre con la imagen
    alto_deseado = int((alto_encabezado / ancho_encabezado) 
                       * ancho_canvas)
    encabezado = encabezado.resize((ancho_canvas, alto_deseado))
    ancho_encabezado, alto_encabezado = encabezado.size

    # Aumentar el encabezado a la imagen de los mapas
    resultado = Image.new('RGB', 
                          (ancho_canvas, 
                          alto_canvas + alto_encabezado))
    resultado.paste(encabezado, (0, 0))
    resultado.paste(nuevo_canvas, (0, alto_encabezado))

    # Guardar la imagen resultante
    resultado.save('fondo_presentador.jpg')

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

        user = config['d-id1']['user']
        password = config['d-id1']['password']

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

def elegir_presentador():
    voces = ["es-CL-CatalinaNeural", "es-GT-AndresNeural",
             "es-BO-MarceloNeural", "es-CR-MariaNeural",
             "es-BO-SofiaNeural", "es-CL-LorenzoNeural"]
    presentadores = [(presentador, voz) for (presentador, voz) in zip(os.listdir('presentadores'), voces)]
    return random.choice(presentadores)

def main():
    if len(sys.argv) != 5: 
        sys.exit('Uso: python video_talks.py "Imagen_tabla_probs" "api_video.ini" "CSV_tabla_probs" "Imagen ecuador"')

    generarfondo(sys.argv[3], sys.argv[1], sys.argv[4]) #Tabla_probs_csv, Tabla_probs_imagen, Imagen_ecuador
    
    imagen_presentador, voz = elegir_presentador()

    credenciales = sys.argv[2]
    tabla = sys.argv[3]
    
    generar_imagen('fondo_presentador.jpg', 'presentadores/' + imagen_presentador, 'nueva_imagen.jpg')
    texto = leertabla(tabla)
    header, headers = acceder_api(credenciales)
    url_imagen_final, id_imagen = obtener_url_imagen('nueva_imagen.jpg', headers)
    video_path = generar_video(url_imagen_final, texto, header, voz)
    print(video_path)
    borrar_imagen(id_imagen, headers)

if __name__ == "__main__":
    main()