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
    islem_turu_toptan = st.radio("İşlem Seçin:", ["Yeni Satış Ekle", "Kayıt Düzenle / Sil"], key="radio_toptan", horizontal=True)

    if islem_turu_toptan == "Yeni Satış Ekle":
        st.subheader("Toptan Satış Ekle")
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
                st.rerun()

    else:
        st.subheader("Toptan Kayıt Düzenle / Sil")
        df_toptan_all = pd.read_sql_query("SELECT id, firma_adi, tarih, adet, birim_fiyat, toplam_tutar, aciklama FROM toptan_satis ORDER BY id DESC", conn)
        
        if not df_toptan_all.empty:
            secilen_id = st.selectbox("Düzenlenecek / Silinecek Kaydı Seçin (ID - Firma):", 
                                     options=df_toptan_all["id"], 
                                     format_func=lambda x: f"ID: {x} - {df_toptan_all[df_toptan_all['id']==x]['firma_adi'].values[0]} ({df_toptan_all[df_toptan_all['id']==x]['tarih'].values[0]})")
            
            kayit = df_toptan_all[df_toptan_all["id"] == secilen_id].iloc[0]
            
            with st.form("toptan_duzenle_form"):
                e_firma = st.text_input("Firma Adı", value=kayit["firma_adi"])
                e_tarih = st.date_input("Tarih", datetime.strptime(kayit["tarih"], "%Y-%m-%d"))
                e_adet = st.number_input("Satılan Adet", min_value=1, step=50, value=int(kayit["adet"]))
                e_birim_fiyat = st.number_input("Birim Fiyat (TL)", min_value=0.0, step=0.5, value=float(kayit["birim_fiyat"]), format="%.2f")
                e_aciklama = st.text_input("Açıklama / Not", value=str(kayit["aciklama"]) if kayit["aciklama"] else "")
                
                e_toplam = e_adet * e_birim_fiyat
                st.info(f"Hesaplanan Yeni Toplam: **{e_toplam:,.2f} TL**")
                
                col_guncelle, col_sil = st.columns(2)
                guncelle = col_guncelle.form_submit_button("Güncelle", type="primary")
                sil = col_sil.form_submit_button("Kaydı Sil")
                
                if guncelle:
                    cursor.execute("""
                        UPDATE toptan_satis 
                        SET firma_adi=?, tarih=?, adet=?, birim_fiyat=?, toplam_tutar=?, aciklama=? 
                        WHERE id=?
                    """, (e_firma, e_tarih.strftime("%Y-%m-%d"), e_adet, e_birim_fiyat, e_toplam, e_aciklama, secilen_id))
                    conn.commit()
                    st.success("Kayıt güncellendi!")
                    st.rerun()
                    
                if sil:
                    cursor.execute("DELETE FROM toptan_satis WHERE id=?", (secilen_id,))
                    conn.commit()
                    st.warning("Kayıt silindi!")
                    st.rerun()
        else:
            st.info("Düzenlenecek kayıt bulunamadı.")

    st.divider()
    
    # Günlük Özet
    df_toptan_bugun = pd.read_sql_query(f"SELECT SUM(adet) as toplam_adet, SUM(toplam_tutar) as toplam_ciro FROM toptan_satis WHERE tarih='{bugun}'", conn)
    t_adet = df_toptan_bugun['toplam_adet'].iloc[0] or 0
    t_ciro = df_toptan_bugun['toplam_ciro'].iloc[0] or 0.0
    
    col1, col2 = st.columns(2)
    col1.metric("Bugün Toptan Adet", f"{int(t_adet):,} adet")
    col2.metric("Bugün Toptan Ciro", f"{t_ciro:,.2f} TL")
    
    st.subheader("Geçmiş Toptan Satış Kayıtları")
    df_toptan_view = pd.read_sql_query("SELECT id, firma_adi, tarih, adet, birim_fiyat, toplam_tutar FROM toptan_satis ORDER BY id DESC", conn)
    st.dataframe(df_toptan_view, use_container_width=True)

# ==========================================
# 2. SEKME: DÜKKAN GELİR / GİDER & STOK
# ==========================================
with tab2:
    islem_turu_dukkan = st.radio("İşlem Seçin:", ["Yeni Hareket Ekle", "Kayıt Düzenle / Sil"], key="radio_dukkan", horizontal=True)

    if islem_turu_dukkan == "Yeni Hareket Ekle":
        st.subheader("Dükkan Hareketi Ekle")
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
                st.rerun()

    else:
        st.subheader("Dükkan Kaydı Düzenle / Sil")
        df_dukkan_all = pd.read_sql_query("SELECT id, tarih, islem_tipi, kategori, urun_adi, miktar, birim_fiyat, tutar FROM dukkan_hareket ORDER BY id DESC", conn)
        
        if not df_dukkan_all.empty:
            secilen_d_id = st.selectbox("Düzenlenecek / Silinecek Kaydı Seçin:", 
                                       options=df_dukkan_all["id"], 
                                       format_func=lambda x: f"ID: {x} - {df_dukkan_all[df_dukkan_all['id']==x]['kategori'].values[0]} ({df_dukkan_all[df_dukkan_all['id']==x]['tarih'].values[0]})")
            
            kayit_d = df_dukkan_all[df_dukkan_all["id"] == secilen_d_id].iloc[0]
            
            kat_list = ["Midye Dolma", "Çiğ Köfte", "İçecek", "Dükkan Genel Gider", "Diğer"]
            tip_list = ["Günlük Satış (Gelir)", "Gider (Harcama)", "Stok Girişi"]
            
            with st.form("dukkan_duzenle_form"):
                e_tip = st.selectbox("İşlem Tipi", tip_list, index=tip_list.index(kayit_d["islem_tipi"]) if kayit_d["islem_tipi"] in tip_list else 0)
                e_tarih_d = st.date_input("Tarih", datetime.strptime(kayit_d["tarih"], "%Y-%m-%d"))
                e_kat = st.selectbox("Kategori", kat_list, index=kat_list.index(kayit_d["kategori"]) if kayit_d["kategori"] in kat_list else 0)
                e_urun = st.text_input("Ürün Adı / Detay", value=str(kayit_d["urun_adi"]) if kayit_d["urun_adi"] else "")
                e_m = st.number_input("Miktar / Adet", min_value=1, step=1, value=int(kayit_d["miktar"]))
                e_f = st.number_input("Birim Fiyat (TL)", min_value=0.0, step=0.5, value=float(kayit_d["birim_fiyat"]), format="%.2f")
                
                e_toplam_d = e_m * e_f
                st.info(f"Hesaplanan Yeni Toplam: **{e_toplam_d:,.2f} TL**")
                
                col_guncelle_d, col_sil_d = st.columns(2)
                guncelle_d = col_guncelle_d.form_submit_button("Güncelle", type="primary")
                sil_d = col_sil_d.form_submit_button("Kaydı Sil")
                
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
            st.info("Düzenlenecek kayıt bulunamadı.")

    st.divider()
    
    # Günlük Özet
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
    df_dukkan_view = pd.read_sql_query("SELECT id, tarih, islem_tipi, kategori, urun_adi, miktar, birim_fiyat, tutar FROM dukkan_hareket ORDER BY id DESC", conn)
    st.dataframe(df_dukkan_view, use_container_width=True)