"""
src/p1_baseline.py
Implementasi Baseline Praktikum Steganografi sesuai Kode Slide 74–77.

Program ini mengimplementasikan algoritma asli dari slide dosen tanpa modifikasi,
sehingga perilaku awal, bug, dan anomali perubahan bit dapat diukur dan
didokumentasikan secara empiris (Evidence First).
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


def EmbeddingPesanBaseline(cover_path, pesan, stego_path):
    """
    Algoritma penyisipan pesan asli dari Slide 74–75.
    """
    citra = Image.open(cover_path, "r")
    lebar, tinggi = citra.size
    larik_pixel = np.array(list(citra.getdata()))
    if citra.mode == "RGB":
        n = 3
    else:
        n = 1

    total_pixel = larik_pixel.size // n  # jumlah pixel di dalam citra
    pesan = pesan + "stego"  # tambahkan delimiter untuk menandai akhir pesan

    # ubah pesan ke dalam biner
    pesan_biner = "".join([format(ord(i), "08b") for i in pesan])
    jumlah_pixel_embed = len(pesan_biner)

    print(f"[BASELINE EMBED] Total piksel: {total_pixel:,}")
    print(f"[BASELINE EMBED] Panjang pesan biner (termasuk delimiter 'stego'): {jumlah_pixel_embed} bit")

    if jumlah_pixel_embed > total_pixel:
        print("ERROR: Ukuran citra tidak mencukupi untuk penyembunyian pesan")
        return False

    # Sisipkan bit-bit pesan pada LSB setiap byte pixel (Kode asli slide 75)
    index = 0
    for p in range(total_pixel):
        for q in range(0, 2):  # CATATAN: Kode asli hanya menggunakan kanal 0 dan 1
            if index < jumlah_pixel_embed:
                # CATATAN: Kode asli menggunakan manipulasi string bin()[2:9]
                larik_pixel[p][q] = int(bin(larik_pixel[p][q])[2:9] + pesan_biner[index], 2)
                index = index + 1
            else:
                break
        if index >= jumlah_pixel_embed:
            break

    larik_pixel = larik_pixel.reshape(tinggi, lebar, n)
    stego_image = Image.fromarray(larik_pixel.astype("uint8"))
    stego_image.save(stego_path, format="PNG")
    print(f"[BASELINE EMBED] Penyisipan selesai. Stego image disimpan di: {stego_path}")
    return True


def EkstraksiPesanBaseline(stego_path):
    """
    Algoritma ekstraksi pesan asli dari Slide 76–77.
    """
    citra = Image.open(stego_path, "r")
    larik_pixel = np.array(list(citra.getdata()))
    if citra.mode == "RGB":
        n = 3
    else:
        n = 1

    total_pixel = larik_pixel.size // n

    # Ekstraksi bit-bit pesan dari bit LSB setiap byte pixel (Kode asli slide 76)
    bit_pesan = ""
    for p in range(total_pixel):
        for q in range(0, 2):
            bit_pesan += bin(larik_pixel[p][q])[2:][-1]  # ambil bit LSB

    # Kelompokkan setiap 8-bit dari bit_pesan, simpan sebagai list
    bit_pesan = [bit_pesan[i : i + 8] for i in range(0, len(bit_pesan), 8)]

    # Ubah 8-bit pesan ke dalam setiap karakter (Kode asli slide 77)
    pesan = ""
    for i in range(len(bit_pesan)):
        if pesan[-5:] == "stego":  # ketemu delimiter
            break
        else:
            pesan = pesan + chr(int(bit_pesan[i], 2))

    if "stego" in pesan:
        extracted = pesan[:-5]
        print(f"[BASELINE EXTRACT] Berhasil mengekstrak pesan: '{extracted}'")
        return extracted
    else:
        print("[BASELINE EXTRACT] Delimiter 'stego' tidak ditemukan!")
        return pesan


def demonstrate_bin_slicing_bug(cover_arr):
    """
    Menganalisis dan mendemonstrasikan secara empiris kelemahan baris:
    int(bin(val)[2:9] + bit, 2)
    apabila bertemu byte piksel dengan nilai < 128.
    """
    flat = cover_arr.reshape(-1, 3)
    dark_examples = []
    test_cases = [127, 64, 32, 5, 1, 0]

    for val in test_cases:
        bin_orig = bin(val)
        sliced = bin_orig[2:9]
        for bit in ['0', '1']:
            val_new = int(sliced + bit, 2)
            diff = abs(val_new - val)
            dark_examples.append({
                "original_val": val,
                "bin_original": bin_orig,
                "sliced_2_9": sliced,
                "bit_injected": bit,
                "new_val": val_new,
                "bin_new": bin(val_new),
                "abs_diff": diff,
            })

    # Cari contoh piksel nyata di cover_working.png yang memiliki nilai < 128
    found_real_pixel = None
    for idx in range(len(flat)):
        for ch in range(2):
            val = int(flat[idx, ch])
            if val < 128:
                bin_orig = bin(val)
                sliced = bin_orig[2:9]
                val_new_0 = int(sliced + '0', 2)
                val_new_1 = int(sliced + '1', 2)
                found_real_pixel = {
                    "pixel_index": idx,
                    "channel": ch,
                    "channel_name": "R" if ch == 0 else "G",
                    "original_val": val,
                    "diff_with_bit_0": abs(val_new_0 - val),
                    "diff_with_bit_1": abs(val_new_1 - val),
                    "max_diff_possible": max(abs(val_new_0 - val), abs(val_new_1 - val)),
                }
                break
        if found_real_pixel:
            break

    return dark_examples, found_real_pixel


def run_baseline_experiment():
    print("=" * 60)
    print("FASE P0: VALIDASI INPUT CITRA COVER")
    print("=" * 60)
    info_cover = validate_and_prepare_cover()
    for k, v in info_cover.items():
        print(f"  {k:15}: {v}")

    print("\n" + "=" * 60)
    print("FASE P1.1: MENJALANKAN BASELINE EMBEDDING & EXTRACTION")
    print("=" * 60)

    stego_baseline_path = OUTPUTS_DIR / "p1" / "stego_baseline.png"
    pesan_rahasia = DEFAULT_SECRET_MESSAGE

    print(f"Pesan yang akan disisipkan ({len(pesan_rahasia)} karakter):")
    print(f"'{pesan_rahasia}'\n")

    # Jalankan embedding
    success = EmbeddingPesanBaseline(WORKING_COVER_PATH, pesan_rahasia, stego_baseline_path)
    if not success:
        raise RuntimeError("Embedding baseline gagal!")

    # Jalankan ekstraksi
    extracted = EkstraksiPesanBaseline(stego_baseline_path)

    # Analisis Perubahan Byte (P1.2)
    cover_arr = np.array(Image.open(WORKING_COVER_PATH), dtype=np.uint8)
    stego_arr = np.array(Image.open(stego_baseline_path), dtype=np.uint8)

    diff_stats = calc_diff_stats(cover_arr, stego_arr)
    mse = calc_mse(cover_arr, stego_arr)
    psnr = calc_psnr(cover_arr, stego_arr)

    dark_tests, real_pixel_bug = demonstrate_bin_slicing_bug(cover_arr)

    print("\n" + "=" * 60)
    print("FASE P1.2: ANALISIS METRIK PERUBAHAN PIKSEL BASELINE")
    print("=" * 60)
    print(f"Max Absolute Difference (|delta|_max) pada pesan uji : {diff_stats['max_diff']}")
    print(f"Jumlah Byte yang Berubah                             : {diff_stats['changed_bytes']:,} dari {diff_stats['total_bytes']:,} byte")
    print(f"Rasio Perubahan Byte                                : {diff_stats['change_ratio'] * 100:.4f}%")
    print(f"MSE                                                 : {mse:.6f}")
    print(f"PSNR                                                : {psnr:.2f} dB")
    print(f"Pesan Sesuai Asli?                                  : {extracted == pesan_rahasia}")

    print("\n[ANALISIS KRITIS BUG bin()[2:9]]:")
    print("Pada pesan uji di atas (1.320 bit), seluruh piksel awal (0 s.d. 659) bernilai >= 128 (141-195),")
    print("sehingga representasi bin() selalu 8-bit ('0bxxxxxxx') dan slicing [2:9] kebetulan menghasilkan 7-bit.")
    print("Namun jika bertemu piksel < 128, slicing string bin() menghasilkan penyimpangan nilai yang sangat masif:")
    for ex in dark_tests[:4]:
        print(f"  - Nilai Asli {ex['original_val']:3d} ({ex['bin_original']:>10s}) + bit '{ex['bit_injected']}' -> "
              f"Nilai Baru {ex['new_val']:3d} ({ex['bin_new']:>10s}) | Selisih = {ex['abs_diff']}")

    if real_pixel_bug:
        print(f"\nContoh piksel riil pada Diva_selfie:")
        print(f"  Piksel indeks {real_pixel_bug['pixel_index']:,}, Kanal {real_pixel_bug['channel_name']}: "
              f"nilai asli = {real_pixel_bug['original_val']}, jika disisipi pesan baseline selisihnya bisa mencapai {real_pixel_bug['max_diff_possible']}!")

    # Simpan hasil metrik ke file JSON
    metrics_baseline = {
        "experiment": "P1_Baseline",
        "cover_info": info_cover,
        "secret_message": pesan_rahasia,
        "extracted_message": extracted,
        "is_exact_match": (extracted == pesan_rahasia),
        "total_message_bits_with_delimiter": (len(pesan_rahasia) + 5) * 8,
        "max_diff_test_message": diff_stats["max_diff"],
        "changed_bytes": diff_stats["changed_bytes"],
        "total_bytes": diff_stats["total_bytes"],
        "change_ratio": diff_stats["change_ratio"],
        "mse": mse,
        "psnr": psnr,
        "bug_analysis": {
            "root_cause": "Slicing bin()[2:9] tidak mempertimbangkan padding 8-bit untuk nilai < 128",
            "synthetic_tests": dark_tests,
            "real_pixel_proof": real_pixel_bug,
        }
    }

    metrics_file = RESULTS_DIR / "p1_baseline_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics_baseline, f, indent=4)
    print(f"\n[HASIL TERSIMPAN] Metrik baseline disimpan di: {metrics_file}")

    return metrics_baseline


if __name__ == "__main__":
    run_baseline_experiment()
