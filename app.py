import streamlit as st
import urllib.request
import json
import base64
from PIL import Image
import io

st.set_page_config(page_title="Fiyat Karşılaştırma", page_icon="📸")

st.title("👋 Hoş geldin, Eren Can!")
st.subheader("📸 Görselden Fiyat Karşılaştırma Asistanı")
st.write("Ürünün fotoğrafını yükle, yapay zeka tanısın ve internetteki en güncel fiyatları karşılaştırsın.")

# API Anahtarlarını Al
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
except Exception as e:
    st.error("API anahtarları (Secrets) bulunamadı! Lütfen Streamlit ayarlarından eklediğinizden emin olun.")
    st.stop()

yuklenen_foto = st.file_uploader("Ürün fotoğrafı seç", type=["jpg", "png", "jpeg"])

if yuklenen_foto is not None:
    image = Image.open(yuklenen_foto)
    st.image(image, caption="Yüklenen Ürün", use_column_width=True)
    
    if st.button("Ürünü Tanı ve Fiyatları Ara"):
        with st.spinner("Yapay zeka ürünü inceliyor ve fiyatları topluyor..."):
            try:
                # Fotoğrafı Base64 formatına çevir
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                
                # Gemini API'ye doğrudan HTTP isteği at (Ek kütüphane hatası vermez)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                headers = {'Content-Type': 'application/json'}
                data = {
                    "contents": [{
                        "parts": [
                            {"text": "Bu fotoğraftaki ürünün tam marka ve modelini sadece ürün adı olarak tek cümleyle yaz."},
                            {"inline_data": {"mime_type": "image/jpeg", "data": img_str}}
                        ]
                    }]
                }
                
                req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
                with urllib.request.urlopen(req) as response:
                    res_json = json.loads(response.read().decode('utf-8'))
                    urun_adi = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
                
                st.info(f"🔍 Algılanan Ürün: **{urun_adi}**")
                
                # SerpApi ile fiyat arama
                params = urllib.parse.urlencode({
                    "engine": "google_shopping",
                    "q": urun_adi,
                    "hl": "tr",
                    "gl": "tr",
                    "api_key": SERPAPI_KEY
                })
                search_url = f"https://serpapi.com/search.json?{params}"
                
                with urllib.request.urlopen(search_url) as search_res:
                    search_data = json.loads(search_res.read().decode('utf-8'))
                    shopping_results = search_data.get("shopping_results", [])
                
                if shopping_results:
                    st.subheader("🛒 Bulunan Fiyatlar ve Satıcılar")
                    fiyatlar = []
                    
                    for item in shopping_results[:10]:
                        satici = item.get("source")
                        fiyat_str = item.get("extracted_price")
                        link = item.get("link")
                        baslik = item.get("title")
                        
                        if fiyat_str and satici:
                            fiyatlar.append(float(fiyat_str))
                            st.write(f"• **{satici}**: {fiyat_str} TL - [{baslik}]({link})")
                    
                    if fiyatlar:
                        ortalama = sum(fiyatlar) / len(fiyatlar)
                        st.success(f"📊 Ortalama Piyasa Değeri: **{ortalama:.2f} TL**")
                else:
                    st.warning("Bu ürün için internette doğrudan satış sonucu bulunamadı.")
            except Exception as ex:
                st.error(f"İşlem sırasında bir hata oluştu: {ex}")
