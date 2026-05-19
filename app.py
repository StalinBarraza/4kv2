# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import pickle
import streamlit as st
import io
from datetime import datetime

st.set_page_config(
    page_title='Load Forecast — Complex',
    page_icon='⛏️',
    layout='wide',
    initial_sidebar_state='collapsed'
)

# ══════════════════════════════════════════════════════════════════
# CSS (Tipografía incrementada entre 30% y 40%)
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600;700&family=JetBrains+Mono:wght=300;400;500;600&display=swap');

:root {
    --bg-app:     #0F1115;
    --bg-card:    #161920;
    --bg-elev:    #1C2029;
    --bg-deep:    #0A0C10;

    --copper:     #A67C52;
    --copper-hi:  #C49770;
    --copper-dim: rgba(166,124,82,0.12);

    --green:      #6BBE83;
    --green-dim:  rgba(107,190,131,0.08);
    --red:        #C76B6B;
    --red-dim:    rgba(199,107,107,0.08);
    --amber:      #D4A857;

    --t1: #E4E7ED;
    --t2: #8B92A0;
    --t3: #545B6A;
    --t4: #2C313C;

    --b1: rgba(255,255,255,0.04);
    --b2: rgba(255,255,255,0.07);
    --b3: rgba(255,255,255,0.12);

    --sans: 'Inter', -apple-system, sans-serif;
    --mono: 'JetBrains Mono', monospace;
}

/* ── Reset ── */
.stApp { background: var(--bg-app) !important; }
html, body, [class*="css"], .stMarkdown, p, span, div {
    font-family: var(--sans) !important;
    color: var(--t1);
    -webkit-font-smoothing: antialiased;
}
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { visibility:hidden !important; display:none !important; }
.main .block-container { padding: 0 1.6rem 2rem 1.6rem !important; max-width:1800px !important; }

/* ── Header ── */
.app-header {
    display:flex; align-items:center; justify-content:space-between;
    padding: 0.9rem 0 0.8rem 0;
    border-bottom: 1px solid var(--b1);
    margin-bottom: 1rem;
}
.app-brand { display:flex; align-items:center; gap:12px; }
.app-mark {
    width:40px; height:40px;
    background: var(--bg-elev);
    border: 1px solid var(--b3);
    border-radius:4px;
    display:flex; align-items:center; justify-content:center;
    font-size:1.2rem; color:var(--copper);
}
.app-title { font-size:1.3rem !important; font-weight:600 !important; color:var(--t1) !important; letter-spacing:-0.1px; }
.app-sub   { font-size:0.85rem !important; color:var(--t3) !important; letter-spacing:1.5px; text-transform:uppercase; font-family:var(--mono) !important; margin-top:1px; }
.app-meta  { display:flex; align-items:center; gap:20px; }
.meta-pill {
    display:flex; align-items:center; gap:6px;
    font-size:0.85rem; color:var(--green); letter-spacing:1.2px; text-transform:uppercase;
    font-family:var(--mono) !important;
}
.live-dot {
    width:7px; height:7px; background:var(--green); border-radius:50%;
    box-shadow:0 0 5px var(--green); animation:blink 2.2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.meta-txt { font-family:var(--mono) !important; font-size:0.85rem !important; color:var(--t3) !important; }

/* ── Mode tabs ── */
.stRadio > div {
    display:flex !important; gap:0 !important;
    background:transparent !important; border:none !important; padding:0 !important;
    border-bottom: 1px solid var(--b1) !important;
    border-radius:0 !important; width:100% !important;
}
.stRadio > div > label {
    padding:10px 25px 11px 25px !important; border-radius:0 !important;
    font-size:0.9rem !important; font-weight:500 !important;
    letter-spacing:1.2px !important; text-transform:uppercase;
    cursor:pointer; transition:all 0.15s !important;
    color:var(--t3) !important; background:transparent !important;
    border-bottom:2px solid transparent !important;
    margin-bottom:-1px !important; font-family:var(--mono) !important;
}
.stRadio > div > label:hover { color:var(--t2) !important; }
.stRadio > div > label:has(input:checked) {
    color:var(--copper-hi) !important;
    border-bottom-color:var(--copper) !important;
}

/* ── Sidebar nav ── */
.sidebar-nav {
    background: var(--bg-card);
    border: 1px solid var(--b1);
    border-radius:6px;
    overflow:hidden;
    height:100%;
}
.sidebar-top {
    padding:16px 18px 14px 18px;
    border-bottom:1px solid var(--b1);
}
.sidebar-section-lbl {
    font-family:var(--mono) !important;
    font-size:0.75rem !important; color:var(--t3) !important;
    letter-spacing:2.5px !important; text-transform:uppercase !important;
    padding:14px 18px 8px 18px; display:block;
}
.pit-nav-item {
    display:flex; align-items:center; gap:10px;
    padding:12px 16px; cursor:pointer;
    border-left:3px solid transparent;
    transition:all 0.15s;
}
.pit-nav-item.active {
    background:rgba(166,124,82,0.08);
    border-left-color:var(--copper);
}
.pit-nav-item:hover:not(.active) {
    background:rgba(255,255,255,0.02);
    border-left-color:var(--b3);
}
.pit-nav-name { font-size:1.1rem !important; font-weight:500 !important; }
.pit-nav-item.active .pit-nav-name { color:var(--copper-hi) !important; }
.pit-nav-item:not(.active) .pit-nav-name { color:var(--t2) !important; }
.pit-nav-code { font-family:var(--mono) !important; font-size:0.75rem !important; color:var(--t3) !important; margin-top:2px; }
.pit-nav-count {
    margin-left:auto;
    font-family:var(--mono) !important; font-size:0.75rem !important;
    color:var(--t3) !important;
    background:var(--bg-elev);
    border:1px solid var(--b1);
    border-radius:3px; padding:2px 7px;
}

/* Turno toggle in sidebar */
.turno-section {
    padding:14px 18px 16px 18px;
    border-top:1px solid var(--b1);
    margin-top:auto;
}
.turno-lbl {
    font-family:var(--mono) !important;
    font-size:0.7rem !important; color:var(--t3) !important;
    letter-spacing:2.5px !important; text-transform:uppercase !important;
    margin-bottom:8px; display:block;
}

/* ── Selectbox (turno) ── */
div[data-testid="stSelectbox"] > label {
    font-size:0.75rem !important; color:var(--t3) !important;
    letter-spacing:1.8px !important; text-transform:uppercase !important;
    font-family:var(--mono) !important; margin-bottom:5px !important;
}
div[data-testid="stSelectbox"] > div > div {
    background:var(--bg-elev) !important; border:1px solid var(--b2) !important;
    border-radius:4px !important; color:var(--t1) !important;
    font-size:1.1rem !important; min-height:38px !important;
    font-family:var(--mono) !important;
}
div[data-testid="stSelectbox"] > div > div:hover { border-color:var(--copper) !important; }

/* ── Content panel ── */
.content-panel {
    background:var(--bg-card);
    border:1px solid var(--b1);
    border-radius:6px;
    overflow:hidden;
}
.content-topbar {
    display:flex; align-items:center; justify-content:space-between;
    padding:15px 22px;
    background:var(--bg-elev);
    border-bottom:1px solid var(--b1);
}
.content-pit-name { font-size:1.25rem !important; font-weight:600 !important; color:var(--t1) !important; }
.content-pit-meta { font-family:var(--mono) !important; font-size:0.8rem !important; color:var(--t3) !important; margin-top:4px; }

/* ── Nav buttons ── */
.stButton > button {
    font-family:var(--mono) !important; font-size:0.9rem !important;
    font-weight:500 !important; letter-spacing:1px !important;
    text-transform:uppercase !important; border-radius:4px !important;
    padding:8px 16px !important; transition:all 0.15s !important;
    cursor:pointer !important; width:100%;
    background:var(--bg-elev) !important; color:var(--t2) !important;
    border:1px solid var(--b2) !important;
}
.stButton > button:hover {
    border-color:var(--copper) !important; color:var(--copper-hi) !important;
    background:var(--copper-dim) !important;
}
.stButton > button:disabled {
    opacity:0.35 !important; cursor:not-allowed !important;
}

/* ── Number inputs — line style ── */
div[data-testid="stNumberInput"] { margin-bottom:0 !important; }
div[data-testid="stNumberInput"] label {
    font-size:0.72rem !important; font-weight:400 !important;
    color:var(--t3) !important; letter-spacing:1px !important;
    text-transform:uppercase !important; font-family:var(--mono) !important;
    margin-bottom:4px !important; line-height:1.2 !important;
    white-space:nowrap !important; overflow:hidden !important;
    text-overflow:ellipsis !important;
}
div[data-testid="stNumberInput"] > div { gap:0 !important; }
div[data-testid="stNumberInput"] input {
    background:transparent !important; color:var(--t1) !important;
    border:none !important;
    border-bottom:1px solid var(--b2) !important;
    border-radius:0 !important;
    font-size:1.15rem !important; font-family:var(--mono) !important;
    font-weight:500 !important;
    padding:4px 6px !important; height:34px !important;
    transition:border-color 0.15s, color 0.15s !important;
}
div[data-testid="stNumberInput"] input:hover { border-bottom-color:var(--t2) !important; }
div[data-testid="stNumberInput"] input:focus {
    border-bottom-color:var(--copper) !important;
    color:var(--copper-hi) !important; outline:none !important; box-shadow:none !important;
}
div[data-testid="stNumberInput"] button {
    background:transparent !important; border:1px solid var(--b1) !important;
    color:var(--t3) !important; height:34px !important;
    min-width:28px !important; padding:0 5px !important; border-radius:3px !important;
}
div[data-testid="stNumberInput"] button:hover { color:var(--copper) !important; border-color:var(--b2) !important; }

/* ── Equipment section inside content ── */
.eq-block {
    padding:16px 22px 14px 22px;
    border-bottom:1px solid var(--b1);
}
.eq-model-lbl {
    font-family:var(--mono) !important;
    font-size:0.72rem !important; font-weight:500 !important;
    letter-spacing:2px !important; text-transform:uppercase !important;
    margin-bottom:11px !important;
    padding-left:8px;
    border-left:2px solid;
    line-height:1;
    display:block;
}
.eq-model-lbl.pc8000 { color:#7B8FC4; border-left-color:rgba(123,143,196,0.5); }
.eq-model-lbl.pc4000 { color:#5FA8C4; border-left-color:rgba(95,168,196,0.5); }
.eq-model-lbl.ex3600 { color:#6BBEB6; border-left-color:rgba(107,190,182,0.5); }
.eq-model-lbl.be495  { color:#6BBE83; border-left-color:rgba(107,190,131,0.5); }
.eq-model-lbl.apron  { color:#C4885B; border-left-color:rgba(196,136,91,0.5); }

/* Trucks block */
.trucks-block {
    padding:14px 22px 16px 22px;
}
.trucks-lbl {
    font-family:var(--mono) !important; font-size:0.72rem !important;
    font-weight:500 !important; color:var(--t3) !important;
    letter-spacing:2px !important; text-transform:uppercase !important;
    margin-bottom:11px !important; display:block;
}

/* ── Camiones validation banner ── */
.cam-banner {
    margin:0 0 1rem 0;
    border-radius:4px; padding:12px 18px;
    display:flex; align-items:center; justify-content:space-between;
}
.cam-banner.ok   { background:var(--green-dim); border:1px solid rgba(107,190,131,0.2); border-left:3px solid var(--green); }
.cam-banner.warn { background:var(--red-dim);   border:1px solid rgba(199,107,107,0.2); border-left:3px solid var(--red); }
.cam-banner-msg  { font-size:1.0rem !important; font-weight:500 !important; }
.cam-banner.ok   .cam-banner-msg { color:var(--green) !important; }
.cam-banner.warn .cam-banner-msg { color:var(--red) !important; }
.cam-banner-sub  { font-size:0.85rem !important; font-family:var(--mono) !important; color:var(--t3) !important; margin-top:3px; }
.cam-banner-num  { font-family:var(--mono) !important; font-size:2.1rem !important; font-weight:300 !important; letter-spacing:-1px !important; }
.cam-banner.ok   .cam-banner-num { color:var(--green) !important; }
.cam-banner.warn .cam-banner-num { color:var(--red) !important; }

/* ── Hero result ── */
.hero {
    background:var(--bg-card);
    border:1px solid var(--b1);
    border-radius:6px;
    padding:2rem 2.5rem 1.8rem 2.5rem;
    position:relative; overflow:hidden;
}
.hero::before {
    content:''; position:absolute; top:0; left:0;
    width:2px; height:100%;
    background:linear-gradient(180deg, var(--copper), transparent 70%);
}
.hero-top { display: flex; justify-content: space-between; align-items: center; }
.hero-eyebrow {
    font-family:var(--mono) !important; font-size:0.75rem !important;
    color:var(--t3) !important; letter-spacing:2.5px !important; text-transform:uppercase;
}
.hero-num {
    font-family:var(--mono) !important; font-size:5.8rem !important;
    font-weight:300 !important; line-height:0.95 !important;
    letter-spacing:-3px !important; margin:0.6rem 0 0.35rem 0;
    color:var(--t3) !important;
}
.hero-num.live { color:var(--green) !important; }
.hero-unit { font-family:var(--mono) !important; font-size:0.85rem !important; color:var(--t3) !important; letter-spacing:2px !important; text-transform:uppercase; }
.hero-range { font-family:var(--mono) !important; font-size:0.9rem !important; color:var(--green) !important; margin-top:0.5rem; }
.hero-shift {
    font-family:var(--mono) !important; font-size:0.85rem !important;
    color:var(--t3) !important; background:var(--bg-elev);
    border:1px solid var(--b1); border-radius:3px; padding:4px 12px;
    letter-spacing:1.2px; text-transform:uppercase;
}
.conf-block { border-top:1px solid var(--b1); padding-top:1.1rem; margin-top:1.1rem; }
.conf-head  { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:6px; }
.conf-lbl   { font-family:var(--mono) !important; font-size:0.75rem !important; color:var(--t3) !important; letter-spacing:2px !important; text-transform:uppercase; }
.conf-val   { font-family:var(--mono) !important; font-size:1.15rem !important; font-weight:600 !important; color:var(--copper-hi) !important; }
.conf-bar-bg   { width:100%; height:4px; background:var(--bg-elev); border-radius:2px; overflow:hidden; }
.conf-bar-fill { height:100%; background:linear-gradient(90deg, var(--copper), var(--copper-hi)); border-radius:2px; }

/* ── Calc button ── */
.calc-wrap .stButton > button {
    background:linear-gradient(180deg, #B68B5E 0%, #8C6440 100%) !important;
    color:#0F1115 !important; font-family:var(--sans) !important;
    font-size:0.95rem !important; font-weight:700 !important;
    letter-spacing:1.5px !important; border:none !important;
    border-radius:4px !important; padding:16px 28px !important;
    box-shadow:0 2px 8px rgba(0,0,0,0.4) !important;
    transition:all 0.18s !important; width:100% !important;
}
.calc-wrap .stButton > button:hover {
    background:linear-gradient(180deg, #C49770 0%, #A67C52 100%) !important;
    transform:translateY(-1px) !important;
    box-shadow:0 4px 14px rgba(166,124,82,0.35) !important;
}
.calc-wrap .stButton > button:disabled {
    background:var(--bg-elev) !important; color:var(--t4) !important;
    transform:none !important; box-shadow:none !important; opacity:0.6 !important;
    border:1px solid var(--b1) !important; cursor:not-allowed !important;
}

div[data-testid="stMetric"] label {
    font-size:0.75rem !important; color:var(--t3) !important;
    letter-spacing:1.8px !important; text-transform:uppercase !important;
    font-family:var(--mono) !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-family:var(--mono) !important; color:var(--t1) !important;
    font-size:1.6rem !important; font-weight:500 !important;
}
div[data-testid="stFileUploader"] > div {
    background:var(--bg-card) !important; border:1px dashed var(--b2) !important;
    border-radius:4px !important; padding:1.4rem !important;
}
div[data-testid="stFileUploader"] > div:hover { border-color:var(--copper) !important; }
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
        'Komatsu PC8000': ['6233','6234','6247','6248'],
        'Bucyrus BE495':  ['6243','6244'],
        'Hitachi EX3600': ['6260'],
    },
    'DP5': {
        'Komatsu PC8000': ['6232','6236','6237','6238','6250'],
        'Bucyrus BE495':  ['6242'],
        'Hitachi EX3600': ['6261','6263'],
        'Apron Feeder':   ['6449','6455'],
    },
    'EC': {
        'Komatsu PC8000': ['6231','6239'],
        'Hitachi EX3600': ['6262','6268'],
        'Komatsu PC4000': ['6264','6269'],
    },
    'PRIBBENOW': {
        'Komatsu PC8000': ['6235','6245','6246'],
        'Bucyrus BE495':  ['6241'],
        'Komatsu PC4000': ['6249'],
        'Apron Feeder':   ['6457'],
    },
}

EQ_MODEL_CLASS = {
    'Komatsu PC8000': 'pc8000',
    'Komatsu PC4000': 'pc4000',
    'Hitachi EX3600': 'ex3600',
    'Bucyrus BE495':  'be495',
    'Apron Feeder':   'apron',
}

PIT_LABELS = {
    'DESCANSO':  'El Descanso',
    'DP5':       'Pit 5',
    'EC':        'El Corozo',
    'PRIBBENOW': 'Pribbenow',
}

DEFAULTS_CAM = {
    'DESCANSO': {'qty': 80.0, 'disp': 80.0, 'uso': 75.0, 'ciclo': 30.0},
    'DP5':      {'qty': 80.0, 'disp': 80.0, 'uso': 75.0, 'ciclo': 30.0},
    'EC':       {'qty': 15.0, 'disp': 80.0, 'uso': 75.0, 'ciclo': 28.0},
    'PRIBBENOW':{'qty': 68.0, 'disp': 80.0, 'uso': 75.0, 'ciclo': 26.0},
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
# CALLBACKS PARA CONTROLAR EL RE-WRITE BUG (Valores Persistentes)
# ══════════════════════════════════════════════════════════════════
def update_pala(eq):
    st.session_state[f'val_{eq}'] = st.session_state[f'ni_{eq}']

def update_qty(pit):
    st.session_state[f'val_qty_{pit}'] = st.session_state[f'ni_qty_{pit}']

def update_disp(pit):
    st.session_state[f'val_disp_{pit}'] = st.session_state[f'ni_disp_{pit}']

def update_uso(pit):
    st.session_state[f'val_uso_{pit}'] = st.session_state[f'ni_uso_{pit}']

def update_ciclo(pit):
    st.session_state[f'val_ciclo_{pit}'] = st.session_state[f'ni_ciclo_{pit}']

COL_CICLO_MAP = {
    'DESCANSO':  'TiempoCiclo_TKS_DESCANSO',
    'DP5':       'TiempoCiclo2_DP5',
    'EC':        'TiempoCiclo2_EC',
    'PRIBBENOW': 'TiempoCiclo_TKS_PRIBBENOW',
}

PITS        = list(EQUIPOS_POR_PIT.keys())
QTY_TOTAL   = 255
MODEL_ERROR = 1.5
CONFIDENCE  = 100 - MODEL_ERROR   # 98.5 %

# ══════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════
def reset_values():
    for pit, modelos in EQUIPOS_POR_PIT.items():
        for equipos in modelos.values():
            for eq in equipos:
                st.session_state[f'val_{eq}'] = 75.0
                if f'ni_{eq}' in st.session_state:
                    st.session_state[f'ni_{eq}'] = 75.0
        src = DEFAULTS_CAM[pit]
        st.session_state[f'val_qty_{pit}']   = float(src['qty'])
        st.session_state[f'val_disp_{pit}']  = float(src['disp'])
        st.session_state[f'val_uso_{pit}']   = float(src['uso'])
        st.session_state[f'val_ciclo_{pit}'] = float(src['ciclo'])
        
        if f'ni_qty_{pit}' in st.session_state: st.session_state[f'ni_qty_{pit}'] = float(src['qty'])
        if f'ni_disp_{pit}' in st.session_state: st.session_state[f'ni_disp_{pit}'] = float(src['disp'])
        if f'ni_uso_{pit}' in st.session_state: st.session_state[f'ni_uso_{pit}'] = float(src['uso'])
        if f'ni_ciclo_{pit}' in st.session_state: st.session_state[f'ni_ciclo_{pit}'] = float(src['ciclo'])

if 'initialized' not in st.session_state:
    reset_values()
    st.session_state['initialized'] = True
if 'pit_idx' not in st.session_state:
    st.session_state['pit_idx'] = 0

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
# HEADER
# ══════════════════════════════════════════════════════════════════
hoy = datetime.now().strftime('%d %b %Y · %H:%M').upper()
st.markdown(f"""
<div class="app-header">
  <div class="app-brand">
    <div class="app-mark">◆</div>
    <div>
      <div class="app-title">LOAD FORECAST · COMPLEX</div>
      <div class="app-sub">Production Engineering / Ensemble ML v2.1</div>
    </div>
  </div>
  <div class="app-meta">
    <span class="meta-txt">{hoy}</span>
    <span class="meta-txt">04 PITS</span>
    <div class="meta-pill"><span class="live-dot"></span>Online</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MODE TABS
# ══════════════════════════════════════════════════════════════════
modo = st.radio('', ['Predicción Manual', 'Carga Masiva'],
                horizontal=True, label_visibility='collapsed')


# ══════════════════════════════════════════════════════════════════
# MODO 1 — PREDICCIÓN MANUAL
# ══════════════════════════════════════════════════════════════════
if modo == 'Predicción Manual':

    st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)

    # ── Sidebar + Content + Result — 3 columnas ──────────────────
    sidebar_col, content_col, result_col = st.columns([1, 3, 1.8], gap='small')

    # ════════════════════════════
    # SIDEBAR
    # ════════════════════════════
    with sidebar_col:
        st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)

        st.markdown("""
            <div class="sidebar-top">
              <div style="font-size:0.9rem;font-weight:600;color:var(--t1);">Frentes Mineros</div>
              <div style="font-size:0.75rem;color:var(--t3);font-family:var(--mono);margin-top:2px;">
                Selecciona un pit para editar
              </div>
            </div>
            <span class="sidebar-section-lbl">Operaciones activas</span>
        """, unsafe_allow_html=True)

        for i, pit in enumerate(PITS):
            label   = PIT_LABELS[pit]
            eq_cnt  = sum(len(v) for v in EQUIPOS_POR_PIT[pit].values())
            is_active = (st.session_state['pit_idx'] == i)
            active_cls = 'active' if is_active else ''

            st.markdown(f"""
                <div class="pit-nav-item {active_cls}" id="pit-nav-{i}">
                  <div style="flex:1;min-width:0;">
                    <div class="pit-nav-name">{label}</div>
                    <div class="pit-nav-code">{pit}</div>
                  </div>
                  <span class="pit-nav-count">{eq_cnt}</span>
                </div>
            """, unsafe_allow_html=True)

            if st.button(f'›', key=f'nav_pit_{i}',
                         help=f'Ver {label}',
                         use_container_width=True):
                st.session_state['pit_idx'] = i
                st.rerun()

        st.markdown('<div class="turno-section"><span class="turno-lbl">Turno de operación</span></div>',
                    unsafe_allow_html=True)
        turno = st.selectbox('', ['D', 'N'],
                             key='turno_sel',
                             label_visibility='collapsed')

        st.markdown('<div style="padding:0 14px 12px 14px;">', unsafe_allow_html=True)
        if st.button('↺  Resetear valores', use_container_width=True):
            reset_values()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════
    # CONTENT PANEL
    # ════════════════════════════
    with content_col:
        pit_idx   = st.session_state['pit_idx']
        pit       = PITS[pit_idx]
        pit_label = PIT_LABELS[pit]
        eq_count  = sum(len(v) for v in EQUIPOS_POR_PIT[pit].values())

        st.markdown(f"""
            <div class="content-panel">
              <div class="content-topbar">
                <div>
                  <div class="content-pit-name">{pit_label}</div>
                  <div class="content-pit-meta">{pit} · {eq_count} unidades · Pit {pit_idx+1} de {len(PITS)}</div>
                </div>
              </div>
            </div>
        """, unsafe_allow_html=True)

        arr_l, arr_r, arr_sp = st.columns([0.5, 0.5, 6])
        with arr_l:
            if st.button('‹', key='prev_pit'):
                st.session_state['pit_idx'] = (pit_idx - 1) % len(PITS)
                st.rerun()
        with arr_r:
            if st.button('›', key='next_pit'):
                st.session_state['pit_idx'] = (pit_idx + 1) % len(PITS)
                st.rerun()

        st.markdown('<div style="height:0.3rem"></div>', unsafe_allow_html=True)

        # Render de inputs dinámicos con callback on_change
        for modelo_eq, equipos in EQUIPOS_POR_PIT[pit].items():
            cls = EQ_MODEL_CLASS.get(modelo_eq, 'pc8000')
            st.markdown(
                f'<div class="eq-block">'
                f'<span class="eq-model-lbl {cls}">{modelo_eq}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            eq_cols = st.columns(len(equipos))
            for ec, eq in zip(eq_cols, equipos):
                with ec:
                    st.session_state[f'ni_{eq}'] = st.session_state.get(f'val_{eq}', 75.0)
                    st.number_input(
                        f'{eq} — Util %',
                        min_value=0.0, max_value=100.0,
                        step=1.0, format='%.1f',
                        key=f'ni_{eq}',
                        on_change=update_pala,
                        args=(eq,)
                    )

        st.markdown(
            '<div class="trucks-block"><span class="trucks-lbl">Flota de Camiones</span></div>',
            unsafe_allow_html=True
        )
        tc1, tc2, tc3, tc4 = st.columns(4)
        with tc1:
            st.session_state[f'ni_qty_{pit}'] = st.session_state.get(f'val_qty_{pit}', DEFAULTS_CAM[pit]['qty'])
            st.number_input('Qty', min_value=0.0, max_value=400.0,
                                  step=1.0, format='%.1f', key=f'ni_qty_{pit}',
                                  on_change=update_qty, args=(pit,))
        with tc2:
            st.session_state[f'ni_disp_{pit}'] = st.session_state.get(f'val_disp_{pit}', DEFAULTS_CAM[pit]['disp'])
            st.number_input('Disp %', min_value=0.0, max_value=100.0,
                                   step=1.0, format='%.1f', key=f'ni_disp_{pit}',
                                   on_change=update_disp, args=(pit,))
        with tc3:
            st.session_state[f'ni_uso_{pit}'] = st.session_state.get(f'val_uso_{pit}', DEFAULTS_CAM[pit]['uso'])
            st.number_input('Uso %', min_value=0.0, max_value=100.0,
                                  step=1.0, format='%.1f', key=f'ni_uso_{pit}',
                                  on_change=update_uso, args=(pit,))
        with tc4:
            st.session_state[f'ni_ciclo_{pit}'] = st.session_state.get(f'val_ciclo_{pit}', DEFAULTS_CAM[pit]['ciclo'])
            st.number_input('Ciclo (min)', min_value=15.0, max_value=60.0,
                                    step=0.1, format='%.1f', key=f'ni_ciclo_{pit}',
                                    on_change=update_ciclo, args=(pit,))

        # Resumen inferior de camiones
        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
        st.markdown("""
            <div style="background:var(--bg-elev);border:1px solid var(--b1);border-radius:4px;
                        padding:8px 14px;display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
              <span style="font-family:var(--mono);font-size:0.75rem;color:var(--t3);
                           letter-spacing:2px;text-transform:uppercase;">Flota total por frente:</span>
        """, unsafe_allow_html=True)

        resumen_parts = []
        for p in PITS:
            qty_p = st.session_state.get(f'val_qty_{p}', DEFAULTS_CAM[p]['qty'])
            resumen_parts.append(f"<span style='font-family:var(--mono);font-size:0.8rem;color:var(--t2);'>{p}: <b>{int(qty_p)}</b></span>")
        
        st.markdown(" · ".join(resumen_parts) + "</div>", unsafe_allow_html=True)

    # ════════════════════════════
    # PANEL DE RESULTADOS (3RA COLUMNA con VALIDACIÓN)
    # ════════════════════════════
    with result_col:
        suma_camiones = sum(int(st.session_state.get(f'val_qty_{p}', DEFAULTS_CAM[p]['qty'])) for p in PITS)
        flota_invalida = (suma_camiones != QTY_TOTAL)

        st.markdown('<div class="hero">', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="hero-top">
                <span class="hero-eyebrow">Forecast de Producción</span>
                <span class="hero-shift">{st.session_state.get("turno_sel", "D")}</span>
            </div>
        ''', unsafe_allow_html=True)
        
        if flota_invalida:
            st.markdown(f'''
                <div class="cam-banner warn" style="margin-top: 1rem;">
                    <div>
                        <div class="cam-banner-msg">Bloqueo de Seguridad</div>
                        <div class="cam-banner-sub">Suma total de camiones incorrecta (Requerido: {QTY_TOTAL})</div>
                    </div>
                    <div class="cam-banner-num">{suma_camiones}</div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
                <div class="cam-banner ok" style="margin-top: 1rem;">
                    <div>
                        <div class="cam-banner-msg">Flota Validada</div>
                        <div class="cam-banner-sub">Distribución óptima del pool global</div>
                    </div>
                    <div class="cam-banner-num">{suma_camiones}</div>
                </div>
            ''', unsafe_allow_html=True)

        st.markdown('<div class="calc-wrap" style="margin-bottom: 1rem;">', unsafe_allow_html=True)
        btn_predecir = st.button('⚡ Ejecutar Predicción', use_container_width=True, disabled=flota_invalida)
        st.markdown('</div>', unsafe_allow_html=True)

        if not flota_invalida and btn_predecir:
            registro = {}
            for p in PITS:
                for mod_eq, equipos in EQUIPOS_POR_PIT[p].items():
                    for eq in equipos:
                        val_pala = st.session_state.get(f'val_{eq}', 75.0)
                        registro[f'UsodeDisp_{eq}'] = val_pala / 100.0
                
                registro[f'QtyCamiones_{p}'] = st.session_state.get(f'val_qty_{p}', DEFAULTS_CAM[p]['qty'])
                registro[f'Disponibilidad_TKS_{p}'] = st.session_state.get(f'val_disp_{p}', DEFAULTS_CAM[p]['disp']) / 100.0
                registro[f'UsodeDisp_TKS_{p}'] = st.session_state.get(f'val_uso_{p}', DEFAULTS_CAM[p]['uso']) / 100.0
                registro[COL_CICLO_MAP[p]] = st.session_state.get(f'val_ciclo_{p}', DEFAULTS_CAM[p]['ciclo'])
            
            registro['turno'] = turno
            df_input = pd.DataFrame([registro])

            try:
                res_prediccion = predecir(df_input)[0]
                lower_bound = res_prediccion * (1 - (MODEL_ERROR / 100.0))
                upper_bound = res_prediccion * (1 + (MODEL_ERROR / 100.0))

                st.markdown(f'''
                    <div class="hero-num live">{res_prediccion:.1f}</div>
                    <div class="hero-unit">K Toneladas / Turno</div>
                    <div class="hero-range">Rango esperado: {lower_bound:.1f} - {upper_bound:.1f} K Ton</div>
                ''', unsafe_allow_html=True)

                st.markdown(f'''
                    <div class="conf-block">
                        <div class="conf-head">
                            <span class="conf-lbl">Confianza del Modelo</span>
                            <span class="conf-val">{CONFIDENCE:.1f}%</span>
                        </div>
                        <div class="conf-bar-bg">
                            <div class="conf-bar-fill" style="width: {CONFIDENCE}%;"></div>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error en la inferencia del modelo: {e}")
        else:
            if flota_invalida:
                st.markdown(f'''
                    <div class="hero-num" style="color:var(--t4);">ERROR</div>
                    <div class="hero-unit">Cálculo deshabilitado</div>
                    <div style="font-family:var(--mono); font-size:0.75rem; color:var(--red); margin-top:0.8rem;">
                        Ajusta las cantidades fijas en los frentes. Faltan o sobran {abs(QTY_TOTAL - suma_camiones)} camiones en el balance.
                    </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown('''
                    <div class="hero-num">- -</div>
                    <div class="hero-unit">Listo para procesar datos</div>
                    <div style="font-family:var(--mono); font-size:0.75rem; color:var(--t3); margin-top:0.8rem;">
                        Configura los parámetros de los frentes y presiona el botón superior.
                    </div>
                ''', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MODO 2 — CARGA MASIVA (Modulo completamente Funcional)
# ══════════════════════════════════════════════════════════════════
else:
    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    st.markdown("### 📊 Procesamiento Masivo de Datos")
    st.markdown("""
        <div style="font-size:0.9rem; color:var(--t2); margin-bottom:1.5rem;">
        Sube un archivo con los frentes estructurados. El pipeline validará automáticamente que cada fila sume exactamente 
        <b>255 camiones</b> globales distribuidos entre los frentes antes de computar las estimaciones mediante el modelo.
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Cargar lote de frentes (.csv, .xlsx)", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        try:
            # Identificación de extensión para lectura de datos
            if uploaded_file.name.endswith('.csv'):
                df_bulk = pd.read_csv(uploaded_file)
            else:
                df_bulk = pd.read_excel(uploaded_file)
            
            # Variables requeridas de flota para realizar la validación por fila
            cols_camiones = ['QtyCamiones_DESCANSO', 'QtyCamiones_DP5', 'QtyCamiones_EC', 'QtyCamiones_PRIBBENOW']
            missing_cols = [c for c in cols_camiones if c not in df_bulk.columns]
            
            if missing_cols:
                st.error(f"❌ Estructura de archivo inválida. Faltan las siguientes columnas de flota: {missing_cols}")
            else:
                # Verificación analítica de camiones totales en lote
                df_bulk['Suma_Camiones'] = df_bulk[cols_camiones].fillna(0).sum(axis=1).astype(int)
                df_bulk['Flota_Valida'] = df_bulk['Suma_Camiones'] == QTY_TOTAL
                
                total_filas = len(df_bulk)
                filas_validas = int(df_bulk['Flota_Valida'].sum())
                filas_invalidas = total_filas - filas_validas
                
                # Tablero de métricas del lote
                cm1, cm2, cm3 = st.columns(3)
                with cm1:
                    st.metric("Total Registros Cargados", total_filas)
                with cm2:
                    st.metric("Registros Válidos", filas_validas)
                with cm3:
                    st.metric("Registros Rechazados (≠ 255)", filas_invalidas, 
                              delta=-filas_invalidas if filas_invalidas > 0 else None, 
                              delta_color="inverse")
                
                st.markdown('<hr style="border-color:var(--b1); margin:1.5rem 0;">', unsafe_allow_html=True)
                
                if filas_invalidas > 0:
                    st.markdown(f"""
                        <div style="background:var(--red-dim); border-left:3px solid var(--red); padding:10px 16px; border-radius:4px; margin-bottom:1rem; font-size:0.85rem;">
                        ⚠️ <b>Aviso de exclusión:</b> Se detectaron {filas_invalidas} filas cuya suma de flota no es igual a {QTY_TOTAL}. Estas filas se mantendrán en el reporte pero se marcarán como inválidas y no generarán estimaciones.
                        </div>
                    """, unsafe_allow_html=True)
                
                if filas_validas > 0:
                    # Aislamiento y procesamiento exclusivo de vectores aprobados
                    df_validas = df_bulk[df_bulk['Flota_Valida']].copy()
                    
                    # Ejecución del pipeline de ensamble en batch
                    preds = predecir(df_validas)
                    
                    # Consolidación estructurada en el DataFrame maestro
                    df_bulk['Prediccion_K_Ton'] = np.nan
                    df_bulk.loc[df_bulk['Flota_Valida'], 'Prediccion_K_Ton'] = np.round(preds, 2)
                    
                    # Generación de bandas de dispersión analítica
                    df_bulk['Rango_Min_K_Ton'] = np.nan
                    df_bulk['Rango_Max_K_Ton'] = np.nan
                    df_bulk.loc[df_bulk['Flota_Valida'], 'Rango_Min_K_Ton'] = np.round(preds * (1 - (MODEL_ERROR / 100.0)), 2)
                    df_bulk.loc[df_bulk['Flota_Valida'], 'Rango_Max_K_Ton'] = np.round(preds * (1 + (MODEL_ERROR / 100.0)), 2)
                    
                    st.markdown(f"""
                        <div style="background:var(--green-dim); border-left:3px solid var(--green); padding:10px 16px; border-radius:4px; margin-bottom:1.5rem; font-size:0.9rem; color:var(--green);">
                        ✓ Inferencia masiva ejecutada correctamente. Modelos predictivos acoplados al set de datos.
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Visualización matricial de resultados
                    st.markdown("#### Vista previa de matriz procesada")
                    st.dataframe(df_bulk, use_container_width=True)
                    
                    # Serialización y buffer de descarga
                    csv_buffer = io.StringIO()
                    df_bulk.to_csv(csv_buffer, index=False)
                    csv_data = csv_buffer.getvalue()
                    
                    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
                    st.download_button(
                        label="📥 Descargar Reporte de Forecast Consolidados (CSV)",
                        data=csv_data,
                        file_name=f"reporte_batch_forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("❌ Error de procesamiento crítico: Ningún registro del archivo cumple con la restricción balanceada de 255 camiones.")
                    
        except Exception as e:
            st.error(f"Error crítico durante el análisis estructural del archivo: {e}")
