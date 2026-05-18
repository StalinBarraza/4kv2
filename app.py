# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import pickle
import streamlit as st
import io

st.set_page_config(
    page_title='Load Forecast — Complex',
    page_icon='⛏️',
    layout='wide',
    initial_sidebar_state='collapsed'
)

# ══════════════════════════════════════════════════════════════════
# CSS — COMPACT OBSIDIAN
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-void:       #08090C;
    --bg-deep:       #0C0F15;
    --bg-surface:    #10141C;
    --bg-raised:     #161D2B;
    --bg-card:       rgba(20, 26, 40, 0.85);

    --copper:        #D4822A;
    --copper-dim:    rgba(212, 130, 42, 0.15);
    --cyan:          #3EC9C1;
    --cyan-dim:      rgba(62, 201, 193, 0.12);
    --green-neo:     #35C97A;
    --green-dim:     rgba(53, 201, 122, 0.12);

    --text-primary:  #DDE4F0;
    --text-secondary:#6B7E9E;
    --text-muted:    #3A4558;

    --border-subtle: rgba(255,255,255,0.045);
    --border-mid:    rgba(255,255,255,0.08);
    --border-accent: rgba(212, 130, 42, 0.28);

    --shadow-copper: 0 0 24px rgba(212,130,42,0.1);
    --shadow-cyan:   0 0 16px rgba(62,201,193,0.08);

    --r-sm: 5px;
    --r-md: 8px;
    --r-lg: 12px;
    --r-xl: 16px;

    --font-display: 'Syne', sans-serif;
    --font-body:    'DM Sans', sans-serif;
    --font-mono:    'JetBrains Mono', monospace;
}

/* ── Reset ── */
.stApp {
    background: var(--bg-void) !important;
    background-image:
        radial-gradient(ellipse 70% 40% at 50% 0%, rgba(212,130,42,0.035) 0%, transparent 55%),
        radial-gradient(ellipse 50% 35% at 90% 100%, rgba(62,201,193,0.025) 0%, transparent 50%) !important;
}
html, body, [class*="css"], .stMarkdown, p, span, div {
    font-family: var(--font-body) !important;
    color: var(--text-primary);
}
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { visibility: hidden !important; display: none !important; }

.main .block-container {
    padding: 0 1.4rem 2rem 1.4rem !important;
    max-width: 1700px !important;
}

/* ── Header ── */
.cmd-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 0 0.8rem 0;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 1rem;
}
.cmd-logo {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, var(--copper) 0%, #9E5C18 100%);
    border-radius: var(--r-md);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
    box-shadow: var(--shadow-copper);
}
.cmd-title {
    font-family: var(--font-display) !important;
    font-size: 1.05rem !important; font-weight: 800 !important;
    color: var(--text-primary) !important; letter-spacing: 0.3px; line-height: 1.1;
}
.cmd-subtitle {
    font-size: 0.62rem !important; color: var(--text-muted) !important;
    letter-spacing: 2px; text-transform: uppercase; margin-top: 1px;
}
.cmd-header-left { display: flex; align-items: center; gap: 10px; }
.cmd-header-right { display: flex; align-items: center; gap: 14px; }
.status-pill {
    display: flex; align-items: center; gap: 6px;
    background: var(--green-dim); border: 1px solid rgba(53,201,122,0.18);
    border-radius: 20px; padding: 3px 10px;
    font-size: 0.62rem; color: var(--green-neo);
    letter-spacing: 1px; text-transform: uppercase;
    font-family: var(--font-mono) !important;
}
.status-dot {
    width: 6px; height: 6px; background: var(--green-neo);
    border-radius: 50%; box-shadow: 0 0 5px var(--green-neo);
    animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.35} }
.version-tag {
    font-family: var(--font-mono) !important;
    font-size: 0.58rem !important; color: var(--text-muted) !important;
    background: var(--bg-raised); border: 1px solid var(--border-subtle);
    border-radius: var(--r-sm); padding: 2px 8px;
}

/* ── Radio / Tabs ── */
.stRadio > div {
    display: flex !important; gap: 3px !important;
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--r-md) !important;
    padding: 3px !important; width: fit-content;
}
.stRadio > div > label {
    padding: 5px 14px !important; border-radius: var(--r-sm) !important;
    font-size: 0.7rem !important; font-weight: 600 !important;
    letter-spacing: 0.4px !important; cursor: pointer;
    transition: all 0.15s !important; color: var(--text-secondary) !important;
    background: transparent !important;
}
.stRadio > div > label:hover { background: var(--bg-raised) !important; color: var(--text-primary) !important; }

/* ── Selectbox ── */
div[data-testid="stSelectbox"] > label {
    font-size: 0.58rem !important; font-weight: 600 !important;
    color: var(--text-muted) !important; letter-spacing: 1.8px !important;
    text-transform: uppercase !important; margin-bottom: 3px !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: var(--bg-raised) !important; border: 1px solid var(--border-mid) !important;
    border-radius: var(--r-sm) !important; color: var(--text-primary) !important;
    font-size: 0.76rem !important; min-height: 30px !important;
}
div[data-testid="stSelectbox"] > div > div:hover { border-color: var(--border-accent) !important; }

/* ── Buttons ── */
.stButton > button {
    font-family: var(--font-display) !important;
    font-size: 0.65rem !important; font-weight: 700 !important;
    letter-spacing: 1.2px !important; text-transform: uppercase !important;
    border-radius: var(--r-sm) !important; padding: 7px 14px !important;
    transition: all 0.18s ease !important; cursor: pointer !important; width: 100%;
    background: var(--bg-raised) !important; color: var(--text-secondary) !important;
    border: 1px solid var(--border-mid) !important;
}
.stButton > button:hover {
    border-color: var(--border-accent) !important;
    color: var(--copper) !important;
}

/* ── Number Inputs — COMPACT ── */
div[data-testid="stNumberInput"] { margin-bottom: 0 !important; }
div[data-testid="stNumberInput"] label {
    font-size: 0.55rem !important; font-weight: 500 !important;
    color: var(--text-muted) !important; letter-spacing: 1.2px !important;
    text-transform: uppercase !important; font-family: var(--font-mono) !important;
    margin-bottom: 1px !important; line-height: 1.2 !important;
}
div[data-testid="stNumberInput"] > div { gap: 0 !important; }
div[data-testid="stNumberInput"] input {
    background: var(--bg-void) !important; color: var(--text-primary) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--r-sm) !important;
    font-size: 0.74rem !important; font-family: var(--font-mono) !important;
    padding: 3px 6px !important; height: 26px !important;
    transition: border-color 0.15s !important;
}
div[data-testid="stNumberInput"] input:focus {
    border-color: var(--copper) !important;
    box-shadow: 0 0 0 2px var(--copper-dim) !important; outline: none !important;
}
div[data-testid="stNumberInput"] button {
    background: var(--bg-raised) !important; border: 1px solid var(--border-subtle) !important;
    color: var(--text-secondary) !important; height: 26px !important;
    min-width: 22px !important; padding: 0 4px !important;
}
div[data-testid="stNumberInput"] button:hover { color: var(--copper) !important; }

/* ── Download Button ── */
div[data-testid="stDownloadButton"] > button {
    background: var(--bg-raised) !important; color: var(--cyan) !important;
    border: 1px solid rgba(62,201,193,0.22) !important;
    font-size: 0.65rem !important; font-weight: 700 !important;
    letter-spacing: 1px !important; text-transform: uppercase !important;
    border-radius: var(--r-sm) !important; padding: 7px 14px !important; width: auto !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: var(--cyan-dim) !important; box-shadow: var(--shadow-cyan) !important;
}

/* ── File Uploader ── */
div[data-testid="stFileUploader"] > div {
    background: var(--bg-surface) !important;
    border: 1px dashed rgba(62,201,193,0.2) !important;
    border-radius: var(--r-lg) !important; padding: 1.2rem !important;
}
div[data-testid="stFileUploader"] > div:hover {
    border-color: rgba(62,201,193,0.4) !important; background: var(--bg-raised) !important;
}

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {
    border-radius: var(--r-md) !important; overflow: hidden !important;
    border: 1px solid var(--border-subtle) !important;
}

/* ── Metric ── */
div[data-testid="stMetric"] {
    background: var(--bg-raised) !important; border: 1px solid var(--border-subtle) !important;
    border-radius: var(--r-md) !important; padding: 0.7rem 0.9rem !important;
}
div[data-testid="stMetric"] label {
    font-size: 0.58rem !important; color: var(--text-muted) !important;
    letter-spacing: 1.8px !important; text-transform: uppercase !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-family: var(--font-display) !important; color: var(--cyan) !important;
    font-size: 1.3rem !important;
}

/* ── Misc ── */
div[data-testid="stAlert"] { border-radius: var(--r-md) !important; border: none !important; font-size: 0.76rem !important; }
div[data-testid="stCaptionContainer"] { color: var(--text-muted) !important; font-size: 0.62rem !important; font-family: var(--font-mono) !important; }
hr { border: none !important; border-top: 1px solid var(--border-subtle) !important; margin: 0.8rem 0 !important; }
div[data-testid="stHorizontalBlock"] { gap: 0.6rem; }

/* ══ COMPONENT CLASSES ══ */

.pit-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-top: 2px solid var(--copper);
    border-radius: var(--r-lg);
    padding: 0.55rem 0.75rem 0.45rem 0.75rem;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    margin-bottom: 0.45rem;
}
.pit-header-row {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 0.4rem;
}
.pit-name {
    font-family: var(--font-display) !important;
    font-size: 0.72rem !important; font-weight: 800 !important;
    color: var(--copper) !important; letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
.pit-badge {
    font-family: var(--font-mono) !important;
    font-size: 0.5rem !important; color: var(--text-muted) !important;
    background: var(--bg-deep); border: 1px solid var(--border-subtle);
    border-radius: 3px; padding: 1px 5px; letter-spacing: 0.8px;
}
.eq-chip {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 1px 7px 1px 5px; border-radius: 20px;
    font-size: 0.52rem !important; font-weight: 700 !important;
    font-family: var(--font-mono) !important; text-transform: uppercase;
    border: 1px solid transparent; margin: 2px 0 2px 0;
}
.eq-chip.pc8000 { background: rgba(25,32,80,0.9); color: #6E82C8; border-color: rgba(110,130,200,0.18); }
.eq-chip.pc4000 { background: rgba(5,75,108,0.7); color: #55AECB; border-color: rgba(85,174,203,0.18); }
.eq-chip.ex3600 { background: rgba(2,100,112,0.6); color: var(--cyan); border-color: rgba(62,201,193,0.18); }
.eq-chip.be495  { background: rgba(35,75,36,0.6); color: #6CC86C; border-color: rgba(108,200,108,0.18); }
.eq-chip.apron  { background: rgba(140,60,0,0.4); color: #E08840; border-color: rgba(224,136,64,0.18); }

.trucks-row {
    border-top: 1px solid var(--border-subtle);
    padding-top: 0.3rem; margin-top: 0.35rem;
}
.trucks-lbl {
    font-size: 0.5rem !important; font-weight: 700 !important;
    color: var(--text-muted) !important; letter-spacing: 2.5px !important;
    text-transform: uppercase !important; font-family: var(--font-mono) !important;
    margin-bottom: 0.2rem !important;
}

.calc-wrap .stButton > button {
    background: linear-gradient(135deg, var(--copper) 0%, #A85E18 100%) !important;
    color: #08090C !important; font-family: var(--font-display) !important;
    font-size: 0.68rem !important; font-weight: 800 !important;
    letter-spacing: 2px !important; border: none !important;
    border-radius: var(--r-md) !important; padding: 11px 20px !important;
    box-shadow: 0 4px 16px rgba(212,130,42,0.3) !important;
    transition: all 0.18s !important; width: 100% !important;
}
.calc-wrap .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(212,130,42,0.45) !important;
}

.result-box {
    background: var(--bg-card);
    border: 1px solid var(--border-mid);
    border-radius: var(--r-xl);
    padding: 1.4rem 1.6rem;
    text-align: center;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    position: relative; overflow: hidden;
    height: 100%; display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 0.15rem;
}
.result-box::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--copper) 40%, transparent);
}
.result-box::after {
    content: ''; position: absolute; bottom: -30px; right: -30px;
    width: 120px; height: 120px;
    background: radial-gradient(circle, rgba(212,130,42,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.res-eyebrow {
    font-size: 0.55rem !important; font-weight: 700 !important;
    color: var(--text-muted) !important; letter-spacing: 3.5px !important;
    text-transform: uppercase !important; font-family: var(--font-mono) !important;
}
.res-num {
    font-family: var(--font-display) !important;
    font-size: 4rem !important; font-weight: 800 !important;
    color: var(--green-neo) !important; line-height: 1 !important;
    letter-spacing: -2px !important;
    text-shadow: 0 0 32px rgba(53,201,122,0.28) !important;
}
.res-num.empty { color: var(--bg-raised) !important; text-shadow: none !important; }
.res-unit {
    font-size: 0.6rem !important; color: var(--text-muted) !important;
    letter-spacing: 2.5px !important; text-transform: uppercase !important;
    font-family: var(--font-mono) !important;
}
.res-tag {
    display: inline-flex; align-items: center; gap: 5px;
    background: var(--bg-raised); border: 1px solid var(--border-subtle);
    border-radius: 20px; padding: 3px 10px; margin-top: 0.4rem;
    font-size: 0.58rem !important; color: var(--text-secondary) !important;
    font-family: var(--font-mono) !important;
}
.res-err {
    font-size: 0.56rem !important; color: var(--copper) !important;
    font-family: var(--font-mono) !important; letter-spacing: 0.8px !important;
    margin-top: 0.15rem !important;
}

.cfg-panel {
    background: rgba(0,0,0,0.22);
    border: 1px solid var(--border-subtle);
    border-radius: var(--r-md);
    padding: 0.65rem 0.85rem;
    margin-top: 0.65rem;
}
.cfg-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 4px 0; border-bottom: 1px solid var(--border-subtle);
    font-size: 0.66rem;
}
.cfg-row:last-child { border-bottom: none; }
.cfg-key { color: var(--text-secondary); }
.cfg-val-cyan   { color: var(--cyan);   font-family: var(--font-mono); }
.cfg-val-copper { color: var(--copper); font-family: var(--font-mono); }

.step-lbl {
    display: flex; align-items: center; gap: 8px;
    font-family: var(--font-display) !important;
    font-size: 0.66rem !important; font-weight: 700 !important;
    color: var(--text-secondary) !important; letter-spacing: 1.2px !important;
    text-transform: uppercase !important; margin: 1rem 0 0.5rem 0;
}
.step-circ {
    width: 20px; height: 20px; background: var(--copper); border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 0.6rem; font-weight: 800; color: #08090C; flex-shrink: 0;
}

::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--bg-raised); border-radius: 2px; }
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

EQ_CHIP_CLASS = {
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
    'DESCANSO': {'qty': 80.0, 'disp': 0.800, 'uso': 0.750, 'ciclo': 30.0},
    'DP5':      {'qty': 80.0, 'disp': 0.800, 'uso': 0.750, 'ciclo': 30.0},
    'EC':       {'qty': 15.0, 'disp': 0.800, 'uso': 0.750, 'ciclo': 28.0},
    'PRIBBENOW':{'qty': 68.0, 'disp': 0.800, 'uso': 0.750, 'ciclo': 26.0},
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
# SESSION STATE + RESET
# Fix: escribir directamente sobre las widget-keys 'ni_*'
# ══════════════════════════════════════════════════════════════════
def reset_values():
    for pit, modelos in EQUIPOS_POR_PIT.items():
        for equipos in modelos.values():
            for eq in equipos:
                st.session_state[f'ni_{eq}'] = 0.75
        src = DEFAULTS_CAM[pit]
        st.session_state[f'ni_qty_{pit}']  = float(src['qty'])
        st.session_state[f'ni_disp_{pit}'] = float(src['disp'])
        st.session_state[f'ni_uso_{pit}']  = float(src['uso'])
        st.session_state[f'ni_ciclo_{pit}']= float(src['ciclo'])

if 'initialized' not in st.session_state:
    reset_values()
    st.session_state['initialized'] = True

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
st.markdown("""
<div class="cmd-header">
  <div class="cmd-header-left">
    <div class="cmd-logo">⛏</div>
    <div>
      <div class="cmd-title">Load Forecast Simulator</div>
      <div class="cmd-subtitle">Complex Ops · Ensemble ML v2.1</div>
    </div>
  </div>
  <div class="cmd-header-right">
    <div class="status-pill"><span class="status-dot"></span>Model Online</div>
    <div class="version-tag">v2.1.0</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MODE SELECTOR
# ══════════════════════════════════════════════════════════════════
modo = st.radio('', ['📊  Predicción Manual', '📁  Carga Masiva'],
                horizontal=True, label_visibility='collapsed')
st.markdown('<hr>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# MODO 1 — PREDICCIÓN MANUAL
# ══════════════════════════════════════════════════════════════════
if modo == '📊  Predicción Manual':

    # ── Control bar ──────────────────────────────────────────────
    cb1, cb2, cb3 = st.columns([1, 1, 5])
    with cb1:
        turno = st.selectbox('Turno', ['D', 'N'])
    with cb2:
        st.markdown('<div style="height:22px"></div>', unsafe_allow_html=True)
        if st.button('↺  Resetear'):
            reset_values()
            st.rerun()

    st.markdown('<div style="height:2px"></div>', unsafe_allow_html=True)

    vals_palas, vals_camiones = {}, {}
    PITS = list(EQUIPOS_POR_PIT.keys())

    # ── 2×2 Pit grid ─────────────────────────────────────────────
    for fila_pits in [PITS[:2], PITS[2:]]:
        pit_cols = st.columns(2, gap='small')

        for col_pit, pit in zip(pit_cols, fila_pits):
            with col_pit:
                pit_label = PIT_LABELS.get(pit, pit)
                eq_count  = sum(len(v) for v in EQUIPOS_POR_PIT[pit].values())

                st.markdown(
                    f'<div class="pit-card">'
                    f'<div class="pit-header-row">'
                    f'<span class="pit-name">◆ {pit_label}</span>'
                    f'<span class="pit-badge">{pit} · {eq_count} EQ</span>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )

                for modelo_eq, equipos in EQUIPOS_POR_PIT[pit].items():
                    chip_cls = EQ_CHIP_CLASS.get(modelo_eq, 'pc8000')
                    st.markdown(
                        f'<span class="eq-chip {chip_cls}">◉ {modelo_eq}</span>',
                        unsafe_allow_html=True
                    )
                    eq_cols = st.columns(len(equipos))
                    for ec, eq in zip(eq_cols, equipos):
                        with ec:
                            vals_palas[f'UsodeDisp_{eq}'] = st.number_input(
                                eq,
                                min_value=0.0, max_value=1.0,
                                step=0.01, format='%.2f',
                                key=f'ni_{eq}'
                            )

                # Trucks
                st.markdown(
                    '<div class="trucks-row"><div class="trucks-lbl">▶ Camiones</div></div>',
                    unsafe_allow_html=True
                )
                t1, t2, t3, t4 = st.columns(4)
                with t1:
                    vals_camiones[f'QtyCamiones_{pit}'] = st.number_input(
                        'Qty', min_value=0.0, max_value=200.0,
                        step=1.0, format='%.1f', key=f'ni_qty_{pit}')
                with t2:
                    vals_camiones[f'Disponibilidad_TKS_{pit}'] = st.number_input(
                        'Disp', min_value=0.0, max_value=1.0,
                        step=0.01, format='%.3f', key=f'ni_disp_{pit}')
                with t3:
                    vals_camiones[f'UsodeDisp_TKS_{pit}'] = st.number_input(
                        'Uso', min_value=0.0, max_value=1.0,
                        step=0.01, format='%.3f', key=f'ni_uso_{pit}')
                with t4:
                    vals_camiones[COL_CICLO_MAP[pit]] = st.number_input(
                        'Ciclo', min_value=15.0, max_value=60.0,
                        step=0.1, format='%.1f', key=f'ni_ciclo_{pit}')

    # ── Predict row ───────────────────────────────────────────────
    st.markdown('<hr>', unsafe_allow_html=True)
    btn_col, _, res_col = st.columns([1.4, 0.15, 2.6])

    with btn_col:
        st.markdown('<div class="calc-wrap">', unsafe_allow_html=True)
        calcular = st.button('▶  CALCULAR PREDICCIÓN', use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="cfg-panel">
              <div style="font-size:0.52rem;color:var(--text-muted);letter-spacing:2.5px;
                          text-transform:uppercase;font-family:var(--font-mono);margin-bottom:6px;">
                Configuración activa
              </div>
              <div class="cfg-row"><span class="cfg-key">Frentes activos</span><span class="cfg-val-cyan">4</span></div>
              <div class="cfg-row"><span class="cfg-key">Variables input</span><span class="cfg-val-cyan">45</span></div>
              <div class="cfg-row"><span class="cfg-key">Algoritmo</span><span class="cfg-val-copper">Ensemble v2.1</span></div>
            </div>
        """, unsafe_allow_html=True)

    with res_col:
        ph = st.empty()
        ph.markdown("""
            <div class="result-box">
              <div class="res-eyebrow">Predicted Load Count</div>
              <div class="res-num empty">—</div>
              <div class="res-unit">loads / shift</div>
              <div class="res-tag">Ingresa parámetros y presiona Calcular</div>
            </div>
        """, unsafe_allow_html=True)

    if calcular:
        datos  = {**vals_palas, **vals_camiones, 'turno': turno}
        data   = pd.DataFrame([datos])[COLUMNAS_ESPERADAS]
        Y_pred = predecir(data)
        cargas = int(round(Y_pred[0]))
        turno_label = 'Diurno (D)' if turno == 'D' else 'Nocturno (N)'
        ph.markdown(f"""
            <div class="result-box">
              <div class="res-eyebrow">Predicted Load Count</div>
              <div class="res-num">{cargas:,}</div>
              <div class="res-unit">loads / shift</div>
              <div class="res-tag">✏ Manual &nbsp;·&nbsp; Turno {turno_label}</div>
              <div class="res-err">⚠ Model error: ±1.5%</div>
            </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# MODO 2 — CARGA MASIVA
# ══════════════════════════════════════════════════════════════════
else:
    bulk_l, bulk_r = st.columns([3, 2], gap='large')

    with bulk_l:
        st.markdown(
            '<div class="step-lbl"><span class="step-circ">1</span>Descarga la plantilla CSV</div>',
            unsafe_allow_html=True
        )
        st.markdown("""
            <div style="background:var(--bg-raised);border:1px solid var(--border-subtle);
                        border-radius:var(--r-md);padding:0.65rem 0.85rem;margin-bottom:0.5rem;
                        font-size:0.7rem;color:var(--text-secondary);line-height:1.5;">
                Plantilla con los 45 parámetros requeridos. Cada fila = un turno de operación.
            </div>
        """, unsafe_allow_html=True)

        ej = {col: 0.75 for col in COLS_NUMERICAS}
        ej.update({
            'QtyCamiones_DESCANSO': 89.7,   'Disponibilidad_TKS_DESCANSO': 0.664,
            'UsodeDisp_TKS_DESCANSO': 0.834, 'TiempoCiclo_TKS_DESCANSO': 30.62,
            'QtyCamiones_DP5': 81.9,         'Disponibilidad_TKS_DP5': 0.925,
            'UsodeDisp_TKS_DP5': 0.860,      'TiempoCiclo2_DP5': 32.72,
            'QtyCamiones_EC': 15.55,          'Disponibilidad_TKS_EC': 0.942,
            'UsodeDisp_TKS_EC': 0.814,        'TiempoCiclo2_EC': 28.32,
            'QtyCamiones_PRIBBENOW': 67.95,  'Disponibilidad_TKS_PRIBBENOW': 0.716,
            'UsodeDisp_TKS_PRIBBENOW': 0.865,'TiempoCiclo_TKS_PRIBBENOW': 25.60,
            'turno': 'D'
        })
        buf = io.BytesIO()
        pd.DataFrame([ej]).to_csv(buf, index=False)
        buf.seek(0)
        st.download_button('⬇  Descargar Plantilla CSV', data=buf,
                           file_name='plantilla_prediccion.csv', mime='text/csv')

        st.markdown(
            '<div class="step-lbl" style="margin-top:0.9rem;"><span class="step-circ">2</span>Carga tu archivo</div>',
            unsafe_allow_html=True
        )
        archivo = st.file_uploader(
            'Arrastra tu CSV aquí o haz click para seleccionar',
            type=['csv'], label_visibility='visible'
        )

    with bulk_r:
        st.markdown("""
            <div style="background:var(--bg-card);border:1px solid var(--border-subtle);
                        border-radius:var(--r-xl);padding:1rem 1.1rem;backdrop-filter:blur(10px);">
              <div style="font-size:0.52rem;color:var(--text-muted);letter-spacing:3px;
                          text-transform:uppercase;font-family:var(--font-mono);margin-bottom:0.7rem;">
                Especificaciones del modelo
              </div>
              <div class="cfg-row"><span class="cfg-key">Variables numéricas</span><span class="cfg-val-cyan">44</span></div>
              <div class="cfg-row"><span class="cfg-key">Variable categórica</span><span class="cfg-val-cyan">turno (D/N)</span></div>
              <div class="cfg-row"><span class="cfg-key">Frentes mineros</span><span class="cfg-val-copper">4</span></div>
              <div class="cfg-row"><span class="cfg-key">Algoritmo</span><span class="cfg-val-copper">Ensemble Reg.</span></div>
              <div class="cfg-row" style="border-bottom:none;">
                <span class="cfg-key">Error estimado</span>
                <span style="color:var(--green-neo);font-family:var(--font-mono);">±1.5%</span>
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

            st.markdown(
                '<div class="step-lbl"><span class="step-circ">3</span>Ejecuta la predicción masiva</div>',
                unsafe_allow_html=True
            )
            st.markdown('<div class="calc-wrap">', unsafe_allow_html=True)
            run_bulk = st.button('▶  PREDECIR TODOS LOS TURNOS', use_container_width=False)
            st.markdown('</div>', unsafe_allow_html=True)

            if run_bulk:
                Y = predecir(df[COLUMNAS_ESPERADAS].copy())
                df['Prediccion_Cargas'] = np.round(Y).astype(int)

                m1, m2, m3, m4 = st.columns(4)
                m1.metric('Turnos procesados', f"{len(df):,}")
                m2.metric('Promedio de cargas', f"{df['Prediccion_Cargas'].mean():,.0f}")
                m3.metric('Mínimo', f"{df['Prediccion_Cargas'].min():,}")
                m4.metric('Máximo', f"{df['Prediccion_Cargas'].max():,}")

                st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
                cols_v = ['turno', 'Prediccion_Cargas'] + [c for c in COLUMNAS_ESPERADAS if c != 'turno']
                st.dataframe(df[cols_v], use_container_width=True)

                buf2 = io.BytesIO()
                df.to_csv(buf2, index=False)
                buf2.seek(0)
                st.download_button('⬇  Descargar Resultados', data=buf2,
                                   file_name='predicciones.csv', mime='text/csv')
                st.caption('⚠ Error del modelo: ±1.5% — Usar como referencia operacional.')

        except Exception as e:
            st.error(f'Error al procesar el archivo: {e}')
