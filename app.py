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
        "api_key": SERPAPI_KEY
    })
    
    search_url = "https://serpapi.com/search.json?" + params
    req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            sonuc = json.loads(response.read().decode("utf-8"))
        if sonuc.get("error"):
            raise Exception(sonuc["error"])
        return sonuc.get("shopping_results", [])
    except urllib.error.HTTPError as ex:
        detay = ex.read().decode("utf-8", errors="replace")
        raise Exception(f"SerpApi HTTP {ex.code}: {detay}")

# ---------------------------------
# ANA EKRAN VE GİRİŞ (UI)
# ---------------------------------

st.title("📸 Görselden Fiyat Karşılaştırma Asistanı")
st.markdown("Yapay zeka destekli alışveriş asistanına hoş geldin. Ürünün fotoğrafını çek, en uygun fiyatı bulalım.")
st.divider()

kullanici_adi = st.text_input("Devam etmek için adını gir:", placeholder="Örn: Eren Can")

if not kullanici_adi:
    st.info("👆 Lütfen uygulamayı kullanmak için yukarıya adını yazıp 'Enter'a bas.")
    st.stop()

st.success(f"👋 Hoş geldin, **{kullanici_adi}**! Asistanın kullanıma hazır.")
st.markdown("---")

# ---------------------------------
# API ANAHTARLARI KONTROLÜ
# ---------------------------------
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
except Exception:
    st.error("API anahtarları bulunamadı! Streamlit Secrets ayarlarını kontrol et.")
    st.stop()

# ---------------------------------
# FOTOĞRAF YÜKLEME VE ANALİZ
# ---------------------------------
st.markdown("### 📤 Ürün Fotoğrafını Yükle")
yuklenen_foto = st.file_uploader("Kutunun üzerindeki yazıların net okunduğu bir fotoğraf seç:", type=["jpg", "jpeg", "png"])

if yuklenen_foto is not None:
    try:
        image = Image.open(yuklenen_foto).convert("RGB")
        st.image(image, caption="Yüklenen Ürün", use_container_width=True)
    except Exception as ex:
        st.error(f"Fotoğraf okunamadı: {ex}")
        st.stop()

    if st.button("🔍 Ürünü Tanı ve Fiyatları Ara", type="primary", use_container_width=True):
        
        with st.spinner("Yapay zeka ürünü tanıyor (Yoğunluk varsa otomatik tekrar deneniyor)..."):
            try:
                urun_adi = gemini_urun_tani(image)
                st.success(f"🎯 **Algılanan Ürün:** {urun_adi}")
            except Exception as ex:
                st.error(f"Gemini analiz hatası: {ex}")
                st.stop()

        with st.spinner("Google Shopping fiyatları aranıyor..."):
            try:
                shopping_results = fiyatlari_ara(urun_adi)
            except Exception as ex:
                st.error(f"Fiyat arama hatası: {ex}")
                st.stop()

        if shopping_results:
            st.subheader("🛒 Bulunan Fiyatlar ve Satıcılar")
            fiyatlar = []

            for item in shopping_results[:10]:
                satici = item.get("source", "Satıcı belirtilmemiş")
                fiyat = item.get("price", "Fiyat belirtilmemiş")
                baslik = item.get("title", "Ürün")
                link = item.get("link")
                extracted_price = item.get("extracted_price")

                with st.container(border=True):
                    st.markdown(f"**🏪 {satici}**")
                    st.write(f"📦 {baslik}")
                    st.write(f"💰 {fiyat}")
                    if link:
                        st.link_button("Ürünü İncele", link, use_container_width=True)

                if extracted_price is not None:
                    try:
                        fiyatlar.append(float(extracted_price))
                    except (ValueError, TypeError):
                        pass

            if fiyatlar:
                ortalama = sum(fiyatlar) / len(fiyatlar)
                st.subheader("📊 Fiyat Analizi")
                st.metric("Piyasa Ortalama Fiyatı", f"{ortalama:,.2f} TL")
                st.caption(f"Bu ortalama değer, bulunan {len(fiyatlar)} farklı satıcının fiyatı üzerinden hesaplanmıştır.")
            else:
                st.warning("Ürünler bulundu ancak net bir sayısal fiyat bilgisi çekilemedi.")
        else:
            st.warning("Bu ürün için Google Shopping üzerinde doğrudan bir satış sonucu bulunamadı.")

st.divider()
st.caption("Görselden Fiyat Karşılaştırma Asistanı | Streamlit Cloud")
