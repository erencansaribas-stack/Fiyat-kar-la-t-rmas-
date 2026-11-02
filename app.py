import streamlit as st
import json
import base64
import io
import time
import re
import hashlib
from concurrent.futures import ThreadPoolExecutor
import random
import html
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from PIL import Image, ImageOps

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

.card .match { font-weight: 700; }
.card .match.ayni { color: var(--brand); }
.card .match.benzer { color: #9A6B00; }
.card .old { color: var(--muted); font-size: .8rem; font-weight: 500; margin-left: 8px; }
.card .meta { display: flex; gap: 12px; flex-wrap: wrap; color: var(--muted); font-size: .78rem; margin-top: 2px; }
.stButton button[kind="secondary"], [data-testid="stBaseButton-secondary"] {
    background: #fff !important; border: 1px solid var(--line) !important;
    border-radius: 14px; font-weight: 700;
}
.stButton button[kind="secondary"] *, [data-testid="stBaseButton-secondary"] * { color: var(--ink) !important; }
.stButton button[kind="primary"] *, [data-testid="stBaseButton-primary"] * { color: #fff !important; }
[data-testid="stRadio"] label p, [data-testid="stCheckbox"] label p { color: var(--ink) !important; }

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

try:
    IMGBB_KEY = st.secrets["IMGBB_KEY"]  # İsteğe bağlı: fotoğrafla birebir arama için
except Exception:
    IMGBB_KEY = None

# ---------------------------------
# FONKSİYONLAR
# ---------------------------------
# Model adları sık değiştiği için liste Google'dan canlı çekilir.
# Çekilemezse bu süper hızlı ve sorunsuz yedek liste kullanılır.
YEDEK_MODELLER = ["gemini-1.5-flash-8b", "gemini-1.5-flash"]


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

    # Nesne formunu önceleyen güncellenmiş kural
    kural = (
        "DİKKAT: Öncelikle fotoğraftaki nesnenin fiziksel olarak tam olarak ne olduğunu "
        "(kupa, fincan, kase, tabak, şişe, kutu vb.) kesin ve hatasız bir şekilde belirle. "
        "Örneğin fotoğraftaki bir fincan veya kupa ise, deseninden dolayı ona asla tabak deme. "
        "Yazı okunmuyorsa görünümden marka, desen ve rengi belirle. "
        "Cevap, Google Shopping'de aratılacak KISA bir ürün adı olsun: "
        "marka, desen/renk ve AYIRT EDİCİ nesne türü (örn. mavi beyaz çiçekli porselen kupa). "
        "En fazla 7 kelime kullan. Açıklama veya yorum yapmadan sadece tek satır ürün adı yaz."
    )
    
    if marka_ipucu.strip():
        talimat = (f"Kullanıcı bu ürünün '{marka_ipucu.strip()}' markasına ait olduğunu "
                   "belirtti. Fotoğraftaki ana ürünü üzerindeki yazıları okuyarak "
                   "belirle. " + kural)
    else:
        talimat = ("Bu fotoğrafta el ile tutulan veya odaklanılan ana ürünün marka ve "
                   "modelini, üzerindeki yazıları okuyarak belirle. " + kural)

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
        "q": urun_adi,
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

    hata = sonuc.get("error")
    if hata:
        if "hasn't returned any results" in hata:
            return []  # Hata değil: bu ifade için sonuç yok
        raise Exception(hata)
    return sonuc.get("shopping_results") or sonuc.get("inline_shopping_results") or []


def gorsel_yukle(image, api_key=None):
    """Fotoğrafı geçici, herkese açık bir bağlantıya yükler.
    imgbb anahtarı varsa 10 dk, yoksa anahtarsız Litterbox ile 1 saat sonra silinir."""
    foto = image.copy()
    foto.thumbnail((1000, 1000))
    buf = io.BytesIO()
    foto.save(buf, format="JPEG", quality=85)
    try:
        if api_key:
            govde = urlencode({"image": base64.b64encode(buf.getvalue()).decode("utf-8")})
            req = Request(
                "https://api.imgbb.com/1/upload?" + urlencode({"key": api_key, "expiration": 600}),
                data=govde.encode("utf-8"), method="POST",
            )
            with urlopen(req, timeout=30) as r:
                url = (json.loads(r.read().decode("utf-8")).get("data") or {}).get("url")
        else:
            import requests  # Streamlit ile birlikte kurulur
            r = requests.post(
                "https://litterbox.catbox.moe/resources/internals/api.php",
                data={"reqtype": "fileupload", "time": "1h"},
                files={"fileToUpload": ("urun.jpg", buf.getvalue(), "image/jpeg")},
                timeout=30,
            )
            url = r.text.strip() if r.ok and r.text.strip().startswith("http") else None
    except HTTPError as ex:
        raise Exception(f"Fotoğraf yüklenemedi (imgbb {ex.code}). IMGBB_KEY'i kontrol et.")
    except Exception:
        raise Exception("Fotoğraf yükleme servisine bağlanılamadı.")
    if not url:
        raise Exception("Fotoğraf yüklenemedi.")
    return url


def lens_karti(r):
    """Google Lens sonucunu, ürün kartının beklediği biçime çevirir."""
    f = r.get("price")
    if isinstance(f, dict):
        gosterim, sayi, para = f.get("value"), f.get("extracted_value"), f.get("currency")
    else:
        gosterim, sayi, para = f, r.get("extracted_price"), None
    return {
        "title": r.get("title") or "Ürün",
        "source": r.get("source") or "Bilinmeyen satıcı",
        "price": str(gosterim).replace("*", "").strip() if gosterim else "-",
        "extracted_price": sayi, "para": para,
        "thumbnail": r.get("thumbnail") or r.get("image"),
        "link": r.get("link"), "rating": r.get("rating"), "reviews": r.get("reviews"),
    }


def lens_ara(foto_url, api_key):
    """Google Lens ile fotoğraftaki ürünün aynısını/benzerlerini fiyatlarıyla bulur."""
    en_iyi = []
    for tip in ("products", "visual_matches"):
        params = urlencode({"engine": "google_lens", "url": foto_url, "type": tip,
                            "hl": "tr", "country": "tr", "api_key": api_key})
        req = Request("https://serpapi.com/search.json?" + params,
                      headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urlopen(req, timeout=60) as r:
                veri = json.loads(r.read().decode("utf-8"))
        except HTTPError as ex:
            raise Exception(f"SerpApi hatası {ex.code}")
        except (URLError, TimeoutError):
            raise Exception("SerpApi'ye bağlanılamadı.")
        hata = veri.get("error")
        if hata and "hasn't returned any results" not in hata:
            raise Exception(hata)
        kartlar = [lens_karti(x) for x in (veri.get("visual_matches") or [])]
        fiyatli = [k for k in kartlar if k["extracted_price"]
                   and k["para"] in (None, "₺", "TL", "TRY")]
        if len(fiyatli) >= 3:
            return fiyatli
        en_iyi = max(en_iyi, fiyatli, key=len)
    return en_iyi


def _gemini_metin(parcalar, api_key, maks=256):
    """Verilen parçalarla (metin + görseller) Gemini'ye JSON yanıt için sorar."""
    son_hata, son_kod = "", None
    for model_adi in mevcut_modeller(api_key)[:3]:
        cfg = {"temperature": 0, "maxOutputTokens": maks,
               "responseMimeType": "application/json"}
        if model_adi.startswith("gemini-2.5"):
            cfg["thinkingConfig"] = {"thinkingBudget": 0}
        url = ("https://generativelanguage.googleapis.com/v1beta/models/"
               f"{model_adi}:generateContent")
        for deneme in range(2):
            data = {"contents": [{"parts": parcalar}], "generationConfig": cfg}
            req = Request(url, data=json.dumps(data).encode("utf-8"),
                          headers={"Content-Type": "application/json",
                                   "x-goog-api-key": api_key}, method="POST")
            try:
                with urlopen(req, timeout=40) as r:
                    sonuc = json.loads(r.read().decode("utf-8"))
                return "".join(p.get("text", "") for p in
                               sonuc["candidates"][0]["content"]["parts"])
            except HTTPError as ex:
                son_kod, son_hata = ex.code, _hata_mesaji(ex)
                if ex.code == 400 and "thinkingConfig" in cfg:
                    cfg.pop("thinkingConfig")
                    continue
                if ex.code in GECICI_HATALAR:
                    time.sleep(1.5 * (deneme + 1))
                    continue
                break
            except (URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as ex:
                son_hata = str(ex)
                break
    raise Exception(f"Gemini yanıt vermedi ({son_kod or 'bağlantı'}): {son_hata}")


def kucuk_resim_indir(url):
    """Aday küçük resmini indirir; (mime, base64) döner, olmazsa None."""
    try:
        if url.startswith("data:image"):
            bas, veri = url.split(",", 1)
            return bas[5:].split(";")[0], veri
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=10) as r:
            tip = r.headers.get_content_type()
            veri = r.read(400_000)
        if tip not in ("image/jpeg", "image/png", "image/webp"):
            return None
        return tip, base64.b64encode(veri).decode("utf-8")
    except Exception:
        return None


def eslestir(image, adaylar, api_key):
    """Her adayı fotoğraftaki ürünle Gemini'ye karşılaştırtır; 'eslesme' (0-10) yazar."""
    foto = image.copy()
    foto.thumbnail((640, 640))
    buf = io.BytesIO()
    foto.save(buf, format="JPEG", quality=75)
    parcalar = [
        {"text": "Birinci görsel kullanıcının aradığı ÜRÜN. Sonraki görseller numaralı "
                 "adaylar. Her aday için, birinci görseldeki ürünün AYNISI olup olmadığını "
                 "0-10 puanla (aynı model, tasarım, renk ve desen = 9-10). Aynı marka veya "
                 "aynı türde olması yetmez; model, desen veya renk farklıysa düşük puan ver. "
                 "Sadece aday sayısı kadar tam sayıdan oluşan bir JSON dizisi döndür, örn: [9,2,0]"},
        {"inline_data": {"mime_type": "image/jpeg",
                         "data": base64.b64encode(buf.getvalue()).decode("utf-8")}},
    ]
    with ThreadPoolExecutor(8) as ex:
        resimler = list(ex.map(kucuk_resim_indir,
                               [a.get("thumbnail") or "" for a in adaylar]))
    kullanilan = []
    for a, r in zip(adaylar, resimler):
        if r:
            kullanilan.append(a)
            parcalar += [{"text": f"Aday {len(kullanilan)}:"},
                         {"inline_data": {"mime_type": r[0], "data": r[1]}}]
    if not kullanilan:
        raise Exception("Aday resimleri indirilemedi.")
    eslesen = re.search(r"\[[\d,\s]*\]", _gemini_metin(parcalar, api_key))
    if not eslesen:
        raise Exception("Karşılaştırma sonucu okunamadı.")
    for a, puan in zip(kullanilan, json.loads(eslesen.group(0))):
        
