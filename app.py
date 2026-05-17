# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import pickle
import streamlit as st

# ══════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title='Load Forecast — Complex',
    page_icon='⛏️',
    layout='wide'
)

# ══════════════════════════════════════════════════════════════════
# ESTILOS
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* Fondo general */
    .stApp { background-color: #1A1A2E; }
    section[data-testid="stSidebar"] { background-color: #16213E; }

    /* Tipografía general */
    html, body, [class*="css"] {
        color: #E8EDF5;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Título principal */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #F0A500;
        letter-spacing: 2px;
        text-transform: uppercase;
        border-bottom: 2px solid #F0A500;
        padding-bottom: 10px;
        margin-bottom: 24px;
    }

    /* Encabezado de pit */
    .pit-header {
        background: linear-gradient(90deg, #0F3460, #16213E);
        border-left: 4px solid #F0A500;
        border-radius: 6px;
        padding: 10px 18px;
        margin: 20px 0 12px 0;
        font-size: 1.1rem;
        font-weight: 700;
        color: #F0A500;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* Encabezado de modelo */
    .model-header {
        background-color: #0F3460;
        border-radius: 6px;
        padding: 6px 14px;
        margin: 10px 0 8px 0;
        font-size: 0.85rem;
        font-weight: 600;
        color: #B0C4DE;
        letter-spacing: 1px;
    }

    /* Cards de sección */
    .section-card {
        background-color: #16213E;
        border: 1px solid #0F3460;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 16px;
    }

    /* Resultado */
    .result-box {
        background: linear-gradient(135deg, #0F3460, #1A1A2E);
        border: 2px solid #F0A500;
        border-radius: 14px;
        padding: 32px;
        text-align: center;
        margin-top: 20px;
    }
    .result-label {
        font-size: 0.95rem;
        color: #8899BB;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .result-value {
        font-size: 4rem;
        font-weight: 900;
        color: #00E676;
        line-height: 1;
    }
    .result-error {
        font-size: 0.8rem;
        color: #8899BB;
        margin-top: 10px;
    }

    /* Sliders */
    .stSlider > div > div > div > div {
        background-color: #F0A500 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #16213E;
        border-radius: 8px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8899BB;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0F3460 !important;
        color: #F0A500 !important;
        border-radius: 6px;
    }

    /* Botón */
    .stButton > button {
        background-color: #F0A500;
        color: #1A1A2E;
        font-weight: 800;
        font-size: 1.1rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        border: none;
        border-radius: 10px;
        padding: 14px 40px;
        width: 100%;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #FFC027;
        transform: scale(1.02);
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #0F3460;
        border: 1px solid #1E3A5F;
        color: #E8EDF5;
    }

    /* Ocultar elementos por defecto de Streamlit */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# CARGAR MODELO
# ══════════════════════════════════════════════════════════════════
@st.cache_resource
def cargar_modelo():
    filename = 'modelo-ensamble-reg-loads-v2.1.pkl'
    return pickle.load(open(filename, 'rb'))

modelo, variables, min_max_scaler = cargar_modelo()

# ══════════════════════════════════════════════════════════════════
# ESTRUCTURA DE EQUIPOS POR PIT Y MODELO
# ══════════════════════════════════════════════════════════════════
EQUIPOS_POR_PIT = {
    'DESCANSO': {
        'Komatsu PC8000': ['6233', '6234', '6239','6247', '6248'],
        'Bucyrus BE495':  ['6243', '6244'],
        'Hitachi EX3600': ['6260'],
    },
    'DP5': {
        'Komatsu PC8000': ['6232', '6236', '6237', '6238', '6250'],
        'Bucyrus BE495':  ['6242'],
        'Hitachi EX3600': ['6261', '6263'],
        'Apron Feeder':   ['6449', '6455'],
    },
    'EC': {
        'Komatsu PC8000': ['6231'],
        'Hitachi EX3600': ['6262'],
        'Komatsu PC4000': ['6268'],
    },
    'PRIBBENOW': {
        'Komatsu PC8000': ['6235', '6245', '6246', '6249'],
        'Bucyrus BE495':  ['6241'],
        'Komatsu PC4000': ['6264', '6269'],
        'Apron Feeder':   ['6457'],
    },
}

# Colores por modelo (consistente con Power BI)
COLOR_MODELO = {
    'Komatsu PC8000': '#1E2761',
    'Komatsu PC4000': '#065A82',
    'Hitachi EX3600': '#028090',
    'Bucyrus BE495':  '#2C5F2D',
    'Apron Feeder':   '#FF8C00',
}

COLS_NUMERICAS = [
    'UsodeDisp_6231','UsodeDisp_6232','UsodeDisp_6233','UsodeDisp_6234',
    'UsodeDisp_6235','UsodeDisp_6236','UsodeDisp_6237','UsodeDisp_6238',
    'UsodeDisp_6239','UsodeDisp_6241','UsodeDisp_6242','UsodeDisp_6243',
    'UsodeDisp_6244','UsodeDisp_6245','UsodeDisp_6246','UsodeDisp_6247',
    'UsodeDisp_6248','UsodeDisp_6249','UsodeDisp_6250','UsodeDisp_6260',
    'UsodeDisp_6261','UsodeDisp_6262','UsodeDisp_6263','UsodeDisp_6264',
    'UsodeDisp_6268','UsodeDisp_6269','UsodeDisp_6449','UsodeDisp_6455',
    'UsodeDisp_6457',
    'QtyCamiones_DESCANSO','Disponibilidad_TKS_DESCANSO',
    'UsodeDisp_TKS_DESCANSO','TiempoCiclo_TKS_DESCANSO',
    'QtyCamiones_DP5','Disponibilidad_TKS_DP5',
    'UsodeDisp_TKS_DP5','TiempoCiclo2_DP5',
    'QtyCamiones_EC','Disponibilidad_TKS_EC',
    'UsodeDisp_TKS_EC','TiempoCiclo2_EC',
    'QtyCamiones_PRIBBENOW','Disponibilidad_TKS_PRIBBENOW',
    'UsodeDisp_TKS_PRIBBENOW','TiempoCiclo_TKS_PRIBBENOW',
]

COLUMNAS_ESPERADAS = COLS_NUMERICAS + ['turno']

# ══════════════════════════════════════════════════════════════════
# TÍTULO
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="main-title">⛏ Load Forecast Simulator — Complex</div>',
            unsafe_allow_html=True)

col_form, col_result = st.columns([3, 1])

with col_form:
    # ── TURNO ────────────────────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 3])
    with c1:
        turno = st.selectbox('⚙️ Turno', ['D', 'N'])
    st.markdown('</div>', unsafe_allow_html=True)

    # ── PALAS POR PIT Y MODELO ───────────────────────────────────
    st.markdown('### 🚧 Palas — Uso de Disponibilidad')

    vals_palas = {}
    tabs_pit = st.tabs(list(EQUIPOS_POR_PIT.keys()))

    for tab, pit in zip(tabs_pit, EQUIPOS_POR_PIT.keys()):
        with tab:
            for modelo_eq, equipos in EQUIPOS_POR_PIT[pit].items():
                color = COLOR_MODELO.get(modelo_eq, '#555')
                st.markdown(
                    f'<div class="model-header" style="border-left:3px solid {color}">'
                    f'  {modelo_eq}'
                    f'</div>',
                    unsafe_allow_html=True
                )
                cols = st.columns(len(equipos))
                for col, eq in zip(cols, equipos):
                    with col:
                        vals_palas[f'UsodeDisp_{eq}'] = st.slider(
                            f'{eq}',
                            min_value=0.0, max_value=1.0,
                            value=0.75, step=0.01,
                            key=f'pala_{eq}'
                        )

    # ── CAMIONES POR PIT ─────────────────────────────────────────
    st.markdown('### 🚛 Camiones — por Pit')

    vals_camiones = {}
    tabs_cam = st.tabs(list(EQUIPOS_POR_PIT.keys()))

    for tab, pit in zip(tabs_cam, EQUIPOS_POR_PIT.keys()):
        with tab:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)

            with c1:
                vals_camiones[f'QtyCamiones_{pit}'] = st.slider(
                    '🔢 Qty Camiones',
                    min_value=0.0, max_value=150.0,
                    value=80.0, step=1.0,
                    key=f'qty_{pit}'
                )
            with c2:
                vals_camiones[f'Disponibilidad_TKS_{pit}'] = st.slider(
                    '✅ Disponibilidad',
                    min_value=0.0, max_value=1.0,
                    value=0.80, step=0.01,
                    key=f'disp_{pit}'
                )
            with c3:
                vals_camiones[f'UsodeDisp_TKS_{pit}'] = st.slider(
                    '📊 Uso Disponibilidad',
                    min_value=0.0, max_value=1.0,
                    value=0.75, step=0.01,
                    key=f'uso_{pit}'
                )
            with c4:
                col_ciclo = (
                    'TiempoCiclo_TKS_DESCANSO' if pit == 'DESCANSO'  else
                    'TiempoCiclo2_DP5'          if pit == 'DP5'       else
                    'TiempoCiclo2_EC'            if pit == 'EC'        else
                    'TiempoCiclo_TKS_PRIBBENOW'
                )
                vals_camiones[col_ciclo] = st.slider(
                    '⏱ Ciclo (min)',
                    min_value=20.0, max_value=42.0,
                    value=30.0, step=0.1,
                    key=f'ciclo_{pit}'
                )
            st.markdown('</div>', unsafe_allow_html=True)

    # ── BOTÓN PREDECIR ───────────────────────────────────────────
    st.markdown('<br>', unsafe_allow_html=True)
    predecir = st.button('▶ CALCULAR PREDICCIÓN')

# ══════════════════════════════════════════════════════════════════
# PANEL DE RESULTADO
# ══════════════════════════════════════════════════════════════════
with col_result:
    st.markdown('<br><br>', unsafe_allow_html=True)
    resultado_placeholder = st.empty()

    resultado_placeholder.markdown("""
        <div class="result-box">
            <div class="result-label">Loads Predicted</div>
            <div class="result-value" style="color:#2A3A5A">—</div>
            <div class="result-error">Ingresa los datos y presiona Calcular</div>
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# PREDICCIÓN
# ══════════════════════════════════════════════════════════════════
if predecir:
    # Construir DataFrame
    datos = {**vals_palas, **vals_camiones, 'turno': turno}
    data = pd.DataFrame([datos])[COLUMNAS_ESPERADAS]

    # Preparar datos
    data_prep = data.copy()
    data_prep = pd.get_dummies(data_prep, columns=['turno'],
                                drop_first=False, dtype=int)
    data_prep = data_prep.reindex(columns=variables, fill_value=0)
    data_prep[COLS_NUMERICAS] = min_max_scaler.transform(
        data_prep[COLS_NUMERICAS]
    )

    # Predecir
    Y_pred = modelo.predict(data_prep)
    cargas = int(round(Y_pred[0]))

    # Mostrar resultado
    with col_result:
        resultado_placeholder.markdown(f"""
            <div class="result-box">
                <div class="result-label">Loads Predicted</div>
                <div class="result-value">{cargas:,}</div>
                <div class="result-error">⚠ Error del modelo: ±1.5%</div>
            </div>
        """, unsafe_allow_html=True)

    # Detalle expandible
    with st.expander('📋 Ver datos ingresados'):
        st.dataframe(
            data.T.rename(columns={0: 'Valor'}),
            use_container_width=True
        )
