import streamlit as st
import pandas as pd
from datetime import datetime
import libsql_client as libsql
import base64
from datetime import datetime, timedelta

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

# Sekmeler (5 Sekmeli Yapı)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏪 Dükkan", "🚚 Toptan", "🏢 Firmalar", "📊 Cari Ekstre", "💰 Borç/Alacak"])

bugun = datetime.now().strftime("%Y-%m-%d")

# ==========================================
# 1. SEKME: DÜKKAN (GÜNCELLENMİŞ FORM STATE)
# ==========================================
with tab1:
    st.subheader("🏪 Dükkan Hareketleri & Ekstre")
    
    islem_modu = st.radio("İşlem Seçin:", ["🔴 Yeni Hareket", "📅 Tarihe Göre Bul", "📈 Dükkan Ekstresi", "📊 Aylık Karşılaştırma", "📋 Tüm Kayıtları Yönet", "🗓️ İki Tarih Arası Ciro"], horizontal=True)

    if islem_modu == "🔴 Yeni Hareket":
        kategoriler = ["Midye", "Çiğ Köfte", "İçecek", "Dükkan Gideri", "Personel", "Diğer"]
        
        # Form içi state çakışmasını önlemek için form key'ini dinamik hale getirdik
        with st.form("dukkan_form_yeni", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                islem_tipi = st.selectbox("İşlem Tipini Seçin", ["Günlük Satış (Gelir)", "Dükkan Gideri (Gider)"], index=1) # Gider eklediğin için varsayılan gider seçilebilir
                tarih_secim = st.date_input("Tarih", datetime.now(), key="yeni_hareket_tarih")
                kategori = st.selectbox("Kategori", kategoriler, index=3, key="yeni_hareket_kategori") # Varsayılan Dükkan Gideri
            with col2:
                urun_adi = st.text_input("Ürün / Detay Açıklaması", placeholder="Örn: Pepsi sarf malzemeleri", key="yeni_hareket_urun")
                miktar = st.number_input("Miktar / Adet", min_value=1, value=1, step=1, key="yeni_hareket_miktar")
                
                son_fiyat_sorgu = run_query_df("SELECT birim_fiyat FROM dukkan_hareket WHERE kategori=? AND birim_fiyat > 0 ORDER BY id DESC LIMIT 1", [kategori])
                varsayilan_fiyat = float(son_fiyat_sorgu['birim_fiyat'].iloc[0]) if not son_fiyat_sorgu.empty else 0.0
                
                birim_fiyat = st.number_input("Birim Fiyat / Tutar (TL)", min_value=0.0, value=0.0, step=0.5, format="%.2f", key="yeni_hareket_fiyat")

            hesaplanan_tutar = miktar * birim_fiyat
            st.info(f"Hesaplanan Toplam Tutar: **{hesaplanan_tutar:,.2f} TL**")

            submitted = st.form_submit_button("💾 Dükkan Hareketi Kaydet")
            if submitted:
                if hesaplanan_tutar > 0:
                    simdi_zaman = datetime.now().strftime("%H:%M:%S")
                    tam_tarih_saat = f"{tarih_secim.strftime('%Y-%m-%d')} {simdi_zaman}"
                    
                    kayit_aciklama = urun_adi if urun_adi and urun_adi.strip() != "" else kategori
                    
                    # Veritabanına doğrudan o an formdan gelen güncel değerler işleniyor
                    client.execute(
                        "INSERT INTO dukkan_hareket (tarih, islem_tipi, kategori, urun_adi, miktar, birim_fiyat, tutar) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        [tam_tarih_saat, islem_tipi, kategori, kayit_aciklama, miktar, birim_fiyat, hesaplanan_tutar]
                    )
                    st.success(f"Dükkan hareketi başarıyla kaydedildi! Toplam: {hesaplanan_tutar:,.2f} TL ({tam_tarih_saat})")
                    st.rerun()
                else:
                    st.warning("Lütfen geçerli bir miktar ve tutar girin!")

        st.markdown("---")
        st.subheader("📋 Bugünün Dükkan Kayıtları")
        
        df_bugun_dukkan = run_query_df("SELECT * FROM dukkan_hareket WHERE SUBSTR(tarih, 1, 10) = ? ORDER BY id DESC", [bugun])
        
        if not df_bugun_dukkan.empty:
            st.dataframe(df_bugun_dukkan, use_container_width=True)
        else:
            st.info("Bugüne ait henüz dükkan hareketi kaydedilmedi.")

# ==========================================
# 2. SEKME: TOPTAN (DÜZENLİ ALT SEKME YAPISI)
# ==========================================
with tab2:
    df_firmalar_opt = run_query_df("SELECT firma_adi FROM firmalar ORDER BY firma_adi ASC")
    firma_listesi = df_firmalar_opt["firma_adi"].tolist() if not df_firmalar_opt.empty else []

    if not firma_listesi:
        st.warning("⚠️ Lütfen önce 'Firmalar' sekmesinden bir firma ekleyin!")
    else:
        # ANA DAĞINIKLIĞI BİTİREN ALT SEKMELER
        alt_sekme1, alt_sekme2, alt_sekme3, alt_sekme4 = st.tabs([
            "➕ Yeni İşlem", 
            "📅 Tarihe Göre İşlemler", 
            "📄 Cari Ekstre & PDF", 
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
        # 3. ALT SEKME: CARİ EKSTRE & PDF RAPORLAR
        # ---------------------------------------------------------
        with alt_sekme3:
            st.subheader("📄 Kurumsal Firma Ekstresi ve PDF Çıktısı")
            
            col_f1, col_f2, col_f3, col_f4 = st.columns([2, 1, 1, 1.5])
            with col_f1:
                secilen_firma = st.selectbox("Ekstresi Alınacak Firma:", firma_listesi, key="ekstre_firma_sec_temiz")
            with col_f2:
                bas_tarih = st.date_input("Başlangıç", datetime.now().replace(day=1), key="toptan_bas_tarih_temiz")
            with col_f3:
                bit_tarih = st.date_input("Bitiş", datetime.now(), key="toptan_bit_tarih_temiz")
            with col_f4:
                ekstre_tipi = st.radio("Ekstre Türü", ["🔍 Detaylı", "📋 Özet"], key="toptan_ekstre_tipi_sec_temiz", horizontal=True)
                
            str_bas_tarih = bas_tarih.strftime("%Y-%m-%d")
            str_bit_tarih = bit_tarih.strftime("%Y-%m-%d")
            
            df_firma_hareket = run_query_df("""
                SELECT tarih, islem_turu, adet, birim_fiyat, toplam_tutar, aciklama 
                FROM toptan_satis 
                WHERE firma_adi = ? AND SUBSTR(tarih, 1, 10) BETWEEN ? AND ? 
                ORDER BY id ASC
            """, [secilen_firma, str_bas_tarih, str_bit_tarih])
            
            if not df_firma_hareket.empty:
                toplam_satis = df_firma_hareket[df_firma_hareket['islem_turu'] == 'Satış']['toplam_tutar'].sum()
                toplam_tahsilat = df_firma_hareket[df_firma_hareket['islem_turu'] == 'Tahsilat']['toplam_tutar'].sum()
                bakiye = toplam_satis - toplam_tahsilat
                
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Toplam Satış (Borç)", f"{toplam_satis:,.2f} TL")
                with m2:
                    st.metric("Yapılan Tahsilat", f"{toplam_tahsilat:,.2f} TL")
                with m3:
                    st.metric("Güncel Bakiye", f"{bakiye:,.2f} TL")
                    
                st.markdown("---")
                
                if ekstre_tipi == "🔍 Detaylı":
                    st.dataframe(df_firma_hareket, use_container_width=True, hide_index=True)
                else:
                    st.dataframe(df_firma_hareket[['tarih', 'islem_turu', 'toplam_tutar', 'aciklama']], use_container_width=True, hide_index=True)
                
                st.markdown("### 🖨️ Yazıcı ve PDF İşlemi")
                
                html_content = f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; color: #000; background: #fff;">
                    <h2 style="text-align: center; color: #333;">MİDYECİ ABLA - CARİ HESAP EKSTRESİ</h2>
                    <p style="text-align: center; color: #555; font-size: 14px;"><b>Rapor Türü:</b> {ekstre_tipi} Ekstre</p>
                    <hr>
                    <p><b>Firma Adı:</b> {secilen_firma}</p>
                    <p><b>Tarih Aralığı:</b> {str_bas_tarih} / {str_bit_tarih}</p>
                    <br>
                    <table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
                        <thead>
                            <tr style="background-color: #f2f2f2;">
                                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Tarih</th>
                                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">İşlem Türü</th>
                """
                if ekstre_tipi == "🔍 Detaylı":
                    html_content += """
                                <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Adet</th>
                                <th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Birim Fiyat</th>
                    """
                html_content += """
                                <th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Tutar</th>
                                <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Açıklama</th>
                            </tr>
                        </thead>
                        <tbody>
                """
                for index, row in df_firma_hareket.iterrows():
                    html_content += f"""
                            <tr>
                                <td style="border: 1px solid #ddd; padding: 8px;">{row['tarih']}</td>
                                <td style="border: 1px solid #ddd; padding: 8px;">{row['islem_turu']}</td>
                    """
                    if ekstre_tipi == "🔍 Detaylı":
                        html_content += f"""
                                <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{row['adet']}</td>
                                <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">{row['birim_fiyat']:,.2f} TL</td>
                        """
                    html_content += f"""
                                <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">{row['toplam_tutar']:,.2f} TL</td>
                                <td style="border: 1px solid #ddd; padding: 8px;">{row['aciklama'] if pd.notna(row['aciklama']) else '-'}</td>
                            </tr>
                    """
                html_content += f"""
                        </tbody>
                    </table>
                    <br>
                    <h3>Özet:</h3>
                    <p><b>Toplam Borç:</b> {toplam_satis:,.2f} TL</p>
                    <p><b>Toplam Tahsilat:</b> {toplam_tahsilat:,.2f} TL</p>
                    <p><b>Kalan Bakiye:</b> {bakiye:,.2f} TL</p>
                </div>
                """
                
                import streamlit.components.v1 as components
                print_button_html = f"""
                <script>
                function printDiv() {{
                    var printContents = `{html_content}`;
                    var originalContents = document.body.innerHTML;
                    document.body.innerHTML = printContents;
                    window.print();
                    document.body.innerHTML = originalContents;
                    window.location.reload();
                }}
                </script>
                <button onclick="printDiv()" style="background-color: #ff4b4b; color: white; padding: 12px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold;">🖨️ Yazdır / PDF Olarak Kaydet</button>
                """
                components.html(print_button_html, height=70)
            else:
                st.warning(f"🔍 {secilen_firma} firmasına ait bu tarih aralığında hareket bulunamadı.")

        # ---------------------------------------------------------
        # 4. ALT SEKME: TÜM KAYITLAR & GENEL YÖNETİM
        # ---------------------------------------------------------
        with alt_sekme4:
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
with tab3:
    st.subheader("🏢 Firma Yönetimi")
    f_islem = st.radio("İşlem Seçin:", ["Yeni Firma Ekle", "Firma Düzenle / Sil"], horizontal=True)
    
    if f_islem == "Yeni Firma Ekle":
        with st.form("yeni_firma_form", clear_on_submit=True):
            yeni_f_adi = st.text_input("Firma Ünvanı / Adı *")
            yeni_f_tel = st.text_input("Telefon No")
            yeni_f_not = st.text_input("Açıklama / Not")
            
            f_kaydet = st.form_submit_button("➕ Firmayı Kaydet", type="primary")
            if f_kaydet and yeni_f_adi:
                try:
                    client.execute("INSERT INTO firmalar (firma_adi, telefon, aciklama) VALUES (?, ?, ?)", 
                                   [yeni_f_adi.strip(), yeni_f_tel.strip(), yeni_f_not.strip()])
                    st.success(f"'{yeni_f_adi.strip()}' eklendi!")
                    st.rerun()
                except Exception:
                    st.error("Bu firma zaten kayıtlı veya bir hata oluştu!")
                    
    else:
        df_firmalar_all = run_query_df("SELECT id, firma_adi, telefon, aciklama FROM firmalar ORDER BY firma_adi ASC")
        if not df_firmalar_all.empty:
            secili_f_id = st.selectbox("Düzenlenecek Firmayı Seçin:", 
                                       options=df_firmalar_all["id"], 
                                       format_func=lambda x: df_firmalar_all[df_firmalar_all['id']==x]['firma_adi'].values[0])
            
            f_kayit = df_firmalar_all[df_firmalar_all["id"] == secili_f_id].iloc[0]
            
            with st.form("firma_duzenle_form"):
                e_f_adi = st.text_input("Firma Adı", value=f_kayit["firma_adi"])
                e_f_tel = st.text_input("Telefon No", value=str(f_kayit["telefon"]) if f_kayit["telefon"] else "")
                e_f_not = st.text_input("Açıklama", value=str(f_kayit["aciklama"]) if f_kayit["aciklama"] else "")
                
                f_guncelle = st.form_submit_button("✏️ Güncelle", type="primary")
                f_sil = st.form_submit_button("🗑️ Firmayı Sil")
                
                if f_guncelle:
                    client.execute("UPDATE firmalar SET firma_adi=?, telefon=?, aciklama=? WHERE id=?", 
                                   [e_f_adi.strip(), e_f_tel.strip(), e_f_not.strip(), int(secili_f_id)])
                    st.success("Firma güncellendi!")
                    st.rerun()
                    
                if f_sil:
                    client.execute("DELETE FROM firmalar WHERE id=?", [int(secili_f_id)])
                    st.warning("Firma silindi!")
                    st.rerun()
        else:
            st.info("Kayıtlı firma bulunmuyor.")

    st.divider()
    st.write("**Kayıtlı Firmalar**")
    df_f_list = run_query_df("SELECT firma_adi as 'Firma Adı', telefon as 'Telefon' FROM firmalar ORDER BY firma_adi ASC")
    st.dataframe(df_f_list, use_container_width=True)

# ==========================================
# 4. SEKME: CARİ EKSTRE
# ==========================================
with tab4:
    st.subheader("📊 Firma Cari Ekstresi")
    
    df_firmalar_cari = run_query_df("SELECT firma_adi FROM firmalar ORDER BY firma_adi ASC")
    
    if not df_firmalar_cari.empty:
        firmalar_list = df_firmalar_cari["firma_adi"].tolist()
        secili_firma_detay = st.selectbox("🔍 Firma Seçin:", firmalar_list)
        
        if secili_firma_detay:
            st.divider()
            st.markdown(f"### 📌 {secili_firma_detay}")
            
            df_f_satis = run_query_df("SELECT SUM(toplam_tutar) as t FROM toptan_satis WHERE firma_adi=? AND islem_turu='Satış'", [secili_firma_detay])
            df_f_tahsilat = run_query_df("SELECT SUM(toplam_tutar) as t FROM toptan_satis WHERE firma_adi=? AND islem_turu='Tahsilat'", [secili_firma_detay])
            
            tot_satis = df_f_satis['t'].iloc[0] if not df_f_satis.empty and pd.notnull(df_f_satis['t'].iloc[0]) else 0.0
            tot_tahsilat = df_f_tahsilat['t'].iloc[0] if not df_f_tahsilat.empty and pd.notnull(df_f_tahsilat['t'].iloc[0]) else 0.0
            net_bakiye = tot_satis - tot_tahsilat
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Toplam Satış", f"{tot_satis:,.2f} TL")
            with col2:
                st.metric("Toplam Tahsilat", f"{tot_tahsilat:,.2f} TL")
            with col3:
                if net_bakiye > 0:
                    st.metric("Kalan Borç", f"{net_bakiye:,.2f} TL", delta="- Borçlu", delta_color="inverse")
                elif net_bakiye < 0:
                    st.metric("Alacak Bakiyesi", f"{abs(net_bakiye):,.2f} TL", delta="+ Alacaklı", delta_color="normal")
                else:
                    st.metric("Net Bakiye", "0.00 TL", delta="Dengede")
                
            st.write("**İşlem Geçmişi**")
            df_ekstre = run_query_df("""
                SELECT tarih as 'Tarih', islem_turu as 'İşlem', adet as 'Adet', toplam_tutar as 'Tutar (TL)'
                FROM toptan_satis 
                WHERE firma_adi=? 
                ORDER BY id DESC
            """, [secili_firma_detay])
            
            if not df_ekstre.empty:
                st.dataframe(df_ekstre, use_container_width=True)
            else:
                st.info("İşlem hareketi bulunmuyor.")

# ==========================================
# 5. SEKME: TÜM BORÇ / ALACAK ÖZETİ (YENİ SEKME)
# ==========================================
with tab5:
    st.subheader("💰 Tüm Firmaların Borç / Alacak Listesi")
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
