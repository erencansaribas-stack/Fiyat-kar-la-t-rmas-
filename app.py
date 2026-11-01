import streamlit as st
import urllib.request
import urllib.parse
import urllib.error
import json
import base64
import io

from PIL import Image


# ---------------------------------
# SAYFA AYARLARI
# ---------------------------------

st.set_page_config(
    page_title="Görselden Fiyat Karşılaştırma",
    page_icon="📸",
    layout="centered"
)

st.title("📸 Görselden Fiyat Karşılaştırma Asistanı")

st.write(
    "Ürünün fotoğrafını yükle, yapay zeka tanısın "
    "ve internetteki fiyatları karşılaştırsın."
)


# ---------------------------------
# KULLANICI
# ---------------------------------

kullanici_adi = st.text_input(
    "Adın nedir?",
    value="Eren Can"
)

if kullanici_adi:
    st.subheader(f"👋 Hoş geldin, {kullanici_adi}!")


# ---------------------------------
# API ANAHTARLARI
# ---------------------------------

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    SERPAPI_KEY = st.secrets["SERPAPI_KEY"]

except Exception:
    st.error(
        "API anahtarları bulunamadı! "
        "Streamlit Secrets ayarlarını kontrol et."
    )
    st.stop()


# ---------------------------------
# GEMINI ÜRÜN TANIMA FONKSİYONU
# ---------------------------------

def gemini_urun_tani(image):

    buffered = io.BytesIO()

    image.save(buffered, format="JPEG", quality=90)

    img_str = base64.b64encode(
        buffered.getvalue()
    ).decode("utf-8")

    # Düzeltilen doğru URL modeli
    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.8-flash:generateContent"
    )

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

        with urllib.request.urlopen(
            req,
            timeout=60
        ) as response:

            sonuc = json.loads(
                response.read().decode("utf-8")
            )

        urun_adi = (
            sonuc["candidates"][0]
            ["content"]["parts"][0]["text"]
            .strip()
        )

        if not urun_adi:
            raise ValueError("Gemini boş ürün adı döndürdü.")

        return urun_adi

    except urllib.error.HTTPError as ex:

        detay = ex.read().decode(
            "utf-8",
            errors="replace"
        )

        raise Exception(
            f"Gemini HTTP {ex.code}: {detay}"
        )

    except (KeyError, IndexError, TypeError):

        raise Exception(
            "Gemini yanıtı beklenen formatta değil. "
            "Modelin yanıtını kontrol et."
        )


# ---------------------------------
# SERPAPI FİYAT ARAMA FONKSİYONU
# ---------------------------------

def fiyatlari_ara(urun_adi):

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

    try:

        with urllib.request.urlopen(
            req,
            timeout=45
        ) as response:

            sonuc = json.loads(
                response.read().decode("utf-8")
            )

        if sonuc.get("error"):
            raise Exception(sonuc["error"])

        return sonuc.get("shopping_results", [])

    except urllib.error.HTTPError as ex:

        detay = ex.read().decode(
            "utf-8",
            errors="replace"
        )

        raise Exception(
            f"SerpApi HTTP {ex.code}: {detay}"
        )


# ---------------------------------
# FOTOĞRAF YÜKLEME
# ---------------------------------

yuklenen_foto = st.file_uploader(
    "Ürün fotoğrafı seç",
    type=["jpg", "jpeg", "png"]
)


if yuklenen_foto is not None:

    try:

        image = Image.open(
            yuklenen_foto
        ).convert("RGB")

        st.image(
            image,
            caption="Yüklenen Ürün",
            use_container_width=True
        )

    except Exception as ex:

        st.error(f"Fotoğraf okunamadı: {ex}")
        st.stop()


    # ---------------------------------
    # ARAMA BUTONU
    # ---------------------------------

    if st.button(
        "🔍 Ürünü Tanı ve Fiyatları Ara",
        type="primary",
        use_container_width=True
    ):

        # GEMINI ANALİZİ

        with st.spinner(
            "Yapay zeka ürünü tanıyor..."
        ):

            try:

                urun_adi = gemini_urun_tani(image)

                st.success(
                    f"🔍 Algılanan Ürün: {urun_adi}"
                )

            except Exception as ex:

                st.error(
                    f"Gemini analiz hatası: {ex}"
                )

                st.stop()


        # SERPAPI ARAMASI

        with st.spinner(
            "Google Shopping fiyatları aranıyor..."
        ):

            try:

                shopping_results = fiyatlari_ara(
                    urun_adi
                )

            except Exception as ex:

                st.error(
                    f"Fiyat arama hatası: {ex}"
                )

                st.stop()


        # ---------------------------------
        # SONUÇLARI GÖSTER
        # ---------------------------------

        if shopping_results:

            st.subheader(
                "🛒 Bulunan Fiyatlar ve Satıcılar"
            )

            fiyatlar = []

            for item in shopping_results[:10]:

                satici = item.get(
                    "source",
                    "Satıcı belirtilmemiş"
                )

                fiyat = item.get(
                    "price",
                    "Fiyat belirtilmemiş"
                )

                baslik = item.get(
                    "title",
                    "Ürün"
                )

                link = item.get("link")

                extracted_price = item.get(
                    "extracted_price"
                )

                with st.container(border=True):

                    st.markdown(
                        f"**🏪 {satici}**"
                    )

                    st.write(
                        f"📦 {baslik}"
                    )

                    st.write(
                        f"💰 {fiyat}"
                    )

                    if link:

                        st.link_button(
                            "Ürünü incele",
                            link,
                            use_container_width=True
                        )

                if extracted_price is not None:

                    try:

                        fiyatlar.append(
                            float(extracted_price)
                        )

                    except (ValueError, TypeError):
                        pass


            # ---------------------------------
            # ORTALAMA FİYAT
            # ---------------------------------

            if fiyatlar:

                ortalama = (
                    sum(fiyatlar) / len(fiyatlar)
                )

                st.subheader(
                    "📊 Fiyat Analizi"
                )

                st.metric(
                    "Bulunan fiyatların sayısal ortalaması",
                    f"{ortalama:,.2f}"
                )

                st.caption(
                    "Ortalama, sayısal fiyat alanlarından "
                    "hesaplanmıştır. Farklı para birimleri "
                    "varsa doğrudan karşılaştırılamaz."
                )

                st.write(
                    f"Karşılaştırılan fiyat sayısı: {len(fiyatlar)}"
                )

            else:

                st.warning(
                    "Ürünler bulundu ancak sayısal fiyat "
                    "bilgisi alınamadı."
                )

        else:

            st.warning(
                "Bu ürün için Google Shopping üzerinde "
                "satış sonucu bulunamadı."
            )


# ---------------------------------
# ALT BİLGİ
# ---------------------------------

st.divider()

st.caption(
    "Görselden Fiyat Karşılaştırma Asistanı"
)
