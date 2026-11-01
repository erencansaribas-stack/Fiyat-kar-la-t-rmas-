
import streamlit as st
import urllib.request
import urllib.parse
import urllib.error
import json

from PIL import Image
from google import genai


# SAYFA AYARLARI
st.set_page_config(
    page_title="Fiyat Karşılaştırma",
    page_icon="📸"
)

st.title("📸 Görselden Fiyat Karşılaştırma Asistanı")

st.write(
    "Ürünün fotoğrafını yükle, yapay zeka tanısın "
    "ve internetteki fiyatları karşılaştırsın."
)


# KULLANICI
kullanici_adi = st.text_input(
    "Adın nedir?",
    value="Eren Can"
)

if kullanici_adi:
    st.subheader(f"👋 Hoş geldin, {kullanici_adi}!")


# API ANAHTARLARI
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    SERPAPI_KEY = st.secrets["SERPAPI_KEY"]

except Exception:
    st.error(
        "API anahtarları bulunamadı. "
        "Lütfen Streamlit Secrets ayarlarını kontrol et."
    )
    st.stop()


# GEMINI İSTEMCİSİ
client = genai.Client(api_key=GEMINI_API_KEY)


# FOTOĞRAF YÜKLEME
yuklenen_foto = st.file_uploader(
    "Ürün fotoğrafı seç",
    type=["jpg", "jpeg", "png"]
)


if yuklenen_foto is not None:

    try:
        image = Image.open(yuklenen_foto).convert("RGB")

        st.image(
            image,
            caption="Yüklenen Ürün",
            use_container_width=True
        )

    except Exception as ex:
        st.error(f"Fotoğraf okunamadı: {ex}")
        st.stop()


    if st.button(
        "Ürünü Tanı ve Fiyatları Ara",
        type="primary"
    ):

        # 1. GEMINI İLE ÜRÜN TANIMA
        with st.spinner("Yapay zeka ürünü inceliyor..."):

            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=[
                        """
                        Bu fotoğraftaki ürünü analiz et.

                        Mümkünse:
                        - Marka
                        - Model
                        - Ürün türü

                        bilgilerini belirle.

                        Emin olmadığın marka veya modeli uydurma.
                        Sadece ürünün arama yapılabilecek adını yaz.
                        """,
                        image
                    ]
                )

                urun_adi = response.text.strip()

                if not urun_adi:
                    st.error("Gemini ürün adını belirleyemedi.")
                    st.stop()

                st.success(
                    f"🔍 Algılanan Ürün: {urun_adi}"
                )

            except Exception as ex:
                st.error(f"Gemini API hatası: {ex}")
                st.stop()


        # 2. SERPAPI İLE GOOGLE SHOPPING ARAMASI
        with st.spinner("Google Shopping fiyatları aranıyor..."):

            try:
                params = urllib.parse.urlencode({
                    "engine": "google_shopping",
                    "q": urun_adi,
                    "hl": "tr",
                    "gl": "tr",
                    "api_key": SERPAPI_KEY
                })

                search_url = (
                    "https://serpapi.com/search.json?"
                    + params
                )

                req = urllib.request.Request(
                    search_url,
                    headers={
                        "User-Agent": "Mozilla/5.0"
                    }
                )

                with urllib.request.urlopen(
                    req,
                    timeout=30
                ) as search_res:

                    search_data = json.loads(
                        search_res.read().decode("utf-8")
                    )

                if search_data.get("error"):
                    st.error(
                        f"SerpApi hatası: {search_data['error']}"
                    )
                    st.stop()

                shopping_results = search_data.get(
                    "shopping_results", []
                )

            except Exception as ex:
                st.error(f"Fiyat arama hatası: {ex}")
                st.stop()


        # 3. SONUÇLARI GÖSTER
        if shopping_results:

            st.subheader("🛒 Bulunan Fiyatlar ve Satıcılar")

            fiyatlar = []

            for item in shopping_results[:10]:

                satici = item.get("source", "Satıcı belirtilmemiş")
                fiyat = item.get("price", "Fiyat belirtilmemiş")
                baslik = item.get("title", "Ürün")
                link = item.get("link")
                extracted_price = item.get("extracted_price")

                st.markdown(f"**{satici}**")

                st.write(f"Ürün: {baslik}")
                st.write(f"Fiyat: {fiyat}")

                if link:
                    st.markdown(
                        f"[Ürünü incele]({link})"
                    )

                if extracted_price is not None:
                    try:
                        fiyatlar.append(float(extracted_price))
                    except (ValueError, TypeError):
                        pass

                st.divider()


            # 4. ORTALAMA FİYAT
            if fiyatlar:

                ortalama = sum(fiyatlar) / len(fiyatlar)

                st.success(
                    "📊 Sonuçlardaki sayısal fiyat ortalaması: "
                    f"{ortalama:.2f}"
                )

                st.caption(
                    "Bu ortalama, bulunan sonuçların sayısal "
                    "fiyatlarından hesaplanır. Farklı para "
                    "birimleri varsa doğrudan karşılaştırılmamalıdır."
                )

        else:

            st.warning(
                "Bu ürün için Google Shopping üzerinde "
                "satış sonucu bulunamadı."
            )
