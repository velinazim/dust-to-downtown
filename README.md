# Dust to Downtown

Şehirlerin ilk yerleşimden bugüne nasıl büyüdüğünü gösteren sessiz 3D timelapse videoları üreten otomasyon.
Kanal: **Dust to Downtown** (@DustToDowntown). Haftada 2 uzun video (Salı ve Cuma 18:00 Türkiye saati).

## Nasıl çalışır

1. **Araştırma (Claude):** Sıradaki şehir `cities/queue.md`'den seçilir. Kaynaklar okunur, tarihler, nüfus ve
   koordinatlar `cities/<şehir>/research.md`'ye yazılır. Bölümün tamamı `city.json` dosyasına dökülür.
2. **Önizleme (GitHub Actions, otomatik):** Gerçek harita (yükseklik + OpenStreetMap su alanları) çekilir,
   10 kontrol karesi üretilir. Claude kareleri kontrol eder ve hataları düzeltir.
3. **Render (GitHub Actions, otomatik):** Video 20 parçaya bölünüp aynı anda 20 makinede çizilir,
   birleştirilir, özgün müzik eklenir.
4. **Yükleme:** İngilizce video YouTube'a gizli olarak yüklenir ve sıradaki yayın saatine zamanlanır.
   Türkçe versiyon 30 gün boyunca Actions sayfasında indirilebilir durur.

## Sana düşenler

- Hiçbir şey zorunlu değil. İstersen Claude'a "rapor", "yeni bölüm", "Londra'dan sonra Paris'i yap" gibi
  şeyler söyleyebilirsin.
- Videolar zamanlanmış yüklendiği için YouTube kendiliğinden yayınlar.

## Dosyalar

| Yer | Ne |
| --- | --- |
| `engine/index.html` | 3D motor + ekran yazıları |
| `engine/render.py` | Kare yakalama, parça render, küçük resim |
| `tools/` | Harita hazırlama, doğrulama, müzik, birleştirme, YouTube |
| `cities/<şehir>/` | `city.json` (bölüm), `research.md` (kaynaklar), `preview/` (kontrol kareleri) |
| `config/schedule.json` | Yayın saatleri (UTC) |
| `uploads.json` | Yüklenen videolar ve linkleri |
| `RUNBOOK.md`, `CITY_SPEC.md` | Claude'un çalışma talimatları |
