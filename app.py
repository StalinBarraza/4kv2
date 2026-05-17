# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import pickle
import streamlit as st
import io

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
    .stApp { background-color: #1A1A2E; }
    section[data-testid="stSidebar"] { background-color: #16213E; }
    html, body, [class*="css"] { color: #E8EDF5; font-family: 'Segoe UI', sans-serif; }

    .main-title {
        font-size: 2rem; font-weight: 800; color: #F0A500;
        letter-spacing: 2px; text-transform: uppercase;
        border-bottom: 2px solid #F0A500;
        padding-bottom: 10px; margin-bottom: 20px;
    }
    .pit-header {
        background: linear-gradient(90deg, #0F3460, #16213E);
        border-left: 5px solid #F0A500;
        border-radius: 6px; padding: 10px 18px;
        margin: 18px 0 10px 0;
        font-size: 1.05rem; font-weight: 800;
        color: #F0A500; letter-spacing: 2px; text-transform: uppercase;
    }
    .model-badge {
        display: inline-block;
        padding: 3px 12px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 700;
        letter-spacing: 1px; margin-bottom: 8px;
        color: white;
    }
    .trucks-header {
        background-color: #6B1A3A;
        border-radius: 6px; padding: 6px 14px;
        margin: 10px 0 8px 0;
        font-size: 0.8rem; font-weight: 700;
        color: #FFB3C6; letter-spacing: 1px;
    }
    .result-box {
        background: linear-gradient(135deg, #0F3460, #1A1A2E);
        border: 2px solid #F0A500; border-radius: 14px;
        padding: 28px; text-align: center; margin-bottom: 16px;
    }
    .result-label {
        font-size: 0.8rem; color: #8899BB;
        letter-spacing: 3px; text-transform: uppercase; margin-bottom: 6px;
    }
    .result-value {
        font-size: 3.5rem; font-weight: 900;
        color: #00E676; line-height: 1;
    }
    .result-error { font-size: 0.75rem; color: #8899BB; margin-top: 8px; }
    .section-divider {
        border: none; border-top: 1px solid #0F3460; margin: 24px 0;
    }
    .mode-title {
        font-size: 1rem; font-weight: 700; color: #B0C4DE;
        letter-spacing: 2px; text-transform: uppercase;
        margin-bottom: 12px;
    }
    .stButton > button {
        font-weight: 800; font-size: 0.95rem;
        letter-spacing: 1px; text-transform: uppercase;
        border: none; border-radius: 8px; padding: 10px 20px;
        transition: all 0.2s; width: 100%;
    }
    .stButton > button:hover { transform: scale(1.02); }
    #MainMenu, footer, header { visibility: hidden; }
    .stSlider > label { font-size: 0.78rem !important; color: #8899BB !important; }
    div[data-testid="stHorizontalBlock"] { gap: 8px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# CARGAR MODELO
# ══════════════════════════════════════════════════════════════════
@st.cache_resource
def cargar_modelo():
    filename = 'modelo-ensamble-reg-loads-v2.1.pkl'
    return pickle.load(open(filename, 'rb'))

modelo_ml, variables, min_max_scaler = cargar_modelo()

# ══════════════════════════════════════════════════════════════════
# ESTRUCTURAS DE DATOS
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
        'Komatsu PC4000': ['6264', '6269'],  # ajusta según tus datos reales
    },
    'PRIBBENOW': {
        'Komatsu PC8000': ['6235', '6245', '6246'],
        'Bucyrus BE495':  ['6241'],
        'Komatsu PC4000': ['6249'],
        'Apron Feeder':   ['6457'],
    },
}

COLOR_MODELO = {
    'Komatsu PC8000': '#1E2761',
    'Komatsu PC4000': '#065A82',
    'Hitachi EX3600': '#028090',
    'Bucyrus BE495':  '#2C5F2D',
    'Apron Feeder':   '#FF8C00',
}

# Valores óptimos históricos por pit-modelo (de TablaResumenGoals.xlsx)
OPTIMOS = {
    # formato: (pit, modelo) -> {equipo: uso_disp}
    # Para palas: UsoDisp_media del modelo aplicado a todos sus equipos
    # Para camiones: valores del pit
    'palas': {
        ('DESCANSO', 'Komatsu PC8000'): 0.833,
        ('DESCANSO', 'Bucyrus BE495'):  0.836,
        ('DESCANSO', 'Hitachi EX3600'): 0.759,
        ('DP5', 'Dragline 6449'):        0.899,
        ('DP5', 'Dragline 6455'):        0.916,
        ('DP5', 'Hitachi EX3600'):       0.752,
        ('DP5', 'Komatsu PC8000'):       0.843,
        ('DP5', 'Bucyrus BE495'):        0.810,
        ('EC', 'Komatsu PC8000'):        0.789,
        ('EC', 'Hitachi EX3600'):        0.739,
        ('EC', 'Komatsu PC4000'):        0.677,
        ('PRIBBENOW', 'Dragline 6457'):  0.902,
        ('PRIBBENOW', 'Komatsu PC8000'): 0.810,
        ('PRIBBENOW', 'Komatsu PC4000'): 0.759,
        ('PRIBBENOW', 'Bucyrus BE495'):  0.799,
    },
    'camiones': {
        'DESCANSO': {'qty': 89.7,  'disp': 0.664, 'uso': 0.834, 'ciclo': 30.62},
        'DP5':      {'qty': 81.9,  'disp': 0.925, 'uso': 0.860, 'ciclo': 32.72},
        'EC':       {'qty': 15.55, 'disp': 0.942, 'uso': 0.814, 'ciclo': 28.32},
        'PRIBBENOW':{'qty': 67.95, 'disp': 0.716, 'uso': 0.865, 'ciclo': 25.60},
    }
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
# FUNCIÓN DE PREDICCIÓN
# ══════════════════════════════════════════════════════════════════
def predecir(data_df):
    data_prep = data_df.copy()
    data_prep = pd.get_dummies(data_prep, columns=['turno'], drop_first=False, dtype=int)
    data_prep = data_prep.reindex(columns=variables, fill_value=0)
    data_prep[COLS_NUMERICAS] = min_max_scaler.transform(data_prep[COLS_NUMERICAS])
    return modelo_ml.predict(data_prep)

# ══════════════════════════════════════════════════════════════════
# ESTADO DE SESIÓN para turno óptimo
# ══════════════════════════════════════════════════════════════════
if 'usar_optimo' not in st.session_state:
    st.session_state.usar_optimo = False

# ══════════════════════════════════════════════════════════════════
# TÍTULO Y MODO
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="main-title">⛏ Load Forecast Simulator — Complex</div>',
            unsafe_allow_html=True)

modo = st.radio('', ['📊 Predicción Manual', '📁 Carga Masiva'],
                horizontal=True, label_visibility='collapsed')

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MODO 1: PREDICCIÓN MANUAL
# ══════════════════════════════════════════════════════════════════
if modo == '📊 Predicción Manual':

    # ── Controles superiores ─────────────────────────────────────
    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1, 1, 1, 2])
    with ctrl1:
        turno = st.selectbox('⚙️ Turno', ['D', 'N'])
    with ctrl2:
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button('⭐ TURNO ÓPTIMO'):
            st.session_state.usar_optimo = True
    with ctrl3:
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button('🔄 RESETEAR'):
            st.session_state.usar_optimo = False
            st.rerun()

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Helper para valor inicial de slider ──────────────────────
    def val_pala(pit, modelo_eq, eq):
        if st.session_state.usar_optimo:
            key = (pit, modelo_eq)
            # Apron Feeder usa nombre de dragline en los óptimos
            if modelo_eq == 'Apron Feeder':
                if eq in ['6449']: key = (pit, 'Dragline 6449')
                elif eq in ['6455']: key = (pit, 'Dragline 6455')
                elif eq in ['6457']: key = (pit, 'Dragline 6457')
            return float(OPTIMOS['palas'].get(key, 0.75))
        return 0.75

    def val_cam(pit, campo):
        if st.session_state.usar_optimo:
            return float(OPTIMOS['camiones'][pit][campo])
        defaults = {'qty': 80.0, 'disp': 0.80, 'uso': 0.75, 'ciclo': 30.0}
        return defaults[campo]

    # ── 4 pits en página única ───────────────────────────────────
    vals_palas    = {}
    vals_camiones = {}

    PITS = list(EQUIPOS_POR_PIT.keys())

    # Dos filas de dos pits cada una
    for fila_pits in [PITS[:2], PITS[2:]]:
        cols_pit = st.columns(2)
        for col_pit, pit in zip(cols_pit, fila_pits):
            with col_pit:
                st.markdown(f'<div class="pit-header">📍 {pit}</div>',
                            unsafe_allow_html=True)

                # Palas por modelo
                for modelo_eq, equipos in EQUIPOS_POR_PIT[pit].items():
                    color = COLOR_MODELO.get(modelo_eq, '#555')
                    st.markdown(
                        f'<span class="model-badge" style="background:{color}">'
                        f'{modelo_eq}</span>',
                        unsafe_allow_html=True
                    )
                    eq_cols = st.columns(len(equipos))
                    for ec, eq in zip(eq_cols, equipos):
                        with ec:
                            vals_palas[f'UsodeDisp_{eq}'] = st.slider(
                                f'Uso {eq}',
                                min_value=0.0, max_value=1.0,
                                value=val_pala(pit, modelo_eq, eq),
                                step=0.01, key=f'pala_{eq}'
                            )

                # Camiones
                st.markdown('<div class="trucks-header">🚛 CAMIONES</div>',
                            unsafe_allow_html=True)
                cc1, cc2, cc3, cc4 = st.columns(4)
                with cc1:
                    vals_camiones[f'QtyCamiones_{pit}'] = st.slider(
                        'Qty', min_value=0.0, max_value=150.0,
                        value=val_cam(pit, 'qty'), step=1.0,
                        key=f'qty_{pit}'
                    )
                with cc2:
                    vals_camiones[f'Disponibilidad_TKS_{pit}'] = st.slider(
                        'Disp', min_value=0.0, max_value=1.0,
                        value=val_cam(pit, 'disp'), step=0.01,
                        key=f'disp_{pit}'
                    )
                with cc3:
                    vals_camiones[f'UsodeDisp_TKS_{pit}'] = st.slider(
                        'Uso', min_value=0.0, max_value=1.0,
                        value=val_cam(pit, 'uso'), step=0.01,
                        key=f'uso_{pit}'
                    )
                with cc4:
                    vals_camiones[COL_CICLO_MAP[pit]] = st.slider(
                        'Ciclo (min)', min_value=20.0, max_value=42.0,
                        value=val_cam(pit, 'ciclo'), step=0.1,
                        key=f'ciclo_{pit}'
                    )

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Botón predecir y resultado ───────────────────────────────
    col_btn, col_res = st.columns([1, 2])
    with col_btn:
        predecir_btn = st.button('▶ CALCULAR PREDICCIÓN',
                                  use_container_width=True)

    with col_res:
        res_placeholder = st.empty()
        res_placeholder.markdown("""
            <div class="result-box">
                <div class="result-label">Loads Predicted</div>
                <div class="result-value" style="color:#2A3A5A">—</div>
                <div class="result-error">Presiona Calcular para obtener la predicción</div>
            </div>
        """, unsafe_allow_html=True)

    if predecir_btn:
        datos = {**vals_palas, **vals_camiones, 'turno': turno}
        data  = pd.DataFrame([datos])[COLUMNAS_ESPERADAS]
        Y_pred = predecir(data)
        cargas = int(round(Y_pred[0]))

        res_placeholder.markdown(f"""
            <div class="result-box">
                <div class="result-label">Loads Predicted</div>
                <div class="result-value">{cargas:,}</div>
                <div class="result-error">⚠ Error del modelo: ±1.5%</div>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.usar_optimo:
            st.info('⭐ Resultado calculado con valores del Turno Óptimo histórico.')

# ══════════════════════════════════════════════════════════════════
# MODO 2: CARGA MASIVA
# ══════════════════════════════════════════════════════════════════
else:
    st.markdown('<div class="mode-title">📁 Carga Masiva de Turnos</div>',
                unsafe_allow_html=True)

    # ── Descargar plantilla ──────────────────────────────────────
    st.markdown('#### 1️⃣ Descarga la plantilla')
    plantilla_df = pd.DataFrame(columns=COLUMNAS_ESPERADAS)

    # Agregar fila de ejemplo con valores típicos
    ejemplo = {col: 0.75 for col in COLS_NUMERICAS}
    ejemplo.update({
        'QtyCamiones_DESCANSO': 89.7,  'Disponibilidad_TKS_DESCANSO': 0.664,
        'UsodeDisp_TKS_DESCANSO': 0.834, 'TiempoCiclo_TKS_DESCANSO': 30.62,
        'QtyCamiones_DP5': 81.9,        'Disponibilidad_TKS_DP5': 0.925,
        'UsodeDisp_TKS_DP5': 0.860,     'TiempoCiclo2_DP5': 32.72,
        'QtyCamiones_EC': 15.55,         'Disponibilidad_TKS_EC': 0.942,
        'UsodeDisp_TKS_EC': 0.814,       'TiempoCiclo2_EC': 28.32,
        'QtyCamiones_PRIBBENOW': 67.95, 'Disponibilidad_TKS_PRIBBENOW': 0.716,
        'UsodeDisp_TKS_PRIBBENOW': 0.865,'TiempoCiclo_TKS_PRIBBENOW': 25.60,
        'turno': 'D'
    })
    plantilla_df = pd.DataFrame([ejemplo])

    buffer = io.BytesIO()
    plantilla_df.to_csv(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label='⬇ Descargar Plantilla CSV',
        data=buffer,
        file_name='plantilla_prediccion.csv',
        mime='text/csv',
        use_container_width=False
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Cargar archivo ───────────────────────────────────────────
    st.markdown('#### 2️⃣ Carga tu archivo con los datos')
    archivo = st.file_uploader('Selecciona el archivo CSV',
                                type=['csv'], label_visibility='collapsed')

    if archivo is not None:
        try:
            df_cargado = pd.read_csv(archivo)
            st.success(f'✅ Archivo cargado: {len(df_cargado)} filas detectadas')

            # Verificar columnas
            faltantes = [c for c in COLUMNAS_ESPERADAS if c not in df_cargado.columns]
            if faltantes:
                st.error(f'❌ Columnas faltantes: {faltantes}')
                st.stop()

            st.markdown('**Vista previa:**')
            st.dataframe(df_cargado[COLUMNAS_ESPERADAS].head(5),
                         use_container_width=True)

            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            st.markdown('#### 3️⃣ Ejecuta la predicción')

            if st.button('▶ PREDECIR TODOS LOS TURNOS', use_container_width=False):
                data_pred = df_cargado[COLUMNAS_ESPERADAS].copy()
                Y_pred = predecir(data_pred)
                df_resultado = df_cargado.copy()
                df_resultado['Prediccion_Cargas'] = np.round(Y_pred).astype(int)

                # Métricas resumen
                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric('Total Turnos',    f"{len(df_resultado):,}")
                m2.metric('Cargas Promedio', f"{df_resultado['Prediccion_Cargas'].mean():,.0f}")
                m3.metric('Cargas Mínimas',  f"{df_resultado['Prediccion_Cargas'].min():,}")
                m4.metric('Cargas Máximas',  f"{df_resultado['Prediccion_Cargas'].max():,}")

                st.markdown('**Resultados completos:**')
                st.dataframe(df_resultado[['turno', 'Prediccion_Cargas'] +
                             [c for c in COLUMNAS_ESPERADAS if c != 'turno']],
                             use_container_width=True)

                # Descargar resultados
                buf_out = io.BytesIO()
                df_resultado.to_csv(buf_out, index=False)
                buf_out.seek(0)
                st.download_button(
                    label='⬇ Descargar Resultados CSV',
                    data=buf_out,
                    file_name='predicciones_resultado.csv',
                    mime='text/csv'
                )
                st.caption('⚠ Error del modelo: ±1.5%')

        except Exception as e:
            st.error(f'Error al procesar el archivo: {e}')
