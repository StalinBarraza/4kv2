# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import pickle
import streamlit as st

# ══════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════════════════
st.set_page_config(page_title='Load Forecast — Compact', layout='wide')

# ══════════════════════════════════════════════════════════════════
# ESTILOS CSS (Compactación Máxima y Colores)
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .stApp { background-color: #1A1A2E; color: #E8EDF5; }
    .block-container { padding: 1rem 2rem !important; }
    .pit-header {
        background: #F0A500; color: #1A1A2E; font-weight: 800;
        padding: 2px 10px; border-radius: 3px; font-size: 0.85rem; 
        margin-bottom: 5px; text-align: center;
    }
    .result-box {
        background: linear-gradient(135deg, #0F3460, #1A1A2E);
        border: 2px solid #00E676; border-radius: 8px;
        padding: 10px; text-align: center; height: 100%;
    }
    .stNumberInput label, .stSelectbox label { font-size: 0.7rem !important; margin-bottom: -5px; color: #8899BB !important; }
    input { height: 28px !important; font-size: 0.8rem !important; padding: 0px 5px !important; }
    .stButton > button { height: 45px !important; font-weight: bold; background-color: #F0A500 !important; color: #1A1A2E !important; }
    hr { margin: 8px 0 !important; border-color: #0F3460 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# CARGA DE MODELO Y DEFINICIÓN DE COLUMNAS
# ══════════════════════════════════════════════════════════════════
@st.cache_resource
def cargar_modelo():
    try:
        return pickle.load(open('modelo-ensamble-reg-loads-v2.1.pkl', 'rb'))
    except: return None, None, None

modelo, variables, min_max_scaler = cargar_modelo()

# Columnas exactas según tu plantilla.csv
COLS_PALAS = [f'UsodeDisp_{i}' for i in [
    '6231','6232','6233','6234','6235','6236','6237','6238','6239','6241',
    '6242','6243','6244','6245','6246','6247','6248','6249','6250','6260',
    '6261','6262','6263','6264','6268','6269','6449','6455','6457'
]]

COLS_TKS = [
    'QtyCamiones_DESCANSO', 'Disponibilidad_TKS_DESCANSO', 'UsodeDisp_TKS_DESCANSO', 'TiempoCiclo_TKS_DESCANSO',
    'QtyCamiones_DP5', 'Disponibilidad_TKS_DP5', 'UsodeDisp_TKS_DP5', 'TiempoCiclo2_DP5',
    'QtyCamiones_EC', 'Disponibilidad_TKS_EC', 'UsodeDisp_TKS_EC', 'TiempoCiclo2_EC',
    'QtyCamiones_PRIBBENOW', 'Disponibilidad_TKS_PRIBBENOW', 'UsodeDisp_TKS_PRIBBENOW', 'TiempoCiclo_TKS_PRIBBENOW'
]

COLS_NUMERICAS = COLS_PALAS + COLS_TKS

EQUIPOS_POR_PIT = {
    'DESCANSO': {'Komatsu PC8000': ['6233', '6234', '6239','6247', '6248'], 'Bucyrus BE495': ['6243', '6244'], 'Hitachi EX3600': ['6260']},
    'DP5': {'Komatsu PC8000': ['6232', '6236', '6237', '6238', '6250'], 'Bucyrus BE495': ['6242'], 'Hitachi EX3600': ['6261', '6263'], 'Apron Feeder': ['6449', '6455']},
    'EC': {'Komatsu PC8000': ['6231'], 'Hitachi EX3600': ['6262'], 'Komatsu PC4000': ['6268']},
    'PRIBBENOW': {'Komatsu PC8000': ['6235', '6245', '6246', '6249'], 'Bucyrus BE495': ['6241'], 'Komatsu PC4000': ['6264', '6269'], 'Apron Feeder': ['6457']},
}

# Inicializar Session State para sincronización
if 'form_data' not in st.session_state:
    st.session_state.form_data = {col: 0.75 if 'UsodeDisp' in col else 0.0 for col in COLS_NUMERICAS}
    st.session_state.form_data['turno'] = 'D'

# ══════════════════════════════════════════════════════════════════
# HEADER Y LOGICA DE CARGA CSV
# ══════════════════════════════════════════════════════════════════
st.markdown('<h3 style="color:#F0A500; margin:0;">⛏ Operaciones Load Forecast</h3>', unsafe_allow_html=True)

c_up1, c_up2 = st.columns([1, 2])
with c_up1:
    df_template = pd.DataFrame(columns=COLS_NUMERICAS + ['turno'])
    st.download_button("📥 Bajar Plantilla", df_template.to_csv(index=False).encode('utf-8'), "plantilla.csv", "text/csv")

with c_up2:
    uploaded_file = st.file_uploader("Cargar CSV para autocompletar", type=['csv'], label_visibility="collapsed")
    if uploaded_file:
        df_load = pd.read_csv(uploaded_file)
        if not df_load.empty:
            for col in df_load.columns:
                if col in st.session_state.form_data:
                    st.session_state.form_data[col] = df_load.iloc[0][col]
            if 'turno' in df_load.columns:
                st.session_state.form_data['turno'] = df_load.iloc[0]['turno']
            st.success("✅ Campos actualizados con el archivo.")

# ══════════════════════════════════════════════════════════════════
# PANEL DE CONTROL Y RESULTADOS
# ══════════════════════════════════════════════════════════════════
st.divider()
ctrl1, ctrl2, res_panel = st.columns([1, 1, 2])

with ctrl1:
    turno_sel = st.selectbox('TURNO ACTUAL', ['D', 'N'], index=0 if st.session_state.form_data['turno'] == 'D' else 1)
with ctrl2:
    st.write("") 
    btn_calc = st.button('🚀 CALCULAR AHORA', use_container_width=True)

with res_panel:
    placeholder_res = st.empty()
    placeholder_res.markdown('<div class="result-box"><span style="color:#8899BB; font-size:0.7rem;">CARGAS ESTIMADAS</span><br><b style="font-size:1.5rem; color:#555;">---</b></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# CUERPO PRINCIPAL (GRID 4 COLUMNAS)
# ══════════════════════════════════════════════════════════════════
cols_pits = st.columns(4)
current_inputs = {}

for idx, (pit, modelos) in enumerate(EQUIPOS_POR_PIT.items()):
    with cols_pits[idx]:
        st.markdown(f'<div class="pit-header">{pit}</div>', unsafe_allow_html=True)
        
        # --- SECCIÓN PALAS ---
        for m_name, eqs in modelos.items():
            st.markdown(f'<p style="font-size:0.7rem; margin:0; color:#F0A500;"><b>{m_name}</b></p>', unsafe_allow_html=True)
            c_sh1, c_sh2 = st.columns(2)
            for j, eq in enumerate(eqs):
                key_pala = f"UsodeDisp_{eq}"
                val_init = float(st.session_state.form_data.get(key_pala, 0.75))
                with (c_sh1 if j % 2 == 0 else c_sh2):
                    current_inputs[key_pala] = st.number_input(f"ID {eq}", 0.0, 1.0, val_init, 0.01, key=f"ui_{eq}")

        # --- SECCIÓN CAMIONES (NOMBRES ESPECÍFICOS DEL CSV) ---
        st.markdown('<p style="font-size:0.7rem; margin:0; color:#00E676;"><b>CAMIONES (TKS)</b></p>', unsafe_allow_html=True)
        ctk1, ctk2 = st.columns(2)
        
        # Definir nombres de columnas según el PIT
        k_qty = f"QtyCamiones_{pit}"
        k_disp = f"Disponibilidad_TKS_{pit}"
        k_uso = f"UsodeDisp_TKS_{pit}"
        # Manejo especial del ciclo (DP5 y EC usan 'TiempoCiclo2')
        k_ciclo = f"TiempoCiclo2_{pit}" if pit in ['DP5', 'EC'] else f"TiempoCiclo_TKS_{pit}"
        
        with ctk1:
            current_inputs[k_qty] = st.number_input("Qty", 0.0, 150.0, float(st.session_state.form_data.get(k_qty, 0.0)), 1.0, key=f"ui_{k_qty}")
            current_inputs[k_uso] = st.number_input("Uso", 0.0, 1.0, float(st.session_state.form_data.get(k_uso, 0.0)), 0.01, key=f"ui_{k_uso}")
        with ctk2:
            current_inputs[k_disp] = st.number_input("Disp", 0.0, 1.0, float(st.session_state.form_data.get(k_disp, 0.0)), 0.01, key=f"ui_{k_disp}")
            current_inputs[k_ciclo] = st.number_input("Ciclo", 0.0, 60.0, float(st.session_state.form_data.get(k_ciclo, 0.0)), 0.1, key=f"ui_{k_ciclo}")

# ══════════════════════════════════════════════════════════════════
# PROCESAMIENTO DE PREDICCIÓN
# ══════════════════════════════════════════════════════════════════
if btn_calc and modelo is not None:
    current_inputs['turno'] = turno_sel
    # Asegurar que todas las columnas numéricas existan (rellenar con 0 si faltara alguna por error)
    for c in COLS_NUMERICAS:
        if c not in current_inputs: current_inputs[c] = 0.0
        
    df_pred = pd.DataFrame([current_inputs])
    
    # Preparación: One-hot encoding y reordenar según entrenamiento
    df_prep = pd.get_dummies(df_pred, columns=['turno'], drop_first=False).reindex(columns=variables, fill_value=0)
    
    # Escalamiento (Solo a las columnas numéricas que el scaler espera)
    df_prep[COLS_NUMERICAS] = min_max_scaler.transform(df_prep[COLS_NUMERICAS])
    
    # Predicción final
    prediccion = int(round(modelo.predict(df_prep)[0]))
    
    placeholder_res.markdown(f"""
        <div class="result-box">
            <span style="color:#8899BB; font-size:0.7rem;">CARGAS ESTIMADAS</span><br>
            <b style="font-size:1.8rem; color:#00E676;">{prediccion:,}</b>
        </div>
    """, unsafe_allow_html=True)
