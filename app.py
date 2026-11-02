import streamlit as st
import json
import base64
import io
import re
import html
import time
import random
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError

from PIL import Image, ImageOps

# ============================================================
# AYARLAR
# ============================================================
st.set_page_config(
    page_title="Akıllı Alışveriş Asistanı",
    page_icon="🛍️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# TASARIM
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
:root {
  --bg:#F5F7F5; --surface:#FFFFFF; --ink:#17231E; --muted:#718078;
  --line:#E3E9E5; --brand:#126B55; --brand2:#0C5141; --soft:#EAF4EF;
}
html, body, [class*="css"], .stApp {font-family:'Manrope',sans-serif;color:var(--ink);}
.stApp {background:var(--bg);}
#MainMenu, footer, header {visibility:hidden;}
.block-container {max-width:820px;padding-top:1.4rem;padding-bottom:3rem;}
.hero {
  background:linear-gradient(135deg,#0C5141,#168267);
  color:white;border-radius:24px;padding:26px 24px;margin-bottom:18px;
  box-shadow:0 12px 28px rgba(12,81,65,.12);
}
.hero h1 {font-size:1.8rem;font-weight:800;letter-spacing:-.04em;margin:0;color:white;}
.hero p {margin:7px 0 0;color:#E0F0E9;font-size:.95rem;}
.section-title {font-size:1.05rem;font-weight:800;margin:18px 0 8px;}
.hint {color:var(--muted);font-size:.83rem;}
[data-testid="stWidgetLabel"] p,[data-testid="stWidgetLabel"] label {color:var(--ink)!important;font-weight:700;}
.stTextInput input,.stTextArea textarea {background:white!important;color:var(--ink)!important;border-radius:12px!important;}
.stTextInput input::placeholder {color:#98A39D!important;}
[data-testid="stFileUploader"] section {background:white;border:1.5px dashed #B9C9C0;border-radius:16px;}
.stButton>button {border-radius:13px;font-weight:800;min-height:2.8rem;}
.stButton>button[kind="primary"] {background:var(--brand);border:0;}
.stButton>button[kind="primary"]:hover {background:var(--brand2);}
.stButton>button[kind="secondary"] {background:white;border:1px solid var(--line);}
.stTabs [data-baseweb="tab"] {font-weight:700;}
.detected {background:white;border:1px solid var(--line);border-left:5px solid var(--brand);
  padding:14px 16px;border-radius:14px;margin:12px 0;}
.detected small {display:block;color:var(--muted);font-size:.76rem;margin-bottom:4px;}
.detected strong {font-size:1.05rem;}
.metric-row {display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin:14px 0;}
.metric {background:white;border:1px solid var(--line);border-radius:14px;padding:12px;}
.metric span {display:block;color:var(--muted);font-size:.75rem;}
.metric b {font-size:1.02rem;}
.metric.primary {background:var(--brand);border-color:var(--brand);color:white;}
.metric.primary span {color:#D5EAE2;}
.product {display:flex;gap:13px;align-items:center;background:white;border:1px solid var(--line);
  border-radius:16px;padding:12px;margin:10px 0;position:relative;}
.product.best {border:2px solid var(--brand);}
.product img,.product .placeholder {width:86px;height:86px;object-fit:contain;flex-shrink:0;
  border-radius:11px;background:#F8FAF8;}
.product .placeholder {display:flex;align-items:center;justify-content:center;font-size:1.7rem;}
.product .details {flex:1;min-width:0;}
.product .price {font-size:1.22rem;font-weight:800;color:var(--brand);}
.product .seller {font-weight:800;font-size:.9rem;margin-top:2px;}
.product .name {font-size:.79rem;color:var(--muted);line-height:1.35;margin-top:3px;}
.product a {display:inline-block;background:var(--ink);color:white!important;text-decoration:none;
  padding:9px 12px;border-radius:10px;font-size:.78rem;font-weight:800;white-space:nowrap;}
.product a:hover {background:var(--brand);}
.pill {display:inline-block;background:var(--soft);color:var(--brand);font-size:.7rem;
  font-weight:800;padding:4px 8px;border-radius:99px;margin-top:5px;}
.warning {background:#FFF7E7;border:1px solid #F0D9A9;border-radius:12px;padding:11px 13px;
  color:#72531A;font-size:.83rem;}
@media(max-width:560px) {
 .hero h1{font-size:1.48rem}.metric-row{grid-template-columns:1fr}
 .product{align-items:flex-start;flex-wrap:wrap}.product a{width:100%;text-align:center;box-sizing:border-box}
 .product img,.product .placeholder{width:72px;height:72px}
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# GİZLİ ANAHTARLAR
# ============================================================
def get_secret(name, required=True):
    try:
        value = st.secrets.get(name, "")
    except Exception:
        value = ""
    value = str(value).strip() if value else ""
    if required and not value:
        st.error(f"`{name}` anahtarı bulunamadı. Streamlit Secrets bölümüne ekle.")
        st.stop()
    return value or None

GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
SERPAPI_KEY = get_secret("SERPAPI_KEY")
IMGBB_KEY = get_secret("IMGBB_KEY", required=False)

# ============================================================
# GENEL YARDIMCILAR
# ============================================================
def safe_json_loads(raw):
    """Model cevabındaki JSON'u toleranslı biçimde ayıklar."""
    raw = (raw or "").strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}|\[.*\]", raw, flags=re.S)
        if match:
            return json.loads(match.group(0))
        raise

def api_error_message(exc):
    try:
        body = json.loads(exc.read().decode("utf-8", errors="replace"))
        err = body.get("error", {})
        return err.get("message") or str(body)
    except Exception:
        return str(exc)

def post_json(url, payload, api_key, timeout=45):
    req = Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    try:
        with urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = api_error_message(exc)
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"Bağlantı/zaman aşımı: {exc}") from exc

# ============================================================
# GEMINI MODEL LİSTESİ VE GÖRSEL TANIMA
# ============================================================
FALLBACK_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
]

@st.cache_data(ttl=1800, show_spinner=False)
def available_gemini_models(api_key):
    """API'nin gerçekten bu anahtara açtığı generateContent modellerini bulur."""
    url = "https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000"
    req = Request(url, headers={"x-goog-api-key": api_key})
    try:
        with urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception:
        return FALLBACK_MODELS

    found = []
    for model in data.get("models", []):
        if "generateContent" not in model.get("supportedGenerationMethods", []):
            continue
        # baseModelId, models.list yanıtındaki sürümlü addan daha uygun olabilir.
        name = (model.get("baseModelId") or model.get("name", "").split("/")[-1]).strip()
        low = name.lower()
        # Görsel/metin üretimi için Flash ailesini seç; TTS, live, image-only modelleri alma.
        if not re.fullmatch(r"gemini-\d+(?:\.\d+)?-flash(?:-lite)?", low):
            continue
        found.append(name)

    # Büyük sürüm ve ardından lite olmayan model önce gelsin.
    def model_sort(name):
        m = re.search(r"gemini-(\d+(?:\.\d+)?)-flash(-lite)?", name)
        return (float(m.group(1)) if m else 0, 0 if (m and m.group(2)) else 1)
    found = sorted(set(found), key=model_sort, reverse=True)
    return found[:6] or FALLBACK_MODELS

def image_to_jpeg_bytes(image, max_side=1100, quality=88):
    img = ImageOps.exif_transpose(image).convert("RGB")
    img.thumbnail((max_side, max_side))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)
    return buffer.getvalue()

def gemini_generate(parts, api_key, max_tokens=400, json_mode=False):
    models = available_gemini_models(api_key)
    errors = []
    for model in models:
        cfg = {"temperature": 0.1, "maxOutputTokens": max_tokens}
        if json_mode:
            cfg["responseMimeType"] = "application/json"
        payload = {"contents": [{"role": "user", "parts": parts}], "generationConfig": cfg}
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        try:
            result = post_json(endpoint, payload, api_key)
            candidates = result.get("candidates") or []
            if not candidates:
                feedback = result.get("promptFeedback", {})
                raise RuntimeError(f"Model yanıt üretmedi. Güvenlik/istem bilgisi: {feedback}")
            content = candidates[0].get("content", {})
            text_parts = [p.get("text", "") for p in content.get("parts", []) if p.get("text")]
            answer = "\n".join(text_parts).strip()
            if answer:
                return answer, model
            raise RuntimeError("Model boş yanıt döndürdü.")
        except Exception as exc:
            errors.append(f"{model}: {exc}")
            # Yetki/kota gibi anahtar kaynaklı sorunlarda diğer modeller de çalışmayabilir;
            # yine de model listesi içindeki sonraki uygun modeli deniyoruz.
            continue
    raise RuntimeError("Gemini ile ürün analizi yapılamadı.\n" + "\n".join(errors[-4:]))

def identify_product(image, api_key, brand_hint=""):
    jpeg = image_to_jpeg_bytes(image, max_side=1200, quality=90)
    encoded = base64.b64encode(jpeg).decode("ascii")
    hint = f"Kullanıcının verdiği marka ipucu: {brand_hint.strip()}." if brand_hint.strip() else ""

    prompt = f"""
Sen deneyimli bir e-ticaret ürün katalog uzmanısın. Fotoğrafı dikkatle incele.
{hint}

ÖNEMLİ KURALLAR:
- Önce nesnenin gerçek türünü belirle: yemek tabağı, servis tabağı, pasta tabağı,
  kase, çukur tabak, fincan, kupa, bardak, çay seti, tencere vb.
- Fincanı tabak, kaseyi tabak, bardağı kupa olarak sınıflandırma.
- Porselen/seramik/cam/emaye/metal gibi malzemeyi yalnızca görüntü destekliyorsa belirt.
- Desen, baskı, ana renk ve görülebilen marka/logoyu ayırt et.
- Marka okunmuyorsa marka uydurma; null yaz.
- Fotoğraf tek başına model kodunu veya üreticiyi kanıtlamıyorsa uydurma.
- Ürün birden fazla parçalı set ise bunu belirt.
- Arama için kısa, Türkçe ve alışverişte kullanılabilir bir ürün adı oluştur.
- Emin olmadığın alanları null bırak; tahminini kesin bilgi gibi sunma.

SADECE şu JSON biçiminde yanıt ver:
{{
 "product_type": "ürünün açık türü",
 "material": "malzeme veya null",
 "brand": "marka veya null",
 "pattern": "desen veya null",
 "color": "renk veya null",
 "set_info": "set bilgisi veya null",
 "search_query": "Google Shopping için kısa ve net arama sorgusu",
 "confidence": 0-100,
 "visual_notes": "görselde gerçekten seçilebilen kısa ayırt edici özellikler"
}}
"""
    answer, model = gemini_generate(
        [
            {"text": prompt},
            {"inline_data": {"mime_type": "image/jpeg", "data": encoded}},
        ],
        api_key,
        max_tokens=500,
        json_mode=True,
    )
    data = safe_json_loads(answer)
    if not isinstance(data, dict) or not data.get("search_query"):
        raise RuntimeError(f"Gemini beklenen ürün bilgisini döndürmedi: {answer[:500]}")
    data["_model"] = model
    return data

# ============================================================
# SERPAPI GOOGLE SHOPPING
# ============================================================
@st.cache_data(ttl=900, show_spinner=False)
def shopping_search(query, api_key):
    params = urlencode({
        "engine": "google_shopping",
        "q": query,
        "hl": "tr",
        "gl": "tr",
        "api_key": api_key,
    })
    req = Request(
        "https://serpapi.com/search.json?" + params,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    try:
        with urlopen(req, timeout=35) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"SerpApi HTTP {exc.code}: {api_error_message(exc)}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"SerpApi bağlantı hatası: {exc}") from exc

    if data.get("error"):
        raise RuntimeError(data["error"])
    return data.get("shopping_results") or data.get("inline_shopping_results") or []

def normalize(text):
    table = str.maketrans({
        "ı":"i","İ":"i","ş":"s","Ş":"s","ğ":"g","Ğ":"g",
        "ü":"u","Ü":"u","ö":"o","Ö":"o","ç":"c","Ç":"c",
    })
    return re.sub(r"[^a-z0-9 ]+", " ", str(text or "").translate(table).lower()).strip()

ACCESSORY_WORDS = [
    "kilif", "kapak", "case", "cover", "koruyucu", "aksesuar", "film",
    "kulaklik ucu", "kordon", "askilik", "tutucu", "sticker", "etiket",
    "temizleme", "temizlik", "aparat", "yedek parca",
]

def parse_price(item):
    price = item.get("price")
    if isinstance(price, dict):
        shown = price.get("value")
        numeric = price.get("extracted_value")
        currency = price.get("currency")
    else:
        shown = price
        numeric = item.get("extracted_price")
        currency = None
    try:
        numeric = float(numeric) if numeric is not None else None
    except (TypeError, ValueError):
        numeric = None
    return shown, numeric, currency

def normalize_result(raw):
    shown, numeric, currency = parse_price(raw)
    return {
        "title": raw.get("title") or "Ürün",
        "source": raw.get("source") or "Satıcı bilgisi yok",
        "price": str(shown or "-").replace("*", "").strip(),
        "numeric_price": numeric,
        "currency": currency,
        "image": raw.get("thumbnail") or raw.get("serpapi_thumbnail"),
        "link": raw.get("product_link") or raw.get("link"),
        "rating": raw.get("rating"),
        "reviews": raw.get("reviews"),
        "delivery": raw.get("delivery"),
    }

def filter_results(results, query):
    tokens = [t for t in normalize(query).split() if len(t) > 1]
    filtered = []
    for item in results:
        title = normalize(item["title"])
        # Aksesuarları ana ürün aramasından çıkar.
        if any(word in title for word in ACCESSORY_WORDS):
            continue
        if tokens:
            matched = sum(1 for token in tokens if token in title)
            # Kısa sorgularda eşleşme oranını biraz daha sıkı tut.
            threshold = 0.5 if len(tokens) <= 3 else 0.4
            if matched / len(tokens) < threshold:
                continue
        filtered.append(item)

    # Para birimi açıkça TL/TRY olmayan fiyatları TL istatistiğine dahil etme.
    return filtered

def format_tl(value):
    return f"{value:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")

def render_product(item, is_best=False):
    image_html = (
        f'<img src="{html.escape(item["image"], quote=True)}" alt="Ürün görseli">'
        if item.get("image") else '<div class="placeholder">🛍️</div>'
    )
    link = item.get("link")
    link_html = (
        f'<a href="{html.escape(link, quote=True)}" target="_blank" rel="noopener noreferrer">Ürünü incele ↗</a>'
        if link else ""
    )
    best_label = '<span class="pill">En düşük fiyat</span>' if is_best else ""
    title = html.escape(item.get("title", "Ürün"))
    seller = html.escape(item.get("source", "Satıcı"))
    price = html.escape(item.get("price", "-"))
    rating = item.get("rating")
    rating_html = f'<span class="pill">⭐ {html.escape(str(rating))}</span>' if rating else ""
    st.markdown(
        f'<div class="product {"best" if is_best else ""}>{image_html}'
        f'<div class="details"><div class="price">{price}</div>'
        f'<div class="seller">{seller}</div><div class="name">{title}</div>'
        f'{best_label}{rating_html}</div>{link_html}</div>',
        unsafe_allow_html=True,
    )

# ============================================================
# ARAYÜZ
# ============================================================
st.markdown("""
<div class="hero">
  <h1>🛍️ Akıllı Alışveriş Asistanı</h1>
  <p>Fotoğrafı yükle, ürünü tanıyalım ve mağazalardaki fiyatları karşılaştıralım.</p>
</div>
""", unsafe_allow_html=True)

with st.expander("Nasıl çalışır?", expanded=False):
    st.markdown("""
    1. Ürünün net bir fotoğrafını yükle veya kamerayla çek.
    2. Yapay zekâ ürün türünü, malzemeyi, rengi ve deseni analiz etsin.
    3. Oluşan arama adını gerekirse düzelt.
    4. Google Shopping sonuçlarını fiyatlarına göre karşılaştır.

    **İpucu:** Ürünü tek başına, iyi ışıkta ve mümkünse önden çek. Marka/model yazısı varsa fotoğrafta görünsün.
    """)

# Geçmiş aramayı temizleme
top1, top2 = st.columns([3, 1])
with top1:
    st.markdown('<div class="section-title">Ürün fotoğrafı</div>', unsafe_allow_html=True)
with top2:
    if st.button("Temizle", use_container_width=True):
        for key in ("product_data", "search_results", "last_query", "image_hash"):
            st.session_state.pop(key, None)
        st.rerun()

tab_upload, tab_camera = st.tabs(["📤 Fotoğraf yükle", "📷 Kamerayla çek"])
with tab_upload:
    uploaded = st.file_uploader(
        "JPG, JPEG veya PNG seç",
        type=["jpg", "jpeg", "png"],
        help="En fazla 10 MB önerilir.",
    )
with tab_camera:
    camera = st.camera_input("Ürünü kadraja al")

source = uploaded or camera
brand_hint = st.text_input(
    "Marka (isteğe bağlı)",
    placeholder="Örn. Kütahya Porselen, Güral, Paşabahçe",
)
extra_hint = st.text_input(
    "Ürün hakkında bildiğin başka bir şey (isteğe bağlı)",
    placeholder="Örn. 6 kişilik yemek tabağı, 27 cm",
)

if source is not None:
    try:
        raw_bytes = source.getvalue()
        if len(raw_bytes) > 10 * 1024 * 1024:
            st.error("Fotoğraf 10 MB'dan büyük. Daha küçük bir görsel yükle.")
            st.stop()
        image = ImageOps.exif_transpose(Image.open(io.BytesIO(raw_bytes))).convert("RGB")
        st.image(image, caption="Yüklediğin ürün", use_container_width=True)
    except Exception as exc:
        st.error(f"Fotoğraf okunamadı: {exc}")
        st.stop()

    if st.button("🔎 Ürünü tanı ve fiyatları bul", type="primary", use_container_width=True):
        st.session_state.pop("product_data", None)
        st.session_state.pop("search_results", None)
        st.session_state.pop("last_query", None)

        with st.status("Fotoğraf analiz ediliyor…", expanded=True) as status:
            try:
                st.write("1/2 · Görsel Gemini'ye gönderiliyor…")
                product = identify_product(image, GEMINI_API_KEY, brand_hint)
                if extra_hint.strip():
                    # Kullanıcının eklediği somut bilgiyi arama sorgusuna ekle.
                    product["search_query"] = (
                        product["search_query"] + " " + extra_hint.strip()
                    ).strip()
                st.session_state["product_data"] = product
                st.write(f"Ürün tanındı · {product.get('_model', 'Gemini')}")
                st.write("2/2 · Google Shopping fiyatları aranıyor…")
                query = product["search_query"]
                raw_results = shopping_search(query, SERPAPI_KEY)
                results = [normalize_result(x) for x in raw_results]
                filtered = filter_results(results, query)
                # Filtre çok sert davranıp tüm ürünleri silerse sonuçları kaybetme.
                if len(filtered) >= 2:
                    results = filtered
                st.session_state["search_results"] = results
                st.session_state["last_query"] = query
                status.update(label="Analiz tamamlandı", state="complete", expanded=False)
            except Exception as exc:
                status.update(label="İşlem tamamlanamadı", state="error", expanded=True)
                st.error("**Teknik hata ayrıntısı:**")
                st.code(str(exc))
                st.info(
                    "Bu hata mesajı sorunun Gemini model/anahtar, SerpApi kotası veya bağlantı "
                    "kaynaklı olup olmadığını ayırt etmeye yardımcı olur."
                )

# Ürün bilgisi düzenlenebilir
product = st.session_state.get("product_data")
if product:
    st.markdown('<div class="section-title">Tanımlanan ürün</div>', unsafe_allow_html=True)
    brand = product.get("brand") or "Marka belirlenemedi"
    details = [
        ("Ürün türü", product.get("product_type")),
        ("Malzeme", product.get("material")),
        ("Marka", brand),
        ("Desen", product.get("pattern")),
        ("Renk", product.get("color")),
        ("Set bilgisi", product.get("set_info")),
    ]
    cols = st.columns(2)
    for index, (label, value) in enumerate(details):
        with cols[index % 2]:
            st.caption(label)
            st.markdown(f"**{value or 'Belirlenemedi'}**")
    confidence = product.get("confidence")
    if isinstance(confidence, (int, float)):
        st.caption(f"Yapay zekâ güven puanı: %{int(max(0, min(100, confidence)))}")
    if product.get("visual_notes"):
        st.caption(product["visual_notes"])

    edited_query = st.text_input(
        "Arama adını düzenle",
        value=st.session_state.get("last_query", product.get("search_query", "")),
        help="Yanlış ürün türü veya desen varsa burada düzeltip yeniden arat.",
        key="editable_search_query",
    )
    if st.button("Bu ürün adıyla fiyatları yeniden ara", use_container_width=True):
        if not edited_query.strip():
            st.warning("Arama adı boş olamaz.")
        else:
            with st.spinner("Yeni arama yapılıyor…"):
                try:
                    raw_results = shopping_search(edited_query.strip(), SERPAPI_KEY)
                    results = [normalize_result(x) for x in raw_results]
                    filtered = filter_results(results, edited_query.strip())
                    if len(filtered) >= 2:
                        results = filtered
                    st.session_state["search_results"] = results
                    st.session_state["last_query"] = edited_query.strip()
                    st.rerun()
                except Exception as exc:
                    st.error(f"Fiyat araması yapılamadı: {exc}")

# Sonuçlar
results = st.session_state.get("search_results")
if results is not None:
    st.markdown('<div class="section-title">Fiyat karşılaştırması</div>', unsafe_allow_html=True)
    st.caption(f'Aranan ifade: {st.session_state.get("last_query", "")}')
    if not results:
        st.warning("Bu arama için sonuç bulunamadı. Arama adını kısaltmayı veya marka/model eklemeyi dene.")
    else:
        priced = [
            r for r in results
            if r.get("numeric_price") is not None
            and (r.get("currency") in (None, "", "₺", "TL", "TRY"))
        ]
        if priced:
            values = [r["numeric_price"] for r in priced]
            st.markdown(
                f'<div class="metric-row">'
                f'<div class="metric primary"><span>En düşük</span><b>{format_tl(min(values))}</b></div>'
                f'<div class="metric"><span>Ortalama</span><b>{format_tl(sum(values)/len(values))}</b></div>'
                f'<div class="metric"><span>En yüksek</span><b>{format_tl(max(values))}</b></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.caption(f"{len(values)} TL fiyatı üzerinden hesaplandı. Kargo ve ürün adedi farklı olabilir.")

        sort_mode = st.radio(
            "Sıralama",
            ["En ucuz", "En pahalı", "En yüksek puan"],
            horizontal=True,
            label_visibility="collapsed",
        )
        if sort_mode == "En ucuz":
            ordered = sorted(results, key=lambda r: r.get("numeric_price") or float("inf"))
        elif sort_mode == "En pahalı":
            ordered = sorted(results, key=lambda r: r.get("numeric_price") or -1, reverse=True)
        else:
            ordered = sorted(results, key=lambda r: float(r.get("rating") or 0), reverse=True)

        for item in ordered[:12]:
            best = bool(priced) and item is min(priced, key=lambda r: r["numeric_price"])
            render_product(item, is_best=best)

st.markdown(
    '<div style="text-align:center;color:#829087;font-size:.76rem;margin-top:34px">'
    'Fiyatlar mağazalara ve zamana göre değişebilir. Satın almadan önce ürün adedini, '
    'ölçüyü, kargo ücretini ve satıcı bilgilerini kontrol et.</div>',
    unsafe_allow_html=True,
)
