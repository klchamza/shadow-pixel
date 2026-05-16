"""
stego.py — Gelişmiş LSB Steganografi Aracı
Yöntem: LSB (Least Significant Bit) + isteğe bağlı güvenlik katmanları
by:klchamza
instagram:klc.hamzaa
github:https://klchamza
"""

from PIL import Image
import sys, random, hashlib, os

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    AES_MEVCUT = True
except ImportError:
    AES_MEVCUT = False


# ══════════════════════════════════════════════════════════════════════
#  YARDIM METİNLERİ
# ══════════════════════════════════════════════════════════════════════

YARDIM = {

"genel": """
╔════════════════════════════════════════════════════════════════════╗
║          🔐  STEGO.PY — Gelişmiş LSB Steganografi Aracı           ║
╚════════════════════════════════════════════════════════════════════╝

  Ne yapar?
  ─────────
  Bir resmin piksellerinin içine metin mesajı gizler.
  İnsan gözü farkı göremez. Resim görsel olarak aynı kalır.
  İsteğe bağlı olarak mesajı şifreleyebilir, kilitleyebilir,
  bitlerini rastgele dağıtabilir, farklı kanallara saklayabilir.

  Temel Mantık (LSB nedir?)
  ─────────────────────────
  Her piksel 3 renk kanalından oluşur: Kırmızı, Yeşil, Mavi (RGB).
  Her kanal 0-255 arası bir sayıdır, yani 8 bittir.
  Bu 8 bitin son 1-2 tanesi değiştirilse insan gözü FAR ETMEZ.
  (255 ile 254 arasındaki fark gözle görünmez.)
  İşte bu son bitlere mesaj gizliyoruz.

  Çözme Mantığı
  ─────────────
  Mesajı çözmek için encode'da kullandığın seçeneklerin
  TAMAMINI decode'da da kullanman gerekir.
  Örnek: --sifre ile gömdüysen --sifre ile açarsın.
         --seed ile gömdüysen --seed ile açarsın.
  Seçeneklerin kombinasyonu bir tür "anahtar" gibi düşün.

  Komutlar
  ────────
  encode      Mesajı resme göm
  decode      Gömülü mesajı oku
  kapasite    Resmin kaç karakter taşıyabileceğini göster
  help        Bu genel yardımı göster

  Her parametre için detaylı yardım:
    python stego.py --sifre help
    python stego.py --parola help
    python stego.py --seed help
    python stego.py --kanal help
    python stego.py --bit help

  Her komut için detaylı yardım:
    python stego.py encode help
    python stego.py decode help

  Kurulum
  ───────
  pip install pillow            (zorunlu, resim işleme)
  pip install pycryptodome      (sadece --sifre için)

  ⚠️  Önemli Kurallar
  ───────────────────
  • Çıkış dosyası MUTLAKA .png olmalı!
    JPEG sıkıştırma yapar ve gizli bitleri bozar, mesaj kaybolur.
  • Encode'da ne kullandıysan decode'da da aynısını kullan.
  • --sifre ve --parola aynı anda kullanılmaz, biri seçilir.
""",

"encode": """
╔════════════════════════════════════════════════════════════════════╗
║                      encode — Mesaj Gömme                         ║
╚════════════════════════════════════════════════════════════════════╝

  Kullanım:
    python stego.py encode <resim> <mesaj> <çıkış.png> [parametreler]

  Zorunlu:
    <resim>       Kaynak resim (PNG veya JPEG)
    <mesaj>       Gizlenecek metin — tırnak içine al
    <çıkış.png>   Çıkış dosyası — .png uzantılı olmalı!

  İsteğe Bağlı Parametreler:
    --sifre <parola>       AES-256 şifreleme
    --parola <parola>      Parola ile kilitleme
    --seed <sayi>          Rastgele piksel dağılımı
    --kanal <r|g|b|hepsi>  Hangi renk kanalı kullanılsın
    --bit <1|2>            Kaç LSB biti kullanılsın

  Her parametre için:
    python stego.py --sifre help
    python stego.py --seed help
    ... vb.

  Örnekler:
    # Sadece gömme (koruma yok)
    python stego.py encode foto.png "merhaba" cikis.png

    # AES şifreleme ile
    python stego.py encode foto.png "gizli" cikis.png --sifre p4r0l4

    # Rastgele dağılım + şifreleme (güçlü)
    python stego.py encode foto.png "gizli" cikis.png --sifre p4r0l4 --seed 1337

    # Maksimum güvenlik (her şey birden)
    python stego.py encode foto.png "gizli" cikis.png --sifre p4r0l4 --seed 1337 --kanal g --bit 1
""",

"decode": """
╔════════════════════════════════════════════════════════════════════╗
║                      decode — Mesaj Okuma                         ║
╚════════════════════════════════════════════════════════════════════╝

  Kullanım:
    python stego.py decode <resim> [parametreler]

  Zorunlu:
    <resim>    Gizli mesaj içeren resim

  Parametreler (encode'da ne kullandıysan onu kullan):
    --sifre <parola>       AES ile şifrelenmişse çözer
    --parola <parola>      Parola ile kilitlenmişse açar
    --seed <sayi>          Rastgele dağıtıldıysa toplar
    --kanal <r|g|b|hepsi>  Hangi kanala gömüldüyse oradan okur
    --bit <1|2>            Kaç bitle gömüldüyse o kadar okur

  ⚠️  Encode'da kullandığın parametrelerin TAMAMINI decode'da
      da kullanmazsan mesaj yanlış veya bozuk çıkar!

  Örnekler:
    python stego.py decode cikis.png
    python stego.py decode cikis.png --sifre p4r0l4
    python stego.py decode cikis.png --sifre p4r0l4 --seed 1337
    python stego.py decode cikis.png --sifre p4r0l4 --seed 1337 --kanal g --bit 1
""",

"--sifre": """
╔════════════════════════════════════════════════════════════════════╗
║                  --sifre — AES-256 Şifreleme                      ║
╚════════════════════════════════════════════════════════════════════╝

  Kullanım:
    ... --sifre <parola>

  Ne yapar?
  ─────────
  Mesajı resme gömmeden önce AES-256-CBC algoritmasıyla şifreler.
  Yani resimden bitleri okumayı başarsan bile elinde anlamsız
  bir şifreli veri olur. Parolayı bilmeden açamazsın.

  AES-256 nedir?
  ──────────────
  Dünyada en yaygın kullanılan simetrik şifreleme algoritması.
  256 bit anahtar uzunluğu = 2^256 olası kombinasyon.
  Kaba kuvvetle kırmak evrenin yaşından daha uzun sürer.
  Bankalar, ordu, devletler kullanır.

  Nasıl çalışır? (teknik)
  ───────────────────────
  1. Paroladan SHA-256 ile 32 byte'lık bir anahtar türetilir.
  2. Rastgele 16 byte'lık IV (initialization vector) üretilir.
     IV her şifrelemede farklıdır → aynı mesaj farklı şifreli veri verir.
  3. Mesaj AES-CBC ile şifrelenir.
  4. IV + şifreli veri birleştirilerek resme gömülür.
  5. Decode'da: ilk 16 byte IV alınır, geri kalanı çözülür.

  Nasıl çözülür?
  ──────────────
  Sadece aynı parolayla:
    python stego.py decode resim.png --sifre <aynı_parola>

  Parolayı bilmeden çözmek mümkün değil (AES-256 kırılmamış).

  Gereksinim:
    pip install pycryptodome

  Örnek:
    python stego.py encode foto.png "mesaj" cikis.png --sifre gizliAnahtar99
    python stego.py decode cikis.png --sifre gizliAnahtar99
""",

"--parola": """
╔════════════════════════════════════════════════════════════════════╗
║                  --parola — Parola Koruması                       ║
╚════════════════════════════════════════════════════════════════════╝

  Kullanım:
    ... --parola <parola>

  Ne yapar?
  ─────────
  Mesajı şifrelemez ama başına parola doğrulama bilgisi ekler.
  Decode sırasında parola yanlışsa mesaj gösterilmez.
  Kurulum gerektirmez ama --sifre kadar güçlü değildir.

  --sifre ile farkı nedir?
  ────────────────────────
  --parola  → mesaj düz metin olarak gömülür, sadece erişim kilitlidir.
              Bitleri ham okuyabilen biri teorik olarak görebilir.
  --sifre   → mesaj şifreli gömülür, parolasız hiç okunamaz.

  Nasıl çalışır? (teknik)
  ───────────────────────
  1. Parola SHA-256 ile hash'lenir (64 hex karakter = 256 bit).
  2. Mesajın başına hash + "||" ayırıcısı eklenir.
  3. Tamamı resme gömülür.
  4. Decode'da: hash karşılaştırılır, eşleşirse mesaj gösterilir.

  Nasıl çözülür?
  ──────────────
    python stego.py decode resim.png --parola <aynı_parola>

  Örnek:
    python stego.py encode foto.png "mesaj" cikis.png --parola s1frEm
    python stego.py decode cikis.png --parola s1frEm
""",

"--seed": """
╔════════════════════════════════════════════════════════════════════╗
║                  --seed — Rastgele Piksel Dağılımı                ║
╚════════════════════════════════════════════════════════════════════╝

  Kullanım:
    ... --seed <sayi>

  Ne yapar?
  ─────────
  Normalde mesaj bitleri resmin başından itibaren sırayla gömülür.
  Bu tahmin edilebilir: steganografi analiz araçları ilk piksellere bakar.

  --seed ile mesaj bitleri tüm resme RASTGELE dağıtılır.
  Hangi pikselde ne olduğunu bilmeden bulmak çok zordur.

  Seed nedir?
  ───────────
  Rastgele sayı üreticisinin başlangıç noktası.
  Aynı seed her zaman aynı "rastgele" sırayı üretir.
  Yani encode'da 42 kullandıysan decode'da da 42 kullanırsan
  tam olarak aynı piksel sırası oluşur ve mesaj okunur.

  Nasıl çözülür?
  ──────────────
  Seed bilinmeden çözmek çok zordur (1 milyar+ kombinasyon).
  Aynı seed ile:
    python stego.py decode resim.png --seed <aynı_sayi>

  İpucu: seed olarak büyük rastgele bir sayı seç.
  Örnek: --seed 7392041856  (tahmin edilmesi çok zor)

  Örnek:
    python stego.py encode foto.png "mesaj" cikis.png --seed 42
    python stego.py decode cikis.png --seed 42
""",

"--kanal": """
╔════════════════════════════════════════════════════════════════════╗
║                  --kanal — Renk Kanalı Seçimi                     ║
╚════════════════════════════════════════════════════════════════════╝

  Kullanım:
    ... --kanal <r|g|b|hepsi>

  Varsayılan: hepsi

  Ne yapar?
  ─────────
  Her piksel R (kırmızı), G (yeşil), B (mavi) kanallarından oluşur.
  Normalde üç kanala da birer bit gömülür (3 bit/piksel).

  --kanal ile sadece tek bir kanala gömebilirsin.
  Hangi kanala gömüldüğünü bilmeyen analiz araçları yanlış kanala bakar.

  Seçenekler:
    r        Sadece Kırmızı kanala göm
    g        Sadece Yeşil kanala göm   (en iyi: göze en az fark eder)
    b        Sadece Mavi kanala göm
    hepsi    Üç kanala da göm (varsayılan)

  Kapasite etkisi:
    hepsi → piksel başına 3 bit
    tek kanal → piksel başına 1 bit (3x daha az kapasite)

  Nasıl çözülür?
  ──────────────
  Hangi kanalın kullanıldığını bilmeden çözmek zordur (3 seçenek).
  Aynı kanal ile:
    python stego.py decode resim.png --kanal g

  Örnek:
    python stego.py encode foto.png "mesaj" cikis.png --kanal g
    python stego.py decode cikis.png --kanal g
""",

"--bit": """
╔════════════════════════════════════════════════════════════════════╗
║                  --bit — Bit Derinliği                            ║
╚════════════════════════════════════════════════════════════════════╝

  Kullanım:
    ... --bit <1|2>

  Varsayılan: 1

  Ne yapar?
  ─────────
  Normalde her kanalın sadece SON 1 bitine veri gömülür.
  --bit 2 ile son 2 bitine gömülür.

  1 bit → kanal değeri en fazla 1 değişir (254↔255 gibi) — gözle görünmez
  2 bit → kanal değeri en fazla 3 değişir — hâlâ çok zor fark edilir
           ama piksel başına 2x daha fazla veri sığar

  Kapasite etkisi:
    --bit 1 → kanal başına 1 bit
    --bit 2 → kanal başına 2 bit (2x kapasite)

  Güvenlik etkisi:
  ────────────────
  2 bit kullanmak daha fazla piksel değiştirir.
  İstatistiksel analiz araçları bunu teorik olarak fark edebilir.
  Gizlilik öncelikliyse --bit 1 kullan.
  Kapasite öncelikliyse --bit 2 kullan.

  Nasıl çözülür?
  ──────────────
  Kaç bit kullanıldığını bilmeden çözmek zordur.
  Aynı değerle:
    python stego.py decode resim.png --bit 2

  Örnek:
    python stego.py encode foto.png "uzun mesaj" cikis.png --bit 2
    python stego.py decode cikis.png --bit 2
""",

}


# ══════════════════════════════════════════════════════════════════════
#  DÖNÜŞÜM YARDIMCILARI
# ══════════════════════════════════════════════════════════════════════

def metin_to_binary(metin: str) -> str:
    return ''.join(format(ord(c), '08b') for c in metin)

def binary_to_metin(binary: str) -> str:
    return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))

def bytes_to_binary(veri: bytes) -> str:
    return ''.join(format(b, '08b') for b in veri)

def binary_to_bytes(binary: str) -> bytes:
    return bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))


# ══════════════════════════════════════════════════════════════════════
#  GÜVENLİK: ŞİFRELEME / PAROLA
# ══════════════════════════════════════════════════════════════════════

def parola_hash(parola: str) -> str:
    # SHA-256 → 64 hex karakter
    return hashlib.sha256(parola.encode()).hexdigest()

def aes_sifrele(mesaj: str, parola: str) -> bytes:
    if not AES_MEVCUT:
        sys.exit("✗ AES için: pip install pycryptodome")
    anahtar = hashlib.sha256(parola.encode()).digest()  # 32 byte anahtar
    iv      = os.urandom(16)                             # her seferinde farklı IV
    cipher  = AES.new(anahtar, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(pad(mesaj.encode(), AES.block_size))

def aes_coz(veri: bytes, parola: str) -> str:
    if not AES_MEVCUT:
        sys.exit("✗ AES için: pip install pycryptodome")
    anahtar = hashlib.sha256(parola.encode()).digest()
    try:
        cipher = AES.new(anahtar, AES.MODE_CBC, veri[:16])  # ilk 16 byte IV
        return unpad(cipher.decrypt(veri[16:]), AES.block_size).decode()
    except Exception:
        sys.exit("✗ Yanlış şifre veya bozuk veri!")


# ══════════════════════════════════════════════════════════════════════
#  GÜVENLİK: RASTGELE DAĞILIM
# ══════════════════════════════════════════════════════════════════════

def piksel_sirasi(toplam: int, seed: int = None, parola_tuzu: str = "") -> list:
    """
    Piksellerin işlenme sırasını döner.
    seed + parola_tuzu birleştirilerek tohum oluşturulur.
    Bu sayede aynı seed farklı parolayla farklı sıra üretir.
    """
    siralama = list(range(toplam))
    if seed is not None:
        # seed'i parolayla tuzla: aynı seed + farklı parola = farklı dağılım
        tuz    = f"{seed}{parola_tuzu}"
        tohum  = int(hashlib.md5(tuz.encode()).hexdigest(), 16) % (2**32)
        random.seed(tohum)
        random.shuffle(siralama)
    return siralama


# ══════════════════════════════════════════════════════════════════════
#  KANAL SEÇİMİ
# ══════════════════════════════════════════════════════════════════════

KANAL_MAP = {"r": [0], "g": [1], "b": [2], "hepsi": [0, 1, 2]}

def kanal_listesi(kanal: str) -> list:
    k = kanal.lower()
    if k not in KANAL_MAP:
        sys.exit(f"✗ Geçersiz kanal: '{kanal}'. Seçenekler: r, g, b, hepsi")
    return KANAL_MAP[k]


# ══════════════════════════════════════════════════════════════════════
#  BİT GÖMME / OKUMA
# ══════════════════════════════════════════════════════════════════════

def bitleri_gom(pikseller, veri_binary, seed=None, kanal="hepsi", bit_derinlik=1, parola_tuzu=""):
    kanallar  = kanal_listesi(kanal)
    siralama  = piksel_sirasi(len(pikseller), seed, parola_tuzu)
    maske_sil = 0xFF ^ ((1 << bit_derinlik) - 1)   # örn bit=2: 11111100
    # bu maske son bit_derinlik kadar biti sıfırlar, gerisini korur

    kapasite = len(siralama) * len(kanallar) * bit_derinlik
    if len(veri_binary) > kapasite:
        sys.exit(f"✗ Mesaj çok uzun! Mevcut kapasite: {(kapasite - 32) // 8} karakter")

    plist     = [list(p) for p in pikseller]
    bit_idx   = 0

    for piksel_no in siralama:
        if bit_idx >= len(veri_binary):
            break
        for k in kanallar:
            if bit_idx >= len(veri_binary):
                break
            # kaç bit alacağız? (son chunk küçük olabilir)
            parca     = veri_binary[bit_idx : bit_idx + bit_derinlik]
            parca     = parca.ljust(bit_derinlik, '0')  # eksikse sağdan sıfırla
            deger     = int(parca, 2)
            plist[piksel_no][k] = (plist[piksel_no][k] & maske_sil) | deger
            # maske_sil ile hedef bitleri sıfırla, sonra yeni değeri yaz
            bit_idx  += bit_derinlik

    return [tuple(p) for p in plist]


def bitleri_oku(pikseller, seed=None, kanal="hepsi", bit_derinlik=1, parola_tuzu=""):
    kanallar = kanal_listesi(kanal)
    siralama = piksel_sirasi(len(pikseller), seed, parola_tuzu)
    maske    = (1 << bit_derinlik) - 1  # örn bit=2: 00000011 → son 2 biti al

    bitler = []
    for piksel_no in siralama:
        for k in kanallar:
            deger = pikseller[piksel_no][k] & maske          # son N biti al
            bitler.append(format(deger, f'0{bit_derinlik}b'))  # binary stringe çevir

    return ''.join(bitler)


# ══════════════════════════════════════════════════════════════════════
#  KAPASİTE HESABI
# ══════════════════════════════════════════════════════════════════════

def kapasitesi(resim_yolu, kanal="hepsi", bit_derinlik=1):
    img     = Image.open(resim_yolu).convert("RGB")
    w, h    = img.size
    kanallar = kanal_listesi(kanal)
    toplam_bit = w * h * len(kanallar) * bit_derinlik
    return toplam_bit


# ══════════════════════════════════════════════════════════════════════
#  ENCODE
# ══════════════════════════════════════════════════════════════════════

def encode(resim, mesaj, cikis, sifre=None, parola=None, seed=None,
           kanal="hepsi", bit_derinlik=1):

    img      = Image.open(resim).convert("RGB")
    pikseller = list(img.getdata())
    tuzu     = sifre or parola or ""   # seed tuzlama için parola kullan

    print()

    # ── güvenlik katmanları ───────────────────────────────────────────

    if sifre and parola:
        sys.exit("✗ --sifre ve --parola aynı anda kullanılamaz, birini seç.")

    if sifre:
        veri_bin = bytes_to_binary(aes_sifrele(mesaj, sifre))
        print("  🔒 AES-256-CBC şifreleme uygulandı.")
    elif parola:
        birlesik = parola_hash(parola) + "||" + mesaj
        veri_bin = metin_to_binary(birlesik)
        print("  🔑 Parola koruması uygulandı.")
    else:
        veri_bin = metin_to_binary(mesaj)

    if seed is not None:
        print(f"  🎲 Rastgele dağılım aktif (seed: {seed})")

    if kanal != "hepsi":
        print(f"  📡 Kanal: sadece '{kanal.upper()}' kanalı kullanılıyor.")

    if bit_derinlik == 2:
        print(f"  🔢 Bit derinliği: 2 (kanal başına 2 bit)")

    # ── uzunluk başlığı + veri ────────────────────────────────────────

    uzunluk_bin = format(len(veri_bin), '032b')   # 32 bit uzunluk başlığı
    toplam      = uzunluk_bin + veri_bin

    # ── gömme ─────────────────────────────────────────────────────────

    yeni = bitleri_gom(pikseller, toplam, seed, kanal, bit_derinlik, tuzu)
    img.putdata(yeni)
    img.save(cikis, "PNG")   # JPEG sıkıştırır, PNG zorunlu

    kapasite_bit = kapasitesi(resim, kanal, bit_derinlik)
    kullanim     = len(toplam) / kapasite_bit * 100

    print(f"\n  ✓ Mesaj gömüldü → {cikis}")
    print(f"    Mesaj uzunluğu  : {len(mesaj)} karakter")
    print(f"    Gömülen bit     : {len(veri_bin)} bit")
    print(f"    Kapasite kullanım: %{kullanim:.2f}")
    print()


# ══════════════════════════════════════════════════════════════════════
#  DECODE
# ══════════════════════════════════════════════════════════════════════

def decode(resim, sifre=None, parola=None, seed=None,
           kanal="hepsi", bit_derinlik=1):

    img      = Image.open(resim).convert("RGB")
    pikseller = list(img.getdata())
    tuzu     = sifre or parola or ""

    print()

    # ── bitleri topla ─────────────────────────────────────────────────

    tum_bitler = bitleri_oku(pikseller, seed, kanal, bit_derinlik, tuzu)

    # ── ilk 32 bit = mesaj uzunluğu ───────────────────────────────────

    uzunluk  = int(tum_bitler[:32], 2)
    veri_bin = tum_bitler[32 : 32 + uzunluk]

    # ── güvenlik katmanlarını geri al ─────────────────────────────────

    if sifre:
        mesaj = aes_coz(binary_to_bytes(veri_bin), sifre)
        print("  🔓 AES şifresi çözüldü.")
    elif parola:
        birlesik = binary_to_metin(veri_bin)
        if "||" not in birlesik:
            sys.exit("✗ Bu resim parola korumalı değil veya bozuk.")
        kayitli_hash, mesaj = birlesik.split("||", 1)
        if kayitli_hash != parola_hash(parola):
            sys.exit("✗ Yanlış parola!")
        print("  ✅ Parola doğrulandı.")
    else:
        mesaj = binary_to_metin(veri_bin)

    print(f"\n  ✓ Gizli mesaj:\n")
    print(f"    {mesaj}")
    print()


# ══════════════════════════════════════════════════════════════════════
#  ARGÜMAN AYRIŞTIRICISI
# ══════════════════════════════════════════════════════════════════════

def arg_al(arglar, anahtar, varsayilan=None):
    if anahtar in arglar:
        idx = arglar.index(anahtar)
        if idx + 1 < len(arglar):
            return arglar[idx + 1]
    return varsayilan

def ortak_parametreler(arglar):
    sifre      = arg_al(arglar, "--sifre")
    parola     = arg_al(arglar, "--parola")
    seed       = arg_al(arglar, "--seed")
    kanal      = arg_al(arglar, "--kanal", "hepsi")
    bit        = arg_al(arglar, "--bit", "1")
    seed       = int(seed) if seed is not None else None
    bit        = int(bit)
    if bit not in (1, 2):
        sys.exit("✗ --bit sadece 1 veya 2 olabilir.")
    return sifre, parola, seed, kanal, bit


# ══════════════════════════════════════════════════════════════════════
#  ANA PROGRAM
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(YARDIM["genel"])
        sys.exit(0)

    mod   = sys.argv[1].lower()
    arglar = sys.argv[2:]

    # ── parametre yardımları: --sifre help, --seed help, vb. ──────────
    if mod in YARDIM:
        print(YARDIM[mod])
        sys.exit(0)

    # ── genel help ────────────────────────────────────────────────────
    if mod in ("help", "--help", "-h"):
        print(YARDIM["genel"])
        sys.exit(0)

    # ── komut yardımları: encode help, decode help ────────────────────
    if arglar and arglar[0].lower() == "help":
        anahtar = mod if mod in YARDIM else "genel"
        print(YARDIM.get(anahtar, YARDIM["genel"]))
        sys.exit(0)

    # ── encode ────────────────────────────────────────────────────────
    if mod == "encode":
        if len(arglar) < 3:
            print("✗ Eksik parametre!")
            print("  python stego.py encode <resim> <mesaj> <çıkış.png> [seçenekler]")
            print("  Detay: python stego.py encode help")
            sys.exit(1)
        resim, mesaj, cikis        = arglar[0], arglar[1], arglar[2]
        sifre, parola, seed, kanal, bit = ortak_parametreler(arglar)
        encode(resim, mesaj, cikis, sifre, parola, seed, kanal, bit)

    # ── decode ────────────────────────────────────────────────────────
    elif mod == "decode":
        if len(arglar) < 1:
            print("✗ Resim dosyası belirtilmedi!")
            print("  python stego.py decode <resim> [seçenekler]")
            print("  Detay: python stego.py decode help")
            sys.exit(1)
        resim                      = arglar[0]
        sifre, parola, seed, kanal, bit = ortak_parametreler(arglar)
        decode(resim, sifre, parola, seed, kanal, bit)

    # ── kapasite ──────────────────────────────────────────────────────
    elif mod == "kapasite":
        if len(arglar) < 1:
            print("✗ Resim dosyası belirtilmedi!")
            sys.exit(1)
        kanal = arg_al(arglar, "--kanal", "hepsi")
        bit   = int(arg_al(arglar, "--bit", "1"))
        maks  = kapasitesi(arglar[0], kanal, bit)
        print(f"\n  ✓ {arglar[0]}")
        print(f"    Kanal           : {kanal}")
        print(f"    Bit derinliği   : {bit}")
        print(f"    Toplam kapasite : {maks} bit")
        print(f"    Max karakter    : {(maks - 32) // 8}")
        print()

    # ── bilinmeyen ────────────────────────────────────────────────────
    else:
        print(f"✗ Bilinmeyen komut: '{mod}'")
        print("  Geçerli: encode, decode, kapasite, help")
        print("  Parametre yardımı: python stego.py --sifre help")
        sys.exit(1)


