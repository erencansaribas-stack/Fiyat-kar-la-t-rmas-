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
# SAYFA AYARLARI
# ---------------------------------
st.set_page_config(
    page_title="Görselden Fiyat Karşılaştırma",
    page_icon="📸",
    layout="centered"
)

# ---------------------------------
# FONKSİYONLAR
# ---------------------------------

def gemini_urun_tani(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=90)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    modeller = [
        "gemini-3.8-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash"
    ]

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "Bu fotoğrafta el ile tutulan veya odaklanılan ana ürünün tam marka adını ve modelini, "
                            "sadece kutu üzerindeki yazıları harfi harfine okuyarak belirle. "
                            "Asla yorum yapma veya kategori uydurma. "
                            "Sadece Google Shopping üzerinde aratılacak en doğru ve net ürün adını tek bir satır halinde yaz. "
                            "Örneğin: 'Ceel Retinal Shot 30 ml' gibi."
                        )
                    },
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": img_str
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 150
        }
    }

    son_hata = None

    for model_adi in modeller:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_adi}:generateContent"

        for deneme in range(3):
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": GEMINI_API_KEY
                },
                method="POST"
            )

            try:
                with urllib.request.urlopen(req, timeout=60) as response:
                    sonuc = json.loads(response.read().decode("utf-8"))

                urun_adi = sonuc["candidates"][0]["content"]["parts"][0]["text"].strip()
                if urun_adi:
                    return urun_adi

            except urllib.error.HTTPError as ex:
                son_hata = ex
                if ex.code in [503, 429]:  
                    time.sleep(2)  
                    continue
                else:
                    break  
            except Exception as ex:
                son_hata = ex
                break

    if isinstance(son_hata, urllib.error.HTTPError):
        detay = son_hata.read().decode("utf-8", errors="replace")
        raise Exception(f"Gemini HTTP {son_hata.code}: Sunucu yoğun, lütfen birkaç saniye sonra tekrar dene.")
    else:
        raise Exception(f"Gemini bağlantı hatası: {son_hata}")


def fiyatlari_ara(urun_adi):
    params = urllib.parse.urlencode({
        "engine": "google_shopping",
        "q": urun_adi,
        "hl": "tr",
        "gl": "tr",
        "api_key

            
