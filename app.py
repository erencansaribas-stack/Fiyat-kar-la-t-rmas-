import streamlit as st
import urllib.request
import urllib.parse
import urllib.error
import json
import base64
import io
import time

from PIL import Image

# ---------------------------------
# SAYFA AYARLARI VE ÖZEL TASARIM (CSS)
# ---------------------------------
st.set_page_config(
    page_title="Akıllı Alışveriş Asistanı",
    page_icon="🛍️",
    layout="centered"
)

# Streamlit'in varsayılan menülerini gizleyip, arayüzü daha "uygulama" gibi gösteren CSS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {
        border-radius: 20px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------
# FONKSİYONLAR
# ---------------------------------
def gemini_urun_tani(image, marka_ipucu=""):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=90)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    modeller = ["gemini-3.8-flash", "gemini-1.5-flash-latest", "gemini-1.5-flash"]

    if marka_ipucu.strip():
        talimat = (
            f"Kullanıcı bu ürünün '{marka_ipucu}' markasına ait olduğunu belirtti. "
            "Bu bilgi ışığında, fotoğrafta el ile tutulan ana ürünün tam modelini "
            "sadece kutu üzerindeki yazıları harfi harfine okuyarak belirle. "
            "Sadece Google Shopping üzerinde aratılacak en doğru ve net ürün adını (Marka + Model) tek bir satır halinde yaz."
        )
    else:
        talimat = (
            "Bu fotoğrafta el ile tutulan veya odaklanılan ana ürünün tam marka adını ve modelini, "
            "sadece kutu üzerindeki yazıları harfi harfine okuyarak belirle. "
            "Asla yorum yapma veya kategori uydurma. "
            "Sadece Google Shopping üzerinde aratılacak en doğru ve net ürün adını tek bir satır halinde yaz."
        )

    data = {
        "contents": [{"parts": [{"text": talimat}, {"inline_data": {"mime_type": "image/jpeg", "data": img_str}}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 150}
    }

    son_hata = None

    for model_adi in modeller:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_adi}:generateContent"
        for deneme in range(3):
            req = urllib.request.Request(
                url, data=json.dumps(data).encode("utf-8"),
                headers={"Content-Type": "application/json", "x-goog
