import streamlit as st
import pandas as pd

# Configuración de la página para celulares
st.set_page_config(page_title="Buscador de Precios", layout="centered")

st.title("📱 Buscador de Productos")

# Función para cargar los datos del Excel
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("productos.xlsx")
        
        # Convertimos a texto para evitar errores en las búsquedas
        df['desc_busqueda'] = df['Descripcion'].astype(str).str.lower()
        df['scan_busqueda'] = df['codigoscanner'].astype(str).str.strip()
        
        return df
    except Exception as e:
        st.error("No se pudo cargar el archivo 'productos.xlsx'. Asegúrate de que los nombres de las columnas en la primera fila coincidan exactamente.")
        return None

df = cargar_datos()

if df is not None:
    # Barra de búsqueda única (sirve para la descripción o el código de barras)
    busqueda = st.text_input("🔍 Buscar por Descripción o Código Scanner:", "").strip().lower()

    if busqueda:
        # Filtra si coincide con la descripción o con el código de barras
        resultados = df[
            df['desc_busqueda'].str.contains(busqueda, na=False) | 
            df['scan_busqueda'].str.contains(busqueda, na=False)
        ]
        
        if not resultados.empty:
            st.success(f"Se encontraron {len(resultados)} productos:")
            
            # Mostramos los resultados adaptados a la pantalla del celular
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
                            # Pequeño truco para que los códigos numéricos enteros no se muestren con decimales (.0)
                            cod_int = fila['Codigo Interno']
                            st.markdown(f"🔢 **Cód. Interno:** {int(cod_int) if isinstance(cod_int, float) and cod_int.is_integer() else cod_int}")
                        if pd.notna(fila['Descrip Sector']):
                            st.markdown(f"📁 **Sector:** {fila['Descrip Sector']}")
                    with col2:
                        if pd.notna(fila['codigoscanner']):
                            # Evita que códigos de barra largos se muestren en formato científico (ej: 7.79e+12) o con decimales
                            scanner_texto = str(fila['codigoscanner']).split('.')[0] if '.' in str(fila['codigoscanner']) else str(fila['codigoscanner'])
                            st.markdown(f"🏷️ **Scanner:** {scanner_texto}")
                            
                    st.write("---")
        else:
            st.warning("No se encontraron productos con esa descripción o código.")
