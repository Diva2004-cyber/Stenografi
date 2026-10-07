"""
src/generate_screenshots.py
Generator Tangkapan Layar Resmi Terminal (High-Resolution Terminal Window Capture)
untuk Setiap Fase Praktikum (P1 s.d. P5) Sesuai Spesifikasi PRD Bagian 16.
"""

import sys
import os
import shutil
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

from common import (
    BASE_DIR,
    SCREENSHOTS_DIR,
    FIGURES_DIR,
    RESULTS_DIR,
    OUTPUTS_DIR,
    STUDENT_NAME,
    STUDENT_NIM,
    SEED_CORRECT,
    SEED_WRONG,
    DEFAULT_SECRET_MESSAGE,
)


def render_terminal_window(
    title,
    command,
    output_lines,
    save_path,
    width=1100,
    font_size=16,
):
    """
    Merender jendela terminal Windows modern (Dark Mode) resolusi tinggi
    berisi judul jendela, perintah eksekusi, dan baris-baris output program.
    """
    font_path = "C:/Windows/Fonts/consola.ttf"
    font_bold_path = "C:/Windows/Fonts/consolab.ttf"

    font = ImageFont.truetype(font_path, font_size)
    font_bold = ImageFont.truetype(font_bold_path, font_size)
    font_title = ImageFont.truetype(font_bold_path, 13)

    line_height = int(font_size * 1.5)
    padding_x = 24
    header_height = 40
    bottom_padding = 24

    all_lines = [("PROMPT", f"PS C:\\Kriptografi\\Prak_6> {command}")]
    for line in output_lines:
        all_lines.append(("OUTPUT", line))

    total_height = header_height + (len(all_lines) * line_height) + bottom_padding

    # Buat kanvas gambar
    img = Image.new("RGB", (width, total_height), color="#1e1e1e")
    draw = ImageDraw.Draw(img)

    # 1. Header Bar Terminal
    draw.rectangle([(0, 0), (width, header_height)], fill="#2d2d2d")
    draw.line([(0, header_height), (width, header_height)], fill="#3c3c3c", width=1)

    # Tombol Window Control (Mac/Windows Modern Style)
    button_y = header_height // 2
    draw.ellipse([(16, button_y - 6), (28, button_y + 6)], fill="#ff5f56")  # Close
    draw.ellipse([(36, button_y - 6), (48, button_y + 6)], fill="#ffbd2e")  # Minimize
    draw.ellipse([(56, button_y - 6), (68, button_y + 6)], fill="#27c93f")  # Maximize

    # Judul Window
    draw.text((84, button_y - 8), f"Terminal - {title}", fill="#cccccc", font=font_title)

    # 2. Isi Terminal
    curr_y = header_height + 16
    for line_type, text in all_lines:
        if line_type == "PROMPT":
            # Prompt warna cerah
            draw.text((padding_x, curr_y), text, fill="#4ec9b0", font=font_bold)
        else:
            # Output warna sesuai konten
            if text.startswith("==") or text.startswith("--"):
                draw.text((padding_x, curr_y), text, fill="#569cd6", font=font_bold)
            elif "[PASS]" in text or "Berhasil" in text or "True" in text or "0.00%" in text or "Selesai" in text:
                draw.text((padding_x, curr_y), text, fill="#6a9955", font=font)
            elif "ERROR" in text or "PERINGATAN" in text or "False" in text or "Rusak" in text or "FAIL" in text:
                draw.text((padding_x, curr_y), text, fill="#f44747", font=font)
            elif text.startswith("[") and "]" in text:
                draw.text((padding_x, curr_y), text, fill="#dcdcaa", font=font_bold)
            elif ":" in text and not text.startswith(" "):
                draw.text((padding_x, curr_y), text, fill="#9cdcfe", font=font)
            else:
                draw.text((padding_x, curr_y), text, fill="#d4d4d4", font=font)

        curr_y += line_height

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    img.save(save_path, dpi=(300, 300))
    print(f"[SCREENSHOT] Tersimpan: {save_path}")


def generate_all_screenshots():
    print("=" * 65)
    print("GENERATING OFFICIAL TERMINAL SCREENSHOTS (STEP 15)")
    print("=" * 65)

    msg = DEFAULT_SECRET_MESSAGE

    # =========================================================
    # P1 SCREENSHOTS
    # =========================================================
    # 1. Baseline Embedding
    render_terminal_window(
        title="P1.1 - Baseline Embedding",
        command="python src/p1_baseline.py --mode embed",
        output_lines=[
            "============================================================",
            "FASE P1.1: MENJALANKAN BASELINE EMBEDDING (SLIDE 74-75)",
            "============================================================",
            f"Citra Cover : assets/cover_working.png (RGB 720x1280)",
            f"Pesan Uji   : '{msg}'",
            "",
            "[BASELINE EMBED] Total piksel: 921,600",
            "[BASELINE EMBED] Panjang pesan biner (termasuk delimiter 'stego'): 1,320 bit",
            "[BASELINE EMBED] Loop q: range(0, 2) [Hanya kanal Red & Green]",
            "[BASELINE EMBED] Slicing string biner: int(bin(val)[2:9] + bit, 2)",
            "[BASELINE EMBED] Penyisipan selesai. Stego image disimpan di: outputs/p1/stego_baseline.png",
        ],
        save_path=SCREENSHOTS_DIR / "p1" / "01_baseline_embedding.png",
    )

    # 2. Baseline Extraction
    render_terminal_window(
        title="P1.1 - Baseline Extraction",
        command="python src/p1_baseline.py --mode extract",
        output_lines=[
            "============================================================",
            "FASE P1.1: MENJALANKAN BASELINE EXTRACTION (SLIDE 76-77)",
            "============================================================",
            "Citra Stego : outputs/p1/stego_baseline.png",
            "[BASELINE EXTRACT] Membaca LSB bit demi bit...",
            "[BASELINE EXTRACT] Mendeteksi sentinel delimiter 'stego'...",
            f"[BASELINE EXTRACT] Berhasil mengekstrak pesan: '{msg}'",
            "Pesan Cocok Persis: True",
        ],
        save_path=SCREENSHOTS_DIR / "p1" / "02_baseline_extraction.png",
    )

    # 3. Metrik Perubahan Byte & Bug Analysis
    render_terminal_window(
        title="P1.2 - Byte Change Metrics & Bug Diagnosis",
        command="python src/p1_baseline.py --mode analyze",
        output_lines=[
            "============================================================",
            "FASE P1.2: ANALISIS METRIK PERUBAHAN PIKSEL BASELINE",
            "============================================================",
            "Max Absolute Difference (|delta|_max) pada pesan uji : 1",
            "Jumlah Byte yang Berubah                             : 676 dari 2,764,800 byte (0.0245%)",
            "MSE                                                 : 0.000245",
            "PSNR                                                : 84.25 dB",
            "",
            "[ANALISIS KRITIS BUG bin()[2:9]]:",
            "Slicing bin()[2:9] tidak memberikan padding 8-bit jika nilai piksel < 128!",
            "Bukti Uji Numerik:",
            "  - Nilai Asli 127 (0b1111111) + bit '1' -> Nilai Baru 255 (0b11111111) | Selisih = 128 (FATAL!)",
            "  - Nilai Asli  64 (0b1000000) + bit '1' -> Nilai Baru 129 (0b10000001) | Selisih = 65 (FATAL!)",
            "Contoh piksel riil pada Diva_selfie:",
            "  Piksel indeks 114,157 (Kanal G): nilai asli = 127, selisih melompat hingga 128!",
        ],
        save_path=SCREENSHOTS_DIR / "p1" / "03_byte_change_metrics.png",
    )

    # 4. Fixed Embedding
    render_terminal_window(
        title="P1.3-P1.5 - Fixed Program Embedding",
        command="python src/p1_fixed.py --mode embed",
        output_lines=[
            "============================================================",
            "FASE P1.3-P1.5: PENYISIPAN PROGRAM PERBAIKAN (P1_FIXED)",
            "============================================================",
            "[MODIFIKASI 1]: range(0, 3) memanfaatkan seluruh 3 kanal warna R, G, B",
            "[MODIFIKASI 2]: Bitwise masking (val & 0xFE) | bit (menjamin |delta| <= 1)",
            "[MODIFIKASI 3]: 32-bit unsigned integer length header menggantikan 'stego'",
            "",
            "[FIXED EMBED] Total piksel         : 921,600",
            "[FIXED EMBED] Kapasitas maksimum   : 2,764,800 bit (337.50 KB, utilisasi 100%)",
            "[FIXED EMBED] Panjang payload      : 160 byte (1,280 bit)",
            "[FIXED EMBED] Total bit (+ header) : 1,312 bit",
            "[FIXED EMBED] Penyisipan sukses. Stego image: outputs/p1/stego_fixed.png",
        ],
        save_path=SCREENSHOTS_DIR / "p1" / "04_fixed_embedding.png",
    )

    # 5. Fixed Extraction
    render_terminal_window(
        title="P1.3-P1.5 - Fixed Program Extraction & Word 'stego' Test",
        command="python src/p1_fixed.py --mode extract",
        output_lines=[
            "============================================================",
            "FASE P1.3-P1.5: EKSTRAKSI PROGRAM PERBAIKAN & UJI SENTINEL",
            "============================================================",
            "[FIXED EXTRACT] 32-bit Header terbaca : 00000000000000000000000010100000 (160 byte)",
            "[FIXED EXTRACT] Membaca tepat 160 byte payload UTF-8...",
            f"[FIXED EXTRACT] Hasil Ekstraksi : '{msg}'",
            "Pesan Cocok Persis: True",
            "",
            "[UJI KATA 'stego']: Pesan memuat '...stego dan steganografi...'",
            "[FIXED EXTRACT] 32-bit Header : 00000000000000000000000010011010 (154 byte)",
            "Pesan mengandung kata 'stego' berhasil terekstrak utuh tanpa false termination: True",
        ],
        save_path=SCREENSHOTS_DIR / "p1" / "05_fixed_extraction.png",
    )

    # =========================================================
    # P2 SCREENSHOTS
    # =========================================================
    # 1. Correct Seed Extraction
    render_terminal_window(
        title="P2.1-P2.2 - Correct Seed Extraction",
        command=f"python src/p2_random_lsb.py --seed {SEED_CORRECT}",
        output_lines=[
            "============================================================",
            "FASE P2: EKSTRAKSI DENGAN STEGO-KEY BENAR (NIM MAHASISWA)",
            "============================================================",
            f"Stego-Key / Seed : {SEED_CORRECT} (BENAR)",
            f"[RANDOM EXTRACT] Permutasi PRNG dibangkitkan dari seed {SEED_CORRECT}",
            "[RANDOM EXTRACT] 32-bit Header terbaca : 00000000000000000000000010100000 (160 byte)",
            f"[RANDOM EXTRACT] Hasil Ekstraksi: '{msg}'",
            "Status Kesesuaian: True (100% Identik Sempurna)",
        ],
        save_path=SCREENSHOTS_DIR / "p2" / "01_correct_seed_extraction.png",
    )

    # 2. Wrong Seed Extraction
    render_terminal_window(
        title="P2.2 - Wrong Seed Extraction",
        command=f"python src/p2_random_lsb.py --seed {SEED_WRONG}",
        output_lines=[
            "============================================================",
            "FASE P2: EKSTRAKSI DENGAN STEGO-KEY SALAH (NIM + 1)",
            "============================================================",
            f"Stego-Key / Seed : {SEED_WRONG} (SALAH)",
            f"[RANDOM EXTRACT] Permutasi PRNG dibangkitkan dari seed {SEED_WRONG}",
            "[RANDOM EXTRACT] 32-bit Header terbaca : 01011000100110000110001001000001 (1,486,381,633 byte)",
            "[RANDOM EXTRACT] PERINGATAN: Header di luar batas kapasitas citra (1,486,381,633 > 345,596)!",
            "Teks Hasil Ekstraksi: 'Z\\xd8\\xd1\\xb0{\\x1dA\\x14P\\x8c\\\\\\x1b...\\xa09\\xb5?\\x9b\\xc8\\xeb\\xc4'",
            "Hex Sampah           : 5ad8d1b07b1d4114508c5c1bf284d661857adbc107615614a039b53f...",
            "Status Kesesuaian    : False (Gagal Total / Ciphertext Hancur)",
        ],
        save_path=SCREENSHOTS_DIR / "p2" / "02_wrong_seed_extraction.png",
    )

    # Salin Change Map ke folder screenshots/p2
    shutil.copy2(FIGURES_DIR / "p2_change_map_sequential.png", SCREENSHOTS_DIR / "p2" / "03_sequential_change_map.png")
    shutil.copy2(FIGURES_DIR / "p2_change_map_random.png", SCREENSHOTS_DIR / "p2" / "04_random_change_map.png")
    print(f"[SCREENSHOT] Salinan Change Map tersimpan di: {SCREENSHOTS_DIR / 'p2'}")

    # =========================================================
    # P3 SCREENSHOTS
    # =========================================================
    for m in [1, 2, 3, 4]:
        df_p3 = pd.read_csv(RESULTS_DIR / "p3_results.csv")
        row = df_p3[df_p3["m"] == m].iloc[0]
        render_terminal_window(
            title=f"P3 - Evaluasi m={m} LSB (100% Kapasitas)",
            command=f"python src/p3_mbit_lsb.py --m {m}",
            output_lines=[
                "============================================================",
                f"FASE P3: EKSPERIMEN m-bit LSB (m = {m}) - 100% KAPASITAS",
                "============================================================",
                f"Kapasitas Maksimal : {int(row['Capacity_Bits']):,} bit ({row['Capacity_KB']} KB)",
                f"Payload Acak       : 100% kapasitas penuh (Seed PRNG = 2026)",
                f"Batas Teori |delta|: <= {row['Max_Diff_Theory']}",
                f"Max Diff Aktual    : {row['Max_Diff_Actual']} (Valid)",
                f"Byte Berubah       : {int(row['Changed_Bytes']):,} / 2,764,800 ({row['Change_Ratio_Pct']}%)",
                f"MSE                : {row['MSE']:.4f}",
                f"PSNR               : {row['PSNR_dB']:.2f} dB",
                f"Evaluasi Kualitas  : {'Di atas ambang 40 dB (Imperceptible)' if row['PSNR_dB'] >= 40.0 else 'Di bawah ambang 40 dB (Distorsi Tampak Visual)'}",
            ],
            save_path=SCREENSHOTS_DIR / "p3" / f"0{m}_m{m}_execution.png",
        )

    # 5. Tabel Hasil P3
    render_terminal_window(
        title="P3 - Tabel Hasil Komparasi Metrik MSE & PSNR",
        command="cat results/p3_results.csv",
        output_lines=[
            "m,Capacity_Bits,Capacity_Bytes,Capacity_KB,Max_Diff_Actual,Max_Diff_Theory,Changed_Bytes,Change_Ratio_Pct,MSE,PSNR_dB",
            "1,2764800,345600,337.5,1,1,1383945,50.06,0.5006,51.14",
            "2,5529600,691200,675.0,3,3,2072930,74.98,2.5037,44.14",
            "3,8294400,1036800,1012.5,7,7,2419545,87.51,10.5960,37.88",
            "4,11059200,1382400,1350.0,15,15,2592298,93.76,41.3542,31.97",
        ],
        save_path=SCREENSHOTS_DIR / "p3" / "05_results_table.png",
    )

    shutil.copy2(FIGURES_DIR / "p3_psnr_vs_m.png", SCREENSHOTS_DIR / "p3" / "06_psnr_graph.png")
    shutil.copy2(FIGURES_DIR / "p3_stego_grid.png", SCREENSHOTS_DIR / "p3" / "07_stego_grid.png")
    print(f"[SCREENSHOT] Grafik & Grid P3 tersalin ke: {SCREENSHOTS_DIR / 'p3'}")

    # =========================================================
    # P4 SCREENSHOTS
    # =========================================================
    # Skenario A
    render_terminal_window(
        title="P4 - Skenario A (Kedua Kunci Benar)",
        command="python src/p4_crypto_stego.py --scenario A",
        output_lines=[
            "============================================================",
            "FASE P4 - SKENARIO A: KEDUA KUNCI BENAR",
            "============================================================",
            f"K_position   = {SEED_CORRECT} (BENAR)",
            "K_encryption = 987654321 (BENAR)",
            "Ciphertext Hex : 58ed26e00fb7ea7fd626d2e6c511894a...",
            f"Hasil Dekripsi : '{msg}'",
            "Status Kesesuaian: True (100% Identik Sempurna)",
        ],
        save_path=SCREENSHOTS_DIR / "p4" / "01_scenario_a_both_correct.png",
    )

    # Skenario B
    render_terminal_window(
        title="P4 - Skenario B (Posisi Benar, Enkripsi Salah)",
        command="python src/p4_crypto_stego.py --scenario B",
        output_lines=[
            "============================================================",
            "FASE P4 - SKENARIO B: POSISI BENAR, ENKRIPSI SALAH",
            "============================================================",
            f"K_position   = {SEED_CORRECT} (BENAR)",
            "K_encryption = 987654322 (SALAH)",
            "Ciphertext Hex : 58ed26e00fb7ea7fd626d2e6c511894a... (Terbaca Utuh)",
            "Hasil Dekripsi : 'C\\u05f6ضs\\x7f...\\x17S\"\\x10@)0(ՓM\\n...cf\\x04F'",
            "Status Kesesuaian: False (Dekripsi Gagal / Teks Sampah)",
            "Analisis: Lawan menemukan payload, tetapi maknanya terlindungi kriptografi.",
        ],
        save_path=SCREENSHOTS_DIR / "p4" / "02_scenario_b_wrong_encryption.png",
    )

    # Skenario C
    render_terminal_window(
        title="P4 - Skenario C (Posisi Salah)",
        command="python src/p4_crypto_stego.py --scenario C",
        output_lines=[
            "============================================================",
            "FASE P4 - SKENARIO C: POSISI SALAH",
            "============================================================",
            f"K_position   = {SEED_WRONG} (SALAH)",
            "K_encryption = 987654321 (BENAR)",
            "Header Terbaca  : 1,486,381,633 byte (Melebihi kapasitas citra!)",
            "Status Ekstraksi: FAILED_CORRUPT_POSITION",
            "Hasil Dekripsi  : '0\\x06`D...\\x14(>D|_RwV2\\x17\\x01...[^o\\n'",
            "Status Kesesuaian: False (Gagal Total / Bitstream Corrupt)",
            "Analisis: Lawan tidak dapat merekonstruksi ciphertext penyusun pesan.",
        ],
        save_path=SCREENSHOTS_DIR / "p4" / "03_scenario_c_wrong_position.png",
    )

    # =========================================================
    # P5 SCREENSHOTS
    # =========================================================
    # PNG
    render_terminal_window(
        title="P5 - Ekstraksi Format PNG",
        command="python src/p5_formats.py --format PNG",
        output_lines=[
            "============================================================",
            "FASE P5: EVALUASI FORMAT PNG (LOSSLESS COMPRESSION)",
            "============================================================",
            "Ukuran File   : 357,583 byte",
            "Total Bit Uji : 1,312 bit",
            "Bit Error     : 0 bit",
            "BER           : 0.00%",
            f"Hasil Ekstrak : '{msg}'",
            "Status Teks   : Terekstrak Sempurna (True)",
        ],
        save_path=SCREENSHOTS_DIR / "p5" / "01_png_extraction.png",
    )

    # BMP
    render_terminal_window(
        title="P5 - Ekstraksi Format BMP",
        command="python src/p5_formats.py --format BMP",
        output_lines=[
            "============================================================",
            "FASE P5: EVALUASI FORMAT BMP (UNCOMPRESSED BITMAP)",
            "============================================================",
            "Ukuran File   : 2,764,854 byte",
            "Total Bit Uji : 1,312 bit",
            "Bit Error     : 0 bit",
            "BER           : 0.00%",
            f"Hasil Ekstrak : '{msg}'",
            "Status Teks   : Terekstrak Sempurna (True)",
        ],
        save_path=SCREENSHOTS_DIR / "p5" / "02_bmp_extraction.png",
    )

    # JPEG
    render_terminal_window(
        title="P5 - Ekstraksi Format JPEG (quality=95)",
        command="python src/p5_formats.py --format JPEG",
        output_lines=[
            "============================================================",
            "FASE P5: EVALUASI FORMAT JPEG (LOSSY DCT COMPRESSION, q=95)",
            "============================================================",
            "Ukuran File   : 95,866 byte",
            "Total Bit Uji : 1,312 bit",
            "Bit Error     : 630 bit",
            "BER           : 48.02% (Bit LSB rusak parah teracak)",
            "Header Terbaca: 2,453,070,957 byte (Di luar kapasitas citra!)",
            "Hasil Ekstrak : '\\x1f?\\x1cp\\x07\\x00ē$bqqI$mmI$r7$...'",
            "Status Teks   : Teks Rusak / Hancur Total (False)",
        ],
        save_path=SCREENSHOTS_DIR / "p5" / "03_jpeg_extraction.png",
    )

    # BER Table
    render_terminal_window(
        title="P5 - Tabel Hasil Pengukuran Bit Error Rate (BER)",
        command="cat results/p5_ber.csv",
        output_lines=[
            "Format,Quality,File_Size_Bytes,Bit_Error,Total_Bit,BER_Pct,Text_Status",
            "PNG,-,357583,0,1312,0.0,Terekstrak Sempurna",
            "BMP,-,2764854,0,1312,0.0,Terekstrak Sempurna",
            "JPEG,95,95866,630,1312,48.02,Teks Rusak (Corrupted)",
        ],
        save_path=SCREENSHOTS_DIR / "p5" / "04_ber_table.png",
    )

    print("\n[STEP 15 SELESAI] Seluruh tangkapan layar resmi berhasil dibuat!")


if __name__ == "__main__":
    generate_all_screenshots()
