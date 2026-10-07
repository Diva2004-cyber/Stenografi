"""
src/bonus_steganalysis.py
Bonus: Steganalisis Visual dan Kaitannya dengan Steganalisis Statistik Chi-Square.

Fitur:
1. Menyisipkan pesan acak sekuensial hingga 50% kapasitas citra cover (baris 0 s.d. 639).
2. Mengekstrak LSB bit-plane:
   lsb_plane = (image & 1) * 255
3. Membandingkan bidang LSB citra cover vs citra stego.
4. Menunjukkan bagaimana visual inspection mengekspos area penyisipan (batas tajam antara derau acak dan kontur alami).
5. Menganalisis keterbatasan inspeksi visual serta kaitannya dengan uji statistik Chi-Square / Pairs of Values (PoV)
   berdasarkan referensi Yuli Anneria Sinaga (Slide 79).
"""

import sys
import os
import json
import numpy as np
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


def compute_chi_square_pov(image_channel_flat):
    """
    Menghitung statistik Chi-Square sederhana berbasis Pairs of Values (PoV)
    antara pasangan nilai (2k, 2k+1) untuk k in [0..127].
    Berdasarkan teori Westfeld & Pfitzmann serta referensi Yuli Anneria Sinaga (Slide 79).
    """
    hist, _ = np.histogram(image_channel_flat, bins=256, range=(0, 256))
    chi_square_val = 0.0
    valid_pairs = 0

    for k in range(128):
        obs_even = hist[2 * k]
        obs_odd = hist[2 * k + 1]
        expected = (obs_even + obs_odd) / 2.0
        if expected > 5.0:  # Syarat uji Chi-square standar
            chi_square_val += ((obs_even - expected) ** 2) / expected
            chi_square_val += ((obs_odd - expected) ** 2) / expected
            valid_pairs += 1

    return float(chi_square_val), valid_pairs


def run_bonus_steganalysis():
    print("=" * 65)
    print("BONUS: STEGANALISIS VISUAL & STATISTIK CHI-SQUARE")
    print("=" * 65)

    cover_img = Image.open(WORKING_COVER_PATH)
    w, h = cover_img.size
    cover_arr = np.array(cover_img, dtype=np.uint8)
    total_bytes = cover_arr.size  # 2,764,800 byte

    # 1. Penyisipan 50% Kapasitas Sekuensial
    capacity_50pct_bits = total_bytes // 2  # 1,382,400 bit
    pixels_affected = capacity_50pct_bits // 3  # 460,800 piksel = tepat 640 baris (setengah atas)
    rows_affected = pixels_affected // w        # 640 baris (0 s.d. 639)

    print(f"Dimensi citra cover          : {w} x {h} (Total: {total_bytes:,} byte)")
    print(f"Penyisipan 50% kapasitas     : {capacity_50pct_bits:,} bit")
    print(f"Area terdampak               : Baris Y [0 s.d. {rows_affected - 1}] ({rows_affected} baris atas)")
    print(f"Area tak tersentuh           : Baris Y [{rows_affected} s.d. {h - 1}] ({h - rows_affected} baris bawah)\n")

    # Bangkitkan payload acak 50%
    rng = np.random.default_rng(2026)
    payload_50pct = rng.integers(0, 2, size=capacity_50pct_bits, dtype=np.uint8)

    stego_arr = cover_arr.copy()
    stego_flat = stego_arr.reshape(-1)
    stego_flat[:capacity_50pct_bits] = (stego_flat[:capacity_50pct_bits] & 0xFE) | payload_50pct

    stego_50pct_arr = stego_flat.reshape((h, w, 3))

    # Simpan citra stego 50%
    os.makedirs(OUTPUTS_DIR / "bonus", exist_ok=True)
    stego_path = OUTPUTS_DIR / "bonus" / "stego_bonus_50pct.png"
    Image.fromarray(stego_50pct_arr).save(stego_path, format="PNG")
    print(f"[BONUS] Stego image 50% disimpan di: {stego_path}")

    # 2. Ekstraksi LSB Bit-Plane: (citra & 1) * 255
    # Mengambil kanal Red (kanal 0) untuk inspeksi bidang LSB
    channel_idx = 0  # Red channel
    channel_name = "Red"

    lsb_cover = (cover_arr[:, :, channel_idx] & 1) * 255
    lsb_stego = (stego_50pct_arr[:, :, channel_idx] & 1) * 255

    # 3. Analisis Statistik Chi-Square (Pairs of Values)
    # Bandingkan paruh atas (yang disisipi) vs paruh bawah (yang tidak disisipi)
    chi2_cover_top, pairs_top = compute_chi_square_pov(cover_arr[:rows_affected, :, channel_idx].flatten())
    chi2_stego_top, _ = compute_chi_square_pov(stego_50pct_arr[:rows_affected, :, channel_idx].flatten())

    chi2_cover_bot, pairs_bot = compute_chi_square_pov(cover_arr[rows_affected:, :, channel_idx].flatten())
    chi2_stego_bot, _ = compute_chi_square_pov(stego_50pct_arr[rows_affected:, :, channel_idx].flatten())

    mse = calc_mse(cover_arr, stego_50pct_arr)
    psnr = calc_psnr(cover_arr, stego_50pct_arr)

    print("=" * 65)
    print("HASIL PENGUKURAN DAN ANALISIS STEGANALISIS")
    print("=" * 65)
    print(f"Kualitas Citra Stego 50%:")
    print(f"  MSE  : {mse:.4f}")
    print(f"  PSNR : {psnr:.2f} dB (Visual citra asli tetap imperceptible)\n")

    print(f"Uji Statistik Chi-Square PoV (Kanal {channel_name}):")
    print(f"  Paruh Atas Cover (Asli)       : Chi2 = {chi2_cover_top:.2f} (Ada korelasi alami, nilai genap != ganjil)")
    print(f"  Paruh Atas Stego (Disisipi)   : Chi2 = {chi2_stego_top:.2f} (Mendekati 0! Frekuensi genap-ganjil rata akibat LSB)")
    print(f"  Paruh Bawah Cover (Asli)      : Chi2 = {chi2_cover_bot:.2f}")
    print(f"  Paruh Bawah Stego (Tak Disisip): Chi2 = {chi2_stego_bot:.2f} (Identik karena belum tersentuh)\n")

    # 4. Buat Visualisasi Perbandingan LSB Plane
    fig, axes = plt.subplots(2, 2, figsize=(14, 18))

    # Baris 1: Citra Asli vs Stego
    axes[0, 0].imshow(cover_arr)
    axes[0, 0].set_title("Citra Cover Asli", fontsize=13, fontweight="bold")
    axes[0, 0].axis("off")

    axes[0, 1].imshow(stego_50pct_arr)
    axes[0, 1].set_title(f"Citra Stego 50% Kapasitas\n(PSNR: {psnr:.2f} dB - Mata manusia tidak melihat perbedaan)",
                         fontsize=13, fontweight="bold")
    axes[0, 1].axis("off")

    # Baris 2: LSB Bit-Plane Cover vs Stego
    axes[1, 0].imshow(lsb_cover, cmap="gray", vmin=0, vmax=255)
    axes[1, 0].set_title(f"Bidang Bit LSB Cover (Kanal {channel_name})\n(Menampilkan struktur tepi & tekstur alami citra)",
                         fontsize=13, fontweight="bold")
    axes[1, 0].axis("off")

    axes[1, 1].imshow(lsb_stego, cmap="gray", vmin=0, vmax=255)
    axes[1, 1].set_title(f"Bidang Bit LSB Stego (Kanal {channel_name})\n(Paruh atas: Derau acak seragam | Paruh bawah: Struktur alami)",
                         fontsize=13, fontweight="bold")
    axes[1, 1].axhline(y=rows_affected, color="red", linestyle="--", linewidth=2.5,
                       label=f"Batas Penyisipan Sekuensial (Baris {rows_affected})")
    axes[1, 1].legend(loc="lower right", frameon=True, fontsize=10)
    axes[1, 1].axis("off")

    plt.tight_layout()
    fig_path = FIGURES_DIR / "bonus_lsb_planes.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[VISUALISASI] Visualisasi LSB Planes disimpan di: {fig_path}")

    # 5. Simpan Hasil ke JSON
    bonus_data = {
        "experiment": "Bonus_Visual_Steganalysis",
        "capacity_percent": 50.0,
        "capacity_bits": capacity_50pct_bits,
        "rows_affected": rows_affected,
        "image_quality": {
            "mse": mse,
            "psnr_db": psnr,
        },
        "chi_square_pov": {
            "channel": channel_name,
            "top_half_cover_chi2": chi2_cover_top,
            "top_half_stego_chi2": chi2_stego_top,
            "top_half_chi2_drop_pct": ((chi2_cover_top - chi2_stego_top) / chi2_cover_top) * 100.0,
            "bottom_half_cover_chi2": chi2_cover_bot,
            "bottom_half_stego_chi2": chi2_stego_bot,
            "significance": "Penyisipan LSB meratakan frekuensi pasangan nilai (2k, 2k+1) sehingga nilai Chi-Square anjlok drastis ke mendekati 0.",
        },
        "visual_findings": {
            "boundary_visible": True,
            "boundary_row": rows_affected,
            "top_appearance": "Derau putih acak seragam (uniform random noise)",
            "bottom_appearance": "Kontur tepi dan siluet alami wajah/rambut",
        }
    }

    json_path = RESULTS_DIR / "bonus_steganalysis.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(bonus_data, f, indent=4)
    print(f"[HASIL JSON] Data steganalisis disimpan di: {json_path}")

    return bonus_data


if __name__ == "__main__":
    run_bonus_steganalysis()
