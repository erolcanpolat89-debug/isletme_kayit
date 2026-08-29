import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Sayfa Ayarları (Mobil Uyumlu)
st.set_page_config(page_title="İşletme Takip", page_icon="🦪", layout="centered")

# Veritabanı Bağlantısı
def get_connection():
    conn = sqlite3.connect("isletme_takip.db", check_same_thread=False)
    return conn

conn = get_connection()
cursor = conn.cursor()

# Tablo Oluşturma
cursor.execute('''
    CREATE TABLE IF NOT EXISTS toptan_satis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firma_adi TEXT,
        tarih TEXT,
        adet INTEGER,
        birim_fiyat REAL,
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

# Başlık
st.title("🦪 İşletme Takip Otomasyonu")

# Sekmeler
tab1, tab2 = st.tabs(["🚚 Toptan Midye", "🏪 Dükkan / Stok"])

bugun = datetime.now().strftime("%Y-%m-%d")

# ==========================================
# 1. SEKME: TOPTAN MIDYE SATIŞLARI
# ==========================================
with tab1:
    st.header("Toptan Satış Ekle")
    
    with st.form("toptan_form", clear_on_submit=True):
        firma = st.text_input("Firma Adı")
        tarih = st.date_input("Tarih", datetime.now())
        adet = st.number_input("Satılan Adet", min_value=1, step=50, value=100)
        birim_fiyat = st.number_input("Birim Fiyat (TL)", min_value=0.0, step=0.5, value=15.0, format="%.2f")
        aciklama = st.text_input("Açıklama / Not")
        
        toplam_tutar = adet * birim_fiyat
        st.info(f"Hesaplanan Toplam: **{toplam_tutar:,.2f} TL**")
        
        kaydet = st.form_submit_button("Satışı Kaydet", type="primary")
        if kaydet and firma:
            cursor.execute("""
                INSERT INTO toptan_satis (firma_adi, tarih, adet, birim_fiyat, toplam_tutar, aciklama)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (firma, tarih.strftime("%Y-%m-%d"), adet, birim_fiyat, toplam_tutar, aciklama))
            conn.commit()
            st.success("Toptan satış kaydedildi!")

    st.divider()
    
    # Günlük Özet Kutusu
    df_toptan_bugun = pd.read_sql_query(f"SELECT SUM(adet) as toplam_adet, SUM(toplam_tutar) as toplam_ciro FROM toptan_satis WHERE tarih='{bugun}'", conn)
    t_adet = df_toptan_bugun['toplam_adet'].iloc[0] or 0
    t_ciro = df_toptan_bugun['toplam_ciro'].iloc[0] or 0.0
    
    col1, col2 = st.columns(2)
    col1.metric("Bugün Toptan Adet", f"{int(t_adet):,} adet")
    col2.metric("Bugün Toptan Ciro", f"{t_ciro:,.2f} TL")
    
    st.subheader("Geçmiş Satış Kayıtları")
    df_toptan = pd.read_sql_query("SELECT id, firma_adi, tarih, adet, birim_fiyat, toplam_tutar FROM toptan_satis ORDER BY id DESC", conn)
    st.dataframe(df_toptan, use_container_width=True)

# ==========================================
# 2. SEKME: DÜKKAN GELİR / GİDER & STOK
# ==========================================
with tab2:
    st.header("Dükkan Hareketi Ekle")
    
    with st.form("dukkan_form", clear_on_submit=True):
        islem_tipi = st.selectbox("İşlem Tipi", ["Günlük Satış (Gelir)", "Gider (Harcama)", "Stok Girişi"])
        tarih_d = st.date_input("Tarih", datetime.now(), key="dukkan_tarih")
        kategori = st.selectbox("Kategori", ["Midye Dolma", "Çiğ Köfte", "İçecek", "Dükkan Genel Gider", "Diğer"])
        urun_adi = st.text_input("Ürün Adı / Detay")
        miktar = st.number_input("Miktar / Adet", min_value=1, step=1, value=1)
        birim_fiyat_d = st.number_input("Birim Fiyat (TL)", min_value=0.0, step=0.5, value=17.5, format="%.2f")
        
        toplam_d = miktar * birim_fiyat_d
        st.info(f"Hesaplanan Toplam: **{toplam_d:,.2f} TL**")
        
        kaydet_d = st.form_submit_button("Hareketi Kaydet", type="primary")
        if kaydet_d:
            cursor.execute("""
                INSERT INTO dukkan_hareket (tarih, islem_tipi, kategori, urun_adi, miktar, birim_fiyat, tutar)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tarih_d.strftime("%Y-%m-%d"), islem_tipi, kategori, urun_adi, miktar, birim_fiyat_d, toplam_d))
            conn.commit()
            st.success("Dükkan hareketi kaydedildi!")

    st.divider()
    
    # Günlük Dükkan Midye Özeti
    df_dukkan_bugun = pd.read_sql_query(f"""
        SELECT SUM(miktar) as adet, SUM(tutar) as ciro 
        FROM dukkan_hareket 
        WHERE tarih='{bugun}' AND kategori='Midye Dolma' AND islem_tipi='Günlük Satış (Gelir)'
    """, conn)
    d_adet = df_dukkan_bugun['adet'].iloc[0] or 0
    d_ciro = df_dukkan_bugun['ciro'].iloc[0] or 0.0
    
    c1, c2 = st.columns(2)
    c1.metric("Bugün Dükkan Midye", f"{int(d_adet):,} adet")
    c2.metric("Bugün Dükkan Ciro", f"{d_ciro:,.2f} TL")
    
    st.subheader("Dükkan Kayıtları")
    df_dukkan = pd.read_sql_query("SELECT id, tarih, islem_tipi, kategori, urun_adi, miktar, birim_fiyat, tutar FROM dukkan_hareket ORDER BY id DESC", conn)
    st.dataframe(df_dukkan, use_container_width=True)