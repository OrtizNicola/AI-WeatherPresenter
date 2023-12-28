from PIL import Image, ImageDraw

# Ruta de tu imagen
mapa = 'mapa.png'
lluvia = 'lluvia.png'

# Cargar la imagen
mapa = Image.open(mapa)
lluvia = Image.open(lluvia)

ancho_lluvia, alto_lluvia = lluvia.size

coordenadas_recorte = (20, 48, ancho_lluvia - 10, alto_lluvia - 122)  

lluvia = lluvia.crop(coordenadas_recorte)

ancho_lluvia, alto_lluvia = lluvia.size


largo_deseado = alto_lluvia  # Reemplaza con el largo deseado

# Calcular el ancho correspondiente manteniendo la proporción de la imagen original
ancho_original, alto_original = mapa.size
ancho_deseado = int((ancho_original / alto_original) * largo_deseado)

# Redimensionar la imagen manteniendo la proporción de aspecto
mapa = mapa.resize((ancho_deseado, largo_deseado))

nueva_imagen = Image.new('RGB', (ancho_deseado + ancho_lluvia, largo_deseado))

# Pegar las imágenes una al lado de la otra
nueva_imagen.paste(mapa, (0, 0))
nueva_imagen.paste(lluvia, (ancho_deseado, 0))

dibujante = ImageDraw.Draw(nueva_imagen)

# Definir las coordenadas para la línea (x0, y0, x1, y1)
coordenadas_linea1 = (ancho_deseado, 5, 610 + 2, 150 + 2)
coordenadas_linea2 = (ancho_deseado, largo_deseado - 5, 610 + 2, 235 - 2)

color_borde = (255, 0, 0)  # Por ejemplo, rojo en este caso

# Coordenadas de los vértices del rectángulo
vertices = [(610, 150), (710, 150), (710, 235), (610, 235), (610, 160)]

# Dibujar el borde del rectángulo utilizando las coordenadas de los vértices
dibujante.polygon(vertices, outline='black', width=5)


# Dibujar una línea en la imagen
dibujante.line(coordenadas_linea1, fill='black', width=5) 
dibujante.line(coordenadas_linea2, fill='black', width=5) 


# Guardar la imagen resultante
#       lluvia.save('imagen_resultante.png')
nueva_imagen.show()
