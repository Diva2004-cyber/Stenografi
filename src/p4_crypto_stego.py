"""
src/p4_crypto_stego.py
Fase P4: Kombinasi Kriptografi dan Steganografi.

Arsitektur:
Plaintext -> Encryption (K_encryption) -> Ciphertext -> Random LSB Embedding (K_position) -> Stego-image

Stego-Keys:
- K_position   : Seed PRNG permutasi posisi (NIM = 237006173)
- K_encryption : Seed PRNG keystream XOR (987654321)

Tiga Skenario Wajib:
- Skenario A: Kedua key benar (K_pos benar, K_enc benar) -> Berhasil dipulihkan utuh (Exact match)
- Skenario B: Posisi benar, enkripsi salah (K_pos benar, K_enc salah) -> Ciphertext utuh, dekripsi salah/sampah
- Skenario C: Posisi salah (K_pos salah) -> Header & ciphertext rusak, pemulihan gagal total
"""

import sys
import os
import json
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

from common import (
    WORKING_COVER_PATH,
    OUTPUTS_DIR,
    RESULTS_DIR,
    DEFAULT_SECRET_MESSAGE,
    SEED_CORRECT,
    SEED_WRONG,
    calc_diff_stats,
    calc_mse,
    calc_psnr,
)

K_POSITION_CORRECT = SEED_CORRECT        # 237006173
K_POSITION_WRONG = SEED_WRONG            # 237006174
K_ENCRYPTION_CORRECT = 987654321         # Kunci enkripsi benar
K_ENCRYPTION_WRONG = 987654322           # Kunci enkripsi salah


def encrypt_xor_prng(plaintext_bytes, key_seed):
    """
    Enkripsi stream cipher XOR berbasis PRNG reproducible:
    C_i = P_i XOR Keystream_i
    """
    rng = np.random.default_rng(key_seed)
    keystream = rng.integers(0, 256, size=len(plaintext_bytes), dtype=np.uint8)
    ciphertext_bytes = bytes([p ^ k for p, k in zip(plaintext_bytes, keystream)])
    return ciphertext_bytes, keystream


def decrypt_xor_prng(ciphertext_bytes, key_seed):
    """
    Dekripsi stream cipher XOR berbasis PRNG:
    P_i = C_i XOR Keystream_i
    """
    rng = np.random.default_rng(key_seed)
    keystream = rng.integers(0, 256, size=len(ciphertext_bytes), dtype=np.uint8)
    decrypted_bytes = bytes([c ^ k for c, k in zip(ciphertext_bytes, keystream)])
    return decrypted_bytes


def embed_crypto_stego(cover_path, plaintext, stego_path, k_pos=K_POSITION_CORRECT, k_enc=K_ENCRYPTION_CORRECT):
    """
    Proses lengkap: Enkripsi plaintext -> Random LSB Embedding ke citra cover.
    """
    # 1. Konversi pesan ke bytes UTF-8
    if isinstance(plaintext, str):
        pt_bytes = plaintext.encode("utf-8")
    else:
        pt_bytes = bytes(plaintext)

    # 2. Enkripsi dengan K_encryption
    ct_bytes, keystream = encrypt_xor_prng(pt_bytes, k_enc)
    ct_len_bytes = len(ct_bytes)

    # 3. Bentuk bitstream: 32-bit header (panjang ciphertext) + ciphertext bits
    header_biner = format(ct_len_bytes, "032b")
    payload_biner = "".join([format(b, "08b") for b in ct_bytes])
    total_bitstream = header_biner + payload_biner
    total_bits = len(total_bitstream)

    # 4. Muat citra cover
    citra = Image.open(cover_path)
    w, h = citra.size
    cover_arr = np.array(citra, dtype=np.uint8)
    flat_bytes = cover_arr.flatten().copy()

    # 5. Permutasi posisi berbasis K_position
    rng_pos = np.random.default_rng(k_pos)
    permutation = rng_pos.permutation(flat_bytes.size)
    embed_indices = permutation[:total_bits]

    # 6. Penyisipan 1-bit LSB
    for i, idx in enumerate(embed_indices):
        bit_val = int(total_bitstream[i])
        flat_bytes[idx] = (flat_bytes[idx] & 0xFE) | bit_val

    stego_arr = flat_bytes.reshape((h, w, 3))
    Image.fromarray(stego_arr).save(stego_path, format="PNG")

    print(f"[CRYPTO-STEGO EMBED] K_position  : {k_pos}")
    print(f"[CRYPTO-STEGO EMBED] K_encryption: {k_enc}")
    print(f"[CRYPTO-STEGO EMBED] Plaintext   : {len(pt_bytes)} byte")
    print(f"[CRYPTO-STEGO EMBED] Ciphertext  : {ct_len_bytes} byte (Hex: {ct_bytes.hex()[:32]}...)")
    print(f"[CRYPTO-STEGO EMBED] Total Bit   : {total_bits} bit disisipkan ke {total_bits} posisi acak")
    print(f"[CRYPTO-STEGO EMBED] Stego path  : {stego_path}")

    return stego_arr, ct_bytes


def extract_crypto_stego(stego_path, k_pos, k_enc):
    """
    Proses ekstraksi & dekripsi menggunakan dua kunci:
    1. Membaca bitstream dari posisi acak berbasis k_pos
    2. Membaca 32-bit header untuk panjang ciphertext
    3. Membaca ciphertext bytes
    4. Mendekripsi ciphertext dengan k_enc
    """
    citra = Image.open(stego_path)
    flat_bytes = np.array(citra, dtype=np.uint8).flatten()
    total_bytes = flat_bytes.size

    # Permutasi posisi berbasis k_pos yang diinput
    rng_pos = np.random.default_rng(k_pos)
    permutation = rng_pos.permutation(total_bytes)

    # Langkah 1: Baca 32-bit header
    header_indices = permutation[:32]
    header_bits = "".join([str(flat_bytes[idx] & 1) for idx in header_indices])
    payload_len_bytes = int(header_bits, 2)

    max_capacity_bytes = (total_bytes - 32) // 8

    # Cek kewajaran header
    if payload_len_bytes > max_capacity_bytes or payload_len_bytes < 0:
        # Kunci posisi salah: header corrupt di luar kapasitas
        # Baca sampel 160 byte untuk melihat ciphertext rusak
        sample_len = 160
        payload_indices = permutation[32 : 32 + (sample_len * 8)]
        payload_bits = "".join([str(flat_bytes[idx] & 1) for idx in payload_indices])
        raw_ct = bytes([int(payload_bits[i : i + 8], 2) for i in range(0, len(payload_bits), 8)])
        raw_dec = decrypt_xor_prng(raw_ct, k_enc)

        return {
            "status": "FAILED_CORRUPT_POSITION",
            "header_decimal": payload_len_bytes,
            "ciphertext_hex": raw_ct.hex()[:32],
            "decrypted_hex": raw_dec.hex()[:32],
            "decrypted_repr": repr(raw_dec.decode("utf-8", errors="replace")),
            "is_exact_match": False,
            "explanation": "Kunci posisi salah -> header acak tidak valid di luar batas kapasitas citra.",
        }

    # Langkah 2: Baca tepat payload_len_bytes
    payload_bits_count = payload_len_bytes * 8
    payload_indices = permutation[32 : 32 + payload_bits_count]
    payload_bits = "".join([str(flat_bytes[idx] & 1) for idx in payload_indices])
    ct_extracted = bytes([int(payload_bits[i : i + 8], 2) for i in range(0, len(payload_bits), 8)])

    # Langkah 3: Dekripsi dengan k_enc
    decrypted_bytes = decrypt_xor_prng(ct_extracted, k_enc)

    try:
        decrypted_text = decrypted_bytes.decode("utf-8")
        is_clean_utf8 = True
    except UnicodeDecodeError:
        decrypted_text = decrypted_bytes.decode("utf-8", errors="replace")
        is_clean_utf8 = False

    return {
        "status": "SUCCESS" if is_clean_utf8 else "CORRUPTED_TEXT",
        "header_decimal": payload_len_bytes,
        "ciphertext_hex": ct_extracted.hex()[:32],
        "decrypted_hex": decrypted_bytes.hex()[:32],
        "decrypted_text": decrypted_text,
        "decrypted_repr": repr(decrypted_text),
        "is_exact_match": False,  # Akan divalidasi terhadap plaintext asli
        "explanation": "Payload berhasil dibaca dari posisi acak.",
    }


def run_p4_experiment():
    print("=" * 65)
    print("FASE P4: KOMBINASI KRIPTOGRAFI DAN STEGANOGRAFI")
    print("=" * 65)

    plaintext = DEFAULT_SECRET_MESSAGE
    stego_crypto_path = OUTPUTS_DIR / "p4" / "stego_crypto.png"

    print(f"Plaintext Asli ({len(plaintext)} karakter):")
    print(f"'{plaintext}'\n")

    # 1. Embedding dengan kedua kunci BENAR
    stego_arr, original_ct = embed_crypto_stego(
        WORKING_COVER_PATH,
        plaintext,
        stego_crypto_path,
        k_pos=K_POSITION_CORRECT,
        k_enc=K_ENCRYPTION_CORRECT,
    )

    print("\n" + "=" * 65)
    print("PENGUJIAN TIGA SKENARIO KUNCI (Wajib P4)")
    print("=" * 65)

    # -------------------------------------------------------------
    # Skenario A: Kedua Kunci Benar
    # -------------------------------------------------------------
    print("\n[SKENARIO A] Kedua Kunci Benar")
    print(f"  K_position   = {K_POSITION_CORRECT} (BENAR)")
    print(f"  K_encryption = {K_ENCRYPTION_CORRECT} (BENAR)")
    res_a = extract_crypto_stego(stego_crypto_path, K_POSITION_CORRECT, K_ENCRYPTION_CORRECT)
    res_a["is_exact_match"] = (res_a.get("decrypted_text") == plaintext)
    print(f"  Ciphertext Hex : {res_a['ciphertext_hex']}...")
    print(f"  Hasil Dekripsi : '{res_a.get('decrypted_text')}'")
    print(f"  Kesesuaian     : {res_a['is_exact_match']} (Ekspektasi: True)")

    # -------------------------------------------------------------
    # Skenario B: Posisi Benar, Enkripsi Salah
    # -------------------------------------------------------------
    print("\n[SKENARIO B] Kunci Posisi Benar, Kunci Enkripsi Salah")
    print(f"  K_position   = {K_POSITION_CORRECT} (BENAR)")
    print(f"  K_encryption = {K_ENCRYPTION_WRONG} (SALAH)")
    res_b = extract_crypto_stego(stego_crypto_path, K_POSITION_CORRECT, K_ENCRYPTION_WRONG)
    res_b["is_exact_match"] = (res_b.get("decrypted_text") == plaintext)
    print(f"  Ciphertext Hex : {res_b['ciphertext_hex']}... (Identik dengan aslinya: {res_b['ciphertext_hex'] == original_ct.hex()[:32]})")
    print(f"  Hasil Dekripsi : {res_b['decrypted_repr']}")
    print(f"  Kesesuaian     : {res_b['is_exact_match']} (Ekspektasi: False)")
    print("  Catatan: Lawan berhasil menemukan payload tersembunyi, tetapi maknanya tetap terlindungi secara kriptografis.")

    # -------------------------------------------------------------
    # Skenario C: Kunci Posisi Salah
    # -------------------------------------------------------------
    print("\n[SKENARIO C] Kunci Posisi Salah")
    print(f"  K_position   = {K_POSITION_WRONG} (SALAH)")
    print(f"  K_encryption = {K_ENCRYPTION_CORRECT}")
    res_c = extract_crypto_stego(stego_crypto_path, K_POSITION_WRONG, K_ENCRYPTION_CORRECT)
    print(f"  Status Ekstraksi: {res_c['status']}")
    print(f"  Header Terbaca  : {res_c.get('header_decimal'):,} byte")
    print(f"  Hasil Dekripsi  : {res_c['decrypted_repr']}")
    print(f"  Kesesuaian      : {res_c['is_exact_match']} (Ekspektasi: False)")
    print("  Catatan: Lawan bahkan tidak dapat merekonstruksi ciphertext karena tidak mengetahui lokasi bit.")

    # 2. Metrik Kualitas Citra Stego
    cover_arr = np.array(Image.open(WORKING_COVER_PATH), dtype=np.uint8)
    diff_stats = calc_diff_stats(cover_arr, stego_arr)
    mse = calc_mse(cover_arr, stego_arr)
    psnr = calc_psnr(cover_arr, stego_arr)

    print("\n" + "=" * 65)
    print("METRIK CITRA STEGO KRIPTO-STEGANOGRAFI")
    print("=" * 65)
    print(f"Max Diff       : {diff_stats['max_diff']}")
    print(f"Byte Berubah   : {diff_stats['changed_bytes']:,} dari {diff_stats['total_bytes']:,} ({diff_stats['change_ratio']*100:.4f}%)")
    print(f"MSE            : {mse:.6f}")
    print(f"PSNR           : {psnr:.2f} dB")

    # 3. Simpan Hasil Lengkap ke JSON
    results_p4 = {
        "experiment": "P4_Crypto_Stego",
        "plaintext": plaintext,
        "keys": {
            "k_position_correct": K_POSITION_CORRECT,
            "k_position_wrong": K_POSITION_WRONG,
            "k_encryption_correct": K_ENCRYPTION_CORRECT,
            "k_encryption_wrong": K_ENCRYPTION_WRONG,
        },
        "original_ciphertext_hex_prefix": original_ct.hex()[:64],
        "scenario_a": res_a,
        "scenario_b": res_b,
        "scenario_c": res_c,
        "image_quality": {
            "max_diff": diff_stats["max_diff"],
            "changed_bytes": diff_stats["changed_bytes"],
            "total_bytes": diff_stats["total_bytes"],
            "change_ratio_pct": diff_stats["change_ratio"] * 100,
            "mse": mse,
            "psnr_db": psnr,
        }
    }

    json_path = RESULTS_DIR / "p4_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results_p4, f, indent=4)
    print(f"\n[HASIL TERSIMPAN] Seluruh hasil skenario P4 disimpan di: {json_path}")

    return results_p4


if __name__ == "__main__":
    run_p4_experiment()
