"""
src/p2_random_lsb.py
Fase P2: LSB Acak dengan Stego-key (NIM Mahasiswa).

Fitur:
1. P2.1: Penyisipan 1-bit LSB pada posisi acak menggunakan PRNG numpy.random.default_rng(seed).permutation(...).
         Stego-key benar = 237006173 (NIM Mahasiswa).
2. P2.2: Pengujian ekstraksi kunci benar (237006173) vs kunci salah (237006174 / NIM + 1).
3. P2.3: Pembuatan peta perubahan (Change Map) untuk metode sekuensial vs metode acak.
"""

import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Pastikan output konsol Windows mendukung UTF-8
sys.stdout.reconfigure(encoding="utf-8")

from common import (
    WORKING_COVER_PATH,
    OUTPUTS_DIR,
    RESULTS_DIR,
    FIGURES_DIR,
    DEFAULT_SECRET_MESSAGE,
    SEED_CORRECT,
    SEED_WRONG,
    calc_diff_stats,
    calc_mse,
    calc_psnr,
)


def EmbeddingPesanRandom(cover_path, pesan, stego_path, seed=SEED_CORRECT):
    """
    Penyisipan 1-bit LSB dengan posisi acak berbasis permutasi PRNG:
    - seed berfungsi sebagai stego-key
    - 32-bit length header + payload disisipkan di posisi-posisi permutasi unik
    """
    citra = Image.open(cover_path, "r")
    lebar, tinggi = citra.size
    cover_arr = np.array(citra, dtype=np.uint8)

    # Flatten ke array 1D byte (tinggi * lebar * 3)
    flat_bytes = cover_arr.flatten().copy()
    total_available_bytes = flat_bytes.size

    # Persiapkan payload dan header 32-bit
    if isinstance(pesan, str):
        payload_bytes = pesan.encode("utf-8")
    else:
        payload_bytes = bytes(pesan)

    payload_len_bytes = len(payload_bytes)
    header_biner = format(payload_len_bytes, "032b")
    payload_biner = "".join([format(b, "08b") for b in payload_bytes])
    bit_stream = header_biner + payload_biner
    total_bits_to_embed = len(bit_stream)

    print(f"[RANDOM EMBED] Seed (Stego-key)    : {seed}")
    print(f"[RANDOM EMBED] Total byte citra    : {total_available_bytes:,}")
    print(f"[RANDOM EMBED] Panjang payload     : {payload_len_bytes} byte")
    print(f"[RANDOM EMBED] Total bit (+ header): {total_bits_to_embed} bit")

    if total_bits_to_embed > total_available_bytes:
        raise ValueError(
            f"Jumlah bit ({total_bits_to_embed}) melebihi kapasitas total ({total_available_bytes})!"
        )

    # Bangkitkan permutasi acak unik tanpa pengulangan
    rng = np.random.default_rng(seed)
    permutation = rng.permutation(total_available_bytes)

    # Ambil sejumlah indeks permutasi sebanyak bit yang akan disisipkan
    embed_indices = permutation[:total_bits_to_embed]

    # Sisipkan bit ke LSB byte yang terpilih
    for i, byte_idx in enumerate(embed_indices):
        bit_val = int(bit_stream[i])
        flat_bytes[byte_idx] = (flat_bytes[byte_idx] & 0xFE) | bit_val

    stego_arr = flat_bytes.reshape((tinggi, lebar, 3))
    stego_img = Image.fromarray(stego_arr)
    stego_img.save(stego_path, format="PNG")
    print(f"[RANDOM EMBED] Penyisipan sukses. Disimpan di: {stego_path}")
    return stego_arr


def EkstraksiPesanRandom(stego_path, seed=SEED_CORRECT):
    """
    Ekstraksi pesan 1-bit LSB dari posisi acak menggunakan stego-key (seed):
    - Jika seed benar, permutasi posisi cocok, header dan pesan terekstrak utuh.
    - Jika seed salah, permutasi posisi salah, menghasilkan bit acak / pesan rusak.
    """
    citra = Image.open(stego_path, "r")
    stego_arr = np.array(citra, dtype=np.uint8)
    flat_bytes = stego_arr.flatten()
    total_available_bytes = flat_bytes.size

    # Bangkitkan permutasi dengan seed ekstraksi
    rng = np.random.default_rng(seed)
    permutation = rng.permutation(total_available_bytes)

    # Langkah 1: Ekstraksi 32-bit header dari 32 posisi pertama permutasi
    header_indices = permutation[:32]
    header_bits = "".join([str(flat_bytes[idx] & 1) for idx in header_indices])
    payload_len_bytes = int(header_bits, 2)

    print(f"[RANDOM EXTRACT] Seed: {seed}")
    print(f"[RANDOM EXTRACT] 32-bit Header: {header_bits} (Desimal: {payload_len_bytes:,} byte)")

    # Validasi batas kewajaran header
    max_sensible_bytes = (total_available_bytes - 32) // 8
    if payload_len_bytes > max_sensible_bytes or payload_len_bytes < 0:
        print(f"[RANDOM EXTRACT] PERINGATAN: Header di luar batas kapasitas ({payload_len_bytes:,} > {max_sensible_bytes:,}). "
              f"Ini membuktikan stego-key salah!")
        # Baca sejumlah byte terbatas untuk melihat output teks sampah (corrupted text)
        sample_bytes_to_read = min(160, max_sensible_bytes)
        payload_bits_to_read = sample_bytes_to_read * 8
        payload_indices = permutation[32 : 32 + payload_bits_to_read]
        payload_bits = "".join([str(flat_bytes[idx] & 1) for idx in payload_indices])

        raw_bytes = bytearray()
        for i in range(0, len(payload_bits), 8):
            raw_bytes.append(int(payload_bits[i : i + 8], 2))

        corrupted_text = raw_bytes.decode("utf-8", errors="replace")
        return {
            "success": False,
            "header_decimal": payload_len_bytes,
            "extracted_text": corrupted_text,
            "raw_hex": raw_bytes.hex()[:64],
            "note": "Header di luar batas kapasitas karena seed salah.",
        }

    # Langkah 2: Jika header dalam batas kapasitas, baca payload
    payload_total_bits = payload_len_bytes * 8
    payload_indices = permutation[32 : 32 + payload_total_bits]
    payload_bits = "".join([str(flat_bytes[idx] & 1) for idx in payload_indices])

    payload_bytes = bytearray()
    for i in range(0, len(payload_bits), 8):
        payload_bytes.append(int(payload_bits[i : i + 8], 2))

    try:
        decoded_text = payload_bytes.decode("utf-8")
        is_valid_utf8 = True
    except UnicodeDecodeError:
        decoded_text = payload_bytes.decode("utf-8", errors="replace")
        is_valid_utf8 = False

    return {
        "success": is_valid_utf8,
        "header_decimal": payload_len_bytes,
        "extracted_text": decoded_text,
        "raw_hex": payload_bytes.hex()[:64],
        "note": "Berhasil diekstrak" if is_valid_utf8 else "Terjadi UnicodeDecodeError",
    }


def generate_change_maps(cover_arr, stego_seq_arr, stego_rand_arr):
    """
    P2.3: Membuat Change Map (peta perubahan piksel)
    - Byte berubah: Putih (255)
    - Byte tidak berubah: Hitam (0)
    Piksel dianggap berubah jika salah satu dari 3 kanalnya berubah.
    """
    # Deteksi perubahan per piksel (H, W)
    mask_seq = np.any(cover_arr != stego_seq_arr, axis=2).astype(np.uint8) * 255
    mask_rand = np.any(cover_arr != stego_rand_arr, axis=2).astype(np.uint8) * 255

    # Simpan citra biner mandiri
    path_seq = FIGURES_DIR / "p2_change_map_sequential.png"
    path_rand = FIGURES_DIR / "p2_change_map_random.png"

    Image.fromarray(mask_seq, mode="L").save(path_seq)
    Image.fromarray(mask_rand, mode="L").save(path_rand)

    print(f"[CHANGE MAP] Disimpan: {path_seq}")
    print(f"[CHANGE MAP] Disimpan: {path_rand}")

    # Visualisasi perbandingan berdampingan (side-by-side)
    fig, axes = plt.subplots(1, 2, figsize=(12, 10))
    axes[0].imshow(mask_seq, cmap="gray", vmin=0, vmax=255)
    axes[0].set_title("Sequential Change Map\n(Terkonsentrasi padat di sudut kiri atas)", fontsize=12)
    axes[0].axis("off")

    axes[1].imshow(mask_rand, cmap="gray", vmin=0, vmax=255)
    axes[1].set_title(f"Random Change Map (Seed: {SEED_CORRECT})\n(Tersebar merata/difus di seluruh citra)", fontsize=12)
    axes[1].axis("off")

    plt.tight_layout()
    path_comparison = FIGURES_DIR / "p2_change_map_comparison.png"
    plt.savefig(path_comparison, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[CHANGE MAP] Gambar perbandingan disimpan di: {path_comparison}")

    # Hitung metrik spasial sebaran
    changed_pixels_seq = int(np.count_nonzero(mask_seq))
    changed_pixels_rand = int(np.count_nonzero(mask_rand))

    y_seq, x_seq = np.where(mask_seq > 0)
    y_rand, x_rand = np.where(mask_rand > 0)

    bbox_seq = {
        "y_min": int(y_seq.min()), "y_max": int(y_seq.max()),
        "x_min": int(x_seq.min()), "x_max": int(x_seq.max()),
        "height_span": int(y_seq.max() - y_seq.min() + 1),
        "width_span": int(x_seq.max() - x_seq.min() + 1),
    } if len(y_seq) > 0 else {}

    bbox_rand = {
        "y_min": int(y_rand.min()), "y_max": int(y_rand.max()),
        "x_min": int(x_rand.min()), "x_max": int(x_rand.max()),
        "height_span": int(y_rand.max() - y_rand.min() + 1),
        "width_span": int(x_rand.max() - x_rand.min() + 1),
    } if len(y_rand) > 0 else {}

    return {
        "changed_pixels_seq": changed_pixels_seq,
        "changed_pixels_rand": changed_pixels_rand,
        "bbox_seq": bbox_seq,
        "bbox_rand": bbox_rand,
    }


def run_p2_experiment():
    print("=" * 60)
    print("FASE P2: LSB ACAK DENGAN STEGO-KEY (PRNG SEED)")
    print("=" * 60)

    cover_arr = np.array(Image.open(WORKING_COVER_PATH), dtype=np.uint8)
    pesan_rahasia = DEFAULT_SECRET_MESSAGE
    stego_rand_path = OUTPUTS_DIR / "p2" / "stego_random_correct.png"

    # 1. Embedding dengan Stego-key Benar (NIM = 237006173)
    stego_rand_arr = EmbeddingPesanRandom(
        WORKING_COVER_PATH, pesan_rahasia, stego_rand_path, seed=SEED_CORRECT
    )

    # 2. Skenario 1: Ekstraksi dengan Stego-key BENAR
    print("\n" + "-" * 50)
    print("SKENARIO 1: Ekstraksi dengan Kunci BENAR (seed = 237006173)")
    print("-" * 50)
    result_correct = EkstraksiPesanRandom(stego_rand_path, seed=SEED_CORRECT)
    print(f"Hasil Ekstraksi Kunci Benar:\n'{result_correct['extracted_text']}'")
    match_correct = (result_correct["extracted_text"] == pesan_rahasia)
    print(f"Pesan Cocok Persis: {match_correct}")

    # 3. Skenario 2: Ekstraksi dengan Stego-key SALAH (NIM + 1 = 237006174)
    print("\n" + "-" * 50)
    print("SKENARIO 2: Ekstraksi dengan Kunci SALAH (seed = 237006174)")
    print("-" * 50)
    result_wrong = EkstraksiPesanRandom(stego_rand_path, seed=SEED_WRONG)
    print(f"Hasil Ekstraksi Kunci Salah (Teks Corrupt / Sampah):")
    print(f"  Repr: {repr(result_wrong['extracted_text'])}")
    print(f"  Hex Sampah: {result_wrong['raw_hex']}")
    match_wrong = (result_wrong["extracted_text"] == pesan_rahasia)
    print(f"Pesan Cocok Persis: {match_wrong} (Ekspektasi: False)")

    # 4. Hitung Metrik Citra Stego Acak
    diff_stats = calc_diff_stats(cover_arr, stego_rand_arr)
    mse = calc_mse(cover_arr, stego_rand_arr)
    psnr = calc_psnr(cover_arr, stego_rand_arr)

    # 5. P2.3: Generate Change Maps (Sequential vs Random)
    stego_seq_path = OUTPUTS_DIR / "p1" / "stego_fixed.png"
    stego_seq_arr = np.array(Image.open(stego_seq_path), dtype=np.uint8)

    change_map_stats = generate_change_maps(cover_arr, stego_seq_arr, stego_rand_arr)

    print("\n" + "=" * 60)
    print("ANALISIS CHANGE MAP: SEKUENSIAL VS ACAK")
    print("=" * 60)
    print(f"Metode Sekuensial:")
    print(f"  Piksel berubah : {change_map_stats['changed_pixels_seq']} piksel")
    print(f"  Rentang BBox   : Y [{change_map_stats['bbox_seq']['y_min']}..{change_map_stats['bbox_seq']['y_max']}] "
          f"(Tinggi: {change_map_stats['bbox_seq']['height_span']} baris), "
          f"X [{change_map_stats['bbox_seq']['x_min']}..{change_map_stats['bbox_seq']['x_max']}]")
    print(f"Metode Acak:")
    print(f"  Piksel berubah : {change_map_stats['changed_pixels_rand']} piksel")
    print(f"  Rentang BBox   : Y [{change_map_stats['bbox_rand']['y_min']}..{change_map_stats['bbox_rand']['y_max']}] "
          f"(Tinggi: {change_map_stats['bbox_rand']['height_span']} baris), "
          f"X [{change_map_stats['bbox_rand']['x_min']}..{change_map_stats['bbox_rand']['x_max']}]")

    # 6. Simpan seluruh data ke JSON
    metrics_p2 = {
        "experiment": "P2_Random_LSB",
        "seed_correct": SEED_CORRECT,
        "seed_wrong": SEED_WRONG,
        "secret_message": pesan_rahasia,
        "scenario_correct_key": {
            "seed": SEED_CORRECT,
            "is_exact_match": match_correct,
            "extracted_text": result_correct["extracted_text"],
        },
        "scenario_wrong_key": {
            "seed": SEED_WRONG,
            "is_exact_match": match_wrong,
            "header_decimal": result_wrong["header_decimal"],
            "corrupted_sample_text": repr(result_wrong["extracted_text"]),
            "corrupted_raw_hex": result_wrong["raw_hex"],
            "note": result_wrong["note"],
        },
        "image_metrics": {
            "max_diff": diff_stats["max_diff"],
            "changed_bytes": diff_stats["changed_bytes"],
            "total_bytes": diff_stats["total_bytes"],
            "change_ratio": diff_stats["change_ratio"],
            "mse": mse,
            "psnr": psnr,
        },
        "change_map_analysis": change_map_stats,
    }

    metrics_file = RESULTS_DIR / "p2_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics_p2, f, indent=4)
    print(f"\n[HASIL TERSIMPAN] Metrik P2 disimpan di: {metrics_file}")

    return metrics_p2


if __name__ == "__main__":
    run_p2_experiment()
