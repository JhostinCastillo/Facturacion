import streamlit as st

def facturacion_impresiones_3d():
    st.header("Facturación de Impresiones 3D")
    # Aquí agregas los formularios y cálculos específicos para impresiones 3D
    largo = st.number_input("Largo (cm)", min_value=0.0)
    ancho = st.number_input("Ancho (cm)", min_value=0.0)
    alto = st.number_input("Alto (cm)", min_value=0.0)
    
    if st.button("Calcular Precio Impresión 3D"):
        # Lógica para calcular el precio de las impresiones 3D
        precio = calcular_precio_impresion_3d(largo, ancho, alto)
        st.write(f"Precio total de la impresión 3D: ${precio:.2f}")

def facturacion_pcbs():
    st.header("Facturación de PCBs")
    # Aquí agregas los formularios y cálculos específicos para PCBs
    num_circuitos = st.number_input("Número de circuitos", min_value=1)
    area = st.number_input("Área (cm²)", min_value=0.0)
    
    if st.button("Calcular Precio PCB"):
        # Lógica para calcular el precio de los PCBs
        precio = calcular_precio_pcb(num_circuitos, area)
        st.write(f"Precio total del PCB: ${precio:.2f}")

def calcular_precio_impresion_3d(largo, ancho, alto):
    # Ejemplo de cálculo para impresión 3D
    return largo * ancho * alto * 0.1

def calcular_precio_pcb(num_circuitos, area):
    # Ejemplo de cálculo para PCB
    return num_circuitos * area * 0.05

def main():
    st.title("Aplicación de Facturación")
    
    # Selección de modo de facturación
    modo = st.selectbox("Selecciona el Modo de Facturación", ["Impresiones 3D", "PCBs"])

    if modo == "Impresiones 3D":
        facturacion_impresiones_3d()
    elif modo == "PCBs":
        facturacion_pcbs()

if __name__ == "__main__":
    main()
