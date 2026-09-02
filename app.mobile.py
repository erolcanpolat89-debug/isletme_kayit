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
# 1. SEKME: DÜKKAN
# ==========================================
with tab1:
    st.subheader("🏪 Dükkan Hareketleri & Ekstre")
    
    islem_modu = st.radio("İşlem Seçin:", ["🔴 Yeni Hareket", "📅 Tarihe Göre Bul", "📈 Dükkan Ekstresi", "📊 Aylık Karşılaştırma", "📋 Tüm Kayıtları Yönet"], horizontal=True)

    if islem_modu == "🔴 Yeni Hareket":
        kategoriler = ["Midye", "Çiğ Köfte", "İçecek", "Dükkan Gideri", "Personel", "Diğer"]
        
        with st.form("dukkan_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                islem_tipi = st.selectbox("İşlem Tipi", ["Günlük Satış (Gelir)", "Dükkan Gideri (Gider)"])
                tarih_secim = st.date_input("Tarih", datetime.now())
                kategori = st.selectbox("Kategori", kategoriler, index=0)
            with col2:
                urun_adi = st.text_input("Ürün / Detay Açıklaması", placeholder="Örn: Midye Satışı veya Kira Gideri")
                miktar = st.number_input("Miktar / Adet", min_value=1, value=1, step=1)
                
                son_fiyat_sorgu = run_query_df("SELECT birim_fiyat FROM dukkan_hareket WHERE kategori=? AND birim_fiyat > 0 ORDER BY id DESC LIMIT 1", [kategori])
                varsayilan_fiyat = float(son_fiyat_sorgu['birim_fiyat'].iloc[0]) if not son_fiyat_sorgu.empty else 0.0
                
                birim_fiyat = st.number_input("Birim Fiyat (TL)", min_value=0.0, value=varsayilan_fiyat, step=0.5, format="%.2f")

            hesaplanan_tutar = miktar * birim_fiyat
            st.info(f"Hesaplanan Toplam Tutar: **{hesaplanan_tutar:,.2f} TL** (Seçilen kategori son fiyatı: {varsayilan_fiyat} TL)")

            submitted = st.form_submit_button("💾 Dükkan Hareketi Kaydet")
            if submitted:
                if hesaplanan_tutar > 0:
                    simdi_zaman = datetime.now().strftime("%H:%M:%S")
                    tam_tarih_saat = f"{tarih_secim.strftime('%Y-%m-%d')} {simdi_zaman}"
                    
                    client.execute(
                        "INSERT INTO dukkan_hareket (tarih, islem_tipi, kategori, urun_adi, miktar, birim_fiyat, tutar) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        [tam_tarih_saat, islem_tipi, kategori, urun_adi, miktar, birim_fiyat, hesaplanan_tutar]
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
            
            df_gelirler = df_dukkan_gun[df_dukkan_gun['islem_tipi'] == 'Günlük Satış (Gelir)']
            
            toplam_ciro = df_gelirler['tutar'].sum() if not df_gelirler.empty else 0.0
            
            midye_df = df_gelirler[df_gelirler['kategori'] == 'Midye']
            toplam_midye = midye_df['miktar'].sum() if not midye_df.empty else 0
            
            cig_kofte_df = df_gelirler[df_gelirler['kategori'] == 'Çiğ Köfte']
            toplam_cig_kofte = cig_kofte_df['miktar'].sum() if not cig_kofte_df.empty else 0
            
            icecek_df = df_gelirler[df_gelirler['kategori'] == 'İçecek']
            toplam_icecek = icecek_df['miktar'].sum() if not icecek_df.empty else 0

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Seçilen Gün Ciro", f"{toplam_ciro:,.2f} TL")
            with col2:
                st.metric("Toplam Midye", f"{int(toplam_midye):,} adet")
            with col3:
                st.metric("Toplam Çiğ Köfte", f"{int(toplam_cig_kofte):,} adet")
            with col4:
                st.metric("Toplam İçecek", f"{int(toplam_icecek):,} adet")
            
            st.markdown("---")
            st.dataframe(df_dukkan_gun, use_container_width=True)

            st.markdown("---")
            
            col_slider1, col_slider2 = st.columns([2, 1])
            with col_slider1:
                st.subheader("📊 Ciro ve Satış Trendi")
            with col_slider2:
                gun_sayisi = st.slider("Trend Gün Sayısı:", min_value=3, max_value=30, value=7, key="trend_gun_slider")

            df_trend = run_query_df("""
                SELECT SUBSTR(tarih, 1, 10) as gun, 
                       SUM(tutar) as toplam_ciro,
                       SUM(CASE WHEN kategori = 'Midye' THEN miktar ELSE 0 END) as toplam_midye
                FROM dukkan_hareket 
                WHERE islem_tipi = 'Günlük Satış (Gelir)'
                GROUP BY gun 
                ORDER BY gun DESC 
                LIMIT ?
            """, [gun_sayisi])

            if not df_trend.empty:
                df_trend = df_trend.sort_values('gun').reset_index(drop=True)
                df_chart = df_trend.set_index('gun')
                st.bar_chart(df_chart['toplam_ciro'], color="#ff4b4b")
                
                if len(df_trend) >= 2:
                    son_ciro = df_trend.iloc[-1]['toplam_ciro']
                    bir_onceki_ciro = df_trend.iloc[-2]['toplam_ciro']
                    son_tarih = df_trend.iloc[-1]['gun']
                    bir_onceki_tarih = df_trend.iloc[-2]['gun']
                    
                    if bir_onceki_ciro > 0:
                        yuzde_degisim = ((son_ciro - bir_onceki_ciro) / bir_onceki_ciro) * 100
                    else:
                        yuzde_degisim = 100.0 if son_ciro > 0 else 0.0
                        
                    st.markdown(f"📈 **Son İki Günün Değişim Analizi ({bir_onceki_tarih} ➔ {son_tarih}):**")
                    
                    col_A, col_B, col_C = st.columns(3)
                    with col_A:
                        st.metric("Önceki Gün Ciro", f"{bir_onceki_ciro:,.2f} TL")
                    with col_B:
                        st.metric("Son Gün Ciro", f"{son_ciro:,.2f} TL")
                    with col_C:
                        st.metric("Değişim Oranı", f"%{yuzde_degisim:+.1f}", delta=f"%{yuzde_degisim:+.1f}")
            else:
                st.info("📊 Grafik için henüz yeterli satış verisi bulunmuyor.")

    elif islem_modu == "📈 Dükkan Ekstresi":
        st.subheader("📈 Dükkan Ekstresi & Tarih Bazlı Detaylı Döküm")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            baslangic_tarihi = st.date_input("Başlangıç Tarihi", datetime.now() - timedelta(days=30), key="ekstre_bas_tarih")
        with col_f2:
            bitis_tarihi = st.date_input("Bitiş Tarihi", datetime.now(), key="ekstre_bit_tarih")
            
        str_bas = baslangic_tarihi.strftime("%Y-%m-%d")
        str_bit = bitis_tarihi.strftime("%Y-%m-%d")
        
        # Seçilen tarih aralığındaki hareketleri çekelim
        query_ekstre = """
            SELECT * FROM dukkan_hareket 
            WHERE SUBSTR(tarih, 1, 10) BETWEEN ? AND ? 
            ORDER BY id DESC
        """
        df_ekstre = run_query_df(query_ekstre, [str_bas, str_bit])
        
        # Seçilen aralığın genel gelir/gider özeti
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
        st.subheader(f"📦 {str_bas} ➔ {str_bit} Arasındaki Giden Ürünler ve Detaylar")
        
        if not df_ekstre.empty:
            # Ürün/Kategori bazlı giden toplam miktarlar (Sadece Satışlar)
            df_urun_ozet = run_query_df("""
                SELECT kategori, urun_adi, SUM(miktar) as toplam_miktar, SUM(tutar) as toplam_tutar 
                FROM dukkan_hareket 
                WHERE SUBSTR(tarih, 1, 10) BETWEEN ? AND ? AND islem_tipi = 'Günlük Satış (Gelir)'
                GROUP BY kategori, urun_adi
            """, [str_bas, str_bit])
            
            if not df_urun_ozet.empty:
                st.markdown("**📌 Ürün Bazlı Toplam Satışlar (Neler Gitti?):**")
                st.dataframe(df_urun_ozet, use_container_width=True, hide_index=True)
            
            st.markdown("**📋 Tüm İşlem Listesi:**")
            st.dataframe(df_ekstre, use_container_width=True, hide_index=True)
        else:
            st.warning("Bu tarih aralığına ait kayıt bulunamadı.")

    elif islem_modu == "📊 Aylık Karşılaştırma":
        st.subheader("📊 İki Ayın Performans ve Ürün Kıyaslama Raporu")
        
        # Veritabanından mevcut kayıtlı olan tüm ayları çekelim
        df_aylar = run_query_df("""
            SELECT DISTINCT SUBSTR(tarih, 1, 7) as yil_ay 
            FROM dukkan_hareket 
            WHERE islem_tipi = 'Günlük Satış (Gelir)' 
            ORDER BY yil_ay DESC
        """)
        
        if not df_aylar.empty:
            mevcut_aylar = df_aylar['yil_ay'].tolist()
        else:
            mevcut_aylar = [datetime.now().strftime("%Y-%m")]
            
        col_sec1, col_sec2 = st.columns(2)
        with col_sec1:
            # 1. Ay Seçimi (Örn: Geçen Ay veya baz alınacak ay)
            default_idx_1 = 1 if len(mevcut_aylar) > 1 else 0
            secilen_ay_1 = st.selectbox("1. Ayı Seçin (Sol Taraf):", mevcut_aylar, index=default_idx_1, key="ay_secim_1")
        with col_sec2:
            # 2. Ay Seçimi (Örn: Bu Ay veya kıyaslanacak ay)
            secilen_ay_2 = st.selectbox("2. Ayı Seçin (Sağ Taraf):", mevcut_aylar, index=0, key="ay_secim_2")
        
        # Seçilen 1. Ayın verilerini çek
        df_ay1 = run_query_df("""
            SELECT SUM(tutar) as toplam_ciro,
                   SUM(CASE WHEN kategori = 'Midye' THEN miktar ELSE 0 END) as toplam_midye,
                   SUM(CASE WHEN kategori = 'Çiğ Köfte' THEN miktar ELSE 0 END) as toplam_cigkofte,
                   SUM(CASE WHEN kategori = 'İçecek' THEN miktar ELSE 0 END) as toplam_icecek
            FROM dukkan_hareket 
            WHERE islem_tipi = 'Günlük Satış (Gelir)' AND SUBSTR(tarih, 1, 7) = ?
        """, [secilen_ay_1])
        
        # Seçilen 2. Ayın verilerini çek
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
        
        midye_1 = df_ay1.iloc[0]['toplam_midye'] if not df_ay1.empty and df_ay1.iloc[0]['toplam_midye'] is not None else 0
        midye_2 = df_ay2.iloc[0]['toplam_midye'] if not df_ay2.empty and df_ay2.iloc[0]['toplam_midye'] is not None else 0

        if ciro_1 > 0:
            ciro_degisim = ((ciro_2 - ciro_1) / ciro_1) * 100
        else:
            ciro_degisim = 100.0 if ciro_2 > 0 else 0.0

        st.markdown(f"### 🗓️ {secilen_ay_1} ➔ {secilen_ay_2} Performans Özeti")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"{secilen_ay_1} Ciro", f"{ciro_1:,.2f} TL")
        with col2:
            st.metric(f"{secilen_ay_2} Ciro", f"{ciro_2:,.2f} TL", delta=f"%{ciro_degisim:+.1f}")
        with col3:
            st.metric("Ciro Farkı", f"{(ciro_2 - ciro_1):+,.2f} TL")
            
        st.markdown("---")
        
        st.subheader("📦 Ürün Bazlı Ay Karşılaştırması")
        data_karsilastirma = {
            "Kategori": ["Midye (Adet)", "Çiğ Köfte (Adet)", "İçecek (Adet)"],
            f"{secilen_ay_1}": [
                int(midye_1), 
                int(df_ay1.iloc[0]['toplam_cigkofte'] if not df_ay1.empty and df_ay1.iloc[0]['toplam_cigkofte'] is not None else 0), 
                int(df_ay1.iloc[0]['toplam_icecek'] if not df_ay1.empty and df_ay1.iloc[0]['toplam_icecek'] is not None else 0)
            ],
            f"{secilen_ay_2}": [
                int(midye_2), 
                int(df_ay2.iloc[0]['toplam_cigkofte'] if not df_ay2.empty and df_ay2.iloc[0]['toplam_cigkofte'] is not None else 0), 
                int(df_ay2.iloc[0]['toplam_icecek'] if not df_ay2.empty and df_ay2.iloc[0]['toplam_icecek'] is not None else 0)
            ]
        }
        df_karsilastirma_tablo = pd.DataFrame(data_karsilastirma)
        st.dataframe(df_karsilastirma_tablo, use_container_width=True, hide_index=True)

    elif islem_modu == "📋 Tüm Kayıtları Yönet":
        st.subheader("📋 Dükkan Kayıtlarını Düzenle / Sil")
        df_dukkan_all = run_query_df("SELECT * FROM dukkan_hareket ORDER BY id DESC LIMIT 50")
        
        if df_dukkan_all.empty:
            st.info("Düzenlenecek kayıt bulunmuyor.")
        else:
            secilen_dukkan_id = st.selectbox(
                "İşlem Yapılacak Kaydı Seçin:", 
                options=df_dukkan_all["id"], 
                format_func=lambda x: f"ID:{x} - {df_dukkan_all[df_dukkan_all['id']==x]['tarih'].values[0]} | {df_dukkan_all[df_dukkan_all['id']==x]['kategori'].values[0]} ({df_dukkan_all[df_dukkan_all['id']==x]['tutar'].values[0]} TL)"
            )
            
            dukkan_kayit = df_dukkan_all[df_dukkan_all["id"] == secilen_dukkan_id].iloc[0]
            kategoriler = ["Midye", "Çiğ Köfte", "İçecek", "Dükkan Gideri", "Personel", "Diğer"]
            
            with st.form("dukkan_duzenle_form"):
                e_islem_tipi = st.selectbox("İşlem Tipi", ["Günlük Satış (Gelir)", "Dükkan Gideri (Gider)"], index=0 if dukkan_kayit["islem_tipi"] == "Günlük Satış (Gelir)" else 1)
                e_kategori = st.selectbox("Kategori", kategoriler, index=kategoriler.index(dukkan_kayit["kategori"]) if dukkan_kayit["kategori"] in kategoriler else 0)
                e_urun = st.text_input("Ürün / Detay Açıklaması", value=str(dukkan_kayit["urun_adi"]) if pd.notnull(dukkan_kayit["urun_adi"]) else "")
                e_miktar = st.number_input("Miktar / Adet", min_value=1, value=int(dukkan_kayit["miktar"]), step=1)
                e_birim = st.number_input("Birim Fiyat (TL)", min_value=0.0, value=float(dukkan_kayit["birim_fiyat"]), step=0.5, format="%.2f")
                
                e_hesaplanan_tutar = e_miktar * e_birim
                st.info(f"Güncellenecek Toplam Tutar: **{e_hesaplanan_tutar:,.2f} TL**")
                
                d_guncelle = st.form_submit_button("✏️ Kaydı Güncelle", type="primary")
                d_sil = st.form_submit_button("🗑️ Kaydı Sil")
                
                if d_guncelle:
                    client.execute(
                        "UPDATE dukkan_hareket SET islem_tipi=?, kategori=?, urun_adi=?, miktar=?, birim_fiyat=?, tutar=? WHERE id=?",
                        [e_islem_tipi, e_kategori, e_urun, e_miktar, e_birim, e_hesaplanan_tutar, int(secilen_dukkan_id)]
                    )
                    st.success("Kayıt başarıyla güncellendi!")
                    st.rerun()
                    
                if d_sil:
                    client.execute("DELETE FROM dukkan_hareket WHERE id=?", [int(secilen_dukkan_id)])
                    st.warning("Kayıt silindi!")
                    st.rerun()

    elif islem_modu == "📅 Tarihe Göre Bul":
        secilen_tarih = st.date_input("Filtrelenecek Tarih", datetime.now()).strftime("%Y-%m-%d")
        df_dukkan_tarih = run_query_df("SELECT * FROM dukkan_hareket WHERE SUBSTR(tarih, 1, 10) = ? ORDER BY id DESC", [secilen_tarih])
        
        if not df_dukkan_tarih.empty:
            st.dataframe(df_dukkan_tarih, use_container_width=True)
            toplam_gelir = df_dukkan_tarih[df_dukkan_tarih["islem_tipi"] == "Günlük Satış (Gelir)"]["tutar"].sum() if "islem_tipi" in df_dukkan_tarih.columns else 0
            toplam_gider = df_dukkan_tarih[df_dukkan_tarih["islem_tipi"] == "Dükkan Gideri (Gider)"]["tutar"].sum() if "islem_tipi" in df_dukkan_tarih.columns else 0
            c1, c2, c3 = st.columns(3)
            c1.metric("Günün Geliri", f"{toplam_gelir:,.2f} TL")
            c2.metric("Günün Gideri", f"{toplam_gider:,.2f} TL")
            c3.metric("Net Durum", f"{(toplam_gelir - toplam_gider):,.2f} TL")
        else:
            st.info("Seçilen tarihe ait kayıt bulunamadı.")

    elif islem_modu == "📈 Dükkan Ekstresi":
        st.markdown("### 🦪 Dükkan Satış ve Kategori Ekstresi")
        
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            baslangic_tarihi = st.date_input("Başlangıç Tarihi", datetime.now()).strftime("%Y-%m-%d")
        with col_e2:
            bitis_tarihi = st.date_input("Bitiş Tarihi", datetime.now()).strftime("%Y-%m-%d")
            
        secilen_kategori = st.selectbox("Kategori Filtresi", ["Tümü", "Çiğ Köfte", "Midye", "İçecek", "Dükkan Gideri", "Personel", "Diğer"])
        ekstre_tipi = st.radio("Ekstre Görünüm Modu:", ["Detaylı Ekstre (Tüm İşlemler)", "Detaysız Ekstre (Kategori Toplamları)"], horizontal=True)
        
        query = "SELECT * FROM dukkan_hareket WHERE SUBSTR(tarih, 1, 10) >= ? AND SUBSTR(tarih, 1, 10) <= ?"
        params = [baslangic_tarihi, bitis_tarihi]
        
        if secilen_kategori != "Tümü":
            query += " AND kategori LIKE ?"
            params.append(f"%{secilen_kategori}%")
            
        query += " ORDER BY tarih DESC"
        df_ekstre = run_query_df(query, params)
        
        st.markdown("---")
        st.subheader("👁️ Canlı Ekstre Ön İzlemesi")
        
        if not df_ekstre.empty:
            st.markdown('<div class="preview-box">', unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align: center; color: #000000;'>MİDYECİ ABLA - DÜKKAN EKSTRESİ</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #555;'>Tarih Aralığı: <b>{baslangic_tarihi}</b> ile <b>{bitis_tarihi}</b> | Kategori: <b>{secilen_kategori}</b></p>", unsafe_allow_html=True)
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
            st.info("💡 Yukarıdaki ön izlemeyi tarayıcınızın yazdırma özelliğiyle (Ctrl + P) direkt kağıda dökebilir veya PDF olarak kaydedebilirsiniz.")
        else:
            st.warning("Belirtilen kriterlerde ve tarih aralığında herhangi bir hareket bulunamadı.")

    elif islem_modu == "📋 Tüm Kayıtları Yönet":
        df_tum_dukkan = run_query_df("SELECT * FROM dukkan_hareket ORDER BY id DESC")
        st.dataframe(df_tum_dukkan, use_container_width=True)
        
        silinecek_id = st.number_input("Silinecek Kayıt ID", min_value=1, step=1)
        if st.button("🗑️ Seçili Kaydı Sil"):
            client.execute("DELETE FROM dukkan_hareket WHERE id = ?", [silinecek_id])
            st.success(f"ID: {silinecek_id} olan kayıt silindi.")
            st.rerun()

    else:
        st.subheader("Tüm Dükkan Kayıtlarını Yönet")
        df_dukkan_all = run_query_df("SELECT id, tarih, islem_tipi, kategori, urun_adi, miktar, birim_fiyat, tutar FROM dukkan_hareket ORDER BY id DESC")
        
        if not df_dukkan_all.empty:
            secilen_d_id = st.selectbox("Kayıt Seçin:", 
                                        options=df_dukkan_all["id"], 
                                        format_func=lambda x: f"ID:{x} - {df_dukkan_all[df_dukkan_all['id']==x]['tarih'].values[0]} - {df_dukkan_all[df_dukkan_all['id']==x]['kategori'].values[0]} ({df_dukkan_all[df_dukkan_all['id']==x]['tutar'].values[0]} TL)")
            
            kayit_d = df_dukkan_all[df_dukkan_all["id"] == secilen_d_id].iloc[0]
            kat_list = ["Midye Dolma", "Çiğ Köfte", "İçecek", "Dükkan Genel Gider", "Diğer"]
            tip_list = ["Günlük Satış (Gelir)", "Gider (Harcama)", "Stok Girişi"]
            
            with st.form("dukkan_duzenle_form"):
                e_tip = st.selectbox("İşlem Tipi", tip_list, index=tip_list.index(kayit_d["islem_tipi"]) if kayit_d["islem_tipi"] in tip_list else 0)
                e_tarih_d = st.date_input("Tarih", datetime.strptime(str(kayit_d["tarih"]), "%Y-%m-%d"))
                e_kat = st.selectbox("Kategori", kat_list, index=kat_list.index(kayit_d["kategori"]) if kayit_d["kategori"] in kat_list else 0)
                e_urun = st.text_input("Ürün / Detay", value=str(kayit_d["urun_adi"]) if kayit_d["urun_adi"] else "")
                e_m = st.number_input("Miktar", min_value=1, step=1, value=int(kayit_d["miktar"]))
                e_f = st.number_input("Birim Fiyat (TL)", min_value=0.0, step=0.5, value=float(kayit_d["birim_fiyat"]), format="%.2f")
                
                e_toplam_d = e_m * e_f
                st.info(f"Yeni Toplam: **{e_toplam_d:,.2f} TL**")
                
                guncelle_d = st.form_submit_button("✏️ Güncelle", type="primary")
                sil_d = st.form_submit_button("🗑️ Sil")
                
                if guncelle_d:
                    client.execute("""
                        UPDATE dukkan_hareket 
                        SET tarih=?, islem_tipi=?, kategori=?, urun_adi=?, miktar=?, birim_fiyat=?, tutar=? 
                        WHERE id=?
                    """, [e_tarih_d.strftime("%Y-%m-%d"), e_tip, e_kat, e_urun, e_m, e_f, e_toplam_d, int(secilen_d_id)])
                    st.success("Kayıt güncellendi!")
                    st.rerun()
                    
                if sil_d:
                    client.execute("DELETE FROM dukkan_hareket WHERE id=?", [int(secilen_d_id)])
                    st.warning("Kayıt silindi!")
                    st.rerun()

    st.divider()
    
    # Günlük Özet
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
                    e_firma = st.selectbox("Firma Seçin", firma_listesi, index=firma_listesi.index(kayit__tum) if 'kayit_tum' in locals() and kayit_tum["firma_adi"] in firma_listesi else 0, key="efirma_arsiv")
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
