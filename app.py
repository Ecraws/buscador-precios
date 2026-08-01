import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re
import os
import glob
import unicodedata

# Configuración de página optimizada para rendimiento y diseño móvil
st.set_page_config(
    page_title="Depot Consultas", 
    page_icon="🛒", 
    layout="centered"
)

# --- CONSTANTES DE CONTROL ---
MAX_RESULTADOS_VISIBLES = 25

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
        background-color: #081C33 !important; /* Azul marino Depot */
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
        border-color: #FF8135 !important;
        box-shadow: 0 0 10px rgba(255, 129, 53, 0.25) !important;
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
        background: linear-gradient(135deg, #FF8135 0%, #FFB35C 100%) !important;
        color: #081C33 !important;
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
        background: linear-gradient(90deg, #0B3B6B, #4A85BD);
    }

    .producto-card.con-oferta::before {
        background: linear-gradient(90deg, #ff4757, #FF8135) !important;
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
        background: rgba(255, 129, 53, 0.05);
        border: 1px solid rgba(255, 129, 53, 0.25) !important;
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
        background: linear-gradient(90deg, #ff4757 0%, #FF8135 100%);
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
st.markdown(
    '<div style="text-align:center; margin-bottom:20px;">'
    '<span style="font-size:30px; font-weight:800; color:#ffffff;">Depot<span style="color:#FF8135;">.</span> Consultas</span>'
    '<span style="font-size:13px; font-style:italic; color:#FF8135; margin-left:8px;">by ecraws</span>'
    '</div>',
    unsafe_allow_html=True
)

# --- FIRMA DE ARCHIVOS PARA INVALIDAR CACHÉ AUTOMÁTICAMENTE ---
def obtener_firma_archivos():
    """Devuelve una tupla (ruta, fecha_modificacion) por cada archivo relevante.
    Cambia apenas se sube/reemplaza un Excel, forzando a Streamlit a recalcular."""
    firma = []
    for carpeta in ("precios", "ofertas"):
        if os.path.isdir(carpeta):
            for patron in ("*.xlsx", "*.xls"):
                for f in glob.glob(os.path.join(carpeta, patron)):
                    try:
                        firma.append((f, os.path.getmtime(f)))
                    except OSError:
                        pass
    for nombre in ("maestro ean.xlsx", "productos.xlsx", "padron de ofertas.xlsx"):
        if os.path.exists(nombre):
            try:
                firma.append((nombre, os.path.getmtime(nombre)))
            except OSError:
                pass
    return tuple(sorted(firma))

# --- AUXILIARES Y FORMATEROS ---
def formatear_precio(valor):
    try:
        if pd.isna(valor) or valor == '': return "N/A"
        entero = round(float(valor))
        return f"${entero:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return f"${valor}"

def formatear_fecha(val):
    try:
        if pd.isna(val): return "Sin fecha"
        dt = pd.to_datetime(val, errors='coerce')
        if pd.notna(dt):
            return dt.strftime("%d/%m/%Y")
        return str(val).split(" ")[0]
    except (ValueError, TypeError):
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
            
        dias_para_terminar = (f_hasta - hoy).days

        if hoy == f_hasta:
            return '<span class="status-tiempo status-ultimo">⚠️ ¡ÚLTIMO DÍA! Quitar cartel al cerrar</span>'
            
        diferencia = (hoy - f_desde).days
        if diferencia >= 0:
            return f'<span class="status-tiempo status-activo">⏱️ Activa (Hace {diferencia} días · Termina en {dias_para_terminar} días)</span>'
        else:
            return f'<span class="status-tiempo status-futuro">⏳ Inicia en {abs(diferencia)} días (Termina en {dias_para_terminar} días)</span>'
    except (ValueError, TypeError, AttributeError):
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
        except (ValueError, TypeError):
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

# --- DICCIONARIO DE ENCABEZADOS REALES (según referencia provista por el usuario) ---
# Cada campo lógico que la app necesita puede tener varios nombres de columna según la hoja
# (OFERTAS/DESTACADO usan "COD_INT", "PRECIO", "OFERTA"; BODEGA LIQUID/PDP usan "Código Interno",
# "PVP CU", "Oferta CU"; COMBOS agrega sufijos numéricos como "OFERTA7"). Para agregar soporte a
# una hoja nueva en el futuro, alcanza con sumar el nombre de columna que use a la lista del
# campo correspondiente acá abajo — no hace falta tocar el resto del código.
ALIAS_CAMPOS = {
    'interno':       ['cod_int', 'codigo interno', 'interno'],
    'sku':           ['sku', 'codigo de barras', 'codigo ean', 'ean', 'barra'],
    'descripcion':   ['descripcion_articulos', 'articulo', 'descripcion'],
    'precio_normal': ['pvp cu', 'precio'],
    'precio_oferta': ['oferta cu', 'oferta'],
    'ahorro':        ['ahorro cu', 'ahorro'],
    'concepto':      ['concepto'],
    'desde':         ['desde'],
    'hasta':         ['hasta'],
    'sector':        ['sector', 'rubro'],
}

def _normalizar_encabezado(texto):
    """Pasa a minúsculas, saca acentos y quita sufijos numéricos finales
    (ej: 'SKU4' -> 'sku', 'OFERTA7' -> 'oferta', 'Código Interno' -> 'codigo interno')."""
    texto = str(texto).strip().lower()
    texto = ''.join(c for c in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(c))
    texto = re.sub(r'\d+$', '', texto).strip()
    return texto

def detectar_columna_por_campo(df, campo, indice_fallback=None, excluir=None):
    """Busca la columna que corresponde a un campo lógico (ej: 'precio_oferta') usando el
    diccionario ALIAS_CAMPOS. Primero intenta una coincidencia EXACTA de encabezado normalizado
    (evita que 'precio' matchee 'Precio Individual' cuando existe una columna 'Oferta' separada);
    si ninguna columna coincide exactamente, prueba una coincidencia parcial como respaldo."""
    excluir = excluir or []
    alias_posibles = ALIAS_CAMPOS.get(campo, [campo])
    normalizados = {_normalizar_encabezado(c): c for c in df.columns}

    for alias in alias_posibles:
        if alias in normalizados:
            col = normalizados[alias]
            if not any(ex in _normalizar_encabezado(col) for ex in excluir):
                return col

    for alias in alias_posibles:
        for col in df.columns:
            col_norm = _normalizar_encabezado(col)
            if alias in col_norm and not any(ex in col_norm for ex in excluir):
                return col

    if indice_fallback is not None and indice_fallback < len(df.columns):
        return df.columns[indice_fallback]
    return None

def buscar_hoja(nombres_disponibles, objetivo):
    """Encuentra el nombre real de una hoja de Excel comparando sin importar
    mayúsculas/minúsculas ni espacios sobrantes (ej: ' ofertas ' == 'OFERTAS')."""
    objetivo_low = objetivo.strip().lower()
    for nombre in nombres_disponibles:
        if str(nombre).strip().lower() == objetivo_low:
            return nombre
    return None


def valor_fila(fila, columna, default=None):
    """Acceso seguro a un valor de fila por nombre de columna."""
    if columna is None or columna not in fila:
        return default
    val = fila[columna]
    return val if pd.notna(val) else default

# --- CARGA DE DATOS INDEXADA (OPTIMIZADA Y DINÁMICA) ---
@st.cache_data(show_spinner=False)
def cargar_todo(firma_archivos):
    # 'firma_archivos' no se usa dentro de la función: solo sirve como parte de la
    # clave de caché, así Streamlit recalcula todo apenas cambia algún Excel en disco.
    df_base, mapa_base = None, {}
    mapa_puente_barras = {}
    mapa_interno_a_barras = {}
    diagnosticos = []

    # 1 y 2. Carpeta "precios/": products con precio Y maestro de códigos/EAN.
    # No importa el nombre de los archivos: se procesan TODOS los que haya en la carpeta,
    # y cada uno se clasifica según su contenido (si tiene una columna de precio, se trata
    # como padrón de productos; si no, se asume que es un maestro de códigos/EAN).
    archivos_precios_candidatos = []
    if os.path.isdir("precios"):
        archivos_precios_candidatos = glob.glob(os.path.join("precios", "*.xlsx")) + glob.glob(os.path.join("precios", "*.xls"))
    for nombre_respaldo in ("productos.xlsx", "maestro ean.xlsx"):
        if os.path.exists(nombre_respaldo) and nombre_respaldo not in archivos_precios_candidatos:
            archivos_precios_candidatos.append(nombre_respaldo)

    frames_productos = []

    for ruta in archivos_precios_candidatos:
        try:
            df_temp = pd.read_excel(ruta)
        except Exception as e:
            diagnosticos.append(f"No se pudo leer '{ruta}': {e}")
            continue

        if df_temp.dropna(how='all').empty:
            continue

        try:
            # Tolerancia a padrones exportados de sistemas con encabezado en fila 4 o estándar
            header_idx = 0
            for idx, row in df_temp.iterrows():
                row_str = [str(v).lower() for v in row.tolist()]
                if any('codigo' in s or 'código' in s or 'descripcion' in s or 'descripción' in s for s in row_str):
                    header_idx = idx + 1
                    break
            df_archivo = pd.read_excel(ruta, skiprows=header_idx) if header_idx > 0 else df_temp

            columnas_low = [_normalizar_encabezado(c) for c in df_archivo.columns]
            parece_productos = any(
                alias in col_norm for col_norm in columnas_low for alias in ALIAS_CAMPOS['precio_normal']
            )

            if parece_productos:
                col_cod = detectar_columna_por_campo(df_archivo, 'interno', 0, excluir=['ean', 'barra'])
                col_ean = detectar_columna_por_campo(df_archivo, 'sku')
                col_desc = detectar_columna_por_campo(df_archivo, 'descripcion', 1, excluir=['sector', 'rubro'])
                col_prec = detectar_columna_por_campo(df_archivo, 'precio_normal', 2)
                col_sec = detectar_columna_por_campo(df_archivo, 'sector', 3)

                if col_cod is None or col_desc is None or col_prec is None:
                    diagnosticos.append(f"'{ruta}': no se pudieron identificar columnas de código/descripción/precio, se omite.")
                else:
                    sub = pd.DataFrame()
                    sub['Descripcion_Clean'] = df_archivo[col_desc].astype(str).str.strip()
                    sub['Precio_Clean'] = df_archivo[col_prec].fillna(0)
                    sub['cod_interno_clean'] = df_archivo[col_cod].apply(limpiar_codigo)
                    sub['ean_clean'] = df_archivo[col_ean].apply(limpiar_codigo) if col_ean is not None else ""
                    sub['Sector_Clean'] = df_archivo[col_sec].astype(str).str.strip() if col_sec is not None else 'N/A'
                    frames_productos.append(sub)
            else:
                # No tiene columna de precio: se asume maestro de códigos/EAN.
                # Columna 0 = código interno; columnas 2 y 3 = códigos de barra/EAN asociados.
                for fila_idx, fila in df_archivo.iterrows():
                    if fila.dropna().empty: continue
                    try:
                        cod_interno_objetivo = limpiar_codigo(fila.iloc[0])
                        if not cod_interno_objetivo: continue

                        barras_c = fragmentar_codigos_multiples(fila.iloc[2]) if len(fila) > 2 else []
                        barras_d = fragmentar_codigos_multiples(fila.iloc[3]) if len(fila) > 3 else []

                        for cb in (barras_c + barras_d):
                            if cb:
                                mapa_puente_barras[cb] = cod_interno_objetivo
                                lista_barras = mapa_interno_a_barras.setdefault(cod_interno_objetivo, [])
                                if cb not in lista_barras:
                                    lista_barras.append(cb)
                    except Exception as e:
                        diagnosticos.append(f"'{ruta}', fila {fila_idx + 2}: {e}")
        except Exception as e:
            diagnosticos.append(f"'{ruta}': {e}")

    if frames_productos:
        df_base = pd.concat(frames_productos, ignore_index=True)
        for fila_idx, fila in df_base.iterrows():
            try:
                interno = fila['cod_interno_clean']
                if interno:
                    mapa_base[interno] = {
                        'desc': fila['Descripcion_Clean'],
                        'precio': fila['Precio_Clean'],
                        'interno': interno,
                        'ean': fila['ean_clean'],
                        'sector': fila['Sector_Clean']
                    }
            except Exception as e:
                diagnosticos.append(f"Error al indexar producto (fila {fila_idx + 2}): {e}")

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
            except (ValueError, TypeError):
                mapa_ofertas[codigo] = nueva_of
        else:
            mapa_ofertas[codigo] = nueva_of

    def _procesar_hoja_de_ofertas(df_hoja, tipo_etiqueta, nombre_hoja, ruta, permite_multiples_codigos=False):
        """Extrae ofertas de una hoja usando el diccionario ALIAS_CAMPOS. Sirve para cualquier
        hoja con esta forma (OFERTAS, DESTACADO, BODEGA LIQUID, PDP, COMBOS)."""
        c_int = detectar_columna_por_campo(df_hoja, 'interno', 0)
        c_sku = detectar_columna_por_campo(df_hoja, 'sku', 2)
        c_concepto = detectar_columna_por_campo(df_hoja, 'concepto', excluir=['producto', 'articulo'])
        c_precio_of = detectar_columna_por_campo(df_hoja, 'precio_oferta', excluir=['normal', 'individual', 'unitario', 'lista'])
        if c_precio_of is None:
            # Hojas de un solo precio (ej. DESTACADO) no tienen columna "oferta" separada:
            # esa única columna de precio ES el precio a mostrar.
            c_precio_of = detectar_columna_por_campo(df_hoja, 'precio_normal')
        c_ahorro = detectar_columna_por_campo(df_hoja, 'ahorro')
        c_desde = detectar_columna_por_campo(df_hoja, 'desde')
        c_hasta = detectar_columna_por_campo(df_hoja, 'hasta')

        if c_precio_of is None:
            diagnosticos.append(f"'{ruta}', hoja {nombre_hoja}: no se encontró una columna de precio de oferta reconocible, se omite la hoja.")
            return

        for fila_idx, fila in df_hoja.iterrows():
            if fila.dropna().empty: continue
            try:
                of_data = {
                    'tipo': tipo_etiqueta,
                    'precio_of': valor_fila(fila, c_precio_of, 0),
                    'ahorro': valor_fila(fila, c_ahorro),
                    'concepto': valor_fila(fila, c_concepto, tipo_etiqueta),
                    'desde': valor_fila(fila, c_desde),
                    'hasta': valor_fila(fila, c_hasta)
                }
                if permite_multiples_codigos:
                    for cod in fragmentar_codigos_multiples(valor_fila(fila, c_int)):
                        agregar_oferta_con_prioridad(cod, of_data)
                    for cod in fragmentar_codigos_multiples(valor_fila(fila, c_sku)):
                        agregar_oferta_con_prioridad(cod, of_data)
                else:
                    agregar_oferta_con_prioridad(limpiar_codigo(valor_fila(fila, c_int, '')), of_data)
                    agregar_oferta_con_prioridad(limpiar_codigo(valor_fila(fila, c_sku, '')), of_data)
            except Exception as e:
                diagnosticos.append(f"'{ruta}', hoja {nombre_hoja}, fila {fila_idx + 2}: {e}")

    # Hojas reconocidas: (nombre de la hoja en el Excel, etiqueta a mostrar en la tarjeta,
    # permite varios códigos por celda). Para sumar una hoja nueva en el futuro, agregá una
    # tupla acá — no hace falta tocar nada más.
    HOJAS_RECONOCIDAS = [
        ("OFERTAS", "OFERTA", False),
        ("DESTACADO", "DESTACADO", False),
        ("DESTACADOS", "DESTACADO", False),
        ("BODEGA LIQUID", "LIQUIDACIÓN", False),
        ("PDP", "PDP", False),
        ("COMBOS", "COMBO", True),
    ]

    archivos_ofertas_candidatos = []
    if os.path.isdir("ofertas"):
        archivos_ofertas_candidatos = glob.glob(os.path.join("ofertas", "*.xlsx")) + glob.glob(os.path.join("ofertas", "*.xls"))
    if os.path.exists("padron de ofertas.xlsx") and "padron de ofertas.xlsx" not in archivos_ofertas_candidatos:
        archivos_ofertas_candidatos.append("padron de ofertas.xlsx")

    for ruta in archivos_ofertas_candidatos:
        try:
            xls = pd.ExcelFile(ruta)
            hojas_ya_procesadas = set()

            for nombre_objetivo, tipo_etiqueta, multi_codigo in HOJAS_RECONOCIDAS:
                hoja_real = buscar_hoja(xls.sheet_names, nombre_objetivo)
                if hoja_real and hoja_real not in hojas_ya_procesadas:
                    df_hoja = pd.read_excel(xls, sheet_name=hoja_real)
                    _procesar_hoja_de_ofertas(df_hoja, tipo_etiqueta, hoja_real, ruta, permite_multiples_codigos=multi_codigo)
                    hojas_ya_procesadas.add(hoja_real)

            if not hojas_ya_procesadas:
                nombres_reconocidos = ", ".join(sorted(set(n for n, _, _ in HOJAS_RECONOCIDAS)))
                diagnosticos.append(f"'{ruta}': no se encontró ninguna hoja reconocida (se esperaba alguna de: {nombres_reconocidos}).")
        except Exception as e:
            diagnosticos.append(f"No se pudo leer '{ruta}': {e}")

    return df_base, mapa_base, mapa_ofertas, mapa_puente_barras, mapa_interno_a_barras, diagnosticos

firma_actual = obtener_firma_archivos()
df_base, mapa_base, mapa_ofertas, mapa_puente_barras, mapa_interno_a_barras, diagnosticos_carga = cargar_todo(firma_actual)

# --- PANEL DE DIAGNÓSTICO (solo aparece si hubo problemas al leer algún Excel) ---
if diagnosticos_carga:
    with st.expander(f"⚠️ Avisos al cargar los datos ({len(diagnosticos_carga)})", expanded=False):
        st.caption("Estas filas o archivos tuvieron problemas y se omitieron. El resto de la app funciona con normalidad.")
        for d in diagnosticos_carga[:50]:
            st.caption(f"• {d}")
        if len(diagnosticos_carga) > 50:
            st.caption(f"... y {len(diagnosticos_carga) - 50} avisos más.")

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
                badge_promo = f"🔥 <span style='color: #FF8135; font-weight: bold;'>{promo_info['tipo']}</span>"
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
                    'ean': fila['ean_clean'] if 'ean_clean' in fila and pd.notna(fila['ean_clean']) else '',
                    'sector': fila['Sector_Clean'] if 'Sector_Clean' in fila and pd.notna(fila['Sector_Clean']) else 'N/A'
                })

        # --- MOSTRAR RESULTADOS ---
        if resultados_lista:
            st.write("---")

            total_encontrados = len(resultados_lista)
            if total_encontrados > MAX_RESULTADOS_VISIBLES:
                st.info(
                    f"🔎 Se encontraron {total_encontrados} resultados. Mostrando los primeros "
                    f"{MAX_RESULTADOS_VISIBLES}: afiná tu búsqueda para ver menos coincidencias."
                )
                resultados_lista = resultados_lista[:MAX_RESULTADOS_VISIBLES]

            for idx, prod in enumerate(resultados_lista):
                oferta_vinculada = mapa_ofertas.get(prod['interno'])
                precio_base_visual = formatear_precio(prod['precio'])
                cod_int = prod['interno'] if prod['interno'] != '' else 'N/A'

                ean_directo = prod.get('ean', '')
                if ean_directo:
                    ean_visual = ean_directo
                else:
                    barras_relacionadas = mapa_interno_a_barras.get(prod['interno'], [])
                    ean_visual = ", ".join(barras_relacionadas) if barras_relacionadas else "N/A"
                
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
                            f'<div class="split-label" style="color:#FF8135;">Precio Combo</div>'
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
                        f'<span style="padding:4px 10px; background:linear-gradient(135deg, #ff4757, #FF8135); color:white; font-weight:700; font-size:11px; border-radius:8px; text-transform:uppercase; letter-spacing:0.5px;">🔥 {tipo_promo}</span>'
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
                        f'<div class="meta-item"><span class="meta-label">EAN</span><span class="meta-valor">{ean_visual}</span></div>'
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
                        f'<div class="meta-item"><span class="meta-label">EAN</span><span class="meta-valor">{ean_visual}</span></div>'
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
