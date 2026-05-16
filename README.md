# ShadowPixel — Hamza Hack Team

> Resmin içine gizli mesaj göm. İnsan gözü hiç fark etmez.

🌐 **Canlı Site:** [shadowpixel.netlify.app](https://shadowpixel.netlify.app)

---

## Ne Bu?

ShadowPixel, **LSB (Least Significant Bit)** yöntemini kullanan bir steganografi aracı. Yani bir resim dosyasının piksellerinin içine, görüntüyü bozmadan metin gizleyebiliyorsun. Mesajı gömen kişi dışında kimse bakıp "bu resimde bir şey var" diyemez.

İki versiyonu var: biri terminalde çalışan Python scripti, diğeri tarayıcıda çalışan web arayüzü. HTML versiyonunda gömme/çözme işlemlerine ek olarak, aracı sana anlatan bir AI chat asistanı da entegre edilmiş.

---

## Nasıl Çalışır?

Her piksel 3 renk kanalından oluşur: Kırmızı, Yeşil, Mavi (RGB). Her kanal 0-255 arasında bir sayıdır, yani 8 bittir. Bu 8 bitin son 1-2 tanesi değiştirilse insan gözü hiç fark etmez — 255 ile 254 arasındaki fark görünmez. ShadowPixel tam olarak bu son bitlere mesajı yerleştiriyor.

---

## Dosyalar

```
├── shadowpixel.html   → Tarayıcıda çalışan web arayüzü (AI chat dahil)
├── stego.py           → Terminalde çalışan Python versiyonu
└── README.md          → Bu dosya
```

---

## Güvenlik Seçenekleri

Her iki versiyonda da aşağıdaki parametrelerle mesajına ekstra koruma katabilirsin. Bunlar birbirleriyle kombine edilebilir, kombinasyon bir tür "anahtar" gibi davranır — encode'da ne kullandıysan decode'da da aynısını kullanman gerekir.

| Parametre | Ne Yapar |
|---|---|
| `--sifre` | AES-256-CBC ile mesajı şifreler. Parolasız açılamaz. En güçlü koruma. |
| `--parola` | Parola hash'i ile kilitler. Şifreleme yok ama erişim korumalı. Kurulum gerektirmez. |
| `--seed` | Piksel sırasını rastgele dağıtır. Seed bilinmeden mesajı bulmak çok zordur. |
| `--kanal` | Hangi renk kanalına gömüleceği (r / g / b / hepsi). |
| `--bit` | Bit derinliği: 1 = gizlilik öncelikli, 2 = kapasite 2x artar. |

> ⚠️ `--sifre` ve `--parola` aynı anda kullanılamaz, birini seç.

---

## Python Versiyonu (stego.py)

**Kurulum:**
```bash
pip install pillow           # zorunlu
pip install pycryptodome     # sadece --sifre kullanacaksan
```

**Mesaj göm:**
```bash
python stego.py encode foto.png "gizli mesaj" cikis.png
```

**Mesaj oku:**
```bash
python stego.py decode cikis.png
```

**AES şifreli gömme:**
```bash
python stego.py encode foto.png "gizli mesaj" cikis.png --sifre parolam
python stego.py decode cikis.png --sifre parolam
```

**Maksimum güvenlik (şifre + seed + kanal seçimi):**
```bash
python stego.py encode foto.png "gizli" cikis.png --sifre p4r0l4 --seed 1337 --kanal g --bit 1
python stego.py decode cikis.png --sifre p4r0l4 --seed 1337 --kanal g --bit 1
```

**Kapasite kontrolü (resim kaç karakter taşır?):**
```bash
python stego.py kapasite foto.png
```

**Her komut için detaylı yardım:**
```bash
python stego.py help
python stego.py encode help
python stego.py --sifre help
```

> ⚠️ Çıkış dosyası mutlaka `.png` olmalı. JPEG sıkıştırma yapar ve gizlenmiş bitleri bozar, mesaj gider.

---

## Web Versiyonu (shadowpixel.html)

Dosyayı tarayıcıda direkt açabilir ya da Netlify, GitHub Pages gibi bir platforma deploy edebilirsin.

Arayüzde encode, decode ve kapasite hesaplama sekmeleri var. Parametreleri butonlarla seçiyorsun, komut yazmana gerek yok.

### AI Chat Asistanı

HTML versiyonunda entegre bir AI asistan var. LSB steganografi hakkında sorularını yanıtlıyor, ShadowPixel'i nasıl kullanacağını adım adım anlatıyor.

Çalışması için Groq API key gerekiyor:

1. [console.groq.com](https://console.groq.com) adresinden ücretsiz hesap aç
2. API Keys sekmesinden yeni key oluştur (`gsk_` ile başlar)
3. Sitedeki **AI Asistan** bölümündeki kutuya key'i yapıştır, **Kaydet**'e bas

Doğrudan koda gömmek istersen `shadowpixel.html` dosyasını aç ve şu satırı bul:

```javascript
let groqApiKey = 'buraya_kendi_key_ini_yaz';
```

Tırnak içine key'ini yaz, kaydet, bitti.

---

## Önemli Not

Groq API key'ini **public repoya koyma.** GitHub'a yükleyeceksen key'i boş bırak, sitenin arayüzünden girmeyi tercih et. Ya da `.env` kullan ve `.gitignore`'a ekle.

---

## Geliştirici

**klchamza** — Hamza Hack Team  
Instagram: [@klc.hamzaa](https://instagram.com/klc.hamzaa)  
GitHub: [github.com/klchamza](https://github.com/klchamza)  
Model: `llama-3.3-70b-versatile` via [Groq](https://groq.com)
