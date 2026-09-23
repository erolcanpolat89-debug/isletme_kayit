import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import libsql_client as libsql
import base64
from io import BytesIO
from html import escape
import streamlit.components.v1 as components
from zoneinfo import ZoneInfo
import zipfile

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Sayfa Ayarları
st.set_page_config(
    page_title="Midyeci Abla Canlı Takip",
    page_icon="🦪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Yerel PNG Dosyasını Base64 Formatına Çevirme
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

img_base64 = get_base64_image("1000295034.png")

# Koyu Tema & Arka Plan Logo
st.markdown(f"""
<style>
    /* Ana Ekran Arka Planı */
    .stApp {{
        background: linear-gradient(rgba(15, 23, 42, 0.55), rgba(15, 23, 42, 0.55)), 
                    url('data:image/png;base64,{img_base64}') no-repeat center center fixed !important;
        background-size: cover !important;
    }}

    /* Streamlit Üst Çubuk Transparent Yapma */
    header, [data-testid="stHeader"], [data-testid="stToolbar"] {{
        background: transparent !important;
    }}

    /* NEON YANIP SÖNEN ORTALI KUTU TASARIMI */
    @keyframes neonPulse {{
        0% {{
            color: #e5c158;
            text-shadow: 0 0 5px #ffcc00, 0 0 10px #ffcc00, 0 0 15px #ff9900;
        }}
        50% {{
            color: #fff1b0;
            text-shadow: 0 0 2px #fff, 0 0 5px #ffcc00, 0 0 8px #ffcc00;
        }}
        100% {{
            color: #e5c158;
            text-shadow: 0 0 5px #ffcc00, 0 0 10px #ffcc00, 0 0 15px #ff9900;
        }}
    }}

    .neon-kutu {{
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(30, 30, 35, 0.45);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 12px;
        padding: 12px 15px;
        margin-top: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }}

    .neon-yazi {{
        font-size: 26px;
        font-weight: 800;
        font-style: italic;
        letter-spacing: 1px;
        animation: neonPulse 2s infinite ease-in-out;
        text-align: center;
    }}

    /* SEKMELERİ ÇEVRELEYEN ARKA GÖLGELİ KUTU */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background: rgba(255, 255, 255, 0.10) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 12px !important;
        padding: 8px !important;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important;
    }}

    /* SEKMELERİN KENDİSİ VE DARK GOLD YAZILAR */
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(0, 0, 0, 0.25) !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        color: #c5a059 !important; /* Dark Gold */
        text-shadow: 0px 1px 3px rgba(0, 0, 0, 0.9);
        border: 1px solid rgba(197, 160, 89, 0.3) !important;
        position: relative;
        transition: all 0.3s ease;
    }}

    .stTabs [data-baseweb="tab"] * {{
        color: #c5a059 !important;
        font-weight: 800 !important;
    }}

    /* SEKME ÜZERİNE GELİNCE (HOVER) - IŞIK YANSIMASI VE ALT PARLAMA ÇİZGİSİ */
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: rgba(197, 160, 89, 0.25) !important;
        border-color: #c5a059 !important;
        box-shadow: 0 6px 20px rgba(197, 160, 89, 0.4), inset 0 0 10px rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-2px);
    }}

    .stTabs [data-baseweb="tab"]:hover::after {{
        content: '';
        position: absolute;
        bottom: -4px;
        left: 10%;
        width: 80%;
        height: 3px;
        background: linear-gradient(90deg, transparent, #f3e5ab, transparent);
        box-shadow: 0 0 8px #d4af37;
        border-radius: 2px;
    }}

    /* Seçili Sekme (Active Tab) */
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #c5a059, #8a6d29) !important;
        border-color: #f3e5ab !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
        transform: translateY(0px);
    }}

    .stTabs [aria-selected="true"] * {{
        color: #ffffff !important;
    }}

    .stTabs [aria-selected="true"]::after {{
        content: '';
        position: absolute;
        bottom: -4px;
        left: 5%;
        width: 90%;
        height: 3px;
        background: #ffffff;
        box-shadow: 0 0 10px #ffffff, 0 0 15px #d4af37;
        border-radius: 2px;
    }}

    /* TÜM ETIKETLER VE BAŞLIKLAR */
    .stApp, .stApp p, .stApp label, .stApp span, 
    div[data-testid="stMarkdownContainer"] p, 
    label[data-testid="stWidgetLabel"] p {{
        color: #ffffff !important;
        font-weight: 700 !important;
        opacity: 1 !important;
        text-shadow: 0px 1px 4px rgba(0, 0, 0, 0.9);
    }}

    div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {{
        color: #ffffff !important;
    }}

    /* TARİH VE INPUT KUTULARI */
    div[data-baseweb="input"] input, 
    div[data-baseweb="base-input"] input,
    div[data-testid="stTextInput"] input,
    div[data-testid="stDateInput"] input,
    input[type="text"], 
    input[type="number"] {{
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 800 !important;
        background-color: #ffffff !important;
        opacity: 1 !important;
    }}

    div[data-baseweb="input"], 
    div[data-baseweb="base-input"],
    div[data-baseweb="select"] {{
        background-color: #ffffff !important;
        border-radius: 10px !important;
    }}

    div[data-baseweb="select"] div {{
        color: #000000 !important;
        font-weight: 800 !important;
    }}

    /* Glassmorphic Form Kutu Alanları */
    div[data-testid="stForm"], div[data-testid="stExpander"] {{
        background: rgba(15, 23, 42, 0.45) !important;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        padding: 18px !important;
    }}

    /* Kaydet Butonları */
    div.stButton > button, div.stFormSubmitButton > button {{
        width: 100% !important;
        height: 50px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        background: linear-gradient(135deg, #ff4b4b, #ef4444) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(239, 68, 68, 0.4);
    }}

    /* Ön İzleme Yazdırma Kağıdı Tasarımı */
    .preview-box {{
        background: #ffffff !important;
        color: #000000 !important;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }}
    .preview-box * {{
        color: #000000 !important;
        text-shadow: none !important;
    }}

    /* Metrik Kartları */
    div[data-testid="stMetric"] {{
        background: rgba(15, 23, 42, 0.45);
        backdrop-filter: blur(6px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 14px;
        padding: 12px 16px;
    }}

    div[data-testid="stMetricValue"] {{
        font-size: 24px !important;
        font-weight: 800 !important;
        color: #ff6b6b !important;
    }}

    div[data-testid="stMetricLabel"] {{
        color: #cbd5e1 !important;
    }}

    /* =====================================================
       PROFESYONEL KONTROL PANELİ
       ===================================================== */
    .hero-panel {{
        background: linear-gradient(135deg, rgba(10,15,25,.88), rgba(44,32,12,.78));
        border: 1px solid rgba(229,193,88,.38);
        border-radius: 22px;
        padding: 22px 24px;
        margin: 8px 0 18px 0;
        box-shadow: 0 18px 50px rgba(0,0,0,.42), inset 0 0 30px rgba(229,193,88,.04);
        backdrop-filter: blur(12px);
    }}
    .hero-title {{
        font-size: 30px;
        font-weight: 900;
        letter-spacing: .5px;
        margin: 0;
        color: #f6df9b;
        text-shadow: 0 0 18px rgba(229,193,88,.22);
    }}
    .hero-sub {{
        color: #d7dce5;
        margin-top: 5px;
        font-size: 14px;
    }}
    .status-pill {{
        display: inline-block;
        padding: 6px 11px;
        border-radius: 999px;
        background: rgba(34,197,94,.13);
        border: 1px solid rgba(34,197,94,.35);
        color: #86efac;
        font-weight: 800;
        font-size: 12px;
        margin-top: 10px;
    }}
    .section-ribbon {{
        display:flex;
        align-items:center;
        gap:10px;
        margin: 18px 0 10px 0;
        padding: 10px 14px;
        border-left: 4px solid #c5a059;
        background: linear-gradient(90deg, rgba(197,160,89,.15), rgba(197,160,89,.02));
        border-radius: 10px;
        font-weight: 900;
        color:#f3e5ab;
    }}
    .mini-note {{
        color:#b9c0cc;
        font-size:12px;
        margin-top:-4px;
    }}
</style>
""", unsafe_allow_html=True)

# Turso Bulut Veritabanı Bağlantı Fonksiyonu
def get_client():
    url = st.secrets["TURSO_DATABASE_URL"]
    if url.startswith("libsql://"):
        url = url.replace("libsql://", "https://")
    elif url.startswith("wss://"):
        url = url.replace("wss://", "https://")
        
    token = st.secrets["TURSO_AUTH_TOKEN"]
    return libsql.create_client_sync(url=url, auth_token=token)

client = get_client()

# Yardımcı Fonksiyon: Libsql Sonucunu Pandas Dataframe'e Çevirir
def run_query_df(query, params=None):
    res = client.execute(query, params or [])
    columns = res.columns
    rows = res.rows
    return pd.DataFrame(rows, columns=columns)

# Tabloları Oluşturma
client.execute('''
    CREATE TABLE IF NOT EXISTS firmalar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firma_adi TEXT UNIQUE,
        telefon TEXT,
        aciklama TEXT
    )
''')

client.execute('''
    CREATE TABLE IF NOT EXISTS toptan_satis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firma_adi TEXT,
        tarih TEXT,
        islem_turu TEXT DEFAULT 'Satış',
        adet INTEGER DEFAULT 0,
        birim_fiyat REAL DEFAULT 0.0,
        toplam_tutar REAL,
        aciklama TEXT
    )
''')

client.execute('''
    CREATE TABLE IF NOT EXISTS dukkan_hareket (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarih TEXT,
        islem_tipi TEXT,
        kategori TEXT,
        urun_adi TEXT,
        miktar INTEGER,
        birim_fiyat REAL,
        tutar REAL
    )
''')

# Şık, Ortalanmış ve Neon Yanıp Sönen Başlık Kutusu
st.markdown("""
<div class="neon-kutu">
    <div class="neon-yazi">🦪 MİDYECİ ABLA CANLI TAKİP 🦪</div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# PROFESYONEL RAPOR / PDF YARDIMCILARI
# =========================================================
def _tr_now():
    """Türkiye saatini güvenli şekilde döndürür."""
    try:
        return datetime.now(ZoneInfo("Europe/Istanbul"))
    except Exception:
        # ZoneInfo kullanılamazsa uygulama yine çalışsın.
        return datetime.now()


def _money(value):
    try:
        return f"{float(value or 0):,.2f} TL"
    except Exception:
        return "0.00 TL"


def _num(value):
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def _register_pdf_fonts():
    regular = "DejaVuSans.ttf"
    bold = "DejaVuSans-Bold.ttf"
    try:
        if "DejaVu" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("DejaVu", regular))
            pdfmetrics.registerFont(TTFont("DejaVu-Bold", bold))
        return "DejaVu", "DejaVu-Bold"
    except Exception:
        return "Helvetica", "Helvetica-Bold"


def _pdf_header(canvas, doc):
    canvas.saveState()
    canvas.setFont("DejaVu", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(18 * mm, 10 * mm, "Midyeci Abla Canlı Takip")
    canvas.drawRightString(192 * mm, 10 * mm, f"Sayfa {doc.page}")
    canvas.restoreState()


def build_dukkan_pdf(df, bas_tarih, bit_tarih, kategori, net, gelir, gider):
    regular, bold = _register_pdf_fonts()
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=12 * mm, leftMargin=12 * mm,
        topMargin=14 * mm, bottomMargin=16 * mm,
        title="Midyeci Abla - Dükkan Ekstresi"
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TRTitle", fontName=bold, fontSize=17, leading=21, alignment=TA_CENTER, spaceAfter=8))
    styles.add(ParagraphStyle(name="TRSub", fontName=regular, fontSize=9, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=10))
    styles.add(ParagraphStyle(name="TRBody", fontName=regular, fontSize=8.5, leading=11))
    styles.add(ParagraphStyle(name="TRRight", fontName=regular, fontSize=8.5, leading=11, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name="TRSmall", fontName=regular, fontSize=7.5, leading=9))

    story = [
        Paragraph("MİDYECİ ABLA", styles["TRTitle"]),
        Paragraph("DÜKKAN CARİ EKSTRESİ / GELİR-GİDER RAPORU", styles["TRTitle"]),
        Paragraph(f"Tarih Aralığı: {bas_tarih} - {bit_tarih} &nbsp;&nbsp; | &nbsp;&nbsp; Kategori: {escape(str(kategori))}", styles["TRSub"]),
    ]

    summary = [
        [Paragraph("Toplam Gelir", styles["TRBody"]), Paragraph(_money(gelir), styles["TRRight"]),
         Paragraph("Toplam Gider", styles["TRBody"]), Paragraph(_money(gider), styles["TRRight"]),
         Paragraph("Net Sonuç", styles["TRBody"]), Paragraph(_money(net), styles["TRRight"])],
    ]
    t = Table(summary, colWidths=[25*mm, 28*mm, 25*mm, 28*mm, 22*mm, 28*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F4F6F8")),
        ("BOX", (0,0), (-1,-1), 0.6, colors.HexColor("#C8CDD3")),
        ("INNERGRID", (0,0), (-1,-1), 0.3, colors.HexColor("#D8DDE2")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [t, Spacer(1, 7*mm)]

    rows = [[
        Paragraph("Tarih", styles["TRSmall"]), Paragraph("İşlem", styles["TRSmall"]),
        Paragraph("Kategori", styles["TRSmall"]), Paragraph("Ürün / Açıklama", styles["TRSmall"]),
        Paragraph("Adet", styles["TRSmall"]), Paragraph("Birim", styles["TRSmall"]),
        Paragraph("Tutar", styles["TRSmall"])
    ]]
    for _, r in df.iterrows():
        islem = str(r.get("islem_tipi", ""))
        rows.append([
            Paragraph(escape(str(r.get("tarih", "")))[:16], styles["TRSmall"]),
            Paragraph(escape(islem), styles["TRSmall"]),
            Paragraph(escape(str(r.get("kategori", ""))), styles["TRSmall"]),
            Paragraph(escape(str(r.get("urun_adi", "") or "-")), styles["TRSmall"]),
            Paragraph(f"{_num(r.get('miktar')):,.0f}", styles["TRSmall"]),
            Paragraph(_money(r.get("birim_fiyat")), styles["TRSmall"]),
            Paragraph(_money(r.get("tutar")), styles["TRSmall"]),
        ])

    table = Table(rows, repeatRows=1, colWidths=[21*mm, 31*mm, 24*mm, 43*mm, 14*mm, 22*mm, 25*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#20252B")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#C9CDD1")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (4,1), (6,-1), "RIGHT"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F9FA")]),
        ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story += [table, Spacer(1, 5*mm), Paragraph("Not: Bu rapor sistemdeki kayıtlar esas alınarak oluşturulmuştur.", styles["TRSmall"])]
    doc.build(story, onFirstPage=_pdf_header, onLaterPages=_pdf_header)
    buf.seek(0)
    return buf.getvalue()


def build_toptan_pdf(df, firma, bas_tarih, bit_tarih, devir, satis, tahsilat, bakiye):
    regular, bold = _register_pdf_fonts()
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=12 * mm, leftMargin=12 * mm,
        topMargin=14 * mm, bottomMargin=16 * mm,
        title=f"{firma} - Cari Ekstre"
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TRTitle", fontName=bold, fontSize=17, leading=21, alignment=TA_CENTER, spaceAfter=8))
    styles.add(ParagraphStyle(name="TRSub", fontName=regular, fontSize=9, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=10))
    styles.add(ParagraphStyle(name="TRBody", fontName=regular, fontSize=8.5, leading=11))
    styles.add(ParagraphStyle(name="TRRight", fontName=regular, fontSize=8.5, leading=11, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name="TRSmall", fontName=regular, fontSize=7.5, leading=9))

    story = [
        Paragraph("MİDYECİ ABLA", styles["TRTitle"]),
        Paragraph("TOPTAN CARİ HESAP EKSTRESİ", styles["TRTitle"]),
        Paragraph(f"Firma: <b>{escape(str(firma))}</b> &nbsp;&nbsp; | &nbsp;&nbsp; {bas_tarih} - {bit_tarih}", styles["TRSub"]),
    ]
    summary = [[
        Paragraph("Devir", styles["TRBody"]), Paragraph(_money(devir), styles["TRRight"]),
        Paragraph("Dönem Satış", styles["TRBody"]), Paragraph(_money(satis), styles["TRRight"]),
        Paragraph("Tahsilat", styles["TRBody"]), Paragraph(_money(tahsilat), styles["TRRight"]),
        Paragraph("Kapanış", styles["TRBody"]), Paragraph(_money(bakiye), styles["TRRight"]),
    ]]
    t = Table(summary, colWidths=[18*mm, 24*mm, 24*mm, 24*mm, 20*mm, 24*mm, 20*mm, 25*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F4F6F8")),
        ("BOX", (0,0), (-1,-1), 0.6, colors.HexColor("#C8CDD3")),
        ("INNERGRID", (0,0), (-1,-1), 0.3, colors.HexColor("#D8DDE2")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [t, Spacer(1, 7*mm)]

    rows = [[
        Paragraph("Tarih", styles["TRSmall"]), Paragraph("İşlem", styles["TRSmall"]),
        Paragraph("Adet", styles["TRSmall"]), Paragraph("Birim Fiyat", styles["TRSmall"]),
        Paragraph("Tutar", styles["TRSmall"]), Paragraph("Bakiye", styles["TRSmall"]),
        Paragraph("Açıklama", styles["TRSmall"])
    ]]
    running = _num(devir)
    for _, r in df.iterrows():
        tutar = _num(r.get("toplam_tutar"))
        if str(r.get("islem_turu")) == "Satış":
            running += tutar
        else:
            running -= tutar
        rows.append([
            Paragraph(escape(str(r.get("tarih", "")))[:16], styles["TRSmall"]),
            Paragraph(escape(str(r.get("islem_turu", ""))), styles["TRSmall"]),
            Paragraph(f"{_num(r.get('adet')):,.0f}", styles["TRSmall"]),
            Paragraph(_money(r.get("birim_fiyat")), styles["TRSmall"]),
            Paragraph(_money(tutar), styles["TRSmall"]),
            Paragraph(_money(running), styles["TRSmall"]),
            Paragraph(escape(str(r.get("aciklama", "") or "-")), styles["TRSmall"]),
        ])

    table = Table(rows, repeatRows=1, colWidths=[21*mm, 24*mm, 14*mm, 24*mm, 24*mm, 25*mm, 50*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#20252B")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#C9CDD1")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (2,1), (5,-1), "RIGHT"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F9FA")]),
        ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story += [table, Spacer(1, 5*mm), Paragraph("Bakiye hesabı: Satışlar borç ekler, tahsilatlar borcu düşürür.", styles["TRSmall"])]
    doc.build(story, onFirstPage=_pdf_header, onLaterPages=_pdf_header)
    buf.seek(0)
    return buf.getvalue()


# =========================================================

# =========================================================
# 2 AŞAMALI ANA MENÜ / YÖNETİM MERKEZİ
# =========================================================
# 1. AŞAMA: Karşılama ve ana menü
# 2. AŞAMA: Seçilen modülün kendi ekranı
if "aktif_sayfa" not in st.session_state:
    st.session_state.aktif_sayfa = "ANA_MENU"


def ana_menuye_don():
    st.session_state.aktif_sayfa = "ANA_MENU"
    st.rerun()

now_tr = _tr_now()
bugun = now_tr.strftime("%Y-%m-%d")
aktif_ay = now_tr.strftime("%Y-%m")

# Canlı saat/tarih — tüm ekranlarda görünür.
components.html(
    """
    <div style="font-family:Arial,sans-serif; background:linear-gradient(135deg,#111827,#30230f);
        border:1px solid rgba(229,193,88,.45); border-radius:18px; padding:10px 18px;
        color:white; text-align:center; box-shadow:0 10px 35px rgba(0,0,0,.35);">
        <div id="saat" style="font-size:27px;font-weight:900;color:#f6df9b;letter-spacing:1px;"></div>
        <div id="tarih" style="font-size:13px;color:#d1d5db;margin-top:3px;"></div>
    </div>
    <script>
    function guncelleSaat(){
        const d=new Date();
        const saat=d.toLocaleTimeString('tr-TR',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
        const tarih=d.toLocaleDateString('tr-TR',{weekday:'long',day:'2-digit',month:'long',year:'numeric'});
        document.getElementById('saat').innerText='🕒 '+saat;
        document.getElementById('tarih').innerText='📅 '+tarih;
    }
    guncelleSaat(); setInterval(guncelleSaat,1000);
    </script>
    """,
    height=84,
)

# Ana menüde kullanılacak özetler
if st.session_state.aktif_sayfa == "ANA_MENU":
    df_d_ay = run_query_df("""
        SELECT
            COALESCE(SUM(CASE WHEN islem_tipi='Günlük Satış (Gelir)' THEN tutar ELSE 0 END),0) AS gelir,
            COALESCE(SUM(CASE WHEN islem_tipi='Dükkan Gideri (Gider)' THEN tutar ELSE 0 END),0) AS gider,
            COUNT(*) AS hareket
        FROM dukkan_hareket
        WHERE SUBSTR(tarih,1,7)=?
    """, [aktif_ay])

    df_t_ay = run_query_df("""
        SELECT
            COALESCE(SUM(CASE WHEN islem_turu='Satış' THEN toplam_tutar ELSE 0 END),0) AS satis,
            COALESCE(SUM(CASE WHEN islem_turu='Tahsilat' THEN toplam_tutar ELSE 0 END),0) AS tahsilat,
            COUNT(*) AS hareket
        FROM toptan_satis
        WHERE SUBSTR(tarih,1,7)=?
    """, [aktif_ay])

    df_f_say = run_query_df("SELECT COUNT(*) AS adet FROM firmalar")
    ay_gelir = _safe_sum(df_d_ay, "gelir")
    ay_gider = _safe_sum(df_d_ay, "gider")
    ay_toptan_satis = _safe_sum(df_t_ay, "satis")
    ay_toptan_tahsilat = _safe_sum(df_t_ay, "tahsilat")
    firma_sayisi = int(df_f_say['adet'].iloc[0]) if not df_f_say.empty else 0
    ay_net = ay_gelir - ay_gider

    st.markdown(f"""
    <div class="hero-panel">
        <div class="hero-title">🦪 MİDYECİ ABLA • YÖNETİM MERKEZİ</div>
        <div class="hero-sub">Hoş geldin abi. Yapmak istediğin işlemi aşağıdan seç; seçtiğin bölümün içine geçelim.</div>
        <span class="status-pill">● VERİTABANI BAĞLI • {firma_sayisi} FİRMA KAYITLI</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-ribbon">🧭 ANA İŞLEM MENÜSÜ</div>', unsafe_allow_html=True)
    st.caption("Önce bölümü seç. İçeri girdiğinde kendi işlemlerini yap; üstteki Geri butonuyla bu menüye dönebilirsin.")

    menu_items = [
        ("🏪 DÜKKAN", "Günlük satışlar, giderler, ciro, ekstre ve dükkan raporları", "DUKKAN"),
        ("🚚 TOPTAN", "Toptan satış, tahsilat, tarih bazlı işlemler ve kayıt yönetimi", "TOPTAN"),
        ("🏢 FİRMALAR", "Firma ekleme, düzenleme, silme ve firma bilgileri", "FIRMALAR"),
        ("📊 CARİ EKSTRE", "Dükkan ve toptan cari raporları, bakiye ve profesyonel PDF", "EKSTRE"),
        ("💰 BORÇ / ALACAK", "Firma bakiyeleri, borç-alacak durumu ve hareket geçmişi", "BORC"),
    ]

    for baslik, aciklama, hedef in menu_items:
        c1, c2 = st.columns([5.8, 1.2])
        with c1:
            st.markdown(
                f"""<div class="menu-card"><div class="menu-title">{baslik}</div><div class="menu-desc">{aciklama}</div></div>""",
                unsafe_allow_html=True,
            )
        with c2:
            if st.button("AÇ  ›", key=f"ana_menu_{hedef}", use_container_width=True):
                st.session_state.aktif_sayfa = hedef
                st.rerun()

    st.markdown('<div class="section-ribbon">📊 HIZLI DURUM</div>', unsafe_allow_html=True)
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("🏪 Dükkan Net", _money(ay_net))
    k2.metric("🚚 Toptan Satış", _money(ay_toptan_satis))
    k3.metric("💵 Toptan Tahsilat", _money(ay_toptan_tahsilat))
    k4.metric("🏢 Firma", f"{firma_sayisi:,}")

    qc1, qc2 = st.columns([2, 1])
    with qc1:
        st.markdown(f"**📅 Bugün:** `{now_tr.strftime('%d.%m.%Y')}` &nbsp;&nbsp; **🕒 Saat:** `{now_tr.strftime('%H:%M:%S')}`")
    with qc2:
        if st.button("🔄 Paneli Yenile", use_container_width=True, key="dashboard_refresh_home"):
            st.rerun()

    with st.expander("🛡️ Veri Güvenliği • Mevcut Kayıtları Yedekle", expanded=False):
        st.caption("Bu işlem veritabanındaki kayıtları silmez veya değiştirmez; sadece CSV arşivi oluşturur.")
        st.download_button(
            "📦 3 Tabloyu ZIP Olarak Yedekle",
            data=create_full_backup_zip(),
            file_name=f"midyeci_abla_yedek_{now_tr.strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip",
            use_container_width=True,
            key="full_backup_download_home"
        )

# =========================================================
# 2. AŞAMA: MODÜL EKRANLARI
# =========================================================
if st.session_state.aktif_sayfa == "DUKKAN":
    top1, top2 = st.columns([1, 6])
    with top1:
        if st.button("⬅️ Geri", key="geri_dukkan", use_container_width=True):
            ana_menuye_don()
    with top2:
        st.markdown('<div class="module-path">🦪 MİDYECİ ABLA  /  DUKKAN</div>', unsafe_allow_html=True)

        st.subheader("🏪 Dükkan Hareketleri & Ekstre")
        st.caption("Günlük satış, gider, ürün hareketleri, dönem karşılaştırmaları ve profesyonel PDF raporları.")
    
        islem_modu = st.radio("İşlem Seçin:", ["🔴 Yeni Hareket", "📅 Tarihe Göre Bul", "📈 Dükkan Ekstresi", "📊 Aylık Karşılaştırma", "📋 Tüm Kayıtları Yönet", "🗓️ İki Tarih Arası Ciro"], horizontal=True)

        if islem_modu == "🔴 Yeni Hareket":
            kategoriler = ["Midye", "Çiğ Köfte", "İçecek", "Dükkan Gideri", "Personel", "Diğer"]
        
            with st.form("dukkan_form_yeni", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    islem_tipi = st.selectbox("İşlem Tipi", ["Günlük Satış (Gelir)", "Dükkan Gideri (Gider)"])
                    tarih_secim = st.date_input("Tarih", datetime.now(), key="yeni_hareket_tarih")
                    kategori = st.selectbox("Kategori", kategoriler, index=0, key="yeni_hareket_kategori")
                with col2:
                    urun_adi = st.text_input("Ürün / Detay Açıklaması", placeholder="Örn: Pepsi sarf malzemeleri", key="yeni_hareket_urun")
                    miktar = st.number_input("Miktar / Adet", min_value=1, value=1, step=1, key="yeni_hareket_miktar")
                
                    son_fiyat_sorgu = run_query_df("SELECT birim_fiyat FROM dukkan_hareket WHERE kategori=? AND birim_fiyat > 0 ORDER BY id DESC LIMIT 1", [kategori])
                    varsayilan_fiyat = float(son_fiyat_sorgu['birim_fiyat'].iloc[0]) if not son_fiyat_sorgu.empty else 0.0
                
                    birim_fiyat = st.number_input("Birim Fiyat (TL)", min_value=0.0, value=varsayilan_fiyat, step=0.5, format="%.2f", key="yeni_hareket_fiyat")

                hesaplanan_tutar = miktar * birim_fiyat
                st.info(f"Hesaplanan Toplam Tutar: **{hesaplanan_tutar:,.2f} TL** (Seçilen kategori son fiyatı: {varsayilan_fiyat} TL)")

                submitted = st.form_submit_button("💾 Dükkan Hareketi Kaydet")
                if submitted:
                    if hesaplanan_tutar > 0:
                        simdi_zaman = datetime.now().strftime("%H:%M:%S")
                        tam_tarih_saat = f"{tarih_secim.strftime('%Y-%m-%d')} {simdi_zaman}"
                    
                        kayit_aciklama = urun_adi if urun_adi and urun_adi.strip() != "" else kategori
                    
                        client.execute(
                            "INSERT INTO dukkan_hareket (tarih, islem_tipi, kategori, urun_adi, miktar, birim_fiyat, tutar) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            [tam_tarih_saat, islem_tipi, kategori, kayit_aciklama, miktar, birim_fiyat, hesaplanan_tutar]
                        )
                        st.success(f"Dükkan hareketi başarıyla kaydedildi! Toplam: {hesaplanan_tutar:,.2f} TL ({tam_tarih_saat})")
                        st.rerun()
                    else:
                        st.warning("Lütfen geçerli bir miktar ve birim fiyat girin!")

            st.markdown("---")
            st.subheader("📋 Bugünün Dükkan Kayıtları")
        
            df_bugun_dukkan = run_query_df("SELECT * FROM dukkan_hareket WHERE SUBSTR(tarih, 1, 10) = ? ORDER BY id DESC", [bugun])
        
            if not df_bugun_dukkan.empty:
                st.dataframe(df_bugun_dukkan, use_container_width=True)
            else:
                st.info("Bugüne ait henüz dükkan hareketi kaydedilmedi.")

        elif islem_modu == "📅 Tarihe Göre Bul":
            st.subheader("📅 Tarihe Göre Dükkan İşlemi Arama ve Özet")
            secilen_tarih = st.date_input("Sorgulanacak Tarih Seçin:", datetime.now(), key="dukkan_tarih_sorgu")
            str_tarih = secilen_tarih.strftime("%Y-%m-%d")
        
            df_dukkan_gun = run_query_df("SELECT * FROM dukkan_hareket WHERE SUBSTR(tarih, 1, 10) = ? ORDER BY id DESC", [str_tarih])
        
            if df_dukkan_gun.empty:
                st.warning(f"🔍 {str_tarih} tarihine ait dükkan kayıt bulunamadı.")
            else:
                st.success(f"📌 {str_tarih} Tarihindeki Kayıtlar ({len(df_dukkan_gun)} Adet)")
            
                toplam_gelir = df_dukkan_gun[df_dukkan_gun["islem_tipi"] == "Günlük Satış (Gelir)"]["tutar"].sum() if "islem_tipi" in df_dukkan_gun.columns else 0
                toplam_gider = df_dukkan_gun[df_dukkan_gun["islem_tipi"] == "Dükkan Gideri (Gider)"]["tutar"].sum() if "islem_tipi" in df_dukkan_gun.columns else 0
            
                df_gelirler = df_dukkan_gun[df_dukkan_gun['islem_tipi'] == 'Günlük Satış (Gelir)']
                toplam_ciro = df_gelirler['tutar'].sum() if not df_gelirler.empty else 0.0
            
                midye_df = df_gelirler[df_gelirler['kategori'] == 'Midye']
                toplam_midye = midye_df['miktar'].sum() if not midye_df.empty else 0
            
                cig_kofte_df = df_gelirler[df_gelirler['kategori'] == 'Çiğ Köfte']
                toplam_cig_kofte = cig_kofte_df['miktar'].sum() if not cig_kofte_df.empty else 0
            
                icecek_df = df_gelirler[df_gelirler['kategori'] == 'İçecek']
                toplam_icecek = icecek_df['miktar'].sum() if not icecek_df.empty else 0

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Seçilen Gün Ciro", f"{toplam_ciro:,.2f} TL")
                with c2:
                    st.metric("Toplam Midye", f"{int(toplam_midye):,} adet")
                with c3:
                    st.metric("Toplam Çiğ Köfte", f"{int(toplam_cig_kofte):,} adet")
                with c4:
                    st.metric("Toplam İçecek", f"{int(toplam_icecek):,} adet")
            
                st.markdown("---")
                c_m1, c_m2, c_m3 = st.columns(3)
                c_m1.metric("Günün Geliri", f"{toplam_gelir:,.2f} TL")
                c_m2.metric("Günün Gideri", f"{toplam_gider:,.2f} TL")
                c_m3.metric("Net Durum", f"{(toplam_gelir - toplam_gider):,.2f} TL")

                st.markdown("---")
                st.dataframe(df_dukkan_gun, use_container_width=True)

        elif islem_modu == "📈 Dükkan Ekstresi":
            st.subheader("📈 Dükkan Ekstresi & Tarih Bazlı Detaylı Döküm")
        
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                baslangic_tarihi_obj = st.date_input("Başlangıç Tarihi", datetime.now() - timedelta(days=30), key="ekstre_bas_tarih")
            with col_f2:
                bitis_tarihi_obj = st.date_input("Bitiş Tarihi", datetime.now(), key="ekstre_bit_tarih")
            
            str_bas = baslangic_tarihi_obj.strftime("%Y-%m-%d")
            str_bit = bitis_tarihi_obj.strftime("%Y-%m-%d")
        
            secilen_kategori = st.selectbox("Kategori Filtresi", ["Tümü", "Çiğ Köfte", "Midye", "İçecek", "Dükkan Gideri", "Personel", "Diğer"], key="ekstre_kat_filtre")
            ekstre_tipi = st.radio("Ekstre Görünüm Modu:", ["Detaylı Ekstre (Tüm İşlemler)", "Detaysız Ekstre (Kategori Toplamları)"], horizontal=True, key="ekstre_tipi_radio")
        
            query = "SELECT * FROM dukkan_hareket WHERE SUBSTR(tarih, 1, 10) >= ? AND SUBSTR(tarih, 1, 10) <= ?"
            params = [str_bas, str_bit]
        
            if secilen_kategori != "Tümü":
                query += " AND kategori LIKE ?"
                params.append(f"%{secilen_kategori}%")
            
            query += " ORDER BY tarih DESC"
            df_ekstre = run_query_df(query, params)
        
            st.markdown("### 📊 Seçilen Aralık Gelir / Gider Özeti")
            df_toplam_ozet = run_query_df("""
                SELECT islem_tipi, SUM(tutar) as toplam_tutar 
                FROM dukkan_hareket 
                WHERE SUBSTR(tarih, 1, 10) BETWEEN ? AND ? 
                GROUP BY islem_tipi
            """, [str_bas, str_bit])
        
            if not df_toplam_ozet.empty:
                st.dataframe(df_toplam_ozet, use_container_width=True, hide_index=True)
            else:
                st.info("Seçilen tarih aralığında işlem bulunmuyor.")
            
            st.markdown("---")
            st.subheader("👁️ Canlı Ekstre Ön İzlemesi")
        
            if not df_ekstre.empty:
                st.markdown('<div class="preview-box">', unsafe_allow_html=True)
                st.markdown(f"<h2 style='text-align: center; color: #000000;'>MİDYECİ ABLA - DÜKKAN EKSTRESİ</h2>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; color: #555;'>Tarih Aralığı: <b>{str_bas}</b> ile <b>{str_bit}</b> | Kategori: <b>{secilen_kategori}</b></p>", unsafe_allow_html=True)
                st.markdown("<hr>", unsafe_allow_html=True)
            
                if ekstre_tipi == "Detaylı Ekstre (Tüm İşlemler)":
                    st.write(f"Toplam İşlem Adedi: **{len(df_ekstre)}**")
                    st.dataframe(df_ekstre, use_container_width=True)
                    toplam_tutar = df_ekstre["tutar"].sum()
                    st.markdown(f"<h3 style='text-align: right; color: #000000;'>Genel Toplam Tutar: {toplam_tutar:,.2f} TL</h3>", unsafe_allow_html=True)
                else:
                    df_ozet = df_ekstre.groupby("kategori").agg(
                        İşlem_Adedi=("id", "count"),
                        Toplam_Miktar=("miktar", "sum"),
                        Toplam_Tutar=("tutar", "sum")
                    ).reset_index()
                    st.dataframe(df_ozet, use_container_width=True)
                    genel_toplam = df_ozet["Toplam_Tutar"].sum()
                    st.markdown(f"<h3 style='text-align: right; color: #000000;'>Özet Genel Toplam: {genel_toplam:,.2f} TL</h3>", unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Belirtilen kriterlerde ve tarih aralığında herhangi bir hareket bulunamadı.")

            # Profesyonel PDF — mevcut Dükkan ekstresi kayıtlarından üretilir.
            if not df_ekstre.empty:
                gelir_pdf = float(df_ekstre.loc[df_ekstre["islem_tipi"] == "Günlük Satış (Gelir)", "tutar"].sum())
                gider_pdf = float(df_ekstre.loc[df_ekstre["islem_tipi"] == "Dükkan Gideri (Gider)", "tutar"].sum())
                net_pdf = gelir_pdf - gider_pdf
                pdf_dukkan = build_dukkan_pdf(
                    df_ekstre, str_bas, str_bit, secilen_kategori,
                    net_pdf, gelir_pdf, gider_pdf
                )
                st.download_button(
                    "📥 Bu Dükkan Ekstresini Profesyonel PDF Olarak İndir",
                    data=pdf_dukkan,
                    file_name=f"dukkan_ekstresi_{str_bas}_{str_bit}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                    key="pdf_dukkan_ekstre_tab1"
                )

        elif islem_modu == "📊 Aylık Karşılaştırma":
            st.subheader("📊 İki Ayın Performans ve Ürün Kıyaslama Raporu")
        
            df_aylar = run_query_df("""
                SELECT DISTINCT SUBSTR(tarih, 1, 7) as yil_ay 
                FROM dukkan_hareket 
                WHERE islem_tipi = 'Günlük Satış (Gelir)' 
                ORDER BY yil_ay DESC
            """)
        
            mevcut_aylar = df_aylar['yil_ay'].tolist() if not df_aylar.empty else [datetime.now().strftime("%Y-%m")]
            
            col_sec1, col_sec2 = st.columns(2)
            with col_sec1:
                default_idx_1 = 1 if len(mevcut_aylar) > 1 else 0
                secilen_ay_1 = st.selectbox("1. Ayı Seçin (Sol Taraf):", mevcut_aylar, index=default_idx_1, key="ay_secim_1")
            with col_sec2:
                secilen_ay_2 = st.selectbox("2. Ayı Seçin (Sağ Taraf):", mevcut_aylar, index=0, key="ay_secim_2")
        
            df_ay1 = run_query_df("""
                SELECT SUM(tutar) as toplam_ciro,
                       SUM(CASE WHEN kategori = 'Midye' THEN miktar ELSE 0 END) as toplam_midye,
                       SUM(CASE WHEN kategori = 'Çiğ Köfte' THEN miktar ELSE 0 END) as toplam_cigkofte,
                       SUM(CASE WHEN kategori = 'İçecek' THEN miktar ELSE 0 END) as toplam_icecek
                FROM dukkan_hareket 
                WHERE islem_tipi = 'Günlük Satış (Gelir)' AND SUBSTR(tarih, 1, 7) = ?
            """, [secilen_ay_1])
        
            df_ay2 = run_query_df("""
                SELECT SUM(tutar) as toplam_ciro,
                       SUM(CASE WHEN kategori = 'Midye' THEN miktar ELSE 0 END) as toplam_midye,
                       SUM(CASE WHEN kategori = 'Çiğ Köfte' THEN miktar ELSE 0 END) as toplam_cigkofte,
                       SUM(CASE WHEN kategori = 'İçecek' THEN miktar ELSE 0 END) as toplam_icecek
                FROM dukkan_hareket 
                WHERE islem_tipi = 'Günlük Satış (Gelir)' AND SUBSTR(tarih, 1, 7) = ?
            """, [secilen_ay_2])
        
            ciro_1 = df_ay1.iloc[0]['toplam_ciro'] if not df_ay1.empty and df_ay1.iloc[0]['toplam_ciro'] is not None else 0.0
            ciro_2 = df_ay2.iloc[0]['toplam_ciro'] if not df_ay2.empty and df_ay2.iloc[0]['toplam_ciro'] is not None else 0.0
        
            ciro_degisim = ((ciro_2 - ciro_1) / ciro_1) * 100 if ciro_1 > 0 else (100.0 if ciro_2 > 0 else 0.0)

            st.markdown(f"### 🗓️ {secilen_ay_1} ➔ {secilen_ay_2} Performans Özeti")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"{secilen_ay_1} Ciro", f"{ciro_1:,.2f} TL")
            with col2:
                st.metric(f"{secilen_ay_2} Ciro", f"{ciro_2:,.2f} TL", delta=f"%{ciro_degisim:+.1f}")
            with col3:
                st.metric("Ciro Farkı", f"{(ciro_2 - ciro_1):+,.2f} TL")

        elif islem_modu == "📋 Tüm Kayıtları Yönet":
            st.subheader("📋 Dükkan Kayıtlarını Düzenle / Sil")
            df_dukkan_all = run_query_df("SELECT * FROM dukkan_hareket ORDER BY id DESC LIMIT 50")
        
            if df_dukkan_all.empty:
                st.info("Düzenlenecek kayıt bulunmuyor.")
            else:
                secilen_dukkan_id = st.selectbox(
                    "İşlem Yapılacak Kaydı Seçin:", 
                    options=df_dukkan_all["id"], 
                    format_func=lambda x: f"ID:{x} - {df_dukkan_all[df_dukkan_all['id']==x]['tarih'].values[0]} | {df_dukkan_all[df_dukkan_all['id']==x]['kategori'].values[0]} ({df_dukkan_all[df_dukkan_all['id']==x]['tutar'].values[0]} TL)",
                    key="yonet_secilen_id"
                )
            
                dukkan_kayit = df_dukkan_all[df_dukkan_all["id"] == secilen_dukkan_id].iloc[0]
                kategoriler = ["Midye", "Çiğ Köfte", "İçecek", "Dükkan Gideri", "Personel", "Diğer"]
            
                with st.form("dukkan_duzenle_form"):
                    e_islem_tipi = st.selectbox("İşlem Tipi", ["Günlük Satış (Gelir)", "Dükkan Gideri (Gider)"], index=0 if dukkan_kayit["islem_tipi"] == "Günlük Satış (Gelir)" else 1, key="yonet_islem_tipi")
                    e_tarih_val = datetime.strptime(str(dukkan_kayit["tarih"])[:10], "%Y-%m-%d") if pd.notnull(dukkan_kayit["tarih"]) else datetime.now()
                    e_tarih_input = st.date_input("Tarih", e_tarih_val, key="yonet_tarih")
                    e_kategori = st.selectbox("Kategori", kategoriler, index=kategoriler.index(dukkan_kayit["kategori"]) if dukkan_kayit["kategori"] in kategoriler else 0, key="yonet_kategori")
                    e_urun = st.text_input("Ürün / Detay Açıklaması", value=str(dukkan_kayit["urun_adi"]) if pd.notnull(dukkan_kayit["urun_adi"]) else "", key="yonet_urun")
                    e_miktar = st.number_input("Miktar / Adet", min_value=1, value=int(dukkan_kayit["miktar"]), step=1, key="yonet_miktar")
                    e_birim = st.number_input("Birim Fiyat (TL)", min_value=0.0, value=float(dukkan_kayit["birim_fiyat"]), step=0.5, format="%.2f", key="yonet_birim")
                
                    e_hesaplanan_tutar = e_miktar * e_birim
                    st.info(f"Güncellenecek Toplam Tutar: **{e_hesaplanan_tutar:,.2f} TL**")
                
                    d_guncelle = st.form_submit_button("✏️ Kaydı Güncelle", type="primary")
                    d_sil = st.form_submit_button("🗑️ Kaydı Sil")
                
                    if d_guncelle:
                        mevcut_saat = str(dukkan_kayit["tarih"])[11:] if len(str(dukkan_kayit["tarih"])) > 10 else datetime.now().strftime("%H:%M:%S")
                        yeni_tam_tarih = f"{e_tarih_input.strftime('%Y-%m-%d')} {mevcut_saat}"
                    
                        client.execute(
                            "UPDATE dukkan_hareket SET tarih=?, islem_tipi=?, kategori=?, urun_adi=?, miktar=?, birim_fiyat=?, tutar=? WHERE id=?",
                            [yeni_tam_tarih, e_islem_tipi, e_kategori, e_urun, e_miktar, e_birim, e_hesaplanan_tutar, int(secilen_dukkan_id)]
                        )
                        st.success("Kayıt başarıyla güncellendi!")
                        st.rerun()
                    
                    if d_sil:
                        client.execute("DELETE FROM dukkan_hareket WHERE id=?", [int(secilen_dukkan_id)])
                        st.warning("Kayıt silindi!")
                        st.rerun()

        elif islem_modu == "🗓️ İki Tarih Arası Ciro":
            st.subheader("🗓️ İki Tarih Arası Toptan ve Dükkan Detaylı Ciro Raporu")
        
            col_b, col_s = st.columns(2)
            with col_b:
                bas_tarih = st.date_input("Başlangıç Tarihi", datetime.now().replace(day=1), key="dukkan_ciro_bas")
            with col_s:
                bit_tarih = st.date_input("Bitiş Tarihi", datetime.now(), key="dukkan_ciro_bit")
            
            str_bas = bas_tarih.strftime("%Y-%m-%d")
            str_bit = bit_tarih.strftime("%Y-%m-%d")
        
            df_dukkan_satis = run_query_df("""
                SELECT 
                    CASE 
                        WHEN LOWER(kategori) LIKE '%midye%' OR LOWER(urun_adi) LIKE '%midye%' THEN 'Midye'
                        ELSE kategori 
                    END as kategori, 
                    SUM(miktar) as toplam_adet, 
                    SUM(tutar) as toplam_tutar
                FROM dukkan_hareket
                WHERE SUBSTR(tarih, 1, 10) BETWEEN ? AND ? AND islem_tipi = 'Günlük Satış (Gelir)'
                GROUP BY 
                    CASE 
                        WHEN LOWER(kategori) LIKE '%midye%' OR LOWER(urun_adi) LIKE '%midye%' THEN 'Midye'
                        ELSE kategori 
                    END
            """, [str_bas, str_bit])
        
            try:
                df_toptan_satis = run_query_df("""
                    SELECT firma_adi as kategori, SUM(adet) as toplam_adet, SUM(toplam_tutar) as toplam_tutar
                    FROM toptan_satis
                    WHERE SUBSTR(tarih, 1, 10) BETWEEN ? AND ? AND (islem_turu = 'Satış' OR islem_turu LIKE 'Satış%')
                    GROUP BY firma_adi
                """, [str_bas, str_bit])
            except:
                df_toptan_satis = pd.DataFrame(columns=['kategori', 'toplam_adet', 'toplam_tutar'])

            st.markdown("---")
            st.markdown("### 🏪 Dükkan Satışları")
            if df_dukkan_satis.empty:
                st.info("Seçilen tarih aralığında dükkan satış hareketi bulunamadı.")
                dukkan_toplam_ciro = 0.0
            else:
                dukkan_toplam_ciro = df_dukkan_satis['toplam_tutar'].sum()
                st.dataframe(df_dukkan_satis.rename(columns={'kategori': 'Kategori', 'toplam_adet': 'Toplam Adet', 'toplam_tutar': 'Toplam Tutar (TL)'}), use_container_width=True, hide_index=True)
                st.metric("📦 Dükkan Toplam Ciro", f"{dukkan_toplam_ciro:,.2f} TL")

            st.markdown("---")
            st.markdown("### 📦 Toptan Satışları")
            if df_toptan_satis.empty:
                st.info("Seçilen tarih aralığında toptan satış hareketi bulunamadı.")
                toptan_toplam_ciro = 0.0
            else:
                toptan_toplam_ciro = df_toptan_satis['toplam_tutar'].sum()
                st.dataframe(df_toptan_satis.rename(columns={'kategori': 'Firma Adı', 'toplam_adet': 'Toplam Adet', 'toplam_tutar': 'Toplam Tutar (TL)'}), use_container_width=True, hide_index=True)
                st.metric("💰 Toptan Toplam Ciro", f"{toptan_toplam_ciro:,.2f} TL")

            st.markdown("---")
            genel_toplam_ciro = dukkan_toplam_ciro + toptan_toplam_ciro
            st.success(f"🎯 **GENEL TOPLAM CİRO ({str_bas} ➔ {str_bit}): {genel_toplam_ciro:,.2f} TL**")

        st.divider()
        bugun_str = datetime.now().strftime("%Y-%m-%d")
    
        df_dukkan_bugun = run_query_df("""
            SELECT SUM(miktar) as adet, SUM(tutar) as ciro 
            FROM dukkan_hareket 
            WHERE SUBSTR(tarih, 1, 10) = ? AND kategori = 'Midye' AND islem_tipi = 'Günlük Satış (Gelir)'
        """, [bugun_str])
    
        d_adet = df_dukkan_bugun['adet'].iloc[0] if not df_dukkan_bugun.empty and pd.notnull(df_dukkan_bugun['adet'].iloc[0]) else 0
        d_ciro = df_dukkan_bugun['ciro'].iloc[0] if not df_dukkan_bugun.empty and pd.notnull(df_dukkan_bugun['ciro'].iloc[0]) else 0.0
    
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Bugün Dükkan Midye", f"{int(d_adet):,} adet")
        with col2:
            st.metric("Bugün Dükkan Ciro", f"{d_ciro:,.2f} TL")
    
        st.write("**Son Dükkan Kayıtları**")
        df_dukkan_view = run_query_df("SELECT tarih as 'Tarih', kategori as 'Kategori', miktar as 'Adet', tutar as 'Tutar' FROM dukkan_hareket ORDER BY id DESC LIMIT 10")
        st.dataframe(df_dukkan_view, use_container_width=True)
    
    # ==========================================
    # 2. SEKME: TOPTAN (DÜZENLİ ALT SEKME YAPISI)
    # ==========================================

if st.session_state.aktif_sayfa == "TOPTAN":
    top1, top2 = st.columns([1, 6])
    with top1:
        if st.button("⬅️ Geri", key="geri_toptan", use_container_width=True):
            ana_menuye_don()
    with top2:
        st.markdown('<div class="module-path">🦪 MİDYECİ ABLA  /  TOPTAN</div>', unsafe_allow_html=True)

        st.caption("Toptan satış, tahsilat, firma bazlı işlemler ve kayıt yönetimi.")
        df_firmalar_opt = run_query_df("SELECT firma_adi FROM firmalar ORDER BY firma_adi ASC")
        firma_listesi = df_firmalar_opt["firma_adi"].tolist() if not df_firmalar_opt.empty else []

        if not firma_listesi:
            st.warning("⚠️ Lütfen önce 'Firmalar' sekmesinden bir firma ekleyin!")
        else:
            # ANA DAĞINIKLIĞI BİTİREN ALT SEKMELER
            alt_sekme1, alt_sekme2, alt_sekme3 = st.tabs([
                "➕ Yeni İşlem",
                "📅 Tarihe Göre İşlemler",
                "⚙️ Tüm Kayıtlar & Yönetim"
            ])

            # ---------------------------------------------------------
            # 1. ALT SEKME: YENİ İŞLEM (Satış / Tahsilat Girişi)
            # ---------------------------------------------------------
            with alt_sekme1:
                st.subheader("Yeni Toptan İşlem Girişi")
                islem_turu = st.selectbox("İşlem Tipi", ["Satış (Borç Ekle)", "Tahsilat (Borç Düş/Alacak)"], key="toptan_islem_tipi_select_yeni")

                secili_firma_toptan = st.selectbox("Firma Seçin", firma_listesi, key="toptan_firma_secim_yeni")
            
                if secili_firma_toptan:
                    df_f_s = run_query_df("SELECT SUM(toplam_tutar) as t FROM toptan_satis WHERE firma_adi=? AND islem_turu='Satış'", [secili_firma_toptan])
                    df_f_t = run_query_df("SELECT SUM(toplam_tutar) as t FROM toptan_satis WHERE firma_adi=? AND islem_turu='Tahsilat'", [secili_firma_toptan])
                    f_s = df_f_s['t'].iloc[0] if not df_f_s.empty and pd.notnull(df_f_s['t'].iloc[0]) else 0.0
                    f_t = df_f_t['t'].iloc[0] if not df_f_t.empty and pd.notnull(df_f_t['t'].iloc[0]) else 0.0
                    f_bakiye = f_s - f_t
                
                    if f_bakiye > 0:
                        st.error(f"📌 **{secili_firma_toptan}** Güncel Durumu: **{f_bakiye:,.2f} TL BORÇLU**")
                    elif f_bakiye < 0:
                        st.success(f"📌 **{secili_firma_toptan}** Güncel Durumu: **{abs(f_bakiye):,.2f} TL ALACAKLI (Fazla Ödeme)**")
                    else:
                        st.info(f"📌 **{secili_firma_toptan}** Güncel Durumu: **0.00 TL (Hesap Kapalı / Borcu Yok)**")

                with st.form("toptan_form_duzenli", clear_on_submit=True):
                    tarih = st.date_input("İşlem Tarihi", datetime.now())
                
                    if islem_turu == "Satış (Borç Ekle)":
                        adet = st.number_input("Satılan Adet", min_value=1, step=50, value=100)
                        birim_fiyat = st.number_input("Birim Fiyat (TL)", min_value=0.0, step=0.5, value=15.0, format="%.2f")
                        toplam_tutar = adet * birim_fiyat
                        st.info(f"Hesaplanan Tutar: **{toplam_tutar:,.2f} TL**")
                    else:
                        adet = 0
                        birim_fiyat = 0.0
                        toplam_tutar = st.number_input("Tahsil Edilen Tutar (TL)", min_value=0.0, step=50.0, value=2430.0, format="%.2f")
                        st.success(f"Tahsilat Tutarı: **{toplam_tutar:,.2f} TL**")

                    aciklama = st.text_input("Açıklama / Not")
                
                    kaydet = st.form_submit_button("💾 İşlemi Kaydet", type="primary")
                    if kaydet:
                        t_tur = "Satış" if islem_turu == "Satış (Borç Ekle)" else "Tahsilat"
                        client.execute("""
                            INSERT INTO toptan_satis (firma_adi, tarih, islem_turu, adet, birim_fiyat, toplam_tutar, aciklama)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, [secili_firma_toptan, tarih.strftime("%Y-%m-%d"), t_tur, adet, birim_fiyat, toplam_tutar, aciklama])
                        st.success(f"{t_tur} başarıyla kaydedildi!")
                        st.rerun()

            # ---------------------------------------------------------
            # 2. ALT SEKME: TARİHE GÖRE İŞLEMLER (Süzme, Düzenleme, Silme)
            # ---------------------------------------------------------
            with alt_sekme2:
                st.subheader("📅 Tarih Bazlı Arama ve Günlük Yönetim")
            
                col_t1, col_t2 = st.columns([1, 1])
                with col_t1:
                    secilen_tarih = st.date_input("Sorgulanacak Tarih Seçin:", datetime.now(), key="toptan_tarih_sorgu_temiz")
                with col_t2:
                    islem_filtresi = st.radio("İşlem Filtresi", ["🔄 Tümü", "📦 Sadece Satışlar", "💰 Sadece Tahsilatlar"], key="toptan_islem_filtresi_temiz", horizontal=True)
                
                str_tarih = secilen_tarih.strftime("%Y-%m-%d")
            
                if islem_filtresi == "📦 Sadece Satışlar":
                    df_toptan_gun = run_query_df("SELECT id, firma_adi, tarih, islem_turu, adet, birim_fiyat, toplam_tutar, aciklama FROM toptan_satis WHERE tarih=? AND islem_turu='Satış' ORDER BY id DESC", [str_tarih])
                elif islem_filtresi == "💰 Sadece Tahsilatlar":
                    df_toptan_gun = run_query_df("SELECT id, firma_adi, tarih, islem_turu, adet, birim_fiyat, toplam_tutar, aciklama FROM toptan_satis WHERE tarih=? AND islem_turu='Tahsilat' ORDER BY id DESC", [str_tarih])
                else:
                    df_toptan_gun = run_query_df("SELECT id, firma_adi, tarih, islem_turu, adet, birim_fiyat, toplam_tutar, aciklama FROM toptan_satis WHERE tarih=? ORDER BY id DESC", [str_tarih])
            
                if df_toptan_gun.empty:
                    st.warning(f"🔍 {str_tarih} tarihinde seçilen filtreye uygun işlem kaydı bulunamadı.")
                else:
                    st.success(f"📌 {str_tarih} Tarihindeki Kayıtlar ({len(df_toptan_gun)} Adet)")
                    st.dataframe(df_toptan_gun[['firma_adi', 'islem_turu', 'adet', 'toplam_tutar', 'aciklama']], use_container_width=True)
                
                    toplam_adet_gun = df_toptan_gun['adet'].sum()
                    toplam_tutar_gun = df_toptan_gun['toplam_tutar'].sum()
                
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        st.metric("İşlem Adedi", f"{len(df_toptan_gun)} Adet")
                    with col_m2:
                        st.metric("Toplam Ürün", f"{toplam_adet_gun:,} Adet")
                    with col_m3:
                        st.metric("Toplam Tutar", f"{toplam_tutar_gun:,.2f} TL")
                
                    st.divider()
                    st.write("**Seçilen Günkü Kaydı Düzenle / Sil**")
                    secilen_id_gun = st.selectbox(
                        "İşlem Seçin:", 
                        options=df_toptan_gun["id"], 
                        format_func=lambda x: f"ID:{x} - {df_toptan_gun[df_toptan_gun['id']==x]['firma_adi'].values[0]} ({df_toptan_gun[df_toptan_gun['id']==x]['islem_turu'].values[0]} - {df_toptan_gun[df_toptan_gun['id']==x]['toplam_tutar'].values[0]} TL)",
                        key="sec_id_gunluk"
                    )
                
                    kayit_gun = df_toptan_gun[df_toptan_gun["id"] == secilen_id_gun].iloc[0]
                
                    with st.form("toptan_gun_duzenle_form_temiz"):
                        e_tur = st.selectbox("İşlem Türü", ["Satış", "Tahsilat"], index=0 if kayit_gun["islem_turu"] == "Satış" else 1)
                        e_firma = st.selectbox("Firma Seçin", firma_listesi, index=firma_listesi.index(kayit_gun["firma_adi"]) if kayit_gun["firma_adi"] in firma_listesi else 0, key="efirma_gun")
                        e_tarih = st.date_input("Tarih", datetime.strptime(str(kayit_gun["tarih"]), "%Y-%m-%d"), key="etarih_gun")
                    
                        if e_tur == "Satış":
                            e_adet = st.number_input("Adet", min_value=0, step=50, value=int(kayit_gun["adet"]), key="eadet_gun")
                            e_birim_fiyat = st.number_input("Birim Fiyat (TL)", min_value=0.0, step=0.5, value=float(kayit_gun["birim_fiyat"]), format="%.2f", key="ebirim_gun")
                            e_toplam = e_adet * e_birim_fiyat
                        else:
                            e_adet = 0
                            e_birim_fiyat = 0.0
                            e_toplam = st.number_input("Tahsil Edilen Tutar (TL)", min_value=0.0, step=50.0, value=float(kayit_gun["toplam_tutar"]), format="%.2f", key="etahsilat_gun")

                        st.info(f"Güncel Tutar: **{e_toplam:,.2f} TL**")
                        e_aciklama = st.text_input("Açıklama", value=str(kayit_gun["aciklama"]) if kayit_gun["aciklama"] else "", key="eaciklama_gun")
                    
                        guncelle_g = st.form_submit_button("✏️ Güncelle", type="primary")
                        sil_g = st.form_submit_button("🗑️ Sil")
                    
                        if guncelle_g:
                            client.execute("""
                                UPDATE toptan_satis 
                                SET firma_adi=?, tarih=?, islem_turu=?, adet=?, birim_fiyat=?, toplam_tutar=?, aciklama=? 
                                WHERE id=?
                            """, [e_firma, e_tarih.strftime("%Y-%m-%d"), e_tur, e_adet, e_birim_fiyat, e_toplam, e_aciklama, int(secilen_id_gun)])
                            st.success("Kayıt güncellendi!")
                            st.rerun()
                        
                        if sil_g:
                            client.execute("DELETE FROM toptan_satis WHERE id=?", [int(secilen_id_gun)])
                            st.warning("Kayıt silindi!")
                            st.rerun()

            # ---------------------------------------------------------
            # 4. ALT SEKME: TÜM KAYITLAR & GENEL YÖNETİM
            # ---------------------------------------------------------
            with alt_sekme3:
                st.subheader("⚙️ Tüm Toptan Kayıtları Arşivi ve Düzenleme")
                df_toptan_all = run_query_df("SELECT id, firma_adi, tarih, islem_turu, adet, birim_fiyat, toplam_tutar, aciklama FROM toptan_satis ORDER BY id DESC")
            
                if not df_toptan_all.empty:
                    secilen_id_tum = st.selectbox(
                        "Arşivden Kayıt Seçin:", 
                        options=df_toptan_all["id"], 
                        format_func=lambda x: f"ID:{x} - {df_toptan_all[df_toptan_all['id']==x]['tarih'].values[0]} - {df_toptan_all[df_toptan_all['id']==x]['firma_adi'].values[0]} ({df_toptan_all[df_toptan_all['id']==x]['toplam_tutar'].values[0]} TL)",
                        key="sec_id_tum_arsiv"
                    )
                
                    kayit_tum = df_toptan_all[df_toptan_all["id"] == secilen_id_tum].iloc[0]
                
                    with st.form("toptan_duzenle_form_arsiv"):
                        e_tur = st.selectbox("İşlem Türü", ["Satış", "Tahsilat"], index=0 if kayit_tum["islem_turu"] == "Satış" else 1, key="etur_arsiv")
                        e_firma = st.selectbox("Firma Seçin", firma_listesi, index=firma_listesi.index(kayit_tum["firma_adi"]) if kayit_tum["firma_adi"] in firma_listesi else 0, key="efirma_arsiv")
                        e_tarih = st.date_input("Tarih", datetime.strptime(str(kayit_tum["tarih"]), "%Y-%m-%d"), key="etarih_arsiv")
                    
                        if e_tur == "Satış":
                            e_adet = st.number_input("Adet", min_value=0, step=50, value=int(kayit_tum["adet"]), key="eadet_arsiv")
                            e_birim_fiyat = st.number_input("Birim Fiyat (TL)", min_value=0.0, step=0.5, value=float(kayit_tum["birim_fiyat"]), format="%.2f", key="ebirim_arsiv")
                            e_toplam = e_adet * e_birim_fiyat
                        else:
                            e_adet = 0
                            e_birim_fiyat = 0.0
                            e_toplam = st.number_input("Tahsil Edilen Tutar (TL)", min_value=0.0, step=50.0, value=float(kayit_tum["toplam_tutar"]), format="%.2f", key="etahsilat_arsiv")

                        st.info(f"Tutar: **{e_toplam:,.2f} TL**")
                        e_aciklama = st.text_input("Açıklama", value=str(kayit_tum["aciklama"]) if kayit_tum["aciklama"] else "", key="eaciklama_arsiv")
                    
                        guncelle_a = st.form_submit_button("✏️ Güncelle", type="primary")
                        sil_a = st.form_submit_button("🗑️ Sil")
                    
                        if guncelle_a:
                            client.execute("""
                                UPDATE toptan_satis 
                                SET firma_adi=?, tarih=?, islem_turu=?, adet=?, birim_fiyat=?, toplam_tutar=?, aciklama=? 
                                WHERE id=?
                            """, [e_firma, e_tarih.strftime("%Y-%m-%d"), e_tur, e_adet, e_birim_fiyat, e_toplam, e_aciklama, int(secilen_id_tum)])
                            st.success("Kayıt güncellendi!")
                            st.rerun()
                        
                        if sil_a:
                            client.execute("DELETE FROM toptan_satis WHERE id=?", [int(secilen_id_tum)])
                            st.warning("Kayıt silindi!")
                            st.rerun()

                st.divider()
                st.write("**Son 10 İşlem Genel Listesi**")
                df_toptan_view = run_query_df("SELECT firma_adi as 'Firma', tarih as 'Tarih', islem_turu as 'İşlem', toplam_tutar as 'Tutar' FROM toptan_satis ORDER BY id DESC LIMIT 10")
                st.dataframe(df_toptan_view, use_container_width=True)
    # ==========================================
    # 3. SEKME: FİRMA YÖNETİMİ
    # ==========================================

if st.session_state.aktif_sayfa == "FIRMALAR":
    top1, top2 = st.columns([1, 6])
    with top1:
        if st.button("⬅️ Geri", key="geri_firmalar", use_container_width=True):
            ana_menuye_don()
    with top2:
        st.markdown('<div class="module-path">🦪 MİDYECİ ABLA  /  FIRMALAR</div>', unsafe_allow_html=True)

        st.subheader("🏢 Firma Yönetimi")
        st.caption("Firma kartları, telefon bilgileri, açıklamalar ve cari hesap bağlantısı.")
        st.caption("Toptan satış ve cari hesaplarda kullanılacak firmaları buradan yönetin.")

        f_islem = st.radio(
            "İşlem Seçin:",
            ["➕ Yeni Firma Ekle", "✏️ Firma Düzenle / Sil"],
            horizontal=True,
            key="firma_yonetim_modu"
        )

        if f_islem == "➕ Yeni Firma Ekle":
            with st.form("yeni_firma_form_prof", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    yeni_f_adi = st.text_input("Firma Ünvanı / Adı *", key="firma_yeni_adi_prof")
                    yeni_f_tel = st.text_input("Telefon No", key="firma_yeni_tel_prof")
                with c2:
                    yeni_f_not = st.text_area("Açıklama / Not", key="firma_yeni_not_prof", height=95)

                f_kaydet = st.form_submit_button("➕ Firmayı Kaydet", type="primary", use_container_width=True)

                if f_kaydet:
                    firma_adi_temiz = yeni_f_adi.strip()
                    if not firma_adi_temiz:
                        st.error("⚠️ Firma adı boş bırakılamaz.")
                    else:
                        try:
                            client.execute(
                                "INSERT INTO firmalar (firma_adi, telefon, aciklama) VALUES (?, ?, ?)",
                                [firma_adi_temiz, yeni_f_tel.strip(), yeni_f_not.strip()]
                            )
                            st.success("✅ Firma başarıyla eklendi.")
                            st.rerun()
                        except Exception as e:
                            st.error("❌ Firma eklenemedi. Aynı isimde firma varsa önce onu kontrol edin.")
                            st.code(str(e))
        else:
            df_firma_yonet = run_query_df("SELECT id, firma_adi, telefon, aciklama FROM firmalar ORDER BY firma_adi ASC")
            if df_firma_yonet.empty:
                st.info("📭 Henüz kayıtlı firma bulunmuyor.")
            else:
                secili_f_id = st.selectbox(
                    "Düzenlenecek firmayı seçin:",
                    df_firma_yonet["id"].tolist(),
                    format_func=lambda x: df_firma_yonet.loc[df_firma_yonet["id"] == x, "firma_adi"].iloc[0],
                    key="firma_duzenle_sec_prof"
                )
                f_kayit = df_firma_yonet[df_firma_yonet["id"] == secili_f_id].iloc[0]

                with st.form("firma_duzenle_form_prof"):
                    e_adi = st.text_input("Firma Ünvanı / Adı", value=str(f_kayit["firma_adi"] or ""), key="firma_duzenle_adi_prof")
                    e_tel = st.text_input("Telefon", value=str(f_kayit["telefon"] or ""), key="firma_duzenle_tel_prof")
                    e_not = st.text_area("Açıklama / Not", value=str(f_kayit["aciklama"] or ""), key="firma_duzenle_not_prof", height=90)
                    c1, c2 = st.columns(2)
                    with c1:
                        guncelle = st.form_submit_button("✏️ Güncelle", type="primary", use_container_width=True)
                    with c2:
                        sil = st.form_submit_button("🗑️ Firmayı Sil", use_container_width=True)

                    if guncelle:
                        yeni_adi = e_adi.strip()
                        if not yeni_adi:
                            st.error("⚠️ Firma adı boş bırakılamaz.")
                        else:
                            try:
                                client.execute(
                                    "UPDATE firmalar SET firma_adi=?, telefon=?, aciklama=? WHERE id=?",
                                    [yeni_adi, e_tel.strip(), e_not.strip(), int(secili_f_id)]
                                )
                                st.success("✅ Firma güncellendi.")
                                st.rerun()
                            except Exception as e:
                                st.error("❌ Firma güncellenemedi.")
                                st.code(str(e))

                    if sil:
                        st.warning("Bu firmayı silmek, eski toptan hareketlerini silmez; sadece firma listesinden kaldırır.")
                        try:
                            client.execute("DELETE FROM firmalar WHERE id=?", [int(secili_f_id)])
                            st.success("🗑️ Firma silindi.")
                            st.rerun()
                        except Exception as e:
                            st.error("❌ Firma silinemedi.")
                            st.code(str(e))

        st.divider()
        st.markdown("### 📋 Kayıtlı Firmalar")
        df_f_list = run_query_df("""
            SELECT id AS 'ID', firma_adi AS 'Firma Adı', telefon AS 'Telefon', aciklama AS 'Açıklama'
            FROM firmalar ORDER BY firma_adi ASC
        """)
        if df_f_list.empty:
            st.info("Henüz kayıtlı firma bulunmuyor.")
        else:
            st.dataframe(df_f_list, use_container_width=True, hide_index=True)


    # ==========================================
    # 4. SEKME: PROFESYONEL CARİ EKSTRE / RAPOR MERKEZİ
    # ==========================================

if st.session_state.aktif_sayfa == "EKSTRE":
    top1, top2 = st.columns([1, 6])
    with top1:
        if st.button("⬅️ Geri", key="geri_ekstre", use_container_width=True):
            ana_menuye_don()
    with top2:
        st.markdown('<div class="module-path">🦪 MİDYECİ ABLA  /  EKSTRE</div>', unsafe_allow_html=True)

        st.subheader("📊 Profesyonel Ekstre & Rapor Merkezi")
        st.caption("Dükkan gelir-gider raporlarını ve firma bazlı toptan cari ekstrelerini tek merkezden hazırlayın.")

        rapor_tab1, rapor_tab2 = st.tabs(["🏪 Dükkan Ekstresi", "🚚 Toptan Cari Ekstresi"])

        # ---------------------------------------------------------
        # DÜKKAN EKSTRESİ
        # ---------------------------------------------------------
        with rapor_tab1:
            st.markdown("### 🏪 Dükkan Gelir / Gider Ekstresi")
            c1, c2, c3 = st.columns([1, 1, 1.4])
            with c1:
                rapor_bas = st.date_input("Başlangıç", datetime.now() - timedelta(days=30), key="rapor_dukkan_bas")
            with c2:
                rapor_bit = st.date_input("Bitiş", datetime.now(), key="rapor_dukkan_bit")
            with c3:
                rapor_kat = st.selectbox(
                    "Kategori",
                    ["Tümü", "Midye", "Çiğ Köfte", "İçecek", "Dükkan Gideri", "Personel", "Diğer"],
                    key="rapor_dukkan_kat"
                )

            if rapor_bas > rapor_bit:
                st.error("⚠️ Başlangıç tarihi bitiş tarihinden büyük olamaz.")
            else:
                rb = rapor_bas.strftime("%Y-%m-%d")
                re_ = rapor_bit.strftime("%Y-%m-%d")
                q = """
                    SELECT id, tarih, islem_tipi, kategori, urun_adi, miktar, birim_fiyat, tutar
                    FROM dukkan_hareket
                    WHERE SUBSTR(tarih,1,10) BETWEEN ? AND ?
                """
                p = [rb, re_]
                if rapor_kat != "Tümü":
                    q += " AND kategori = ?"
                    p.append(rapor_kat)
                q += " ORDER BY SUBSTR(tarih,1,10) ASC, id ASC"
                df_rduk = run_query_df(q, p)

                gelir = _num(df_rduk.loc[df_rduk["islem_tipi"] == "Günlük Satış (Gelir)", "tutar"].sum()) if not df_rduk.empty else 0.0
                gider = _num(df_rduk.loc[df_rduk["islem_tipi"] == "Dükkan Gideri (Gider)", "tutar"].sum()) if not df_rduk.empty else 0.0
                net = gelir - gider

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("💵 Gelir", _money(gelir))
                m2.metric("💸 Gider", _money(gider))
                m3.metric("📈 Net", _money(net))
                m4.metric("🧾 İşlem", f"{len(df_rduk):,}")

                if not df_rduk.empty:
                    st.markdown("#### 📅 Günlük Özet")
                    df_gun = run_query_df("""
                        SELECT SUBSTR(tarih,1,10) AS 'Tarih',
                               SUM(CASE WHEN islem_tipi='Günlük Satış (Gelir)' THEN tutar ELSE 0 END) AS 'Gelir',
                               SUM(CASE WHEN islem_tipi='Dükkan Gideri (Gider)' THEN tutar ELSE 0 END) AS 'Gider'
                        FROM dukkan_hareket
                        WHERE SUBSTR(tarih,1,10) BETWEEN ? AND ?
                        GROUP BY SUBSTR(tarih,1,10)
                        ORDER BY SUBSTR(tarih,1,10) ASC
                    """, [rb, re_])
                    if not df_gun.empty:
                        df_gun["Net"] = df_gun["Gelir"].fillna(0) - df_gun["Gider"].fillna(0)
                        for col in ["Gelir", "Gider", "Net"]:
                            df_gun[col] = df_gun[col].map(lambda x: f"{_num(x):,.2f} TL")
                        st.dataframe(df_gun, use_container_width=True, hide_index=True)

                    st.markdown("#### 📄 Hareket Dökümü")
                    df_goster = df_rduk.copy()
                    df_goster.columns = ["ID", "Tarih", "İşlem", "Kategori", "Ürün / Açıklama", "Adet", "Birim Fiyat", "Tutar"]
                    st.dataframe(df_goster, use_container_width=True, hide_index=True)

                    st.markdown("#### 📊 Kategori Özeti")
                    df_kat = run_query_df("""
                        SELECT kategori AS 'Kategori',
                               COUNT(*) AS 'İşlem',
                               SUM(miktar) AS 'Toplam Adet',
                               SUM(tutar) AS 'Toplam Tutar'
                        FROM dukkan_hareket
                        WHERE SUBSTR(tarih,1,10) BETWEEN ? AND ?
                        GROUP BY kategori
                        ORDER BY SUM(tutar) DESC
                    """, [rb, re_])
                    if not df_kat.empty:
                        st.dataframe(df_kat, use_container_width=True, hide_index=True)

                    pdf_bytes = build_dukkan_pdf(df_rduk, rb, re_, rapor_kat, net, gelir, gider)
                    st.download_button(
                        "📥 Dükkan Ekstresini PDF İndir",
                        data=pdf_bytes,
                        file_name=f"dukkan_ekstre_{rb}_{re_}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True,
                        key="pdf_dukkan_prof"
                    )
                else:
                    st.info("🔍 Seçilen tarih ve kategori kriterlerinde kayıt bulunamadı.")

        # ---------------------------------------------------------
        # TOPTAN CARİ EKSTRESİ
        # ---------------------------------------------------------
        with rapor_tab2:
            st.markdown("### 🚚 Firma Bazlı Toptan Cari Ekstresi")
            df_rf = run_query_df("SELECT firma_adi FROM firmalar ORDER BY firma_adi ASC")

            if df_rf.empty:
                st.warning("⚠️ Önce 'Firmalar' sekmesinden en az bir firma ekleyin.")
            else:
                firmalar_rapor = df_rf["firma_adi"].tolist()
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1.3])
                with c1:
                    rfirma = st.selectbox("Firma", firmalar_rapor, key="prof_toptan_firma")
                with c2:
                    rbas = st.date_input("Başlangıç", datetime.now().replace(day=1), key="prof_toptan_bas")
                with c3:
                    rbit = st.date_input("Bitiş", datetime.now(), key="prof_toptan_bit")
                with c4:
                    rturu = st.radio("Görünüm", ["Detaylı", "Özet"], horizontal=True, key="prof_toptan_gorunum")

                if rbas > rbit:
                    st.error("⚠️ Başlangıç tarihi bitiş tarihinden büyük olamaz.")
                else:
                    rb2 = rbas.strftime("%Y-%m-%d")
                    re2 = rbit.strftime("%Y-%m-%d")
                    df_rt = run_query_df("""
                        SELECT id, tarih, islem_turu, adet, birim_fiyat, toplam_tutar, aciklama
                        FROM toptan_satis
                        WHERE firma_adi = ?
                          AND SUBSTR(tarih,1,10) BETWEEN ? AND ?
                        ORDER BY SUBSTR(tarih,1,10) ASC, id ASC
                    """, [rfirma, rb2, re2])

                    df_dev = run_query_df("""
                        SELECT COALESCE(SUM(CASE WHEN islem_turu='Satış' THEN toplam_tutar ELSE -toplam_tutar END),0) AS devir
                        FROM toptan_satis
                        WHERE firma_adi=? AND SUBSTR(tarih,1,10) < ?
                    """, [rfirma, rb2])
                    devir = _num(df_dev["devir"].iloc[0]) if not df_dev.empty else 0.0
                    satis = _num(df_rt.loc[df_rt["islem_turu"] == "Satış", "toplam_tutar"].sum()) if not df_rt.empty else 0.0
                    tahsilat = _num(df_rt.loc[df_rt["islem_turu"] == "Tahsilat", "toplam_tutar"].sum()) if not df_rt.empty else 0.0
                    bakiye = devir + satis - tahsilat

                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("↩️ Devir", _money(devir))
                    m2.metric("🧾 Dönem Satış", _money(satis))
                    m3.metric("💵 Tahsilat", _money(tahsilat))
                    m4.metric("📌 Kapanış Bakiyesi", _money(bakiye))

                    if not df_rt.empty:
                        st.markdown("#### 📒 Cari Hareketler")
                        if rturu == "Detaylı":
                            df_cari = df_rt.copy()
                            running = devir
                            bakiye_list = []
                            for _, rr in df_cari.iterrows():
                                tut = _num(rr["toplam_tutar"])
                                running += tut if rr["islem_turu"] == "Satış" else -tut
                                bakiye_list.append(running)
                            df_cari["bakiye"] = bakiye_list
                            df_cari = df_cari[["tarih", "islem_turu", "adet", "birim_fiyat", "toplam_tutar", "bakiye", "aciklama"]]
                            df_cari.columns = ["Tarih", "İşlem", "Adet", "Birim Fiyat", "Tutar", "Bakiye", "Açıklama"]
                        else:
                            df_cari = pd.DataFrame({
                                "İşlem": ["Devir", "Dönem Satış", "Tahsilat", "Kapanış Bakiyesi"],
                                "Tutar (TL)": [devir, satis, tahsilat, bakiye]
                            })
                        st.dataframe(df_cari, use_container_width=True, hide_index=True)

                        st.markdown("#### 📅 Aylık Hareket Özeti")
                        df_ay_t = run_query_df("""
                            SELECT SUBSTR(tarih,1,7) AS 'Ay',
                                   SUM(CASE WHEN islem_turu='Satış' THEN toplam_tutar ELSE 0 END) AS 'Satış',
                                   SUM(CASE WHEN islem_turu='Tahsilat' THEN toplam_tutar ELSE 0 END) AS 'Tahsilat'
                            FROM toptan_satis
                            WHERE firma_adi=? AND SUBSTR(tarih,1,10) BETWEEN ? AND ?
                            GROUP BY SUBSTR(tarih,1,7)
                            ORDER BY SUBSTR(tarih,1,7) ASC
                        """, [rfirma, rb2, re2])
                        if not df_ay_t.empty:
                            df_ay_t["Net Hareket"] = df_ay_t["Satış"].fillna(0) - df_ay_t["Tahsilat"].fillna(0)
                            st.dataframe(df_ay_t, use_container_width=True, hide_index=True)

                        pdf_bytes = build_toptan_pdf(df_rt, rfirma, rb2, re2, devir, satis, tahsilat, bakiye)
                        st.download_button(
                            "📥 Firma Cari Ekstresini PDF İndir",
                            data=pdf_bytes,
                            file_name=f"cari_ekstre_{rfirma}_{rb2}_{re2}.pdf".replace(" ", "_"),
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True,
                            key="pdf_toptan_prof"
                        )
                    else:
                        st.info("🔍 Seçilen firma ve tarih aralığında hareket bulunamadı.")


    # ==========================================
    # 5. SEKME: TÜM BORÇ / ALACAK ÖZETİ (YENİ SEKME)
    # ==========================================

if st.session_state.aktif_sayfa == "BORC":
    top1, top2 = st.columns([1, 6])
    with top1:
        if st.button("⬅️ Geri", key="geri_borc", use_container_width=True):
            ana_menuye_don()
    with top2:
        st.markdown('<div class="module-path">🦪 MİDYECİ ABLA  /  BORC</div>', unsafe_allow_html=True)

        st.subheader("💰 Tüm Firmaların Borç / Alacak Listesi")
        st.caption("Firmaların güncel satış, tahsilat ve bakiye durumunu toplu olarak izleyin.")
        st.write("Sistemde kayıtlı bütün firmaların borç ve alacak durumlarını toplu olarak görüntüleyin.")
    
        # BUTON İLE BORÇLU/ALACAKLI LİSTESİ GETİRME
        if st.button("📊 Tüm Firmaların Borç/Alacak Listesini Getir", type="primary"):
            df_f_all = run_query_df("SELECT firma_adi FROM firmalar ORDER BY firma_adi ASC")
        
            if df_f_all.empty:
                st.warning("Henüz kayıtlı firma bulunmuyor.")
            else:
                ozet_veri = []
                toplam_piyasa_borcu = 0.0
            
                for f_adi in df_f_all["firma_adi"]:
                    s_res = run_query_df("SELECT SUM(toplam_tutar) as t FROM toptan_satis WHERE firma_adi=? AND islem_turu='Satış'", [f_adi])
                    t_res = run_query_df("SELECT SUM(toplam_tutar) as t FROM toptan_satis WHERE firma_adi=? AND islem_turu='Tahsilat'", [f_adi])
                
                    satis_t = s_res['t'].iloc[0] if not s_res.empty and pd.notnull(s_res['t'].iloc[0]) else 0.0
                    tahsilat_t = t_res['t'].iloc[0] if not t_res.empty and pd.notnull(t_res['t'].iloc[0]) else 0.0
                    bakiye = satis_t - tahsilat_t
                
                    if bakiye > 0:
                        durum = "🔴 BORÇLU"
                        toplam_piyasa_borcu += bakiye
                    elif bakiye < 0:
                        durum = "🟢 ALACAKLI (Fazla Ödeme)"
                    else:
                        durum = "⚪ HESAP KAPALI (0.00 TL)"
                    
                    ozet_veri.append({
                        "Firma Ünvanı": f_adi,
                        "Toplam Satış (TL)": f"{satis_t:,.2f}",
                        "Toplam Tahsilat (TL)": f"{tahsilat_t:,.2f}",
                        "Net Bakiye (TL)": f"{abs(bakiye):,.2f}",
                        "Durum": durum
                    })
            
                df_ozet = pd.DataFrame(ozet_veri)
            
                st.success(f"📌 **Toplam Piyasa Alacağınız:** {toplam_piyasa_borcu:,.2f} TL")
                st.dataframe(df_ozet, use_container_width=True)
