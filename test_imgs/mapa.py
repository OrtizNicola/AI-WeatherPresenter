import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from PIL import Image
import csv

pichincha = gpd.read_file('./Quito/quito_urbano.shp')

marcadores = {
    10: "./iconos_clima/soleado.png",
    20: "./iconos_clima/parcialm_nublado.png",
    30: "./iconos_clima/parcialm_nublado2.png",
    40: "./iconos_clima/nublado.png",
    50: "./iconos_clima/nublado.png",
    60: "./iconos_clima/chubascos.png",
    70: "./iconos_clima/lluvia.png",
    80: "./iconos_clima/lluvia.png",
    90: "./iconos_clima/lluvia_tormenta_electrica.png",
    100: "./iconos_clima/tormenta_electrica.png"
}

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

from matplotlib.offsetbox import OffsetImage, AnnotationBbox

fig, ax = plt.subplots(figsize=(8, 8))

pichincha.plot(ax=ax, alpha=0.3, edgecolor='k', color='grey')

ctx.add_basemap(ax, crs=pichincha.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik, alpha=0.8)

probs = mapear_probs("../PREC_Estaciones_prueba.csv") ####################### remplazar archivo

for (station, latlon) in stations_latlon.items():
    if station in ("ElCamal", "SanAntonio", "Tumbaco"):
        continue
    marcador = marcadores[probs[station]] 
    imagen_marcador = plt.imread(marcador)
    img = OffsetImage(imagen_marcador, zoom=0.18)  
    ab = AnnotationBbox(img, (latlon[1], latlon[0]), xycoords='data', frameon=False, xybox=(0, 9), boxcoords="offset points")  # Ajusta el desplazamiento vertical aquí
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
