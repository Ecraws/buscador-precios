import streamlit as st
import pandas as pd
import requests
import io

# ==========================================
# CONFIGURACIÓN DEL REPOSITORIO DE GITHUB
# ==========================================
USUARIO_GITHUB = "Ecraws"
REPO_GITHUB = "buscador-precios"
GITHUB_TOKEN = None  # Poné tu token si tu repositorio es privado (ej: "ghp_xxxx...")

# Configuración de página de Streamlit
st.set_page_config(
    page_title="Buscador de Precios y Ofertas",
    page_icon="🛒",
    layout="centered"
)


# ==========================================
# FUNCIONES DE CARGA Y PROCESAMIENTO
# ==========================================

def obtener_ultimo_archivo_github(repo_owner, repo_name, folder_path, github_token=None):
    """
    Obtiene los bytes del archivo Excel o CSV más reciente subido a una carpeta de GitHub.
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_path}"
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
        
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None, None
            
        files = response.json()
        if not isinstance(files, list):
            return None, None

        # Filtrar solo archivos válidos (Excel y CSV)
        valid_files = [f for f in files if f.get('name', '').lower().endswith(('.xlsx', '.xls', '.csv'))]
        
        if not valid_files:
            return None, None
            
        # Ordenar para tomar el último subido
        ultimo_archivo = sorted(valid_files, key=lambda x: x['name'])[-1]
        
        # Descargar el contenido
        download_url = ultimo_archivo['download_url']
        file_res = requests.get(download_url)
        if file_res.status_code == 200:
            return io.BytesIO(file_res.content), ultimo_archivo['name']
        return None, None

    except Exception:
        return None, None


def procesar_archivo_inteligente(file_buffer, nombre_archivo):
    """
    Lee Excel o CSV detectando la fila de encabezados ('Codigo Interno')
    sin requerir modificaciones previas en la planilla.
    """
    if file_buffer is None:
        return None

    try:
        es_csv = nombre_archivo.lower().endswith('.csv')
        
        # 1. Intentar lectura normal
        if es_csv:
            df = pd.read_csv(file_buffer, encoding='utf-8', on_bad_lines='skip')
        else:
            df = pd.read_excel(file_buffer)
        
        # 2. Si 'Codigo Interno' no está en el encabezado, buscar salteando filas
        cols_limpias = [str(c).strip() for c in df.columns]
        if 'Codigo Interno' not in cols_limpias:
            for skip in range(1, 10):
                file_buffer.seek(0)
                if es_csv:
                    df_temp = pd.read_csv(file_buffer, skiprows=skip, encoding='utf-8', on_bad_lines='skip')
                else:
                    df_temp = pd.read_excel(file_buffer, skiprows=skip)
                    
                df_temp.columns = [str(c).strip() for c in df_temp.columns]
                
                if 'Codigo Interno' in df_temp.columns:
                    df = df_temp
                    break

        # Limpiar nombres de columnas
        df.columns = [str(c).strip() for c in df.columns]

        # Limpiar y formatear filas
        if 'Codigo Interno' in df.columns:
            df = df.dropna(subset=['Codigo Interno'])
            df['Codigo Interno'] = df['Codigo Interno'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

        if 'codigoscanner' in df.columns:
            df['codigoscanner'] = df['codigoscanner'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df['codigoscanner'] = df['codigoscanner'].replace('0', '')

        if 'Descripcion' in df.columns:
            df['Descripcion'] = df['Descripcion'].astype(str).str.strip()

        if 'Precio' in df.columns:
            df['Precio'] = pd.to_numeric(df['Precio'], errors='coerce').fillna(0)

        if 'Descrip Sector' in df.columns:
            df['Descrip Sector'] = df['Descrip Sector'].astype(str).str.strip()

        return df

    except Exception as e:
        st.error(f"Error al procesar `{nombre_archivo}`: {e}")
        return None


# ==========================================
# CARGA CON CACHÉ (PRECIOS Y OFERTAS)
# ==========================================

@st.cache_data(ttl=300)
def cargar_datos_carpeta(carpeta):
    buffer, nombre_archivo = obtener_ultimo_archivo_github(USUARIO_GITHUB, REPO_GITHUB, carpeta, GITHUB_TOKEN)
    if buffer and nombre_archivo:
        df = procesar_archivo_inteligente(buffer, nombre_archivo)
        return df, nombre_archivo
    return None, None


# ==========================================
# INTERFAZ PRINCIPAL CON PESTAÑAS
# ==========================================

st.title("📱 Consultador de Productos")

tab1, tab2 = st.tabs(["🏷️ Padrón General", "🔥 Ofertas"])

# --- PESTAÑA 1: PADRÓN GENERAL ---
with tab1:
    df_precios, archivo_p = cargar_datos_carpeta("precios")
    
    if df_precios is not None:
        st.caption(f"📁 Archivo activo: `{archivo_p}` ({len(df_precios)} productos)")
        
        busqueda = st.text_input("Buscar por Cód. Interno, Barras o Descripción:", key="busq_general").strip()
        
        if busqueda:
            b_lower = busqueda.lower()
            cond_cod = df_precios['Codigo Interno'].str.lower() == b_lower
            cond_scan = df_precios['codigoscanner'].str.lower() == b_lower if 'codigoscanner' in df_precios.columns else False
            cond_desc = df_precios['Descripcion'].str.lower().str.contains(b_lower, regex=False) if 'Descripcion' in df_precios.columns else False
            
            res = df_precios[cond_cod | cond_scan | cond_desc]
            
            if not res.empty:
                st.success(f"Resultados encontrados: {len(res)}")
                for _, row in res.iterrows():
                    st.markdown("---")
                    st.subheader(f"📦 {row.get('Descripcion', '-')}")
                    c1, c2 = st.columns(2)
                    c1.markdown(f"**Precio:** 💵 `${row.get('Precio', 0):,.2f}`")
                    c1.markdown(f"**Cód. Interno:** `{row.get('Codigo Interno', '-')}`")
                    c2.markdown(f"**Sector:** {row.get('Descrip Sector', '-')}")
                    c2.markdown(f"**Cód. Barras:** `{row.get('codigoscanner', '-')}`")
            else:
                st.warning("No se encontraron coincidencias.")
    else:
        st.info("No se encontró ningún archivo válido en la carpeta `precios/` de GitHub.")


# --- PESTAÑA 2: OFERTAS ---
with tab2:
    df_ofertas, archivo_o = cargar_datos_carpeta("ofertas")
    
    if df_ofertas is not None:
        st.caption(f"🔥 Archivo activo: `{archivo_o}` ({len(df_ofertas)} ofertas)")
        
        busqueda_of = st.text_input("Buscar en ofertas:", key="busq_ofertas").strip()
        
        if busqueda_of:
            b_lower = busqueda_of.lower()
            cond_cod = df_ofertas['Codigo Interno'].str.lower() == b_lower
            cond_scan = df_ofertas['codigoscanner'].str.lower() == b_lower if 'codigoscanner' in df_ofertas.columns else False
            cond_desc = df_ofertas['Descripcion'].str.lower().str.contains(b_lower, regex=False) if 'Descripcion' in df_ofertas.columns else False
            
            res_of = df_ofertas[cond_cod | cond_scan | cond_desc]
            
            if not res_of.empty:
                st.success(f"Ofertas encontradas: {len(res_of)}")
                for _, row in res_of.iterrows():
                    st.markdown("---")
                    st.subheader(f"🏷️ {row.get('Descripcion', '-')}")
                    c1, c2 = st.columns(2)
                    c1.markdown(f"**Precio Oferta:** 💥 `${row.get('Precio', 0):,.2f}`")
                    c1.markdown(f"**Cód. Interno:** `{row.get('Codigo Interno', '-')}`")
                    c2.markdown(f"**Sector:** {row.get('Descrip Sector', '-')}")
                    c2.markdown(f"**Cód. Barras:** `{row.get('codigoscanner', '-')}`")
            else:
                st.warning("No se encontraron ofertas con esa búsqueda.")
        else:
            # Mostrar lista completa de ofertas si no busca nada
            st.markdown("### Lista completa de ofertas disponibles:")
            st.dataframe(df_ofertas[['Codigo Interno', 'Descripcion', 'Precio']], use_container_width=True)
    else:
        st.info("No se encontró ningún archivo en la carpeta `ofertas/` de GitHub.")
        
