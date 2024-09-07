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

st.set_page_config(page_title="Impresiones 3D", page_icon="⭐")

def cargar_configuracion():
    with open("config/config.json", "r") as file:
        return json.load(file)

def guardar_configuracion(config):
    with open("config/config.json", "w") as file:
        json.dump(config, file, indent=4)

def calcular_precios(tipo_material, peso, tiempo, coste_diseno, config):
    if peso <= 20:
        coste_material = config['materiales'][tipo_material]['0-20g']
    elif peso <= 200:
        coste_material = config['materiales'][tipo_material]['21-200g']
    elif peso <= 400:
        coste_material = config['materiales'][tipo_material]['201-400g']
    else:
        coste_material = config['materiales'][tipo_material]['401-1000g']

    total_material = coste_material * peso


    if tiempo <= 10:
        coste_tiempo = config['tiempo']['0-10h']
    elif tiempo <= 20:
        coste_tiempo = config['tiempo']['11-20h']
    elif tiempo <= 30:
        coste_tiempo = config['tiempo']['21-30h']
    elif tiempo > 30:
        coste_tiempo = config['tiempo']['mas de 31h']

    total_tiempo = coste_tiempo * tiempo

    if peso <= 20:
        mano_obra = total_material * config['mano_de_obra']['0-20g']
    elif peso <= 200:
        mano_obra = total_material * config['mano_de_obra']['21-200g']
    elif peso <= 400:
        mano_obra = total_material * config['mano_de_obra']['201-400g']
    else:
        mano_obra = total_material * config['mano_de_obra']['401-1000g']

    if peso <= 20:
        margen_error = total_material * config['margen_perdida']['0-20g']
    elif peso <= 200:
        margen_error = total_material * config['margen_perdida']['21-200g']
    elif peso <= 400:
        margen_error = total_material * config['margen_perdida']['201-400g']
    else:
        margen_error = total_material * config['margen_perdida']['401-1000g']

    coste_maquina = (total_material + total_tiempo) * config['coste_maquina']

    subtotal = total_material + total_tiempo + mano_obra + coste_diseno + margen_error + coste_maquina

    return {
        "coste_material": coste_material,
        "total_material": total_material,
        "coste_tiempo": coste_tiempo,
        "total_tiempo": total_tiempo,
        "mano_obra": mano_obra,
        "margen_error": margen_error,
        "coste_maquina": coste_maquina,
        "subtotal": subtotal
    }

config = cargar_configuracion()

st.sidebar.header("Configuraciones impresiones3D")
for material in config['materiales']:
    st.sidebar.write(f"### {material}")
    config['materiales'][material]['0-20g'] = st.sidebar.number_input(f"Precio por gramo (0-20g) para {material} (DOP)", value=config['materiales'][material]['0-20g'])
    config['materiales'][material]['21-200g'] = st.sidebar.number_input(f"Precio por gramo (21-200g) para {material} (DOP)", value=config['materiales'][material]['21-200g'])
    config['materiales'][material]['201-400g'] = st.sidebar.number_input(f"Precio por gramo (201-400g) para {material} (DOP)", value=config['materiales'][material]['201-400g'])
    config['materiales'][material]['401-1000g'] = st.sidebar.number_input(f"Precio por gramo (401-1000g) para {material} (DOP)", value=config['materiales'][material]['401-1000g'])

for idx, (rango, precio) in enumerate(config['tiempo'].items()):
    st.sidebar.write(f"### Tiempo de impresión ({rango})")
    config['tiempo'][rango] = st.sidebar.number_input(f"Precio por hora ({rango}) (DOP)", value=precio)

for idx, (rango, porcentaje) in enumerate(config['mano_de_obra'].items()):
    st.sidebar.write(f"### Mano de Obra ({rango})")
    config['mano_de_obra'][rango] = st.sidebar.number_input(f"Porcentaje de Mano de Obra ({rango})", value=porcentaje)

for idx, (rango, porcentaje) in enumerate(config['margen_perdida'].items()):
    st.sidebar.write(f"### Margen de Pérdida ({rango})")
    config['margen_perdida'][rango] = st.sidebar.number_input(f"Porcentaje de Margen de Pérdida ({rango})", value=porcentaje)

st.sidebar.write(f"### Ruta para guardar facturas")
config["path"] = st.sidebar.text_input("Ruta para guardar factura", value= config["path"])

st.sidebar.write(f"### Publicidad")
config["Texto de publicidad"] = st.sidebar.text_input("Marketing nivel Dios", value= config["Texto de publicidad"])
im_publicidad = st.sidebar.file_uploader("Subir una imagen diferente para la publicidad, por defecto se pondrán las PCBs de siempre", type=["png", "jpg"], key="publicidad")
config["TamanioTXTPublicidad"] = st.sidebar.text_input("Tamaño del texto", value= config["TamanioTXTPublicidad"])
config["Tamanio"] = st.sidebar.text_input("Tamaño de la imagen", value= config["Tamanio"])

if st.sidebar.button("Guardar configuraciones"):
    guardar_configuracion(config)
    st.sidebar.success("Configuraciones guardadas correctamente")

st.image("imagenes/logopng.png",width=200,)

st.header("Facturar impresiones 3D")
nombre = st.text_input("Nombre del Cliente")
apellido = st.text_input("Apellido")
contacto = st.text_input("Contacto")
fecha = st.date_input("Fecha")
numero_pedido = st.text_input("Número de Pedido")
numero_modelados = st.number_input("Número de Modelados", min_value=1, step=1)

if 'articulos' not in st.session_state:
    st.session_state['articulos'] = []

with st.form(key='form_articulo'):
    tipo_material = st.selectbox("Tipo de Material", ["PLA", "PETg", "TPU", "ASA"], key="material")
    peso = st.number_input("Peso (gramos)", min_value=0.0, key="peso")
    tiempo = st.number_input("Tiempo de Impresión (horas)", min_value=0.0, key="tiempo")
    coste_diseno = st.number_input("Coste por Diseño (DOP)", min_value=0.0, key="diseno")
    imagen_modelo = st.file_uploader("Subir Imagen del Modelo (PNG/JPG)", type=["png", "jpg"], key="modelo")
    imagen_impresion = st.file_uploader("Subir Imagen de la Impresión (PNG/JPG)", type=["png", "jpg"], key="impresion")

    submit_button = st.form_submit_button(label="Guardar Artículo")

    if submit_button:
        precios = calcular_precios(tipo_material, peso, tiempo, coste_diseno, config)
        articulo = {
            "tipo_material": tipo_material,
            "peso": peso,
            "tiempo": tiempo,
            "coste_diseno": coste_diseno,
            "imagen_modelo": imagen_modelo,
            "imagen_impresion": imagen_impresion,
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
st.write(f"**Número de Modelados:** {numero_modelados}")

for i, articulo in enumerate(st.session_state['articulos']):
    st.subheader(f"Artículo {i + 1}")
    st.write(f"Tipo de Material: {articulo['tipo_material']}")
    st.write(f"Peso: {articulo['peso']}g")
    st.write(f"Tiempo de Impresión: {articulo['tiempo']}h")
    st.write(f"Coste por Diseño: {articulo['coste_diseno']} DOP")
    st.write(f"Coste Material: {articulo['total_material']} DOP")
    st.write(f"Coste Tiempo: {articulo['total_tiempo']} DOP")
    st.write(f"Coste Mano de Obra: {articulo['mano_obra']} DOP")
    st.write(f"Margen de Error: {articulo['margen_error']} DOP")
    st.write(f"Coste Máquina: {articulo['coste_maquina']} DOP")
    st.write(f"Subtotal: {articulo['subtotal']} DOP")

    if articulo['imagen_modelo']:
        st.image(articulo['imagen_modelo'], caption='Imagen del Modelo STL')
    if articulo['imagen_impresion']:
        st.image(articulo['imagen_impresion'], caption='Imagen de la Impresión')

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
    
    ruta_completa = os.path.join(config['path'], nombre_archivo)

    if not os.path.exists(config['path']):
        try:
            os.makedirs(config['path'])
        except Exception as e:
            st.error("Hay algo mal con esa ruta, revisa bien.")
    
    if os.path.exists(ruta_completa):
        return st.error("Ya existe una factura con ese número de pedido en esa ruta :(")

    doc = SimpleDocTemplate(ruta_completa, pagesize=letter)
    styles = getSampleStyleSheet()
    
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
        fontSize= 24, #int(config["TamanioTXTPublicidad"]),
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
    content.append(Paragraph("<b>Impresión 3D</b>", times_new_roman))

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
    content.append(Paragraph(f"Número de Modelados: {cliente['numero_modelados']}", style_left))
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
        content.append(Paragraph(f"<b>Artículo {i + 1}:</b>", style_left))
        content.append(Paragraph(f"<b>Tipo de Material:</b> {articulo['tipo_material']}", style_left))
        content.append(Paragraph(f"<b>Peso:</b> {articulo['peso']}g", style_left))
        content.append(Paragraph(f"<b>Tiempo de Impresión:</b> {articulo['tiempo']}h", style_left))
        content.append(Paragraph(f"<b>Coste por Diseño:</b> {round(articulo['coste_diseno'],2)} DOP", style_left))
        content.append(Paragraph(f"<b>Coste Material:</b> {round(articulo['total_material'],2)} DOP", style_left))
        content.append(Paragraph(f"<b>Coste Tiempo:</b> {round(articulo['total_tiempo'],2)} DOP", style_left))
        content.append(Paragraph(f"<b>Coste Mano de Obra:</b> {round(articulo['mano_obra'],2)} DOP", style_left))
        content.append(Paragraph(f"<b>Margen de Error:</b> {round(articulo['margen_error'],2)} DOP", style_left))
        content.append(Paragraph(f"<b>Coste Máquina:</b> {round(articulo['coste_maquina'],2)} DOP", style_left))
        content.append(Paragraph(f"<b>Subtotal: {round(articulo['subtotal'],2)} DOP</b>", style_left))
        content.append(Spacer(1, 12))

        if articulo['imagen_modelo']:
            content.append(Paragraph("<b>Modelado STL</b>", times_new_roman))
            separador1_path = articulo['imagen_modelo']

            separador1_width, separador1_height = ajustar_imagen(separador1_path, 10*inch, 10*inch)
            separador1 = Image(separador1_path, width=separador1_width, height=separador1_height)
            content.append(separador1)

        if articulo['imagen_impresion']:
            content.append(Spacer(1, 12))
            content.append(Paragraph("<b>Impresión 3D</b>", times_new_roman))
            separador1_path = articulo['imagen_modelo']

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
        type(config["TamanioTXTPublicidad"])
        doc.build(content)
        exito = True

    except PermissionError:
        st.error("Ya existe una factura con ese número de pedido :(")
    
    # except Exception as e:
    #     st.error(f"Se produjo un error inesperado: {e}")

    if exito:
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
            "numero_modelados": numero_modelados
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

    lottie_file_path = "lottie/lottie.json"  
    lottie_data = load_lottie_file(lottie_file_path)
    st_lottie(lottie_data, speed=1, width=600, height=400, key="lottie_animation")
    st.write("Nada que buscar por acá :)")

if __name__ == "__main__":
    main()