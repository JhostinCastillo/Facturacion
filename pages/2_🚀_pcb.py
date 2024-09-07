import streamlit as st
from streamlit_lottie import st_lottie
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Table, TableStyle, Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors
from PIL import Image as PILImage
import os
import io 

st.set_page_config(page_title="PCBs", page_icon="🚀")

def cargar_configuracion():
    with open("config/configpcb.json", "r") as file:
        return json.load(file)

def guardar_configuracion(config):
    with open("config/configpcb.json", "w") as file:
        json.dump(config, file, indent=4)

def calcular_precios(tipopcb,hoyos,x,y,tiempo,config):
    
    coste_mm2 = (x*y) * config["slice"][tipopcb]["mm2"]
    coste_hoyos = hoyos * config["hoyos"]
    coste_tiempo = tiempo * config["slice"][tipopcb]["tiempo"]

    consumible = [config["slice"][tipopcb]["multiplicador_consumible"] * i for i in range(10,110,10)]

    if x < 10:
        coste_consumible = consumible[0]
    elif x < 20:
        coste_consumible = consumible[1]
    elif x < 30:
        coste_consumible = consumible[2]
    elif x < 40:
        coste_consumible = consumible[3]
    elif x < 50:
        coste_consumible = consumible[4]
    elif x < 60:
        coste_consumible = consumible[5]
    elif x < 70:
        coste_consumible = consumible[6]
    elif x < 80:
        coste_consumible = consumible[7]
    elif x < 90:
        coste_consumible = consumible[8]
    elif x < 100:
        coste_consumible = consumible[9]
    else:
        coste_consumible = consumible[9] + (5 * config["slice"][tipopcb]["multiplicador_consumible"])
    
    coste_obra = (coste_hoyos + coste_tiempo + coste_mm2) * config["slice"][slice]["obra"]
    coste_error = (coste_consumible + coste_hoyos + coste_mm2) * config["error"]

    subtotal = coste_consumible + coste_error + coste_hoyos + coste_mm2 + coste_tiempo + coste_obra

    coste_maquina = subtotal * config["maquina"]
    subtotal = subtotal + (coste_maquina)

    return {
        "coste_mm2": config["slice"][tipopcb]["mm2"],
        "total_mm2": coste_mm2,
        "coste_hoyo": config["hoyos"],
        "total_hoyos": coste_hoyos,
        "coste_tiempo": config["slice"][tipopcb]["tiempo"],
        "total_tiempo": coste_tiempo,
        "total_consumible": coste_consumible,
        "total_obra": coste_obra,
        "margen_error": coste_error,
        "coste_maquina": coste_maquina,
        "subtotal": subtotal
    }

config = cargar_configuracion()

st.sidebar.header("Configuraciones PCB")
for slice in config['slice']:
    st.sidebar.write(f"### {slice}")
    config['slice'][slice]['mm2'] = st.sidebar.number_input(f"Precio de mm2 para slice{slice} (DOP)", value=config['slice'][slice]['mm2'])
    config['slice'][slice]['obra'] = st.sidebar.number_input(f"Porcentaje de obra para slice{slice} (DOP)", value=config['slice'][slice]['obra'])
    config['slice'][slice]['tiempo'] = st.sidebar.number_input(f"Precio de tiempo para slice{slice} (DOP)", value=config['slice'][slice]['tiempo'])
    config['slice'][slice]['multiplicador_consumible'] = st.sidebar.number_input(f"Multipplicador de consumible cada 10mm para slice{slice} (DOP)", value=config['slice'][slice]['multiplicador_consumible'])
   
st.sidebar.write("### Porcentaje de máquina")
config['maquina'] = st.sidebar.number_input("Porcentaje de máquina", value= config['maquina'])

st.sidebar.write("### Coste de agujero")
config['hoyos'] = st.sidebar.number_input("Coste de agujero", value= config['hoyos'])

st.sidebar.write("### Coste de consumible")
config['consumible'] = st.sidebar.number_input(f"Coste de consumible = {config['consumible']} x multiplicador de consumible", value= config['consumible'])
                                        
st.sidebar.write("### Porcentaje de error")
config['error'] = st.sidebar.number_input("Porcentaje de error", value= config['error'])                                        

st.sidebar.write(f"### Ruta para guardar facturas")
config["path"] = st.sidebar.text_input("Ruta para guardar factura", value= config["path"])

st.sidebar.write(f"### Publicidad")
config["Texto de publicidad"] = st.sidebar.text_input("Marketing nivel Dios", value= config["Texto de publicidad"])
im_publicidad = st.sidebar.file_uploader("Subir una imagen diferente para la publicidad, por defecto se pondrán las PCBs de siempre", type=["png", "jpg"], key="publicidad")
config["TamanioTXTPublicidad"] = st.sidebar.number_input("Tamaño del texto", value= config["TamanioTXTPublicidad"])
config["Tamanio"] = st.sidebar.number_input("Tamaño de la imagen", value= config["Tamanio"])

if st.sidebar.button("Guardar configuraciones"):
    guardar_configuracion(config)
    st.sidebar.success("Configuraciones guardadas correctamente")

st.image("imagenes/logopng.png",width=200,)

st.header("Facturar PCBs")
nombre = st.text_input("Nombre del Cliente")
apellido = st.text_input("Apellido")
contacto = st.text_input("Contacto")
fecha = st.date_input("Fecha")
numero_pedido = st.text_input("Número de Pedido")
numero_pcbs = st.number_input("Número de PCBs", min_value=1, step=1)

if 'articulos' not in st.session_state:
    st.session_state['articulos'] = []

with st.form(key='form_articulo'):
    tipo_slice = st.selectbox("Tipo de Slice", ["1", "2"], key="slice")
    hoyos = st.number_input("Agujeros", min_value=0, key="hoyos")
    tiempo = st.number_input("Tiempo de fabricación (horas)", min_value=0.0, value= 1.0,key="tiempo")
    x = st.number_input("Tamaño de x (mm)", min_value=0.0, key="x")
    y = st.number_input("Tamaño de y (mm)", min_value=0.0, key="y")
    imagen_pcb = st.file_uploader("Subir Imagen de la PCB (PNG/JPG)", type=["png", "jpg"], key="pcb")

    submit_button = st.form_submit_button(label="Guardar Artículo")

    if submit_button:
        precios = calcular_precios(tipo_slice,hoyos,x,y,tiempo,config)
        articulo = {
            "slice": tipo_slice,
            "hoyos": hoyos,
            "tiempo": tiempo,
            "x": x,
            "y": y,
            "imagen_pcb": imagen_pcb,
            **precios
        }
        st.session_state['articulos'].append(articulo)
        st.success("Artículo añadido correctamente")

st.header("Factura")
st.write(f"**Nombre del Cliente:** {nombre}")
st.write(f"**Apellido:** {apellido}")
st.write(f"**Contacto:** {contacto}")
st.write(f"**Fecha:** {fecha}")
st.write(f"**Número de Pedido:** {numero_pedido}")
st.write(f"**Número de PCBs:** {numero_pcbs}")

for i, articulo in enumerate(st.session_state['articulos']):
    st.subheader(f"Artículo {i + 1}")
    st.write(f"Tipo de PCB: {articulo['slice']}")
    st.write(f"Agujeros: {articulo['hoyos']}")
    st.write(f"Tiempo de fabricación: {articulo['tiempo']}h")
    st.write(f"Tamaño en X: {articulo['x']}")
    st.write(f"Tamaño en Y: {articulo['y']}")
    st.write(f"Coste en mm2: {articulo['total_mm2']} DOP")
    st.write(f"Coste en agujero: {articulo['total_hoyos']} DOP")
    st.write(f"Coste en tiempo: {articulo['total_tiempo']} DOP")
    st.write(f"Coste en consumibles: {articulo['total_consumible']} DOP")
    st.write(f"Coste en obra: {articulo['total_obra']} DOP")
    st.write(f"Coste Máquina: {articulo['coste_maquina']} DOP")
    st.write(f"Margen de error: {articulo['margen_error']} DOP")
    st.write(f"Subtotal: {articulo['subtotal']} DOP")

    if articulo['imagen_pcb']:
        st.image(articulo['imagen_pcb'], caption='Imagen de la PCB')

total = sum([item["subtotal"] for item in st.session_state['articulos']])
st.write(f"**Total a pagar: {total} DOP**")


def ajustar_imagen(imagen_path, max_width, max_height):
    with PILImage.open(imagen_path) as img:
        width, height = img.size
        aspect_ratio = width / height
        
        if width > max_width or height > max_height:
            if aspect_ratio > 1:
                new_width = min(max_width, width)
                new_height = new_width / aspect_ratio
            else:
                new_height = min(max_height, height)
                new_width = new_height * aspect_ratio
        else:
            new_width, new_height = width, height
        
        return new_width, new_height

def generar_pdf(nombre_archivo, cliente, pedido, articulos, imagenes_pcb):
    
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    fsize = int(config["TamanioTXTPublicidad"])
    times_new_roman = ParagraphStyle(
        name='TimesNewRoman',
        fontName='Times-Roman',
        fontSize=24,
        leading=30,
        alignment=1,  
        parent=styles['Normal']
    )

    times_new_roman_italic = ParagraphStyle(
        name='Times-Italic',
        fontName='Times-Italic',
        fontSize= fsize,
        leading=30,
        alignment=1,  
        textColor=colors.HexColor("#72B22D"), 
        parent=styles['Normal']
    )

    style_left = ParagraphStyle(
        name='LeftAligned',
        fontName='Times-Roman',
        fontSize=24,
        leading=30,
        alignment=0,  
        parent=styles['Normal']
    )

    content = []

    logo_path = "imagenes/logo.png"
    if os.path.exists(logo_path):
        logo_width, logo_height = ajustar_imagen(logo_path, 3*inch, 3*inch)
        logo = Image(logo_path, width=logo_width, height=logo_height)
        content.append(logo)

    gracias_path = "imagenes/gracias.png"
    if os.path.exists(gracias_path):
        gracias_width, gracias_height = ajustar_imagen(gracias_path, 3*inch, 3*inch)
        gracias = Image(gracias_path, width=gracias_width, height=gracias_height)
        content.append(gracias)
    
    separador1_path = "imagenes/separador1.png"
    if os.path.exists(separador1_path):
        separador1_width, separador1_height = ajustar_imagen(separador1_path, 10*inch, 10*inch)
        separador1 = Image(separador1_path, width=separador1_width, height=separador1_height)
        content.append(separador1)

    content.append(Paragraph("<b>GabyTronicX</b>", times_new_roman))
    content.append(Paragraph("IG: @gabytronicx WS: 809-884-9764", times_new_roman))
    content.append(Paragraph("<b>PCBs</b>", times_new_roman))

    separador1_path = "imagenes/separador2.png"
    if os.path.exists(separador1_path):
        separador1_width, separador1_height = ajustar_imagen(separador1_path, 10*inch, 10*inch)
        separador1 = Image(separador1_path, width=separador1_width, height=separador1_height)
        content.append(separador1)
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"Nombre: {cliente['nombre']}", style_left))
    content.append(Paragraph(f"Apellido: {cliente['apellido']}", style_left))
    content.append(Paragraph(f"Contacto: {cliente['contacto']}", style_left))
    content.append(Paragraph(f"Fecha: {cliente['fecha']}", style_left))
    content.append(Paragraph(f"Número de Pedido: {cliente['numero_pedido']}", style_left))
    content.append(Paragraph(f"Número de Modelados: {cliente['numero_pcbs']}", style_left))
    content.append(Paragraph(f"<b>Total: {round(total,2)} DOP</b>", style_left))
    content.append(Spacer(1, 12))

    separador1_path = "imagenes/separador3.png"
    if os.path.exists(separador1_path):
        separador1_width, separador1_height = ajustar_imagen(separador1_path, 10*inch, 10*inch)
        separador1 = Image(separador1_path, width=separador1_width, height=separador1_height)
        content.append(separador1)
    content.append(Spacer(1, 12))

    content.append(Paragraph("<b>Datos del Pedido</b>", style_left))
    content.append(Spacer(1, 12))

    for i, articulo in enumerate(articulos):
        if articulo['slice'] == "1":
            tipo = "Simple"
        else:
            tipo = "Doble cara"

    for i, articulo in enumerate(articulos):
        content.append(Paragraph(f"<b>Artículo {i + 1}:</b>", style_left))
        content.append(Paragraph(f"<b>Tipo de PCB:</b> {tipo}", style_left))
        content.append(Paragraph(f"<b>Agujeros:</b> {articulo['hoyos']}", style_left))
        content.append(Paragraph(f"<b>Tiempo de fabricación:</b> {articulo['tiempo']}h", style_left))
        content.append(Paragraph(f"<b>Tamaño en X:</b> {articulo['x']}", style_left))
        content.append(Paragraph(f"<b>Tamaño en Y:</b> {articulo['y']}", style_left))
        content.append(Paragraph(f"<b>Coste en mm2:</b> {articulo['total_mm2']} DOP", style_left))
        content.append(Paragraph(f"<b>Coste en agujero:</b> {articulo['total_hoyos']} DOP", style_left))
        content.append(Paragraph(f"<b>Coste en tiempo:</b> {articulo['total_tiempo']} DOP", style_left))
        content.append(Paragraph(f"<b>Coste en consumibles:</b> {articulo['total_consumible']} DOP", style_left))
        content.append(Paragraph(f"<b>Coste en obra:</b> {articulo['total_obra']} DOP", style_left))
        content.append(Paragraph(f"<b>Coste Máquina:</b> {articulo['coste_maquina']} DOP", style_left))
        content.append(Paragraph(f"<b>Margen de error:</b> {articulo['margen_error']} DOP", style_left))
        content.append(Paragraph(f"<b>Subtotal: {round(articulo['subtotal'],2)} DOP</b>", style_left))
        content.append(Spacer(1, 12))

        if articulo['imagen_pcb']:
            content.append(Paragraph("<b>PCB</b>", times_new_roman))
            separador1_path = articulo['imagen_pcb']

            separador1_width, separador1_height = ajustar_imagen(separador1_path, 10*inch, 10*inch)
            separador1 = Image(separador1_path, width=separador1_width, height=separador1_height)
            content.append(separador1)

    content.append(Paragraph(f"<b>Total: {round(total,2)} DOP</b>", style_left))

    separador1_path = "imagenes/separador4.png"
    if os.path.exists(separador1_path):
        separador1_width, separador1_height = ajustar_imagen(separador1_path, 10*inch, 10*inch)
        separador1 = Image(separador1_path, width=separador1_width, height=separador1_height)
        content.append(separador1)
    content.append(Spacer(1, 12))

    txt_publicidad = config["Texto de publicidad"]
    content.append(Paragraph(f"<b>{txt_publicidad}</b>", times_new_roman_italic))
 
    if im_publicidad:
        separador1_width, separador1_height = ajustar_imagen(im_publicidad, config["Tamanio"]*inch, config["Tamanio"]*inch)
        separador1 = Image(im_publicidad, width=separador1_width, height=separador1_height)
        content.append(separador1)
    else:
        pcb_images = []
        for img_pcb in imagenes_pcb:
            img_pcb_width, img_pcb_height = ajustar_imagen(img_pcb, 8*inch, 8*inch)
            img_pcb_image = Image(img_pcb, width=img_pcb_width, height=img_pcb_height)
            pcb_images.append(img_pcb_image)
        
        num_images_per_row = 2
        rows = [pcb_images[i:i+num_images_per_row] for i in range(0, len(pcb_images), num_images_per_row)]
        pcb_table = Table(rows)
        pcb_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
        content.append(pcb_table)

    exito = False
    try:
        doc.build(content)
        exito = True
    except PermissionError:
        st.error("Ya existe una factura con ese número de pedido :(")
    except Exception as e:
        st.error(f"Se produjo un error inesperado: {e}")

    if exito:
        buffer.seek(0)

        st.download_button(
            label="Descargar PDF",
            data=buffer,
            file_name=nombre_archivo, 
            mime="application/pdf"
        )

        st.success("PDF generado correctamente :)") 

def main():

    if st.button("Generar PDF"):
        nombre_archivo = f"GabyTronicX Factura {numero_pedido}.pdf"
        cliente = {
            "nombre": nombre,
            "apellido": apellido,
            "contacto": contacto,
            "fecha": fecha,
            "numero_pedido": numero_pedido,
            "numero_pcbs": numero_pcbs
        }

        imagenes_pcb = [
            config["Ruta de imagen de publicidad"]
        ]

        generar_pdf(nombre_archivo, cliente, numero_pedido, st.session_state['articulos'], imagenes_pcb)
    
    def load_lottie_file(filepath: str):
        with open(filepath, "r") as f:
            return json.load(f)
        
    st.markdown("""
        <style>
        .spacer {
            height: 500px;  /* Ajusta la altura del espacio */
        }
        </style>
        <div class="spacer"></div>
        """, unsafe_allow_html=True)

    lottie_file_path = "lottie/lottierocket.json"  
    lottie_data = load_lottie_file(lottie_file_path)

    st_lottie(lottie_data, speed=1, width=600, height=400, key="lottie_animation")
    st.write("Hasta el infinito y más allá")
if __name__ == "__main__":
    main()