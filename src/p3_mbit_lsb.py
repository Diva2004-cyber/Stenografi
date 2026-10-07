"""
src/p3_mbit_lsb.py
Fase P3: Eksperimen m-bit LSB dan Kualitas Citra (m = 1, 2, 3, 4).

Fitur:
1. P3.1: Implementasi penyisipan m-bit LSB (m in [1, 2, 3, 4]) menggunakan masking bitwise:
         mask = 0xFF ^ ((1 << m) - 1)
         stego = (cover & mask) | payload_m_bits
         Menjamin perubahan per-byte maksimum tidak melebihi (2^m - 1).
2. P3.2: Penyisipan pesan acak berkapasitas 100% untuk setiap m (reproducible seed = 2026).
3. P3.3: Perhitungan MSE dan PSNR untuk setiap m, ekspor tabel ke results/p3_results.csv.
4. P3.4: Pembuatan grafik PSNR vs m (figures/p3_psnr_vs_m.png) dan grid 4 stego-image (figures/p3_stego_grid.png).
"""

import sys
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

from common import (
    WORKING_COVER_PATH,
    OUTPUTS_DIR,
    RESULTS_DIR,
    FIGURES_DIR,
    calc_mse,
    calc_psnr,
)

PAYLOAD_SEED_P3 = 2026


def embed_mbit_lsb_100pct(cover_arr, m, seed=PAYLOAD_SEED_P3):
    """
    Menyisipkan pesan acak sebesar 100% kapasitas citra menggunakan m-bit LSB.
    Setiap byte citra diganti m bit LSB-nya dengan bit acak.
    """
    if m not in [1, 2, 3, 4]:
        raise ValueError(f"Nilai m harus 1, 2, 3, atau 4 (diterima: {m})")

    # Masking bitwise: menghapus m bit terbawah
    # m=1 -> 0xFE (11111110)
    # m=2 -> 0xFC (11111100)
    # m=3 -> 0xF8 (11111000)
    # m=4 -> 0xF0 (11110000)
    mask = np.uint8(0xFF ^ ((1 << m) - 1))

    # Bangkitkan payload acak berukuran sama persis dengan citra (100% kapasitas)
    rng = np.random.default_rng(seed)
    payload_vals = rng.integers(0, 1 << m, size=cover_arr.shape, dtype=np.uint8)

    # Operasi bitwise LSB replacement
    stego_arr = (cover_arr & mask) | payload_vals

    # Validasi teoritis: selisih maksimum tidak boleh melebihi (2^m - 1)
    diff = np.abs(cover_arr.astype(int) - stego_arr.astype(int))
    max_diff = int(diff.max())
    expected_max_diff = (1 << m) - 1
    assert max_diff <= expected_max_diff, (
        f"Pelanggaran batas! max_diff={max_diff} > {expected_max_diff}"
    )

    return stego_arr, max_diff, expected_max_diff


def run_p3_experiment():
    print("=" * 65)
    print("FASE P3: EKSPERIMEN m-bit LSB DAN KUALITAS CITRA (m = 1, 2, 3, 4)")
    print("=" * 65)

    cover_img = Image.open(WORKING_COVER_PATH)
    cover_arr = np.array(cover_img, dtype=np.uint8)
    h, w, c = cover_arr.shape
    total_bytes = cover_arr.size

    print(f"Dimensi citra cover: {w} x {h} x {c} ({total_bytes:,} byte)")
    print(f"Seed payload acak  : {PAYLOAD_SEED_P3}\n")

    results_data = []
    stego_images = {}

    for m in [1, 2, 3, 4]:
        # 1. Hitung kapasitas
        capacity_bits = total_bytes * m
        capacity_bytes = capacity_bits // 8
        capacity_kb = capacity_bytes / 1024.0

        # 2. Embedding 100% kapasitas
        stego_arr, max_diff, expected_max_diff = embed_mbit_lsb_100pct(
            cover_arr, m, seed=PAYLOAD_SEED_P3
        )

        # 3. Simpan stego image
        stego_path = OUTPUTS_DIR / "p3" / f"stego_m{m}.png"
        Image.fromarray(stego_arr).save(stego_path, format="PNG")
        stego_images[m] = stego_arr

        # 4. Hitung MSE dan PSNR
        mse = calc_mse(cover_arr, stego_arr)
        psnr = calc_psnr(cover_arr, stego_arr)

        diff = np.abs(cover_arr.astype(int) - stego_arr.astype(int))
        changed_bytes = int(np.count_nonzero(diff))
        change_ratio = (changed_bytes / total_bytes) * 100.0

        print(f"--- Evaluasi m = {m} ---")
        print(f"  Kapasitas       : {capacity_bits:,} bit | {capacity_bytes:,} byte | {capacity_kb:.2f} KB")
        print(f"  Max Diff Aktual : {max_diff} (Batas Teori: <= {expected_max_diff})")
        print(f"  Byte Berubah    : {changed_bytes:,} / {total_bytes:,} ({change_ratio:.2f}%)")
        print(f"  MSE             : {mse:.4f}")
        print(f"  PSNR            : {psnr:.2f} dB")
        print(f"  Status Ambang 40dB: {'Di atas 40 dB (Kualitas Sangat Tinggi)' if psnr >= 40.0 else 'Di bawah 40 dB (Mulai Terlihat Degradasi)'}\n")

        results_data.append({
            "m": m,
            "Capacity_Bits": capacity_bits,
            "Capacity_Bytes": capacity_bytes,
            "Capacity_KB": round(capacity_kb, 2),
            "Max_Diff_Actual": max_diff,
            "Max_Diff_Theory": expected_max_diff,
            "Changed_Bytes": changed_bytes,
            "Change_Ratio_Pct": round(change_ratio, 2),
            "MSE": round(mse, 4),
            "PSNR_dB": round(psnr, 2),
        })

    # Simpan ke CSV
    df = pd.DataFrame(results_data)
    csv_path = RESULTS_DIR / "p3_results.csv"
    df.to_csv(csv_path, index=False)
    print(f"[HASIL CSV] Tabel hasil P3 disimpan di: {csv_path}")

    # Simpan ke JSON
    json_path = RESULTS_DIR / "p3_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=4)

    # 5. P3.4: Buat Grafik PSNR vs m
    plt.figure(figsize=(8, 5))
    plt.plot(df["m"], df["PSNR_dB"], marker="o", color="#1f77b4", linewidth=2.5, markersize=8, label="PSNR Aktual")
    plt.axhline(y=40.0, color="#d62728", linestyle="--", linewidth=1.5, label="Ambang Batas 40 dB (Imperceptible)")

    for _, row in df.iterrows():
        plt.annotate(
            f"{row['PSNR_dB']:.2f} dB\n({row['Capacity_KB']:.0f} KB)",
            (row["m"], row["PSNR_dB"]),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=9,
            fontweight="bold"
        )

    plt.title("Grafik Kualitas Citra: PSNR vs Nilai m (m-bit LSB)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Jumlah Bit LSB per Byte (m)", fontsize=11)
    plt.ylabel("PSNR (dB)", fontsize=11)
    plt.xticks([1, 2, 3, 4])
    plt.ylim(25, 60)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", frameon=True)
    plt.tight_layout()

    fig_psnr_path = FIGURES_DIR / "p3_psnr_vs_m.png"
    plt.savefig(fig_psnr_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[GRAFIK] Grafik PSNR vs m disimpan di: {fig_psnr_path}")

    # 6. P3.4: Buat Grid 4 Stego-Image Berdampingan
    fig, axes = plt.subplots(1, 4, figsize=(20, 8))
    for idx, m in enumerate([1, 2, 3, 4]):
        row_m = df[df["m"] == m].iloc[0]
        axes[idx].imshow(stego_images[m])
        axes[idx].set_title(
            f"m = {m}\n"
            f"Kapasitas: {row_m['Capacity_KB']:.1f} KB\n"
            f"MSE: {row_m['MSE']:.2f} | PSNR: {row_m['PSNR_dB']:.2f} dB",
            fontsize=11
        )
        axes[idx].axis("off")

    plt.tight_layout()
    fig_grid_path = FIGURES_DIR / "p3_stego_grid.png"
    plt.savefig(fig_grid_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[GRID CITRA] Grid stego images disimpan di: {fig_grid_path}")

    return results_data


if __name__ == "__main__":
    run_p3_experiment()
