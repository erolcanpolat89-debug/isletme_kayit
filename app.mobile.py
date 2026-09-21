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
# 1. SEKME: DÜKKAN (TÜM MODLARIYLA TAM VE EKSİKSİZ KOD)
# ==========================================
with tab1:
    st.subheader("🏪 Dükkan Hareketleri & Ekstre")
    
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
                urun_adi = st.text_input("Ürün / Detay Açıklaması", placeholder="Örn: Açıklama Giriniz.", key="yeni_hareket_urun")
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
with tab2:

    df_firmalar_opt = run_query_df(
        "SELECT firma_adi FROM firmalar ORDER BY firma_adi ASC"
    )

    firma_listesi = (
        df_firmalar_opt["firma_adi"].tolist()
        if not df_firmalar_opt.empty
        else []
    )

    if not firma_listesi:

        st.warning(
            "⚠️ Lütfen önce 'Firmalar' sekmesinden bir firma ekleyin!"
        )

    else:

        # =====================================================
        # TOPTAN ALT SEKMELER
        # =====================================================
        alt_sekme1, alt_sekme2, alt_sekme3, alt_sekme4 = st.tabs([
            "➕ Yeni İşlem",
            "📅 Tarihe Göre İşlemler",
            "📄 Cari Ekstre & PDF",
            "⚙️ Tüm Kayıtlar & Yönetim"
        ])


        # =====================================================
        # 1. ALT SEKME: YENİ İŞLEM
        # =====================================================
        with alt_sekme1:

            st.subheader("Yeni Toptan İşlem Girişi")

            islem_turu = st.selectbox(
                "İşlem Tipi",
                [
                    "Satış (Borç Ekle)",
                    "Tahsilat (Borç Düş/Alacak)"
                ],
                key="toptan_islem_tipi_select_yeni"
            )

            secili_firma_toptan = st.selectbox(
                "Firma Seçin",
                firma_listesi,
                key="toptan_firma_secim_yeni"
            )

            if secili_firma_toptan:

                df_f_s = run_query_df(
                    """
                    SELECT SUM(toplam_tutar) as t
                    FROM toptan_satis
                    WHERE firma_adi=?
                      AND islem_turu='Satış'
                    """,
                    [secili_firma_toptan]
                )

                df_f_t = run_query_df(
                    """
                    SELECT SUM(toplam_tutar) as t
                    FROM toptan_satis
                    WHERE firma_adi=?
                      AND islem_turu='Tahsilat'
                    """,
                    [secili_firma_toptan]
                )

                f_s = (
                    df_f_s["t"].iloc[0]
                    if not df_f_s.empty
                    and pd.notnull(df_f_s["t"].iloc[0])
                    else 0.0
                )

                f_t = (
                    df_f_t["t"].iloc[0]
                    if not df_f_t.empty
                    and pd.notnull(df_f_t["t"].iloc[0])
                    else 0.0
                )

                f_bakiye = f_s - f_t

                if f_bakiye > 0:

                    st.error(
                        f"📌 **{secili_firma_toptan}** "
                        f"Güncel Durumu: "
                        f"**{f_bakiye:,.2f} TL BORÇLU**"
                    )

                elif f_bakiye < 0:

                    st.success(
                        f"📌 **{secili_firma_toptan}** "
                        f"Güncel Durumu: "
                        f"**{abs(f_bakiye):,.2f} TL ALACAKLI "
                        f"(Fazla Ödeme)**"
                    )

                else:

                    st.info(
                        f"📌 **{secili_firma_toptan}** "
                        f"Güncel Durumu: "
                        f"**0.00 TL "
                        f"(Hesap Kapalı / Borcu Yok)**"
                    )

            with st.form(
                "toptan_form_duzenli",
                clear_on_submit=True
            ):

                tarih = st.date_input(
                    "İşlem Tarihi",
                    datetime.now()
                )

                if islem_turu == "Satış (Borç Ekle)":

                    adet = st.number_input(
                        "Satılan Adet",
                        min_value=1,
                        step=50,
                        value=100
                    )

                    birim_fiyat = st.number_input(
                        "Birim Fiyat (TL)",
                        min_value=0.0,
                        step=0.5,
                        value=15.0,
                        format="%.2f"
                    )

                    toplam_tutar = adet * birim_fiyat

                    st.info(
                        f"Hesaplanan Tutar: "
                        f"**{toplam_tutar:,.2f} TL**"
                    )

                else:

                    adet = 0
                    birim_fiyat = 0.0

                    toplam_tutar = st.number_input(
                        "Tahsil Edilen Tutar (TL)",
                        min_value=0.0,
                        step=50.0,
                        value=2430.0,
                        format="%.2f"
                    )

                    st.success(
                        f"Tahsilat Tutarı: "
                        f"**{toplam_tutar:,.2f} TL**"
                    )

                aciklama = st.text_input(
                    "Açıklama / Not"
                )

                kaydet = st.form_submit_button(
                    "💾 İşlemi Kaydet",
                    type="primary"
                )

                if kaydet:

                    t_tur = (
                        "Satış"
                        if islem_turu == "Satış (Borç Ekle)"
                        else "Tahsilat"
                    )

                    client.execute(
                        """
                        INSERT INTO toptan_satis
                        (
                            firma_adi,
                            tarih,
                            islem_turu,
                            adet,
                            birim_fiyat,
                            toplam_tutar,
                            aciklama
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        [
                            secili_firma_toptan,
                            tarih.strftime("%Y-%m-%d"),
                            t_tur,
                            adet,
                            birim_fiyat,
                            toplam_tutar,
                            aciklama
                        ]
                    )

                    st.success(
                        f"✅ {t_tur} başarıyla kaydedildi!"
                    )

                    st.rerun()


        # =====================================================
        # 2. ALT SEKME: TARİHE GÖRE İŞLEMLER
        # =====================================================
        with alt_sekme2:

            st.subheader(
                "📅 Tarih Bazlı Arama ve Günlük Yönetim"
            )

            col_t1, col_t2 = st.columns([1, 1])

            with col_t1:

                secilen_tarih = st.date_input(
                    "Sorgulanacak Tarih Seçin:",
                    datetime.now(),
                    key="toptan_tarih_sorgu_temiz"
                )

            with col_t2:

                islem_filtresi = st.radio(
                    "İşlem Filtresi",
                    [
                        "🔄 Tümü",
                        "📦 Sadece Satışlar",
                        "💰 Sadece Tahsilatlar"
                    ],
                    key="toptan_islem_filtresi_temiz",
                    horizontal=True
                )

            str_tarih = secilen_tarih.strftime(
                "%Y-%m-%d"
            )

            if islem_filtresi == "📦 Sadece Satışlar":

                df_toptan_gun = run_query_df(
                    """
                    SELECT
                        id,
                        firma_adi,
                        tarih,
                        islem_turu,
                        adet,
                        birim_fiyat,
                        toplam_tutar,
                        aciklama
                    FROM toptan_satis
                    WHERE tarih=?
                      AND islem_turu='Satış'
                    ORDER BY id DESC
                    """,
                    [str_tarih]
                )

            elif islem_filtresi == "💰 Sadece Tahsilatlar":

                df_toptan_gun = run_query_df(
                    """
                    SELECT
                        id,
                        firma_adi,
                        tarih,
                        islem_turu,
                        adet,
                        birim_fiyat,
                        toplam_tutar,
                        aciklama
                    FROM toptan_satis
                    WHERE tarih=?
                      AND islem_turu='Tahsilat'
                    ORDER BY id DESC
                    """,
                    [str_tarih]
                )

            else:

                df_toptan_gun = run_query_df(
                    """
                    SELECT
                        id,
                        firma_adi,
                        tarih,
                        islem_turu,
                        adet,
                        birim_fiyat,
                        toplam_tutar,
                        aciklama
                    FROM toptan_satis
                    WHERE tarih=?
                    ORDER BY id DESC
                    """,
                    [str_tarih]
                )

            if df_toptan_gun.empty:

                st.warning(
                    f"🔍 {str_tarih} tarihinde seçilen filtreye "
                    f"uygun işlem kaydı bulunamadı."
                )

            else:

                st.success(
                    f"📌 {str_tarih} Tarihindeki Kayıtlar "
                    f"({len(df_toptan_gun)} Adet)"
                )

                st.dataframe(
                    df_toptan_gun[
                        [
                            "firma_adi",
                            "islem_turu",
                            "adet",
                            "toplam_tutar",
                            "aciklama"
                        ]
                    ],
                    use_container_width=True
                )

                toplam_adet_gun = df_toptan_gun[
                    "adet"
                ].sum()

                toplam_tutar_gun = df_toptan_gun[
                    "toplam_tutar"
                ].sum()

                col_m1, col_m2, col_m3 = st.columns(3)

                with col_m1:

                    st.metric(
                        "İşlem Adedi",
                        f"{len(df_toptan_gun)} Adet"
                    )

                with col_m2:

                    st.metric(
                        "Toplam Ürün",
                        f"{toplam_adet_gun:,} Adet"
                    )

                with col_m3:

                    st.metric(
                        "Toplam Tutar",
                        f"{toplam_tutar_gun:,.2f} TL"
                    )

                st.divider()

                st.write(
                    "**Seçilen Günkü Kaydı Düzenle / Sil**"
                )

                secilen_id_gun = st.selectbox(
                    "İşlem Seçin:",
                    options=df_toptan_gun["id"],
                    format_func=lambda x:
                        f"ID:{x} - "
                        f"{df_toptan_gun[df_toptan_gun['id'] == x]['firma_adi'].values[0]} "
                        f"("
                        f"{df_toptan_gun[df_toptan_gun['id'] == x]['islem_turu'].values[0]} "
                        f"- "
                        f"{df_toptan_gun[df_toptan_gun['id'] == x]['toplam_tutar'].values[0]} TL"
                        f")",
                    key="sec_id_gunluk"
                )

                kayit_gun = df_toptan_gun[
                    df_toptan_gun["id"] == secilen_id_gun
                ].iloc[0]

                with st.form(
                    "toptan_gun_duzenle_form_temiz"
                ):

                    e_tur = st.selectbox(
                        "İşlem Türü",
                        ["Satış", "Tahsilat"],
                        index=(
                            0
                            if kayit_gun["islem_turu"] == "Satış"
                            else 1
                        )
                    )

                    e_firma = st.selectbox(
                        "Firma Seçin",
                        firma_listesi,
                        index=(
                            firma_listesi.index(
                                kayit_gun["firma_adi"]
                            )
                            if kayit_gun["firma_adi"]
                            in firma_listesi
                            else 0
                        ),
                        key="efirma_gun"
                    )

                    e_tarih = st.date_input(
                        "Tarih",
                        datetime.strptime(
                            str(kayit_gun["tarih"]),
                            "%Y-%m-%d"
                        ),
                        key="etarih_gun"
                    )

                    if e_tur == "Satış":

                        e_adet = st.number_input(
                            "Adet",
                            min_value=0,
                            step=50,
                            value=int(
                                kayit_gun["adet"]
                            ),
                            key="eadet_gun"
                        )

                        e_birim_fiyat = st.number_input(
                            "Birim Fiyat (TL)",
                            min_value=0.0,
                            step=0.5,
                            value=float(
                                kayit_gun["birim_fiyat"]
                            ),
                            format="%.2f",
                            key="ebirim_gun"
                        )

                        e_toplam = (
                            e_adet * e_birim_fiyat
                        )

                    else:

                        e_adet = 0
                        e_birim_fiyat = 0.0

                        e_toplam = st.number_input(
                            "Tahsil Edilen Tutar (TL)",
                            min_value=0.0,
                            step=50.0,
                            value=float(
                                kayit_gun["toplam_tutar"]
                            ),
                            format="%.2f",
                            key="etahsilat_gun"
                        )

                    st.info(
                        f"Güncel Tutar: "
                        f"**{e_toplam:,.2f} TL**"
                    )

                    e_aciklama = st.text_input(
                        "Açıklama",
                        value=(
                            str(kayit_gun["aciklama"])
                            if kayit_gun["aciklama"]
                            else ""
                        ),
                        key="eaciklama_gun"
                    )

                    guncelle_g = st.form_submit_button(
                        "✏️ Güncelle",
                        type="primary"
                    )

                    sil_g = st.form_submit_button(
                        "🗑️ Sil"
                    )

                    if guncelle_g:

                        client.execute(
                            """
                            UPDATE toptan_satis
                            SET
                                firma_adi=?,
                                tarih=?,
                                islem_turu=?,
                                adet=?,
                                birim_fiyat=?,
                                toplam_tutar=?,
                                aciklama=?
                            WHERE id=?
                            """,
                            [
                                e_firma,
                                e_tarih.strftime(
                                    "%Y-%m-%d"
                                ),
                                e_tur,
                                e_adet,
                                e_birim_fiyat,
                                e_toplam,
                                e_aciklama,
                                int(secilen_id_gun)
                            ]
                        )

                        st.success(
                            "✅ Kayıt güncellendi!"
                        )

                        st.rerun()

                    if sil_g:

                        client.execute(
                            "DELETE FROM toptan_satis WHERE id=?",
                            [int(secilen_id_gun)]
                        )

                        st.warning(
                            "🗑️ Kayıt silindi!"
                        )

                        st.rerun()


        # =====================================================
        # 3. ALT SEKME: CARİ EKSTRE & PDF
        # =====================================================
        #
        # BURASI SENİN MEVCUT CARİ EKSTRE & PDF KODUNUN YERİ.
        #
        # Eğer mevcut kodunda zaten:
        #
        # with alt_sekme3:
        #
        # diye başlayan Cari Ekstre & PDF bölümü varsa,
        # ONU BURAYA AYNEN KOY.
        #
        # =====================================================


        # =====================================================
        # 4. ALT SEKME: TÜM KAYITLAR & YÖNETİM
        # =====================================================
        with alt_sekme4:

            st.subheader(
                "⚙️ Tüm Toptan Kayıtlar ve Yönetim"
            )

            # -------------------------------------------------
            # TÜM KAYITLARI ÇEK
            # -------------------------------------------------
            df_tum_kayitlar = run_query_df(
                """
                SELECT
                    id,
                    firma_adi,
                    tarih,
                    islem_turu,
                    adet,
                    birim_fiyat,
                    toplam_tutar,
                    aciklama
                FROM toptan_satis
                ORDER BY tarih DESC, id DESC
                """
            )

            if df_tum_kayitlar.empty:

                st.info(
                    "📭 Henüz hiçbir toptan işlem kaydı bulunmuyor."
                )

            else:

                # -------------------------------------------------
                # GENEL TOPLAMLAR
                # -------------------------------------------------
                toplam_satis = df_tum_kayitlar.loc[
                    df_tum_kayitlar["islem_turu"] == "Satış",
                    "toplam_tutar"
                ].sum()

                toplam_tahsilat = df_tum_kayitlar.loc[
                    df_tum_kayitlar["islem_turu"] == "Tahsilat",
                    "toplam_tutar"
                ].sum()

                toplam_adet = df_tum_kayitlar.loc[
                    df_tum_kayitlar["islem_turu"] == "Satış",
                    "adet"
                ].sum()

                kalan_bakiye = (
                    toplam_satis - toplam_tahsilat
                )

                st.success(
                    f"📌 Toplam {len(df_tum_kayitlar)} adet "
                    f"toptan işlem kaydı bulundu."
                )

                col_y1, col_y2, col_y3, col_y4 = st.columns(4)

                with col_y1:

                    st.metric(
                        "📦 Toplam Satış",
                        f"{toplam_satis:,.2f} TL"
                    )

                with col_y2:

                    st.metric(
                        "💰 Toplam Tahsilat",
                        f"{toplam_tahsilat:,.2f} TL"
                    )

                with col_y3:

                    st.metric(
                        "📦 Toplam Ürün",
                        f"{toplam_adet:,} Adet"
                    )

                with col_y4:

                    st.metric(
                        "💳 Kalan Bakiye",
                        f"{kalan_bakiye:,.2f} TL"
                    )

                st.divider()

                # -------------------------------------------------
                # FİLTRELER
                # -------------------------------------------------
                col_f1, col_f2 = st.columns(2)

                with col_f1:

                    yonetim_firma = st.selectbox(
                        "🏢 Firma Filtresi",
                        ["Tümü"] + firma_listesi,
                        key="yonetim_firma_filtresi"
                    )

                with col_f2:

                    yonetim_islem = st.selectbox(
                        "🔄 İşlem Türü",
                        [
                            "Tümü",
                            "Satış",
                            "Tahsilat"
                        ],
                        key="yonetim_islem_filtresi"
                    )

                df_yonetim = df_tum_kayitlar.copy()

                if yonetim_firma != "Tümü":

                    df_yonetim = df_yonetim[
                        df_yonetim["firma_adi"]
                        == yonetim_firma
                    ]

                if yonetim_islem != "Tümü":

                    df_yonetim = df_yonetim[
                        df_yonetim["islem_turu"]
                        == yonetim_islem
                    ]

                st.write(
                    f"**Gösterilen kayıt:** "
                    f"{len(df_yonetim)} adet"
                )

                # -------------------------------------------------
                # KAYITLAR
                # -------------------------------------------------
                if not df_yonetim.empty:

                    st.dataframe(
                        df_yonetim[
                            [
                                "id",
                                "firma_adi",
                                "tarih",
                                "islem_turu",
                                "adet",
                                "birim_fiyat",
                                "toplam_tutar",
                                "aciklama"
                            ]
                        ],
                        use_container_width=True,
                        hide_index=True
                    )

                    st.divider()

                    # -------------------------------------------------
                    # DÜZENLE / SİL
                    # -------------------------------------------------
                    st.subheader(
                        "✏️ Kayıt Düzenle / Sil"
                    )

                    secilecek_idler = (
                        df_yonetim["id"].tolist()
                    )

                    secilen_id_yonetim = st.selectbox(
                        "İşlem Seçin:",
                        secilecek_idler,
                        format_func=lambda x:
                            (
                                f"ID:{x} | "
                                f"{df_yonetim[df_yonetim['id'] == x]['firma_adi'].iloc[0]} | "
                                f"{df_yonetim[df_yonetim['id'] == x]['islem_turu'].iloc[0]} | "
                                f"{float(df_yonetim[df_yonetim['id'] == x]['toplam_tutar'].iloc[0]):,.2f} TL | "
                                f"{df_yonetim[df_yonetim['id'] == x]['tarih'].iloc[0]}"
                            ),
                        key="yonetim_secilen_id"
                    )

                    secilen_kayit = df_yonetim[
                        df_yonetim["id"]
                        == secilen_id_yonetim
                    ].iloc[0]

                    with st.form(
                        "toptan_tum_kayit_duzenle_form"
                    ):

                        e2_firma = st.selectbox(
                            "Firma",
                            firma_listesi,
                            index=(
                                firma_listesi.index(
                                    secilen_kayit[
                                        "firma_adi"
                                    ]
                                )
                                if secilen_kayit[
                                    "firma_adi"
                                ] in firma_listesi
                                else 0
                            ),
                            key="yonetim_duzenle_firma"
                        )

                        e2_tarih = st.date_input(
                            "Tarih",
                            datetime.strptime(
                                str(
                                    secilen_kayit[
                                        "tarih"
                                    ]
                                ),
                                "%Y-%m-%d"
                            ),
                            key="yonetim_duzenle_tarih"
                        )

                        e2_tur = st.selectbox(
                            "İşlem Türü",
                            [
                                "Satış",
                                "Tahsilat"
                            ],
                            index=(
                                0
                                if secilen_kayit[
                                    "islem_turu"
                                ] == "Satış"
                                else 1
                            ),
                            key="yonetim_duzenle_tur"
                        )

                        if e2_tur == "Satış":

                            e2_adet = st.number_input(
                                "Adet",
                                min_value=0,
                                step=50,
                                value=int(
                                    secilen_kayit[
                                        "adet"
                                    ]
                                ),
                                key="yonetim_duzenle_adet"
                            )

                            e2_birim = st.number_input(
                                "Birim Fiyat (TL)",
                                min_value=0.0,
                                step=0.5,
                                value=float(
                                    secilen_kayit[
                                        "birim_fiyat"
                                    ]
                                ),
                                format="%.2f",
                                key="yonetim_duzenle_birim"
                            )

                            e2_toplam = (
                                e2_adet * e2_birim
                            )

                        else:

                            e2_adet = 0
                            e2_birim = 0.0

                            e2_toplam = st.number_input(
                                "Tahsil Edilen Tutar (TL)",
                                min_value=0.0,
                                step=50.0,
                                value=float(
                                    secilen_kayit[
                                        "toplam_tutar"
                                    ]
                                ),
                                format="%.2f",
                                key="yonetim_duzenle_tahsilat"
                            )

                        st.info(
                            f"💰 Güncel Tutar: "
                            f"**{e2_toplam:,.2f} TL**"
                        )

                        e2_aciklama = st.text_input(
                            "Açıklama / Not",
                            value=(
                                str(
                                    secilen_kayit[
                                        "aciklama"
                                    ]
                                )
                                if secilen_kayit[
                                    "aciklama"
                                ]
                                else ""
                            ),
                            key="yonetim_duzenle_aciklama"
                        )

                        col_k1, col_k2 = st.columns(2)

                        with col_k1:

                            guncelle_yonetim = (
                                st.form_submit_button(
                                    "✏️ KAYDI GÜNCELLE",
                                    type="primary",
                                    use_container_width=True
                                )
                            )

                        with col_k2:

                            sil_yonetim = (
                                st.form_submit_button(
                                    "🗑️ KAYDI SİL",
                                    use_container_width=True
                                )
                            )

                        if guncelle_yonetim:

                            client.execute(
                                """
                                UPDATE toptan_satis
                                SET
                                    firma_adi=?,
                                    tarih=?,
                                    islem_turu=?,
                                    adet=?,
                                    birim_fiyat=?,
                                    toplam_tutar=?,
                                    aciklama=?
                                WHERE id=?
                                """,
                                [
                                    e2_firma,
                                    e2_tarih.strftime(
                                        "%Y-%m-%d"
                                    ),
                                    e2_tur,
                                    e2_adet,
                                    e2_birim,
                                    e2_toplam,
                                    e2_aciklama,
                                    int(
                                        secilen_id_yonetim
                                    )
                                ]
                            )

                            st.success(
                                "✅ Kayıt başarıyla güncellendi."
                            )

                            st.rerun()

                        if sil_yonetim:

                            client.execute(
                                """
                                DELETE FROM toptan_satis
                                WHERE id=?
                                """,
                                [
                                    int(
                                        secilen_id_yonetim
                                    )
                                ]
                            )

                            st.success(
                                "🗑️ Kayıt başarıyla silindi."
                            )

                            st.rerun()

                else:

                    st.warning(
                        "🔍 Seçilen filtrelere uygun kayıt bulunamadı."
                    )

# ---------------------------------------------------------
# 3. ALT SEKME: CARİ EKSTRE & PDF RAPORLAR
# ---------------------------------------------------------
with alt_sekme3:

    st.subheader("📄 Kurumsal Firma Ekstresi ve PDF Çıktısı")

    # =====================================================
    # 1. FİRMA / TARİH / EKSTRE TÜRÜ SEÇİMİ
    # =====================================================

    col_f1, col_f2, col_f3, col_f4 = st.columns([2, 1, 1, 1.5])

    with col_f1:
        secilen_firma = st.selectbox(
            "Ekstresi Alınacak Firma:",
            firma_listesi,
            key="ekstre_firma_sec_temiz"
        )

    with col_f2:
        bas_tarih = st.date_input(
            "Başlangıç",
            datetime.now().replace(day=1),
            key="toptan_bas_tarih_temiz"
        )

    with col_f3:
        bit_tarih = st.date_input(
            "Bitiş",
            datetime.now(),
            key="toptan_bit_tarih_temiz"
        )

    with col_f4:
        ekstre_tipi = st.radio(
            "Ekstre Türü",
            ["🔍 Detaylı", "📋 Özet"],
            key="toptan_ekstre_tipi_sec_temiz",
            horizontal=True
        )

    str_bas_tarih = bas_tarih.strftime("%Y-%m-%d")
    str_bit_tarih = bit_tarih.strftime("%Y-%m-%d")

    # =====================================================
    # 2. TARİH KONTROLÜ
    # =====================================================

    if bas_tarih > bit_tarih:

        st.error(
            "⚠️ Başlangıç tarihi, bitiş tarihinden büyük olamaz."
        )

    else:

        # =================================================
        # 3. SEÇİLEN TARİH ARALIĞINDAKİ HAREKETLER
        # =================================================

        df_firma_hareket = run_query_df(
            """
            SELECT
                id,
                tarih,
                islem_turu,
                adet,
                birim_fiyat,
                toplam_tutar,
                aciklama
            FROM toptan_satis
            WHERE firma_adi = ?
              AND SUBSTR(tarih, 1, 10) BETWEEN ? AND ?
            ORDER BY SUBSTR(tarih, 1, 10) ASC, id ASC
            """,
            [
                secilen_firma,
                str_bas_tarih,
                str_bit_tarih
            ]
        )

        # =================================================
        # 4. DEVİR BAKİYE VE DEVİR ADET
        # =================================================

        df_devir = run_query_df(
            """
            SELECT
                COALESCE(
                    SUM(
                        CASE
                            WHEN islem_turu = 'Satış'
                            THEN toplam_tutar
                            ELSE -toplam_tutar
                        END
                    ),
                    0
                ) AS devir_bakiye,

                COALESCE(
                    SUM(
                        CASE
                            WHEN islem_turu = 'Satış'
                            THEN adet
                            ELSE 0
                        END
                    ),
                    0
                ) AS devir_adet

            FROM toptan_satis

            WHERE firma_adi = ?
              AND SUBSTR(tarih, 1, 10) < ?
            """,
            [
                secilen_firma,
                str_bas_tarih
            ]
        )

        if not df_devir.empty:

            try:
                devir_bakiye = float(
                    df_devir.iloc[0]["devir_bakiye"] or 0
                )
            except Exception:
                devir_bakiye = 0.0

            try:
                devir_adet = int(
                    df_devir.iloc[0]["devir_adet"] or 0
                )
            except Exception:
                devir_adet = 0

        else:

            devir_bakiye = 0.0
            devir_adet = 0

        # =================================================
        # 5. HAREKET VARSA
        # =================================================

        if not df_firma_hareket.empty:

            # ---------------------------------------------
            # SAYISAL ALANLARI TEMİZLE
            # ---------------------------------------------

            df_firma_hareket["adet"] = pd.to_numeric(
                df_firma_hareket["adet"],
                errors="coerce"
            ).fillna(0)

            df_firma_hareket["birim_fiyat"] = pd.to_numeric(
                df_firma_hareket["birim_fiyat"],
                errors="coerce"
            ).fillna(0)

            df_firma_hareket["toplam_tutar"] = pd.to_numeric(
                df_firma_hareket["toplam_tutar"],
                errors="coerce"
            ).fillna(0)

            # ---------------------------------------------
            # BORÇ
            # ---------------------------------------------

            df_firma_hareket["Borç"] = df_firma_hareket.apply(
                lambda row:
                    float(row["toplam_tutar"])
                    if row["islem_turu"] == "Satış"
                    else 0.0,
                axis=1
            )

            # ---------------------------------------------
            # TAHSİLAT
            # ---------------------------------------------

            df_firma_hareket["Tahsilat"] = df_firma_hareket.apply(
                lambda row:
                    float(row["toplam_tutar"])
                    if row["islem_turu"] == "Tahsilat"
                    else 0.0,
                axis=1
            )

            # ---------------------------------------------
            # NET HAREKET
            # ---------------------------------------------

            df_firma_hareket["Net_Hareket"] = (
                df_firma_hareket["Borç"]
                - df_firma_hareket["Tahsilat"]
            )

            # ---------------------------------------------
            # KÜMÜLATİF ADET
            # ---------------------------------------------

            satis_adetleri = df_firma_hareket["adet"].where(
                df_firma_hareket["islem_turu"] == "Satış",
                0
            )

            df_firma_hareket["Kümülatif_Adet"] = (
                devir_adet
                + satis_adetleri.cumsum()
            )

            # ---------------------------------------------
            # KALAN BAKİYE
            # ---------------------------------------------

            df_firma_hareket["Kalan_Bakiye"] = (
                devir_bakiye
                + df_firma_hareket["Net_Hareket"].cumsum()
            )

            # =================================================
            # 6. TOPLAM HESAPLAR
            # =================================================

            toplam_satis = float(
                df_firma_hareket["Borç"].sum()
            )

            toplam_tahsilat = float(
                df_firma_hareket["Tahsilat"].sum()
            )

            donem_adet = int(
                df_firma_hareket.loc[
                    df_firma_hareket["islem_turu"] == "Satış",
                    "adet"
                ].sum()
            )

            toplam_adet = (
                devir_adet
                + donem_adet
            )

            bakiye = (
                devir_bakiye
                + toplam_satis
                - toplam_tahsilat
            )

            # =================================================
            # 7. EKRAN METRİKLERİ
            # =================================================

            m1, m2, m3, m4 = st.columns(4)

            with m1:
                st.metric(
                    "Toplam Satış (Borç)",
                    f"{toplam_satis:,.2f} TL"
                )

            with m2:
                st.metric(
                    "Yapılan Tahsilat",
                    f"{toplam_tahsilat:,.2f} TL"
                )

            with m3:

                if bakiye > 0:

                    st.metric(
                        "Kalan Bakiye",
                        f"{bakiye:,.2f} TL"
                    )

                elif bakiye < 0:

                    st.metric(
                        "Alacak Bakiyesi",
                        f"{abs(bakiye):,.2f} TL"
                    )

                else:

                    st.metric(
                        "Kalan Bakiye",
                        "0.00 TL"
                    )

            with m4:
                st.metric(
                    "Toplam Kümülatif Adet",
                    f"{toplam_adet:,} Adet"
                )

            # =================================================
            # 8. DEVİR BİLGİSİ
            # =================================================

            if devir_bakiye != 0 or devir_adet != 0:

                st.info(
                    f"📌 Devir Bakiye: **{devir_bakiye:,.2f} TL** "
                    f"| Devir Adet: **{devir_adet:,} Adet**"
                )

            st.markdown("---")

            # =================================================
            # 9. EKRANDA GÖSTERİLECEK TABLO
            # =================================================

            if ekstre_tipi == "🔍 Detaylı":

                df_gosterim = df_firma_hareket[
                    [
                        "tarih",
                        "islem_turu",
                        "adet",
                        "Kümülatif_Adet",
                        "birim_fiyat",
                        "toplam_tutar",
                        "Kalan_Bakiye",
                        "aciklama"
                    ]
                ].copy()

                df_gosterim.columns = [
                    "Tarih",
                    "İşlem",
                    "Adet",
                    "Kümülatif Adet",
                    "Birim Fiyat",
                    "Tutar",
                    "Kalan Bakiye",
                    "Açıklama"
                ]

            else:

                df_gosterim = df_firma_hareket[
                    [
                        "tarih",
                        "islem_turu",
                        "adet",
                        "Kümülatif_Adet",
                        "toplam_tutar",
                        "Kalan_Bakiye",
                        "aciklama"
                    ]
                ].copy()

                df_gosterim.columns = [
                    "Tarih",
                    "İşlem",
                    "Adet",
                    "Kümülatif Adet",
                    "Tutar",
                    "Kalan Bakiye",
                    "Açıklama"
                ]

            # =================================================
            # 10. EKRAN TABLOSU
            # =================================================

            st.markdown("### 📋 İşlem Geçmişi")

            st.dataframe(
                df_gosterim.iloc[::-1],
                use_container_width=True,
                hide_index=True
            )

            # =================================================
            # 11. HTML GÜVENLİĞİ
            # =================================================

            import html
            import json
            import io
            import os

            import streamlit.components.v1 as components

            firma_html = html.escape(
                str(secilen_firma)
            )

            ekstre_tipi_html = html.escape(
                str(ekstre_tipi)
            )

            # =================================================
            # 12. PDF HTML BAŞLANGICI
            # =================================================

            html_content = f"""
<!DOCTYPE html>
<html lang="tr">
<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>
MİDYECİ ABLA - CARİ HESAP EKSTRESİ
</title>

<style>

@page {{
    size: A4;
    margin: 12mm;
}}

* {{
    box-sizing: border-box;
}}

body {{
    font-family:
        Arial,
        "DejaVu Sans",
        sans-serif;

    color: #000;
    background: #fff;
    margin: 0;
    padding: 0;
}}

.rapor {{
    width: 100%;
    max-width: 100%;
    margin: 0 auto;
}}

.baslik {{
    text-align: center;
    font-size: 22px;
    font-weight: bold;
    margin-bottom: 6px;
}}

.altbaslik {{
    text-align: center;
    color: #555;
    font-size: 12px;
    margin-bottom: 15px;
}}

.bilgi {{
    font-size: 12px;
    margin-bottom: 5px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
    font-size: 10px;
}}

th {{
    background: #eeeeee;
    font-weight: bold;
}}

th,
td {{
    border: 1px solid #777;
    padding: 5px;
    vertical-align: middle;
}}

.sag {{
    text-align: right;
}}

.orta {{
    text-align: center;
}}

.bakiye {{
    font-weight: bold;
}}

.ozet {{
    width: 100%;
    margin-top: 20px;
    border-top: 2px solid #333;
    padding-top: 10px;
}}

.ozet-satir {{
    margin: 5px 0;
    font-size: 12px;
}}

.son-bakiye {{
    font-size: 16px;
    font-weight: bold;
    border-top: 1px solid #999;
    padding-top: 8px;
    margin-top: 8px;
}}

@media print {{

    body {{
        background: #fff !important;
    }}

    .rapor {{
        width: 100%;
    }}

    table {{
        page-break-inside: auto;
    }}

    tr {{
        page-break-inside: avoid;
        page-break-after: auto;
    }}

    thead {{
        display: table-header-group;
    }}

}}

</style>

</head>

<body>

<div class="rapor">

    <div class="baslik">
        MİDYECİ ABLA - CARİ HESAP EKSTRESİ
    </div>

    <div class="altbaslik">
        <b>Rapor Türü:</b>
        {ekstre_tipi_html}
    </div>

    <hr>

    <div class="bilgi">
        <b>Firma Adı:</b>
        {firma_html}
    </div>

    <div class="bilgi">
        <b>Tarih Aralığı:</b>
        {str_bas_tarih} / {str_bit_tarih}
    </div>

    <div class="bilgi">
        <b>Devir Bakiye:</b>
        {devir_bakiye:,.2f} TL
    </div>

    <table>

        <thead>

            <tr>

                <th>Tarih</th>

                <th>İşlem</th>

                <th>Adet</th>

                <th>Kümülatif Adet</th>
"""

            # =================================================
            # 13. PDF SÜTUNLARI
            # =================================================

            if ekstre_tipi == "🔍 Detaylı":

                html_content += """
                <th>Birim Fiyat</th>
"""

            html_content += """
                <th>Tutar</th>

                <th>Kalan Bakiye</th>

                <th>Açıklama</th>

            </tr>

        </thead>

        <tbody>
"""

            # =================================================
            # 14. PDF SATIRLARI
            # =================================================

            for index, row in df_firma_hareket.iterrows():

                try:
                    tarih_degeri = str(
                        row["tarih"]
                    )[:10]
                except Exception:
                    tarih_degeri = "-"

                tarih_html = html.escape(
                    tarih_degeri
                )

                islem_html = html.escape(
                    str(row["islem_turu"])
                )

                aciklama_html = (
                    html.escape(
                        str(row["aciklama"])
                    )
                    if pd.notna(row["aciklama"])
                    else "-"
                )

                try:
                    adet = int(
                        float(row["adet"])
                    )
                except Exception:
                    adet = 0

                try:
                    kumulatif_adet = int(
                        float(
                            row["Kümülatif_Adet"]
                        )
                    )
                except Exception:
                    kumulatif_adet = 0

                try:
                    birim_fiyat = float(
                        row["birim_fiyat"]
                    )
                except Exception:
                    birim_fiyat = 0.0

                try:
                    tutar = float(
                        row["toplam_tutar"]
                    )
                except Exception:
                    tutar = 0.0

                try:
                    kalan_bakiye = float(
                        row["Kalan_Bakiye"]
                    )
                except Exception:
                    kalan_bakiye = 0.0

                html_content += f"""
            <tr>

                <td>
                    {tarih_html}
                </td>

                <td>
                    {islem_html}
                </td>

                <td class="orta">
                    {adet:,}
                </td>

                <td class="orta">
                    {kumulatif_adet:,}
                </td>
"""

                if ekstre_tipi == "🔍 Detaylı":

                    html_content += f"""
                <td class="sag">
                    {birim_fiyat:,.2f} TL
                </td>
"""

                html_content += f"""
                <td class="sag">
                    {tutar:,.2f} TL
                </td>

                <td class="sag bakiye">
                    {kalan_bakiye:,.2f} TL
                </td>

                <td>
                    {aciklama_html}
                </td>

            </tr>
"""

            # =================================================
            # 15. PDF ÖZET
            # =================================================

            html_content += f"""
        </tbody>

    </table>

    <div class="ozet">

        <h3>
            📊 Ekstre Özeti
        </h3>

        <div class="ozet-satir">
            <b>Devir Bakiye:</b>
            {devir_bakiye:,.2f} TL
        </div>

        <div class="ozet-satir">
            <b>Dönem Toplam Satış:</b>
            {toplam_satis:,.2f} TL
        </div>

        <div class="ozet-satir">
            <b>Dönem Toplam Tahsilat:</b>
            {toplam_tahsilat:,.2f} TL
        </div>

        <div class="ozet-satir">
            <b>Dönem Satış Adedi:</b>
            {donem_adet:,} Adet
        </div>

        <div class="ozet-satir">
            <b>Kümülatif Toplam Adet:</b>
            {toplam_adet:,} Adet
        </div>

        <div class="son-bakiye">
            Kalan Bakiye:
            {bakiye:,.2f} TL
        </div>

    </div>

</div>

</body>
</html>
"""

            # =================================================
            # 16. ÖN İZLEME
            # =================================================

            st.markdown("---")

            st.markdown(
                "### 👁️ Ekstre Ön İzleme"
            )

            onizleme_ac = st.button(
                "👁️ Ekstreyi Ön İzle",
                use_container_width=True,
                key="cari_ekstre_onizleme"
            )

            if onizleme_ac:

                st.markdown(
                    """
                    <div style="
                        background:#ffffff;
                        color:#000000;
                        border:1px solid #cccccc;
                        border-radius:10px;
                        padding:10px;
                        margin-top:10px;
                    ">
                    """,
                    unsafe_allow_html=True
                )

                components.html(
                    html_content,
                    height=900,
                    scrolling=True
                )

                st.markdown(
                    """
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.success(
                    "✅ Ön izleme hazır. "
                    "Aşağıdaki butondan PDF'yi direkt indirebilirsin."
                )

            # =================================================
            # 17. DOĞRUDAN PDF İNDİRME
            # =================================================

            st.markdown("---")

            st.markdown(
                "### 📥 PDF İNDİR"
            )

            st.info(
                "📱 Ön izlemede gördüğün aynı firma, tarih aralığı "
                "ve hareket bilgileri PDF olarak hazırlanır."
            )

            # =================================================
            # REPORTLAB İLE PDF OLUŞTUR
            # =================================================

            try:

                from reportlab.lib import colors
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib.enums import TA_CENTER, TA_RIGHT
                from reportlab.lib.units import mm
                from reportlab.platypus import (
                    SimpleDocTemplate,
                    Paragraph,
                    Spacer,
                    Table,
                    TableStyle,
                    PageBreak
                )
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont

                               # ---------------------------------------------
                # TÜRKÇE FONT
                # ---------------------------------------------

                # Font dosyaları app.mobile.py ile aynı klasörde.
                # Böylece Streamlit Cloud sistem fontu aramaz.

                font_regular = "DejaVuSans"
                font_bold = "DejaVuSans-Bold"

                font_normal_yolu = os.path.join(
                    os.path.dirname(
                        os.path.abspath(__file__)
                    ),
                    "DejaVuSans.ttf"
                )

                font_bold_yolu = os.path.join(
                    os.path.dirname(
                        os.path.abspath(__file__)
                    ),
                    "DejaVuSans-Bold.ttf"
                )

                # ---------------------------------------------
                # FONT DOSYALARI VAR MI?
                # ---------------------------------------------

                if not os.path.exists(font_normal_yolu):

                    st.error(
                        "❌ DejaVuSans.ttf bulunamadı."
                    )

                    st.code(
                        font_normal_yolu
                    )

                    st.stop()

                if not os.path.exists(font_bold_yolu):

                    st.error(
                        "❌ DejaVuSans-Bold.ttf bulunamadı."
                    )

                    st.code(
                        font_bold_yolu
                    )

                    st.stop()

                # ---------------------------------------------
                # FONTLARI REPORTLAB'A KAYDET
                # ---------------------------------------------

                try:

                    pdfmetrics.registerFont(
                        TTFont(
                            font_regular,
                            font_normal_yolu
                        )
                    )

                    pdfmetrics.registerFont(
                        TTFont(
                            font_bold,
                            font_bold_yolu
                        )
                    )

                except Exception as font_hata:

                    st.error(
                        "❌ Türkçe PDF fontu yüklenemedi."
                    )

                    st.code(
                        str(font_hata)
                    )

                    st.stop()

                # ---------------------------------------------
                # PDF BELLEĞİ
                # ---------------------------------------------

                pdf_buffer = io.BytesIO()

                # ---------------------------------------------
                # PDF BELGESİ
                # ---------------------------------------------

                pdf_doc = SimpleDocTemplate(
                    pdf_buffer,
                    pagesize=A4,
                    rightMargin=10 * mm,
                    leftMargin=10 * mm,
                    topMargin=10 * mm,
                    bottomMargin=10 * mm,
                    title="Midyeci Abla Cari Hesap Ekstresi",
                    author="Midyeci Abla"
                )

                styles = getSampleStyleSheet()

                baslik_stil = styles["Title"].clone(
                    "BaslikStil"
                )

                baslik_stil.fontName = font_bold
                baslik_stil.fontSize = 16
                baslik_stil.leading = 19
                baslik_stil.alignment = TA_CENTER
                baslik_stil.spaceAfter = 5

                altbaslik_stil = styles["Normal"].clone(
                    "AltBaslikStil"
                )

                altbaslik_stil.fontName = font_regular
                altbaslik_stil.fontSize = 9
                altbaslik_stil.leading = 11
                altbaslik_stil.alignment = TA_CENTER
                altbaslik_stil.spaceAfter = 10

                bilgi_stil = styles["Normal"].clone(
                    "BilgiStil"
                )

                bilgi_stil.fontName = font_regular
                bilgi_stil.fontSize = 9
                bilgi_stil.leading = 12

                hucre_stil = styles["Normal"].clone(
                    "HucreStil"
                )

                hucre_stil.fontName = font_regular
                hucre_stil.fontSize = 7
                hucre_stil.leading = 9

                hucre_bold_stil = styles["Normal"].clone(
                    "HucreBoldStil"
                )

                hucre_bold_stil.fontName = font_bold
                hucre_bold_stil.fontSize = 7
                hucre_bold_stil.leading = 9

                # ---------------------------------------------
                # PDF İÇERİĞİ
                # ---------------------------------------------

                pdf_elements = []

                pdf_elements.append(
                    Paragraph(
                        "MİDYECİ ABLA - CARİ HESAP EKSTRESİ",
                        baslik_stil
                    )
                )

                pdf_elements.append(
                    Paragraph(
                        f"<b>Rapor Türü:</b> "
                        f"{html.escape(str(ekstre_tipi))}",
                        altbaslik_stil
                    )
                )

                pdf_elements.append(
                    Paragraph(
                        f"<b>Firma Adı:</b> "
                        f"{firma_html}",
                        bilgi_stil
                    )
                )

                pdf_elements.append(
                    Paragraph(
                        f"<b>Tarih Aralığı:</b> "
                        f"{str_bas_tarih} / {str_bit_tarih}",
                        bilgi_stil
                    )
                )

                pdf_elements.append(
                    Paragraph(
                        f"<b>Devir Bakiye:</b> "
                        f"{devir_bakiye:,.2f} TL",
                        bilgi_stil
                    )
                )

                pdf_elements.append(
                    Spacer(1, 8)
                )

                # ---------------------------------------------
                # PDF TABLO BAŞLIĞI
                # ---------------------------------------------

                if ekstre_tipi == "🔍 Detaylı":

                    pdf_data = [[
                        Paragraph("Tarih", hucre_bold_stil),
                        Paragraph("İşlem", hucre_bold_stil),
                        Paragraph("Adet", hucre_bold_stil),
                        Paragraph("Kümülatif Adet", hucre_bold_stil),
                        Paragraph("Birim Fiyat", hucre_bold_stil),
                        Paragraph("Tutar", hucre_bold_stil),
                        Paragraph("Kalan Bakiye", hucre_bold_stil),
                        Paragraph("Açıklama", hucre_bold_stil)
                    ]]

                else:

                    pdf_data = [[
                        Paragraph("Tarih", hucre_bold_stil),
                        Paragraph("İşlem", hucre_bold_stil),
                        Paragraph("Adet", hucre_bold_stil),
                        Paragraph("Kümülatif Adet", hucre_bold_stil),
                        Paragraph("Tutar", hucre_bold_stil),
                        Paragraph("Kalan Bakiye", hucre_bold_stil),
                        Paragraph("Açıklama", hucre_bold_stil)
                    ]]

                # ---------------------------------------------
                # PDF TABLO SATIRLARI
                # ---------------------------------------------

                for index, row in df_firma_hareket.iterrows():

                    try:
                        tarih_pdf = str(
                            row["tarih"]
                        )[:10]
                    except Exception:
                        tarih_pdf = "-"

                    try:
                        islem_pdf = html.escape(
                            str(row["islem_turu"])
                        )
                    except Exception:
                        islem_pdf = "-"

                    try:
                        adet_pdf = int(
                            float(row["adet"])
                        )
                    except Exception:
                        adet_pdf = 0

                    try:
                        kumulatif_pdf = int(
                            float(
                                row["Kümülatif_Adet"]
                            )
                        )
                    except Exception:
                        kumulatif_pdf = 0

                    try:
                        birim_pdf = float(
                            row["birim_fiyat"]
                        )
                    except Exception:
                        birim_pdf = 0.0

                    try:
                        tutar_pdf = float(
                            row["toplam_tutar"]
                        )
                    except Exception:
                        tutar_pdf = 0.0

                    try:
                        bakiye_pdf = float(
                            row["Kalan_Bakiye"]
                        )
                    except Exception:
                        bakiye_pdf = 0.0

                    if (
                        pd.isna(row["aciklama"])
                        or str(row["aciklama"]).strip() == ""
                    ):

                        aciklama_pdf = "-"

                    else:

                        aciklama_pdf = html.escape(
                            str(row["aciklama"])
                        )

                    if ekstre_tipi == "🔍 Detaylı":

                        pdf_data.append([
                            Paragraph(
                                tarih_pdf,
                                hucre_stil
                            ),
                            Paragraph(
                                islem_pdf,
                                hucre_stil
                            ),
                            Paragraph(
                                f"{adet_pdf:,}",
                                hucre_stil
                            ),
                            Paragraph(
                                f"{kumulatif_pdf:,}",
                                hucre_stil
                            ),
                            Paragraph(
                                f"{birim_pdf:,.2f} TL",
                                hucre_stil
                            ),
                            Paragraph(
                                f"{tutar_pdf:,.2f} TL",
                                hucre_stil
                            ),
                            Paragraph(
                                f"{bakiye_pdf:,.2f} TL",
                                hucre_stil
                            ),
                            Paragraph(
                                aciklama_pdf,
                                hucre_stil
                            )
                        ])

                    else:

                        pdf_data.append([
                            Paragraph(
                                tarih_pdf,
                                hucre_stil
                            ),
                            Paragraph(
                                islem_pdf,
                                hucre_stil
                            ),
                            Paragraph(
                                f"{adet_pdf:,}",
                                hucre_stil
                            ),
                            Paragraph(
                                f"{kumulatif_pdf:,}",
                                hucre_stil
                            ),
                            Paragraph(
                                f"{tutar_pdf:,.2f} TL",
                                hucre_stil
                            ),
                            Paragraph(
                                f"{bakiye_pdf:,.2f} TL",
                                hucre_stil
                            ),
                            Paragraph(
                                aciklama_pdf,
                                hucre_stil
                            )
                        ])

                # ---------------------------------------------
                # TABLO GENİŞLİĞİ
                # ---------------------------------------------

                if ekstre_tipi == "🔍 Detaylı":

                    kolon_genislikleri = [
                        22 * mm,
                        20 * mm,
                        13 * mm,
                        22 * mm,
                        24 * mm,
                        24 * mm,
                        25 * mm,
                        35 * mm
                    ]

                else:

                    kolon_genislikleri = [
                        24 * mm,
                        22 * mm,
                        15 * mm,
                        24 * mm,
                        27 * mm,
                        28 * mm,
                        45 * mm
                    ]

                pdf_tablo = Table(
                    pdf_data,
                    colWidths=kolon_genislikleri,
                    repeatRows=1,
                    splitByRow=1
                )

                pdf_tablo.setStyle(
                    TableStyle([
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor("#eeeeee")
                        ),
                        (
                            "TEXTCOLOR",
                            (0, 0),
                            (-1, 0),
                            colors.black
                        ),
                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, 0),
                            font_bold
                        ),
                        (
                            "FONTNAME",
                            (0, 1),
                            (-1, -1),
                            font_regular
                        ),
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.HexColor("#777777")
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "MIDDLE"
                        ),
                        (
                            "ALIGN",
                            (2, 1),
                            (3, -1),
                            "CENTER"
                        ),
                        (
                            "ALIGN",
                            (4, 1),
                            (-2, -1),
                            "RIGHT"
                        ),
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            3
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            3
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            3
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            3
                        )
                    ])
                )

                pdf_elements.append(
                    pdf_tablo
                )

                # ---------------------------------------------
                # PDF ÖZET
                # ---------------------------------------------

                pdf_elements.append(
                    Spacer(1, 12)
                )

                pdf_elements.append(
                    Paragraph(
                        "Ekstre Özeti",
                        hucre_bold_stil
                    )
                )

                pdf_elements.append(
                    Spacer(1, 4)
                )

                ozet_data = [
                    [
                        Paragraph(
                            "Devir Bakiye",
                            hucre_bold_stil
                        ),
                        Paragraph(
                            f"{devir_bakiye:,.2f} TL",
                            hucre_stil
                        )
                    ],
                    [
                        Paragraph(
                            "Dönem Toplam Satış",
                            hucre_bold_stil
                        ),
                        Paragraph(
                            f"{toplam_satis:,.2f} TL",
                            hucre_stil
                        )
                    ],
                    [
                        Paragraph(
                            "Dönem Toplam Tahsilat",
                            hucre_bold_stil
                        ),
                        Paragraph(
                            f"{toplam_tahsilat:,.2f} TL",
                            hucre_stil
                        )
                    ],
                    [
                        Paragraph(
                            "Dönem Satış Adedi",
                            hucre_bold_stil
                        ),
                        Paragraph(
                            f"{donem_adet:,} Adet",
                            hucre_stil
                        )
                    ],
                    [
                        Paragraph(
                            "Kümülatif Toplam Adet",
                            hucre_bold_stil
                        ),
                        Paragraph(
                            f"{toplam_adet:,} Adet",
                            hucre_stil
                        )
                    ],
                    [
                        Paragraph(
                            "Kalan Bakiye",
                            hucre_bold_stil
                        ),
                        Paragraph(
                            f"{bakiye:,.2f} TL",
                            hucre_bold_stil
                        )
                    ]
                ]

                ozet_tablo = Table(
                    ozet_data,
                    colWidths=[
                        70 * mm,
                        50 * mm
                    ]
                )

                ozet_tablo.setStyle(
                    TableStyle([
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.HexColor("#999999")
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "MIDDLE"
                        ),
                        (
                            "BACKGROUND",
                            (0, 0),
                            (0, -1),
                            colors.HexColor("#eeeeee")
                        ),
                        (
                            "ALIGN",
                            (1, 0),
                            (1, -1),
                            "RIGHT"
                        ),
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            5
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            5
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            5
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            5
                        )
                    ])
                )

                pdf_elements.append(
                    ozet_tablo
                )

                # ---------------------------------------------
                # PDF OLUŞTUR
                # ---------------------------------------------

                pdf_doc.build(
                    pdf_elements
                )

                pdf_bytes = pdf_buffer.getvalue()

                pdf_buffer.close()

                # ---------------------------------------------
                # DOSYA ADI
                # ---------------------------------------------

                temiz_firma_adi = "".join(
                    c
                    for c in str(secilen_firma)
                    if c.isalnum()
                    or c in (
                        " ",
                        "_",
                        "-"
                    )
                ).strip()

                if not temiz_firma_adi:
                    temiz_firma_adi = "Firma"

                pdf_dosya_adi = (
                    f"cari_ekstre_"
                    f"{temiz_firma_adi}_"
                    f"{str_bas_tarih}_"
                    f"{str_bit_tarih}.pdf"
                )

                # ---------------------------------------------
                # DOĞRUDAN PDF İNDİR
                # ---------------------------------------------

                st.download_button(
                    label="📥 PDF'Yİ DİREKT İNDİR",
                    data=pdf_bytes,
                    file_name=pdf_dosya_adi,
                    mime="application/pdf",
                    use_container_width=True,
                    key="cari_ekstre_pdf_indir"
                )

                st.caption(
                    "✅ Bu buton yazdırma ekranı açmaz. "
                    "PDF dosyasını doğrudan indirir."
                )

            except ImportError:

                st.error(
                    "❌ PDF modülü bulunamadı. "
                    "Lütfen requirements.txt dosyana "
                    "'reportlab' satırını ekle."
                )

            except Exception as pdf_hata:

                st.error(
                    "❌ PDF oluşturulurken hata oluştu."
                )

                st.code(
                    str(pdf_hata)
                )

               # =====================================================
        # 18. HAREKET YOKSA
        # =====================================================

        else:

            if devir_bakiye != 0 or devir_adet != 0:

                st.info(
                    f"📌 Bu tarih aralığında yeni hareket yok. "
                    f"Devir Bakiye: **{devir_bakiye:,.2f} TL** "
                    f"| Devir Adet: **{devir_adet:,} Adet**"
                )

            else:

                st.warning(
                    f"🔍 {secilen_firma} firmasına ait "
                    f"bu tarih aralığında hareket bulunamadı."
                )


# ==========================================
# 5. SEKME: BORÇ / ALACAK
# ==========================================
with tab5:

    st.subheader("💰 Borç / Alacak")

    # =====================================================
    # FİRMA BORÇ / ALACAK HESAPLAMA
    # =====================================================

    df_borc_alacak = run_query_df(
        """
        SELECT
            f.firma_adi,

            COALESCE(
                (
                    SELECT SUM(t1.toplam_tutar)
                    FROM toptan_satis t1
                    WHERE t1.firma_adi = f.firma_adi
                      AND t1.islem_turu = 'Satış'
                ),
                0
            ) AS toplam_satis,

            COALESCE(
                (
                    SELECT SUM(t2.toplam_tutar)
                    FROM toptan_satis t2
                    WHERE t2.firma_adi = f.firma_adi
                      AND t2.islem_turu = 'Tahsilat'
                ),
                0
            ) AS toplam_tahsilat

        FROM firmalar f
        ORDER BY f.firma_adi ASC
        """
    )

    if df_borc_alacak.empty:

        st.info("Henüz kayıtlı firma bulunmuyor.")

    else:

        # =====================================================
        # SAYISAL ALANLAR
        # =====================================================

        df_borc_alacak["toplam_satis"] = pd.to_numeric(
            df_borc_alacak["toplam_satis"],
            errors="coerce"
        ).fillna(0.0)

        df_borc_alacak["toplam_tahsilat"] = pd.to_numeric(
            df_borc_alacak["toplam_tahsilat"],
            errors="coerce"
        ).fillna(0.0)

        df_borc_alacak["bakiye"] = (
            df_borc_alacak["toplam_satis"]
            - df_borc_alacak["toplam_tahsilat"]
        )

        # =====================================================
        # DURUM
        # =====================================================

        def durum_belirle(bakiye):

            if bakiye > 0:
                return "BORÇLU"

            elif bakiye < 0:
                return "ALACAKLI"

            else:
                return "KAPALI"

        df_borc_alacak["durum"] = (
            df_borc_alacak["bakiye"]
            .apply(durum_belirle)
        )

        # =====================================================
        # GENEL SAYILAR
        # =====================================================

        borclu_sayisi = len(
            df_borc_alacak[
                df_borc_alacak["bakiye"] > 0
            ]
        )

        alacakli_sayisi = len(
            df_borc_alacak[
                df_borc_alacak["bakiye"] < 0
            ]
        )

        kapali_sayisi = len(
            df_borc_alacak[
                df_borc_alacak["bakiye"] == 0
            ]
        )

        genel_bakiye = (
            df_borc_alacak["bakiye"].sum()
        )

        # =====================================================
        # ÜST ÖZET
        # =====================================================

        st.markdown("### Genel Durum")

        o1, o2, o3, o4 = st.columns(4)

        with o1:
            st.metric(
                "Borçlu",
                f"{borclu_sayisi} Firma"
            )

        with o2:
            st.metric(
                "Alacaklı",
                f"{alacakli_sayisi} Firma"
            )

        with o3:
            st.metric(
                "Hesabı Kapalı",
                f"{kapali_sayisi} Firma"
            )

        with o4:
            st.metric(
                "Genel Bakiye",
                f"{genel_bakiye:,.2f} TL"
            )

        st.divider()

        # =====================================================
        # FİLTRE
        # =====================================================

        f1, f2 = st.columns([2, 5])

        with f1:

            durum_filtresi = st.selectbox(
                "Firma Durumu",
                [
                    "Tümü",
                    "Borçlular",
                    "Alacaklılar",
                    "Hesabı Kapalı"
                ],
                key="borc_alacak_firma_filtre"
            )

        # =====================================================
        # FİLTRE UYGULA
        # =====================================================

        if durum_filtresi == "Borçlular":

            df_goster = df_borc_alacak[
                df_borc_alacak["bakiye"] > 0
            ].copy()

        elif durum_filtresi == "Alacaklılar":

            df_goster = df_borc_alacak[
                df_borc_alacak["bakiye"] < 0
            ].copy()

        elif durum_filtresi == "Hesabı Kapalı":

            df_goster = df_borc_alacak[
                df_borc_alacak["bakiye"] == 0
            ].copy()

        else:

            df_goster = df_borc_alacak.copy()

        # =====================================================
        # FİRMA LİSTESİ
        # =====================================================

        st.markdown("### Firma Listesi")

        if df_goster.empty:

            st.info(
                "Bu filtreye uygun firma bulunamadı."
            )

        else:

            for _, firma in df_goster.iterrows():

                firma_adi = str(
                    firma["firma_adi"]
                )

                satis = float(
                    firma["toplam_satis"]
                )

                tahsilat = float(
                    firma["toplam_tahsilat"]
                )

                bakiye = float(
                    firma["bakiye"]
                )

                # -----------------------------------------
                # BORÇLU
                # -----------------------------------------

                if bakiye > 0:

                    durum = "🔴 BORÇLU"

                    bakiye_yazi = (
                        f"{bakiye:,.2f} TL BORÇ"
                    )

                # -----------------------------------------
                # ALACAKLI
                # -----------------------------------------

                elif bakiye < 0:

                    durum = "🟢 ALACAKLI"

                    bakiye_yazi = (
                        f"{abs(bakiye):,.2f} TL ALACAK"
                    )

                # -----------------------------------------
                # KAPALI
                # -----------------------------------------

                else:

                    durum = "⚪ KAPALI"

                    bakiye_yazi = "0,00 TL"

                # =================================================
                # FİRMA KARTI
                # =================================================

                with st.container(border=True):

                    c1, c2, c3, c4 = st.columns(
                        [3, 2, 2, 2]
                    )

                    with c1:

                        st.markdown(
                            f"**🏢 {firma_adi}**"
                        )

                        st.caption(
                            durum
                        )

                    with c2:

                        st.caption("Satış")

                        st.write(
                            f"**{satis:,.2f} TL**"
                        )

                    with c3:

                        st.caption("Tahsilat")

                        st.write(
                            f"**{tahsilat:,.2f} TL**"
                        )

                    with c4:

                        st.caption("Bakiye")

                        if bakiye > 0:

                            st.markdown(
                                f"**🔴 {bakiye_yazi}**"
                            )

                        elif bakiye < 0:

                            st.markdown(
                                f"**🟢 {bakiye_yazi}**"
                            )

                        else:

                            st.markdown(
                                f"**⚪ {bakiye_yazi}**"
                            )

        # =====================================================
        # FİRMA DETAYI
        # =====================================================

        st.divider()

        st.markdown("### 🔎 Firma Detayı")

        firma_sec = st.selectbox(
            "Firma Seçin",
            df_borc_alacak[
                "firma_adi"
            ].tolist(),
            key="borc_alacak_detay_firma"
        )

        firma_bilgi = df_borc_alacak[
            df_borc_alacak["firma_adi"] == firma_sec
        ].iloc[0]

        detay_satis = float(
            firma_bilgi["toplam_satis"]
        )

        detay_tahsilat = float(
            firma_bilgi["toplam_tahsilat"]
        )

        detay_bakiye = float(
            firma_bilgi["bakiye"]
        )

        # =====================================================
        # DETAY ÖZETİ
        # =====================================================

        d1, d2, d3 = st.columns(3)

        with d1:

            st.metric(
                "Toplam Satış",
                f"{detay_satis:,.2f} TL"
            )

        with d2:

            st.metric(
                "Toplam Tahsilat",
                f"{detay_tahsilat:,.2f} TL"
            )

        with d3:

            if detay_bakiye > 0:

                st.metric(
                    "Kalan Borç",
                    f"{detay_bakiye:,.2f} TL"
                )

            elif detay_bakiye < 0:

                st.metric(
                    "Alacak",
                    f"{abs(detay_bakiye):,.2f} TL"
                )

            else:

                st.metric(
                    "Bakiye",
                    "0,00 TL"
                )

        # =====================================================
        # İŞLEM GEÇMİŞİ
        # =====================================================

        st.markdown(
            f"#### {firma_sec} - İşlem Geçmişi"
        )

        df_firma_hareket = run_query_df(
            """
            SELECT
                id,
                tarih,
                islem_turu,
                adet,
                birim_fiyat,
                toplam_tutar,
                aciklama
            FROM toptan_satis
            WHERE firma_adi = ?
            ORDER BY tarih ASC, id ASC
            """,
            [firma_sec]
        )

        if df_firma_hareket.empty:

            st.info(
                "Bu firmaya ait işlem kaydı bulunmuyor."
            )

        else:

            df_firma_hareket[
                "toplam_tutar"
            ] = pd.to_numeric(
                df_firma_hareket["toplam_tutar"],
                errors="coerce"
            ).fillna(0.0)

            # -----------------------------------------
            # BORÇ HAREKETİ
            # -----------------------------------------

            df_firma_hareket[
                "borc_hareket"
            ] = df_firma_hareket.apply(
                lambda row:
                    float(row["toplam_tutar"])
                    if row["islem_turu"] == "Satış"
                    else 0.0,
                axis=1
            )

            # -----------------------------------------
            # TAHSİLAT HAREKETİ
            # -----------------------------------------

            df_firma_hareket[
                "tahsilat_hareket"
            ] = df_firma_hareket.apply(
                lambda row:
                    float(row["toplam_tutar"])
                    if row["islem_turu"] == "Tahsilat"
                    else 0.0,
                axis=1
            )

            # -----------------------------------------
            # KALAN BAKİYE
            # -----------------------------------------

            df_firma_hareket[
                "kalan_bakiye"
            ] = (
                df_firma_hareket["borc_hareket"]
                - df_firma_hareket["tahsilat_hareket"]
            ).cumsum()

            # -----------------------------------------
            # GÖSTERİLECEK TABLO
            # -----------------------------------------

            df_detay_goster = df_firma_hareket[
                [
                    "tarih",
                    "islem_turu",
                    "adet",
                    "birim_fiyat",
                    "toplam_tutar",
                    "kalan_bakiye",
                    "aciklama"
                ]
            ].copy()

            df_detay_goster.columns = [
                "Tarih",
                "İşlem",
                "Adet",
                "Birim Fiyat",
                "Tutar",
                "Kalan Bakiye",
                "Açıklama"
            ]

            st.dataframe(
                df_detay_goster,
                use_container_width=True,
                hide_index=True
            )

        # =====================================================
        # SON DURUM
        # =====================================================

        if detay_bakiye > 0:

            st.error(
                f"{firma_sec}: "
                f"{detay_bakiye:,.2f} TL borç bulunuyor."
            )

        elif detay_bakiye < 0:

            st.success(
                f"{firma_sec}: "
                f"{abs(detay_bakiye):,.2f} TL alacak bulunuyor."
            )

        else:

            st.info(
                f"{firma_sec}: "
                f"Hesap kapalı."
            )
