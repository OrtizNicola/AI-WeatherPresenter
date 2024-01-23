from PIL import Image, ImageDraw

# Paths de las imágenes
mapa = "mapa.png"
ecuador = "../PrecipitacionAcumulada_fondo.png"
encabezado = "../ImagenFondo.jpg"

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
