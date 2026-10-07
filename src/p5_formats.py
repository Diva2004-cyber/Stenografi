"""
src/p5_formats.py
Fase P5: Pengaruh Format File terhadap Keutuhan Pesan Steganografi (PNG, BMP, JPEG).

Eksperimen:
1. Menyimpan citra stego yang sama ke dalam tiga format:
   - PNG (Lossless)
   - BMP (Lossless / Uncompressed)
   - JPEG (Lossy compression, parameter quality = 95)
2. Melakukan ekstraksi bitstream dari masing-masing file citra.
3. Menghitung Bit Error Rate (BER):
   BER = (Jumlah Bit Salah / Total Bit) * 100%
4. Mengamati keterbacaan pesan teks hasil ekstraksi.
5. Mengekspor hasil ke results/p5_ber.csv dan results/p5_results.json.
"""

import sys
import os
import json
import numpy as np
import pandas as pd
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

from common import (
    WORKING_COVER_PATH,
    OUTPUTS_DIR,
    RESULTS_DIR,
    DEFAULT_SECRET_MESSAGE,
    calc_ber,
)


def run_p5_experiment():
    print("=" * 65)
    print("FASE P5: PENGARUH FORMAT FILE (PNG, BMP, JPEG quality=95)")
    print("=" * 65)

    # 1. Siapkan citra cover dan bitstream pesan asli
    cover_img = Image.open(WORKING_COVER_PATH)
    w, h = cover_img.size
    cover_arr = np.array(cover_img, dtype=np.uint8)

    pesan_bytes = DEFAULT_SECRET_MESSAGE.encode("utf-8")
    payload_len = len(pesan_bytes)
    header_bits = format(payload_len, "032b")
    payload_bits = "".join([format(b, "08b") for b in pesan_bytes])
    expected_bits = header_bits + payload_bits
    total_bits = len(expected_bits)

    print(f"Pesan uji: {DEFAULT_SECRET_MESSAGE[:50]}... ({payload_len} byte)")
    print(f"Total bit stream (+ 32-bit header): {total_bits} bit\n")

    # 2. Sisipkan pesan secara sekuensial (3 kanal) ke cover_arr
    stego_arr = cover_arr.copy()
    flat_bytes = stego_arr.reshape(-1)

    for i in range(total_bits):
        bit_val = int(expected_bits[i])
        flat_bytes[i] = (flat_bytes[i] & 0xFE) | bit_val

    stego_arr_final = flat_bytes.reshape((h, w, 3))
    stego_pil = Image.fromarray(stego_arr_final)

    # 3. Simpan ke tiga format file berbeda
    os.makedirs(OUTPUTS_DIR / "p5", exist_ok=True)
    paths = {
        "PNG": (OUTPUTS_DIR / "p5" / "stego.png", {}),
        "BMP": (OUTPUTS_DIR / "p5" / "stego.bmp", {}),
        "JPEG": (OUTPUTS_DIR / "p5" / "stego.jpg", {"quality": 95, "subsampling": 0}),
    }

    file_sizes = {}
    for fmt, (path, kwargs) in paths.items():
        stego_pil.save(path, format=fmt, **kwargs)
        file_sizes[fmt] = os.path.getsize(path)
        print(f"[SAVE] Disimpan dalam format {fmt:4s}: {path} ({file_sizes[fmt]:,} byte)")

    print("\n" + "=" * 65)
    print("HASIL EKSTRAKSI DAN PENGUKURAN BIT ERROR RATE (BER)")
    print("=" * 65)

    results_table = []
    detailed_results = {}

    for fmt, (path, kwargs) in paths.items():
        reloaded_img = Image.open(path)
        reloaded_arr = np.array(reloaded_img, dtype=np.uint8)
        reloaded_flat = reloaded_arr.reshape(-1)

        # Ekstraksi total_bits pertama
        extracted_bits = "".join([str(reloaded_flat[i] & 1) for i in range(total_bits)])

        # Hitung Bit Error Rate (BER)
        ber, bit_errors, total_evaluated = calc_ber(expected_bits, extracted_bits)

        # Coba rekonstruksi header dan teks
        extracted_hdr = extracted_bits[:32]
        extracted_payload_len = int(extracted_hdr, 2)

        # Baca byte teks
        payload_bits_part = extracted_bits[32:]
        extracted_bytes = bytearray()
        for i in range(0, len(payload_bits_part), 8):
            extracted_bytes.append(int(payload_bits_part[i : i + 8], 2))

        try:
            extracted_text = extracted_bytes.decode("utf-8")
            text_status = "Terekstrak Sempurna"
        except UnicodeDecodeError:
            extracted_text = extracted_bytes.decode("utf-8", errors="replace")
            text_status = "Teks Rusak (Corrupted)"

        quality_param = "95" if fmt == "JPEG" else "-"

        print(f"--- Format: {fmt} (Quality: {quality_param}) ---")
        print(f"  Ukuran File   : {file_sizes[fmt]:,} byte")
        print(f"  Bit Error     : {bit_errors} dari {total_bits} bit")
        print(f"  BER           : {ber:.2f}%")
        print(f"  Header 32-bit : {extracted_hdr} (Desimal: {extracted_payload_len})")
        print(f"  Status Teks   : {text_status}")
        if fmt == "JPEG":
            print(f"  Sampel Teks   : {repr(extracted_text[:60])}...")
        else:
            print(f"  Teks Sesuai?  : {extracted_text == DEFAULT_SECRET_MESSAGE}")
        print()

        results_table.append({
            "Format": fmt,
            "Quality": quality_param,
            "File_Size_Bytes": file_sizes[fmt],
            "Bit_Error": bit_errors,
            "Total_Bit": total_bits,
            "BER_Pct": round(ber, 2),
            "Text_Status": text_status,
        })

        detailed_results[fmt] = {
            "file_path": str(path),
            "file_size_bytes": file_sizes[fmt],
            "quality": quality_param,
            "bit_errors": bit_errors,
            "total_bits": total_bits,
            "ber_percent": ber,
            "header_bits": extracted_hdr,
            "extracted_payload_len": extracted_payload_len,
            "text_status": text_status,
            "sample_extracted_text": repr(extracted_text[:100]),
            "is_exact_match": (extracted_text == DEFAULT_SECRET_MESSAGE),
        }

    # 4. Simpan hasil ke CSV dan JSON
    df = pd.DataFrame(results_table)
    csv_path = RESULTS_DIR / "p5_ber.csv"
    df.to_csv(csv_path, index=False)
    print(f"[HASIL CSV] Tabel BER disimpan di: {csv_path}")

    json_path = RESULTS_DIR / "p5_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(detailed_results, f, indent=4)
    print(f"[HASIL JSON] Detail eksperimen disimpan di: {json_path}")

    return detailed_results


if __name__ == "__main__":
    run_p5_experiment()
