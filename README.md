# Praktikum Kriptografi — Modul 6: Steganografi Citra Digital

Repositori ini memuat implementasi, eksperimen, analisis empiris Steganografi Citra Digital
---

## 📌 Identitas Mahasiswa & Parameter Khusus

- **Nama Lengkap**: Diva Prayoga Alpariji Putra
- **NIM**: 237006173
- **Parameter Khusus $A$**: $A = 3$ (Digit satuan dari NIM `237006173`)
- **Stego-Key Seed (Fase P2)**: `237006173` (Kunci Benar) | `237006174` (Kunci Salah)
- **Kunci Kripto-Stego (Fase P4)**:
  - $K_{\text{position}} = 237006173$ (Stego-key posisi spasial)
  - $K_{\text{encryption}} = 987654321$ (Stream cipher XOR key)
- **Citra Cover Primer**: `assets/Diva_selfie.jpeg` (dan salinan lossless `assets/cover_working.png`)
  - Resolusi: $720 \times 1280$ piksel (TrueColor 24-bit RGB)
  - Total Ukuran: $2.764.800$ byte (`uint8`)
  - Kapasitas 1-bit LSB (3 kanal): $337,50$ KB ($2.764.800$ bit)

---

## 🎯 Ringkasan Modul Eksperimen

1. **Fase P1 — Analisis & Perbaikan Program**
   - Mendiagnosis bug string slicing `bin()[2:9]` pada nilai piksel $< 128$ yang menyebabkan lonjakan nilai piksel drastis hingga selisih $\Delta = 128$.
   - Memperbaiki pembatasan kanal warna `for q in range(0, 2)` menjadi 3 kanal penuh `range(0, 3)` (utilisasi kapasitas meningkat dari $66,67\%$ ke $100\%$).
   - Menggantikan delimiter string `"stego"` dengan **Header Panjang 32-bit** (*unsigned integer*) guna mencegah pemotongan dini (*false positive early truncation*).
   - Menjamin secara matematis $\Delta_{\max} \le 1$ menggunakan operasi bitwise murni `(val & ~1) | bit`.

2. **Fase P2 — LSB Acak dengan Stego-Key**:
   - Mengimplementasikan penyisipan acak berbasis permutasi PRNG deterministik NumPy `default_rng(seed)` (*sampling without replacement* / *zero collision*).
   - Membuktikan ketahanan ekstraksi: seed benar (`237006173`) memulihkan pesan $100\%$ utuh, sedangkan seed salah (`237006174`) menghasilkan header invalid ($1.486.381.633$ byte) dan data terkorupsi total.
   - Menganalisis *Change Map* biner: sekuensial terkonsentrasi pada baris 0 (bounding box $1 \times 438$), sedangkan acak tersebar merata di seluruh citra (bounding box $1278 \times 719$).

3. **Fase P3 — Eksperimen $m$-bit LSB dan Kualitas Citra**
   - Menguji $m \in \{1, 2, 3, 4\}$ pada kapasitas penuh ($100\%$).
   - Membuktikan teorema selisih maksimum $\Delta_{\max} = 2^m - 1$ ($m=1 \to 1$, $m=2 \to 3$, $m=3 \to 7$, $m=4 \to 15$).
   - Mengukur metrik MSE dan PSNR:
     - $m=1$: Kapasitas $337,5$ KB, MSE $0,5006$, PSNR $51,14$ dB (*imperceptible* sempurna).
     - $m=2$: Kapasitas $675,0$ KB, MSE $2,5037$, PSNR $44,14$ dB (kualitas tinggi).
     - $m=3$: Kapasitas $1.012,5$ KB, MSE $10,5960$, PSNR $37,88$ dB (derau halus mulai tampak).
     - $m=4$: Kapasitas $1.350,0$ KB, MSE $41,3542$, PSNR $31,97$ dB (*false contouring* dan distorsi nyata).

4. **Fase P4 — Kombinasi Kriptografi dan Steganografi**:
   - Merancang arsitektur pertahanan berlapis (*Defense-in-Depth*): Plaintext $\to$ Stream Cipher XOR PRNG ($K_{\text{enc}}$) $\to$ Ciphertext $\to$ LSB Acak ($K_{\text{pos}}$) $\to$ Stego-image.
   - Menguji 3 skenario:
     - Skenario A (Kedua kunci benar): Plaintext dipulihkan $100\%$ eksak.
     - Skenario B ($K_{\text{pos}}$ benar, $K_{\text{enc}}$ salah): Ciphertext terbaca utuh, dekripsi menghasilkan derau acak (*confidentiality* terjaga).
     - Skenario C ($K_{\text{pos}}$ salah): Header invalid, ekstraksi gagal total (*payload existence* tersembunyi).

5. **Fase P5 — Pengaruh Format File dan Ketahanan**:
   - Menguji ketahanan pesan pada format PNG (lossless), BMP (uncompressed), dan JPEG (lossy transform Quality 95).
   - Pengukuran *Bit Error Rate* (BER):
     - PNG: BER $0,00\%$ (0 bit eror).
     - BMP: BER $0,00\%$ (0 bit eror).
     - JPEG: BER $48,02\%$ (630 bit eror dari 1.312 bit) $\to$ rusak total akibat kuantisasi DCT blok $8 \times 8$.

6. **Bonus — Steganalisis Visual dan Uji Statistik Chi-Square**:
   - Ekstraksi bidang LSB $I_{\text{LSB}} = (I \ \& \ 1) \times 255$ pada muatan $50\%$ kapasitas ($1.382.400$ bit).
   - Terlihat garis demarkasi horizontal tajam pada baris $y = 640$ memisahkan area derau acak seragam (atas) dan tekstur alami cover (bawah).
   - Uji statistik *Pairs of Values* (PoV) Chi-Square: nilai $\chi^2$ separuh atas anjlok drastis $97,60\%$ (dari $3.758,10$ ke $90,20$), membuktikan kerentanan LSB terhadap detektor statistik otomatis.

---

## 🛠️ Prasyarat & Dependensi

Proyek ini dibangun menggunakan Python 3.13 dan pustaka standar:
```bash
pip install -r requirements.txt
```

Isi `requirements.txt`:
- `numpy>=2.2.0`
- `pillow>=11.0.0`
- `matplotlib>=3.10.0`
- `pymupdf>=1.25.0`

---

## 🚀 Panduan Menjalankan Eksperimen

### 1. Menjalankan Seluruh Pipeline Otomatis (Master Test Suite)
Untuk mereproduksi seluruh hasil eksperimen, menghasilkan citra stego, grafik, tabel metrik, dan memvalidasi kebenaran end-to-end:
```bash
python src/run_all.py
```
*Status: 18 dari 18 unit test PASS (100% verifikasi sukses).*

### 2. Menjalankan Modul Individual
- **Fase P1 (Baseline & Fixed)**:
  ```bash
  python src/p1_baseline.py
  python src/p1_fixed.py
  ```
- **Fase P2 (LSB Acak & Stego-key)**:
  ```bash
  python src/p2_random_lsb.py
  ```
- **Fase P3 (Multi-bit $m=1..4$)**:
  ```bash
  python src/p3_mbit_lsb.py
  ```
- **Fase P4 (Kripto-Steganografi)**:
  ```bash
  python src/p4_crypto_stego.py
  ```
- **Fase P5 (Ketahanan Format PNG/BMP/JPEG)**:
  ```bash
  python src/p5_formats.py
  ```
- **Bonus (Steganalisis LSB & Chi-Square)**:
  ```bash
  python src/bonus_steganalysis.py
  ```
---

## 📁 Struktur Direktori Proyek

```text
c:\Kriptografi\Prak_6\
├── README.md                       # Panduan teknis & ringkasan eksekutif repositori
├── requirements.txt                # Dependensi pustaka Python
├── assets/                         # Direktori citra cover input
│   ├── Diva_selfie.jpeg            # Foto selfie asli mahasiswa Diva Prayoga Alpariji Putra
│   └── cover_working.png           # Salinan kerja lossless format PNG (720x1280 RGB)
├── figures/                        # Grafik, visualisasi komparasi, dan grid hasil
│   ├── bonus_lsb_planes.png        # Bidang LSB cover vs stego (batas baris 640)
│   ├── p2_change_map_comparison.png# Komparasi change map biner sekuensial vs acak
│   ├── p3_psnr_vs_m.png            # Grafik kurva degradasi PSNR vs nilai m
│   └── p3_stego_grid.png           # Grid komparasi visual 4 citra stego m=1..4
├── outputs/                        # Berkas citra stego hasil penyisipan eksperimen
│   ├── p1/                         # Stego-image baseline dan fixed
│   ├── p2/                         # Stego-image kunci benar dan kunci salah
│   ├── p3/                         # Stego-image m=1, m=2, m=3, m=4
│   ├── p4/                         # Stego-image sistem kripto-steganografi
│   ├── p5/                         # Berkas stego format PNG, BMP, JPEG (q=95)
│   └── bonus/                      # Citra stego muatan 50% untuk steganalisis
├── results/                        # Data empiris terstruktur (JSON & CSV)
│   ├── p1_baseline_metrics.json    # Metrik program baseline slide
│   ├── p1_fixed_metrics.json       # Metrik program fixed
│   ├── p2_metrics.json             # Metrik LSB acak & bounding box change map
│   ├── p3_results.json / .csv      # Tabel hasil m-bit LSB (MSE, PSNR, kapasitas)
│   ├── p4_results.json             # Hasil pengujian 3 skenario kunci kripto-stego
│   ├── p5_results.json / .csv      # Tabel Bit Error Rate (BER) format berkas
│   ├── bonus_steganalysis.json     # Hasil perhitungan Chi-Square Pairs of Values
│   └── pipeline_summary.json       # Rangkuman status validasi 18/18 PASS
├── screenshots/                    # Tangkapan layar terminal output resolusi tinggi
│   ├── p1/                         # 5 screenshot eksekusi P1 baseline & fixed
│   ├── p2/                         # 4 screenshot eksekusi P2 & change map
│   ├── p3/                         # 7 screenshot eksekusi P3 m=1..4 & tabel
│   ├── p4/                         # 3 screenshot eksekusi P4 tiga skenario
│   └── p5/                         # 4 screenshot eksekusi P5 & tabel BER
├── src/                            # Kode sumber Python modular
│   ├── common.py                   # Modul utilitas biner, I/O, metrik MSE/PSNR/BER
│   ├── p1_baseline.py              # Eksekusi & pembuktian bug slide 74-77
│   ├── p1_fixed.py                 # Algoritma bitwise fixed 3-kanal & 32-bit header
│   ├── p2_random_lsb.py            # Permutasi PRNG stego-key & change map
│   ├── p3_mbit_lsb.py              # Generator eksperimen multi-bit LSB
│   ├── p4_crypto_stego.py          # Sistem pertahanan berlapis (XOR stream + LSB acak)
│   ├── p5_formats.py               # Pengujian ketahanan format PNG, BMP, JPEG
│   ├── bonus_steganalysis.py       # Ekstraksi bidang LSB & uji statistik Chi-Square
│   ├── run_all.py                  # Master test suite & validator otomatis
```

---
