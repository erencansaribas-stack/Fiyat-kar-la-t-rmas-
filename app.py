import streamlit as st
import json
import base64
import io
import time
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError
from PIL import Image

# ---------------------------------
# SAYFA AYARLARI VE ÖZEL TASARIM
# ---------------------------------
st.set_page_config(
    page_title="Akıllı Alışveriş Asistanı",
    page_icon="🛍️",
    layout="centered"
)

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

    modeller = [
        "gemini-3.8-flash", 
        "gemini-1.5-flash-latest", 
        "gemini-1.5-flash"
    ]

    if marka_ipucu.strip():
        talimat = (
            f"Kullanıcı bu ürünün '{marka_ipucu}' markasına ait "
            "olduğunu belirtti. Bu bilgi ışığında, fotoğrafta "
            "el ile tutulan ana ürünün tam modelini sadece kutu "
            "üzerindeki yazıları harfi harfine okuyarak belirle. "
            "Sadece Google Shopping üzerinde aratılacak en doğru "
            "ve net ürün adını tek bir satır halinde yaz."
        )
    else:
        talimat = (
            "Bu fotoğrafta el ile tutulan veya odaklanılan ana "
            "ürünün tam marka adını ve modelini, sadece kutu "
            "üzerindeki yazıları harfi harfine okuyarak belirle. "
            "Asla yorum yapma veya kategori uydurma. Sadece "
            "Google Shopping üzerinde aratılacak en doğru ve net "
            "ürün adını tek bir satır halinde yaz."
        )

    data = {
        "contents": [
            {
                "parts": [
                    {"text": talimat}, 
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
        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{model_adi}:generateContent"
        )
        
        for deneme in range(3):
            req_headers = {
                "Content-Type": "application/json", 
                "x-goog-api-key": GEMINI_API_KEY
            }
            
            req = Request(
                url, 
                data=json.dumps(data).encode("utf-8"),
                headers=req_headers, 
                method="POST"
            )
            
            try:
                with urlopen(req, timeout=60) as response:
                    sonuc = json.loads(response.read().decode("utf-8"))
                
                urun_adi = sonuc["candidates"][0]["content"]["parts"][0]["text"].strip()
                if urun_adi: 
                    return urun_adi
                    
            except HTTPError as ex:
                son_hata = ex
                if ex.code in [503, 429]: 
                    time.sleep(2)
                    continue
                else: 
                    break  
            except Exception as ex:
                son_hata = ex
                break

    if isinstance(son_hata, HTTPError):
        raise Exception(f"Gemini HTTP {son_hata.code}: Sunucu yoğun, tekrar dene.")
    else:
        raise Exception(f"Gemini bağlantı hatası: {son_hata}")


def fiyatlari_ara(urun_adi):
    params = urlencode({
        "engine": "google_shopping", 
        "q": urun_adi, 
        "hl": "tr", 
        "gl": "tr", 
        "api_key": SERPAPI_KEY
    })
    
    search_url = "https://serpapi.com/search.json?" + params
    
    req_headers = {"User-Agent": "Mozilla/5.0"}
    req = Request(search_url, headers=req_headers)
    
    try:
        with urlopen(req, timeout=45) as response:
            sonuc = json.loads(response.read().decode("utf-8"))
            
        if sonuc.get("error"): 
            raise Exception(sonuc["error"])
            
        return sonuc.get("shopping_results", [])
        
    except HTTPError as ex:
        raise Exception(f"SerpApi Hatası {ex.code}")

# ---------------------------------
# ANA EKRAN VE GİRİŞ (UI)
# ---------------------------------
st.markdown(
    "<div style='text-align: center; padding: 15px; "
    "background-color: #FF4B4B; border-radius: 15px; "
    "margin-bottom: 20px; color: white;'>"
    "<h1 style='margin: 0px; color: white;'>🛍️ Alışveriş Asistanı</h1>"
    "<p style='margin: 5px 0px 0px 0px; font-size: 16px;'>"
    "Ürünün fotoğrafını çek, en ucuzunu bulalım.</p></div>", 
    unsafe_allow_html=True
)

kullanici_adi = st.text_input(
    "👤 Asistanı kullanmak için adını gir:", 
    placeholder="Örn: Eren Can"
)

if not kullanici_adi:
    st.info("👆 Uygulamaya giriş yapmak için adını yaz ve 'Enter'a bas.")
    st.stop()

st.success(f"🎉 Harika! Hoş geldin **{kullanici_adi}**. Hadi başlayalım!")
st.markdown("---")

# ---------------------------------
# API ANAHTARLARI
# ---------------------------------
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
except Exception:
    st.error("API anahtarları (Secrets) bulunamadı!")
    st.stop()

# ---------------------------------
# İPUCU VE FOTOĞRAF YÜKLEME 
# ---------------------------------
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("### 🏷️ Marka (Opsiyonel)")
    girilen_marka = st.text_input(
        "Markayı biliyorsan yaz (Hızlandırır):", 
        placeholder="Örn: Ceel, Apple..."
    )
with col2:
    st.markdown("### 📤 Fotoğraf")
    yuklenen_foto = st.file_uploader(
        "Kutusu okunan fotoğraf seç:", 
        type=["jpg", "jpeg", "png"], 
        label_visibility="collapsed"
    )

if yuklenen_foto is not None:
    try:
        image = Image.open(yuklenen_foto).convert("RGB")
        st.image(image, caption="📸 Yüklediğin Fotoğraf", use_container_width=True)
    except Exception as ex:
        st.error(f"Fotoğraf okunamadı: {ex}")
        st.stop()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Ürünü Tanı ve Fiyatları Getir", type="primary", use_container_width=True):
        
        with st.spinner("🧠 Yapay zeka ürünü inceliyor..."):
            try:
                urun_adi = gemini_urun_tani(image, girilen_marka)
                st.success(f"🎯 **Yapay Zeka Tespit Etti:** {urun_adi}")
            except Exception as ex:
                st.error(f"Analiz hatası: {ex}")
                st.stop()

        with st.spinner("🌐 İnternetten fiyatlar toplanıyor..."):
            try:
                shopping_results = fiyatlari_ara(urun_adi)
            except Exception as ex:
                st.error(f"Fiyat arama hatası: {ex}")
                st.stop()

        if shopping_results:
            st.markdown("### 🛒 En İyi Fiyatlar")
            fiyatlar = []
            
            satirlar = [shopping_results[i:i+2] for i in range(0, min(10, len(shopping_results)), 2)]
            
            for satir in satirlar:
                cols = st.columns(2)
                for idx, item in enumerate(satir):
                    satici = item.get("source", "Bilinmeyen Satıcı")
                    fiyat = item.get("price", "-")
                    baslik = item.get("title", "Ürün")[:50] + "..." 
                    link = item.get("link")
                    extracted_price = item.get("extracted_price")
                    
                    if extracted_price: 
                        fiyatlar.append(float(extracted_price))

                    with cols[idx]:
                        with st.container(border=True):
                            st.markdown(f"<h4 style='text-align: center; color: #FF4B4B;'>{fiyat}</h4>", unsafe_allow_html=True)
                            st.markdown(f"**🏪 {satici}**")
                            st.caption(f"{baslik}")
                            if link:
                                st.link_button("Mağazaya Git 🔗", link, use_container_width=True)

            if fiyatlar:
                ortalama = sum(fiyatlar) / len(fiyatlar)
                st.markdown("---")
                st.markdown("### 📊 Hızlı Piyasa Analizi")
                st.info(
                    f"💡 Bulunan **{len(fiyatlar)}** mağazaya göre "
                    f"ortalama fiyat **{ortalama:,.2f} TL** civarında."
                )
            else:
                st.warning("Ürünler bulundu ancak fiyat rakamları çekilemedi.")
        else:
            st.warning("Bu ürün için doğrudan satış sonucu bulunamadı.")

st.markdown(
    "<br><hr><center><p style='color:gray; font-size:12px;'>"
    "Görselden Fiyat Karşılaştırma Asistanı 🚀</p></center>", 
    unsafe_allow_html=True
)
