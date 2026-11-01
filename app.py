import streamlit as st
import google.generativeai as genai
from serpapi import GoogleSearch
from PIL import Image
import os

# --- API ANAHTARLARI ---
# Kendi API anahtarlarını buraya girmelisin veya ortam değişkeni olarak eklemelisin.
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
SERPAPI_KEY = st.secrets["SERPAPI_KEY"]

genai.configure(api_key=GEMINI_API_KEY)

def urunu_tanimla(image):
    """Gemini API kullanarak fotoğraftaki ürünü tanımlar."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = "Bu fotoğraftaki ürünün tam marka ve modelini tek bir cümleyle, arama motorunda aratılacak formatta yaz. Sadece ürün adını ver, ekstra açıklama yapma."
    response = model.generate_content([prompt, image])
    return response.text.strip()

def fiyatlari_getir(urun_adi):
    """SerpApi (Google Shopping) kullanarak ürünün fiyatlarını çeker."""
    params = {
        "engine": "google_shopping",
        "q": urun_adi,
        "hl": "tr",
        "gl": "tr", # Türkiye pazarındaki fiyatlar
        "api_key": SERPAPI_KEY
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    
    shopping_results = results.get("shopping_results", [])
    fiyat_listesi = []
    
    for item in shopping_results[:10]: # İlk 10 sonucu alıyoruz
        satici = item.get("source")
        fiyat_str = item.get("extracted_price", 0) # Rakam olarak fiyat (örn: 1500.50)
        link = item.get("link")
        
        if fiyat_str and satici:
            fiyat_listesi.append({
                "satici": satici,
                "fiyat": float(fiyat_str),
                "link": link
            })
            
    return fiyat_listesi

# --- STREAMLIT ARAYÜZÜ ---
st.title("📸 Görselden Fiyat Karşılaştırma")
st.write("Bir ürünün fotoğrafını yükle, ne olduğunu bulup farklı sitelerdeki fiyatlarını karşılaştıralım.")

yuklenen_foto = st.file_uploader("Ürün fotoğrafı yükle (JPG, PNG)", type=["jpg", "png", "jpeg"])

if yuklenen_foto is not None:
    # Fotoğrafı göster
    image = Image.open(yuklenen_foto)
    st.image(image, caption="Yüklenen Ürün", use_column_width=True)
    
    if st.button("Fiyatları Bul"):
        with st.spinner("Ürün tanımlanıyor..."):
            urun_adi = urunu_tanimla(image)
            st.success(f"**Tespit Edilen Ürün:** {urun_adi}")
            
        with st.spinner("Fiyatlar internetten toplanıyor..."):
            fiyatlar = fiyatlari_getir(urun_adi)
            
            if fiyatlar:
                st.subheader("Satış Noktaları ve Fiyatlar")
                toplam_fiyat = 0
                
                # Fiyatları tek tek listele
                for urun in fiyatlar:
                    st.write(f"🛒 **{urun['satici']}**: {urun['fiyat']} TL - [Ürüne Git]({urun['link']})")
                    toplam_fiyat += urun['fiyat']
                
                # Ortalama fiyatı hesapla
                ortalama = toplam_fiyat / len(fiyatlar)
                
                st.markdown("---")
                st.subheader(f"📊 Ortalama Piyasa Fiyatı: **{ortalama:.2f} TL**")
                
            else:
                st.error("Bu ürün için fiyat bilgisi bulunamadı veya satışı yok.")
