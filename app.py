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
# ESTILOS CSS (Compactación Máxima)
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .stApp { background-color: #1A1A2E; color: #E8EDF5; }
    .block-container { padding: 1rem 2rem !important; }
    .pit-card {
        background-color: #16213E; border: 1px solid #0F3460;
        border-radius: 5px; padding: 10px; margin-bottom: 10px;
    }
    .pit-header {
        background: #F0A500; color: #1A1A2E; font-weight: 800;
        padding: 2px 10px; border-radius: 3px; font-size: 0.9rem; margin-bottom: 8px;
    }
    .result-box {
        background: linear-gradient(135deg, #0F3460, #1A1A2E);
        border: 2px solid #00E676; border-radius: 8px;
        padding: 15px; text-align: center;
    }
    .stNumberInput label, .stSelectbox label { font-size: 0.75rem !important; margin-bottom: -5px; }
    input { height: 30px !important; font-size: 0.8rem !important; }
    div[data-testid="stExpander"] { border: none !important; background: #0F3460; border-radius: 5px; }
    hr { margin: 10px 0; border-color: #0F3460; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# LOGICA DE DATOS Y MODELO
# ══════════════════════════════════════════════════════════════════
@st.cache_resource
def cargar_modelo():
    try:
        return pickle.load(open('modelo-ensamble-reg-loads-v2.1.pkl', 'rb'))
    except: return None, None, None

modelo, variables, min_max_scaler = cargar_modelo()

EQUIPOS_POR_PIT = {
    'DESCANSO': {'Komatsu PC8000': ['6233', '6234', '6239','6247', '6248'], 'Bucyrus BE495': ['6243', '6244'], 'Hitachi EX3600': ['6260']},
    'DP5': {'Komatsu PC8000': ['6232', '6236', '6237', '6238', '6250'], 'Bucyrus BE495': ['6242'], 'Hitachi EX3600': ['6261', '6263'], 'Apron Feeder': ['6449', '6455']},
    'EC': {'Komatsu PC8000': ['6231'], 'Hitachi EX3600': ['6262'], 'Komatsu PC4000': ['6268']},
    'PRIBBENOW': {'Komatsu PC8000': ['6235', '6245', '6246', '6249'], 'Bucyrus BE495': ['6241'], 'Komatsu PC4000': ['6264', '6269'], 'Apron Feeder': ['6457']},
}

COLS_NUMERICAS = [
    'UsodeDisp_6231','UsodeDisp_6232','UsodeDisp_6233','UsodeDisp_6234','UsodeDisp_6235','UsodeDisp_6236','UsodeDisp_6237','UsodeDisp_6238','UsodeDisp_6239','UsodeDisp_6241','UsodeDisp_6242','UsodeDisp_6243','UsodeDisp_6244','UsodeDisp_6245','UsodeDisp_6246','UsodeDisp_6247','UsodeDisp_6248','UsodeDisp_6249','UsodeDisp_6250','UsodeDisp_6260','UsodeDisp_6261','UsodeDisp_6262','UsodeDisp_6263','UsodeDisp_6264','UsodeDisp_6268','UsodeDisp_6269','UsodeDisp_6449','UsodeDisp_6455','UsodeDisp_6457',
    'QtyCamiones_DESCANSO','Disponibilidad_TKS_DESCANSO','UsodeDisp_TKS_DESCANSO','TiempoCiclo_TKS_DESCANSO',
    'QtyCamiones_DP5','Disponibilidad_TKS_DP5','UsodeDisp_TKS_DP5','TiempoCiclo2_DP5',
    'QtyCamiones_EC','Disponibilidad_TKS_EC','UsodeDisp_TKS_EC','TiempoCiclo2_EC',
    'QtyCamiones_PRIBBENOW','Disponibilidad_TKS_PRIBBENOW','UsodeDisp_TKS_PRIBBENOW','TiempoCiclo_TKS_PRIBBENOW',
]

# Inicializar Session State para que los inputs se puedan actualizar desde el archivo
if 'form_data' not in st.session_state:
    st.session_state.form_data = {col: 0.75 if 'UsodeDisp' in col else 0.0 for col in COLS_NUMERICAS}
    st.session_state.form_data['turno'] = 'D'

# ══════════════════════════════════════════════════════════════════
# HEADER Y CARGA MASIVA
# ══════════════════════════════════════════════════════════════════
st.markdown('<h2 style="color:#F0A500; margin-bottom:0;">⛏ Load Forecast</h2>', unsafe_allow_html=True)

col_up1, col_up2, col_up3 = st.columns([1, 1, 2])
with col_up1:
    # Generar plantilla basada en las columnas reales del modelo
    csv_format = pd.DataFrame(columns=COLS_NUMERICAS + ['turno']).to_csv(index=False).encode('utf-8')
    st.download_button("📄 Bajar Formato", csv_format, "plantilla.csv", "text/csv")

with col_up2:
    uploaded_file = st.file_uploader("Carga Masiva (CSV)", type=['csv'], label_visibility="collapsed")

# Lógica para procesar el archivo y actualizar los campos de la pantalla
df_cargado = None
if uploaded_file is not None:
    df_cargado = pd.read_csv(uploaded_file)
    if not df_cargado.empty:
        # Tomamos la primera fila para actualizar la interfaz visual
        for col in df_cargado.columns:
            if col in st.session_state.form_data:
                st.session_state.form_data[col] = df_cargado.iloc[0][col]
        st.success(f"Cargadas {len(df_cargado)} filas. Los campos se actualizaron.")

# ══════════════════════════════════════════════════════════════════
# BARRA DE CONTROL Y RESULTADO
# ══════════════════════════════════════════════════════════════════
st.hr()
c_ctrl1, c_ctrl2, c_res = st.columns([1, 1, 2])
with c_ctrl1:
    turno = st.selectbox('TURNO', ['D', 'N'], index=0 if st.session_state.form_data['turno'] == 'D' else 1)
with c_ctrl2:
    st.write("") # Espaciador
    btn_calcular = st.button('▶ CALCULAR TODO', use_container_width=True)

with c_res:
    res_placeholder = st.empty()
    res_placeholder.markdown('<div class="result-box"><span style="color:#8899BB; font-size:0.8rem;">RESULTADO</span><br><b style="font-size:1.8rem; color:#555;">---</b></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# GRID DE ENTRADA (4 Columnas)
# ══════════════════════════════════════════════════════════════════
pit_cols = st.columns(4)
inputs_actualizados = {}

for i, (pit, modelos) in enumerate(EQUIPOS_POR_PIT.items()):
    with pit_cols[i]:
        st.markdown(f'<div class="pit-header">{pit}</div>', unsafe_allow_html=True)
        with st.container():
            # Inputs de Palas
            for m_name, eqs in modelos.items():
                st.markdown(f'<b style="font-size:0.7rem; color:#8899BB;">{m_name}</b>', unsafe_allow_html=True)
                cols_eq = st.columns(2)
                for j, eq in enumerate(eqs):
                    key_pala = f"UsodeDisp_{eq}"
                    with cols_eq[j % 2]:
                        inputs_actualizados[key_pala] = st.number_input(f"ID {eq}", 0.0, 1.0, float(st.session_state.form_data.get(key_pala, 0.75)), 0.01, key=f"in_{eq}")
            
            # Inputs de Camiones
            st.markdown('<b style="font-size:0.7rem; color:#8899BB;">TRUCKS</b>', unsafe_allow_html=True)
            tc1, tc2 = st.columns(2)
            with tc1:
                k_qty = f"QtyCamiones_{pit}"; k_uso = f"UsodeDisp_TKS_{pit}"
                inputs_actualizados[k_qty] = st.number_input("Qty", 0.0, 200.0, float(st.session_state.form_data.get(k_qty, 0.0)), 1.0, key=f"q_{pit}")
                inputs_actualizados[k_uso] = st.number_input("Uso", 0.0, 1.0, float(st.session_state.form_data.get(k_uso, 0.0)), 0.01, key=f"u_{pit}")
            with tc2:
                k_disp = f"Disponibilidad_TKS_{pit}"
                k_ciclo = ('TiempoCiclo_TKS_DESCANSO' if pit=='DESCANSO' else 'TiempoCiclo2_DP5' if pit=='DP5' else 'TiempoCiclo2_EC' if pit=='EC' else 'TiempoCiclo_TKS_PRIBBENOW')
                inputs_actualizados[k_disp] = st.number_input("Disp", 0.0, 1.0, float(st.session_state.form_data.get(k_disp, 0.0)), 0.01, key=f"d_{pit}")
                inputs_actualizados[k_ciclo] = st.number_input("Ciclo", 0.0, 60.0, float(st.session_state.form_data.get(k_ciclo, 0.0)), 0.1, key=f"c_{pit}")

# ══════════════════════════════════════════════════════════════════
# PROCESAMIENTO DE PREDICCIÓN
# ══════════════════════════════════════════════════════════════════
if btn_calcular and modelo is not None:
    # Decidir qué datos usar: ¿El archivo completo o lo que está en pantalla?
    if df_cargado is not None:
        data_to_predict = df_cargado.copy()
    else:
        # Usar los valores actuales de los inputs
        inputs_actualizados['turno'] = turno
        data_to_predict = pd.DataFrame([inputs_actualizados])

    # Preparación técnica para el modelo
    data_prep = pd.get_dummies(data_to_predict, columns=['turno'], drop_first=False).reindex(columns=variables, fill_value=0)
    data_prep[COLS_NUMERICAS] = min_max_scaler.transform(data_prep[COLS_NUMERICAS])
    
    preds = modelo.predict(data_prep)
    
    if len(preds) > 1:
        total_cargas = int(round(preds.sum()))
        res_placeholder.markdown(f'<div class="result-box"><span style="color:#8899BB; font-size:0.8rem;">TOTAL CARGAS (BATCH)</span><br><b style="font-size:1.8rem; color:#00E676;">{total_cargas:,}</b></div>', unsafe_allow_html=True)
        # Mostrar tabla de resultados para descarga
        data_to_predict['Prediccion'] = np.round(preds).astype(int)
        st.download_button("📥 Descargar Resultados Procesados", data_to_predict.to_csv(index=False).encode('utf-8'), "resultados.csv")
    else:
        carga_unica = int(round(preds[0]))
        res_placeholder.markdown(f'<div class="result-box"><span style="color:#8899BB; font-size:0.8rem;">CARGAS ESTIMADAS</span><br><b style="font-size:1.8rem; color:#00E676;">{carga_unica:,}</b></div>', unsafe_allow_html=True)
