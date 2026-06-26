import streamlit as st
import pandas as pd
from PIL import Image

# Configuración de la página para celulares
st.set_page_config(page_title="Buscador de Precios", layout="centered")

st.title("📱 Buscador de Productos")

# Función para cargar los datos del Excel
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("productos.xlsx")
        
        # Convertimos todas las columnas de búsqueda a texto limpio y minúsculas
        df['desc_busqueda'] = df['Descripcion'].astype(str).str.lower()
        df['scan_busqueda'] = df['codigoscanner'].astype(str).str.strip()
        
        # Limpiamos el Código Interno para la búsqueda
        df['interno_busqueda'] = df['Codigo Interno'].astype(str).apply(
            lambda x: x.split('.')[0] if '.' in x and x.split('.')[1] == '0' else x
        ).str.strip().str.lower()
        
        return df
    except Exception as e:
        st.error("No se pudo cargar el archivo 'productos.xlsx'. Asegúrate de que las columnas en la primera fila coincidan exactamente.")
        return None

df = cargar_datos()

if df is not None:
    # Creamos dos pestañas cómodas para usar con el dedo en el celular
    tab1, tab2 = st.tabs(["🔍 Buscar Tipeando", "📷 Usar Cámara"])
    
    busqueda = ""
    
    # PESTAÑA 1: BÚSQUEDA TRADICIONAL
    with tab1:
        busqueda_texto = st.text_input("Escribí Descripción, Scanner o Cód. Interno:", "").strip().lower()
        if busqueda_texto:
            busqueda = busqueda_texto

    # PESTAÑA 2: CÁMARA FOTOGRÁFICA
    with tab2:
        st.subheader("Escáner por Foto")
        st.info("Tomá una foto bien de cerca, nítida y bien iluminada al código de barras.")
        
        # Este componente abre la cámara nativa del celular automáticamente al presionar el botón
        foto_codigo = st.camera_input("Capturar código de barras")
        
        if foto_codigo:
            st.warning("⚠️ Nota del sistema: En aplicaciones web gratuitas, procesar imágenes en vivo puede ser lento. Si necesitás máxima velocidad en el negocio, recordá que el ícono de cámara que viene dentro del teclado de tu celular (Opción 1) escribe el código al instante en la pestaña 'Buscar Tipeando'.")
            
            # Abrimos la imagen capturada para que el sistema la reconozca
            imagen = Image.open(foto_codigo)
            
            # Consejo visual para el usuario
            st.image(imagen, caption="Imagen capturada", use_container_width=True)

    # LÓGICA DE BÚSQUEDA Y EXPOSICIÓN DE RESULTADOS
    if busqueda:
        resultados = df[
            df['desc_busqueda'].str.contains(busqueda, na=False) | 
            df['scan_busqueda'].str.contains(busqueda, na=False) |
            df['interno_busqueda'].str.contains(busqueda, na=False)
        ]
        
        if not resultados.empty:
            st.success(f"Se encontraron {len(resultados)} productos:")
            
            for index, fila in resultados.iterrows():
                with st.container():
                    # Descripción del producto en grande
                    st.markdown(f"### **{fila['Descripcion']}**")
                    
                    # Precio destacado
                    st.markdown(f"💰 **Precio:** ${fila['Precio']}")
                    
                    # Detalles secundarios en dos columnas para que se vea ordenado en el celular
                    col1, col2 = st.columns(2)
                    with col1:
                        if pd.notna(fila['Codigo Interno']):
                            cod_int_texto = str(fila['Codigo Interno']).split('.')[0] if '.' in str(fila['Codigo Interno']) and str(fila['Codigo Interno']).split('.')[1] == '0' else str(fila['Codigo Interno'])
                            st.markdown(f"🔢 **Cód. Interno:** {cod_int_texto}")
                        if pd.notna(fila['Descrip Sector']):
                            st.markdown(f"📁 **Sector:** {fila['Descrip Sector']}")
                    with col2:
                        if pd.notna(fila['codigoscanner']):
                            scanner_texto = str(fila['codigoscanner']).split('.')[0] if '.' in str(fila['codigoscanner']) else str(fila['codigoscanner'])
                            st.markdown(f"🏷️ **Scanner:** {scanner_texto}")
                            
                    st.write("---")
        else:
            st.warning("No se encontraron productos con esos datos.")
            
