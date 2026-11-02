import streamlit as st
import json
import base64
import io
import time
import re
import random
import html
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from PIL import Image

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
.detected b { font-size: 1.1rem; }

/* Özet */
.stats { display: flex; gap: 10px; margin: 8px 0 18px 0; }
.stat {
    flex: 1;
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 12px 14px;
}
.stat span { display: block; color: var(--muted); font-size: .78rem; }
.stat b { font-size: 1.15rem; }
.stat.best { background: var(--brand); border-color: var(--brand); color: #fff; }
.stat.best span { color: #CFE6DF; }

/* Ürün kartı */
.card {
    position: relative;
    display: flex;
    gap: 14px;
    align-items: center;
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 12px;
    margin-bottom: 10px;
}
.card.best { border: 2px solid var(--brand); }
.card img {
    width: 84px; height: 84px;
    object-fit: contain;
    border-radius: 10px;
    background: #fff;
    flex-shrink: 0;
}
.card .noimg {
    width: 84px; height: 84px; border-radius: 10px;
    background: var(--bg); display: flex;
    align-items: center; justify-content: center;
    font-size: 1.6rem; flex-shrink: 0;
}
.card .info { flex: 1; min-width: 0; }
.card .price { font-size: 1.25rem; font-weight: 800; color: var(--brand); }
.card .store { font-weight: 700; font-size: .92rem; }
.card .title {
    color: var(--muted); font-size: .82rem;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.card a.go {
    background: var(--ink); color: #fff !important;
    text-decoration: none; font-weight: 700; font-size: .85rem;
    padding: 10px 14px; border-radius: 10px; white-space: nowrap;
}
.card a.go:hover { background: var(--brand); }
.badge {
    position: absolute; top: -10px; left: 14px;
    background: var(--gold); color: var(--ink);
    font-size: .72rem; font-weight: 800;
    padding: 3px 10px; border-radius: 999px;
}

@media (max-width: 520px) {
    .hero h1 { font-size: 1.5rem; }
    .card { flex-wrap: wrap; }
    .card a.go { width: 100%; text-align: center; box-sizing: border-box; }
    .stats { flex-direction: column; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------
# API ANAHTARLARI
# ---------------------------------
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
except Exception:
    st.error("API anahtarları bulunamadı. `.streamlit/secrets.toml` dosyasına "
             "GEMINI_API_KEY ve SERPAPI_KEY ekle.")
    st.stop()

# ---------------------------------
# FONKSİYONLAR
# ---------------------------------
# Model adları sık değiştiği için liste Google'dan canlı çekilir.
# Çekilemezse bu yedek liste kullanılır.
YEDEK_MODELLER = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite"]


@st.cache_data(ttl=3600, show_spinner=False)
def mevcut_modeller(api_key):
    """generateContent destekleyen kararlı flash modellerini yeniden eskiye sıralar."""
    try:
        req = Request(
            "https://generativelanguage.googleapis.com/v1beta/models?pageSize=200",
            headers={"x-goog-api-key": api_key},
        )
        with urlopen(req, timeout=20) as r:
            veri = json.loads(r.read().decode("utf-8"))
    except Exception:
        return YEDEK_MODELLER

    adaylar = []
    for m in veri.get("models", []):
        if "generateContent" not in m.get("supportedGenerationMethods", []):
            continue
        ad = m["name"].split("/", 1)[-1]
        eslesme = re.fullmatch(r"gemini-(\d+(?:\.\d+)?)-flash(-lite)?", ad)
        if eslesme:
            adaylar.append((float(eslesme.group(1)), not eslesme.group(2), ad))
    # En yeni sürüm önce; aynı sürümde normal flash, lite'tan önce gelir
    adaylar.sort(reverse=True)
    return [a[2] for a in adaylar[:4]] or YEDEK_MODELLER


GECICI_HATALAR = {429, 500, 502, 503, 504}
DENEME_SAYISI = 3


def _hata_mesaji(ex):
    """HTTPError gövdesinden okunabilir bir mesaj çıkarır."""
    try:
        govde = json.loads(ex.read().decode("utf-8"))
        return govde.get("error", {}).get("message", "")
    except Exception:
        return ""


def gemini_urun_tani(image, api_key, marka_ipucu="", durum=None):
    foto = image.copy()  # Orijinal görsel bozulmasın
    foto.thumbnail((640, 640))
    buffered = io.BytesIO()
    foto.save(buffered, format="JPEG", quality=70)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    if marka_ipucu.strip():
        talimat = (
            f"Kullanıcı bu ürünün '{marka_ipucu.strip()}' markasına ait olduğunu "
            "belirtti. Fotoğraftaki ana ürünün tam modelini üzerindeki yazıları "
            "okuyarak belirle. Yazı okunmuyorsa görünümden en olası marka ve modeli tahmin et. "
            "Açıklama, soru veya özür yazma; sadece Google Shopping'de aratılacak "
            "ürün adını tek satır olarak yaz."
        )
    else:
        talimat = (
            "Bu fotoğrafta el ile tutulan veya odaklanılan ana ürünün tam marka "
            "adını ve modelini, üzerindeki yazıları okuyarak belirle. Yazı okunmuyorsa görünümden en olası marka ve "
            "modeli tahmin et. Açıklama, soru veya özür yazma; sadece Google "
            "Shopping'de aratılacak ürün adını tek satır olarak yaz."
        )

    son_hata = ""
    son_kod = None

    for model_adi in mevcut_modeller(api_key):
        gen_config = {"temperature": 0.1, "maxOutputTokens": 512}
        if model_adi.startswith("gemini-2.5"):
            gen_config["thinkingConfig"] = {"thinkingBudget": 0}  # Hızlı yanıt

        data = {
            "contents": [{
                "parts": [
                    {"text": talimat},
                    {"inline_data": {"mime_type": "image/jpeg", "data": img_str}},
                ]
            }],
            "generationConfig": gen_config,
        }
        url = ("https://generativelanguage.googleapis.com/v1beta/models/"
               f"{model_adi}:generateContent")

        if durum:
            durum(f"Model deneniyor: {model_adi}")

        for deneme in range(DENEME_SAYISI):
            req = Request(
                url,
                data=json.dumps(data).encode("utf-8"),
                headers={"Content-Type": "application/json",
                         "x-goog-api-key": api_key},
                method="POST",
            )
            try:
                with urlopen(req, timeout=25) as response:
                    sonuc = json.loads(response.read().decode("utf-8"))
                parcalar = sonuc["candidates"][0]["content"]["parts"]
                metin = "".join(p.get("text", "") for p in parcalar).strip()
                if metin:
                    return metin.splitlines()[0].strip(" *`\"'")
                son_hata = "Model boş yanıt döndürdü."
                break  # Boş yanıtta sıradaki modeli dene

            except HTTPError as ex:
                son_kod = ex.code
                son_hata = _hata_mesaji(ex)
                if ex.code == 400 and "thinkingConfig" in gen_config:
                    # Bu model thinkingBudget'ı kabul etmiyor: onsuz yeniden dene
                    gen_config.pop("thinkingConfig")
                    data["generationConfig"] = gen_config
                    continue
                if ex.code in GECICI_HATALAR:
                    if durum:
                        durum(f"{model_adi} yoğun, tekrar deneniyor ({deneme + 1}/{DENEME_SAYISI})")
                    # Üstel bekleme: ~1.5s, 3s, 6s (+ rastgele sapma)
                    time.sleep(1.5 * (2 ** deneme) + random.uniform(0, 0.7))
                    continue
                break  # 400/403/404: bu modelde tekrar denemenin anlamı yok

            except (URLError, TimeoutError) as ex:
                son_hata = str(ex)
                time.sleep(1.5 * (deneme + 1))
                continue

            except (KeyError, IndexError, json.JSONDecodeError) as ex:
                son_hata = f"Beklenmeyen yanıt biçimi: {ex}"
                break

    if son_kod in (401, 403) or (son_kod == 400 and "API key" in son_hata):
        raise Exception("Gemini API anahtarı geçersiz veya yetkisiz. Anahtarı kontrol et.")
    if son_kod == 429:
        raise Exception("Gemini kullanım kotası doldu. Biraz bekleyip tekrar dene.")
    if son_kod in GECICI_HATALAR:
        raise Exception("Gemini sunucuları şu an çok yoğun. Tüm modeller denendi; "
                        "1-2 dakika sonra tekrar dene.")
    raise Exception(f"Gemini hatası ({son_kod or 'bağlantı'}): {son_hata}")


@st.cache_data(ttl=3600, show_spinner=False)
def fiyatlari_ara(urun_adi, api_key, min_fiyat=0):
    istek = {
        "engine": "google_shopping",
        "q": urun_adi + " -kılıf -case -kapak",
        "hl": "tr",
        "gl": "tr",
        "api_key": api_key,
    }
    if min_fiyat:
        istek["min_price"] = int(min_fiyat)
    params = urlencode(istek)
    req = Request("https://serpapi.com/search.json?" + params,
                  headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req, timeout=30) as response:
            sonuc = json.loads(response.read().decode("utf-8"))
    except HTTPError as ex:
        raise Exception(f"SerpApi hatası {ex.code}")
    except (URLError, TimeoutError):
        raise Exception("SerpApi'ye bağlanılamadı.")

    if sonuc.get("error"):
        raise Exception(sonuc["error"])
    return sonuc.get("shopping_results", [])


def fiyatlari_getir(urun_adi, api_key):
    """İlk aramada çoğunlukla aksesuar geliyorsa, fiyat tabanı koyup bir kez daha arar."""
    ilk = fiyatlari_ara(urun_adi, api_key)
    temiz, _ = filtrele(ilk, urun_adi)
    if len(temiz) >= 3:
        return ilk

    fiyatlar = [float(r["extracted_price"]) for r in ilk if r.get("extracted_price")]
    if not fiyatlar:
        return ilk
    # Gelen sonuçlar ucuz aksesuarsa, asıl ürün bunların birkaç katıdır
    ikinci = fiyatlari_ara(urun_adi, api_key, min_fiyat=max(fiyatlar) * 2)
    gorulen, birlesik = set(), []
    for r in ilk + ikinci:
        anahtar = (r.get("title"), r.get("source"))
        if anahtar not in gorulen:
            gorulen.add(anahtar)
            birlesik.append(r)
    return birlesik


def fiyat_goster(x):
    return f"{x:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")


AKSESUAR_KELIMELERI = [
    "kilif", "kapak", "case", "cover", "silikon", "koruyucu", "aksesuar",
    "film", "ear tips", "kulaklik ucu", "kordon", "askili", "askilik",
    "tutucu", "sticker", "etiket", "temizleme", "temizlik", "aparat", "yedek",
]


def normalize(metin):
    tablo = str.maketrans("ıİşŞğĞüÜöÖçÇ", "iissggUUooCC".replace("U", "u").replace("C", "c"))
    metin = (metin or "").translate(tablo).lower()
    return re.sub(r"[^a-z0-9 ]+", " ", metin)


def filtrele(sonuclar, urun_adi):
    """Kılıf/aksesuar gibi alakasız sonuçları eler. (liste, elenen_sayısı) döner."""
    sorgu = normalize(urun_adi)
    tokenlar = sorgu.split()
    yasak = [k for k in AKSESUAR_KELIMELERI if k not in sorgu]

    uygun = []
    for r in sonuclar:
        baslik = normalize(r.get("title", ""))
        kompakt = baslik.replace(" ", "")
        if any(re.search(r"\b" + re.escape(k), baslik) for k in yasak):
            continue
        # Model numarası (4, 15 vb.) başlıkta ayrı bir kelime olarak geçmeli
        sayilar = [t for t in tokenlar if t.isdigit()]
        if any(n not in baslik.split() for n in sayilar):
            continue
        if tokenlar:
            bulunan = sum(1 for t in tokenlar if t in baslik or t in kompakt)
            if bulunan / len(tokenlar) < 0.5:
                continue
        uygun.append(r)

    # Fiyat aykırıları: medyanın çok altındakiler genelde aksesuardır
    fiyatli = sorted(float(r["extracted_price"]) for r in uygun
                     if r.get("extracted_price"))
    if len(fiyatli) >= 5:
        medyan = fiyatli[len(fiyatli) // 2]
        uygun = [r for r in uygun
                 if not r.get("extracted_price")
                 or float(r["extracted_price"]) >= medyan * 0.4]

    return uygun, len(sonuclar) - len(uygun)


def urun_karti(item, en_ucuz):
    satici = html.escape(item.get("source", "Bilinmeyen satıcı"))
    fiyat = html.escape(str(item.get("price", "-")))
    baslik = item.get("title", "Ürün")
    baslik = html.escape(baslik)
    link = item.get("product_link") or item.get("link")
    thumb = item.get("thumbnail")

    gorsel = (f'<img src="{html.escape(thumb)}" alt="">' if thumb
              else '<div class="noimg">🛍️</div>')
    buton = (f'<a class="go" href="{html.escape(link)}" target="_blank" '
             f'rel="noopener noreferrer">Mağazaya git</a>') if link else ""
    rozet = '<span class="badge">En ucuz</span>' if en_ucuz else ""
    sinif = "card best" if en_ucuz else "card"

    st.markdown(
        f'<div class="{sinif}">{rozet}{gorsel}'
        f'<div class="info"><div class="price">{fiyat}</div>'
        f'<div class="store">{satici}</div>'
        f'<div class="title" title="{baslik}">{baslik}</div></div>{buton}</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------
# BAŞLIK VE GİRİŞ
# ---------------------------------
st.markdown(
    '<div class="hero"><h1>🛍️ Alışveriş Asistanı</h1>'
    '<p>Ürünün fotoğrafını yükle, en uygun fiyatı bulalım.</p></div>',
    unsafe_allow_html=True,
)

kullanici_adi = st.text_input("Adın", placeholder="Örn: Eren Can")
if not kullanici_adi.strip():
    st.info("Başlamak için adını yaz ve Enter'a bas.")
    st.stop()

st.markdown(f"Merhaba **{html.escape(kullanici_adi.strip())}** 👋")

# ---------------------------------
# FOTOĞRAF VE MARKA
# ---------------------------------
girilen_marka = st.text_input(
    "Marka (isteğe bağlı)",
    placeholder="Örn: Zara, Ceel…",
    help="Markayı yazarsan tanıma daha hızlı ve doğru olur.",
)

sekme_yukle, sekme_kamera = st.tabs(["📤 Fotoğraf yükle", "📷 Kamera"])
with sekme_yukle:
    yuklenen = st.file_uploader(
        "Fotoğraf seç", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
    )
with sekme_kamera:
    cekilen = st.camera_input("Ürünün fotoğrafını çek", label_visibility="collapsed")

kaynak = yuklenen or cekilen

if kaynak is not None:
    try:
        image = Image.open(kaynak).convert("RGB")
    except Exception as ex:
        st.error(f"Fotoğraf okunamadı: {ex}")
        st.stop()

    st.image(image, width=300)

    if st.button("Ürünü tanı ve fiyatları getir", type="primary",
                 use_container_width=True):
        st.session_state.pop("sonuclar", None)

        with st.status("Ürün tanınıyor…", expanded=True) as durum_kutusu:
            try:
                st.session_state["urun_adi"] = gemini_urun_tani(
                    image, GEMINI_API_KEY, girilen_marka,
                    durum=lambda m: st.write(m),
                )
                durum_kutusu.update(label="Ürün tanındı", state="complete", expanded=False)
            except Exception as ex:
                durum_kutusu.update(label="Ürün tanınamadı", state="error")
                st.error(str(ex))
                st.stop()

    # Algılanan ad düzenlenebilir: yanlışsa kullanıcı düzeltip yeniden arayabilir
    if "urun_adi" in st.session_state:
        st.markdown(
            f'<div class="detected"><small>Tanınan ürün</small>'
            f'<b>{html.escape(st.session_state["urun_adi"])}</b></div>',
            unsafe_allow_html=True,
        )
        duzeltilmis = st.text_input(
            "Yanlışsa ürün adını düzelt",
            value=st.session_state["urun_adi"],
            key="urun_adi_duzenle",
        )

        if st.button("Fiyatları ara", use_container_width=True) or \
                "sonuclar" not in st.session_state:
            with st.spinner("Fiyatlar toplanıyor…"):
                try:
                    st.session_state["sonuclar"] = fiyatlari_getir(
                        duzeltilmis.strip(), SERPAPI_KEY
                    )
                    st.session_state["aranan"] = duzeltilmis.strip()
                except Exception as ex:
                    st.error(f"Fiyat arama hatası: {ex}")
                    st.stop()

# ---------------------------------
# SONUÇLAR
# ---------------------------------
sonuclar = st.session_state.get("sonuclar")
if sonuclar is not None:
    if not sonuclar:
        st.warning("Bu ürün için satış sonucu bulunamadı. Adı düzeltip tekrar dene.")
    else:
        elenen = 0
        if st.checkbox("Kılıf ve aksesuarları gizle", value=True):
            sonuclar, elenen = filtrele(sonuclar, st.session_state.get("aranan", ""))
        if not sonuclar:
            st.warning("Filtre sonrası sonuç kalmadı. Filtreyi kapat veya ürün adını düzelt.")
            st.stop()
        if elenen:
            st.caption(f"{elenen} alakasız sonuç (kılıf, aksesuar vb.) gizlendi.")

        liste = [r for r in sonuclar if r.get("extracted_price")]
        liste.sort(key=lambda r: float(r["extracted_price"]))
        liste = (liste or sonuclar)[:10]

        if liste and liste[0].get("extracted_price"):
            fiyatlar = [float(r["extracted_price"]) for r in liste
                        if r.get("extracted_price")]
            st.markdown(
                '<div class="stats">'
                f'<div class="stat best"><span>En düşük</span><b>{fiyat_goster(min(fiyatlar))}</b></div>'
                f'<div class="stat"><span>Ortalama</span><b>{fiyat_goster(sum(fiyatlar)/len(fiyatlar))}</b></div>'
                f'<div class="stat"><span>En yüksek</span><b>{fiyat_goster(max(fiyatlar))}</b></div>'
                '</div>',
                unsafe_allow_html=True,
            )
            st.caption(f"{len(fiyatlar)} mağazadaki fiyatlara göre, ucuzdan pahalıya.")

        for i, item in enumerate(liste):
            urun_karti(item, en_ucuz=(i == 0 and bool(item.get("extracted_price"))))

st.markdown(
    "<p style='text-align:center;color:#66726D;font-size:.8rem;margin-top:2rem'>"
    "Görselden fiyat karşılaştırma asistanı</p>",
    unsafe_allow_html=True,
)
