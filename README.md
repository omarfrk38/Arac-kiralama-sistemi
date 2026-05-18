# 🚗 Premium Araç Kiralama Sistemi

Modern, kullanıcı dostu ve tam donanımlı bir araç kiralama yönetim sistemi. PyQt5 ile geliştirilmiş, SQLite veritabanı desteğine sahip, grafiksel raporlama ve kullanıcı yönetimi özellikleriyle donatılmıştır.

**🔐 Giriş Bilgileri:**
- Admin: `admin` / `admin123`
- Normal Kullanıcı: `user` / `user123`



# 📋 Özellikler

# 🔐 Kullanıcı Yönetimi
- Admin ve normal kullanıcı girişi
- Kullanıcı ekleme/silme (Admin yetkisi)
- Oturum yönetimi ve çıkış


<img width="441" height="477" alt="Screenshot 2026-05-15 at 18 29 33" src="https://github.com/user-attachments/assets/89d69c98-fa2d-4364-8a75-db5abb68cf70" />



# 🚗 Araç Yönetimi
- Araç ekleme, silme, listeleme
- Araç durumu takibi (Müsait/Kirada)
- Kilometre takibi
- Plaka benzersizlik kontrolü

- 

<img width="1440" height="900" alt="Screenshot 2026-05-15 at 18 30 36" src="https://github.com/user-attachments/assets/ac3396dd-95fb-42db-856a-107983b1dae9" />



# 👥 Müşteri Yönetimi
- Müşteri ekleme, silme, listeleme
- Ehliyet no ve email benzersizlik kontrolü
- Telefon ve email doğrulama


<img width="1440" height="900" alt="Screenshot 2026-05-15 at 18 30 54" src="https://github.com/user-attachments/assets/21a2bb8a-fad8-4339-8b02-73901c6e8eb2" />


# 🔑 Kiralama İşlemleri
- Kiralama başlatma/bitirme
- Günlük fiyat belirleme
- Kilometre takibi ve kontrolü
- Aynı müşteri aynı anda sadece 1 araç kiralayabilir
- Kiradaki araç silinemez
- Aktif kiralaması olan müşteri silinemez

  
<img width="1440" height="900" alt="Kiralamalar" src="https://github.com/user-attachments/assets/73edae5e-ca52-457e-bea4-7f3451c64159" />



# 🎁 Hediye Sistemi (YENİ!)
- Hediye kiralama oluşturma
- Benzersiz hediye kodu üretme
- Hediye kodu ile ücretsiz kiralama
- Hediye notu ekleme
- Hediye durumu takibi (Beklemede/Kullanıldı/İptal Edildi)


<img width="1440" height="900" alt="Hediye" src="https://github.com/user-attachments/assets/995981d1-c334-4e79-bb48-b91b7fd2b79d" />



# 📊 Raporlama ve İstatistikler
- Toplam araç, müşteri, aktif kiralama ve ciro gösterimi
- Pasta grafik ile araç durumu dağılımı
- Çubuk grafik ile sistem istatistikleri
- Detaylı metin raporu

  
<img width="1440" height="900" alt="Istatistikler" src="https://github.com/user-attachments/assets/a6f5c7cf-e10c-41b0-84e3-aa27c2ca79a0" />



<img width="1440" height="900" alt="Raporlar" src="https://github.com/user-attachments/assets/2cc66946-5dd4-4b2e-b30a-88baa2ba6fee" />



# 🔍 Arama Özelliği
Tüm sekmelerde anlık arama:
- **Araç:** Marka, Model, Plaka, Yıl
- **Müşteri:** Ad, Soyad, Ehliyet No, Telefon, Email
- **Kiralama:** Araç adı, Müşteri adı, Durum
- **Hediye:** Hediye kodu, Gönderen, Alan, Durum
- **Kullanıcı:** Kullanıcı Adı, Ad, Soyad, Rol



# 🖥️ Teknolojiler

| Teknoloji | Kullanım Alanı |
|-----------|----------------|
| Python 3.9+ | Ana programlama dili |
| PyQt5 | GUI Framework (Modern arayüz) |
| SQLite3 | Veritabanı yönetimi |
| Matplotlib | Grafik ve görselleştirme |


