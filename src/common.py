"""
src/common.py
Konfigurasi bersama, konstanta identitas mahasiswa, dan fungsi utilitas
untuk praktikum steganografi LSB.
"""

import os
import json
from pathlib import Path
import numpy as np
from PIL import Image

# Identitas Mahasiswa & Parameter Wajib PRD
STUDENT_NAME = "Diva Prayoga Alpariji Putra"
STUDENT_NIM = "237006173"
PARAM_A = 3  # Digit terakhir NIM (237006173 -> 3)
SEED_CORRECT = 237006173
SEED_WRONG = 237006174

# Pesan rahasia standar: NIM - Nama Lengkap - <kalimat bebas minimal 10 kata>
DEFAULT_SECRET_MESSAGE = (
    "237006173 - Diva Prayoga Alpariji Putra - "
    "Praktikum ini menguji bagaimana pesan dapat disembunyikan secara aman tanpa mengubah tampilan citra secara signifikan."
)

# Direktori Proyek
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
REFERENCES_DIR = BASE_DIR / "references"
OUTPUTS_DIR = BASE_DIR / "outputs"
RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = BASE_DIR / "figures"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
REPORT_DIR = BASE_DIR / "report"

ORIGINAL_COVER_PATH = ASSETS_DIR / "Diva_selfie.jpeg"
WORKING_COVER_PATH = ASSETS_DIR / "cover_working.png"


def validate_and_prepare_cover():
    """
    Fase P0: Validasi input citra cover dan simpan salinan kerja PNG.
    """
    if not ORIGINAL_COVER_PATH.exists():
        raise FileNotFoundError(f"File cover asli tidak ditemukan di: {ORIGINAL_COVER_PATH}")

    with Image.open(ORIGINAL_COVER_PATH) as img:
        orig_format = img.format
        orig_mode = img.mode
        width, height = img.size

        # Konversi ke RGB jika belum
        if orig_mode != "RGB":
            rgb_img = img.convert("RGB")
        else:
            rgb_img = img.copy()

        # Simpan salinan kerja lossless PNG jika belum ada
        rgb_img.save(WORKING_COVER_PATH, format="PNG")

        arr = np.array(rgb_img)
        channels = 3 if arr.ndim == 3 else 1
        total_bytes = arr.nbytes

        info = {
            "cover_original": str(ORIGINAL_COVER_PATH.name),
            "cover_working": str(WORKING_COVER_PATH.name),
            "format": orig_format,
            "mode": rgb_img.mode,
            "width": width,
            "height": height,
            "channels": channels,
            "dtype": str(arr.dtype),
            "total_pixels": width * height,
            "total_bytes": total_bytes,
        }

    return info


def load_working_cover_array():
    """Membuka cover_working.png sebagai numpy array uint8."""
    if not WORKING_COVER_PATH.exists():
        validate_and_prepare_cover()
    with Image.open(WORKING_COVER_PATH) as img:
        return np.array(img, dtype=np.uint8)


def calc_diff_stats(cover_arr, stego_arr):
    """Menghitung metrik perbedaan antara citra cover dan stego."""
    diff = np.abs(cover_arr.astype(int) - stego_arr.astype(int))
    max_diff = int(diff.max())
    changed_bytes = int(np.count_nonzero(diff))
    total_bytes = int(cover_arr.size)
    change_ratio = float(changed_bytes / total_bytes)
    return {
        "max_diff": max_diff,
        "changed_bytes": changed_bytes,
        "total_bytes": total_bytes,
        "change_ratio": change_ratio,
        "diff_array": diff,
    }


def calc_mse(cover_arr, stego_arr):
    """Menghitung Mean Squared Error (MSE)."""
    return float(np.mean((cover_arr.astype(float) - stego_arr.astype(float)) ** 2))


def calc_psnr(cover_arr, stego_arr):
    """Menghitung Peak Signal-to-Noise Ratio (PSNR) dalam dB."""
    mse = calc_mse(cover_arr, stego_arr)
    if mse == 0:
        return float("inf")
    return float(10.0 * np.log10((255.0 ** 2) / mse))


def calc_ber(original_bits, extracted_bits):
    """Menghitung Bit Error Rate (BER) dalam persen."""
    min_len = min(len(original_bits), len(extracted_bits))
    max_len = max(len(original_bits), len(extracted_bits))
    if max_len == 0:
        return 0.0, 0, 0
    errors = sum(1 for i in range(min_len) if original_bits[i] != extracted_bits[i])
    errors += (max_len - min_len)  # Missing/excess bits are errors
    ber = (errors / max_len) * 100.0
    return ber, errors, max_len
