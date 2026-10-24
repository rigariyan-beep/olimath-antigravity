# 🦁 OliMath Adventure by antigravity

Platform Latihan Olimpiade Matematika SD (Kelas 1–6) Berbasis Petualangan Gamifikasi RPG, Auto-Update Soal Harian dengan Google Gemini AI, Papan Coret Sentuh Interaktif, Duel Bos Monster, Simulasi Tryout Standar OSN/SASMO/Kangaroo, dan Cetak Sertifikat Juara.

---

## 🌟 Fitur Utama

1. **Auto-Fetch Database Soal (`questions_db.json`)**:
   - Terkoneksi secara langsung ke repository GitHub untuk selalu menyajikan soal-soal olimpiade terbaru tanpa perlu deploy ulang web.
2. **Live AI Question Generator**:
   - Tombol "✨ Minta AI Buat Soal Baru" yang dapat meracik soal baru secara *real-time* berbasis tema petualangan (Astronot, Ekspedisi Satwa, dsb.) menggunakan Google Gemini REST API.
3. **Papan Coret-Coret (Touch Scratchpad)**:
   - Kanvas kalkulasi sentuh ramah tablet & HP dengan berbagai warna pensil, penghapus, dan pembersih kanvas untuk memudahkan anak menghitung rumus.
4. **RPG Boss Battle (Duel Monster Matematika)**:
   - Mode duel RPG seru! Setiap jawaban benar melancarkan serangan sihir matematika pada bos monster (*Drakon Pola*, *Lupus Interval*, *Phoenix Geometri*, dll.).
5. **Simulasi Tryout & Rapor Diagnostik**:
   - Ujian berbatas waktu (10 soal / 15 menit) dengan analisis penguasaan per topik (Aritmatika, Geometri, Aljabar, Teori Bilangan, Kombinatorika).
6. **Piagam & Sertifikat Juara**:
   - Piagam digital resmi dengan nama anak, kelas, skor, dan medali (Emas, Perak, Perunggu) yang bisa langsung diunduh dalam format PNG atau dicetak.
7. **Cloud Sync / Kode Progres**:
   - Fitur ekspor/impor kode progres dengan 1 klik sehingga koin, level, dan medali anak dapat dipindahkan antar HP, tablet, dan laptop.
8. **Synthesized Web Audio SFX**:
   - Efek suara interaktif (*chime*, *buzz*, *coin clink*, *fanfare*) menggunakan Web Audio API murni tanpa memerlukan file audio eksternal.

---

## 📂 Struktur File Proyek

```
Kids_Math/
├── index.html                           # Aplikasi web SPA utama (Tailwind CSS, Web Audio, Canvas)
├── questions_db.json                    # Database soal olimpiade Kelas 1-6 (standar OSN/SASMO/AMC 8)
├── scripts/
│   └── generate_daily_questions.py      # Script Python otomasi generate 6 soal harian dengan Gemini AI
├── .github/
│   └── workflows/
│       └── auto_update_questions.yml    # GitHub Actions cron (00:00 WIB) untuk auto-commit soal baru
└── README.md                            # Panduan instalasi dan dokumentasi
```

---

## 🚀 Panduan Setup & Deploy

### 1. Mengaktifkan GitHub Pages (Gratis)
1. Buka repository Anda di GitHub: `https://github.com/rigariyan-beep/olimath-antigravity`.
2. Klik tab **Settings** > **Pages** (di bilah menu sebelah kiri).
3. Pada bagian **Build and deployment**:
   - **Source**: Pilih `Deploy from a branch`.
   - **Branch**: Pilih `main`, dan foldernya `/ (root)`.
4. Klik **Save**.
5. Tunggu sekitar 1-2 menit, situs Anda akan live di:
   `https://rigariyan-beep.github.io/olimath-antigravity/`

### 2. Mengaktifkan Auto-Update Soal Harian (GitHub Actions)
Agar GitHub Actions dapat memanggil Google Gemini API setiap hari pukul 00:00 WIB:
1. Masuk ke **Settings** repository Anda di GitHub.
2. Pilih menu **Secrets and variables** > **Actions**.
3. Klik tombol **New repository secret**.
4. Isi:
   - **Name**: `GEMINI_API_KEY`
   - **Secret**: *(Masukkan API Key Google Gemini Anda)*
5. Klik **Add secret**.

> **Note**: Workflow juga dapat dijalankan secara manual kapan saja melalui tab **Actions** > **Auto Update Daily Olympiad Questions** > **Run workflow**.

---

## 🛠️ Menjalankan Secara Lokal

Cukup buka file `index.html` langsung di browser Anda, atau gunakan server lokal:
```bash
# Menggunakan Python
python -m http.server 8000
```
Buka browser di `http://localhost:8000`.

---
*Dibuat dengan ❤️ oleh Antigravity AI untuk Generasi Emas Juara Olimpiade Matematika Indonesia.*