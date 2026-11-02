import streamlit as st
import json
import base64
import io
import time
import re
import hashlib
from concurrent.futures import ThreadPoolExecutor
import random
import html
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from PIL import Image, ImageOps

# ---------------------------------
# SAYFA AYARLARI
# ---------------------------------
st.set_page_config(
    page_title="Akıllı Alışveriş Asistanı",
    page_icon="🛍️",
    layout="centered",
)

# ---------------------------------
# TASARIM
# ---------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&display=swap');

:root {
    --bg: #F6F7F4;
    --ink: #14201C;
    --muted: #66726D;
    --line: #E1E6E2;
    --brand: #0F6B57;
    --brand-dark: #0A4F40;
    --gold: #F2B84B;
}

html, body, [class*="css"], .stApp {
    font-family: 'Manrope', sans-serif;
    color: var(--ink);
}
.stApp { background: var(--bg); }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; max-width: 760px; }

/* Üst başlık */
.hero {
    background: var(--brand);
    color: #fff;
    border-radius: 22px;
    padding: 28px 26px;
    margin-bottom: 22px;
}
.hero h1 {
    margin: 0;
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #fff;
}
.hero p { margin: 6px 0 0 0; opacity: .85; font-size: 1rem; }

/* Girişler */
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label { color: var(--ink) !important; font-weight: 600; }
.stTextInput input {
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
    background: #fff !important;
}
.stTextInput input::placeholder { color: #8A958F !important; -webkit-text-fill-color: #8A958F !important; }
[data-testid="stCaptionContainer"] { color: var(--muted) !important; }
[data-testid="stFileUploader"] section * { color: var(--ink) !important; }
[data-testid="stFileUploader"] section button,
[data-testid="stFileUploader"] section button * {
    background: var(--brand) !important; color: #fff !important; border-radius: 10px;
}
.stTabs [data-baseweb="tab"] p { color: var(--ink) !important; font-weight: 600; }
.stTabs [aria-selected="true"] p { color: var(--brand) !important; }
.stTabs [data-baseweb="tab-highlight"] { background: var(--brand) !important; }
.stTextInput input {
    border-radius: 12px;
    border: 1px solid var(--line);
    background: #fff;
}
.stTextInput input:focus { border-color: var(--brand); box-shadow: 0 0 0 1px var(--brand); }
[data-testid="stFileUploader"] section {
    border-radius: 14px;
    border: 1.5px dashed #B9C4BE;
    background: #fff;
}

/* Butonlar */
.stButton > button[kind="primary"] {
    background: var(--brand);
    border: none;
    border-radius: 14px;
    font-weight: 700;
    padding: 0.7rem 1rem;
}
.stButton > button[kind="primary"]:hover { background: var(--brand-dark); }
.stButton > button:focus-visible { outline: 3px solid var(--gold); }

/* Algılanan ürün */
.detected {
    background: #fff;
    border: 1px solid var(--line);
    border-left: 5px solid var(--brand);
    border-radius: 14px;
    padding: 14px 18px;
    margin: 14px 0;
}
.detected small { color: var(--muted); display: block; margin-bottom: 2px; }
.detected b { font
