# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import pickle
import streamlit as st

# ══════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title='Load Forecast — Compact',
    page_icon='⛏️',
    layout='wide'
)

# ══════════════════════════════════════════════════════════════════
# ESTILOS COMPACTOS
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* Fondo general */
    .stApp { background-color: #1A1A2E; }
    
    /* Reducir espacio superior de Streamlit */
    .block-container { padding-top: 2rem !important; padding-bottom: 1rem !important; }

    /* Tipografía general */
    html, body, [class*="css"] {
        color: #E8EDF5;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Título principal más compacto */
    .main-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #F0A500;
        text-transform: uppercase;
        border-bottom: 2px solid #F0A500;
        padding-bottom: 5px;
        margin-bottom: 15px;
    }

    /* Encabezado de pit super compacto */
    .pit-header {
        background: linear-gradient(90deg, #0F3460, #16213E);
        border-left: 4px solid #F0A500;
        border-radius: 4px;
        padding: 5px 10px;
        margin: 5px 0;
        font-size: 1rem;
        font-weight: 700;
        color: #F0A500;
        text-align: center;
        letter-spacing: 1px;
    }

    /* Subtítulos de sección (Palas/Camiones) */
    .section-title {
        font-size: 0.85rem;
        color: #8899BB;
        font-weight: 700;
        border-bottom: 1px solid #0F3460;
        margin-top: 10px;
        margin-bottom: 5px;
        text-transform: uppercase;
    }

    /* Encabezado de modelo miniatura */
    .model-header {
        background-color: #0F3460;
        border-radius: 3px;
        padding: 2px 8px;
        margin: 4px 0;
        font-size: 0.75rem;
        font-weight: 600;
        color: #B0C4DE;
    }

    /* Resultado compacto */
    .result-box {
        background: linear-gradient(135deg, #0F3460, #1A1A2E);
        border: 2px solid #00E676;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .result-label {
        font-size: 0.8rem;
        color: #8899BB;
        text-transform: uppercase;
    }
    .result-value {
        font-size: 2.5rem;
        font-weight: 900;
        color: #00E676;
        line-height: 1.1;
    }
    
    /* Botón compacto */
    .stButton > button {
        background-color: #F0A500;
        color: #1A1A2E;
        font-weight: 800;
        border-radius: 6px;
        width: 100%;
        height: 100%;
        min-height: 50px;
        padding: 0;
    }
    .stButton > button:hover {
        background-color: #FFC027;
    }

    /* Ajuste de Inputs */
    .stNumberInput > div > div > input, .stSelectbox > div > div {
        background-color: #0F3460 !important;
        color: #E8EDF5 !important;
        border: 1px solid #1E3A5F !important;
        font-size: 0.85rem !important;
        padding: 0.2rem !important;
    }
    
    /* Etiquetas de input más pequeñas */
    .stNumberInput label p {
        font-size: 0.75rem !important;
        color: #A0B0D0 !important;
        margin-bottom: -5px !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# CARGAR MODELO Y VARIABLES
# ══════════════════════════════════════════════════════════════════
@st.cache_resource
def cargar_modelo():
    filename = 'modelo-ensamble-reg-loads-v2.1.pkl'
    try:
        return pickle.load(open(filename, 'rb'))
    except:
        return None, None, None

modelo, variables, min_max_scaler = cargar_modelo()

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

COLOR_MODELO = {
    'Komatsu PC8000': '#1E2761', 'Komatsu PC4000': '#065A82',
    'Hitachi EX3600': '#028090', 'Bucyrus BE495': '#2C5F2D', 'Apron Feeder': '#FF8C00',
}

COLS_NUMERICAS = [
    'UsodeDisp_6231','UsodeDisp_6232','UsodeDisp_6233','UsodeDisp_6234','UsodeDisp_6235',
    'UsodeDisp_6236','UsodeDisp_6237','UsodeDisp_6238','UsodeDisp_6239','UsodeDisp_6241',
    'UsodeDisp_6242','UsodeDisp_6243','UsodeDisp_6244','UsodeDisp_6245','UsodeDisp_6246',
    'UsodeDisp_6247','UsodeDisp_6248','UsodeDisp_6249','UsodeDisp_6250','UsodeDisp_6260',
    'UsodeDisp_6261','UsodeDisp_6262','UsodeDisp_6263','UsodeDisp_6264','UsodeDisp_6268',
    'UsodeDisp_6269','UsodeDisp_6449','UsodeDisp_6455','UsodeDisp_6457',
    'QtyCamiones_DESCANSO','Disponibilidad_TKS_DESCANSO','UsodeDisp_TKS_DESCANSO','TiempoCiclo_TKS_DESCANSO',
    'QtyCamiones_DP5','Disponibilidad_TKS_DP5','UsodeDisp_TKS_DP5','TiempoCiclo2_DP5',
    'QtyCamiones_EC','Disponibilidad_TKS_EC','UsodeDisp_TKS_EC','TiempoCiclo2_EC',
    'QtyCamiones_PRIBBENOW','Disponibilidad_TKS_PRIBBENOW','UsodeDisp_TKS_PRIBBENOW','TiempoCiclo_TKS_PRIBBENOW',
]
COLUMNAS_ESPERADAS = COLS_NUMERICAS + ['turno']

# ══════════════════════════════════════════════════════════════════
# HEADER: TÍTULO Y CARGA MASIVA
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="main-title">⛏ Load Forecast Simulator</div>', unsafe_allow_html=True)

with st.expander('📂 Carga Masiva (Archivo CSV)', expanded=False):
    c1, c2 = st.columns([1,2])
    with c1:
        df_plantilla = pd.DataFrame(columns=COLUMNAS_ESPERADAS)
        st.download_button("📄 Bajar Formato", df_plantilla.to_csv(index=False).encode('utf-8'), 'plantilla.csv', 'text/csv')
    with c2:
        uploaded_file = st.file_uploader("Subir Formato Lleno", type=['csv'], label_visibility="collapsed")
        if uploaded_file is not None and modelo is not None:
            df_bulk = pd.read_csv(uploaded_file)
            data_bulk = df_bulk.copy()
            if 'turno' in data_bulk.columns:
                data_bulk = pd.get_dummies(data_bulk, columns=['turno'], drop_first=False, dtype=int)
            data_bulk = data_bulk.reindex(columns=variables, fill_value=0)
            data_bulk[COLS_NUMERICAS] = min_max_scaler.transform(data_bulk[COLS_NUMERICAS])
            df_bulk['Cargas_Predichas'] = np.round(modelo.predict(data_bulk)).astype(int)
            st.download_button("📥 Descargar Resultados", df_bulk.to_csv(index=False).encode('utf-8'), 'resultados.csv', 'text/csv')

# ══════════════════════════════════════════════════════════════════
# PANEL DE CONTROL SUPERIOR Y RESULTADO (Fijo arriba)
# ══════════════════════════════════════════════════════════════════
ctrl_col1, ctrl_col2, res_col = st.columns([1, 1, 3])

with ctrl_col1:
    turno = st.selectbox('⚙️ TURNO', ['D', 'N'])
with ctrl_col2:
    st.markdown('<div style="height:23px;"></div>', unsafe_allow_html=True) # Espaciador
    predecir = st.button('▶ CALCULAR')
with res_col:
    resultado_placeholder = st.empty()
    resultado_placeholder.markdown("""
        <div class="result-box">
            <div class="result-label">Cargas Estimadas</div>
            <div class="result-value" style="color:#555;">—</div>
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# GRID PRINCIPAL COMPACTO (4 Columnas para los Pits)
# ══════════════════════════════════════════════════════════════════
st.markdown("---")
pit_cols = st.columns(4)
vals_palas = {}
vals_camiones = {}

for idx, (pit, equipos_del_pit) in enumerate(EQUIPOS_POR_PIT.items()):
    with pit_cols[idx]:
        st.markdown(f'<div class="pit-header">{pit}</div>', unsafe_allow_html=True)
        
        # ── PALAS ──
        st.markdown('<div class="section-title">🚧 Equipos (Uso Dispo)</div>', unsafe_allow_html=True)
        for modelo_eq, equipos in equipos_del_pit.items():
            color = COLOR_MODELO.get(modelo_eq, '#555')
            st.markdown(f'<div class="model-header" style="border-left:3px solid {color}">{modelo_eq}</div>', unsafe_allow_html=True)
            
            # Agrupar de a 2 inputs por fila para ahorrar altura
            shov_cols = st.columns(2)
            for i, eq in enumerate(equipos):
                with shov_cols[i % 2]:
                    vals_palas[f'UsodeDisp_{eq}'] = st.number_input(
                        f'ID {eq}', min_value=0.0, max_value=1.0, value=0.75, step=0.01, key=f'p_{eq}'
                    )
        
        # ── CAMIONES ──
        st.markdown('<div class="section-title">🚛 Camiones</div>', unsafe_allow_html=True)
        tk_c1, tk_c2 = st.columns(2)
        with tk_c1:
            vals_camiones[f'QtyCamiones_{pit}'] = st.number_input('Qty (Q)', min_value=0.0, max_value=150.0, value=80.0, step=1.0, key=f'q_{pit}')
            vals_camiones[f'UsodeDisp_TKS_{pit}'] = st.number_input('Uso Disp.', min_value=0.0, max_value=1.0, value=0.75, step=0.01, key=f'u_{pit}')
        with tk_c2:
            vals_camiones[f'Disponibilidad_TKS_{pit}'] = st.number_input('Dispo.', min_value=0.0, max_value=1.0, value=0.80, step=0.01, key=f'd_{pit}')
            col_ciclo = (
                'TiempoCiclo_TKS_DESCANSO' if pit == 'DESCANSO' else
                'TiempoCiclo2_DP5'         if pit == 'DP5' else
                'TiempoCiclo2_EC'          if pit == 'EC' else
                'TiempoCiclo_TKS_PRIBBENOW'
            )
            vals_camiones[col_ciclo] = st.number_input('Ciclo (m)', min_value=20.0, max_value=42.0, value=30.0, step=0.1, key=f'c_{pit}')

# ══════════════════════════════════════════════════════════════════
# LÓGICA DE PREDICCIÓN AL PRESIONAR BOTÓN
# ══════════════════════════════════════════════════════════════════
if predecir and modelo is not None:
    datos = {**vals_palas, **vals_camiones, 'turno': turno}
    data = pd.DataFrame([datos])[COLUMNAS_ESPERADAS]

    data_prep = pd.get_dummies(data.copy(), columns=['turno'], drop_first=False, dtype=int)
    data_prep = data_prep.reindex(columns=variables, fill_value=0)
    data_prep[COLS_NUMERICAS] = min_max_scaler.transform(data_prep[COLS_NUMERICAS])

    cargas = int(round(modelo.predict(data_prep)[0]))

    # Actualizar el recuadro superior fijado
    resultado_placeholder.markdown(f"""
        <div class="result-box">
            <div class="result-label">Cargas Estimadas</div>
            <div class="result-value">{cargas:,}</div>
        </div>
    """, unsafe_allow_html=True)
