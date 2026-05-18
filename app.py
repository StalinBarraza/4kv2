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
# OBSIDIAN COMMAND CENTER — CSS
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ───────────────────────────────────────────── */
:root {
    --bg-void:       #0A0C0F;
    --bg-deep:       #0E1117;
    --bg-surface:    #131820;
    --bg-raised:     #1A2235;
    --bg-glass:      rgba(26, 34, 53, 0.6);
    --bg-glass-hi:   rgba(32, 42, 65, 0.75);

    --copper:        #E8922A;
    --copper-dim:    rgba(232, 146, 42, 0.18);
    --copper-glow:   rgba(232, 146, 42, 0.08);
    --cyan:          #4ECDC4;
    --cyan-dim:      rgba(78, 205, 196, 0.15);
    --green-neo:     #3DDB85;
    --green-dim:     rgba(61, 219, 133, 0.15);
    --red-alert:     #FF6B6B;
    --red-dim:       rgba(255, 107, 107, 0.15);

    --text-primary:  #EEF2FA;
    --text-secondary:#8B9EC4;
    --text-muted:    #4A5568;
    --text-accent:   #E8922A;

    --border-subtle: rgba(255,255,255,0.05);
    --border-mid:    rgba(255,255,255,0.09);
    --border-accent: rgba(232, 146, 42, 0.3);

    --shadow-sm:     0 2px 8px rgba(0,0,0,0.4);
    --shadow-md:     0 4px 20px rgba(0,0,0,0.5);
    --shadow-lg:     0 8px 40px rgba(0,0,0,0.6);
    --shadow-copper: 0 0 30px rgba(232, 146, 42, 0.12);
    --shadow-cyan:   0 0 20px rgba(78, 205, 196, 0.1);

    --radius-sm:  6px;
    --radius-md:  10px;
    --radius-lg:  16px;
    --radius-xl:  22px;

    --font-display: 'Syne', sans-serif;
    --font-body:    'DM Sans', sans-serif;
    --font-mono:    'JetBrains Mono', monospace;
}

/* ── Streamlit Reset ────────────────────────────────── */
.stApp {
    background: var(--bg-void) !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(232,146,42,0.04) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(78,205,196,0.03) 0%, transparent 50%),
        repeating-linear-gradient(
            0deg, transparent, transparent 60px,
            rgba(255,255,255,0.008) 60px, rgba(255,255,255,0.008) 61px
        ),
        repeating-linear-gradient(
            90deg, transparent, transparent 80px,
            rgba(255,255,255,0.006) 80px, rgba(255,255,255,0.006) 81px
        ) !important;
}

html, body, [class*="css"], .stMarkdown, p, span, div {
    font-family: var(--font-body) !important;
    color: var(--text-primary);
}

/* Remove Streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { visibility: hidden; display: none; }

/* ── Main container padding ────────────────────────── */
.main .block-container {
    padding: 0 2rem 3rem 2rem !important;
    max-width: 1600px !important;
}

/* ── Header ─────────────────────────────────────────── */
.cmd-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem 0 1rem 0;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 1.5rem;
}
.cmd-header-left {
    display: flex;
    align-items: center;
    gap: 16px;
}
.cmd-logo {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, var(--copper) 0%, #B36A18 100%);
    border-radius: var(--radius-md);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    box-shadow: var(--shadow-copper);
    flex-shrink: 0;
}
.cmd-title {
    font-family: var(--font-display) !important;
    font-size: 1.25rem !important;
    font-weight: 800 !important;
    color: var(--text-primary) !important;
    letter-spacing: 0.5px;
    line-height: 1.1;
}
.cmd-subtitle {
    font-size: 0.72rem !important;
    color: var(--text-muted) !important;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    font-weight: 400 !important;
    margin-top: 2px;
}
.cmd-header-right {
    display: flex;
    align-items: center;
    gap: 20px;
}
.status-pill {
    display: flex; align-items: center; gap: 7px;
    background: var(--green-dim);
    border: 1px solid rgba(61,219,133,0.2);
    border-radius: 20px; padding: 4px 12px;
    font-size: 0.7rem; color: var(--green-neo);
    letter-spacing: 1px; text-transform: uppercase;
    font-family: var(--font-mono) !important;
}
.status-dot {
    width: 7px; height: 7px;
    background: var(--green-neo);
    border-radius: 50%;
    box-shadow: 0 0 6px var(--green-neo);
    animation: pulse-green 2s infinite;
}
@keyframes pulse-green {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}
.version-tag {
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important;
    color: var(--text-muted) !important;
    background: var(--bg-raised);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 3px 9px;
}

/* ── Tab Navigation ─────────────────────────────────── */
div[data-testid="stHorizontalBlock"] > div:has(.stRadio) { display: none; }

.stRadio > div {
    display: flex !important;
    gap: 4px !important;
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    padding: 4px !important;
    width: fit-content;
}
.stRadio > div > label {
    padding: 7px 18px !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    cursor: pointer;
    transition: all 0.2s ease !important;
    color: var(--text-secondary) !important;
    background: transparent !important;
}
.stRadio > div > label:hover {
    background: var(--bg-raised) !important;
    color: var(--text-primary) !important;
}
.stRadio > div > label[data-checked="true"],
.stRadio input:checked + div {
    background: var(--copper) !important;
    color: #0A0C0F !important;
}

/* ── Selectbox ──────────────────────────────────────── */
div[data-testid="stSelectbox"] > label {
    font-size: 0.65rem !important;
    font-weight: 600 !important;
    color: var(--text-muted) !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    margin-bottom: 4px !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: var(--bg-raised) !important;
    border: 1px solid var(--border-mid) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-size: 0.82rem !important;
    min-height: 36px !important;
    transition: border-color 0.2s !important;
}
div[data-testid="stSelectbox"] > div > div:hover {
    border-color: var(--border-accent) !important;
}

/* ── Buttons ────────────────────────────────────────── */
.stButton > button {
    font-family: var(--font-display) !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    padding: 9px 18px !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    width: 100%;
}

/* Default button */
.stButton > button[kind="secondary"],
.stButton > button:not([kind]) {
    background: var(--bg-raised) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-mid) !important;
}
.stButton > button:not([kind]):hover {
    background: var(--bg-glass-hi) !important;
    border-color: var(--border-accent) !important;
    color: var(--copper) !important;
    box-shadow: var(--shadow-copper) !important;
}

/* Primary button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--copper) 0%, #C97820 100%) !important;
    color: #0A0C0F !important;
    box-shadow: 0 4px 16px rgba(232,146,42,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(232,146,42,0.45) !important;
}

/* ── Number Inputs ──────────────────────────────────── */
div[data-testid="stNumberInput"] label {
    font-size: 0.6rem !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    font-family: var(--font-mono) !important;
}
div[data-testid="stNumberInput"] input {
    background: var(--bg-void) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.82rem !important;
    font-family: var(--font-mono) !important;
    padding: 5px 8px !important;
    height: 34px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
div[data-testid="stNumberInput"] input:focus {
    border-color: var(--copper) !important;
    box-shadow: 0 0 0 2px var(--copper-dim) !important;
    outline: none !important;
}
div[data-testid="stNumberInput"] button {
    background: var(--bg-raised) !important;
    border: 1px solid var(--border-subtle) !important;
    color: var(--text-secondary) !important;
    transition: all 0.15s !important;
}
div[data-testid="stNumberInput"] button:hover {
    background: var(--bg-glass-hi) !important;
    color: var(--copper) !important;
}

/* ── Download Button ────────────────────────────────── */
div[data-testid="stDownloadButton"] > button {
    background: var(--bg-raised) !important;
    color: var(--cyan) !important;
    border: 1px solid rgba(78,205,196,0.25) !important;
    font-family: var(--font-display) !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    border-radius: var(--radius-sm) !important;
    padding: 9px 18px !important;
    width: auto !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: var(--cyan-dim) !important;
    box-shadow: var(--shadow-cyan) !important;
}

/* ── File Uploader ──────────────────────────────────── */
div[data-testid="stFileUploader"] > div {
    background: var(--bg-surface) !important;
    border: 1px dashed rgba(78,205,196,0.25) !important;
    border-radius: var(--radius-lg) !important;
    padding: 2rem !important;
    transition: border-color 0.2s !important;
}
div[data-testid="stFileUploader"] > div:hover {
    border-color: rgba(78,205,196,0.5) !important;
    background: var(--bg-raised) !important;
}

/* ── Dataframe ──────────────────────────────────────── */
div[data-testid="stDataFrame"] {
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
    border: 1px solid var(--border-subtle) !important;
}

/* ── Metric ─────────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: var(--bg-raised) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    padding: 1rem 1.2rem !important;
}
div[data-testid="stMetric"] label {
    font-size: 0.65rem !important;
    color: var(--text-muted) !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-family: var(--font-display) !important;
    color: var(--cyan) !important;
    font-size: 1.5rem !important;
}

/* ── Alert / Success ────────────────────────────────── */
div[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    border: none !important;
    font-size: 0.8rem !important;
}

/* ── Caption ────────────────────────────────────────── */
div[data-testid="stCaptionContainer"] {
    color: var(--text-muted) !important;
    font-size: 0.68rem !important;
    font-family: var(--font-mono) !important;
}

/* ── Divider ────────────────────────────────────────── */
hr { border: none !important; border-top: 1px solid var(--border-subtle) !important; margin: 1.2rem 0 !important; }

/* ══════════════════════════════════════════════════════
   CUSTOM COMPONENT CLASSES
══════════════════════════════════════════════════════ */

/* ── Section Label ──────────────────────────────────── */
.section-label {
    font-family: var(--font-display) !important;
    font-size: 0.62rem !important;
    font-weight: 700 !important;
    color: var(--text-muted) !important;
    letter-spacing: 3.5px !important;
    text-transform: uppercase !important;
    margin-bottom: 0.8rem !important;
}

/* ── Pit Panel Card ─────────────────────────────────── */
.pit-card {
    background: var(--bg-glass);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-xl);
    padding: 1.2rem 1.3rem 1.1rem 1.3rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    transition: border-color 0.25s, box-shadow 0.25s;
    position: relative;
    overflow: hidden;
}
.pit-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--copper), transparent 70%);
    border-radius: var(--radius-xl) var(--radius-xl) 0 0;
}
.pit-card:hover {
    border-color: var(--border-accent);
    box-shadow: var(--shadow-copper);
}

/* ── Pit Card Header ────────────────────────────────── */
.pit-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.9rem;
}
.pit-name {
    font-family: var(--font-display) !important;
    font-size: 0.9rem !important;
    font-weight: 800 !important;
    color: var(--text-primary) !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
.pit-location-pin {
    font-size: 0.7rem;
    color: var(--copper);
    margin-right: 5px;
}
.pit-id-badge {
    font-family: var(--font-mono) !important;
    font-size: 0.6rem !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    background: var(--bg-deep);
    border: 1px solid var(--border-subtle);
    border-radius: 4px;
    padding: 2px 8px;
    letter-spacing: 1px;
}

/* ── Equipment Row Label ────────────────────────────── */
.eq-model-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 8px 0 5px 0;
}
.eq-model-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px 3px 8px;
    border-radius: 20px;
    font-size: 0.63rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    font-family: var(--font-mono) !important;
    text-transform: uppercase;
    border: 1px solid transparent;
}
.eq-model-chip.pc8000  { background: rgba(30,39,97,0.8);  color: #7B8FD4; border-color: rgba(123,143,212,0.2); }
.eq-model-chip.pc4000  { background: rgba(6,90,130,0.5);  color: #60B8D4; border-color: rgba(96,184,212,0.2); }
.eq-model-chip.ex3600  { background: rgba(2,128,144,0.4); color: var(--cyan); border-color: rgba(78,205,196,0.2); }
.eq-model-chip.be495   { background: rgba(44,95,45,0.5);  color: #7CDB7C; border-color: rgba(124,219,124,0.2); }
.eq-model-chip.apron   { background: rgba(180,80,0,0.3);  color: #FF9A45; border-color: rgba(255,154,69,0.2); }

/* ── Trucks Section ─────────────────────────────────── */
.trucks-section {
    background: rgba(0,0,0,0.25);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 0.7rem 0.9rem 0.5rem 0.9rem;
    margin-top: 0.6rem;
}
.trucks-label {
    font-size: 0.6rem !important;
    font-weight: 700 !important;
    color: var(--text-muted) !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    font-family: var(--font-display) !important;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 0.6rem !important;
}
.trucks-icon { color: var(--copper); font-size: 0.75rem; }

/* ── Turno Selector ─────────────────────────────────── */
.turno-card {
    background: var(--bg-raised);
    border: 1px solid var(--border-mid);
    border-radius: var(--radius-lg);
    padding: 1.1rem 1.3rem;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

/* ── Control Bar ────────────────────────────────────── */
.control-bar {
    background: var(--bg-glass);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 1rem 1.4rem;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

/* ── Optimo Badge ───────────────────────────────────── */
.optimo-banner {
    background: linear-gradient(90deg, rgba(61,219,133,0.08), transparent);
    border: 1px solid rgba(61,219,133,0.2);
    border-left: 3px solid var(--green-neo);
    border-radius: var(--radius-sm);
    padding: 6px 14px;
    font-size: 0.7rem !important;
    color: var(--green-neo) !important;
    letter-spacing: 1px !important;
    font-family: var(--font-mono) !important;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Result Panel ───────────────────────────────────── */
.result-container {
    background: var(--bg-glass);
    border: 1px solid var(--border-mid);
    border-radius: var(--radius-xl);
    padding: 2rem 1.8rem;
    text-align: center;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.2rem;
}
.result-container::after {
    content: '';
    position: absolute;
    bottom: -40px; right: -40px;
    width: 160px; height: 160px;
    background: radial-gradient(circle, rgba(232,146,42,0.07) 0%, transparent 70%);
    pointer-events: none;
}
.result-eyebrow {
    font-size: 0.6rem !important;
    font-weight: 700 !important;
    color: var(--text-muted) !important;
    letter-spacing: 4px !important;
    text-transform: uppercase !important;
    font-family: var(--font-mono) !important;
    margin-bottom: 0.2rem !important;
}
.result-number {
    font-family: var(--font-display) !important;
    font-size: 4.5rem !important;
    font-weight: 800 !important;
    color: var(--green-neo) !important;
    line-height: 1 !important;
    letter-spacing: -2px !important;
    text-shadow: 0 0 40px rgba(61,219,133,0.3) !important;
    transition: all 0.4s ease !important;
}
.result-number.pending {
    color: var(--bg-raised) !important;
    text-shadow: none !important;
}
.result-unit {
    font-size: 0.7rem !important;
    color: var(--text-muted) !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    font-family: var(--font-mono) !important;
    margin-top: 0.1rem !important;
}
.result-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-raised);
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.65rem !important;
    color: var(--text-secondary) !important;
    letter-spacing: 0.5px !important;
    font-family: var(--font-mono) !important;
    margin-top: 0.6rem !important;
}
.result-error {
    font-size: 0.62rem !important;
    color: var(--copper) !important;
    font-family: var(--font-mono) !important;
    letter-spacing: 1px !important;
    margin-top: 0.2rem !important;
}

/* ── Calcular Button Large ──────────────────────────── */
.calc-btn-wrap .stButton > button {
    background: linear-gradient(135deg, var(--copper) 0%, #C97820 100%) !important;
    color: #0A0C0F !important;
    font-family: var(--font-display) !important;
    font-size: 0.78rem !important;
    font-weight: 800 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 14px 24px !important;
    box-shadow: 0 4px 20px rgba(232,146,42,0.35) !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
.calc-btn-wrap .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(232,146,42,0.5) !important;
}

/* ── Step Label (bulk mode) ─────────────────────────── */
.step-label {
    font-family: var(--font-display) !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    color: var(--text-secondary) !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 1.2rem 0 0.6rem 0;
}
.step-circle {
    width: 24px; height: 24px;
    background: var(--copper);
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    font-weight: 800;
    color: #0A0C0F;
    flex-shrink: 0;
}

/* ── Scrollbar ──────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--bg-raised); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--border-mid); }

/* ── Column spacing fix ─────────────────────────────── */
div[data-testid="stHorizontalBlock"] { gap: 1rem; }
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
# DATOS (sin cambios)
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

OPTIMOS_PALAS = {
    # UsoDisp_media por (pit, modelo) — Sheet1 TablaResumenGoals
    ('DESCANSO', 'Komatsu PC8000'): 0.83311, ('DESCANSO', 'Bucyrus BE495'):  0.83600,
    ('DESCANSO', 'Hitachi EX3600'): 0.75909, ('DP5',      'Komatsu PC8000'): 0.84311,
    ('DP5',      'Bucyrus BE495'):  0.81048,  ('DP5',      'Hitachi EX3600'): 0.75161,
    ('EC',       'Komatsu PC8000'): 0.78935,  ('EC',       'Hitachi EX3600'): 0.73871,
    ('EC',       'Komatsu PC4000'): 0.67669,  ('PRIBBENOW','Komatsu PC8000'): 0.81036,
    ('PRIBBENOW','Komatsu PC4000'): 0.75885,  ('PRIBBENOW','Bucyrus BE495'):  0.79908,
}

# Draglines/Apron con UsoDisp_media individual (Sheet1)
OPTIMOS_PALAS_EQ = {
    '6449': 0.89885,   # DP5  — Dragline 6449
    '6455': 0.91557,   # DP5  — Dragline 6455
    '6457': 0.90221,   # PRIBBENOW — Dragline 6457
}

OPTIMOS_CAM = {
    # TksAvail_mean→disp, TksUtil_mean→uso, Ciclo_mean→ciclo, QtyCam_mean→qty — Sheet1
    'DESCANSO': {'qty': 89.70,  'disp': 0.66377, 'uso': 0.85954, 'ciclo': 30.623},
    'DP5':      {'qty': 81.90,  'disp': 0.92539, 'uso': 0.85954, 'ciclo': 32.723},
    'EC':       {'qty': 15.55,  'disp': 0.94177, 'uso': 0.81408, 'ciclo': 28.323},
    'PRIBBENOW':{'qty': 67.95,  'disp': 0.71570, 'uso': 0.86469, 'ciclo': 25.600},
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

PIT_LABELS = {
    'DESCANSO':  'El Descanso',
    'DP5':       'Pit 5',
    'EC':        'El Corozo',
    'PRIBBENOW': 'Pribbenow',
}

# ══════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════
def init_values(optimo=False):
    for pit, modelos in EQUIPOS_POR_PIT.items():
        for modelo_eq, equipos in modelos.items():
            modelo_val = OPTIMOS_PALAS.get((pit, modelo_eq), 0.75) if optimo else 0.75
            for eq in equipos:
                if optimo and eq in OPTIMOS_PALAS_EQ:
                    val = OPTIMOS_PALAS_EQ[eq]  # valor individual por equipo
                else:
                    val = modelo_val if optimo else 0.75
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
# HEADER
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="cmd-header">
    <div class="cmd-header-left">
        <div class="cmd-logo">⛏</div>
        <div>
            <div class="cmd-title">Load Forecast Simulator</div>
            <div class="cmd-subtitle">Complex Operations · Ensemble ML v2.1</div>
        </div>
    </div>
    <div class="cmd-header-right">
        <div class="status-pill">
            <span class="status-dot"></span> Model Online
        </div>
        <div class="version-tag">v2.1.0</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MODE SELECTOR
# ══════════════════════════════════════════════════════════════════
modo = st.radio(
    '', ['📊  Predicción Manual', '📁  Carga Masiva'],
    horizontal=True, label_visibility='collapsed'
)
st.markdown('<hr>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# MODO 1 — PREDICCIÓN MANUAL
# ══════════════════════════════════════════════════════════════════
if modo == '📊  Predicción Manual':

    # ── Control Bar ──────────────────────────────────────────────
    ctrl1, ctrl2, ctrl3, ctrl_spacer = st.columns([1.2, 1.2, 1.2, 4])

    with ctrl1:
        turno = st.selectbox('Turno de operación', ['D', 'N'])

    with ctrl2:
        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        if st.button('⭐  Turno Óptimo'):
            init_values(optimo=True)
            st.session_state['modo_optimo'] = True
            st.rerun()

    with ctrl3:
        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        if st.button('↺  Resetear valores'):
            init_values(optimo=False)
            st.session_state['modo_optimo'] = False
            st.rerun()

    if st.session_state['modo_optimo']:
        st.markdown(
            '<div class="optimo-banner">⭐ &nbsp;Turno Óptimo activo — valores cargados desde histórico de máximo rendimiento</div>',
            unsafe_allow_html=True
        )

    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

    vals_palas, vals_camiones = {}, {}
    PITS = list(EQUIPOS_POR_PIT.keys())

    # ── 2×2 Pit Grid ─────────────────────────────────────────────
    for fila_pits in [PITS[:2], PITS[2:]]:
        pit_cols = st.columns(2, gap='medium')

        for col_pit, pit in zip(pit_cols, fila_pits):
            with col_pit:
                pit_label = PIT_LABELS.get(pit, pit)
                eq_count  = sum(len(v) for v in EQUIPOS_POR_PIT[pit].values())

                st.markdown(f"""
                <div class="pit-card">
                    <div class="pit-card-header">
                        <div>
                            <span class="pit-location-pin">◆</span>
                            <span class="pit-name">{pit_label}</span>
                        </div>
                        <div class="pit-id-badge">{pit} · {eq_count} EQ</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Equipment rows
                for modelo_eq, equipos in EQUIPOS_POR_PIT[pit].items():
                    chip_class = EQ_CHIP_CLASS.get(modelo_eq, 'pc8000')
                    st.markdown(
                        f'<div class="eq-model-row">'
                        f'<span class="eq-model-chip {chip_class}">◉ {modelo_eq}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    eq_cols = st.columns(len(equipos))
                    for ec, eq in zip(eq_cols, equipos):
                        with ec:
                            vals_palas[f'UsodeDisp_{eq}'] = st.number_input(
                                f'{eq}',
                                min_value=0.0, max_value=1.0,
                                value=st.session_state[f'v_{eq}'],
                                step=0.01, format='%.2f',
                                key=f'ni_{eq}'
                            )

                # Trucks section
                st.markdown('<div class="trucks-section"><div class="trucks-label"><span class="trucks-icon">▶</span> Flota de Camiones</div></div>', unsafe_allow_html=True)

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
                        'Ciclo (min)', min_value=15.0, max_value=60.0,
                        value=st.session_state[f'v_ciclo_{pit}'],
                        step=0.1, format='%.1f', key=f'ni_ciclo_{pit}')

        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

    # ── Prediction Row ────────────────────────────────────────────
    st.markdown('<hr>', unsafe_allow_html=True)
    btn_col, spacer_col, res_col = st.columns([1.5, 0.2, 2.5])

    with btn_col:
        st.markdown('<div style="height: 12px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="calc-btn-wrap">', unsafe_allow_html=True)
        calcular = st.button('▶  CALCULAR PREDICCIÓN', use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("""
            <div style="margin-top:1rem; padding:0.9rem 1rem; background:rgba(0,0,0,0.2);
                        border:1px solid rgba(255,255,255,0.05); border-radius:10px;">
                <div style="font-size:0.6rem;color:var(--text-muted);letter-spacing:2px;
                            text-transform:uppercase;font-family:var(--font-mono);margin-bottom:0.5rem;">
                    Configuración activa
                </div>
                <div style="display:flex;flex-direction:column;gap:4px;">
                    <div style="display:flex;justify-content:space-between;font-size:0.72rem;">
                        <span style="color:var(--text-secondary);">Frentes activos</span>
                        <span style="color:var(--cyan);font-family:var(--font-mono);">4</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:0.72rem;">
                        <span style="color:var(--text-secondary);">Variables input</span>
                        <span style="color:var(--cyan);font-family:var(--font-mono);">45</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:0.72rem;">
                        <span style="color:var(--text-secondary);">Algoritmo</span>
                        <span style="color:var(--copper);font-family:var(--font-mono);">Ensemble v2.1</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with res_col:
        ph = st.empty()
        ph.markdown("""
            <div class="result-container">
                <div class="result-eyebrow">Predicted Load Count</div>
                <div class="result-number pending">—</div>
                <div class="result-unit">loads / shift</div>
                <div class="result-tag">Ingresa parámetros y presiona Calcular</div>
            </div>
        """, unsafe_allow_html=True)

    if calcular:
        datos  = {**vals_palas, **vals_camiones, 'turno': turno}
        data   = pd.DataFrame([datos])[COLUMNAS_ESPERADAS]
        Y_pred = predecir(data)
        cargas = int(round(Y_pred[0]))
        tag    = '⭐ Turno Óptimo' if st.session_state['modo_optimo'] else '✏ Manual'
        turno_label = 'Diurno (D)' if turno == 'D' else 'Nocturno (N)'
        ph.markdown(f"""
            <div class="result-container">
                <div class="result-eyebrow">Predicted Load Count</div>
                <div class="result-number">{cargas:,}</div>
                <div class="result-unit">loads / shift</div>
                <div class="result-tag">{tag} &nbsp;·&nbsp; Turno {turno_label}</div>
                <div class="result-error">⚠ Model error: ±1.5%</div>
            </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# MODO 2 — CARGA MASIVA
# ══════════════════════════════════════════════════════════════════
else:
    bulk_l, bulk_r = st.columns([3, 2], gap='large')

    with bulk_l:
        # Step 1
        st.markdown("""
            <div class="step-label">
                <span class="step-circle">1</span>
                Descarga la plantilla CSV
            </div>
        """, unsafe_allow_html=True)
        st.markdown("""
            <div style="background:var(--bg-raised);border:1px solid var(--border-subtle);
                        border-radius:var(--radius-md);padding:0.9rem 1.1rem;margin-bottom:0.6rem;
                        font-size:0.75rem;color:var(--text-secondary);line-height:1.6;">
                Descarga la plantilla con la estructura de columnas requerida.
                Cada fila representa un turno de operación con los 45 parámetros de entrada.
            </div>
        """, unsafe_allow_html=True)

        ej = {col: 0.75 for col in COLS_NUMERICAS}
        ej.update({
            'QtyCamiones_DESCANSO': 89.7,  'Disponibilidad_TKS_DESCANSO': 0.664,
            'UsodeDisp_TKS_DESCANSO': 0.834,'TiempoCiclo_TKS_DESCANSO': 30.62,
            'QtyCamiones_DP5': 81.9,        'Disponibilidad_TKS_DP5': 0.925,
            'UsodeDisp_TKS_DP5': 0.860,     'TiempoCiclo2_DP5': 32.72,
            'QtyCamiones_EC': 15.55,         'Disponibilidad_TKS_EC': 0.942,
            'UsodeDisp_TKS_EC': 0.814,       'TiempoCiclo2_EC': 28.32,
            'QtyCamiones_PRIBBENOW': 67.95, 'Disponibilidad_TKS_PRIBBENOW': 0.716,
            'UsodeDisp_TKS_PRIBBENOW': 0.865,'TiempoCiclo_TKS_PRIBBENOW': 25.60,
            'turno': 'D'
        })
        buf = io.BytesIO()
        pd.DataFrame([ej]).to_csv(buf, index=False)
        buf.seek(0)
        st.download_button(
            '⬇  Descargar Plantilla CSV',
            data=buf,
            file_name='plantilla_prediccion.csv',
            mime='text/csv'
        )

        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

        # Step 2
        st.markdown("""
            <div class="step-label">
                <span class="step-circle">2</span>
                Carga tu archivo con datos de turnos
            </div>
        """, unsafe_allow_html=True)
        archivo = st.file_uploader(
            'Arrastra tu CSV aquí o haz click para seleccionar',
            type=['csv'],
            label_visibility='visible'
        )

    with bulk_r:
        st.markdown("""
            <div style="background:var(--bg-glass);border:1px solid var(--border-subtle);
                        border-radius:var(--radius-xl);padding:1.4rem 1.5rem;
                        backdrop-filter:blur(12px);">
                <div style="font-size:0.62rem;color:var(--text-muted);letter-spacing:3px;
                            text-transform:uppercase;font-family:var(--font-mono);margin-bottom:1rem;">
                    Especificaciones del modelo
                </div>
                <div style="display:flex;flex-direction:column;gap:10px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;
                                padding:7px 0;border-bottom:1px solid var(--border-subtle);">
                        <span style="font-size:0.75rem;color:var(--text-secondary);">Variables numéricas</span>
                        <span style="font-family:var(--font-mono);font-size:0.75rem;color:var(--cyan);">44</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;
                                padding:7px 0;border-bottom:1px solid var(--border-subtle);">
                        <span style="font-size:0.75rem;color:var(--text-secondary);">Variable categórica</span>
                        <span style="font-family:var(--font-mono);font-size:0.75rem;color:var(--cyan);">turno (D/N)</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;
                                padding:7px 0;border-bottom:1px solid var(--border-subtle);">
                        <span style="font-size:0.75rem;color:var(--text-secondary);">Frentes mineros</span>
                        <span style="font-family:var(--font-mono);font-size:0.75rem;color:var(--copper);">4</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;
                                padding:7px 0;border-bottom:1px solid var(--border-subtle);">
                        <span style="font-size:0.75rem;color:var(--text-secondary);">Algoritmo</span>
                        <span style="font-family:var(--font-mono);font-size:0.75rem;color:var(--copper);">Ensemble Reg.</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;
                                padding:7px 0;">
                        <span style="font-size:0.75rem;color:var(--text-secondary);">Error estimado</span>
                        <span style="font-family:var(--font-mono);font-size:0.75rem;color:var(--green-neo);">±1.5%</span>
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

            st.markdown("""
                <div class="step-label" style="margin-top:1.2rem;">
                    <span class="step-circle">3</span>
                    Ejecuta la predicción masiva
                </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="calc-btn-wrap">', unsafe_allow_html=True)
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

                st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
                cols_v = ['turno','Prediccion_Cargas'] + [c for c in COLUMNAS_ESPERADAS if c != 'turno']
                st.dataframe(df[cols_v], use_container_width=True)

                buf2 = io.BytesIO()
                df.to_csv(buf2, index=False)
                buf2.seek(0)
                st.download_button(
                    '⬇  Descargar Resultados',
                    data=buf2,
                    file_name='predicciones.csv',
                    mime='text/csv'
                )
                st.caption('⚠ Error del modelo: ±5% — Use los resultados como referencia operacional.')

        except Exception as e:
            st.error(f'Error al procesar el archivo: {e}')
