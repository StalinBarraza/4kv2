# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import pickle
import streamlit as st
import io

st.set_page_config(page_title='Load Forecast — Complex', page_icon='⛏️', layout='wide')

st.markdown("""
<style>
    .stApp { background-color: #1A1A2E; }
    html, body, [class*="css"] { color: #E8EDF5; font-family: 'Segoe UI', sans-serif; }
    .main-title {
        font-size: 1.6rem; font-weight: 800; color: #F0A500;
        letter-spacing: 2px; text-transform: uppercase;
        border-bottom: 2px solid #F0A500; padding-bottom: 8px; margin-bottom: 16px;
    }
    .pit-header {
        background: linear-gradient(90deg, #0F3460, #16213E);
        border-left: 4px solid #F0A500; border-radius: 6px;
        padding: 6px 14px; margin: 10px 0 6px 0;
        font-size: 0.85rem; font-weight: 800;
        color: #F0A500; letter-spacing: 2px; text-transform: uppercase;
    }
    .model-badge {
        display: inline-block; padding: 2px 10px; border-radius: 20px;
        font-size: 0.68rem; font-weight: 700; letter-spacing: 0.5px;
        margin: 4px 0 3px 0; color: white;
    }
    .trucks-header {
        background-color: #3B0A20; border-radius: 4px;
        padding: 3px 10px; margin: 6px 0 4px 0;
        font-size: 0.7rem; font-weight: 700; color: #FFB3C6;
    }
    .result-box {
        background: linear-gradient(135deg, #0F3460, #1A1A2E);
        border: 2px solid #F0A500; border-radius: 12px;
        padding: 24px; text-align: center;
    }
    .result-label {
        font-size: 0.7rem; color: #8899BB;
        letter-spacing: 3px; text-transform: uppercase; margin-bottom: 4px;
    }
    .result-value { font-size: 3rem; font-weight: 900; color: #00E676; line-height: 1; }
    .result-sub { font-size: 0.7rem; color: #8899BB; margin-top: 6px; }
    .optimo-badge {
        background: #1A3A1A; border: 1px solid #2C5F2D; border-radius: 6px;
        padding: 6px 12px; font-size: 0.72rem; color: #7CFC00; margin-bottom: 8px;
    }
    .divider { border: none; border-top: 1px solid #0F3460; margin: 12px 0; }
    .stButton > button {
        font-weight: 700; font-size: 0.8rem; letter-spacing: 1px;
        text-transform: uppercase; border: none; border-radius: 6px;
        padding: 8px 16px; transition: all 0.2s; width: 100%;
    }
    div[data-testid="stNumberInput"] input {
        background-color: #0D1B33 !important; color: #E8EDF5 !important;
        border: 1px solid #1E3A5F !important; border-radius: 4px !important;
        font-size: 0.8rem !important; padding: 4px 8px !important; height: 32px !important;
    }
    div[data-testid="stNumberInput"] label { font-size: 0.65rem !important; color: #6E7A88 !important; }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MODELO
# ══════════════════════════════════════════════════════════════════
@st.cache_resource
def cargar_modelo():
    return pickle.load(open('modelo-ensamble-reg-loads-v2.1.pkl', 'rb'))

modelo_ml, variables, min_max_scaler = cargar_modelo()

# ══════════════════════════════════════════════════════════════════
# DATOS
# ══════════════════════════════════════════════════════════════════
EQUIPOS_POR_PIT = {
    'DESCANSO': {
        'Komatsu PC8000': ['6233', '6234', '6247', '6248'],
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
        'Komatsu PC8000': ['6231', '6239'],
        'Hitachi EX3600': ['6262', '6268'],
        'Komatsu PC4000': ['6264', '6269'],
    },
    'PRIBBENOW': {
        'Komatsu PC8000': ['6235', '6245', '6246'],
        'Bucyrus BE495':  ['6241'],
        'Komatsu PC4000': ['6249'],
        'Apron Feeder':   ['6457'],
    },
}

COLOR_MODELO = {
    'Komatsu PC8000': '#1E2761', 'Komatsu PC4000': '#065A82',
    'Hitachi EX3600': '#028090', 'Bucyrus BE495':  '#2C5F2D',
    'Apron Feeder':   '#FF8C00',
}

OPTIMOS_PALAS = {
    ('DESCANSO', 'Komatsu PC8000'): 0.833, ('DESCANSO', 'Bucyrus BE495'):  0.836,
    ('DESCANSO', 'Hitachi EX3600'): 0.759, ('DP5', 'Komatsu PC8000'):      0.843,
    ('DP5', 'Bucyrus BE495'):       0.810,  ('DP5', 'Hitachi EX3600'):      0.752,
    ('DP5', 'Apron Feeder'):        0.907,  ('EC', 'Komatsu PC8000'):       0.789,
    ('EC', 'Hitachi EX3600'):       0.739,  ('EC', 'Komatsu PC4000'):       0.677,
    ('PRIBBENOW', 'Komatsu PC8000'):0.810,  ('PRIBBENOW', 'Komatsu PC4000'):0.759,
    ('PRIBBENOW', 'Bucyrus BE495'): 0.799,  ('PRIBBENOW', 'Apron Feeder'):  0.902,
}

OPTIMOS_CAM = {
    'DESCANSO': {'qty': 89.7,  'disp': 0.664, 'uso': 0.834, 'ciclo': 30.62},
    'DP5':      {'qty': 81.9,  'disp': 0.925, 'uso': 0.860, 'ciclo': 32.72},
    'EC':       {'qty': 15.55, 'disp': 0.942, 'uso': 0.814, 'ciclo': 28.32},
    'PRIBBENOW':{'qty': 67.95, 'disp': 0.716, 'uso': 0.865, 'ciclo': 25.60},
}

DEFAULTS_CAM = {
    'DESCANSO': {'qty': 80.0, 'disp': 0.80, 'uso': 0.75, 'ciclo': 30.0},
    'DP5':      {'qty': 80.0, 'disp': 0.80, 'uso': 0.75, 'ciclo': 30.0},
    'EC':       {'qty': 15.0, 'disp': 0.80, 'uso': 0.75, 'ciclo': 28.0},
    'PRIBBENOW':{'qty': 68.0, 'disp': 0.80, 'uso': 0.75, 'ciclo': 26.0},
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

COL_CICLO_MAP = {
    'DESCANSO':  'TiempoCiclo_TKS_DESCANSO',
    'DP5':       'TiempoCiclo2_DP5',
    'EC':        'TiempoCiclo2_EC',
    'PRIBBENOW': 'TiempoCiclo_TKS_PRIBBENOW',
}

# ══════════════════════════════════════════════════════════════════
# SESSION STATE — fuente de verdad de todos los valores
# ══════════════════════════════════════════════════════════════════
def init_values(optimo=False):
    for pit, modelos in EQUIPOS_POR_PIT.items():
        for modelo_eq, equipos in modelos.items():
            val = OPTIMOS_PALAS.get((pit, modelo_eq), 0.75) if optimo else 0.75
            for eq in equipos:
                st.session_state[f'v_{eq}'] = float(val)
        src = OPTIMOS_CAM[pit] if optimo else DEFAULTS_CAM[pit]
        for campo in ['qty', 'disp', 'uso', 'ciclo']:
            st.session_state[f'v_{campo}_{pit}'] = float(src[campo])

if 'init' not in st.session_state:
    init_values(optimo=False)
    st.session_state['init']        = True
    st.session_state['modo_optimo'] = False

# ══════════════════════════════════════════════════════════════════
# PREDICCIÓN
# ══════════════════════════════════════════════════════════════════
def predecir(data_df):
    dp = data_df.copy()
    dp = pd.get_dummies(dp, columns=['turno'], drop_first=False, dtype=int)
    dp = dp.reindex(columns=variables, fill_value=0)
    dp[COLS_NUMERICAS] = min_max_scaler.transform(dp[COLS_NUMERICAS])
    return modelo_ml.predict(dp)

# ══════════════════════════════════════════════════════════════════
# TÍTULO Y MODO
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="main-title">⛏ Load Forecast Simulator — Complex</div>',
            unsafe_allow_html=True)

modo = st.radio('', ['📊 Predicción Manual', '📁 Carga Masiva'],
                horizontal=True, label_visibility='collapsed')
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MODO 1 — PREDICCIÓN MANUAL
# ══════════════════════════════════════════════════════════════════
if modo == '📊 Predicción Manual':

    # Controles
    c1, c2, c3, _ = st.columns([1, 1, 1, 3])
    with c1:
        turno = st.selectbox('Turno', ['D', 'N'])
    with c2:
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button('⭐ TURNO ÓPTIMO'):
            init_values(optimo=True)
            st.session_state['modo_optimo'] = True
            st.rerun()
    with c3:
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button('🔄 RESETEAR'):
            init_values(optimo=False)
            st.session_state['modo_optimo'] = False
            st.rerun()

    if st.session_state['modo_optimo']:
        st.markdown('<div class="optimo-badge">⭐ Modo Turno Óptimo activo</div>',
                    unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    vals_palas, vals_camiones = {}, {}
    PITS = list(EQUIPOS_POR_PIT.keys())

    for fila_pits in [PITS[:2], PITS[2:]]:
        pit_cols = st.columns(2)
        for col_pit, pit in zip(pit_cols, fila_pits):
            with col_pit:
                st.markdown(f'<div class="pit-header">📍 {pit}</div>',
                            unsafe_allow_html=True)

                for modelo_eq, equipos in EQUIPOS_POR_PIT[pit].items():
                    color = COLOR_MODELO.get(modelo_eq, '#555')
                    st.markdown(
                        f'<span class="model-badge" style="background:{color}">'
                        f'{modelo_eq}</span>', unsafe_allow_html=True)

                    eq_cols = st.columns(len(equipos))
                    for ec, eq in zip(eq_cols, equipos):
                        with ec:
                            # Lee siempre desde session_state como valor inicial
                            vals_palas[f'UsodeDisp_{eq}'] = st.number_input(
                                f'{eq}',
                                min_value=0.0, max_value=1.0,
                                value=st.session_state[f'v_{eq}'],
                                step=0.01, format='%.2f',
                                key=f'ni_{eq}'
                            )

                st.markdown('<div class="trucks-header">🚛 CAMIONES</div>',
                            unsafe_allow_html=True)
                t1, t2, t3, t4 = st.columns(4)
                with t1:
                    vals_camiones[f'QtyCamiones_{pit}'] = st.number_input(
                        'Qty', min_value=0.0, max_value=200.0,
                        value=st.session_state[f'v_qty_{pit}'],
                        step=1.0, format='%.1f', key=f'ni_qty_{pit}')
                with t2:
                    vals_camiones[f'Disponibilidad_TKS_{pit}'] = st.number_input(
                        'Disp', min_value=0.0, max_value=1.0,
                        value=st.session_state[f'v_disp_{pit}'],
                        step=0.01, format='%.3f', key=f'ni_disp_{pit}')
                with t3:
                    vals_camiones[f'UsodeDisp_TKS_{pit}'] = st.number_input(
                        'Uso', min_value=0.0, max_value=1.0,
                        value=st.session_state[f'v_uso_{pit}'],
                        step=0.01, format='%.3f', key=f'ni_uso_{pit}')
                with t4:
                    vals_camiones[COL_CICLO_MAP[pit]] = st.number_input(
                        'Ciclo', min_value=15.0, max_value=60.0,
                        value=st.session_state[f'v_ciclo_{pit}'],
                        step=0.1, format='%.1f', key=f'ni_ciclo_{pit}')

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

    col_btn, col_res = st.columns([1, 2])
    with col_btn:
        calcular = st.button('▶ CALCULAR PREDICCIÓN', use_container_width=True)
    with col_res:
        ph = st.empty()
        ph.markdown("""
            <div class="result-box">
                <div class="result-label">Loads Predicted</div>
                <div class="result-value" style="color:#2A3A5A">—</div>
                <div class="result-sub">Presiona Calcular</div>
            </div>""", unsafe_allow_html=True)

    if calcular:
        datos = {**vals_palas, **vals_camiones, 'turno': turno}
        data  = pd.DataFrame([datos])[COLUMNAS_ESPERADAS]
        Y_pred = predecir(data)
        cargas = int(round(Y_pred[0]))
        tag = '⭐ Turno Óptimo' if st.session_state['modo_optimo'] else '✏️ Manual'
        ph.markdown(f"""
            <div class="result-box">
                <div class="result-label">Loads Predicted</div>
                <div class="result-value">{cargas:,}</div>
                <div class="result-sub">{tag} &nbsp;|&nbsp; ⚠ Error: ±5%</div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MODO 2 — CARGA MASIVA
# ══════════════════════════════════════════════════════════════════
else:
    st.markdown('#### 1️⃣ Descarga la plantilla')
    ej = {col: 0.75 for col in COLS_NUMERICAS}
    ej.update({
        'QtyCamiones_DESCANSO': 89.7,  'Disponibilidad_TKS_DESCANSO': 0.664,
        'UsodeDisp_TKS_DESCANSO': 0.834,'TiempoCiclo_TKS_DESCANSO': 30.62,
        'QtyCamiones_DP5': 81.9,       'Disponibilidad_TKS_DP5': 0.925,
        'UsodeDisp_TKS_DP5': 0.860,    'TiempoCiclo2_DP5': 32.72,
        'QtyCamiones_EC': 15.55,        'Disponibilidad_TKS_EC': 0.942,
        'UsodeDisp_TKS_EC': 0.814,      'TiempoCiclo2_EC': 28.32,
        'QtyCamiones_PRIBBENOW': 67.95,'Disponibilidad_TKS_PRIBBENOW': 0.716,
        'UsodeDisp_TKS_PRIBBENOW': 0.865,'TiempoCiclo_TKS_PRIBBENOW': 25.60,
        'turno': 'D'
    })
    buf = io.BytesIO()
    pd.DataFrame([ej]).to_csv(buf, index=False)
    buf.seek(0)
    st.download_button('⬇ Descargar Plantilla CSV', data=buf,
                        file_name='plantilla_prediccion.csv', mime='text/csv')

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('#### 2️⃣ Carga tu archivo')
    archivo = st.file_uploader('CSV con datos', type=['csv'], label_visibility='collapsed')

    if archivo:
        try:
            df = pd.read_csv(archivo)
            faltantes = [c for c in COLUMNAS_ESPERADAS if c not in df.columns]
            if faltantes:
                st.error(f'❌ Columnas faltantes: {faltantes}')
                st.stop()
            st.success(f'✅ {len(df):,} turnos cargados')
            st.dataframe(df[COLUMNAS_ESPERADAS].head(3), use_container_width=True)

            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown('#### 3️⃣ Ejecuta la predicción')

            if st.button('▶ PREDECIR TODOS LOS TURNOS'):
                Y = predecir(df[COLUMNAS_ESPERADAS].copy())
                df['Prediccion_Cargas'] = np.round(Y).astype(int)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric('Turnos',   f"{len(df):,}")
                m2.metric('Promedio', f"{df['Prediccion_Cargas'].mean():,.0f}")
                m3.metric('Mínimo',   f"{df['Prediccion_Cargas'].min():,}")
                m4.metric('Máximo',   f"{df['Prediccion_Cargas'].max():,}")
                cols_v = ['turno','Prediccion_Cargas'] + [c for c in COLUMNAS_ESPERADAS if c != 'turno']
                st.dataframe(df[cols_v], use_container_width=True)
                buf2 = io.BytesIO()
                df.to_csv(buf2, index=False)
                buf2.seek(0)
                st.download_button('⬇ Descargar Resultados', data=buf2,
                                    file_name='predicciones.csv', mime='text/csv')
                st.caption('⚠ Error del modelo: ±1.5%')
        except Exception as e:
            st.error(f'Error: {e}')
