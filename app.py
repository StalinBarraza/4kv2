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
# CSS
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

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
    width:30px; height:30px;
    background: var(--bg-elev);
    border: 1px solid var(--b3);
    border-radius:4px;
    display:flex; align-items:center; justify-content:center;
    font-size:0.85rem; color:var(--copper);
}
.app-title { font-size:0.9rem !important; font-weight:600 !important; color:var(--t1) !important; letter-spacing:-0.1px; }
.app-sub   { font-size:0.6rem !important; color:var(--t3) !important; letter-spacing:1.5px; text-transform:uppercase; font-family:var(--mono) !important; margin-top:1px; }
.app-meta  { display:flex; align-items:center; gap:20px; }
.meta-pill {
    display:flex; align-items:center; gap:6px;
    font-size:0.6rem; color:var(--green); letter-spacing:1.2px; text-transform:uppercase;
    font-family:var(--mono) !important;
}
.live-dot {
    width:5px; height:5px; background:var(--green); border-radius:50%;
    box-shadow:0 0 5px var(--green); animation:blink 2.2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.meta-txt { font-family:var(--mono) !important; font-size:0.62rem !important; color:var(--t3) !important; }

/* ── Mode tabs ── */
.stRadio > div {
    display:flex !important; gap:0 !important;
    background:transparent !important; border:none !important; padding:0 !important;
    border-bottom: 1px solid var(--b1) !important;
    border-radius:0 !important; width:100% !important;
}
.stRadio > div > label {
    padding:7px 20px 8px 20px !important; border-radius:0 !important;
    font-size:0.65rem !important; font-weight:500 !important;
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
    padding:12px 14px 10px 14px;
    border-bottom:1px solid var(--b1);
}
.sidebar-section-lbl {
    font-family:var(--mono) !important;
    font-size:0.52rem !important; color:var(--t3) !important;
    letter-spacing:2.5px !important; text-transform:uppercase !important;
    padding:10px 14px 6px 14px; display:block;
}
.pit-nav-item {
    display:flex; align-items:center; gap:10px;
    padding:9px 12px; cursor:pointer;
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
.pit-nav-name { font-size:0.78rem !important; font-weight:500 !important; }
.pit-nav-item.active .pit-nav-name { color:var(--copper-hi) !important; }
.pit-nav-item:not(.active) .pit-nav-name { color:var(--t2) !important; }
.pit-nav-code { font-family:var(--mono) !important; font-size:0.55rem !important; color:var(--t3) !important; margin-top:1px; }
.pit-nav-count {
    margin-left:auto;
    font-family:var(--mono) !important; font-size:0.55rem !important;
    color:var(--t3) !important;
    background:var(--bg-elev);
    border:1px solid var(--b1);
    border-radius:3px; padding:1px 5px;
}

/* Turno toggle in sidebar */
.turno-section {
    padding:10px 14px 12px 14px;
    border-top:1px solid var(--b1);
    margin-top:auto;
}
.turno-lbl {
    font-family:var(--mono) !important;
    font-size:0.5rem !important; color:var(--t3) !important;
    letter-spacing:2.5px !important; text-transform:uppercase !important;
    margin-bottom:6px; display:block;
}

/* ── Selectbox (turno) ── */
div[data-testid="stSelectbox"] > label {
    font-size:0.55rem !important; color:var(--t3) !important;
    letter-spacing:1.8px !important; text-transform:uppercase !important;
    font-family:var(--mono) !important; margin-bottom:3px !important;
}
div[data-testid="stSelectbox"] > div > div {
    background:var(--bg-elev) !important; border:1px solid var(--b2) !important;
    border-radius:4px !important; color:var(--t1) !important;
    font-size:0.78rem !important; min-height:28px !important;
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
    padding:11px 16px;
    background:var(--bg-elev);
    border-bottom:1px solid var(--b1);
}
.content-pit-name { font-size:0.88rem !important; font-weight:600 !important; color:var(--t1) !important; }
.content-pit-meta { font-family:var(--mono) !important; font-size:0.58rem !important; color:var(--t3) !important; margin-top:2px; }
.nav-arrows { display:flex; gap:5px; }

/* ── Nav buttons ── */
.stButton > button {
    font-family:var(--mono) !important; font-size:0.65rem !important;
    font-weight:500 !important; letter-spacing:1px !important;
    text-transform:uppercase !important; border-radius:4px !important;
    padding:6px 12px !important; transition:all 0.15s !important;
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
    font-size:0.52rem !important; font-weight:400 !important;
    color:var(--t3) !important; letter-spacing:1px !important;
    text-transform:uppercase !important; font-family:var(--mono) !important;
    margin-bottom:0 !important; line-height:1.2 !important;
    white-space:nowrap !important; overflow:hidden !important;
    text-overflow:ellipsis !important;
}
div[data-testid="stNumberInput"] > div { gap:0 !important; }
div[data-testid="stNumberInput"] input {
    background:transparent !important; color:var(--t1) !important;
    border:none !important;
    border-bottom:1px solid var(--b2) !important;
    border-radius:0 !important;
    font-size:0.82rem !important; font-family:var(--mono) !important;
    font-weight:500 !important;
    padding:2px 4px !important; height:24px !important;
    transition:border-color 0.15s, color 0.15s !important;
}
div[data-testid="stNumberInput"] input:hover { border-bottom-color:var(--t2) !important; }
div[data-testid="stNumberInput"] input:focus {
    border-bottom-color:var(--copper) !important;
    color:var(--copper-hi) !important; outline:none !important; box-shadow:none !important;
}
div[data-testid="stNumberInput"] button {
    background:transparent !important; border:1px solid var(--b1) !important;
    color:var(--t3) !important; height:24px !important;
    min-width:20px !important; padding:0 3px !important; border-radius:3px !important;
}
div[data-testid="stNumberInput"] button:hover { color:var(--copper) !important; border-color:var(--b2) !important; }

/* ── Equipment section inside content ── */
.eq-block {
    padding:12px 16px 10px 16px;
    border-bottom:1px solid var(--b1);
}
.eq-model-lbl {
    font-family:var(--mono) !important;
    font-size:0.52rem !important; font-weight:500 !important;
    letter-spacing:2px !important; text-transform:uppercase !important;
    margin-bottom:8px !important;
    padding-left:6px;
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
    padding:10px 16px 12px 16px;
}
.trucks-lbl {
    font-family:var(--mono) !important; font-size:0.52rem !important;
    font-weight:500 !important; color:var(--t3) !important;
    letter-spacing:2px !important; text-transform:uppercase !important;
    margin-bottom:8px !important; display:block;
}

/* ── Camiones validation banner ── */
.cam-banner {
    margin:0 0 0.7rem 0;
    border-radius:4px; padding:9px 14px;
    display:flex; align-items:center; justify-content:space-between;
}
.cam-banner.ok   { background:var(--green-dim); border:1px solid rgba(107,190,131,0.2); border-left:3px solid var(--green); }
.cam-banner.warn { background:var(--red-dim);   border:1px solid rgba(199,107,107,0.2); border-left:3px solid var(--red); }
.cam-banner-msg  { font-size:0.72rem !important; font-weight:500 !important; }
.cam-banner.ok   .cam-banner-msg { color:var(--green) !important; }
.cam-banner.warn .cam-banner-msg { color:var(--red) !important; }
.cam-banner-sub  { font-size:0.62rem !important; font-family:var(--mono) !important; color:var(--t3) !important; margin-top:2px; }
.cam-banner-num  { font-family:var(--mono) !important; font-size:1.5rem !important; font-weight:300 !important; letter-spacing:-1px !important; }
.cam-banner.ok   .cam-banner-num { color:var(--green) !important; }
.cam-banner.warn .cam-banner-num { color:var(--red) !important; }
.cam-banner-delta { font-family:var(--mono) !important; font-size:0.58rem !important; }
.cam-banner.ok   .cam-banner-delta { color:var(--green) !important; }
.cam-banner.warn .cam-banner-delta { color:var(--red) !important; }

/* ── Hero result ── */
.hero {
    background:var(--bg-card);
    border:1px solid var(--b1);
    border-radius:6px;
    padding:1.4rem 1.8rem 1.3rem 1.8rem;
    position:relative; overflow:hidden;
}
.hero::before {
    content:''; position:absolute; top:0; left:0;
    width:2px; height:100%;
    background:linear-gradient(180deg, var(--copper), transparent 70%);
}
.hero-top { display:flex; justify-content:space-between; align-items:flex-start; }
.hero-eyebrow {
    font-family:var(--mono) !important; font-size:0.55rem !important;
    color:var(--t3) !important; letter-spacing:2.5px !important; text-transform:uppercase;
}
.hero-num {
    font-family:var(--mono) !important; font-size:4.2rem !important;
    font-weight:300 !important; line-height:0.95 !important;
    letter-spacing:-3px !important; margin:0.4rem 0 0.25rem 0;
    color:var(--t3) !important;
}
.hero-num.live { color:var(--green) !important; }
.hero-unit { font-family:var(--mono) !important; font-size:0.6rem !important; color:var(--t3) !important; letter-spacing:2px !important; text-transform:uppercase; }
.hero-range { font-family:var(--mono) !important; font-size:0.65rem !important; color:var(--green) !important; margin-top:0.35rem; }
.hero-shift {
    font-family:var(--mono) !important; font-size:0.6rem !important;
    color:var(--t3) !important; background:var(--bg-elev);
    border:1px solid var(--b1); border-radius:3px; padding:3px 9px;
    letter-spacing:1.2px; text-transform:uppercase;
}
.conf-block { border-top:1px solid var(--b1); padding-top:0.8rem; margin-top:0.8rem; }
.conf-head  { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:6px; }
.conf-lbl   { font-family:var(--mono) !important; font-size:0.55rem !important; color:var(--t3) !important; letter-spacing:2px !important; text-transform:uppercase; }
.conf-val   { font-family:var(--mono) !important; font-size:0.82rem !important; font-weight:600 !important; color:var(--copper-hi) !important; }
.conf-bar-bg   { width:100%; height:3px; background:var(--bg-elev); border-radius:2px; overflow:hidden; }
.conf-bar-fill { height:100%; background:linear-gradient(90deg, var(--copper), var(--copper-hi)); border-radius:2px; }
.conf-foot { display:flex; justify-content:space-between; margin-top:5px;
    font-family:var(--mono) !important; font-size:0.55rem !important; color:var(--t3) !important; }

/* ── Calc button ── */
.calc-wrap .stButton > button {
    background:linear-gradient(180deg, #B68B5E 0%, #8C6440 100%) !important;
    color:#0F1115 !important; font-family:var(--sans) !important;
    font-size:0.68rem !important; font-weight:700 !important;
    letter-spacing:1.5px !important; border:none !important;
    border-radius:4px !important; padding:12px 20px !important;
    box-shadow:0 2px 8px rgba(0,0,0,0.4) !important;
    transition:all 0.18s !important; width:100% !important;
}
.calc-wrap .stButton > button:hover {
    background:linear-gradient(180deg, #C49770 0%, #A67C52 100%) !important;
    transform:translateY(-1px) !important;
    box-shadow:0 4px 14px rgba(166,124,82,0.35) !important;
}
.calc-wrap .stButton > button:disabled {
    background:var(--bg-elev) !important; color:var(--t3) !important;
    transform:none !important; box-shadow:none !important; opacity:1 !important;
    border:1px solid var(--b1) !important; cursor:not-allowed !important;
}

/* ── Download / Metric / File / Alert ── */
div[data-testid="stDownloadButton"] > button {
    background:transparent !important; color:var(--copper-hi) !important;
    border:1px solid rgba(166,124,82,0.3) !important;
    font-family:var(--mono) !important; font-size:0.62rem !important;
    letter-spacing:1.2px !important; text-transform:uppercase !important;
    border-radius:4px !important; padding:7px 14px !important; width:auto !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background:var(--copper-dim) !important; border-color:var(--copper) !important;
}
div[data-testid="stFileUploader"] > div {
    background:var(--bg-card) !important; border:1px dashed var(--b2) !important;
    border-radius:4px !important; padding:1.4rem !important;
}
div[data-testid="stFileUploader"] > div:hover { border-color:var(--copper) !important; }
div[data-testid="stDataFrame"] { border-radius:4px !important; border:1px solid var(--b1) !important; }
div[data-testid="stMetric"] {
    background:var(--bg-card) !important; border:1px solid var(--b1) !important;
    border-left:2px solid var(--copper) !important; border-radius:3px !important;
    padding:0.7rem 1rem !important;
}
div[data-testid="stMetric"] label {
    font-size:0.55rem !important; color:var(--t3) !important;
    letter-spacing:1.8px !important; text-transform:uppercase !important;
    font-family:var(--mono) !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-family:var(--mono) !important; color:var(--t1) !important;
    font-size:1.2rem !important; font-weight:500 !important;
}
div[data-testid="stAlert"] { border-radius:4px !important; font-size:0.76rem !important; }
div[data-testid="stCaptionContainer"] { color:var(--t3) !important; font-size:0.62rem !important; font-family:var(--mono) !important; }
hr { border:none !important; border-top:1px solid var(--b1) !important; margin:0.8rem 0 !important; }
div[data-testid="stHorizontalBlock"] { gap:0.6rem; }

/* Bulk steps */
.step-lbl {
    display:flex; align-items:center; gap:9px;
    font-family:var(--mono) !important; font-size:0.62rem !important;
    color:var(--t2) !important; letter-spacing:1.2px !important;
    text-transform:uppercase !important; margin:1rem 0 0.5rem 0;
}
.step-num {
    width:19px; height:19px; border:1px solid var(--copper);
    color:var(--copper-hi); border-radius:50%;
    display:inline-flex; align-items:center; justify-content:center;
    font-size:0.58rem; font-weight:600; flex-shrink:0;
    background:var(--copper-dim);
}

/* Scrollbar */
::-webkit-scrollbar { width:3px; height:3px; }
::-webkit-scrollbar-track { background:var(--bg-deep); }
::-webkit-scrollbar-thumb { background:var(--bg-elev); border-radius:2px; }
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
                st.session_state[f'ni_{eq}'] = 75.0
        src = DEFAULTS_CAM[pit]
        st.session_state[f'ni_qty_{pit}']  = float(src['qty'])
        st.session_state[f'ni_disp_{pit}'] = float(src['disp'])
        st.session_state[f'ni_uso_{pit}']  = float(src['uso'])
        st.session_state[f'ni_ciclo_{pit}']= float(src['ciclo'])

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

        # Título sidebar
        st.markdown("""
            <div class="sidebar-top">
              <div style="font-size:0.7rem;font-weight:600;color:var(--t1);">Frentes Mineros</div>
              <div style="font-size:0.55rem;color:var(--t3);font-family:var(--mono);margin-top:2px;">
                Selecciona un pit para editar
              </div>
            </div>
            <span class="sidebar-section-lbl">Operaciones activas</span>
        """, unsafe_allow_html=True)

        # Pit nav items — botón real de Streamlit por pit
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

            # Botón invisible superpuesto para capturar el click
            if st.button(f'›', key=f'nav_pit_{i}',
                         help=f'Ver {label}',
                         use_container_width=True):
                st.session_state['pit_idx'] = i
                st.rerun()

        # Turno selector
        st.markdown('<div class="turno-section"><span class="turno-lbl">Turno de operación</span></div>',
                    unsafe_allow_html=True)
        turno = st.selectbox('', ['D', 'N'],
                             key='turno_sel',
                             label_visibility='collapsed')

        # Resetear
        st.markdown('<div style="padding:0 14px 12px 14px;">', unsafe_allow_html=True)
        if st.button('↺  Resetear valores', use_container_width=True):
            reset_values()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)  # close sidebar-nav

    # ════════════════════════════
    # CONTENT PANEL
    # ════════════════════════════
    with content_col:
        pit_idx   = st.session_state['pit_idx']
        pit       = PITS[pit_idx]
        pit_label = PIT_LABELS[pit]
        eq_count  = sum(len(v) for v in EQUIPOS_POR_PIT[pit].values())

        # Top bar with pit name + nav arrows
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

        # Arrows — prev / next
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

        # Collect values for ALL pits (needed for prediction)
        # Only render inputs for the active pit
        for p in PITS:
            for mod_eq, equipos in EQUIPOS_POR_PIT[p].items():
                for eq in equipos:
                    val = st.session_state.get(f'ni_{eq}', 75.0)
                    vals_palas[f'UsodeDisp_{eq}'] = val / 100.0
            vals_camiones[f'QtyCamiones_{p}']         = st.session_state.get(f'ni_qty_{p}', DEFAULTS_CAM[p]['qty'])
            vals_camiones[f'Disponibilidad_TKS_{p}']  = st.session_state.get(f'ni_disp_{p}', DEFAULTS_CAM[p]['disp']) / 100.0
            vals_camiones[f'UsodeDisp_TKS_{p}']       = st.session_state.get(f'ni_uso_{p}',  DEFAULTS_CAM[p]['uso'])  / 100.0
            vals_camiones[COL_CICLO_MAP[p]]            = st.session_state.get(f'ni_ciclo_{p}', DEFAULTS_CAM[p]['ciclo'])

        # Render inputs only for active pit
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
                    pct_val = st.number_input(
                        f'{eq} — Util %',
                        min_value=0.0, max_value=100.0,
                        step=1.0, format='%.1f',
                        key=f'ni_{eq}'
                    )
                    vals_palas[f'UsodeDisp_{eq}'] = pct_val / 100.0

        # Trucks for active pit
        st.markdown(
            '<div class="trucks-block"><span class="trucks-lbl">Flota de Camiones</span></div>',
            unsafe_allow_html=True
        )
        tc1, tc2, tc3, tc4 = st.columns(4)
        with tc1:
            qty = st.number_input('Qty', min_value=0.0, max_value=400.0,
                                  step=1.0, format='%.1f', key=f'ni_qty_{pit}')
            vals_camiones[f'QtyCamiones_{pit}'] = qty
        with tc2:
            disp = st.number_input('Disp %', min_value=0.0, max_value=100.0,
                                   step=1.0, format='%.1f', key=f'ni_disp_{pit}')
            vals_camiones[f'Disponibilidad_TKS_{pit}'] = disp / 100.0
        with tc3:
            uso = st.number_input('Uso %', min_value=0.0, max_value=100.0,
                                  step=1.0, format='%.1f', key=f'ni_uso_{pit}')
            vals_camiones[f'UsodeDisp_TKS_{pit}'] = uso / 100.0
        with tc4:
            ciclo = st.number_input('Ciclo (min)', min_value=15.0, max_value=60.0,
                                    step=0.1, format='%.1f', key=f'ni_ciclo_{pit}')
            vals_camiones[COL_CICLO_MAP[pit]] = ciclo

        # Resumen de todos los pits (camiones)
        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
        st.markdown("""
            <div style="background:var(--bg-elev);border:1px solid var(--b1);border-radius:4px;
                        padding:8px 14px;display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
              <span style="font-family:var(--mono);font-size:0.52rem;color:var(--t3);
                           letter-spacing:2px;text-transform:uppercase;">Flota total por frente:</span>
        """, unsafe_allow_html=True)

        resumen_parts = []
        for p in PITS:
            qty_p = st.session_state.get(f'ni_qty_{p}', DEFAULTS_CAM[p]['qty'])
            resumen_parts.append(
                f'<span style="font-family:var(--mono);font-size:0.65rem;color:var(--t2);">'
                f'{PIT_LABELS[p]}: <strong style="color:var(--t1);">{int(qty_p)}</strong></span>'
            )
        st.markdown(' &nbsp;·&nbsp; '.join(resumen_parts) + '</div>', unsafe_allow_html=True)

    # ════════════════════════════
    # RESULT PANEL
    # ════════════════════════════
    with result_col:

        # ── Validation ──────────────────────────────────────────
        total_cam = sum(
            st.session_state.get(f'ni_qty_{p}', DEFAULTS_CAM[p]['qty'])
            for p in PITS
        )
        total_cam_int = int(round(total_cam))
        cam_ok        = total_cam_int == QTY_TOTAL
        delta_cam     = total_cam_int - QTY_TOTAL
        signo         = f'+{delta_cam}' if delta_cam > 0 else str(delta_cam)

        if cam_ok:
            st.markdown(f"""
                <div class="cam-banner ok">
                  <div>
                    <div class="cam-banner-msg">✓ Flota completa</div>
                    <div class="cam-banner-sub">{total_cam_int} camiones distribuidos</div>
                  </div>
                  <div style="text-align:right;">
                    <div class="cam-banner-num">{QTY_TOTAL}</div>
                    <div class="cam-banner-delta">objetivo</div>
                  </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="cam-banner warn">
                  <div>
                    <div class="cam-banner-msg">⚠ Flota incorrecta</div>
                    <div class="cam-banner-sub">Objetivo: {QTY_TOTAL} · Ajuste: {signo}</div>
                  </div>
                  <div style="text-align:right;">
                    <div class="cam-banner-num">{total_cam_int}</div>
                    <div class="cam-banner-delta">actual</div>
                  </div>
                </div>
            """, unsafe_allow_html=True)

        # ── Hero placeholder ─────────────────────────────────────
        ph = st.empty()
        ph.markdown(f"""
            <div class="hero">
              <div class="hero-top">
                <div>
                  <div class="hero-eyebrow">Predicted Load Count</div>
                  <div class="hero-num">—</div>
                  <div class="hero-unit">loads · per shift</div>
                </div>
                <div class="hero-shift">Shift {turno}</div>
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
                  <span>RMSE ±{MODEL_ERROR:.1f}%</span>
                  <span>Pending</span>
                </div>
              </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)

        # ── Calc button ──────────────────────────────────────────
        st.markdown('<div class="calc-wrap">', unsafe_allow_html=True)
        calcular = st.button(
            '▸  Ejecutar Predicción' if cam_ok else f'▸  Flota ≠ {QTY_TOTAL}',
            use_container_width=True,
            disabled=not cam_ok,
            key='btn_calc'
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Cfg info ─────────────────────────────────────────────
        st.markdown(f"""
            <div style="background:var(--bg-card);border:1px solid var(--b1);
                        border-radius:4px;padding:0.8rem 1rem;margin-top:0.6rem;">
              <div style="font-family:var(--mono);font-size:0.5rem;color:var(--t3);
                          letter-spacing:2.5px;text-transform:uppercase;
                          margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid var(--b1);">
                Configuración Activa
              </div>
              <div style="display:flex;flex-direction:column;gap:5px;">
                <div style="display:flex;justify-content:space-between;font-size:0.65rem;">
                  <span style="color:var(--t2);font-family:var(--mono);">Frentes</span>
                  <span style="color:var(--t1);font-family:var(--mono);">04 / 04</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.65rem;">
                  <span style="color:var(--t2);font-family:var(--mono);">Variables</span>
                  <span style="color:var(--t1);font-family:var(--mono);">45</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.65rem;">
                  <span style="color:var(--t2);font-family:var(--mono);">Algoritmo</span>
                  <span style="color:var(--copper-hi);font-family:var(--mono);">Ensemble</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.65rem;">
                  <span style="color:var(--t2);font-family:var(--mono);">Error RMSE</span>
                  <span style="color:var(--copper-hi);font-family:var(--mono);">±{MODEL_ERROR:.1f}%</span>
                </div>
              </div>
            </div>
        """, unsafe_allow_html=True)

        # ── Ejecutar predicción ──────────────────────────────────
        if calcular and cam_ok:
            datos  = {**vals_palas, **vals_camiones, 'turno': turno}
            data   = pd.DataFrame([datos])[COLUMNAS_ESPERADAS]
            Y_pred = predecir(data)
            cargas = int(round(Y_pred[0]))
            margen = int(round(cargas * MODEL_ERROR / 100))
            lo, hi = cargas - margen, cargas + margen
            turno_label = 'Diurno' if turno == 'D' else 'Nocturno'

            ph.markdown(f"""
                <div class="hero">
                  <div class="hero-top">
                    <div>
                      <div class="hero-eyebrow">Predicted Load Count</div>
                      <div class="hero-num live">{cargas:,}</div>
                      <div class="hero-unit">loads · per shift</div>
                      <div class="hero-range">▴ rango {lo:,} – {hi:,}</div>
                    </div>
                    <div class="hero-shift">{turno_label} ({turno})</div>
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
                      <span>RMSE ±{MODEL_ERROR:.1f}%</span>
                      <span style="color:var(--green);">● Computed</span>
                    </div>
                  </div>
                </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# MODO 2 — CARGA MASIVA
# ══════════════════════════════════════════════════════════════════
else:
    st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)
    bulk_l, bulk_r = st.columns([3, 2], gap='large')

    with bulk_l:
        st.markdown('<div class="step-lbl"><span class="step-num">1</span>Descarga la plantilla CSV</div>',
                    unsafe_allow_html=True)
        st.markdown("""
            <div style="background:var(--bg-card);border:1px solid var(--b1);
                        border-left:2px solid var(--copper);border-radius:3px;
                        padding:0.7rem 1rem;margin-bottom:0.6rem;
                        font-size:0.76rem;color:var(--t2);line-height:1.5;">
                Plantilla con los 45 parámetros requeridos. Cada fila representa un turno.
                <br><span style="font-family:var(--mono);font-size:0.62rem;color:var(--t3);">
                ⓘ Los valores de utilización y disponibilidad en CSV deben ir como decimales (0–1).</span>
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
        st.download_button('⬇  Descargar Plantilla CSV', data=buf,
                           file_name='plantilla_prediccion.csv', mime='text/csv')

        st.markdown('<div class="step-lbl" style="margin-top:1rem;"><span class="step-num">2</span>Carga tu archivo</div>',
                    unsafe_allow_html=True)
        archivo = st.file_uploader('Arrastra tu CSV aquí o haz click para seleccionar',
                                   type=['csv'], label_visibility='visible')

    with bulk_r:
        st.markdown(f"""
            <div style="background:var(--bg-card);border:1px solid var(--b1);
                        border-radius:4px;padding:1rem 1.1rem;">
              <div style="font-family:var(--mono);font-size:0.52rem;color:var(--t3);
                          letter-spacing:2.5px;text-transform:uppercase;
                          margin-bottom:0.8rem;padding-bottom:6px;border-bottom:1px solid var(--b1);">
                Especificaciones del Modelo
              </div>
              <div style="display:flex;flex-direction:column;gap:6px;">
                <div style="display:flex;justify-content:space-between;font-size:0.68rem;padding:4px 0;border-bottom:1px solid var(--b1);">
                  <span style="color:var(--t2);font-family:var(--mono);">Variables numéricas</span>
                  <span style="color:var(--t1);font-family:var(--mono);">44</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.68rem;padding:4px 0;border-bottom:1px solid var(--b1);">
                  <span style="color:var(--t2);font-family:var(--mono);">Variable categórica</span>
                  <span style="color:var(--t1);font-family:var(--mono);">turno (D/N)</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.68rem;padding:4px 0;border-bottom:1px solid var(--b1);">
                  <span style="color:var(--t2);font-family:var(--mono);">Frentes mineros</span>
                  <span style="color:var(--copper-hi);font-family:var(--mono);">04</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.68rem;padding:4px 0;border-bottom:1px solid var(--b1);">
                  <span style="color:var(--t2);font-family:var(--mono);">Algoritmo</span>
                  <span style="color:var(--copper-hi);font-family:var(--mono);">Ensemble Reg.</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.68rem;padding:4px 0;">
                  <span style="color:var(--t2);font-family:var(--mono);">Confianza</span>
                  <span style="color:var(--green);font-family:var(--mono);">{CONFIDENCE:.1f}%</span>
                </div>
              </div>
            </div>
        """, unsafe_allow_html=True)

    if archivo:
        st.markdown('<hr>', unsafe_allow_html=True)
        try:
            df = pd.read_csv(archivo)
            faltantes = [c for c in COLUMNAS_ESPERADAS if c not in df.columns]
            if faltantes:
                st.error(f'❌ Columnas faltantes: {faltantes}')
                st.stop()

            st.success(f'✅ {len(df):,} turnos cargados correctamente')
            st.dataframe(df[COLUMNAS_ESPERADAS].head(3), use_container_width=True)

            st.markdown('<div class="step-lbl"><span class="step-num">3</span>Ejecuta la predicción masiva</div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="calc-wrap">', unsafe_allow_html=True)
            run_bulk = st.button('▸  Predecir todos los turnos', use_container_width=False)
            st.markdown('</div>', unsafe_allow_html=True)

            if run_bulk:
                Y = predecir(df[COLUMNAS_ESPERADAS].copy())
                df['Prediccion_Cargas'] = np.round(Y).astype(int)

                m1, m2, m3, m4 = st.columns(4)
                m1.metric('Turnos procesados',  f"{len(df):,}")
                m2.metric('Promedio de cargas', f"{df['Prediccion_Cargas'].mean():,.0f}")
                m3.metric('Mínimo',             f"{df['Prediccion_Cargas'].min():,}")
                m4.metric('Máximo',             f"{df['Prediccion_Cargas'].max():,}")

                st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
                cols_v = ['turno','Prediccion_Cargas'] + [c for c in COLUMNAS_ESPERADAS if c != 'turno']
                st.dataframe(df[cols_v], use_container_width=True)

                buf2 = io.BytesIO()
                df.to_csv(buf2, index=False)
                buf2.seek(0)
                st.download_button('⬇  Descargar Resultados', data=buf2,
                                   file_name='predicciones.csv', mime='text/csv')
                st.caption(f'⚠ Error del modelo: ±{MODEL_ERROR:.1f}% — Usar como referencia operacional.')

        except Exception as e:
            st.error(f'Error al procesar el archivo: {e}')
