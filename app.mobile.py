import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Sayfa Ayarları (Mobil Uyumlu)
st.set_page_config(page_title="MİDYECİ ABLA CANLI TAKİP", page_icon="🦪", layout="centered")

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

# EKSİK SÜTUNLARI DÜZELTME (Sütun yoksa otomatik ekler)
try:
    cursor.execute("ALTER TABLE toptan_satis ADD COLUMN islem_turu TEXT DEFAULT 'Satış'")
    conn.commit()
except sqlite3.OperationalError:
    pass # Sütun zaten varsa hata vermesini engeller

try:
    cursor.execute("ALTER TABLE toptan_satis ADD COLUMN adet INTEGER DEFAULT 0")
    conn.commit()
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("ALTER TABLE toptan_satis ADD COLUMN birim_fiyat REAL DEFAULT 0.0")
    conn.commit()
except sqlite3.OperationalError:
    pass


# Başlık
st.title("🦪 MİDYECİ ABLA CANLI TAKİP")

# Sekmeler
tab1, tab2, tab3, tab4 = st.tabs(["🏢 Firmalar", "🚚 Toptan İşlemler", "📊 İŞLEM KONTROL", "🏪 CANLI SATIŞ"])

bugun = datetime.now().strftime("%Y-%m-%d")

# ==========================================
# 1. SEKME: FİRMA YÖNETİMİ (EKLE / DÜZENLE / SİL)
# ==========================================
with tab1:
    st.header("🏢 Firma Yönetimi")
    f_islem = st.radio("Firma İşlemi Seçin:", ["Yeni Firma Ekle", "Firma Düzenle / Sil"], horizontal=True)
    
    if f_islem == "Yeni Firma Ekle":
        with st.form("yeni_firma_form", clear_on_submit=True):
            yeni_f_adi = st.text_input("Firma Ünvanı / Adı *")
            yeni_f_tel = st.text_input("Telefon No (İsteğe bağlı)")
            yeni_f_not = st.text_input("Açıklama / Not")
            
            f_kaydet = st.form_submit_button("Firmayı Kaydet", type="primary")
            if f_kaydet and yeni_f_adi:
                try:
                    cursor.execute("INSERT INTO firmalar (firma_adi, telefon, aciklama) VALUES (?, ?, ?)", 
                                   (yeni_f_adi.strip(), yeni_f_tel.strip(), yeni_f_not.strip()))
                    conn.commit()
                    st.success(f"'{yeni_f_adi.strip()}' başarıyla eklendi!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Bu firma adı zaten kayıtlı!")
                    
    else:
        df_firmalar_all = pd.read_sql_query("SELECT id, firma_adi, telefon, aciklama FROM firmalar ORDER BY firma_adi ASC", conn)
        if not df_firmalar_all.empty:
            secili_f_id = st.selectbox("Düzenlenecek / Silinecek Firmayı Seçin:", 
                                       options=df_firmalar_all["id"], 
                                       format_func=lambda x: df_firmalar_all[df_firmalar_all['id']==x]['firma_adi'].values[0])
            
            f_kayit = df_firmalar_all[df_firmalar_all["id"] == secili_f_id].iloc[0]
            
            with st.form("firma_duzenle_form"):
                e_f_adi = st.text_input("Firma Adı", value=f_kayit["firma_adi"])
                e_f_tel = st.text_input("Telefon No", value=str(f_kayit["telefon"]) if f_kayit["telefon"] else "")
                e_f_not = st.text_input("Açıklama", value=str(f_kayit["aciklama"]) if f_kayit["aciklama"] else "")
                
                c_guncelle, c_sil = st.columns(2)
                f_guncelle = c_guncelle.form_submit_button("Güncelle", type="primary")
                f_sil = c_sil.form_submit_button("Firmayı Sil")
                
                if f_guncelle:
                    cursor.execute("UPDATE firmalar SET firma_adi=?, telefon=?, aciklama=? WHERE id=?", 
                                   (e_f_adi.strip(), e_f_tel.strip(), e_f_not.strip(), secili_f_id))
                    conn.commit()
                    st.success("Firma bilgileri güncellendi!")
                    st.rerun()
                    
                if f_sil:
                    cursor.execute("DELETE FROM firmalar WHERE id=?", (secili_f_id,))
                    conn.commit()
                    st.warning("Firma silindi!")
                    st.rerun()
        else:
            st.info("Kayıtlı firma bulunmuyor.")

    st.divider()
    st.subheader("Kayıtlı Firma Listesi")
    df_f_list = pd.read_sql_query("SELECT id, firma_adi as 'Firma Adı', telefon as 'Telefon', aciklama as 'Açıklama' FROM firmalar ORDER BY firma_adi ASC", conn)
    st.dataframe(df_f_list, use_container_width=True)

# ==========================================
# 2. SEKME: TOPTAN MIDYE SATIŞ VE TAHSİLAT
# ==========================================
with tab2:
    df_firmalar_opt = pd.read_sql_query("SELECT firma_adi FROM firmalar ORDER BY firma_adi ASC", conn)
    firma_listesi = df_firmalar_opt["firma_adi"].tolist() if not df_firmalar_opt.empty else []

    if not firma_listesi:
        st.warning("⚠️ Lütfen önce 'Firmalar' sekmesinden en az bir firma ekleyin!")
    else:
        islem_turu_toptan = st.radio("İşlem Seçin:", ["Yeni İşlem (Satış / Tahsilat)", "Kayıt Düzenle / Sil"], key="radio_toptan", horizontal=True)

        if islem_turu_toptan == "Yeni İşlem (Satış / Tahsilat)":
            st.subheader("Yeni Toptan İşlem Ekle")
            with st.form("toptan_form", clear_on_submit=True):
                islem_turu = st.selectbox("İşlem Türü", ["Satış (Borç Ekle)", "Tahsilat (Borç Düş/Alacak)"])
                firma = st.selectbox("Firma Seçin", firma_listesi)
                tarih = st.date_input("Tarih", datetime.now())
                
                if islem_turu == "Satış (Borç Ekle)":
                    col_a, col_f = st.columns(2)
                    adet = col_a.number_input("Satılan Adet", min_value=1, step=50, value=100)
                    birim_fiyat = col_f.number_input("Birim Fiyat (TL)", min_value=0.0, step=0.5, value=15.0, format="%.2f")
                    toplam_tutar = adet * birim_fiyat
                    st.info(f"Hesaplanan Tutar: **{toplam_tutar:,.2f} TL**")
                else:
                    adet = 0
                    birim_fiyat = 0.0
                    toplam_tutar = st.number_input("Tahsil Edilen Tutar (TL)", min_value=0.0, step=50.0, value=1000.0, format="%.2f")
                    st.success(f"Tahsilat Tutarı: **{toplam_tutar:,.2f} TL**")

                aciklama = st.text_input("Açıklama / Not")
                
                kaydet = st.form_submit_button("İşlemi Kaydet", type="primary")
                if kaydet:
                    t_tur = "Satış" if islem_turu == "Satış (Borç Ekle)" else "Tahsilat"
                    cursor.execute("""
                        INSERT INTO toptan_satis (firma_adi, tarih, islem_turu, adet, birim_fiyat, toplam_tutar, aciklama)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (firma, tarih.strftime("%Y-%m-%d"), t_tur, adet, birim_fiyat, toplam_tutar, aciklama))
                    conn.commit()
                    st.success(f"{t_tur} işlemi başarıyla kaydedildi!")
                    st.rerun()

        else:
            st.subheader("Toptan Kayıt Düzenle / Sil")
            df_toptan_all = pd.read_sql_query("SELECT id, firma_adi, tarih, islem_turu, adet, birim_fiyat, toplam_tutar, aciklama FROM toptan_satis ORDER BY id DESC", conn)
            
            if not df_toptan_all.empty:
                secilen_id = st.selectbox(
                    "Kayıt Seçin:", 
                    options=df_toptan_all["id"], 
                    format_func=lambda x: f"ID: {x} - {df_toptan_all[df_toptan_all['id']==x]['firma_adi'].values[0]} | {df_toptan_all[df_toptan_all['id']==x]['islem_turu'].values[0]} | {df_toptan_all[df_toptan_all['id']==x]['toplam_tutar'].values[0]} TL"
                )
                
                kayit = df_toptan_all[df_toptan_all["id"] == secilen_id].iloc[0]
                
                with st.form("toptan_duzenle_form"):
                    e_tur = st.selectbox("İşlem Türü", ["Satış", "Tahsilat"], index=0 if kayit["islem_turu"] == "Satış" else 1)
                    e_firma = st.selectbox("Firma Seçin", firma_listesi, index=firma_listesi.index(kayit["firma_adi"]) if kayit["firma_adi"] in firma_listesi else 0)
                    e_tarih = st.date_input("Tarih", datetime.strptime(kayit["tarih"], "%Y-%m-%d"))
                    
                    if e_tur == "Satış":
                        e_adet = st.number_input("Satılan Adet", min_value=0, step=50, value=int(kayit["adet"]))
                        e_birim_fiyat = st.number_input("Birim Fiyat (TL)", min_value=0.0, step=0.5, value=float(kayit["birim_fiyat"]), format="%.2f")
                        e_toplam = e_adet * e_birim_fiyat
                    else:
                        e_adet = 0
                        e_birim_fiyat = 0.0
                        e_toplam = st.number_input("Tahsil Edilen Tutar (TL)", min_value=0.0, step=50.0, value=float(kayit["toplam_tutar"]), format="%.2f")

                    st.info(f"Yeniden Hesaplanan Tutar: **{e_toplam:,.2f} TL**")
                    e_aciklama = st.text_input("Açıklama / Not", value=str(kayit["aciklama"]) if kayit["aciklama"] else "")
                    
                    col_guncelle, col_sil = st.columns(2)
                    guncelle = col_guncelle.form_submit_button("Güncelle", type="primary")
                    sil = col_sil.form_submit_button("Kaydı Sil")
                    
                    if guncelle:
                        cursor.execute("""
                            UPDATE toptan_satis 
                            SET firma_adi=?, tarih=?, islem_turu=?, adet=?, birim_fiyat=?, toplam_tutar=?, aciklama=? 
                            WHERE id=?
                        """, (e_firma, e_tarih.strftime("%Y-%m-%d"), e_tur, e_adet, e_birim_fiyat, e_toplam, e_aciklama, secilen_id))
                        conn.commit()
                        st.success("Kayıt güncellendi!")
                        st.rerun()
                        
                    if sil:
                        cursor.execute("DELETE FROM toptan_satis WHERE id=?", (secilen_id,))
                        conn.commit()
                        st.warning("Kayıt silindi!")
                        st.rerun()
            else:
                st.info("Kayıt bulunamadı.")

        st.divider()
        st.subheader("Son Toptan İşlem Kayıtları")
        df_toptan_view = pd.read_sql_query("SELECT id, firma_adi, tarih, islem_turu, adet, birim_fiyat, toplam_tutar, aciklama FROM toptan_satis ORDER BY id DESC", conn)
        st.dataframe(df_toptan_view, use_container_width=True)

# ==========================================
# 3. SEKME: FİRMA SEÇİMLİ CARİ EKSTRE & DETAY
# ==========================================
with tab3:
    st.header("📊 Firma Cari Hesap Ekstresi")
    
    df_firmalar_cari = pd.read_sql_query("SELECT firma_adi FROM firmalar ORDER BY firma_adi ASC", conn)
    
    if not df_firmalar_cari.empty:
        firmalar_list = df_firmalar_cari["firma_adi"].tolist()
        
        secili_firma_detay = st.selectbox("🔍 Detaylarını Görmek İstediğiniz Firmayı Seçin:", firmalar_list)
        
        if secili_firma_detay:
            st.divider()
            st.subheader(f"📌 {secili_firma_detay} - Hesap Özeti")
            
            df_f_satis = pd.read_sql_query(f"SELECT SUM(toplam_tutar) as t FROM toptan_satis WHERE firma_adi='{secili_firma_detay}' AND islem_turu='Satış'", conn)
            df_f_tahsilat = pd.read_sql_query(f"SELECT SUM(toplam_tutar) as t FROM toptan_satis WHERE firma_adi='{secili_firma_detay}' AND islem_turu='Tahsilat'", conn)
            
            tot_satis = df_f_satis['t'].iloc[0] or 0.0
            tot_tahsilat = df_f_tahsilat['t'].iloc[0] or 0.0
            net_bakiye = tot_satis - tot_tahsilat
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Toplam Satış", f"{tot_satis:,.2f} TL")
            m2.metric("Toplam Tahsilat", f"{tot_tahsilat:,.2f} TL")
            
            if net_bakiye > 0:
                m3.metric("Kalan Borç", f"{net_bakiye:,.2f} TL", delta="- Borçlu", delta_color="inverse")
            elif net_bakiye < 0:
                m3.metric("Alacak Bakiyesi", f"{abs(net_bakiye):,.2f} TL", delta="+ Alacaklı", delta_color="normal")
            else:
                m3.metric("Net Bakiye", "0.00 TL", delta="Dengede")
                
            st.subheader("🧾 İşlem Geçmişi (Ekstre)")
            df_ekstre = pd.read_sql_query(f"""
                SELECT tarih as 'Tarih', islem_turu as 'İşlem', adet as 'Adet', birim_fiyat as 'Birim Fiyat', toplam_tutar as 'Tutar (TL)', aciklama as 'Açıklama' 
                FROM toptan_satis 
                WHERE firma_adi='{secili_firma_detay}' 
                ORDER BY id ASC
            """, conn)
            
            if not df_ekstre.empty:
                st.dataframe(df_ekstre, use_container_width=True)
            else:
                st.info("Bu firmaya ait henüz işlem hareketi bulunmuyor.")
    else:
        st.info("Henüz sistemde kayıtlı firma bulunmuyor.")

# ==========================================
# 4. SEKME: DÜKKAN GELİR / GİDER & STOK
# ==========================================
with tab4:
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
            secilen_d_id = st.selectbox("Düzenlenecek Kaydı Seçin:", 
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