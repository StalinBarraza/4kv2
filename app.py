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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

:root {
    --red:        #C8102E;
    --red-hi:     #E8253F;
    --red-dim:    rgba(200,16,46,0.14);
    --red-glow:   rgba(200,16,46,0.25);
    --bg-app:     #0E0F11;
    --bg-card:    #161719;
    --bg-elev:    #1E2024;
    --bg-deep:    #09090B;
    --gold:       #C89B3C;
    --gold-hi:    #E8BA52;
    --gold-dim:   rgba(200,155,60,0.14);
    --green:      #3DD68C;
    --green-dim:  rgba(61,214,140,0.10);
    --warn:       #E05C5C;
    --warn-dim:   rgba(224,92,92,0.10);
    --t1: #F4F5F7;
    --t2: #9BA3B0;
    --t3: #5C6470;
    --t4: #30353E;
    --b1: rgba(255,255,255,0.05);
    --b2: rgba(255,255,255,0.09);
    --b3: rgba(255,255,255,0.16);
    --bred: rgba(200,16,46,0.20);
    --sans: 'Inter', -apple-system, sans-serif;
    --mono: 'JetBrains Mono', monospace;
    font-size: 15px;
}

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
.main .block-container { padding: 0 1.8rem 2rem 1.8rem !important; max-width:1800px !important; }

.app-header {
    display:flex; align-items:center; justify-content:space-between;
    padding: 0.9rem 0 0.8rem 0;
    border-bottom: 2px solid var(--red);
    margin-bottom: 1.1rem;
}
.app-brand { display:flex; align-items:center; gap:14px; }
.app-mark {
    width:38px; height:38px;
    background: var(--red);
    border-radius:4px;
    display:flex; align-items:center; justify-content:center;
    font-size:1.1rem; color:#fff; font-weight:700;
    box-shadow: 0 2px 12px var(--red-glow);
}
.app-title { font-size:1.15rem !important; font-weight:700 !important; color:var(--t1) !important; letter-spacing:-0.2px; }
.app-sub   { font-size:0.75rem !important; color:var(--t3) !important; letter-spacing:1.8px; text-transform:uppercase; font-family:var(--mono) !important; margin-top:3px; }
.app-meta  { display:flex; align-items:center; gap:22px; }
.meta-pill {
    display:flex; align-items:center; gap:7px;
    font-size:0.75rem; color:var(--green); letter-spacing:1.2px; text-transform:uppercase;
    font-family:var(--mono) !important; font-weight:600;
}
.live-dot {
    width:7px; height:7px; background:var(--green); border-radius:50%;
    box-shadow:0 0 8px var(--green); animation:blink 2.2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.meta-txt { font-family:var(--mono) !important; font-size:0.8rem !important; color:var(--t2) !important; }

.stRadio > div {
    display:flex !important; gap:0 !important;
    background:transparent !important; border:none !important; padding:0 !important;
    border-bottom: 1px solid var(--b2) !important;
    border-radius:0 !important; width:100% !important;
}
.stRadio > div > label {
    padding:10px 26px 11px 26px !important; border-radius:0 !important;
    font-size:0.82rem !important; font-weight:600 !important;
    letter-spacing:1.5px !important; text-transform:uppercase;
    cursor:pointer; transition:all 0.15s !important;
    color:var(--t3) !important; background:transparent !important;
    border-bottom:2px solid transparent !important;
    margin-bottom:-1px !important; font-family:var(--mono) !important;
}
.stRadio > div > label:hover { color:var(--t2) !important; }
.stRadio > div > label:has(input:checked) {
    color:var(--red-hi) !important;
    border-bottom-color:var(--red) !important;
}

.sidebar-nav {
    background: var(--bg-card);
    border: 1px solid var(--b2);
    border-top: 2px solid var(--red);
    border-radius:6px;
    overflow:hidden;
    height:100%;
}
.sidebar-top {
    padding:15px 17px 12px 17px;
    border-bottom:1px solid var(--b2);
    background: var(--bg-elev);
}
.sidebar-section-lbl {
    font-family:var(--mono) !important;
    font-size:0.68rem !important; color:var(--t3) !important;
    letter-spacing:2.5px !important; text-transform:uppercase !important;
    padding:11px 17px 6px 17px; display:block;
}
.turno-section {
    padding:12px 15px 14px 15px;
    border-top:1px solid var(--b2);
}
.turno-lbl {
    font-family:var(--mono) !important;
    font-size:0.7rem !important; color:var(--t3) !important;
    letter-spacing:2px !important; text-transform:uppercase !important;
    margin-bottom:7px; display:block;
}

div[data-testid="stSelectbox"] > label {
    font-size:0.75rem !important; color:var(--t2) !important;
    letter-spacing:1.2px !important; text-transform:uppercase !important;
    font-family:var(--mono) !important; margin-bottom:5px !important;
}
div[data-testid="stSelectbox"] > div > div {
    background:var(--bg-elev) !important; border:1px solid var(--b2) !important;
    border-radius:4px !important; color:var(--t1) !important;
    font-size:0.95rem !important; min-height:36px !important;
    font-family:var(--mono) !important;
}
div[data-testid="stSelectbox"] > div > div:hover { border-color:var(--red) !important; }

.content-panel {
    background:var(--bg-card);
    border:1px solid var(--b2);
    border-radius:6px;
    overflow:hidden;
}

.stButton > button {
    font-family:var(--mono) !important; font-size:0.8rem !important;
    font-weight:600 !important; letter-spacing:0.8px !important;
    text-transform:uppercase !important; border-radius:4px !important;
    padding:8px 14px !important; transition:all 0.15s !important;
    cursor:pointer !important; width:100%;
    background:var(--bg-elev) !important; color:var(--t2) !important;
    border:1px solid var(--b2) !important;
}
.stButton > button:hover {
    border-color:var(--red) !important; color:var(--red-hi) !important;
    background:var(--red-dim) !important;
}
.stButton > button:disabled { opacity:0.35 !important; cursor:not-allowed !important; }

div[data-testid="stNumberInput"] { margin-bottom:2px !important; }
div[data-testid="stNumberInput"] label {
    font-size:0.76rem !important; font-weight:500 !important;
    color:var(--t2) !important; letter-spacing:0.5px !important;
    text-transform:uppercase !important; font-family:var(--mono) !important;
    margin-bottom:3px !important; line-height:1.3 !important;
}
div[data-testid="stNumberInput"] > div { gap:0 !important; }
div[data-testid="stNumberInput"] input {
    background:var(--bg-elev) !important; color:var(--t1) !important;
    border:1px solid var(--b2) !important; border-radius:4px !important;
    font-size:1.05rem !important; font-family:var(--mono) !important;
    font-weight:600 !important; padding:5px 8px !important; height:36px !important;
    transition:all 0.15s !important;
}
div[data-testid="stNumberInput"] input:hover { border-color:var(--t3) !important; }
div[data-testid="stNumberInput"] input:focus {
    border-color:var(--red) !important; color:var(--red-hi) !important;
    outline:none !important; box-shadow:0 0 0 2px var(--red-dim) !important;
    background:var(--bg-elev) !important;
}
div[data-testid="stNumberInput"] button {
    background:var(--bg-elev) !important; border:1px solid var(--b2) !important;
    color:var(--t2) !important; height:36px !important;
    min-width:28px !important; padding:0 6px !important; border-radius:4px !important;
}
div[data-testid="stNumberInput"] button:hover {
    color:var(--red-hi) !important; border-color:var(--red) !important;
    background:var(--red-dim) !important;
}

.trucks-block {
    padding:13px 19px 15px 19px;
    background: rgba(200,16,46,0.04);
    border-top: 1px solid var(--bred);
}
.trucks-lbl {
    font-family:var(--mono) !important; font-size:0.76rem !important;
    font-weight:700 !important; color:var(--red-hi) !important;
    letter-spacing:2px !important; text-transform:uppercase !important;
    margin-bottom:12px !important; display:block;
}

.cam-banner {
    margin:0 0 0.8rem 0; border-radius:5px; padding:13px 17px;
    display:flex; align-items:center; justify-content:space-between;
}
.cam-banner.ok   { background:var(--green-dim); border:1px solid rgba(61,214,140,0.28); border-left:4px solid var(--green); }
.cam-banner.warn { background:var(--warn-dim);  border:1px solid rgba(200,16,46,0.28);  border-left:4px solid var(--red); }
.cam-banner-msg  { font-size:0.95rem !important; font-weight:700 !important; }
.cam-banner.ok   .cam-banner-msg { color:var(--green) !important; }
.cam-banner.warn .cam-banner-msg { color:var(--red-hi) !important; }
.cam-banner-sub  { font-size:0.78rem !important; font-family:var(--mono) !important; color:var(--t2) !important; margin-top:4px; }
.cam-banner-num  { font-family:var(--mono) !important; font-size:2.2rem !important; font-weight:300 !important; letter-spacing:-2px !important; }
.cam-banner.ok   .cam-banner-num { color:var(--green) !important; }
.cam-banner.warn .cam-banner-num { color:var(--red-hi) !important; }
.cam-banner-delta { font-family:var(--mono) !important; font-size:0.75rem !important; font-weight:600; }
.cam-banner.ok   .cam-banner-delta { color:var(--green) !important; }
.cam-banner.warn .cam-banner-delta { color:var(--red-hi) !important; }

.hero {
    background: linear-gradient(145deg, #161719 0%, #1E2024 100%);
    border:1px solid var(--b2);
    border-top: 2px solid var(--red);
    border-radius:6px;
    padding:1.5rem 1.8rem 1.4rem 1.8rem;
    position:relative; overflow:hidden;
}
.hero::before {
    content:''; position:absolute; top:0; left:0;
    width:100%; height:2px;
    background:linear-gradient(90deg, var(--red), var(--red-hi) 40%, transparent);
}
.hero::after {
    content:''; position:absolute; top:-20px; right:-20px;
    width:140px; height:140px;
    background:radial-gradient(circle, rgba(200,16,46,0.10) 0%, transparent 70%);
}
.hero-top { display:flex; justify-content:space-between; align-items:flex-start; }
.hero-eyebrow {
    font-family:var(--mono) !important; font-size:0.72rem !important;
    color:var(--red) !important; letter-spacing:2.5px !important;
    text-transform:uppercase; font-weight:700;
}
.hero-num {
    font-family:var(--mono) !important; font-size:4.6rem !important;
    font-weight:200 !important; line-height:0.9 !important;
    letter-spacing:-4px !important; margin:0.5rem 0 0.3rem 0;
    color:var(--t3) !important;
}
.hero-num.live { color:#fff !important; text-shadow: 0 0 40px rgba(200,16,46,0.4); }
.hero-unit { font-family:var(--mono) !important; font-size:0.78rem !important; color:var(--t3) !important; letter-spacing:2px !important; text-transform:uppercase; }
.hero-range { font-family:var(--mono) !important; font-size:0.82rem !important; color:var(--green) !important; margin-top:0.4rem; font-weight:500; }
.hero-shift {
    font-family:var(--mono) !important; font-size:0.75rem !important;
    color:#fff !important; background:var(--red);
    border-radius:4px; padding:5px 13px;
    letter-spacing:1.5px; text-transform:uppercase; font-weight:700;
    box-shadow: 0 2px 8px var(--red-glow);
}
.conf-block { border-top:1px solid var(--b2); padding-top:1rem; margin-top:1rem; }
.conf-head  { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:8px; }
.conf-lbl   { font-family:var(--mono) !important; font-size:0.72rem !important; color:var(--t3) !important; letter-spacing:2px !important; text-transform:uppercase; }
.conf-val   { font-family:var(--mono) !important; font-size:1rem !important; font-weight:700 !important; color:var(--gold-hi) !important; }
.conf-bar-bg   { width:100%; height:4px; background:var(--bg-elev); border-radius:2px; overflow:hidden; }
.conf-bar-fill { height:100%; background:linear-gradient(90deg, var(--red), var(--gold-hi)); border-radius:2px; }
.conf-foot { display:flex; justify-content:space-between; margin-top:7px;
    font-family:var(--mono) !important; font-size:0.72rem !important; color:var(--t3) !important; }

.calc-wrap .stButton > button {
    background:linear-gradient(180deg, var(--red-hi) 0%, var(--red) 100%) !important;
    color:#fff !important; font-family:var(--sans) !important;
    font-size:0.9rem !important; font-weight:800 !important;
    letter-spacing:2px !important; border:none !important;
    border-radius:5px !important; padding:14px 20px !important;
    box-shadow:0 4px 18px var(--red-glow) !important;
    transition:all 0.18s !important; width:100% !important;
    text-transform:uppercase !important;
}
.calc-wrap .stButton > button:hover {
    background:linear-gradient(180deg, #FF3050 0%, var(--red-hi) 100%) !important;
    transform:translateY(-2px) !important;
    box-shadow:0 6px 24px rgba(200,16,46,0.50) !important;
}
.calc-wrap .stButton > button:disabled {
    background:var(--bg-elev) !important; color:var(--t3) !important;
    transform:none !important; box-shadow:none !important; opacity:1 !important;
    border:1px solid var(--b2) !important; cursor:not-allowed !important;
    font-size:0.85rem !important;
}

div[data-testid="stDownloadButton"] > button {
    background:transparent !important; color:var(--red-hi) !important;
    border:1px solid var(--bred) !important;
    font-family:var(--mono) !important; font-size:0.8rem !important;
    letter-spacing:1px !important; text-transform:uppercase !important;
    border-radius:4px !important; padding:9px 18px !important; width:auto !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background:var(--red-dim) !important; border-color:var(--red) !important;
}
div[data-testid="stFileUploader"] > div {
    background:var(--bg-card) !important; border:1px dashed var(--b2) !important;
    border-radius:5px !important; padding:1.6rem !important;
}
div[data-testid="stFileUploader"] > div:hover { border-color:var(--red) !important; }
div[data-testid="stDataFrame"] { border-radius:5px !important; border:1px solid var(--b2) !important; }
div[data-testid="stMetric"] {
    background:var(--bg-card) !important; border:1px solid var(--b2) !important;
    border-left:3px solid var(--red) !important; border-radius:5px !important;
    padding:0.9rem 1.1rem !important;
}
div[data-testid="stMetric"] label {
    font-size:0.72rem !important; color:var(--t2) !important;
    letter-spacing:1.5px !important; text-transform:uppercase !important;
    font-family:var(--mono) !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-family:var(--mono) !important; color:var(--t1) !important;
    font-size:1.6rem !important; font-weight:600 !important;
}
div[data-testid="stAlert"] { border-radius:5px !important; font-size:0.9rem !important; }
div[data-testid="stCaptionContainer"] { color:var(--t2) !important; font-size:0.76rem !important; font-family:var(--mono) !important; }
hr { border:none !important; border-top:1px solid var(--b2) !important; margin:0.9rem 0 !important; }
div[data-testid="stHorizontalBlock"] { gap:0.8rem; }

.step-lbl {
    display:flex; align-items:center; gap:10px;
    font-family:var(--mono) !important; font-size:0.82rem !important;
    color:var(--t1) !important; letter-spacing:1px !important;
    text-transform:uppercase !important; margin:1.1rem 0 0.6rem 0; font-weight:600;
}
.step-num {
    width:26px; height:26px; border:2px solid var(--red);
    color:#fff; border-radius:50%;
    display:inline-flex; align-items:center; justify-content:center;
    font-size:0.75rem; font-weight:700; flex-shrink:0;
    background:var(--red);
    box-shadow: 0 2px 8px var(--red-glow);
}

::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:var(--bg-deep); }
::-webkit-scrollbar-thumb { background:var(--red-dim); border-radius:2px; }
::-webkit-scrollbar-thumb:hover { background:var(--bred); }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# MODEL
# ══════════════════════════════════════════════════════════════════
@st.cache_resource
def load_model():
    return pickle.load(open('modelo-ensamble-reg-loads-v2.1.pkl', 'rb'))

modelo_ml, variables, min_max_scaler = load_model()

# ══════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════
EQUIPOS_POR_PIT = {
    'DESCANSO': {
        'Komatsu PC8000': ['6233','6234','6247','6248', '6239'],
        'Bucyrus BE495':  ['6243','6244'],
        'Hitachi EX3600': ['6260'],
    },
    'DP5': {
        'Komatsu PC8000': ['6232','6236','6237','6238','6250'],
        'Bucyrus BE495':  ['6242'],
        'Hitachi EX3600': ['6261','6263'],
        'Dragline':       ['6449','6455'],
    },
    'EC': {
        'Komatsu PC8000': ['6231'],
        'Hitachi EX3600': ['6262'],
        'Komatsu PC4000': ['6268'],
    },
    'PRIBBENOW': {
        'Komatsu PC8000': ['6235','6245','6246', '6249'],
        'Bucyrus BE495':  ['6241'],
        'Komatsu PC4000': ['6264', '6269'],
        'Dragline':       ['6457'],
    },
}

EQ_MODEL_CLASS = {
    'Komatsu PC8000': 'pc8000',
    'Komatsu PC4000': 'pc4000',
    'Hitachi EX3600': 'ex3600',
    'Bucyrus BE495':  'be495',
    'Dragline':       'apron',
}

PIT_LABELS = {
    'DESCANSO':  'El Descanso',
    'DP5':       'Pit 5',
    'EC':        'El Corozo',
    'PRIBBENOW': 'Pribbenow',
}

DEFAULTS_CAM = {
    'DESCANSO': {'qty': 92.0, 'disp': 85.0, 'uso': 87.0, 'ciclo': 29.0},
    'DP5':      {'qty': 80.0, 'disp': 85.0, 'uso': 87.0, 'ciclo': 31.0},
    'EC':       {'qty': 15.0, 'disp': 85.0, 'uso': 87.0, 'ciclo': 23.0},
    'PRIBBENOW':{'qty': 68.0, 'disp': 85.0, 'uso': 87.0, 'ciclo': 25.0},
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

PITS      = list(EQUIPOS_POR_PIT.keys())
QTY_TOTAL = 255

# Pit colors — Drummond brand palette (red + grays)
PIT_COLORS = {
    'DESCANSO':  {'bg': 'rgba(200,16,46,0.10)',   'border': '#C8102E', 'dim': 'rgba(200,16,46,0.22)',   'text': '#FF6075'},
    'DP5':       {'bg': 'rgba(160,10,30,0.10)',   'border': '#A00A1E', 'dim': 'rgba(160,10,30,0.22)',   'text': '#FF8090'},
    'EC':        {'bg': 'rgba(180,185,195,0.08)', 'border': '#8A909E', 'dim': 'rgba(180,185,195,0.18)', 'text': '#C8CDD8'},
    'PRIBBENOW': {'bg': 'rgba(100,108,120,0.10)', 'border': '#606878', 'dim': 'rgba(100,108,120,0.22)', 'text': '#9BA3B2'},
}

# Equipment colors — Drummond brand palette (red intensities + grays)
EQ_COLORS = {
    'Komatsu PC8000': {'bg': 'rgba(200,16,46,0.09)',   'border': '#C8102E', 'text': '#FF6878'},
    'Komatsu PC4000': {'bg': 'rgba(200,16,46,0.09)',   'border': '#C8102E', 'text': '#FF6878'},
    'Hitachi EX3600': {'bg': 'rgba(200,16,46,0.09)',   'border': '#C8102E', 'text': '#FF6878'},
    'Bucyrus BE495':  {'bg': 'rgba(200,16,46,0.09)',   'border': '#C8102E', 'text': '#FF6878'},
    'Dragline':       {'bg': 'rgba(200,16,46,0.09)',   'border': '#C8102E', 'text': '#FF6878'},
}

MODEL_ERROR = 4
CONFIDENCE  = 100 - MODEL_ERROR  # 96.0%

# ══════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════
def reset_values():
    for pit, models in EQUIPOS_POR_PIT.items():
        for equipos in models.values():
            for eq in equipos:
                st.session_state[f'val_{eq}'] = 87.0
        src = DEFAULTS_CAM[pit]
        st.session_state[f'val_qty_{pit}']   = float(src['qty'])
        st.session_state[f'val_disp_{pit}']  = float(src['disp'])
        st.session_state[f'val_uso_{pit}']   = float(src['uso'])
        st.session_state[f'val_ciclo_{pit}'] = float(src['ciclo'])

def _save_eq(eq):
    st.session_state[f'val_{eq}'] = st.session_state[f'ni_{eq}']

def _save_truck(field, pit):
    st.session_state[f'val_{field}_{pit}'] = st.session_state[f'ni_{field}_{pit}']

if 'initialized' not in st.session_state:
    reset_values()
    st.session_state['initialized'] = True
if 'pit_idx' not in st.session_state:
    st.session_state['pit_idx'] = 0

# ══════════════════════════════════════════════════════════════════
# PREDICTION
# ══════════════════════════════════════════════════════════════════
def predict(data_df):
    dp = data_df.copy()
    dp = pd.get_dummies(dp, columns=['turno'], drop_first=False, dtype=int)
    dp = dp.reindex(columns=variables, fill_value=0)
    dp[COLS_NUMERICAS] = min_max_scaler.transform(dp[COLS_NUMERICAS])
    return modelo_ml.predict(dp)


# ══════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════
now = datetime.now().strftime('%d %b %Y · %H:%M').upper()
st.markdown(f"""
<div class="app-header">
  <div class="app-brand">
    <div class="app-mark">◆</div>
    <div>
      <div class="app-title">LOAD FORECAST · COMPLEX</div>
      <div class="app-sub">Production Engineering / Stacking Regressor ML v2.1</div>
    </div>
  </div>
  <div class="app-meta">
    <span class="meta-txt">{now}</span>
    <span class="meta-txt">04 PITS</span>
    <div class="meta-pill"><span class="live-dot"></span>Online</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MODE TABS
# ══════════════════════════════════════════════════════════════════
mode = st.radio('', ['Manual Prediction', 'Bulk Upload'],
                horizontal=True, label_visibility='collapsed')


# ══════════════════════════════════════════════════════════════════
# MODE 1 — MANUAL PREDICTION
# ══════════════════════════════════════════════════════════════════
if mode == 'Manual Prediction':

    st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)

    sidebar_col, content_col, result_col = st.columns([1, 3, 1.8], gap='small')

    # ════════════════════════════
    # SIDEBAR
    # ════════════════════════════
    with sidebar_col:
        st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)

        st.markdown("""
            <div class="sidebar-top">
              <div style="font-size:1.05rem;font-weight:700;color:var(--t1);">Mining Pits</div>
              <div style="font-size:0.78rem;color:var(--t3);font-family:var(--mono);margin-top:4px;letter-spacing:0.5px;">
                Select a pit to edit
              </div>
            </div>
            <span class="sidebar-section-lbl">Active Operations</span>
        """, unsafe_allow_html=True)

        for i, pit in enumerate(PITS):
            label     = PIT_LABELS[pit]
            eq_cnt    = sum(len(v) for v in EQUIPOS_POR_PIT[pit].values())
            is_active = (st.session_state['pit_idx'] == i)
            pc        = PIT_COLORS[pit]

            if is_active:
                nav_style   = f"background:{pc['dim']};border-left:4px solid {pc['border']};"
                name_color  = pc['text']
                badge_style = f"background:{pc['dim']};border:1px solid {pc['border']};color:{pc['text']};"
            else:
                nav_style   = "background:rgba(255,255,255,0.01);border-left:4px solid transparent;"
                name_color  = "var(--t2)"
                badge_style = "background:rgba(255,255,255,0.04);border:1px solid var(--b2);color:var(--t3);"

            st.markdown(f"""
                <div style="display:flex;align-items:center;gap:12px;
                            padding:12px 15px;cursor:pointer;transition:all 0.15s;
                            {nav_style}" id="pit-nav-{i}">
                  <div style="width:8px;height:8px;border-radius:50%;flex-shrink:0;
                              background:{''+pc['border'] if is_active else 'var(--t4)'};
                              box-shadow:{'0 0 6px '+pc['border'] if is_active else 'none'};"></div>
                  <div style="flex:1;min-width:0;">
                    <div style="font-size:1rem;font-weight:600;color:{name_color};">{label}</div>
                    <div style="font-family:var(--mono);font-size:0.7rem;color:var(--t3);margin-top:3px;">{pit}</div>
                  </div>
                  <span style="font-family:var(--mono);font-size:0.72rem;font-weight:700;
                               border-radius:4px;padding:2px 8px;{badge_style}">{eq_cnt}</span>
                </div>
            """, unsafe_allow_html=True)

            if st.button('›', key=f'nav_pit_{i}', help=f'View {label}', use_container_width=True):
                st.session_state['pit_idx'] = i
                st.rerun()

        st.markdown('<div class="turno-section"><span class="turno-lbl">Operating Shift</span></div>',
                    unsafe_allow_html=True)
        turno = st.selectbox('', ['D', 'N'], key='turno_sel', label_visibility='collapsed')

        st.markdown('<div style="padding:0 14px 12px 14px;">', unsafe_allow_html=True)
        if st.button('↺  Reset Values', use_container_width=True):
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

        pc_active = PIT_COLORS[pit]
        st.markdown(f"""
            <div class="content-panel">
              <div style="display:flex;align-items:center;justify-content:space-between;
                          padding:13px 19px;
                          background:linear-gradient(90deg, {pc_active['bg']} 0%, var(--bg-elev) 60%);
                          border-bottom:1px solid var(--b2);
                          border-left:4px solid {pc_active['border']};">
                <div>
                  <div style="font-size:1.1rem;font-weight:700;color:{pc_active['text']};">{pit_label}</div>
                  <div style="font-family:var(--mono);font-size:0.75rem;color:var(--t3);margin-top:4px;">{pit} · {eq_count} units · Pit {pit_idx+1} of {len(PITS)}</div>
                </div>
                <div style="font-family:var(--mono);font-size:0.7rem;font-weight:700;
                            color:{pc_active['text']};background:{pc_active['dim']};
                            border:1px solid {pc_active['border']};border-radius:4px;
                            padding:4px 12px;letter-spacing:2px;text-transform:uppercase;">
                  {pit}
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

        vals_palas    = {}
        vals_camiones = {}

        for p in PITS:
            for mod_eq, equipos in EQUIPOS_POR_PIT[p].items():
                for eq in equipos:
                    vals_palas[f'UsodeDisp_{eq}'] = st.session_state.get(f'val_{eq}', 87.0) / 100.0
            vals_camiones[f'QtyCamiones_{p}']        = st.session_state.get(f'val_qty_{p}',  DEFAULTS_CAM[p]['qty'])
            vals_camiones[f'Disponibilidad_TKS_{p}'] = st.session_state.get(f'val_disp_{p}', DEFAULTS_CAM[p]['disp']) / 100.0
            vals_camiones[f'UsodeDisp_TKS_{p}']      = st.session_state.get(f'val_uso_{p}',  DEFAULTS_CAM[p]['uso'])  / 100.0
            vals_camiones[COL_CICLO_MAP[p]]           = st.session_state.get(f'val_ciclo_{p}', DEFAULTS_CAM[p]['ciclo'])

        for mod_eq, equipos in EQUIPOS_POR_PIT[pit].items():
            for eq in equipos:
                st.session_state[f'ni_{eq}'] = st.session_state.get(f'val_{eq}', 87.0)
        for fld in ['qty', 'disp', 'uso', 'ciclo']:
            st.session_state[f'ni_{fld}_{pit}'] = st.session_state.get(
                f'val_{fld}_{pit}', float(DEFAULTS_CAM[pit][fld])
            )

        for modelo_eq, equipos in EQUIPOS_POR_PIT[pit].items():
            ec_colors = EQ_COLORS.get(modelo_eq, {'bg':'rgba(255,255,255,0.03)','border':'var(--b3)','text':'var(--t2)'})
            st.markdown(
                f'<div style="padding:14px 19px 12px 19px;border-bottom:1px solid var(--b1);'
                f'background:{ec_colors["bg"]};border-left:3px solid {ec_colors["border"]};">'
                f'<span style="font-family:var(--mono);font-size:0.78rem;font-weight:700;'
                f'letter-spacing:2px;text-transform:uppercase;color:{ec_colors["text"]};'
                f'display:block;margin-bottom:12px;">'
                f'▌ {modelo_eq}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            eq_cols = st.columns(len(equipos))
            for ec, eq in zip(eq_cols, equipos):
                with ec:
                    pct_val = st.number_input(
                        f'{eq} — Util %',
                        min_value=0.0, max_value=100.0,
                        step=1.0, format='%.1f',
                        key=f'ni_{eq}',
                        on_change=_save_eq, args=(eq,)
                    )
                    st.session_state[f'val_{eq}'] = pct_val
                    vals_palas[f'UsodeDisp_{eq}'] = pct_val / 100.0

        # Truck fleet inputs
        st.markdown(
            '<div class="trucks-block"><span class="trucks-lbl">Truck Fleet</span></div>',
            unsafe_allow_html=True
        )
        tc1, tc2, tc3, tc4 = st.columns(4)
        with tc1:
            qty = st.number_input('Qty', min_value=0.0, max_value=255.0,
                                  step=1.0, format='%.1f', key=f'ni_qty_{pit}',
                                  on_change=_save_truck, args=('qty', pit))
            st.session_state[f'val_qty_{pit}'] = qty
            vals_camiones[f'QtyCamiones_{pit}'] = qty
        with tc2:
            disp = st.number_input('Avail %', min_value=0.0, max_value=100.0,
                                   step=1.0, format='%.1f', key=f'ni_disp_{pit}',
                                   on_change=_save_truck, args=('disp', pit))
            st.session_state[f'val_disp_{pit}'] = disp
            vals_camiones[f'Disponibilidad_TKS_{pit}'] = disp / 100.0
        with tc3:
            uso = st.number_input('Util %', min_value=0.0, max_value=100.0,
                                  step=1.0, format='%.1f', key=f'ni_uso_{pit}',
                                  on_change=_save_truck, args=('uso', pit))
            st.session_state[f'val_uso_{pit}'] = uso
            vals_camiones[f'UsodeDisp_TKS_{pit}'] = uso / 100.0
        with tc4:
            ciclo = st.number_input('Cycle (min)', min_value=15.0, max_value=60.0,
                                    step=0.1, format='%.1f', key=f'ni_ciclo_{pit}',
                                    on_change=_save_truck, args=('ciclo', pit))
            st.session_state[f'val_ciclo_{pit}'] = ciclo
            vals_camiones[COL_CICLO_MAP[pit]] = ciclo

        # Fleet summary
        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
        st.markdown("""
            <div style="background:var(--bg-elev);border:1px solid var(--bred);border-radius:5px;
                        padding:11px 17px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;
                        border-left:3px solid var(--red);">
              <span style="font-family:var(--mono);font-size:0.82rem;color:var(--red-hi);
                           letter-spacing:2px;text-transform:uppercase;font-weight:700;">Trucks by Pit:</span>
        """, unsafe_allow_html=True)

        summary_parts = []
        for p in PITS:
            qty_p = st.session_state.get(f'val_qty_{p}', DEFAULTS_CAM[p]['qty'])
            summary_parts.append(
                f'<span style="font-family:var(--mono);font-size:0.95rem;color:var(--t2);">'
                f'{PIT_LABELS[p]}: <strong style="color:var(--t1);">{int(qty_p)}</strong></span>'
            )
        st.markdown(' &nbsp;<span style="color:var(--b3)">|</span>&nbsp; '.join(summary_parts) + '</div>', unsafe_allow_html=True)

    # ════════════════════════════
    # RESULT PANEL
    # ════════════════════════════
    with result_col:

        total_cam     = sum(st.session_state.get(f'val_qty_{p}', DEFAULTS_CAM[p]['qty']) for p in PITS)
        total_cam_int = int(round(total_cam))
        cam_ok        = total_cam_int == QTY_TOTAL
        delta_cam     = total_cam_int - QTY_TOTAL
        signo         = f'+{delta_cam}' if delta_cam > 0 else str(delta_cam)

        if cam_ok:
            st.markdown(f"""
                <div class="cam-banner ok">
                  <div>
                    <div class="cam-banner-msg">✓ Fleet Complete</div>
                    <div class="cam-banner-sub">{total_cam_int} trucks distributed</div>
                  </div>
                  <div style="text-align:right;">
                    <div class="cam-banner-num">{QTY_TOTAL}</div>
                    <div class="cam-banner-delta">target</div>
                  </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="cam-banner warn">
                  <div>
                    <div class="cam-banner-msg">⚠ Fleet Mismatch</div>
                    <div class="cam-banner-sub">Target: {QTY_TOTAL} · Adjustment: {signo}</div>
                  </div>
                  <div style="text-align:right;">
                    <div class="cam-banner-num">{total_cam_int}</div>
                    <div class="cam-banner-delta">current</div>
                  </div>
                </div>
            """, unsafe_allow_html=True)

        ph = st.empty()
        shift_label = 'Day' if turno == 'D' else 'Night'
        ph.markdown(f"""
            <div class="hero">
              <div class="hero-top">
                <div>
                  <div class="hero-eyebrow">Predicted Loads</div>
                  <div class="hero-num">—</div>
                  <div class="hero-unit">loads · per shift</div>
                </div>
                <div class="hero-shift">{shift_label} ({turno})</div>
              </div>
              <div class="conf-block">
                <div class="conf-head">
                  <span class="conf-lbl">Model Confidence</span>
                  <span class="conf-val">{CONFIDENCE:.1f}%</span>
                </div>
                <div class="conf-bar-bg">
                  <div class="conf-bar-fill" style="width:{CONFIDENCE}%"></div>
                </div>
                <div class="conf-foot">
                  <span>MAPE ±{MODEL_ERROR:.1f}%</span>
                  <span>Pending</span>
                </div>
              </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)

        st.markdown('<div class="calc-wrap">', unsafe_allow_html=True)
        run_pred = st.button(
            '▸  Run Prediction' if cam_ok else f'▸  Fleet ≠ {QTY_TOTAL}',
            use_container_width=True,
            disabled=not cam_ok,
            key='btn_calc'
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
            <div style="background:var(--bg-elev);border:1px solid var(--b2);
                        border-top:2px solid var(--red);
                        border-radius:5px;padding:1rem 1.1rem;margin-top:0.7rem;">
              <div style="font-family:var(--mono);font-size:0.72rem;color:var(--red);
                          letter-spacing:2px;text-transform:uppercase;font-weight:700;
                          margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid var(--b2);">
                Active Configuration
              </div>
              <div style="display:flex;flex-direction:column;gap:8px;">
                <div style="display:flex;justify-content:space-between;font-size:0.88rem;">
                  <span style="color:var(--t2);font-family:var(--mono);">Pits</span>
                  <span style="color:var(--t1);font-family:var(--mono);font-weight:600;">04 / 04</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.88rem;">
                  <span style="color:var(--t2);font-family:var(--mono);">Variables</span>
                  <span style="color:var(--t1);font-family:var(--mono);font-weight:600;">45</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.88rem;">
                  <span style="color:var(--t2);font-family:var(--mono);">Algorithm</span>
                  <span style="color:var(--gold-hi);font-family:var(--mono);font-weight:600;">Stacking Regressor</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.88rem;">
                  <span style="color:var(--t2);font-family:var(--mono);">MAPE Error</span>
                  <span style="color:var(--gold-hi);font-family:var(--mono);font-weight:600;">±{MODEL_ERROR:.1f}%</span>
                </div>
              </div>
            </div>
        """, unsafe_allow_html=True)

        if run_pred and cam_ok:
            datos  = {**vals_palas, **vals_camiones, 'turno': turno}
            data   = pd.DataFrame([datos])[COLUMNAS_ESPERADAS]
            Y_pred = predict(data)
            cargas = int(round(Y_pred[0]))
            margen = int(round(cargas * MODEL_ERROR / 100))
            lo, hi = cargas - margen, cargas + margen
            shift_full = 'Day' if turno == 'D' else 'Night'

            ph.markdown(f"""
                <div class="hero">
                  <div class="hero-top">
                    <div>
                      <div class="hero-eyebrow">Predicted Loads</div>
                      <div class="hero-num live">{cargas:,}</div>
                      <div class="hero-unit">loads · per shift</div>
                      <div class="hero-range">▴ range {lo:,} – {hi:,}</div>
                    </div>
                    <div class="hero-shift">{shift_full} ({turno})</div>
                  </div>
                  <div class="conf-block">
                    <div class="conf-head">
                      <span class="conf-lbl">Model Confidence</span>
                      <span class="conf-val">{CONFIDENCE:.1f}%</span>
                    </div>
                    <div class="conf-bar-bg">
                      <div class="conf-bar-fill" style="width:{CONFIDENCE}%"></div>
                    </div>
                    <div class="conf-foot">
                      <span>MAPE ±{MODEL_ERROR:.1f}%</span>
                      <span style="color:var(--green);">● Computed</span>
                    </div>
                  </div>
                </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# MODE 2 — BULK UPLOAD
# ══════════════════════════════════════════════════════════════════
else:
    st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)
    bulk_l, bulk_r = st.columns([3, 2], gap='large')

    with bulk_l:
        st.markdown('<div class="step-lbl"><span class="step-num">1</span>Download the CSV template</div>',
                    unsafe_allow_html=True)
        st.markdown("""
            <div style="background:var(--bg-card);border:1px solid var(--b1);
                        border-left:3px solid var(--red);border-radius:4px;
                        padding:0.8rem 1rem;margin-bottom:0.6rem;
                        font-size:0.88rem;color:var(--t2);line-height:1.5;">
                Template with all 45 required parameters. Each row represents one shift.
                <br><span style="font-family:var(--mono);font-size:0.75rem;color:var(--t3);">
                ⓘ Utilization and availability values in the CSV must be decimals (0–1).</span>
            </div>
        """, unsafe_allow_html=True)

        ej = {col: 0.75 for col in COLS_NUMERICAS}
        ej.update({
            'QtyCamiones_DESCANSO': 89.7,    'Disponibilidad_TKS_DESCANSO': 0.664,
            'UsodeDisp_TKS_DESCANSO': 0.834,  'TiempoCiclo_TKS_DESCANSO': 30.62,
            'QtyCamiones_DP5': 81.9,          'Disponibilidad_TKS_DP5': 0.925,
            'UsodeDisp_TKS_DP5': 0.860,       'TiempoCiclo2_DP5': 32.72,
            'QtyCamiones_EC': 15.55,           'Disponibilidad_TKS_EC': 0.942,
            'UsodeDisp_TKS_EC': 0.814,         'TiempoCiclo2_EC': 28.32,
            'QtyCamiones_PRIBBENOW': 67.95,   'Disponibilidad_TKS_PRIBBENOW': 0.716,
            'UsodeDisp_TKS_PRIBBENOW': 0.865, 'TiempoCiclo_TKS_PRIBBENOW': 25.60,
            'turno': 'D'
        })
        buf = io.BytesIO()
        pd.DataFrame([ej]).to_csv(buf, index=False)
        buf.seek(0)
        st.download_button('⬇  Download CSV Template', data=buf,
                           file_name='prediction_template.csv', mime='text/csv')

        st.markdown('<div class="step-lbl" style="margin-top:1rem;"><span class="step-num">2</span>Upload your file</div>',
                    unsafe_allow_html=True)
        archivo = st.file_uploader('Drag your CSV here or click to browse',
                                   type=['csv'], label_visibility='visible')

    with bulk_r:
        st.markdown(f"""
            <div style="background:var(--bg-card);border:1px solid var(--b2);
                        border-top:2px solid var(--red);border-radius:4px;padding:1rem 1.1rem;">
              <div style="font-family:var(--mono);font-size:0.68rem;color:var(--red);
                          letter-spacing:2px;text-transform:uppercase;font-weight:700;
                          margin-bottom:0.8rem;padding-bottom:6px;border-bottom:1px solid var(--b2);">
                Model Specifications
              </div>
              <div style="display:flex;flex-direction:column;gap:6px;">
                <div style="display:flex;justify-content:space-between;font-size:0.82rem;padding:4px 0;border-bottom:1px solid var(--b1);">
                  <span style="color:var(--t2);font-family:var(--mono);">Numeric variables</span>
                  <span style="color:var(--t1);font-family:var(--mono);font-weight:600;">44</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.82rem;padding:4px 0;border-bottom:1px solid var(--b1);">
                  <span style="color:var(--t2);font-family:var(--mono);">Categorical variable</span>
                  <span style="color:var(--t1);font-family:var(--mono);font-weight:600;">shift (D/N)</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.82rem;padding:4px 0;border-bottom:1px solid var(--b1);">
                  <span style="color:var(--t2);font-family:var(--mono);">Mining pits</span>
                  <span style="color:var(--gold-hi);font-family:var(--mono);font-weight:600;">04</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.82rem;padding:4px 0;border-bottom:1px solid var(--b1);">
                  <span style="color:var(--t2);font-family:var(--mono);">Algorithm</span>
                  <span style="color:var(--gold-hi);font-family:var(--mono);font-weight:600;">Stacking Regressor</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.82rem;padding:4px 0;">
                  <span style="color:var(--t2);font-family:var(--mono);">Confidence</span>
                  <span style="color:var(--green);font-family:var(--mono);font-weight:600;">{CONFIDENCE:.1f}%</span>
                </div>
              </div>
            </div>
        """, unsafe_allow_html=True)

    if archivo:
        st.markdown('<hr>', unsafe_allow_html=True)
        try:
            df = pd.read_csv(archivo)
            missing = [c for c in COLUMNAS_ESPERADAS if c not in df.columns]
            if missing:
                st.error(f'❌ Missing columns: {missing}')
                st.stop()

            st.success(f'✅ {len(df):,} shifts loaded successfully')
            st.dataframe(df[COLUMNAS_ESPERADAS].head(3), use_container_width=True)

            st.markdown('<div class="step-lbl"><span class="step-num">3</span>Run bulk prediction</div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="calc-wrap">', unsafe_allow_html=True)
            run_bulk = st.button('▸  Predict All Shifts', use_container_width=False)
            st.markdown('</div>', unsafe_allow_html=True)

            if run_bulk:
                Y = predict(df[COLUMNAS_ESPERADAS].copy())
                df['Predicted_Loads'] = np.round(Y).astype(int)

                m1, m2, m3, m4 = st.columns(4)
                m1.metric('Shifts Processed', f"{len(df):,}")
                m2.metric('Average Loads',    f"{df['Predicted_Loads'].mean():,.0f}")
                m3.metric('Minimum',          f"{df['Predicted_Loads'].min():,}")
                m4.metric('Maximum',          f"{df['Predicted_Loads'].max():,}")

                st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
                cols_v = ['turno','Predicted_Loads'] + [c for c in COLUMNAS_ESPERADAS if c != 'turno']
                st.dataframe(df[cols_v], use_container_width=True)

                buf2 = io.BytesIO()
                df.to_csv(buf2, index=False)
                buf2.seek(0)
                st.download_button('⬇  Download Results', data=buf2,
                                   file_name='predictions.csv', mime='text/csv')
                st.caption(f'⚠ Model error: ±{MODEL_ERROR:.1f}% — For operational reference only.')

        except Exception as e:
            st.error(f'Error processing file: {e}')
