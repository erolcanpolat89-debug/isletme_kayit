import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Sayfa Ayarları (Mobil Uyumlu)
st.set_page_config(
    page_title="Midyeci Abla Canlı Takip",
    page_icon="🦪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# MODERN BACKGROUND VE BEYOĞLU / GLASSMORPHISM STİLİ (CSS)
st.markdown("""
<style>
    /* Arka Plan Degrade (Soft Gradient) */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        background-attachment: fixed;
        color: #f8fafc;
    }

    /* Genel Yazı Fontu ve Renkleri */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
    }

    /* Başlık Tasarımı */
    .custom-title {
        font-size: 26px !important;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #ff7e5f, #feb47b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
        margin-top: -10px;
        letter-spacing: 0.5px;
    }

    /* Sekme (Tabs) Butonları */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        justify-content: space-between;
        background: rgba(255, 255, 255, 0.05);
        padding: 6px;
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: nowrap;
        background-color: transparent;
        border-radius: 8px;
        padding: 6px 10px;
        font-weight: 600;
        font-size: 14px !important;
        color: #cbd5e1 !important;
        flex: 1;
        text-align: center;
        border: none !important;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ff4b4b, #dc2626) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
    }

    /* Form ve Kart Alanları (Şeffaf Buzlu Cam Etkisi - Glassmorphism) */
    div[data-testid="stForm"], div[data-testid="stExpander"] {
        background: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        padding: 18px !important;
    }

    /* Input ve Select Kutuları */
    input, select, textarea, div[data-baseweb="select"] {
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }

    /* Butonlar */
    div.stButton > button, div.stFormSubmitButton > button {
        width: 100% !important;
        height: 50px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        background: linear-gradient(135deg, #ff4b4b, #ef4444) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(239, 68, 68, 0.4);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.6);
    }

    /* Metrik Kartları */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 12px 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    div[data-testid="stMetricValue"] {
        font-size: 24px !important;
        font-weight: 800 !important;
        color: #ff6b6b !important;
    }

    /* Tablo Görünümü */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Veritabanı Bağlantısı
def get_connection():
    conn = sqlite3.connect("isletme_takip.db", check_same_thread=False)
    return conn

conn = get_connection()
cursor = conn.cursor()

# Tabloları Oluşturma
cursor.execute('''
    CREATE TABLE IF NOT EXISTS firmalar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firma_adi TEXT UNIQUE,
        telefon TEXT,
        aciklama TEXT
    )
''')

cursor.execute('''
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

cursor.execute('''
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
conn.commit()

# Veritabanı Otomatik Sütun Güncelleme
for col, dtype in [("islem_turu", "TEXT DEFAULT 'Satış'"), ("adet", "INTEGER DEFAULT 0"), ("birim_fiyat", "REAL DEFAULT 0.0")]:
    try:
        cursor.execute(f"ALTER TABLE toptan_satis ADD COLUMN {col} {dtype}")
        conn.commit()
    except sqlite3.OperationalError:
        pass

# Şık Başlık
st.markdown('<div class="custom-title">🦪 MİDYECİ ABLA CANLI TAKİP</div>', unsafe_allow_html=True)

# Sekme Sıralaması
tab1, tab2, tab3, tab4 = st.tabs(["🏪 Dükkan", "🚚 Toptan", "🏢 Firmalar", "📊 Cari Ekstre"])

bugun = datetime.now().strftime("%Y-%m-%d")

# ==========================================
# 1. SEKME: DÜKKAN CANLI SATIŞ & STOK
# ==========================================
with tab1:
    st.subheader("🏪 Dükkan Hareketleri")
    islem_turu_dukkan = st.radio("İşlem Seçin:", ["Yeni Hareket", "📅 Tarihe Göre Bul", "Tüm Kayıtları Yönet"], key="radio_dukkan", horizontal=True)

    if islem_turu_dukkan == "Yeni Hareket":
        with st.form("dukkan_form", clear_on_submit=True):
            islem_tipi = st.selectbox("İşlem Tipi", ["Günlük Satış (Gelir)", "Gider (Harcama)", "Stok Girişi"])
            tarih_d = st.date_input("Tarih", datetime.now(), key="dukkan_tarih")
            kategori = st.selectbox("Kategori", ["Midye Dolma", "Çiğ Köfte", "İçecek", "Dükkan Genel Gider", "Diğer"])
            urun_adi = st.text_input("Ürün / Detay")
            miktar = st.number_input("Miktar / Adet", min_value=1, step=1, value=1)
            birim_fiyat_d = st.number_input("Birim Fiyat (TL)", min_value=0.0, step=0.5, value=17.5, format="%.2f")
            
            toplam_d = miktar * birim_fiyat_d
            st.info(f"Hesaplanan Toplam: **{toplam_d:,.2f} TL**")
            
            kaydet_d = st.form_submit_button("💾 Hareketi Kaydet", type="primary")
            if kaydet_d:
                cursor.execute("""
                    INSERT INTO dukkan_hareket (tarih, islem_tipi, kategori, urun_adi, miktar, birim_fiyat, tutar)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (tarih_d.strftime("%Y-%m-%d"), islem_tipi, kategori, urun_adi, miktar, birim_fiyat_d, toplam_d))
                conn.commit()
                st.success("Kayıt eklendi!")
                st.rerun()

    elif islem_turu_dukkan == "📅 Tarihe Göre Bul":
        st.subheader("📅 Tarihe Göre Dükkan Kaydı Arama")
        secilen_d_tarih = st.date_input("Sorgulanacak Tarih Seçin:", datetime.now(), key="dukkan_tarih_sorgu")
        str_d_tarih = secilen_d_tarih.strftime("%Y-%m-%d")
        
        df_dukkan_gun = pd.read_sql_query("SELECT id, tarih, islem_tipi, kategori, urun_adi, miktar, birim_fiyat, tutar FROM dukkan_hareket WHERE tarih=? ORDER BY id DESC", conn, params=(str_d_tarih,))
        
        if df_dukkan_gun.empty:
            st.warning(f"🔍 {str_d_tarih} tarihine ait dükkan hareketi bulunamadı.")
        else:
            toplam_gun_ciro = df_dukkan_gun['tutar'].sum()
            st.success(f"📌 {str_d_tarih} Tarihi | Toplam Tutar: **{toplam_gun_ciro:,.2f} TL**")
            st.dataframe(df_dukkan_gun[['islem_tipi', 'kategori', 'urun_adi', 'miktar', 'tutar']], use_container_width=True)
            
            st.divider()
            st.write("**İşlem Düzenle / Sil**")
            secilen_d_id = st.selectbox("Düzenlenecek Kaydı Seçin:", 
                                       options=df_dukkan_gun["id"], 
                                       format_func=lambda x: f"ID:{x} - {df_dukkan_gun[df_dukkan_gun['id']==x]['kategori'].values[0]} ({df_dukkan_gun[df_dukkan_gun['id']==x]['tutar'].values[0]} TL)")
            
            kayit_d = df_dukkan_gun[df_dukkan_gun["id"] == secilen_d_id].iloc[0]
            kat_list = ["Midye Dolma", "Çiğ Köfte", "İçecek", "Dükkan Genel Gider", "Diğer"]
            tip_list = ["Günlük Satış (Gelir)", "Gider (Harcama)", "Stok Girişi"]
            
            with st.form("dukkan_gun_duzenle_form"):
                e_tip = st.selectbox("İşlem Tipi", tip_list, index=tip_list.index(kayit_d["islem_tipi"]) if kayit_d["islem_tipi"] in tip_list else 0)
                e_tarih_d = st.date_input("Tarih", datetime.strptime(kayit_d["tarih"], "%Y-%m-%d"))
                e_kat = st.selectbox("Kategori", kat_list, index=kat_list.index(kayit_d["kategori"]) if kayit_d["kategori"] in kat_list else 0)
                e_urun = st.text_input("Ürün / Detay", value=str(kayit_d["urun_adi"]) if kayit_d["urun_adi"] else "")
                e_m = st.number_input("Miktar", min_value=1, step=1, value=int(kayit_d["miktar"]))
                e_f = st.number_input("Birim Fiyat (TL)", min_value=0.0, step=0.5, value=float(kayit_d["birim_fiyat"]), format="%.2f")
                
                e_toplam_d = e_m * e_f
                st.info(f"Yeni Toplam: **{e_toplam_d:,.2f} TL**")
                
                guncelle_d = st.form_submit_button("✏️ Güncelle", type="primary")
                sil_d = st.form_submit_button("🗑️ Sil")
                
                if guncelle_d:
                    cursor.execute("""
                        UPDATE dukkan_hareket 
                        SET tarih=?, islem_tipi=?, kategori=?, urun_adi=?, miktar=?, birim_fiyat=?, tutar=? 
                        WHERE id=?
                    """, (e_tarih_d.strftime("%Y-%m-%d"), e_tip, e_kat, e_urun, e_m, e_f, e_toplam_d, secilen_d_id))
                    conn.commit()
                    st.success("Kayıt güncellendi!")
                    st.rerun()
                    
                if sil_d:
                    cursor.execute("DELETE FROM dukkan_hareket WHERE id=?", (secilen_d_id,))
                    conn.commit()
                    st.warning("Kayıt silindi!")
                    st.rerun()

    else:
        st.subheader("Tüm Dükkan Kayıtlarını Yönet")
        df_dukkan_all = pd.read_sql_query("SELECT id, tarih, islem_tipi, kategori, urun_adi, miktar, birim_fiyat, tutar FROM dukkan_hareket ORDER BY id DESC", conn)
        
        if not df_dukkan_all.empty:
            secilen_d_id = st.selectbox("Kayıt Seçin:", 
                                       options=df_dukkan_all["id"], 
                                       format_func=lambda x: f"ID:{x} - {df_dukkan_all[df_dukkan_all['id']==x]['tarih'].values[0]} - {df_dukkan_all[df_dukkan_all['id']==x]['kategori'].values[0]} ({df_dukkan_all[df_dukkan_all['id']==x]['tutar'].values[0]} TL)")
            
            kayit_d = df_dukkan_all[df_dukkan_all["id"] == secilen_d_id].iloc[0]
            kat_list = ["Midye Dolma", "Çiğ Köfte", "İçecek", "Dükkan Genel Gider", "Diğer"]
            tip_list = ["Günlük Satış (Gelir)", "Gider (Harcama)", "Stok Girişi"]
            
            with st.form("dukkan_duzenle_form"):
                e_tip = st.selectbox("İşlem Tipi", tip_list, index=tip_list.index(kayit_d["islem_tipi"]) if kayit_d["islem_tipi"] in tip_list else 0)
                e_tarih_d = st.date_input("Tarih", datetime.strptime(kayit_d["tarih"], "%Y-%m-%d"))
                e_kat = st.selectbox("Kategori", kat_list, index=kat_list.index(kayit_d["kategori"]) if kayit_d["kategori"] in kat_list else 0)
                e_urun = st.text_input("Ürün / Detay", value=str(kayit_d["urun_adi"]) if kayit_d["urun_adi"] else "")
                e_m = st.number_input("Miktar", min_value=1, step=1, value=int(kayit_d["miktar"]))
                e_f = st.number_input("Birim Fiyat (TL)", min_value=0.0, step=0.5, value=float(kayit_d["birim_fiyat"]), format="%.2f")
                
                e_toplam_d = e_m * e_f
                st.info(f"Yeni Toplam: **{e_toplam_d:,.2f} TL**")
                
                guncelle_d = st.form_submit_button("✏️ Güncelle", type="primary")
                sil_d = st.form_submit_button("🗑️ Sil")
                
                if guncelle_d:
                    cursor.execute("""
                        UPDATE dukkan_hareket 
                        SET tarih=?, islem_tipi=?, kategori=?, urun_adi=?, miktar=?, birim_fiyat=?, tutar=? 
                        WHERE id=?
                    """, (e_tarih_d.strftime("%Y-%m-%d"), e_tip, e_kat, e_urun, e_m, e_f, e_toplam_d, secilen_d_id))
                    conn.commit()
                    st.success("Kayıt güncellendi!")
                    st.rerun()
                    
                if sil_d:
                    cursor.execute("DELETE FROM dukkan_hareket WHERE id=?", (secilen_d_id,))
                    conn.commit()
                    st.warning("Kayıt silindi!")
                    st.rerun()

    st.divider()
    
    # Günlük Özet Kartları
    df_dukkan_bugun = pd.read_sql_query("""
        SELECT SUM(miktar) as adet, SUM(tutar) as ciro 
        FROM dukkan_hareket 
        WHERE tarih=? AND kategori='Midye Dolma' AND islem_tipi='Günlük Satış (Gelir)'
    """, conn, params=(bugun,))
    
    d_adet = df_dukkan_bugun['adet'].iloc[0] or 0
    d_ciro = df_dukkan_bugun['ciro'].iloc[0] or 0.0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Bugün Dükkan Midye", f"{int(d_adet):,} adet")
    with col2:
        st.metric("Bugün Dükkan Ciro", f"{d_ciro:,.2f} TL")
    
    st.write("**Son Dük
