"""
src/p1_fixed.py
Implementasi P1 Fixed: Perbaikan Program Steganografi Slide Dosen.

Perbaikan yang diterapkan:
1. P1.3: Menggunakan ketiga kanal warna RGB (range(0, 3)), meningkatkan utilisasi kapasitas dari 66.67% ke 100%.
2. P1.4: Mengganti manipulasi string bin()[2:9] dengan operasi bitwise langsung ((val & 0xFE) | bit),
        menjamin perubahan maksimum |delta| <= 1 untuk semua nilai piksel (termasuk nilai < 128).
3. P1.5: Mengganti sentinel text delimiter "stego" dengan 32-bit unsigned integer length header,
        menghilangkan risiko false termination jika pesan mengandung kata "stego".
"""

import os
import json
import numpy as np
from PIL import Image

from common import (
    WORKING_COVER_PATH,
    OUTPUTS_DIR,
    RESULTS_DIR,
    DEFAULT_SECRET_MESSAGE,
    validate_and_prepare_cover,
    calc_diff_stats,
    calc_mse,
    calc_psnr,
)


def EmbeddingPesanFixed(cover_path, pesan, stego_path):
    """
    Penyisipan pesan LSB 1-bit yang telah diperbaiki:
    - 32-bit length header + UTF-8 payload
    - Menggunakan ketiga kanal RGB (range(0, 3))
    - Bitwise LSB masking ((val & 0xFE) | bit)
    """
    citra = Image.open(cover_path, "r")
    lebar, tinggi = citra.size
    larik_pixel = np.array(list(citra.getdata()), dtype=np.uint8)

    if citra.mode == "RGB":
        n = 3
    else:
        n = 1

    total_pixel = larik_pixel.size // n  # jumlah piksel dalam citra
    kapasitas_teoritis_bit = total_pixel * n  # 1 bit per byte pada semua kanal

    # P1.5: Encode pesan ke bytes UTF-8 dan buat 32-bit length header
    if isinstance(pesan, str):
        payload_bytes = pesan.encode("utf-8")
    else:
        payload_bytes = bytes(pesan)

    payload_len_bytes = len(payload_bytes)

    # 32-bit unsigned integer header (panjang dalam byte)
    # MODIFIED FROM SLIDE:
    # Replaced sentinel delimiter "stego" with explicit 32-bit length header
    header_biner = format(payload_len_bytes, "032b")

    # Payload bits
    payload_biner = "".join([format(b, "08b") for b in payload_bytes])
    total_bit_stream = header_biner + payload_biner
    total_bits_to_embed = len(total_bit_stream)

    print(f"[FIXED EMBED] Total piksel         : {total_pixel:,}")
    print(f"[FIXED EMBED] Kapasitas maksimum   : {kapasitas_teoritis_bit:,} bit ({kapasitas_teoritis_bit / 8 / 1024:.2f} KB)")
    print(f"[FIXED EMBED] Panjang payload      : {payload_len_bytes} byte ({len(payload_biner)} bit)")
    print(f"[FIXED EMBED] Total bit (+ 32b hdr): {total_bits_to_embed} bit")

    if total_bits_to_embed > kapasitas_teoritis_bit:
        raise ValueError(
            f"Ukuran pesan ({total_bits_to_embed} bit) melebihi kapasitas citra ({kapasitas_teoritis_bit} bit)!"
        )

    # Sisipkan bit-bit pesan pada LSB setiap byte kanal warna
    index = 0
    # MODIFIED FROM SLIDE:
    # 1. Using range(0, 3) so that all 3 channels (Red, Green, Blue) are fully utilized.
    # 2. Replaced string-based binary concatenation with direct LSB bitwise operation
    #    so only the least significant bit is modified: (val & 0b11111110) | bit
    for p in range(total_pixel):
        for q in range(0, n):  # MODIFIED: range(0, 3) untuk RGB
            if index < total_bits_to_embed:
                bit_val = int(total_bit_stream[index])
                # Operasi bitwise langsung menjamin |delta| <= 1 untuk semua nilai piksel (0 s.d. 255)
                larik_pixel[p][q] = (larik_pixel[p][q] & 0xFE) | bit_val
                index += 1
            else:
                break
        if index >= total_bits_to_embed:
            break

    larik_pixel = larik_pixel.reshape(tinggi, lebar, n)
    stego_image = Image.fromarray(larik_pixel.astype("uint8"))
    stego_image.save(stego_path, format="PNG")
    print(f"[FIXED EMBED] Penyisipan sukses. Stego image tersimpan di: {stego_path}")
    return True


def EkstraksiPesanFixed(stego_path):
    """
    Ekstraksi pesan LSB 1-bit yang telah diperbaiki:
    - Membaca 32-bit header untuk mengetahui jumlah byte pesan
    - Membaca tepat jumlah byte payload yang ditentukan header
    - Menggunakan ketiga kanal RGB (range(0, 3))
    - Decode UTF-8 langsung tanpa bergantung pada sentinel string
    """
    citra = Image.open(stego_path, "r")
    larik_pixel = np.array(list(citra.getdata()), dtype=np.uint8)

    if citra.mode == "RGB":
        n = 3
    else:
        n = 1

    total_pixel = larik_pixel.size // n

    # Langkah 1: Ekstraksi 32-bit header pertama
    header_bits = ""
    index = 0
    p_curr = 0
    q_curr = 0

    while index < 32 and p_curr < total_pixel:
        # MODIFIED FROM SLIDE: Ambil bit LSB via bitwise AND bukan string slice
        header_bits += str(larik_pixel[p_curr][q_curr] & 1)
        index += 1
        q_curr += 1
        if q_curr >= n:
            q_curr = 0
            p_curr += 1

    payload_len_bytes = int(header_bits, 2)
    payload_total_bits = payload_len_bytes * 8
    print(f"[FIXED EXTRACT] 32-bit Header terbaca : {header_bits} (Nilai desimal: {payload_len_bytes} byte)")

    # Langkah 2: Ekstraksi tepat payload_total_bits
    payload_bits = ""
    bits_read = 0
    while bits_read < payload_total_bits and p_curr < total_pixel:
        payload_bits += str(larik_pixel[p_curr][q_curr] & 1)
        bits_read += 1
        q_curr += 1
        if q_curr >= n:
            q_curr = 0
            p_curr += 1

    if bits_read < payload_total_bits:
        raise ValueError("Citra berakhir sebelum seluruh bit payload terbaca!")

    # Langkah 3: Konversi bitstream ke bytes UTF-8
    payload_bytes = bytearray()
    for i in range(0, len(payload_bits), 8):
        byte_val = int(payload_bits[i : i + 8], 2)
        payload_bytes.append(byte_val)

    extracted_text = payload_bytes.decode("utf-8", errors="replace")
    print(f"[FIXED EXTRACT] Berhasil mengekstrak {len(payload_bytes)} byte pesan.")
    return extracted_text


def run_fixed_experiment():
    print("=" * 60)
    print("FASE P1.3 - P1.5: EKSEKUSI PROGRAM PERBAIKAN (P1_FIXED)")
    print("=" * 60)

    stego_fixed_path = OUTPUTS_DIR / "p1" / "stego_fixed.png"
    pesan_rahasia = DEFAULT_SECRET_MESSAGE

    print(f"Pesan yang akan disisipkan ({len(pesan_rahasia)} karakter):")
    print(f"'{pesan_rahasia}'\n")

    # 1. Jalankan embedding fixed
    EmbeddingPesanFixed(WORKING_COVER_PATH, pesan_rahasia, stego_fixed_path)

    # 2. Jalankan ekstraksi fixed
    extracted = EkstraksiPesanFixed(stego_fixed_path)
    print(f"\nHasil ekstraksi:\n'{extracted}'")

    # 3. Hitung metrik perubahan piksel
    cover_arr = np.array(Image.open(WORKING_COVER_PATH), dtype=np.uint8)
    stego_arr = np.array(Image.open(stego_fixed_path), dtype=np.uint8)

    diff_stats = calc_diff_stats(cover_arr, stego_arr)
    mse = calc_mse(cover_arr, stego_arr)
    psnr = calc_psnr(cover_arr, stego_arr)

    # 4. Uji Kasus Khusus: Pesan yang Memuat Delimiter "stego"
    print("\n" + "=" * 60)
    print("UJI VALIDASI DELIMITER: PESAN MENGANDUNG KATA 'stego'")
    print("=" * 60)
    pesan_dengan_stego = (
        "237006173 - Diva Prayoga Alpariji Putra - Eksperimen stego ini membuktikan "
        "bahwa steganografi modern dengan header 32-bit tidak mengalami pemotongan dini."
    )
    stego_special_path = OUTPUTS_DIR / "p1" / "stego_with_word_stego.png"
    EmbeddingPesanFixed(WORKING_COVER_PATH, pesan_dengan_stego, stego_special_path)
    extracted_special = EkstraksiPesanFixed(stego_special_path)
    special_match = (extracted_special == pesan_dengan_stego)
    print(f"Pesan mengandung 'stego' berhasil diekstrak utuh: {special_match}")

    # 5. Analisis Perbandingan Kapasitas & Utilisasi (P1.3)
    total_pixels = cover_arr.shape[0] * cover_arr.shape[1]
    kapasitas_baseline_bit = total_pixels * 2  # range(0, 2)
    kapasitas_fixed_bit = total_pixels * 3     # range(0, 3)
    utilisasi_baseline = (kapasitas_baseline_bit / kapasitas_fixed_bit) * 100.0
    utilisasi_fixed = 100.0

    print("\n" + "=" * 60)
    print("ANALISIS METRIK & PERBANDINGAN BASELINE VS FIXED")
    print("=" * 60)
    print(f"Max Absolute Difference (|delta|_max) : {diff_stats['max_diff']} (Wajib <= 1)")
    print(f"Jumlah Byte yang Berubah               : {diff_stats['changed_bytes']:,} dari {diff_stats['total_bytes']:,} byte")
    print(f"Rasio Perubahan Byte                  : {diff_stats['change_ratio'] * 100:.4f}%")
    print(f"MSE                                   : {mse:.6f}")
    print(f"PSNR                                  : {psnr:.2f} dB")
    print(f"Kapasitas Baseline (2 kanal R+G)      : {kapasitas_baseline_bit:,} bit ({kapasitas_baseline_bit / 8 / 1024:.2f} KB, utilisasi {utilisasi_baseline:.2f}%)")
    print(f"Kapasitas Fixed (3 kanal R+G+B)       : {kapasitas_fixed_bit:,} bit ({kapasitas_fixed_bit / 8 / 1024:.2f} KB, utilisasi {utilisasi_fixed:.2f}%)")

    # 6. Simpan hasil ke file JSON
    metrics_fixed = {
        "experiment": "P1_Fixed",
        "secret_message": pesan_rahasia,
        "extracted_message": extracted,
        "is_exact_match": (extracted == pesan_rahasia),
        "header_type": "32-bit unsigned integer",
        "header_bits": 32,
        "payload_bytes": len(pesan_rahasia.encode('utf-8')),
        "payload_bits": len(pesan_rahasia.encode('utf-8')) * 8,
        "total_bits_embedded": 32 + len(pesan_rahasia.encode('utf-8')) * 8,
        "max_diff": diff_stats["max_diff"],
        "changed_bytes": diff_stats["changed_bytes"],
        "total_bytes": diff_stats["total_bytes"],
        "change_ratio": diff_stats["change_ratio"],
        "mse": mse,
        "psnr": psnr,
        "capacity_analysis": {
            "baseline_channels": "R, G (2 channels)",
            "baseline_capacity_bits": kapasitas_baseline_bit,
            "baseline_capacity_kb": kapasitas_baseline_bit / 8 / 1024,
            "baseline_utilization_percent": utilisasi_baseline,
            "fixed_channels": "R, G, B (3 channels)",
            "fixed_capacity_bits": kapasitas_fixed_bit,
            "fixed_capacity_kb": kapasitas_fixed_bit / 8 / 1024,
            "fixed_utilization_percent": utilisasi_fixed,
        },
        "delimiter_test": {
            "message_with_stego_word": pesan_dengan_stego,
            "extracted_successfully": special_match,
        }
    }

    metrics_file = RESULTS_DIR / "p1_fixed_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics_fixed, f, indent=4)
    print(f"\n[HASIL TERSIMPAN] Metrik P1 Fixed disimpan di: {metrics_file}")

    return metrics_fixed


if __name__ == "__main__":
    run_fixed_experiment()
