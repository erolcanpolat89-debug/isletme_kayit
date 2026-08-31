import streamlit as st
import pandas as pd
from datetime import datetime
import libsql_client as libsql
import io

# Sayfa Ayarları
st.set_page_config(
    page_title="Midyeci Abla Canlı Takip",
    page_icon="🦪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Koyu Tema & Tarih / Detay Kutusu Metin Rengi Düzeltmesi
st.markdown("""
<style>
    /* Arka Plan Degrade */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        background-attachment: fixed;
    }

    /* TÜM ETIKETLER VE BAŞLIKLAR (Beyaz ve Kalın) */
    .stApp, .stApp p, .stApp label, .stApp span, 
    div[data-testid="stMarkdownContainer"] p, 
    label[data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }

    /* Radio (Seçenek) Buton Metinleri */
    div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
    }

    /* TARİH, DETAY VE TÜM INPUT KUTULARININ İÇİ (Koyu Siyah Yazı) */
    div[data-baseweb="input"] input, 
    div[data-baseweb="base-input"] input,
    div[data-testid="stTextInput"] input,
    div[data-testid="stDateInput"] input,
    input[type="text"], 
    input[type="number"] {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 800 !important;
        background-color: #ffffff !important;
        opacity: 1 !important;
    }

    /* Kutuların Arka Planı (Tam Beyaz) */
    div[data-baseweb="input"], 
    div[data-baseweb="base-input"],
    div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border-radius: 10px !important;
    }

    /* Selectbox (Açılır Menü) Seçilen Yazı Rengi */
    div[data-baseweb="select"] div {
        color: #000000 !important;
        font-weight: 800 !important;
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
    }

    /* Sekme (Tabs) Butonları */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(255, 255, 255, 0.08);
        padding: 4px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        padding: 6px 10px;
        font-weight: 600;
        color: #cbd5e1 !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ff4b4b, #dc2626) !important;
        color: #ffffff !important;
    }

    /* Glassmorphic Kutu Alanları */
    div[data-testid="stForm"], div[data-testid="stExpander"] {
        background: rgba(30, 41, 59, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        padding: 18px !important;
    }

    /* Kaydet Butonları */
    div.stButton > button, div.stFormSubmitButton > button, div.stDownloadButton > button {
        width: 100% !important;
        height: 50px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        background: linear-gradient(135deg, #ff4b4b, #ef4444) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(239, 68, 68, 0.4);
    }

    /* Metrik Kartları */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 12px 16px;
    }

    div[data-testid="stMetricValue"] {
        font-size: 24px !important;
        font-weight: 800 !important;
        color: #ff6b6b !important;
    }

    div[data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
    }
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

# Otomatik Sütun Güncelleme Kontrolü
for col, dtype in [("islem_turu", "TEXT DEFAULT 'Satış'"), ("adet", "INTEGER DEFAULT 0"), ("birim_fiyat", "REAL DEFAULT 0.0")]:
    try:
        client.execute(f"ALTER TABLE toptan_satis ADD COLUMN {col} {dtype}")
    except Exception:
        pass

# Başlık
st.markdown('<div class="custom-title">🦪 MİDYECİ ABLA CANLI TAKİP</div>', unsafe_allow_html=True)

# Sekmeler
tab1, tab2, tab3, tab4 = st.tabs(["🏪 Dükkan", "🚚 Toptan", "🏢 Firmalar", "📊 Cari Ekstre"])

bugun = datetime.now().strftime("%Y-%m-%d")

# ==========================================
# 1. SEKME: DÜKKAN
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
                client.execute("""
                    INSERT INTO dukkan_hareket (tarih, islem_tipi, kategori, urun_adi, miktar, birim_fiyat, tutar)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, [tarih_d.strftime("%Y-%m-%d"), islem_tipi, kategori, urun_adi, miktar, birim_fiyat_d, toplam_d])
                st.success("Kayıt eklendi!")
                st.rerun()

    elif islem_turu_dukkan == "📅 Tarihe Göre Bul":
        st.subheader("📅 Tarihe Göre Dükkan Kaydı Arama")
        secilen_d_tarih = st.date_input("Sorgulanacak Tarih Seçin:", datetime.now(), key="dukkan_tarih_sorgu")
        str_d_tarih = secilen_d_tarih.strftime("%Y-%m-%d")
        
        df_dukkan_gun = run_query_df("SELECT id, tarih, islem_tipi, kategori, urun_adi, miktar, birim_fiyat, tutar FROM dukkan_hareket WHERE tarih=? ORDER BY id DESC", [str_d_tarih])
        
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
    df_dukkan_bugun = run_query_df("""
        SELECT SUM(miktar) as adet, SUM(tutar) as ciro 
        FROM dukkan_hareket 
        WHERE tarih=? AND kategori='Midye Dolma' AND islem_tipi='Günlük Satış (Gelir)'
    """, [bugun])
    
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
# 2. SEKME: TOPTAN
# ==========================================
with tab2:
    df_firmalar_opt = run_query_df("SELECT firma_adi FROM firmalar ORDER BY firma_adi ASC")
    firma_listesi = df_firmalar_opt["firma_adi"].tolist() if not df_firmalar_opt.empty else []

    if not firma_listesi:
        st.warning("⚠️ Lütfen önce 'Firmalar' sekmesinden bir firma ekleyin!")
    else:
        islem_turu_toptan = st.radio("İşlem Türü Seçin:", ["Yeni İşlem", "📅 Tarihe Göre Bul", "Tüm Kayıtları Yönet"], key="radio_toptan", horizontal=True)

        if islem_turu_toptan == "Yeni İşlem":
            st.subheader("Yeni Toptan İşlem")
            islem_turu = st.selectbox("İşlem Tipi", ["Satış (Borç Ekle)", "Tahsilat (Borç Düş/Alacak)"], key="toptan_islem_tipi_select")

            with st.form("toptan_form", clear_on_submit=True):
                firma = st.selectbox("Firma Seçin", firma_listesi)
                tarih = st.date_input("Tarih", datetime.now())
                
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
                    """, [firma, tarih.strftime("%Y-%m-%d"), t_tur, adet, birim_fiyat, toplam_tutar, aciklama])
                    st.success(f"{t_tur} kaydedildi!")
                    st.rerun()

        elif islem_turu_toptan == "📅 Tarihe Göre Bul":
            st.subheader("📅 Tarihe Göre Toptan İşlem Arama")
            secilen_tarih = st.date_input("Sorgulanacak Tarih Seçin:", datetime.now(), key="toptan_tarih_sorgu")
            str_tarih = secilen_tarih.strftime("%Y-%m-%d")
            
            df_toptan_gun = run_query_df("SELECT id, firma_adi, tarih, islem_turu, adet, birim_fiyat, toplam_tutar, aciklama FROM toptan_satis WHERE tarih=? ORDER BY id DESC", [str_tarih])
            
            if df_toptan_gun.empty:
                st.warning(f"🔍 {str_tarih} tarihine ait toptan işlem kaydı bulunamadı.")
            else:
                st.success(f"📌 {str_tarih} Tarihindeki Kayıtlar ({len(df_toptan_gun)} Adet)")
                st.dataframe(df_toptan_gun[['firma_adi', 'islem_turu', 'adet', 'toplam_tutar', 'aciklama']], use_container_width=True)
                
                st.divider()
                st.write("**İşlem Düzenle / Sil**")
                secilen_id = st.selectbox(
                    "Düzenlenecek Kaydı Seçin:", 
                    options=df_toptan_gun["id"], 
                    format_func=lambda x: f"ID:{x} - {df_toptan_gun[df_toptan_gun['id']==x]['firma_adi'].values[0]} ({df_toptan_gun[df_toptan_gun['id']==x]['toplam_tutar'].values[0]} TL)"
                )
                
                kayit = df_toptan_gun[df_toptan_gun["id"] == secilen_id].iloc[0]
                
                with st.form("toptan_gun_duzenle_form"):
                    e_tur = st.selectbox("İşlem Türü", ["Satış", "Tahsilat"], index=0 if kayit["islem_turu"] == "Satış" else 1)
                    e_firma = st.selectbox("Firma Seçin", firma_listesi, index=firma_listesi.index(kayit["firma_adi"]) if kayit["firma_adi"] in firma_listesi else 0)
                    e_tarih = st.date_input("Tarih", datetime.strptime(str(kayit["tarih"]), "%Y-%m-%d"))
                    
                    if e_tur == "Satış":
                        e_adet = st.number_input("Adet", min_value=0, step=50, value=int(kayit["adet"]))
                        e_birim_fiyat = st.number_input("Birim Fiyat (TL)", min_value=0.0, step=0.5, value=float(kayit["birim_fiyat"]), format="%.2f")
                        e_toplam = e_adet * e_birim_fiyat
                    else:
                        e_adet = 0
                        e_birim_fiyat = 0.0
                        e_toplam = st.number_input("Tahsil Edilen Tutar (TL)", min_value=0.0, step=50.0, value=float(kayit["toplam_tutar"]), format="%.2f")

                    st.info(f"Tutar: **{e_toplam:,.2f} TL**")
                    e_aciklama = st.text_input("Açıklama", value=str(kayit["aciklama"]) if kayit["aciklama"] else "")
                    
                    guncelle = st.form_submit_button("✏️ Güncelle", type="primary")
                    sil = st.form_submit_button("🗑️ Sil")
                    
                    if guncelle:
                        client.execute("""
                            UPDATE toptan_satis 
                            SET firma_adi=?, tarih=?, islem_turu=?, adet=?, birim_fiyat=?, toplam_tutar=?, aciklama=? 
                            WHERE id=?
                        """, [e_firma, e_tarih.strftime("%Y-%m-%d"), e_tur, e_adet, e_birim_fiyat, e_toplam, e_aciklama, int(secilen_id)])
                        st.success("Kayıt güncellendi!")
                        st.rerun()
                        
                    if sil:
                        client.execute("DELETE FROM toptan_satis WHERE id=?", [int(secilen_id)])
                        st.warning("Kayıt silindi!")
                        st.rerun()

        else:
            st.subheader("Tüm Toptan Kayıtlarını Yönet")
            df_toptan_all = run_query_df("SELECT id, firma_adi, tarih, islem_turu, adet, birim_fiyat, toplam_tutar, aciklama FROM toptan_satis ORDER BY id DESC")
            
            if not df_toptan_all.empty:
                secilen_id = st.selectbox(
                    "Kayıt Seçin:", 
                    options=df_toptan_all["id"], 
                    format_func=lambda x: f"ID:{x} - {df_toptan_all[df_toptan_all['id']==x]['tarih'].values[0]} - {df_toptan_all[df_toptan_all['id']==x]['firma_adi'].values[0]} ({df_toptan_all[df_toptan_all['id']==x]['toplam_tutar'].values[0]} TL)"
                )
                
                kayit = df_toptan_all[df_toptan_all["id"] == secilen_id].iloc[0]
                
                with st.form("toptan_duzenle_form"):
                    e_tur = st.selectbox("İşlem Türü", ["Satış", "Tahsilat"], index=0 if kayit["islem_turu"] == "Satış" else 1)
                    e_firma = st.selectbox("Firma Seçin", firma_listesi, index=firma_listesi.index(kayit["firma_adi"]) if kayit["firma_adi"] in firma_listesi else 0)
                    e_tarih = st.date_input("Tarih", datetime.strptime(str(kayit["tarih"]), "%Y-%m-%d"))
                    
                    if e_tur == "Satış":
                        e_adet = st.number_input("Adet", min_value=0, step=50, value=int(kayit["adet"]))
                        e_birim_fiyat = st.number_input("Birim Fiyat (TL)", min_value=0.0, step=0.5, value=float(kayit["birim_fiyat"]), format="%.2f")
                        e_toplam = e_adet * e_birim_fiyat
                    else:
                        e_adet = 0
                        e_birim_fiyat = 0.0
                        e_toplam = st.number_input("Tahsil Edilen Tutar (TL)", min_value=0.0, step=50.0, value=float(kayit["toplam_tutar"]), format="%.2f")

                    st.info(f"Tutar: **{e_toplam:,.2f} TL**")
                    e_aciklama = st.text_input("Açıklama", value=str(kayit["aciklama"]) if kayit["aciklama"] else "")
                    
                    guncelle = st.form_submit_button("✏️ Güncelle", type="primary")
                    sil = st.form_submit_button("🗑️ Sil")
                    
                    if guncelle:
                        client.execute("""
                            UPDATE toptan_satis 
                            SET firma_adi=?, tarih=?, islem_turu=?, adet=?, birim_fiyat=?, toplam_tutar=?, aciklama=? 
                            WHERE id=?
                        """, [e_firma, e_tarih.strftime("%Y-%m-%d"), e_tur, e_adet, e_birim_fiyat, e_toplam, e_aciklama, int(secilen_id)])
                        st.success("Kayıt güncellendi!")
                        st.rerun()
                        
                    if sil:
                        client.execute("DELETE FROM toptan_satis WHERE id=?", [int(secilen_id)])
                        st.warning("Kayıt silindi!")
                        st.rerun()

        st.divider()
        st.write("**Son İşlemler**")
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
# 5. ALT BÖLÜM: TEK TIKLA YEDEK İNDİRMA
# ==========================================
st.divider()
st.subheader("💾 Veritabanı Yedeği Al (Tek Tıkla İndir)")

with st.expander("📥 Tüm Sistem Yedeğini Bilgisayara / Telefona İndir", expanded=False):
    st.write("Aşağıdaki butona basarak dükkan hareketleri, toptan satışlar ve firma kayıtlarınızın tam yedeğini **Excel/CSV** formatında anında indirebilirsiniz.")
    
    # Tüm tabloları çekip birleştirme
    try:
        df_f = run_query_df("SELECT 'Firma' as Tablo, id, firma_adi as Detay_1, telefon as Detay_2, aciklama as Detay_3, NULL as Tarih, NULL as Tutar FROM firmalar")
        df_t = run_query_df("SELECT 'Toptan Satis' as Tablo, id, firma_adi as Detay_1, islem_turu as Detay_2, aciklama as Detay_3, tarih as Tarih, toplam_tutar as Tutar FROM toptan_satis")
        df_d = run_query_df("SELECT 'Dukkan Hareket' as Tablo, id, kategori as Detay_1, islem_tipi as Detay_2, urun_adi as Detay_3, tarih as Tarih, tutar as Tutar FROM dukkan_hareket")
        
        df_tam_yedek = pd.concat([df_f, df_t, df_d], ignore_index=True)
        
        csv_buffer = io.StringIO()
        df_tam_yedek.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_data = csv_buffer.getvalue().encode('utf-8-sig')
        
        st.download_button(
            label="📲 TÜM VERİTABANINI İNDİR (.CSV / EXCEL)",
            data=csv_data,
            file_name=f"midyeci_abla_yedek_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv",
            mime="text/csv",
            type="primary"
        )
    except Exception as e:
        st.error("Yedek hazırlanırken bir hata oluştu.")
