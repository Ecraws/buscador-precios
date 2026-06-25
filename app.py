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
        
        # Convertimos todas las columnas de búsqueda a texto limpio y minúsculas
        df['desc_busqueda'] = df['Descripcion'].astype(str).str.lower()
        df['scan_busqueda'] = df['codigoscanner'].astype(str).str.strip()
        
        # Limpiamos el Código Interno para la búsqueda (quitando decimales si se generaron de más)
        df['interno_busqueda'] = df['Codigo Interno'].astype(str).apply(
            lambda x: x.split('.')[0] if '.' in x and x.split('.')[1] == '0' else x
        ).str.strip().str.lower()
        
        return df
    except Exception as e:
        st.error("No se pudo cargar el archivo 'productos.xlsx'. Asegúrate de que los nombres de las columnas en la primera fila coincidan exactamente.")
        return None

df = cargar_datos()

if df is not None:
    # Barra de búsqueda única (sirve para Descripción, Scanner o Código Interno)
    busqueda = st.text_input("🔍 Buscar por Descripción, Scanner o Cód. Interno:", "").strip().lower()

    if busqueda:
        # Filtra si coincide con cualquiera de las 3 columnas
        resultados = df[
            df['desc_busqueda'].str.contains(busqueda, na=False) | 
            df['scan_busqueda'].str.contains(busqueda, na=False) |
            df['interno_busqueda'].str.contains(busqueda, na=False)
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
                            # Muestra el código interno limpio sin decimales molestos (.0)
                            cod_int_texto = str(fila['Codigo Interno']).split('.')[0] if '.' in str(fila['Codigo Interno']) and str(fila['Codigo Interno']).split('.')[1] == '0' else str(fila['Codigo Interno'])
                            st.markdown(f"🔢 **Cód. Interno:** {cod_int_texto}")
                        if pd.notna(fila['Descrip Sector']):
                            st.markdown(f"📁 **Sector:** {fila['Descrip Sector']}")
                    with col2:
                        if pd.notna(fila['codigoscanner']):
                            # Evita que códigos de barra largos se muestren en formato científico o con decimales
                            scanner_texto = str(fila['codigoscanner']).split('.')[0] if '.' in str(fila['codigoscanner']) else str(fila['codigoscanner'])
                            st.markdown(f"🏷️ **Scanner:** {scanner_texto}")
                            
                    st.write("---")
        else:
            st.warning("No se encontraron productos con esos datos.")
