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
        st.subheader("Tüm Dükkan Kayıtlarını Yönet")
        df_dukkan_all = run_query_df("SELECT id, tarih, islem_tipi, kategori, urun_adi, miktar, birim_fiyat, tutar FROM dukkan_hareket ORDER BY id DESC")
        
        if not df_dukkan_all.empty:
            secilen_d_id = st.selectbox("Kayıt Seçin:", 
                                        options=df_dukkan_all["id"], 
                                        format_func=lambda x: f"ID:{x} - {df_dukkan_all[df_dukkan_all['id']==x]['tarih'].values[0]} - {df_dukkan_all[df_dukkan_all['id']==x]['kategori'].values[0]} ({df_dukkan_all[df_dukkan_all['id']==x]['tutar'].values[0]} TL)")
            
            kayit_d = df_dukkan_all[df_dukkan_all["id"] == secilen_d_id].iloc[0]
            kat_list = ["Midye", "Çiğ Köfte", "İçecek", "Dükkan Gideri", "Personel", "Diğer"]
            tip_list = ["Günlük Satış (Gelir)", "Dükkan Gideri (Gider)"]
            
            with st.form("dukkan_duzenle_form"):
                e_tip = st.selectbox("İşlem Tipi", tip_list, index=tip_list.index(kayit_d["islem_tipi"]) if kayit_d["islem_tipi"] in tip_list else 0)
                e_tarih_d = st.date_input("Tarih", datetime.strptime(str(kayit_d["tarih"])[:10], "%Y-%m-%d"))
                e_kat = st.selectbox("Kategori", kat_list, index=kat_list.index(kayit_d["kategori"]) if kayit_d["kategori"] in kat_list else 0)
                e_urun = st.text_input("Ürün / Detay", value=str(kayit_d["urun_adi"]) if kayit_d["urun_adi"] else "")
                e_m = st.number_input("Miktar", min_value=1, step=1, value=int(kayit_d["miktar"]))
                e_f = st.number_input("Birim Fiyat (TL)", min_value=0.0, step=0.25, value=float(kayit_d["birim_fiyat"]), format="%.2f")
                
                e_toplam_d = e_m * e_f
                st.info(f"Yeni Toplam: **{e_toplam_d:,.2f} TL**")
                
                guncelle_d = st.form_submit_button("✏️ Güncelle", type="primary")
                sil_d = st.form_submit_button("🗑️ Sil")
                
                if guncelle_d:
                    simdi_zaman = datetime.now().strftime("%H:%M:%S")
                    tam_tarih_saat = f"{e_tarih_d.strftime('%Y-%m-%d')} {simdi_zaman}"
                    client.execute("""
                        UPDATE dukkan_hareket 
                        SET tarih=?, islem_tipi=?, kategori=?, urun_adi=?, miktar=?, birim_fiyat=?, tutar=? 
                        WHERE id=?
                    """, [tam_tarih_saat, e_tip, e_kat, e_urun, e_m, e_f, e_toplam_d, int(secilen_d_id)])
                    st.success("Kayıt güncellendi!")
                    st.rerun()
                    
                if sil_d:
                    client.execute("DELETE FROM dukkan_hareket WHERE id=?", [int(secilen_d_id)])
                    st.warning("Kayıt silindi!")
                    st.rerun()
        else:
            st.info("Yönetilebilecek dükkan kaydı bulunamadı.")

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

            # FIRMA SEÇİMİ VE ANLIK BAKİYE GÖSTERGESİ (GÜNCELLEME)
            secili_firma_toptan = st.selectbox("Firma Seçin", firma_listesi, key="toptan_firma_secim")
            
            # Anlık Firma Bakiyesini Hesapla ve Göster
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

            with st.form("toptan_form", clear_on_submit=True):
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
                    """, [secili_firma_toptan, tarih.strftime("%Y-%m-%d"), t_tur, adet, birim_fiyat, toplam_tutar, aciklama])
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
