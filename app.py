import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re
import os
import glob

# Configuración de página optimizada para rendimiento y diseño móvil
st.set_page_config(
    page_title="ECRAWS PRICE", 
    page_icon="⚡", 
    layout="centered"
)

# --- INICIALIZACIÓN DE ESTADOS PERSISTENTES ---
if 'historial' not in st.session_state:
    st.session_state.historial = []
if 'busqueda_activa' not in st.session_state:
    st.session_state.busqueda_activa = ""

# --- ARQUITECTURA DE DISEÑO ULTRA-PREMIUM (CSS) ---
st.markdown("""
    <style>
    /* Estilos globales y reseteo */
    .main, .block-container {
        max-width: 100% !important;
        padding: 14px !important;
        overflow-x: hidden !important;
        background-color: #0b0f19 !important; /* Fondo Dark Neo-Premium */
    }
    
    h1, h2, h3, h4, p, label {
        color: #ffffff !important;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    /* --- BARRA DE BÚSQUEDA FLOTANTE (Formulario st.form) --- */
    .stTextInput input {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 14px !important;
        padding: 12px !important;
        font-size: 16px !important;
    }
    .stTextInput input:focus {
        border-color: #00f2fe !important;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.2) !important;
    }

    div[data-testid="stForm"] {
        padding: 16px !important;
        border-radius: 20px !important;
        background: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #2ecc71 0%, #00f2fe 100%) !important;
        color: #0b0f19 !important;
        font-weight: 700 !important;
        border-radius: 14px !important;
        border: none !important;
        padding: 12px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    /* Botones secundarios (como Agregar/Quitar) */
    .btn-secundario button {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 6px 12px !important;
        font-size: 13px !important;
        width: auto !important;
    }
    .btn-secundario button:hover {
        background: rgba(255, 255, 255, 0.15) !important;
    }

    .btn-eliminar button {
        background: rgba(231, 76, 60, 0.2) !important;
        color: #ff4757 !important;
        border: 1px solid rgba(231, 76, 60, 0.3) !important;
        border-radius: 10px !important;
        padding: 6px 12px !important;
        font-size: 13px !important;
        width: 100% !important;
    }
    
    /* --- TARJETAS DE PRODUCTOS --- */
    .producto-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
        padding: 24px;
        border-radius: 24px;
        box-shadow: 0px 15px 35px rgba(0, 0, 0, 0.4);
        margin-top: 16px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        position: relative;
        overflow: hidden;
    }
    
    .producto-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #64748b, #cbd5e1);
    }

    .producto-card.con-oferta::before {
        background: linear-gradient(90deg, #ff4757, #ffa502) !important;
    }
    
    .producto-titulo {
        margin: 0 0 14px 0 !important; 
        color: #ffffff !important; 
        font-size: 22px !important; 
        font-weight: 800 !important;
        line-height: 1.3;
    }
    
    .precio-contenedor {
        background: rgba(255, 255, 255, 0.03);
        padding: 14px 18px;
        border-radius: 16px;
        margin-bottom: 14px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .precio-split-container {
        display: flex;
        gap: 12px;
        margin-bottom: 14px;
        width: 100%;
    }
    
    .split-half {
        flex: 1;
        background: rgba(255, 255, 255, 0.03);
        padding: 12px 14px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        text-align: center;
    }
    
    .split-half.combo-side {
        background: rgba(255, 165, 0, 0.04);
        border: 1px solid rgba(254, 165, 2, 0.2) !important;
    }

    /* --- EL PRECIO ES EL REY --- */
    .precio-enorme {
        color: #ffffff;
        font-size: 46px; 
        font-weight: 900;
        line-height: 1;
        margin: 0;
        letter-spacing: -1px;
    }

    .precio-oferta-color {
        background: linear-gradient(90deg, #ff4757 0%, #ffa502 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .split-label {
        font-size: 11px;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 700;
        margin-bottom: 4px;
        letter-spacing: 0.5px;
    }

    /* --- TAGS DE DATOS FLOTANTES --- */
    .info-oferta-bloque {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 12px;
        border-radius: 14px;
        margin-bottom: 14px;
        font-size: 13px;
    }
    
    .status-tiempo {
        font-size: 11px;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 6px;
        display: inline-block;
    }
    .status-activo { background: rgba(46, 204, 113, 0.15); color: #2ecc71 !important; }
    .status-futuro { background: rgba(255, 165, 0, 0.15); color: #ffa502 !important; }
    .status-ultimo { 
        background: rgba(231, 76, 60, 0.25); 
        color: #ff4757 !important; 
        border: 1px solid rgba(231, 76, 60, 0.5);
        animation: pulse_clean 2s infinite ease-in-out;
    }
    
    @keyframes pulse_clean {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Grid de datos técnicos */
    .meta-flex { display: flex; flex-direction: column; gap: 6px; }
    .meta-item {
        font-size: 13px; color: #94a3b8; display: flex; align-items: center; justify-content: space-between;
        background: rgba(255, 255, 255, 0.01); padding: 6px 12px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.02);
    }
    .meta-label { font-weight: 700; color: #64748b; font-size: 11px; text-transform: uppercase; }
    .meta-valor { color: #cbd5e1; font-weight: 600; }
    
    /* Estilos del Historial */
    .historial-container {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 12px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Título de la App
st.markdown('<h1 style="text-align: center; font-size: 28px; font-weight: 800; background: linear-gradient(90deg, #ffffff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px;">⚡ ECRAWS PRICE</h1>', unsafe_allow_html=True)

# --- AUXILIAR PARA OBTENER EL ARCHIVO MÁS RECIENTE ---
def obtener_ultimo_archivo(carpeta, nombre_fallback=""):
    archivos = glob.glob(os.path.join(carpeta, "*.xlsx")) + glob.glob(os.path.join(carpeta, "*.xls"))
    if archivos:
        return max(archivos, key=os.path.getmtime)
    if nombre_fallback and os.path.exists(nombre_fallback):
        return nombre_fallback
    return None

# --- AUXILIARES Y FORMATEROS ---
def formatear_precio(valor):
    try:
        if pd.isna(valor) or valor == '': return "N/A"
        entero = round(float(valor))
        return f"${entero:,.0f}".replace(",", ".")
    except:
        return f"${valor}"

def formatear_fecha(val):
    try:
        if pd.isna(val): return "Sin fecha"
        dt = pd.to_datetime(val, errors='coerce')
        if pd.notna(dt):
            return dt.strftime("%d/%m/%Y")
        return str(val).split(" ")[0]
    except:
        return str(val)

def evaluar_estado_oferta(desde_val, hasta_val):
    try:
        hoy = datetime.now().date()
        dt_hasta = pd.to_datetime(hasta_val, errors='coerce')
        dt_desde = pd.to_datetime(desde_val, errors='coerce')
        
        if pd.isna(dt_hasta) or pd.isna(dt_desde) or not hasattr(dt_hasta, 'date') or not hasattr(dt_desde, 'date'):
            return ""
            
        f_hasta = dt_hasta.date()
        f_desde = dt_desde.date()
            
        if hoy > f_hasta:
            return 'vencido'
            
        if hoy == f_hasta:
            return '<span class="status-tiempo status-ultimo">⚠️ ¡ÚLTIMO DÍA! Quitar cartel al cerrar</span>'
            
        diferencia = (hoy - f_desde).days
        if diferencia >= 0:
            return f'<span class="status-tiempo status-activo">⏱️ Activa (Hace {diferencia} días)</span>'
        else:
            return f'<span class="status-tiempo status-futuro">⏳ Inicia en {abs(diferencia)} días</span>'
    except:
        return ""

def limpiar_codigo(cod):
    if pd.isna(cod): return ""
    if isinstance(cod, float):
        if cod.is_integer():
            return str(int(cod)).strip().lower()
        else:
            st_cod = f"{cod:f}".strip() if 'e' in str(cod).lower() else str(cod).strip()
            if '.' in st_cod and st_cod.split('.')[1] == '0':
                return st_cod.split('.')[0].lower()
            return st_cod.lower()
            
    if isinstance(cod, int):
        return str(cod).strip().lower()

    st_cod = str(cod).strip()
    if 'e+' in st_cod.lower():
        try:
            st_cod = f"{float(st_cod):.0f}"
        except:
            pass
            
    if '.' in st_cod and st_cod.split('.')[1] == '0':
        st_cod = st_cod.split('.')[0]
    return st_cod.lower()

def fragmentar_codigos_multiples(celda):
    if pd.isna(celda): return []
    if isinstance(celda, (int, float)):
        return [limpiar_codigo(celda)]
        
    texto = str(celda).strip()
    partes = re.split(r'\s*[\|\-,\s]\s*', texto)
    
    codigos_limpios = []
    for p in partes:
        if p.strip() != "":
            cod_p = limpiar_codigo(p)
            if cod_p:
                codigos_limpios.append(cod_p)
    return codigos_limpios

# --- CARGA DE DATOS INDEXADA (OPTIMIZADA Y DINÁMICA) ---
@st.cache_data(show_spinner=False)
def cargar_todo():
    df_base, mapa_base = None, {}
    mapa_puente_barras = {} 
    
    # 1. Maestro EAN
    archivo_ean = obtener_ultimo_archivo("precios", "maestro ean.xlsx")
    if not archivo_ean and os.path.exists("maestro ean.xlsx"):
        archivo_ean = "maestro ean.xlsx"
        
    if archivo_ean:
        try:
            df_maestro = pd.read_excel(archivo_ean)
            for _, fila in df_maestro.iterrows():
                if fila.dropna().empty: continue
                cod_interno_objetivo = limpiar_codigo(fila.iloc[0]) 
                if not cod_interno_objetivo: continue
                
                barras_c = fragmentar_codigos_multiples(fila.iloc[2]) if len(fila) > 2 else []
                barras_d = fragmentar_codigos_multiples(fila.iloc[3]) if len(fila) > 3 else []
                
                for cb in (barras_c + barras_d):
                    if cb:
                        mapa_puente_barras[cb] = cod_interno_objetivo
        except:
            pass

    # 2. Productos / Precios (Busca en carpeta precios/)
    archivo_precios = obtener_ultimo_archivo("precios", "productos.xlsx")
    if not archivo_precios and os.path.exists("productos.xlsx"):
        archivo_precios = "productos.xlsx"
        
    if archivo_precios:
        try:
            # Tolerancia a padrones exportados de sistemas con encabezado en fila 4 o estándar
            df_temp = pd.read_excel(archivo_precios)
            header_idx = 0
            for idx, row in df_temp.iterrows():
                row_str = row.astype(str).str.lower().tolist()
                if any('codigo' in s or 'código' in s or 'descripcion' in s or 'descripción' in s for s in row_str):
                    header_idx = idx + 1
                    break
            
            df_base = pd.read_excel(archivo_precios, skiprows=header_idx) if header_idx > 0 else df_temp
            
            # Mapeo flexible de columnas para Padrones de Artículos o productos.xlsx
            col_map = {}
            for col in df_base.columns:
                c_low = str(col).lower()
                if 'codigo' in c_low or 'código' in c_low or 'interno' in c_low:
                    col_map['cod_int'] = col
                elif 'descrip' in c_low and 'sector' not in c_low and 'rubro' not in c_low:
                    col_map['desc'] = col
                elif 'precio' in c_low:
                    col_map['precio'] = col
                elif 'sector' in c_low or 'rubro' in c_low:
                    col_map['sector'] = col

            col_cod = col_map.get('cod_int', df_base.columns[0] if len(df_base.columns) > 0 else 'Codigo Interno')
            col_desc = col_map.get('desc', df_base.columns[1] if len(df_base.columns) > 1 else 'Descripcion')
            col_prec = col_map.get('precio', df_base.columns[2] if len(df_base.columns) > 2 else 'Precio')
            col_sec = col_map.get('sector', df_base.columns[3] if len(df_base.columns) > 3 else 'Descrip Sector')

            df_base['Descripcion_Clean'] = df_base[col_desc].astype(str).str.strip()
            df_base['Precio_Clean'] = df_base[col_prec].fillna(0)
            df_base['cod_interno_clean'] = df_base[col_cod].apply(limpiar_codigo)
            
            for _, fila in df_base.iterrows():
                sec_val = str(fila[col_sec]).strip() if col_sec in fila and pd.notna(fila[col_sec]) else 'N/A'
                prod_info = {
                    'desc': fila['Descripcion_Clean'], 
                    'precio': fila['Precio_Clean'],
                    'interno': fila['cod_interno_clean'],
                    'sector': sec_val
                }
                if prod_info['interno']: 
                    mapa_base[prod_info['interno']] = prod_info
        except:
            pass

    # 3. Padrón de Ofertas (Busca en carpeta ofertas/ o raíz)
    mapa_ofertas = {}
    
    def agregar_oferta_con_prioridad(codigo, nueva_of):
        if not codigo: return
        if codigo in mapa_ofertas:
            existente = mapa_ofertas[codigo]
            try:
                dt_existente = pd.to_datetime(existente['desde'], errors='coerce')
                dt_nueva = pd.to_datetime(nueva_of['desde'], errors='coerce')
                if pd.notna(dt_existente) and pd.notna(dt_nueva):
                    if dt_nueva > dt_existente:
                        mapa_ofertas[codigo] = nueva_of
                elif pd.isna(dt_existente) and pd.notna(dt_nueva):
                    mapa_ofertas[codigo] = nueva_of
            except:
                mapa_ofertas[codigo] = nueva_of
        else:
            mapa_ofertas[codigo] = nueva_of

    archivo_ofertas = obtener_ultimo_archivo("ofertas", "padron de ofertas.xlsx")
    if not archivo_ofertas and os.path.exists("padron de ofertas.xlsx"):
        archivo_ofertas = "padron de ofertas.xlsx"

    if archivo_ofertas:
        try:
            xls = pd.ExcelFile(archivo_ofertas)
            
            if "OFERTAS" in xls.sheet_names:
                df_of = pd.read_excel(xls, sheet_name="OFERTAS")
                for _, fila in df_of.iterrows():
                    if fila.dropna().empty: continue
                    c_int = limpiar_codigo(fila.iloc[0])
                    c_sku = limpiar_codigo(fila.iloc[2]) if len(fila) > 2 else ""
                    
                    of_data = {
                        'tipo': 'OFERTA', 
                        'precio_of': fila.iloc[5] if len(fila) > 5 else 0, 
                        'ahorro': fila.iloc[6] if len(fila) > 6 else None, 
                        'concepto': fila.iloc[3] if len(fila) > 3 else "OFERTA", 
                        'desde': fila.iloc[10] if len(fila) > 10 else None, 
                        'hasta': fila.iloc[11] if len(fila) > 11 else None
                    }
                    agregar_oferta_con_prioridad(c_int, of_data)
                    agregar_oferta_con_prioridad(c_sku, of_data)

            if "DESTACADOS" in xls.sheet_names:
                df_dest = pd.read_excel(xls, sheet_name="DESTACADOS")
                for _, fila in df_dest.iterrows():
                    if fila.dropna().empty: continue
                    c_int = limpiar_codigo(fila.iloc[0])
                    c_sku = limpiar_codigo(fila.iloc[2]) if len(fila) > 2 else ""
                    
                    of_data = {
                        'tipo': 'DESTACADO', 
                        'precio_of': fila.iloc[4] if len(fila) > 4 else 0, 
                        'ahorro': None, 
                        'concepto': fila.iloc[3] if len(fila) > 3 else "DESTACADO", 
                        'desde': fila.iloc[6] if len(fila) > 6 else None, 
                        'hasta': fila.iloc[7] if len(fila) > 7 else None
                    }
                    agregar_oferta_con_prioridad(c_int, of_data)
                    agregar_oferta_con_prioridad(c_sku, of_data)

            if "COMBOS" in xls.sheet_names:
                df_comb = pd.read_excel(xls, sheet_name="COMBOS")
                for _, fila in df_comb.iterrows():
                    if fila.dropna().empty: continue
                    lista_internos = fragmentar_codigos_multiples(fila.iloc[0])
                    lista_skus = fragmentar_codigos_multiples(fila.iloc[2]) if len(fila) > 2 else []
                    of_data = {
                        'tipo': 'COMBO', 
                        'precio_of': fila.iloc[5] if len(fila) > 5 else 0, 
                        'ahorro': fila.iloc[6] if len(fila) > 6 else None, 
                        'concepto': fila.iloc[3] if len(fila) > 3 else "COMBO", 
                        'desde': fila.iloc[7] if len(fila) > 7 else None, 
                        'hasta': fila.iloc[8] if len(fila) > 8 else None
                    }
                    for sub_int in lista_internos:
                        agregar_oferta_con_prioridad(sub_int, of_data)
                    for sub_sku in lista_skus:
                        agregar_oferta_con_prioridad(sub_sku, of_data)
        except:
            pass

    return df_base, mapa_base, mapa_ofertas, mapa_puente_barras

df_base, mapa_base, mapa_ofertas, mapa_puente_barras = cargar_todo()

# --- FUNCIONES DE CONTROL DEL HISTORIAL ---
def agregar_a_comparacion(producto, promo):
    if any(item['interno'] == producto['interno'] for item in st.session_state.historial):
        st.toast(f"⚠️ '{producto['desc'][:15]}...' ya está en la lista de comparación.")
        return
    
    st.session_state.historial.append({
        'interno': producto['interno'],
        'desc': producto['desc'],
        'precio_base': producto['precio'],
        'sector': producto['sector'],
        'promo': promo
    })
    st.toast("➕ Agregado para comparar")

# --- RENDERIZADO DEL PANEL DE HISTORIAL ---
if st.session_state.historial:
    with st.expander(f"📊 Historial de Comparación ({len(st.session_state.historial)})", expanded=True):
        indice_a_eliminar = None
        for idx, item in enumerate(st.session_state.historial):
            precio_base = formatear_precio(item['precio_base'])
            promo_info = item['promo']
            
            if promo_info:
                precio_final = formatear_precio(promo_info['precio_of'])
                badge_promo = f"🔥 <span style='color: #ffa502; font-weight: bold;'>{promo_info['tipo']}</span>"
            else:
                precio_final = precio_base
                badge_promo = "🏷️ <span style='color: #94a3b8;'>Normal</span>"
                
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                st.markdown(
                    f"<div class='historial-container'>"
                    f"<strong style='font-size:14px; color:#fff;'>{item['desc']}</strong><br>"
                    f"<span style='font-size:12px; color:#94a3b8;'>"
                    f"Precio Final: <strong style='color:#2ecc71; font-size:13px;'>{precio_final}</strong> ({badge_promo}) | Base: {precio_base}"
                    f"</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with col_btn:
                st.markdown('<div class="btn-eliminar">', unsafe_allow_html=True)
                if st.button("❌", key=f"del_{item['interno']}_{idx}"):
                    indice_a_eliminar = idx
                st.markdown('</div>', unsafe_allow_html=True)
        
        if indice_a_eliminar is not None:
            st.session_state.historial.pop(indice_a_eliminar)
            st.rerun()
            
        if st.button("🗑️ Vaciar Historial", key="vaciar_historial"):
            st.session_state.historial = []
            st.rerun()

# --- INTERFAZ DE BÚSQUEDA ---
if df_base is not None:
    with st.form(key="formulario_busqueda", clear_on_submit=False):
        busqueda_input = st.text_input("🔍 Buscar Producto:", placeholder="Código o nombre...", value=st.session_state.busqueda_activa)
        bot_buscar = st.form_submit_button("CONSEGUIR PRECIO")
        if bot_buscar:
            st.session_state.busqueda_activa = busqueda_input

    # Procesar resultados
    if st.session_state.busqueda_activa:
        busqueda_limpia = limpiar_codigo(st.session_state.busqueda_activa)
        resultados_lista = []
        
        if busqueda_limpia in mapa_puente_barras:
            busqueda_limpia = mapa_puente_barras[busqueda_limpia]

        if busqueda_limpia in mapa_base:
            resultados_lista.append(mapa_base[busqueda_limpia])
        else:
            res_df = df_base[df_base['Descripcion_Clean'].str.lower().str.contains(st.session_state.busqueda_activa.lower(), na=False)]
            for _, fila in res_df.iterrows():
                resultados_lista.append({
                    'desc': fila['Descripcion_Clean'], 'precio': fila['Precio_Clean'],
                    'interno': fila['cod_interno_clean'],
                    'sector': str(fila['Descrip Sector']).strip() if 'Descrip Sector' in fila and pd.notna(fila['Descrip Sector']) else 'N/A'
                })

        # --- MOSTRAR RESULTADOS ---
        if resultados_lista:
            st.write("---")
            for idx, prod in enumerate(resultados_lista):
                oferta_vinculada = mapa_ofertas.get(prod['interno'])
                precio_base_visual = formatear_precio(prod['precio'])
                cod_int = prod['interno'] if prod['interno'] != '' else 'N/A'
                
                badge_tiempo = ""
                es_oferta_valida = False
                
                if oferta_vinculada:
                    resultado_evaluacion = evaluar_estado_oferta(oferta_vinculada['desde'], oferta_vinculada['hasta'])
                    if resultado_evaluacion != 'vencido':
                        es_oferta_valida = True
                        badge_tiempo = resultado_evaluacion

                # Renderizar tarjeta gráfica
                if es_oferta_valida:
                    precio_oferta_visual = formatear_precio(oferta_vinculada['precio_of'])
                    txt_ahorro = f" | Ahorrás: {formatear_precio(oferta_vinculada['ahorro'])}" if oferta_vinculada['ahorro'] else ""
                    txt_hasta = formatear_fecha(oferta_vinculada['hasta'])
                    concepto_txt = str(oferta_vinculada['concepto']).upper() if pd.notna(oferta_vinculada['concepto']) else "PROMOCIÓN"
                    tipo_promo = str(oferta_vinculada['tipo'])
                    
                    if tipo_promo == "COMBO":
                        bloque_precio_html = (
                            f'<div class="precio-split-container">'
                            f'<div class="split-half">'
                            f'<div class="split-label">Normal Indiv.</div>'
                            f'<div class="precio-enorme" style="color:#94a3b8;">{precio_base_visual}</div>'
                            f'</div>'
                            f'<div class="split-half combo-side">'
                            f'<div class="split-label" style="color:#ffa502;">Precio Combo</div>'
                            f'<div class="precio-enorme precio-oferta-color">{precio_oferta_visual}</div>'
                            f'</div>'
                            f'</div>'
                        )
                    else:
                        bloque_precio_html = (
                            f'<div class="precio-contenedor">'
                            f'<p class="precio-enorme precio-oferta-color">{precio_oferta_visual}</p>'
                            f'<p style="margin:5px 0 0 0; font-size:13px; color:#94a3b8 !important;">Precio normal: <del>{precio_base_visual}</del></p>'
                            f'</div>'
                        )
                    
                    html_tarjeta = (
                        f'<div class="producto-card con-oferta">'
                        f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:6px;">'
                        f'<span style="padding:4px 10px; background:linear-gradient(135deg, #ff4757, #ffa502); color:white; font-weight:700; font-size:11px; border-radius:8px; text-transform:uppercase; letter-spacing:0.5px;">🔥 {tipo_promo}</span>'
                        f'{badge_tiempo}'
                        f'</div>'
                        f'<h2 class="producto-titulo">{prod["desc"]}</h2>'
                        f'{bloque_precio_html}'
                        f'<div class="info-oferta-bloque">'
                        f'📦 <b>DETALLE:</b> {concepto_txt}{txt_ahorro}<br>'
                        f'<span style="color:#94a3b8; font-size:12px;">📅 Vence: {txt_hasta}</span>'
                        f'</div>'
                        f'<div class="meta-flex">'
                        f'<div class="meta-item"><span class="meta-label">Código Interno</span><span class="meta-valor">{cod_int}</span></div>'
                        f'<div class="meta-item"><span class="meta-label">Sector</span><span class="meta-valor">{prod["sector"]}</span></div>'
                        f'</div>'
                        f'</div>'
                    )
                else:
                    html_tarjeta = (
                        f'<div class="producto-card">'
                        f'<h2 class="producto-titulo">{prod["desc"]}</h2>'
                        f'<div class="precio-contenedor"><p class="precio-enorme">{precio_base_visual}</p></div>'
                        f'<div class="meta-flex">'
                        f'<div class="meta-item"><span class="meta-label">Código Interno</span><span class="meta-valor">{cod_int}</span></div>'
                        f'<div class="meta-item"><span class="meta-label">Sector</span><span class="meta-valor">{prod["sector"]}</span></div>'
                        f'</div>'
                        f'</div>'
                    )
                
                st.markdown(html_tarjeta, unsafe_allow_html=True)
                
                st.markdown('<div class="btn-secundario">', unsafe_allow_html=True)
                promo_a_guardar = oferta_vinculada if es_oferta_valida else None
                if st.button("➕ Añadir a comparación", key=f"add_{prod['interno']}_{idx}"):
                    agregar_a_comparacion(prod, promo_a_guardar)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error(f"🔍 No se encontró ningún artículo para: '{st.session_state.busqueda_activa}'.")
else:
    st.info("ℹ️ Sube tus planillas de Excel en la carpeta `precios/` en GitHub para comenzar.")
