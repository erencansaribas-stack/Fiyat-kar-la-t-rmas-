import streamlit as st
from PIL import Image
import google.generativeai as genai
from serpapi import GoogleSearch

st.set_page_config(page_title="Fiyat Karşılaştırma", page_icon="📸")

st.title("📸 Görselden Fiyat Karşılaştırma Asistanı")
st.write("Ürünün fotoğrafını yükle, yapay zeka tanısın ve internetteki en güncel fiyatları karşılaştırsın.")

# Kullanıcı Adı Girişi
kullanici_adi = st.text_input("Adın nedir?", value="Eren Can")

if kullanici_adi:
    st.subheader(f"👋 Hoş geldin, {kullanici_adi}!")

# Güvenli API Anahtarı Okuma
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error("API anahtarları (Secrets) bulunamadı! Lütfen Streamlit ayarlarından eklediğinizden emin olun.")
    st.stop()

# Fotoğraf Yükleme
yuklenen_foto = st.file_uploader("Ürün fotoğrafı seç", type=["jpg", "png", "jpeg"])

if yuklenen_foto is not None:
    image = Image.open(yuklenen_foto)
    st.image(image, caption="Yüklenen Ürün", use_column_width=True)
    
    if st.button("Ürünü Tanı ve Fiyatları Ara"):
        with st.spinner("Yapay zeka ürünü inceliyor ve fiyatları topluyor..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(["Bu fotoğraftaki ürünün tam marka ve modelini sadece ürün adı olarak tek cümleyle yaz.", image])
                urun_adi = response.text.strip()
                
                st.info(f"🔍 Algılanan Ürün: **{urun_adi}**")
                
                params = {
                    "engine": "google_shopping",
                    "q": urun_adi,
                    "hl": "tr",
                    "gl": "tr",
                    "api_key": SERPAPI_KEY
                }
                
                search = GoogleSearch(params)
                results = search.get_dict()
                shopping_results = results.get("shopping_results", [])
                
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
