# Hobilere Göre Eşleştirme Sitesi

## 📌 Proje Hakkında

Bu proje, kullanıcıların ilgi alanlarını analiz ederek kişiler arasında bir benzerlik oranı hesaplayan web tabanlı bir uygulamadır. Sistem, kullanıcıların girdikleri verileri karşılaştırarak iki kişi arasında **0 ile 100** arasında bir eşleşme yüzdesi üretir.

**Amaç:** Ortak ilgi alanlarına sahip kullanıcıları tespit etmek ve aralarındaki uyum oranını sayısal olarak göstermektir.

## ⚙️ Nasıl Çalışır?

Kullanıcılardan aşağıdaki kategorilerde veriler toplanır:

- 🎬 **Film tercihleri**
- 📚 **Kitap tercihleri**
- 📺 **Dizi tercihleri**
- 🎨 **Hobiler**
- 🕷️ **Fobiler**
- 🎵 **Şarkılar / Müzik tercihleri**

Girilen veriler sistem tarafından analiz edilir. Ortak ve benzer içerikler belirlenerek özel bir eşleşme algoritması üzerinden yüzdelik bir sonuç hesaplanır. Sonuç olarak kullanıcılar arası uyum oranı **%0 – %100** arası bir değer olarak ekrana yansıtılır.

## 🛠 Kullanılan Teknolojiler

Projenin geliştirilmesinde aşağıdaki teknolojiler kullanılmıştır:

*   **Python** (Backend algoritması)
*   **MySQL** (Veritabanı yönetimi)
*   **HTML** (Arayüz iskeleti)
*   **CSS** (Tasarım ve stil)

## 🚀 Kurulum ve Çalıştırma

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

1.  Projeyi indirin veya terminal üzerinden klonlayın:
    ```bash
    git clone https://github.com/kullaniciadi/proje-adi.git
    ```
2.  Proje klasörü içinde bulunan `database.sql` dosyasını kendi MySQL veritabanınıza import edin.
3.  Kod içerisindeki veritabanı bağlantı bilgilerini (host, user, password, db_name) kendi sisteminize göre düzenleyin.
4.  Ana Python dosyasını (`main.py`) çalıştırarak uygulamayı başlatın.

## 📎 Not

> ⚠️ **Önemli:** Veritabanı şifreleri güvenlik nedeniyle repoya dahil edilmemiştir. Projeyi çalıştırmadan önce veritabanı ayarlarınızı (`db_config` vb.) kendi yerel sunucunuza göre doğru şekilde yapılandırmanız gerekmektedir.Ayrıca veri tabanındaki tüm insanlar ve verileri sahte olup sadece eşleşme sisteminin sonuç kısmını gösterebilmek amacıyla yazılmışlardır