import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

pichincha = gpd.read_file('./Quito/quito_urbano.shp')

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

ruta_imagen_marcador = 'marcador.png'

imagen_marcador = plt.imread(ruta_imagen_marcador)

fig, ax = plt.subplots(figsize=(8, 8))

pichincha.plot(ax=ax, alpha=0.3, edgecolor='k', color='grey')

ctx.add_basemap(ax, crs=pichincha.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik, alpha=0.8)

for (station, latlon) in stations_latlon.items():
    img = OffsetImage(imagen_marcador, zoom=0.04)  
    ab = AnnotationBbox(img, (latlon[1], latlon[0]), xycoords='data', frameon=False, xybox=(0, 9), boxcoords="offset points")  # Ajusta el desplazamiento vertical aquí
    ax.add_artist(ab)
    ax.annotate(
        station + " 90%",
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

