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
# CSS — EXECUTIVE TERMINAL
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

:root {
    --bg-app:        #0F1115;
    --bg-card:       #161920;
    --bg-elev:       #1C2029;
    --bg-deep:       #0A0C10;

    --copper:        #A67C52;
    --copper-hi:     #C49770;
    --copper-dim:    rgba(166, 124, 82, 0.12);

    --green-pos:     #6BBE83;
    --green-dim:     rgba(107, 190, 131, 0.1);
    --red-neg:       #C76B6B;
    --amber:         #D4A857;

    --text-primary:  #E4E7ED;
    --text-secondary:#8B92A0;
    --text-muted:    #545B6A;
    --text-faint:    #353A45;

    --border-hair:   rgba(255,255,255,0.04);
    --border-line:   rgba(255,255,255,0.07);
    --border-strong: rgba(255,255,255,0.12);

    --font-sans: 'Inter', -apple-system, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
}

/* ═ Base ═ */
.stApp {
    background: var(--bg-app) !important;
}
html, body, [class*="css"], .stMarkdown, p, span, div {
    font-family: var(--font-sans) !important;
    color: var(--text-primary);
    -webkit-font-smoothing: antialiased;
}
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { visibility: hidden !important; display: none !important; }

.main .block-container {
    padding: 0 2rem 2rem 2rem !important;
    max-width: 1700px !important;
}

/* ═ Header ═ */
.cmd-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.1rem 0 0.9rem 0;
    border-bottom: 1px solid var(--border-hair);
    margin-bottom: 1.3rem;
}
.cmd-brand { display: flex; align-items: center; gap: 14px; }
.cmd-mark {
    width: 32px; height: 32px;
    background: var(--bg-elev);
    border: 1px solid var(--border-strong);
    border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.95rem;
    color: var(--copper);
}
.cmd-title {
    font-size: 0.95rem !important; font-weight: 600 !important;
    color: var(--text-primary) !important; letter-spacing: -0.2px;
    line-height: 1.15;
}
.cmd-sub {
    font-size: 0.65rem !important; color: var(--text-muted) !important;
    letter-spacing: 1.5px; text-transform: uppercase;
    font-family: var(--font-mono) !important;
    margin-top: 2px; font-weight: 400 !important;
}
.cmd-meta { display: flex; align-items: center; gap: 18px; }
.meta-item {
    display: flex; flex-direction: column; gap: 1px;
    text-align: right;
}
.meta-label {
    font-size: 0.56rem !important; color: var(--text-muted) !important;
    letter-spacing: 1.5px; text-transform: uppercase;
    font-family: var(--font-mono) !important;
}
.meta-value {
    font-size: 0.72rem !important; color: var(--text-secondary) !important;
    font-family: var(--font-mono) !important; font-weight: 500;
}
.status-live {
    display: flex; align-items: center; gap: 6px;
    font-size: 0.62rem !important; color: var(--green-pos) !important;
    letter-spacing: 1.2px; text-transform: uppercase;
    font-family: var(--font-mono) !important;
}
.status-dot {
    width: 6px; height: 6px; background: var(--green-pos);
    border-radius: 50%; box-shadow: 0 0 6px var(--green-pos);
    animation: pulse 2.4s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.35} }

/* ═ Radio (mode tabs) ═ */
.stRadio > div {
    display: flex !important; gap: 0 !important;
    background: transparent !important;
    border: none !important; padding: 0 !important;
    border-bottom: 1px solid var(--border-hair) !important;
    border-radius: 0 !important;
}
.stRadio > div > label {
    padding: 8px 18px 9px 18px !important;
    border-radius: 0 !important;
    font-size: 0.68rem !important; font-weight: 500 !important;
    letter-spacing: 1px !important; text-transform: uppercase;
    cursor: pointer;
    transition: all 0.15s !important;
    color: var(--text-muted) !important;
    background: transparent !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1px !important;
    font-family: var(--font-mono) !important;
}
.stRadio > div > label:hover { color: var(--text-secondary) !important; }
.stRadio > div > label:has(input:checked) {
    color: var(--copper-hi) !important;
    border-bottom-color: var(--copper) !important;
}

/* ═ Selectbox ═ */
div[data-testid="stSelectbox"] > label {
    font-size: 0.56rem !important; font-weight: 500 !important;
    color: var(--text-muted) !important; letter-spacing: 1.5px !important;
    text-transform: uppercase !important; margin-bottom: 4px !important;
    font-family: var(--font-mono) !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: transparent !important;
    border: none !important;
    border-bottom: 1px solid var(--border-line) !important;
    border-radius: 0 !important;
    color: var(--text-primary) !important;
    font-size: 0.85rem !important; min-height: 30px !important;
    font-family: var(--font-mono) !important;
}
div[data-testid="stSelectbox"] > div > div:hover { border-bottom-color: var(--copper) !important; }

/* ═ Buttons (secondary) ═ */
.stButton > button {
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important; font-weight: 500 !important;
    letter-spacing: 1.5px !important; text-transform: uppercase !important;
    border-radius: 3px !important; padding: 7px 14px !important;
    transition: all 0.18s !important; cursor: pointer !important;
    background: transparent !important; color: var(--text-secondary) !important;
    border: 1px solid var(--border-line) !important;
    width: 100%;
}
.stButton > button:hover {
    border-color: var(--copper) !important;
    color: var(--copper-hi) !important;
    background: var(--copper-dim) !important;
}

/* ═ Number Inputs — Line-only style ═ */
div[data-testid="stNumberInput"] { margin-bottom: 0 !important; }
div[data-testid="stNumberInput"] label {
    font-size: 0.58rem !important; font-weight: 500 !important;
    color: var(--text-muted) !important; letter-spacing: 1.2px !important;
    text-transform: uppercase !important; font-family: var(--font-mono) !important;
    margin-bottom: 1px !important; line-height: 1.2 !important;
}
div[data-testid="stNumberInput"] > div { gap: 0 !important; }
div[data-testid="stNumberInput"] input {
    background: transparent !important;
    color: var(--text-primary) !important;
    border: none !important;
    border-bottom: 1px solid var(--border-line) !important;
    border-radius: 0 !important;
    font-size: 0.88rem !important; font-family: var(--font-mono) !important;
    font-weight: 500 !important;
    padding: 3px 4px !important; height: 26px !important;
    transition: border-color 0.15s, color 0.15s !important;
}
div[data-testid="stNumberInput"] input:hover {
    border-bottom-color: var(--text-secondary) !important;
}
div[data-testid="stNumberInput"] input:focus {
    border-bottom-color: var(--copper) !important;
    color: var(--copper-hi) !important;
    outline: none !important;
    box-shadow: none !important;
}
div[data-testid="stNumberInput"] button {
    background: transparent !important;
    border: 1px solid var(--border-hair) !important;
    color: var(--text-muted) !important; height: 26px !important;
    min-width: 20px !important; padding: 0 4px !important;
    border-radius: 3px !important;
}
div[data-testid="stNumberInput"] button:hover {
    color: var(--copper) !important;
    border-color: var(--border-line) !important;
}

/* ═ Download / File / Dataframe / Metric ═ */
div[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    color: var(--copper-hi) !important;
    border: 1px solid rgba(166,124,82,0.3) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important; font-weight: 500 !important;
    letter-spacing: 1.5px !important; text-transform: uppercase !important;
    border-radius: 3px !important; padding: 7px 14px !important; width: auto !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: var(--copper-dim) !important;
    border-color: var(--copper) !important;
}

div[data-testid="stFileUploader"] > div {
    background: var(--bg-card) !important;
    border: 1px dashed var(--border-line) !important;
    border-radius: 4px !important; padding: 1.4rem !important;
}
div[data-testid="stFileUploader"] > div:hover {
    border-color: var(--copper) !important;
}

div[data-testid="stDataFrame"] {
    border-radius: 4px !important; overflow: hidden !important;
    border: 1px solid var(--border-hair) !important;
}

div[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-hair) !important;
    border-left: 2px solid var(--copper) !important;
    border-radius: 3px !important; padding: 0.7rem 1rem !important;
}
div[data-testid="stMetric"] label {
    font-size: 0.58rem !important; color: var(--text-muted) !important;
    letter-spacing: 1.5px !important; text-transform: uppercase !important;
    font-family: var(--font-mono) !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-family: var(--font-mono) !important;
    color: var(--text-primary) !important;
    font-size: 1.3rem !important; font-weight: 600 !important;
}

div[data-testid="stAlert"] {
    border-radius: 3px !important; border: 1px solid var(--border-hair) !important;
    font-size: 0.78rem !important; background: var(--bg-card) !important;
}
div[data-testid="stCaptionContainer"] {
    color: var(--text-muted) !important; font-size: 0.65rem !important;
    font-family: var(--font-mono) !important;
}
hr { border: none !important; border-top: 1px solid var(--border-hair) !important; margin: 0.8rem 0 !important; }
div[data-testid="stHorizontalBlock"] { gap: 0.8rem; }

/* ══ COMPONENT CLASSES ══ */

/* Pit card — minimalist with side accent */
.pit-card {
    background: var(--bg-card);
    border: 1px solid var(--border-hair);
    border-left: 2px solid var(--copper);
    border-radius: 3px;
    padding: 0.7rem 0.9rem 0.6rem 0.9rem;
    margin-bottom: 0.55rem;
}
.pit-head {
    display: flex; align-items: baseline; justify-content: space-between;
    padding-bottom: 0.45rem;
    border-bottom: 1px solid var(--border-hair);
    margin-bottom: 0.5rem;
}
.pit-head-l { display: flex; align-items: baseline; gap: 8px; }
.pit-name {
    font-size: 0.78rem !important; font-weight: 600 !important;
    color: var(--text-primary) !important;
    letter-spacing: 0.2px !important;
}
.pit-code {
    font-family: var(--font-mono) !important;
    font-size: 0.6rem !important; color: var(--text-muted) !important;
    letter-spacing: 1.2px !important;
}
.pit-meta {
    font-family: var(--font-mono) !important;
    font-size: 0.55rem !important; color: var(--text-muted) !important;
    letter-spacing: 1.2px !important; text-transform: uppercase;
}

/* Equipment model label — strip, no chip */
.eq-model {
    font-family: var(--font-mono) !important;
    font-size: 0.55rem !important; font-weight: 500 !important;
    letter-spacing: 1.8px !important; text-transform: uppercase;
    margin: 8px 0 3px 0;
    padding-left: 6px;
    border-left: 2px solid;
    line-height: 1.2;
}
.eq-model.pc8000 { color: #7B8FC4; border-left-color: rgba(123,143,196,0.5); }
.eq-model.pc4000 { color: #5FA8C4; border-left-color: rgba(95,168,196,0.5); }
.eq-model.ex3600 { color: #6BBEB6; border-left-color: rgba(107,190,182,0.5); }
.eq-model.be495  { color: #6BBE83; border-left-color: rgba(107,190,131,0.5); }
.eq-model.apron  { color: #C4885B; border-left-color: rgba(196,136,91,0.5); }

/* Trucks divider */
.trucks-div {
    border-top: 1px solid var(--border-hair);
    padding-top: 0.35rem; margin-top: 0.45rem;
}
.trucks-lbl {
    font-family: var(--font-mono) !important;
    font-size: 0.52rem !important; font-weight: 500 !important;
    color: var(--text-muted) !important; letter-spacing: 2.2px !important;
    text-transform: uppercase !important;
    margin-bottom: 0.25rem !important;
}

/* Pseudo-bar (input value indicator) */
.val-bar-wrap {
    width: 100%; height: 2px;
    background: var(--border-hair);
    margin-top: 2px;
    border-radius: 1px;
    overflow: hidden;
}
.val-bar {
    height: 100%;
    background: var(--copper);
    transition: width 0.3s ease;
}

/* Calc button — primary */
.calc-wrap .stButton > button {
    background: linear-gradient(180deg, #B68B5E 0%, #8C6440 100%) !important;
    color: #0F1115 !important;
    font-family: var(--font-sans) !important;
    font-size: 0.7rem !important; font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    border: none !important;
    border-radius: 4px !important; padding: 13px 22px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.15) !important;
    transition: all 0.18s !important; width: 100% !important;
}
.calc-wrap .stButton > button:hover {
    background: linear-gradient(180deg, #C49770 0%, #A67C52 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(166,124,82,0.4), inset 0 1px 0 rgba(255,255,255,0.2) !important;
}

/* Hero result — large lateral display */
.hero-result {
    background: var(--bg-card);
    border: 1px solid var(--border-hair);
    border-radius: 4px;
    padding: 1.8rem 2rem 1.6rem 2rem;
    position: relative;
    overflow: hidden;
    height: 100%;
    display: flex; flex-direction: column;
    justify-content: space-between;
    min-height: 280px;
}
.hero-result::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 2px; height: 100%;
    background: linear-gradient(180deg, var(--copper), transparent);
}
.hero-top {
    display: flex; justify-content: space-between; align-items: flex-start;
}
.hero-eyebrow {
    font-family: var(--font-mono) !important;
    font-size: 0.6rem !important; font-weight: 500 !important;
    color: var(--text-muted) !important; letter-spacing: 2.5px !important;
    text-transform: uppercase !important;
}
.hero-shift {
    font-family: var(--font-mono) !important;
    font-size: 0.6rem !important; color: var(--text-secondary) !important;
    letter-spacing: 1.5px !important; text-transform: uppercase;
    background: var(--bg-elev);
    border: 1px solid var(--border-hair);
    padding: 3px 9px; border-radius: 3px;
}
.hero-number {
    font-family: var(--font-mono) !important;
    font-size: 5.2rem !important; font-weight: 300 !important;
    color: var(--text-primary) !important;
    line-height: 0.95 !important;
    letter-spacing: -3px !important;
    margin: 0.6rem 0 0.4rem 0;
}
.hero-number.computed { color: var(--green-pos) !important; }
.hero-number.empty { color: var(--text-faint) !important; }
.hero-unit {
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important; color: var(--text-muted) !important;
    letter-spacing: 2px !important; text-transform: uppercase;
    margin-bottom: 1rem;
}
.hero-delta {
    display: inline-flex; align-items: center; gap: 6px;
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important; color: var(--green-pos) !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 1rem;
}
.hero-delta.empty { color: var(--text-faint) !important; }

/* Confidence section */
.conf-block {
    border-top: 1px solid var(--border-hair);
    padding-top: 0.9rem;
}
.conf-head {
    display: flex; justify-content: space-between; align-items: baseline;
    margin-bottom: 0.5rem;
}
.conf-lbl {
    font-family: var(--font-mono) !important;
    font-size: 0.58rem !important; color: var(--text-muted) !important;
    letter-spacing: 2px !important; text-transform: uppercase;
}
.conf-val {
    font-family: var(--font-mono) !important;
    font-size: 0.85rem !important; font-weight: 600 !important;
    color: var(--copper-hi) !important;
}
.conf-bar-bg {
    width: 100%; height: 4px;
    background: var(--bg-elev);
    border-radius: 2px;
    overflow: hidden;
    position: relative;
}
.conf-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--copper) 0%, var(--copper-hi) 100%);
    border-radius: 2px;
    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.conf-foot {
    display: flex; justify-content: space-between;
    margin-top: 0.45rem;
    font-family: var(--font-mono) !important;
    font-size: 0.55rem !important; color: var(--text-muted) !important;
    letter-spacing: 1px !important;
}
.conf-error {
    color: var(--amber) !important;
}

/* Cfg panel side */
.cfg-side {
    background: var(--bg-card);
    border: 1px solid var(--border-hair);
    border-radius: 4px;
    padding: 0.9rem 1.1rem;
    margin-top: 0.8rem;
}
.cfg-side-title {
    font-family: var(--font-mono) !important;
    font-size: 0.55rem !important; color: var(--text-muted) !important;
    letter-spacing: 2.5px !important; text-transform: uppercase;
    margin-bottom: 0.7rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-hair);
}
.cfg-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 5px 0;
    font-size: 0.7rem;
}
.cfg-key {
    color: var(--text-secondary);
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.3px;
}
.cfg-val {
    color: var(--text-primary);
    font-family: var(--font-mono) !important;
    font-size: 0.7rem !important;
    font-weight: 500;
}
.cfg-val.accent { color: var(--copper-hi); }

/* Step (bulk) */
.step-lbl {
    display: flex; align-items: center; gap: 10px;
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important; font-weight: 500 !important;
    color: var(--text-secondary) !important; letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    margin: 1rem 0 0.5rem 0;
}
.step-num {
    font-family: var(--font-mono) !important;
    width: 20px; height: 20px;
    border: 1px solid var(--copper);
    color: var(--copper-hi);
    border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 0.62rem; font-weight: 600;
    flex-shrink: 0;
    background: var(--copper-dim);
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--bg-elev); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--border-strong); }
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

# Defaults en PORCENTAJES (0-100) para los inputs visibles al usuario
DEFAULTS_CAM = {
    'DESCANSO': {'qty': 80.0, 'disp_pct': 80.0, 'uso_pct': 75.0, 'ciclo': 30.0},
    'DP5':      {'qty': 80.0, 'disp_pct': 80.0, 'uso_pct': 75.0, 'ciclo': 30.0},
    'EC':       {'qty': 15.0, 'disp_pct': 80.0, 'uso_pct': 75.0, 'ciclo': 28.0},
    'PRIBBENOW':{'qty': 68.0, 'disp_pct': 80.0, 'uso_pct': 75.0, 'ciclo': 26.0},
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

# Confianza fija — derivada del error ±1.5% del modelo
MODEL_ERROR_PCT = 1.5
CONFIDENCE_PCT  = 100 - MODEL_ERROR_PCT  # 98.5%

# ══════════════════════════════════════════════════════════════════
# SESSION STATE + RESET
# Inputs visibles al usuario: PORCENTAJES (0-100) para %, valores
# normales para Qty/Ciclo. Conversión a [0,1] al alimentar el modelo.
# ══════════════════════════════════════════════════════════════════
def reset_values():
    for pit, modelos in EQUIPOS_POR_PIT.items():
        for equipos in modelos.values():
            for eq in equipos:
                st.session_state[f'ni_{eq}'] = 75.0  # 75% por default
        src = DEFAULTS_CAM[pit]
        st.session_state[f'ni_qty_{pit}']     = float(src['qty'])
        st.session_state[f'ni_disp_{pit}']    = float(src['disp_pct'])  # 80% (no 0.80)
        st.session_state[f'ni_uso_{pit}']     = float(src['uso_pct'])   # 75%
        st.session_state[f'ni_ciclo_{pit}']   = float(src['ciclo'])

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
from datetime import datetime
hoy = datetime.now().strftime('%d %b %Y · %H:%M').upper()

st.markdown(f"""
<div class="cmd-header">
  <div class="cmd-brand">
    <div class="cmd-mark">◆</div>
    <div>
      <div class="cmd-title">LOAD FORECAST · COMPLEX</div>
      <div class="cmd-sub">Production Engineering / Ensemble ML v2.1</div>
    </div>
  </div>
  <div class="cmd-meta">
    <div class="meta-item">
      <span class="meta-label">Session</span>
      <span class="meta-value">{hoy}</span>
    </div>
    <div class="meta-item">
      <span class="meta-label">Pits</span>
      <span class="meta-value">04 / 04</span>
    </div>
    <div class="meta-item">
      <span class="meta-label">Status</span>
      <span class="status-live"><span class="status-dot"></span>Online</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MODE SELECTOR
# ══════════════════════════════════════════════════════════════════
modo = st.radio('', ['Predicción Manual', 'Carga Masiva'],
                horizontal=True, label_visibility='collapsed')


# ══════════════════════════════════════════════════════════════════
# MODO 1 — PREDICCIÓN MANUAL
# ══════════════════════════════════════════════════════════════════
if modo == 'Predicción Manual':

    st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)

    # ── Control row ─────────────────────────────────────────────
    cb1, cb2, _ = st.columns([1.2, 1.2, 6])
    with cb1:
        turno = st.selectbox('Turno de Operación', ['D', 'N'])
    with cb2:
        st.markdown('<div style="height:22px"></div>', unsafe_allow_html=True)
        if st.button('↺  Resetear valores'):
            reset_values()
            st.rerun()

    st.markdown('<div style="height:0.4rem"></div>', unsafe_allow_html=True)

    vals_palas, vals_camiones = {}, {}
    PITS = list(EQUIPOS_POR_PIT.keys())

    # ── 2×2 Pit grid ────────────────────────────────────────────
    for fila_pits in [PITS[:2], PITS[2:]]:
        pit_cols = st.columns(2, gap='small')

        for col_pit, pit in zip(pit_cols, fila_pits):
            with col_pit:
                pit_label = PIT_LABELS.get(pit, pit)
                eq_count  = sum(len(v) for v in EQUIPOS_POR_PIT[pit].values())

                st.markdown(
                    f'<div class="pit-card">'
                    f'<div class="pit-head">'
                    f'<div class="pit-head-l">'
                    f'<span class="pit-name">{pit_label}</span>'
                    f'<span class="pit-code">/ {pit}</span>'
                    f'</div>'
                    f'<span class="pit-meta">{eq_count} unidades</span>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )

                # Equipment rows
                for modelo_eq, equipos in EQUIPOS_POR_PIT[pit].items():
                    cls = EQ_MODEL_CLASS.get(modelo_eq, 'pc8000')
                    st.markdown(
                        f'<div class="eq-model {cls}">{modelo_eq}</div>',
                        unsafe_allow_html=True
                    )
                    eq_cols = st.columns(len(equipos))
                    for ec, eq in zip(eq_cols, equipos):
                        with ec:
                            # Input en porcentaje (0-100)
                            pct_val = st.number_input(
                                eq,
                                min_value=0.0, max_value=100.0,
                                step=1.0, format='%.1f',
                                key=f'ni_{eq}'
                            )
                            # Conversión interna a [0, 1] para el modelo
                            vals_palas[f'UsodeDisp_{eq}'] = pct_val / 100.0

                # Trucks
                st.markdown(
                    '<div class="trucks-div"><div class="trucks-lbl">'
                    'Flota de Camiones</div></div>',
                    unsafe_allow_html=True
                )
                t1, t2, t3, t4 = st.columns(4)
                with t1:
                    qty = st.number_input(
                        'Qty', min_value=0.0, max_value=200.0,
                        step=1.0, format='%.1f', key=f'ni_qty_{pit}')
                    vals_camiones[f'QtyCamiones_{pit}'] = qty
                with t2:
                    disp_pct = st.number_input(
                        'Disp %', min_value=0.0, max_value=100.0,
                        step=1.0, format='%.1f', key=f'ni_disp_{pit}')
                    vals_camiones[f'Disponibilidad_TKS_{pit}'] = disp_pct / 100.0
                with t3:
                    uso_pct = st.number_input(
                        'Uso %', min_value=0.0, max_value=100.0,
                        step=1.0, format='%.1f', key=f'ni_uso_{pit}')
                    vals_camiones[f'UsodeDisp_TKS_{pit}'] = uso_pct / 100.0
                with t4:
                    ciclo = st.number_input(
                        'Ciclo (min)', min_value=15.0, max_value=60.0,
                        step=0.1, format='%.1f', key=f'ni_ciclo_{pit}')
                    vals_camiones[COL_CICLO_MAP[pit]] = ciclo

    # ── Hero result + side ───────────────────────────────────────
    st.markdown('<hr>', unsafe_allow_html=True)
    hero_col, side_col = st.columns([2.4, 1])

    with side_col:
        st.markdown('<div class="calc-wrap">', unsafe_allow_html=True)
        calcular = st.button('▸  EJECUTAR PREDICCIÓN', use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
            <div class="cfg-side">
              <div class="cfg-side-title">Configuración Activa</div>
              <div class="cfg-row"><span class="cfg-key">Frentes Activos</span><span class="cfg-val">04</span></div>
              <div class="cfg-row"><span class="cfg-key">Variables Input</span><span class="cfg-val">45</span></div>
              <div class="cfg-row"><span class="cfg-key">Algoritmo</span><span class="cfg-val accent">Ensemble Reg.</span></div>
              <div class="cfg-row"><span class="cfg-key">Versión Modelo</span><span class="cfg-val">v2.1.0</span></div>
              <div class="cfg-row"><span class="cfg-key">Error RMSE</span><span class="cfg-val accent">±{MODEL_ERROR_PCT:.1f}%</span></div>
            </div>
        """, unsafe_allow_html=True)

    with hero_col:
        ph = st.empty()
        # Estado inicial (sin predicción)
        ph.markdown(f"""
            <div class="hero-result">
              <div class="hero-top">
                <div>
                  <div class="hero-eyebrow">Predicted Load Count</div>
                  <div class="hero-number empty">0,000</div>
                  <div class="hero-unit">loads · per shift</div>
                  <div class="hero-delta empty">—  awaiting input</div>
                </div>
                <div class="hero-shift">Shift —</div>
              </div>
              <div class="conf-block">
                <div class="conf-head">
                  <span class="conf-lbl">Model Confidence</span>
                  <span class="conf-val">{CONFIDENCE_PCT:.1f}%</span>
                </div>
                <div class="conf-bar-bg">
                  <div class="conf-bar-fill" style="width:{CONFIDENCE_PCT}%"></div>
                </div>
                <div class="conf-foot">
                  <span>RMSE ±{MODEL_ERROR_PCT:.1f}%</span>
                  <span class="conf-error">Pending execution</span>
                </div>
              </div>
            </div>
        """, unsafe_allow_html=True)

    if calcular:
        datos  = {**vals_palas, **vals_camiones, 'turno': turno}
        data   = pd.DataFrame([datos])[COLUMNAS_ESPERADAS]
        Y_pred = predecir(data)
        cargas = int(round(Y_pred[0]))
        turno_label = 'Diurno (D)' if turno == 'D' else 'Nocturno (N)'

        # Banda de incertidumbre
        margen = int(round(cargas * MODEL_ERROR_PCT / 100))
        rango_lo = cargas - margen
        rango_hi = cargas + margen

        ph.markdown(f"""
            <div class="hero-result">
              <div class="hero-top">
                <div>
                  <div class="hero-eyebrow">Predicted Load Count</div>
                  <div class="hero-number computed">{cargas:,}</div>
                  <div class="hero-unit">loads · per shift</div>
                  <div class="hero-delta">▴ rango {rango_lo:,} – {rango_hi:,}</div>
                </div>
                <div class="hero-shift">Shift {turno_label}</div>
              </div>
              <div class="conf-block">
                <div class="conf-head">
                  <span class="conf-lbl">Model Confidence</span>
                  <span class="conf-val">{CONFIDENCE_PCT:.1f}%</span>
                </div>
                <div class="conf-bar-bg">
                  <div class="conf-bar-fill" style="width:{CONFIDENCE_PCT}%"></div>
                </div>
                <div class="conf-foot">
                  <span>RMSE ±{MODEL_ERROR_PCT:.1f}%</span>
                  <span style="color:var(--green-pos);">● Prediction computed</span>
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
        st.markdown(
            '<div class="step-lbl"><span class="step-num">1</span>Descarga la plantilla CSV</div>',
            unsafe_allow_html=True
        )
        st.markdown("""
            <div style="background:var(--bg-card);border:1px solid var(--border-hair);
                        border-left:2px solid var(--copper);
                        border-radius:3px;padding:0.7rem 1rem;margin-bottom:0.6rem;
                        font-size:0.78rem;color:var(--text-secondary);line-height:1.5;">
                Plantilla con los 45 parámetros requeridos. Cada fila representa un turno de operación.
                <br><span style="font-family:var(--font-mono);font-size:0.65rem;color:var(--text-muted);
                                letter-spacing:1px;">
                ⓘ Los valores % en plantilla CSV deben ir como decimales (0–1), no como porcentajes.</span>
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
            '<div class="step-lbl" style="margin-top:1rem;"><span class="step-num">2</span>Carga tu archivo</div>',
            unsafe_allow_html=True
        )
        archivo = st.file_uploader(
            'Arrastra tu CSV aquí o haz click para seleccionar',
            type=['csv'], label_visibility='visible'
        )

    with bulk_r:
        st.markdown(f"""
            <div class="cfg-side" style="margin-top:0;">
              <div class="cfg-side-title">Especificaciones del Modelo</div>
              <div class="cfg-row"><span class="cfg-key">Variables Numéricas</span><span class="cfg-val">44</span></div>
              <div class="cfg-row"><span class="cfg-key">Variable Categórica</span><span class="cfg-val">turno (D/N)</span></div>
              <div class="cfg-row"><span class="cfg-key">Frentes Mineros</span><span class="cfg-val accent">04</span></div>
              <div class="cfg-row"><span class="cfg-key">Algoritmo</span><span class="cfg-val accent">Ensemble Reg.</span></div>
              <div class="cfg-row"><span class="cfg-key">Versión</span><span class="cfg-val">v2.1.0</span></div>
              <div class="cfg-row">
                <span class="cfg-key">Confianza</span>
                <span class="cfg-val" style="color:var(--green-pos);">{CONFIDENCE_PCT:.1f}%</span>
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
                '<div class="step-lbl"><span class="step-num">3</span>Ejecuta la predicción masiva</div>',
                unsafe_allow_html=True
            )
            st.markdown('<div class="calc-wrap">', unsafe_allow_html=True)
            run_bulk = st.button('▸  PREDECIR TODOS LOS TURNOS', use_container_width=False)
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
                st.caption(f'⚠ Error del modelo: ±{MODEL_ERROR_PCT:.1f}% — Usar como referencia operacional.')

        except Exception as e:
            st.error(f'Error al procesar el archivo: {e}')
