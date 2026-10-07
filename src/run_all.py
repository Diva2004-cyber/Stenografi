"""
src/run_all.py
Pipeline Otomatis Eksekusi dan Validasi Seluruh Fase Praktikum Steganografi (P0 - Bonus).

Menjalankan dan memverifikasi:
1. P0: Validasi input citra cover (Diva_selfie.jpeg -> cover_working.png)
2. P1: Baseline slide 74–77 dan P1 Fixed (3 kanal, bitwise LSB, 32-bit header)
3. P2: Random LSB dengan stego-key (seed benar vs salah, Change Map)
4. P3: m-bit LSB (m=1..4, 100% capacity, MSE/PSNR, grafik & grid)
5. P4: Kombinasi kriptografi + steganografi (3 skenario kunci)
6. P5: Pengaruh format file (PNG, BMP, JPEG quality=95, BER)
7. Bonus: Steganalisis visual bidang LSB & statistik Chi-Square PoV
8. Assertion & Acceptance verification
"""

import sys
import os
import json
import time
from datetime import datetime
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

from common import (
    STUDENT_NAME,
    STUDENT_NIM,
    PARAM_A,
    SEED_CORRECT,
    SEED_WRONG,
    DEFAULT_SECRET_MESSAGE,
    BASE_DIR,
    ASSETS_DIR,
    OUTPUTS_DIR,
    RESULTS_DIR,
    FIGURES_DIR,
    WORKING_COVER_PATH,
    ORIGINAL_COVER_PATH,
)

from p1_baseline import run_baseline_experiment
from p1_fixed import run_fixed_experiment
from p2_random_lsb import run_p2_experiment
from p3_mbit_lsb import run_p3_experiment
from p4_crypto_stego import run_p4_experiment
from p5_formats import run_p5_experiment
from bonus_steganalysis import run_bonus_steganalysis


def main():
    start_time = time.time()
    timestamp_str = datetime.now().isoformat()

    print("=" * 75)
    print("   UNIVERSITAS SILIWANGI - PRAKTIKUM STEGANOGRAFI (TUGAS 4)")
    print(f"   Mahasiswa : {STUDENT_NAME} (NIM: {STUDENT_NIM})")
    print(f"   Parameter : A = {PARAM_A} | Seed P2 = {SEED_CORRECT}")
    print(f"   Waktu     : {timestamp_str}")
    print("=" * 75)

    # 1. Catat Metadata Lingkungan Eksekusi
    metadata = {
        "student_name": STUDENT_NAME,
        "student_nim": STUDENT_NIM,
        "param_a": PARAM_A,
        "seed_correct": SEED_CORRECT,
        "seed_wrong": SEED_WRONG,
        "cover_original": str(ORIGINAL_COVER_PATH),
        "timestamp": timestamp_str,
        "python_version": sys.version,
        "numpy_version": np.__version__,
        "pillow_version": Image.__version__,
    }

    test_results = {}
    assertions = []

    def check(name, condition, details=""):
        status = "PASS" if condition else "FAIL"
        assertions.append({
            "check": name,
            "status": status,
            "details": details,
        })
        badge = "[✓ PASS]" if condition else "[✗ FAIL]"
        print(f"  {badge} {name}: {details}")
        return condition

    # ---------------------------------------------------------
    # PIPELINE STEP 1: P0 & P1 Baseline
    # ---------------------------------------------------------
    print("\n>>> MENJALANKAN FASE P0 & P1 BASELINE...")
    res_p1_base = run_baseline_experiment()
    test_results["p1_baseline"] = res_p1_base

    # ---------------------------------------------------------
    # PIPELINE STEP 2: P1 Fixed
    # ---------------------------------------------------------
    print("\n>>> MENJALANKAN FASE P1 FIXED...")
    res_p1_fixed = run_fixed_experiment()
    test_results["p1_fixed"] = res_p1_fixed

    # ---------------------------------------------------------
    # PIPELINE STEP 3: P2 Random LSB
    # ---------------------------------------------------------
    print("\n>>> MENJALANKAN FASE P2 RANDOM LSB...")
    res_p2 = run_p2_experiment()
    test_results["p2"] = res_p2

    # ---------------------------------------------------------
    # PIPELINE STEP 4: P3 m-bit LSB
    # ---------------------------------------------------------
    print("\n>>> MENJALANKAN FASE P3 m-bit LSB...")
    res_p3 = run_p3_experiment()
    test_results["p3"] = res_p3

    # ---------------------------------------------------------
    # PIPELINE STEP 5: P4 Crypto + Stego
    # ---------------------------------------------------------
    print("\n>>> MENJALANKAN FASE P4 KOMBINASI KRIPTO-STEGANO...")
    res_p4 = run_p4_experiment()
    test_results["p4"] = res_p4

    # ---------------------------------------------------------
    # PIPELINE STEP 6: P5 Pengaruh Format File
    # ---------------------------------------------------------
    print("\n>>> MENJALANKAN FASE P5 PENGARUH FORMAT FILE...")
    res_p5 = run_p5_experiment()
    test_results["p5"] = res_p5

    # ---------------------------------------------------------
    # PIPELINE STEP 7: Bonus Visual Steganalysis
    # ---------------------------------------------------------
    print("\n>>> MENJALANKAN FASE BONUS STEGANALISIS...")
    res_bonus = run_bonus_steganalysis()
    test_results["bonus"] = res_bonus

    # ---------------------------------------------------------
    # PIPELINE STEP 8: ASSERTIONS & ACCEPTANCE VERIFICATION
    # ---------------------------------------------------------
    print("\n" + "=" * 75)
    print("                    VALIDASI & VERIFIKASI AKHIR")
    print("=" * 75)

    all_passed = True

    # P0 Checks
    c1 = check(
        "P0_Cover_Image_Valid",
        WORKING_COVER_PATH.exists() and res_p1_base["cover_info"]["mode"] == "RGB",
        f"Dimensi {res_p1_base['cover_info']['width']}x{res_p1_base['cover_info']['height']}, Mode RGB"
    )

    # P1 Checks
    c2 = check(
        "P1_Fixed_Bitwise_LSB_Max_Diff",
        res_p1_fixed["max_diff"] == 1,
        f"|delta|_max = {res_p1_fixed['max_diff']} (Wajib <= 1)"
    )
    c3 = check(
        "P1_Fixed_Exact_Extraction",
        res_p1_fixed["is_exact_match"],
        "Pesan rahasia terekstrak 100% identik"
    )
    c4 = check(
        "P1_Fixed_3Channels_Capacity",
        res_p1_fixed["capacity_analysis"]["fixed_utilization_percent"] == 100.0,
        f"Kapasitas 100% ({res_p1_fixed['capacity_analysis']['fixed_capacity_kb']:.1f} KB)"
    )
    c5 = check(
        "P1_Fixed_Delimiter_Word_Stego_Test",
        res_p1_fixed["delimiter_test"]["extracted_successfully"],
        "Pesan yang mengandung kata 'stego' tidak mengalami false termination"
    )

    # P2 Checks
    c6 = check(
        "P2_Correct_Seed_Match",
        res_p2["scenario_correct_key"]["is_exact_match"],
        f"Ekstraksi seed={SEED_CORRECT} berhasil identik"
    )
    c7 = check(
        "P2_Wrong_Seed_Corruption",
        not res_p2["scenario_wrong_key"]["is_exact_match"],
        f"Ekstraksi seed={SEED_WRONG} gagal/menghasilkan teks rusak"
    )
    c8 = check(
        "P2_Change_Maps_Created",
        (FIGURES_DIR / "p2_change_map_sequential.png").exists() and (FIGURES_DIR / "p2_change_map_random.png").exists(),
        "Change map sequential dan random tersimpan"
    )

    # P3 Checks
    p3_max_diffs_valid = all(
        row["Max_Diff_Actual"] <= row["Max_Diff_Theory"] for row in res_p3
    )
    c9 = check(
        "P3_mbit_Max_Diff_Bounded",
        p3_max_diffs_valid,
        "Untuk semua m, |delta|_max <= 2^m - 1 terbukti valid"
    )
    c10 = check(
        "P3_PSNR_Tradeoff_Order",
        res_p3[0]["PSNR_dB"] > res_p3[1]["PSNR_dB"] > res_p3[2]["PSNR_dB"] > res_p3[3]["PSNR_dB"],
        f"PSNR m=1 ({res_p3[0]['PSNR_dB']} dB) > m=4 ({res_p3[3]['PSNR_dB']} dB)"
    )
    c11 = check(
        "P3_Artifacts_Exported",
        (RESULTS_DIR / "p3_results.csv").exists() and (FIGURES_DIR / "p3_psnr_vs_m.png").exists(),
        "Tabel CSV dan grafik PSNR vs m tersimpan"
    )

    # P4 Checks
    c12 = check(
        "P4_Scenario_A_Both_Keys_Correct",
        res_p4["scenario_a"]["is_exact_match"],
        "K_pos benar + K_enc benar -> Plaintext pulih 100%"
    )
    c13 = check(
        "P4_Scenario_B_Wrong_Encryption_Key",
        not res_p4["scenario_b"]["is_exact_match"],
        "K_pos benar + K_enc salah -> Ciphertext terbaca tapi gagal didekripsi"
    )
    c14 = check(
        "P4_Scenario_C_Wrong_Position_Key",
        not res_p4["scenario_c"]["is_exact_match"],
        "K_pos salah -> Header & ciphertext rusak total"
    )

    # P5 Checks
    c15 = check(
        "P5_Lossless_Formats_Zero_BER",
        res_p5["PNG"]["bit_errors"] == 0 and res_p5["BMP"]["bit_errors"] == 0,
        f"PNG BER = {res_p5['PNG']['ber_percent']}%, BMP BER = {res_p5['BMP']['ber_percent']}%"
    )
    c16 = check(
        "P5_JPEG_Lossy_Destruction",
        res_p5["JPEG"]["ber_percent"] > 40.0,
        f"JPEG quality=95 BER = {res_p5['JPEG']['ber_percent']:.2f}% (merusak LSB)"
    )

    # Bonus Checks
    c17 = check(
        "Bonus_LSB_Planes_Demarcation",
        (FIGURES_DIR / "bonus_lsb_planes.png").exists(),
        "Visualisasi batas horizontal LSB 50% tersimpan"
    )
    c18 = check(
        "Bonus_Chi_Square_PoV_Drop",
        res_bonus["chi_square_pov"]["top_half_stego_chi2"] < 200.0,
        f"Chi2 anjlok dari {res_bonus['chi_square_pov']['top_half_cover_chi2']:.1f} ke {res_bonus['chi_square_pov']['top_half_stego_chi2']:.1f}"
    )

    all_passed = all(a["status"] == "PASS" for a in assertions)

    elapsed_time = time.time() - start_time
    print("-" * 75)
    print(f"TOTAL PENGECEKAN: {len(assertions)} | STATUS: {'SEMUA PASS (100%)' if all_passed else 'ADA YANG GAGAL'}")
    print(f"Waktu Eksekusi  : {elapsed_time:.2f} detik")
    print("=" * 75)

    # Simpan Ringkasan Akhir
    summary_data = {
        "metadata": metadata,
        "execution_duration_seconds": elapsed_time,
        "all_passed": all_passed,
        "total_checks": len(assertions),
        "passed_checks": sum(1 for a in assertions if a["status"] == "PASS"),
        "assertions": assertions,
        "phase_results": test_results,
    }

    summary_file = RESULTS_DIR / "pipeline_summary.json"
    metadata_file = RESULTS_DIR / "experiment_metadata.json"

    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=4)
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    print(f"[RINGKASAN TERSIMPAN] Summary disimpan di: {summary_file}")
    print(f"[METADATA TERSIMPAN] Metadata disimpan di: {metadata_file}\n")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
