"""
build_practicum_report.py
=========================
Generator Laporan Akademik Praktikum Kriptografi Modul 6 (Steganografi Citra Digital)
Format Dokumen : PDF Standar Akademik Sarjana (A4)
Engine         : PyMuPDF (fitz)
Penulis        : Diva Prayoga Alpariji Putra (NIM: 237006173)
Institusi      : Universitas Siliwangi
"""

import os
import json
import csv
import math
import fitz
from PIL import Image

def get_base_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class AcademicReportBuilder:
    def __init__(self, output_path):
        self.output_path = output_path
        self.doc = fitz.open()
        self.page_w = 595.28  # A4 width in pt
        self.page_h = 841.89  # A4 height in pt
        
        # Margins & Usable Dimensions
        self.margin_x = 54.0   # 0.75 in
        self.margin_top = 55.0
        self.margin_bottom = 50.0
        self.content_w = self.page_w - (2 * self.margin_x)  # 487.28 pt
        self.content_y_min = self.margin_top + 10.0
        self.content_y_max = self.page_h - self.margin_bottom - 20.0
        
        # Colors (Professional Academic Navy Palette)
        self.c_primary = (0.102, 0.212, 0.365)     # #1A365D Dark Navy
        self.c_secondary = (0.169, 0.424, 0.690)   # #2B6CB0 Steel Blue
        self.c_accent = (0.843, 0.620, 0.180)      # #D69E2E Warm Gold
        self.c_text = (0.176, 0.216, 0.282)        # #2D3748 Charcoal Body Text
        self.c_muted = (0.431, 0.490, 0.569)       # #6E7D91 Muted Slate
        self.c_bg_light = (0.969, 0.980, 0.988)    # #F7FAFC Soft Gray
        self.c_border = (0.886, 0.910, 0.941)      # #E2E8F0 Subtle Border
        self.c_white = (1.0, 1.0, 1.0)
        self.c_success_bg = (0.941, 0.980, 0.949)  # Soft green
        self.c_success_border = (0.239, 0.592, 0.361)
        self.c_alert_bg = (0.996, 0.953, 0.953)    # Soft red
        self.c_alert_border = (0.886, 0.325, 0.325)
        
        # Fonts
        self.f_reg = "arial"
        self.f_bold = "arialbd"
        self.f_italic = "ariali"
        self.f_code = "consola"
        
        self.current_page = None
        self.current_y = self.content_y_min
        self.page_number = 0
        self.toc_items = []

    def _setup_page_fonts(self, page):
        page.insert_font(fontname="arial", fontfile="C:/Windows/Fonts/arial.ttf")
        page.insert_font(fontname="arialbd", fontfile="C:/Windows/Fonts/arialbd.ttf")
        page.insert_font(fontname="ariali", fontfile="C:/Windows/Fonts/ariali.ttf")
        page.insert_font(fontname="consola", fontfile="C:/Windows/Fonts/consola.ttf")

    def new_page(self):
        self.current_page = self.doc.new_page(width=self.page_w, height=self.page_h)
        self._setup_page_fonts(self.current_page)
        self.page_number += 1
        self.current_y = self.content_y_min
        return self.current_page

    def check_space(self, needed_h):
        if self.current_y + needed_h > self.content_y_max:
            self.new_page()

    def add_chapter_heading(self, bab_str, title_str):
        # Setiap BAB utama dimulai pada halaman baru untuk standar akademik profesional
        if self.page_number > 0 and self.current_y > self.content_y_min + 50:
            self.new_page()
            
        self.check_space(75)
        self.toc_items.append((bab_str, title_str, self.page_number))
        
        # Accent background band
        band_rect = fitz.Rect(self.margin_x, self.current_y, self.margin_x + self.content_w, self.current_y + 46)
        self.current_page.draw_rect(band_rect, color=None, fill=self.c_bg_light)
        
        # Left primary color bar
        bar_rect = fitz.Rect(self.margin_x, self.current_y, self.margin_x + 5, self.current_y + 46)
        self.current_page.draw_rect(bar_rect, color=None, fill=self.c_primary)
        
        # Chapter sub-label
        r_sub = fitz.Rect(self.margin_x + 14, self.current_y + 5, self.margin_x + self.content_w - 10, self.current_y + 19)
        self.current_page.insert_textbox(r_sub, bab_str.upper(), fontname=self.f_bold, fontsize=8.5, color=self.c_secondary)
        
        # Chapter title
        r_title = fitz.Rect(self.margin_x + 14, self.current_y + 20, self.margin_x + self.content_w - 10, self.current_y + 42)
        self.current_page.insert_textbox(r_title, title_str, fontname=self.f_bold, fontsize=13.0, color=self.c_primary)
        
        self.current_y += 56

    def add_section_heading(self, title_str):
        self.check_space(115)
        r_title = fitz.Rect(self.margin_x, self.current_y, self.margin_x + self.content_w, self.current_y + 20)
        self.current_page.insert_textbox(r_title, title_str, fontname=self.f_bold, fontsize=11.2, color=self.c_primary)
        
        line_y = self.current_y + 21
        self.current_page.draw_line(fitz.Point(self.margin_x, line_y), 
                                    fitz.Point(self.margin_x + self.content_w, line_y), 
                                    color=self.c_border, width=0.8)
        self.current_y += 28

    def add_subsection_heading(self, title_str):
        self.check_space(60)
        r_title = fitz.Rect(self.margin_x, self.current_y, self.margin_x + self.content_w, self.current_y + 16)
        self.current_page.insert_textbox(r_title, title_str, fontname=self.f_bold, fontsize=9.8, color=self.c_secondary)
        self.current_y += 20

    def add_paragraph(self, text, space_after=6.0, fontsize=9.2, color=None, align=fitz.TEXT_ALIGN_JUSTIFY):
        if color is None:
            color = self.c_text
            
        lines = max(1, math.ceil(len(text) / 85.0) + text.count('\n'))
        est_h = lines * (fontsize * 1.35) + space_after
        
        if self.current_y + est_h > self.content_y_max and est_h < 300:
            self.new_page()
            
        box_rect = fitz.Rect(self.margin_x, self.current_y, self.margin_x + self.content_w, self.content_y_max)
        rc = self.current_page.insert_textbox(box_rect, text, fontname=self.f_reg, fontsize=fontsize, 
                                              color=color, align=align, lineheight=1.28)
        
        if rc >= 0:
            h_used = (self.content_y_max - self.current_y) - rc
            self.current_y += h_used + space_after
        else:
            self.new_page()
            box_rect2 = fitz.Rect(self.margin_x, self.current_y, self.margin_x + self.content_w, self.content_y_max)
            rc2 = self.current_page.insert_textbox(box_rect2, text, fontname=self.f_reg, fontsize=fontsize, 
                                                   color=color, align=align, lineheight=1.28)
            h_used = (self.content_y_max - self.current_y) - max(0, rc2)
            self.current_y += h_used + space_after

    def add_bullet(self, title, desc, space_after=4.0):
        full_text = f"•  {title}: {desc}" if title else f"•  {desc}"
        lines = max(1, math.ceil(len(full_text) / 82.0) + full_text.count('\n'))
        est_h = lines * 12.5 + space_after
        
        if self.current_y + est_h > self.content_y_max:
            self.new_page()
            
        box_rect = fitz.Rect(self.margin_x + 10, self.current_y, self.margin_x + self.content_w, self.content_y_max)
        rc = self.current_page.insert_textbox(box_rect, full_text, fontname=self.f_reg, fontsize=9.0, 
                                              color=self.c_text, lineheight=1.25)
        h_used = (self.content_y_max - self.current_y) - max(0, rc)
        self.current_y += h_used + space_after

    def add_callout(self, text, title=None, style="info", space_after=8.0):
        lines = max(1, math.ceil(len(text) / 80.0) + (text.count('\n') + (2 if title else 0)))
        est_h = max(38, lines * 13.0 + 16)
        
        if self.current_y + est_h > self.content_y_max:
            self.new_page()
            
        bg_col = self.c_bg_light
        border_col = self.c_secondary
        if style == "success":
            bg_col = self.c_success_bg
            border_col = self.c_success_border
        elif style == "alert":
            bg_col = self.c_alert_bg
            border_col = self.c_alert_border
            
        box_rect = fitz.Rect(self.margin_x, self.current_y, self.margin_x + self.content_w, self.current_y + est_h)
        self.current_page.draw_rect(box_rect, color=self.c_border, fill=bg_col, width=0.6)
        
        # Left indicator bar
        bar_rect = fitz.Rect(self.margin_x, self.current_y, self.margin_x + 4, self.current_y + est_h)
        self.current_page.draw_rect(bar_rect, color=None, fill=border_col)
        
        cur_text_y = self.current_y + 7
        if title:
            r_t = fitz.Rect(self.margin_x + 12, cur_text_y, self.margin_x + self.content_w - 12, cur_text_y + 14)
            self.current_page.insert_textbox(r_t, title, fontname=self.f_bold, fontsize=9.0, color=border_col)
            cur_text_y += 15
            
        r_b = fitz.Rect(self.margin_x + 12, cur_text_y, self.margin_x + self.content_w - 12, self.current_y + est_h - 6)
        self.current_page.insert_textbox(r_b, text, fontname=self.f_reg, fontsize=8.6, color=self.c_text, lineheight=1.22)
        
        self.current_y += est_h + space_after

    def add_table(self, headers, rows, col_widths=None, col_aligns=None, space_after=10.0):
        num_cols = len(headers)
        if col_widths is None:
            w_per_col = self.content_w / num_cols
            col_widths = [w_per_col] * num_cols
            
        if col_aligns is None:
            col_aligns = [fitz.TEXT_ALIGN_LEFT] * num_cols
            
        # Hitung tinggi header secara adaptif
        header_lines = max([math.ceil(len(str(h)) / max(1, col_widths[i] / 5.2)) for i, h in enumerate(headers)])
        header_h = max(22.0, header_lines * 11.0 + 8.0)
        
        # Hitung tinggi masing-masing baris secara dinamis
        row_heights = []
        for row in rows:
            max_lines = 1
            for c_idx, val in enumerate(row):
                c_w = col_widths[c_idx]
                lines = math.ceil(len(str(val)) / max(1, c_w / 5.2)) + str(val).count('\n')
                if lines > max_lines:
                    max_lines = lines
            rh = max(18.0, max_lines * 10.5 + 7.0)
            row_heights.append(rh)
            
        total_h = header_h + sum(row_heights)
        
        if self.current_y + total_h > self.content_y_max:
            self.new_page()
            
        start_y = self.current_y
        
        # Header background
        h_rect = fitz.Rect(self.margin_x, start_y, self.margin_x + self.content_w, start_y + header_h)
        self.current_page.draw_rect(h_rect, color=None, fill=self.c_primary)
        
        # Header texts
        cur_x = self.margin_x
        for i, h_text in enumerate(headers):
            cell_w = col_widths[i]
            r_cell = fitz.Rect(cur_x + 3, start_y + 4, cur_x + cell_w - 3, start_y + header_h - 2)
            self.current_page.insert_textbox(r_cell, str(h_text), fontname=self.f_bold, fontsize=7.6, 
                                             color=self.c_white, align=col_aligns[i], lineheight=1.15)
            cur_x += cell_w
            
        cur_row_y = start_y + header_h
        for r_idx, row in enumerate(rows):
            rh = row_heights[r_idx]
            fill_col = self.c_bg_light if (r_idx % 2 == 1) else self.c_white
            row_rect = fitz.Rect(self.margin_x, cur_row_y, self.margin_x + self.content_w, cur_row_y + rh)
            self.current_page.draw_rect(row_rect, color=None, fill=fill_col)
            
            # Bottom row divider
            self.current_page.draw_line(fitz.Point(self.margin_x, cur_row_y + rh), 
                                        fitz.Point(self.margin_x + self.content_w, cur_row_y + rh), 
                                        color=self.c_border, width=0.5)
            
            cur_x = self.margin_x
            for c_idx, val in enumerate(row):
                cell_w = col_widths[c_idx]
                r_cell = fitz.Rect(cur_x + 4, cur_row_y + 3, cur_x + cell_w - 4, cur_row_y + rh - 2)
                f_name = self.f_bold if c_idx == 0 else self.f_reg
                self.current_page.insert_textbox(r_cell, str(val), fontname=f_name, fontsize=7.6, 
                                                 color=self.c_text, align=col_aligns[c_idx], lineheight=1.18)
                cur_x += cell_w
            cur_row_y += rh
            
        outer_rect = fitz.Rect(self.margin_x, start_y, self.margin_x + self.content_w, cur_row_y)
        self.current_page.draw_rect(outer_rect, color=self.c_secondary, width=0.7)
        
        self.current_y = cur_row_y + space_after

    def add_image(self, img_path, caption, max_h=190.0, space_after=10.0):
        if not os.path.exists(img_path):
            self.add_callout(f"File gambar tidak ditemukan: {img_path}", title="Image Missing", style="alert")
            return
            
        try:
            with Image.open(img_path) as im:
                orig_w, orig_h = im.size
        except Exception:
            orig_w, orig_h = 1000, 400
            
        aspect = orig_h / orig_w
        img_w = min(self.content_w, 460.0)
        img_h = img_w * aspect
        if img_h > max_h:
            img_h = max_h
            img_w = img_h / aspect
            
        needed_total = img_h + 24.0 + space_after
        if self.current_y + needed_total > self.content_y_max:
            self.new_page()
            
        img_x = self.margin_x + ((self.content_w - img_w) / 2.0)
        img_rect = fitz.Rect(img_x, self.current_y, img_x + img_w, self.current_y + img_h)
        
        container_rect = fitz.Rect(img_x - 1, self.current_y - 1, img_x + img_w + 1, self.current_y + img_h + 1)
        self.current_page.draw_rect(container_rect, color=self.c_border, fill=self.c_white, width=0.5)
        
        self.current_page.insert_image(img_rect, filename=img_path, keep_proportion=True)
        
        cap_y = self.current_y + img_h + 4.0
        r_cap = fitz.Rect(self.margin_x, cap_y, self.margin_x + self.content_w, cap_y + 16.0)
        self.current_page.insert_textbox(r_cap, caption, fontname=self.f_italic, fontsize=8.2, 
                                         color=self.c_muted, align=fitz.TEXT_ALIGN_CENTER)
        
        self.current_y += needed_total

    def add_two_images_side_by_side(self, img1_path, cap1, img2_path, cap2, max_h=150.0, space_after=10.0):
        needed_total = max_h + 28.0 + space_after
        if self.current_y + needed_total > self.content_y_max:
            self.new_page()
            
        gap = 14.0
        single_w = (self.content_w - gap) / 2.0
        
        x1 = self.margin_x
        rect1 = fitz.Rect(x1, self.current_y, x1 + single_w, self.current_y + max_h)
        self.current_page.draw_rect(fitz.Rect(x1-1, self.current_y-1, x1+single_w+1, self.current_y+max_h+1), 
                                    color=self.c_border, width=0.5)
        if os.path.exists(img1_path):
            self.current_page.insert_image(rect1, filename=img1_path, keep_proportion=True)
        r_cap1 = fitz.Rect(x1, self.current_y + max_h + 4, x1 + single_w, self.current_y + max_h + 20)
        self.current_page.insert_textbox(r_cap1, cap1, fontname=self.f_italic, fontsize=7.8, 
                                         color=self.c_muted, align=fitz.TEXT_ALIGN_CENTER)
        
        x2 = self.margin_x + single_w + gap
        rect2 = fitz.Rect(x2, self.current_y, x2 + single_w, self.current_y + max_h)
        self.current_page.draw_rect(fitz.Rect(x2-1, self.current_y-1, x2+single_w+1, self.current_y+max_h+1), 
                                    color=self.c_border, width=0.5)
        if os.path.exists(img2_path):
            self.current_page.insert_image(rect2, filename=img2_path, keep_proportion=True)
        r_cap2 = fitz.Rect(x2, self.current_y + max_h + 4, x2 + single_w, self.current_y + max_h + 20)
        self.current_page.insert_textbox(r_cap2, cap2, fontname=self.f_italic, fontsize=7.8, 
                                         color=self.c_muted, align=fitz.TEXT_ALIGN_CENTER)
        
        self.current_y += needed_total

    def add_code_block(self, code_text, caption=None, space_after=8.0):
        lines = code_text.strip().split('\n')
        line_h = 10.5
        box_h = len(lines) * line_h + 14.0 + (14.0 if caption else 0)
        
        if self.current_y + box_h > self.content_y_max:
            self.new_page()
            
        box_rect = fitz.Rect(self.margin_x, self.current_y, self.margin_x + self.content_w, self.current_y + box_h)
        self.current_page.draw_rect(box_rect, color=self.c_border, fill=(0.12, 0.14, 0.18), width=0.5)
        
        cur_txt_y = self.current_y + 6
        if caption:
            r_c = fitz.Rect(self.margin_x + 10, cur_txt_y, self.margin_x + self.content_w - 10, cur_txt_y + 12)
            self.current_page.insert_textbox(r_c, caption, fontname=self.f_bold, fontsize=7.8, color=self.c_accent)
            cur_txt_y += 14
            
        r_code = fitz.Rect(self.margin_x + 10, cur_txt_y, self.margin_x + self.content_w - 10, self.current_y + box_h - 4)
        self.current_page.insert_textbox(r_code, code_text.strip(), fontname=self.f_code, fontsize=7.5, 
                                         color=(0.92, 0.94, 0.96), lineheight=1.2)
        
        self.current_y += box_h + space_after

    def render_cover_page(self):
        page = self.new_page()
        
        # Decorative top banner
        banner_rect = fitz.Rect(0, 0, self.page_w, 200)
        page.draw_rect(banner_rect, color=None, fill=self.c_primary)
        
        stripe_rect = fitz.Rect(0, 196, self.page_w, 202)
        page.draw_rect(stripe_rect, color=None, fill=self.c_accent)
        
        r_inst = fitz.Rect(self.margin_x, 45, self.page_w - self.margin_x, 70)
        page.insert_textbox(r_inst, "UNIVERSITAS SILIWANGI\nFAKULTAS TEKNIK — JURUSAN TEKNIK INFORMATIKA", 
                            fontname=self.f_bold, fontsize=10.0, color=(0.85, 0.90, 0.98), align=fitz.TEXT_ALIGN_CENTER)
        
        r_course = fitz.Rect(self.margin_x, 105, self.page_w - self.margin_x, 150)
        page.insert_textbox(r_course, "PRAKTIKUM KRIPTOGRAFI (MODUL 6)\nSTEGANOGRAFI CITRA DIGITAL", 
                            fontname=self.f_bold, fontsize=16.0, color=self.c_white, align=fitz.TEXT_ALIGN_CENTER)
        
        r_main_box = fitz.Rect(self.margin_x, 240, self.page_w - self.margin_x, 380)
        page.draw_rect(r_main_box, color=self.c_border, fill=self.c_bg_light, width=0.8)
        
        r_main_t1 = fitz.Rect(self.margin_x + 16, 255, self.page_w - self.margin_x - 16, 310)
        page.insert_textbox(r_main_t1, "LAPORAN LENGKAP TUGAS PRAKTIKUM", 
                            fontname=self.f_bold, fontsize=14.0, color=self.c_secondary, align=fitz.TEXT_ALIGN_CENTER)
        
        subtitle_text = ("Rekonstruksi & Analisis Komprehensif Algoritma LSB Spatial-Domain:\n"
                         "Perbaikan Bug Baseline, Proteksi Stego-Key Pseudorandom Permutation, "
                         "Evaluasi m-bit Trade-Off (MSE/PSNR), Arsitektur Kripto-Steganografi Berlapis (Defense-in-Depth), "
                         "Ketahanan Format Berkas (BER), dan Steganalisis Visual Pairs of Values (Chi-Square)")
        r_main_t2 = fitz.Rect(self.margin_x + 16, 305, self.page_w - self.margin_x - 16, 370)
        page.insert_textbox(r_main_t2, subtitle_text, 
                            fontname=self.f_reg, fontsize=9.2, color=self.c_text, align=fitz.TEXT_ALIGN_CENTER, lineheight=1.35)
        
        r_auth = fitz.Rect(self.margin_x, 410, self.page_w - self.margin_x, 620)
        page.draw_rect(r_auth, color=self.c_border, fill=self.c_white, width=0.8)
        
        r_auth_title = fitz.Rect(self.margin_x, 425, self.page_w - self.margin_x, 445)
        page.insert_textbox(r_auth_title, "IDENTITAS MAHASISWA & PARAMETER TUGAS", 
                            fontname=self.f_bold, fontsize=11.0, color=self.c_primary, align=fitz.TEXT_ALIGN_CENTER)
        
        auth_data = [
            ("Nama Lengkap", "Diva Prayoga Alpariji Putra"),
            ("Nomor Induk Mahasiswa (NIM)", "237006173"),
            ("Parameter Khusus A (Digit Terakhir NIM)", "A = 3 (Digit satuan dari NIM 237006173)"),
            ("Stego-Key Seed Eksperimen (P2)", "S_correct = 237006173 | S_wrong = 237006174"),
            ("Kunci Kriptografi & Posisi (P4)", "K_pos = 237006173 | K_enc = 987654321 (Stream XOR)"),
            ("Cover Object Primer", "Diva_selfie.jpeg (720x1280 RGB, 2.764.800 Bytes)"),
            ("Metode Validasi Otomatis", "Automated Test Suite (18/18 Unit Test PASS - 100%)"),
            ("Tahun Akademik / Semester", "2026/2027 — Semester Genap")
        ]
        
        cur_y_auth = 460
        for label, val in auth_data:
            r_lbl = fitz.Rect(self.margin_x + 20, cur_y_auth, self.margin_x + 220, cur_y_auth + 16)
            page.insert_textbox(r_lbl, label, fontname=self.f_bold, fontsize=8.6, color=self.c_muted)
            
            r_sep = fitz.Rect(self.margin_x + 222, cur_y_auth, self.margin_x + 230, cur_y_auth + 16)
            page.insert_textbox(r_sep, ":", fontname=self.f_bold, fontsize=8.6, color=self.c_muted)
            
            r_val = fitz.Rect(self.margin_x + 235, cur_y_auth, self.page_w - self.margin_x - 20, cur_y_auth + 16)
            page.insert_textbox(r_val, val, fontname=self.f_reg, fontsize=8.6, color=self.c_text)
            
            cur_y_auth += 18
            
        r_foot = fitz.Rect(self.margin_x, 720, self.page_w - self.margin_x, 790)
        footer_affil = ("PROGRAM STUDI S1 TEKNIK INFORMATIKA\n"
                        "FAKULTAS TEKNIK — UNIVERSITAS SILIWANGI\n"
                        "TASIKMALAYA\n2026")
        page.insert_textbox(r_foot, footer_affil, fontname=self.f_bold, fontsize=9.5, 
                            color=self.c_primary, align=fitz.TEXT_ALIGN_CENTER, lineheight=1.3)

    def render_table_of_contents_page(self):
        self.new_page()
        self.add_chapter_heading("DAFTAR ISI", "STRUKTUR LAPORAN PRAKTIKUM LENGKAP")
        
        self.add_paragraph("Laporan ini disusun secara sistematis mengikuti panduan penulisan akademik dan spesifikasi "
                           "resmi Product Requirements Document (PRD). Seluruh data numerik, grafik, dan tangkapan layar "
                           "merupakan hasil eksekusi empiris nyata pada environment Python.", space_after=12)
        
        toc_entries = [
            ("BAB 1", "PENDAHULUAN", "Latar Belakang Steganografi, Prisoner's Problem, & Domain Spasial"),
            ("BAB 2", "TUJUAN PRAKTIKUM", "Kompetensi Utama Analisis, Perbaikan, & Pengujian Sistemik"),
            ("BAB 3", "LINGKUNGAN DAN PERANGKAT", "Spesifikasi Hardware, Software, & Arsitektur Modul Python"),
            ("BAB 4", "DATASET DAN CITRA COVER", "Spesifikasi Citra Selfie Diva_selfie.jpeg & Karakteristik Payload"),
            ("BAB 5", "FASE P1 — ANALISIS DAN PERBAIKAN PROGRAM SLIDE", "Analisis Bug bin()[2:9], Kanal range(0,2), Delimiter, & Solusi Fixed"),
            ("BAB 6", "FASE P2 — LSB ACAK DENGAN STEGO-KEY", "Permutasi PRNG Deterministik, Uji Kunci, & Analisis Bounding Box Change Map"),
            ("BAB 7", "FASE P3 — EKSPERIMEN m-bit LSB DAN KUALITAS CITRA", "Kapasitas 100%, Teorema Max Diff 2^m-1, Evaluasi MSE & PSNR, Grid Visual"),
            ("BAB 8", "FASE P4 — KOMBINASI KRIPTOGRAFI DAN STEGANOGRAFI", "Defense-in-Depth: Stream Cipher XOR + Random LSB, Evaluasi 3 Skenario"),
            ("BAB 9", "FASE P5 — PENGARUH FORMAT FILE DAN KETAHANAN", "Analisis Bit Error Rate (BER) pada PNG, BMP, & JPEG Lossy DCT Quality 95"),
            ("BAB 10", "BONUS — STEGANALISIS VISUAL DAN UJI CHI-SQUARE", "Ekstraksi Bidang Bit LSB, Batas Garis Baris 640, & Pairs of Values (PoV)"),
            ("BAB 11", "PEMBAHASAN UMUM DAN SINTESIS KEAMANAN", "The Steganographic Triangle, Trade-Off Imperceptibility-Capacity-Robustness"),
            ("BAB 12", "KESIMPULAN", "Rangkuman Temuan Ilmiah dan Rekomendasi Implementasi Praktis"),
            ("BAB 13", "REFERENSI", "Daftar Pustaka Akademik dan Rujukan Standar"),
            ("BAB 14", "LAMPIRAN", "Ringkasan Kode Sumber Modular & Log Validasi Otomatis (18/18 PASS)")
        ]
        
        for bab, title, desc in toc_entries:
            self.check_space(26)
            r_bab = fitz.Rect(self.margin_x, self.current_y, self.margin_x + 60, self.current_y + 14)
            self.current_page.insert_textbox(r_bab, bab, fontname=self.f_bold, fontsize=8.5, color=self.c_secondary)
            
            r_t = fitz.Rect(self.margin_x + 65, self.current_y, self.margin_x + self.content_w, self.current_y + 14)
            self.current_page.insert_textbox(r_t, title, fontname=self.f_bold, fontsize=8.5, color=self.c_primary)
            
            r_d = fitz.Rect(self.margin_x + 65, self.current_y + 12, self.margin_x + self.content_w, self.current_y + 24)
            self.current_page.insert_textbox(r_d, desc, fontname=self.f_italic, fontsize=7.5, color=self.c_muted)
            
            self.current_y += 26
            
        self.add_callout("Catatan Verifikasi: Seluruh proses eksperimen dikontrol oleh master pipeline `src/run_all.py` "
                         "dan telah terverifikasi lulus 100% (18 dari 18 pengujian berhasil).", title="Status Eksekusi", style="success")

    def finalize_document(self):
        total_p = len(self.doc)
        for i in range(1, total_p):  # Skip Cover Page (page 0)
            p = self.doc[i]
            
            # Running Header
            p.draw_line(fitz.Point(self.margin_x, 42), fitz.Point(self.margin_x + self.content_w, 42), 
                        color=self.c_border, width=0.5)
            r_h_left = fitz.Rect(self.margin_x, 28, self.margin_x + 320, 40)
            p.insert_textbox(r_h_left, "PRAKTIKUM KRIPTOGRAFI — MODUL 6: STEGANOGRAFI CITRA DIGITAL", 
                             fontname=self.f_bold, fontsize=7.2, color=self.c_secondary)
            r_h_right = fitz.Rect(self.margin_x + 320, 28, self.margin_x + self.content_w, 40)
            p.insert_textbox(r_h_right, "237006173 — Diva Prayoga Alpariji Putra", 
                             fontname=self.f_reg, fontsize=7.2, color=self.c_muted, align=fitz.TEXT_ALIGN_RIGHT)
            
            # Running Footer
            p.draw_line(fitz.Point(self.margin_x, self.page_h - 40), 
                        fitz.Point(self.margin_x + self.content_w, self.page_h - 40), 
                        color=self.c_border, width=0.5)
            r_f_left = fitz.Rect(self.margin_x, self.page_h - 36, self.margin_x + 350, self.page_h - 24)
            p.insert_textbox(r_f_left, "Jurusan Teknik Informatika — Fakultas Teknik, Universitas Siliwangi", 
                             fontname=self.f_reg, fontsize=7.5, color=self.c_muted)
            r_f_right = fitz.Rect(self.margin_x + 350, self.page_h - 36, self.margin_x + self.content_w, self.page_h - 24)
            p.insert_textbox(r_f_right, f"Halaman {i + 1} dari {total_p}", 
                             fontname=self.f_bold, fontsize=7.5, color=self.c_primary, align=fitz.TEXT_ALIGN_RIGHT)
            
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.doc.save(self.output_path, deflate=True, garbage=4, clean=True)
        print(f"[SUCCESS] Laporan Praktikum berhasil dikompilasi ke: {self.output_path} ({total_p} halaman)")


def build_full_report():
    base_dir = get_base_dir()
    out_pdf = os.path.join(base_dir, "report", "Praktikum", "237006173_Diva_Prayoga_Alpariji_Putra_Praktikum6.pdf")
    
    # Load all empirical results
    with open(os.path.join(base_dir, "results", "p1_baseline_metrics.json"), "r") as f:
        p1_base = json.load(f)
    with open(os.path.join(base_dir, "results", "p1_fixed_metrics.json"), "r") as f:
        p1_fixed = json.load(f)
    with open(os.path.join(base_dir, "results", "p2_metrics.json"), "r") as f:
        p2_data = json.load(f)
    with open(os.path.join(base_dir, "results", "p3_results.json"), "r") as f:
        p3_data = json.load(f)
    with open(os.path.join(base_dir, "results", "p4_results.json"), "r") as f:
        p4_data = json.load(f)
    with open(os.path.join(base_dir, "results", "p5_results.json"), "r") as f:
        p5_data = json.load(f)
    with open(os.path.join(base_dir, "results", "bonus_steganalysis.json"), "r") as f:
        bonus_data = json.load(f)
        
    builder = AcademicReportBuilder(out_pdf)
    
    # -------------------------------------------------------------
    # HALAMAN JUDUL
    # -------------------------------------------------------------
    builder.render_cover_page()
    
    # -------------------------------------------------------------
    # DAFTAR ISI & EKSEKUTIF
    # -------------------------------------------------------------
    builder.render_table_of_contents_page()
    
    # -------------------------------------------------------------
    # BAB 1: PENDAHULUAN
    # -------------------------------------------------------------
    builder.add_chapter_heading("BAB 1", "PENDAHULUAN")
    builder.add_section_heading("1.1 Latar Belakang Ilmiah")
    builder.add_paragraph("Kebutuhan akan pertukaran informasi rahasia telah mendorong perkembangan dua disiplin ilmu keamanan: "
                          "kriptografi dan steganografi. Kriptografi berfokus pada perlindungan kerahasiaan isi pesan (confidentiality "
                          "of content) melalui proses enkripsi yang mengubah plaintext menjadi ciphertext. Meskipun ciphertext "
                          "tidak dapat dibaca tanpa kunci yang sah, bentuk fisiknya yang berupa deretan karakter acak sering kali "
                          "menimbulkan kecurigaan bagi pihak ketiga atau pengawas saluran transmisi.")
    
    builder.add_paragraph("Paradigma 'Prisoner's Problem' yang diperkenalkan oleh Gustavus J. Simmons pada tahun 1983 mengilustrasikan "
                          "kondisi di mana dua pihak (Alice dan Bob) yang berada dalam tahanan ingin menyusun rencana pelarian melalui "
                          "saluran komunikasi yang diawasi ketat oleh sipir (warden bernama Wendy). Jika Wendy mendeteksi pesan yang "
                          "dienkripsi, Wendy akan langsung menyita pesan tersebut dan memutus komunikasi. Di sinilah steganografi "
                          "memegang peranan esensial: steganografi tidak hanya menyembunyikan arti pesan, tetapi menyembunyikan "
                          "fakta keberadaan komunikasi itu sendiri (confidentiality of communication existence).")
    
    builder.add_section_heading("1.2 Domain Spasial dan Teknik Least Significant Bit (LSB)")
    builder.add_paragraph("Dalam steganografi citra digital, domain spasial merujuk pada manipulasi langsung terhadap nilai intensitas "
                          "piksel tanpa melakukan transformasi frekuensi. Setiap piksel citra digital TrueColor 24-bit direpresentasikan "
                          "oleh tiga kanal warna (Red, Green, Blue), dengan masing-masing kanal bernilai 8-bit dalam rentang desimal [0, 255].")
    
    builder.add_paragraph("Teknik Least Significant Bit (LSB) bekerja dengan memanfaatkan redundansi perseptual pada indra penglihatan manusia. "
                          "Bit ke-0 (LSB) hanya memiliki bobot numerik sebesar 2^0 = 1. Pengubahan bit LSB hanya menyebabkan fluktuasi intensitas "
                          "maksimum sebesar 1 unit, yang secara praktis mustahil dibedakan oleh mata manusia (imperceptible). Namun, implementasi "
                          "program dasar LSB sering kali memiliki kelemahan kritis berupa cacat logika biner, utilisasi kanal yang tidak efisien, "
                          "ketiadaan proteksi posisi, dan ketidakmampuan bertahan terhadap kompresi file.")
    
    # -------------------------------------------------------------
    # BAB 2: TUJUAN PRAKTIKUM
    # -------------------------------------------------------------
    builder.add_chapter_heading("BAB 2", "TUJUAN PRAKTIKUM")
    builder.add_paragraph("Praktikum Modul 6 Kriptografi ini bertujuan untuk memberikan pemahaman teoritis mendalam serta "
                          "keterampilan rekayasa praktis dalam perancangan, evaluasi, dan audit keamanan sistem steganografi citra digital. "
                          "Rincian sasaran teknis eksperimen mencakup:", space_after=8)
    
    builder.add_bullet("Analisis dan Rekonstruksi Program Baseline (P1)", 
                       "Mendiagnosis bug string slicing bin()[2:9] pada piksel < 128, mengatasi restriksi kanal range(0,2), "
                       "mengganti delimiter string rawan tabrakan dengan 32-bit length header, serta membuktikan selisih teoritis.")
    builder.add_bullet("Proteksi Posisi dengan Stego-Key (P2)", 
                       "Mengimplementasikan penyisipan LSB acak berbasis permutasi PRNG deterministik (sampling without replacement), "
                       "menguji ketahanan ekstraksi terhadap kunci salah, dan mengevaluasi peta perubahan (change map).")
    builder.add_bullet("Eksperimen Multi-Bit LSB dan Analisis Citra (P3)", 
                       "Mengevaluasi trade-off kapasitas versus imperceptibility pada m in {1, 2, 3, 4} bit LSB dengan kapasitas 100%, "
                       "serta mengukur metrik objektif MSE dan PSNR.")
    builder.add_bullet("Kombinasi Kripto-Steganografi Berlapis (P4)", 
                       "Merancang sistem pertahanan berlapis (Defense-in-Depth) yang mengintegrasikan stream cipher XOR PRNG dan "
                       "penyisipan LSB acak, serta membuktikan perilakunya pada 3 skenario kunci.")
    builder.add_bullet("Evaluasi Ketahanan Format Berkas (P5)", 
                       "Menguji integritas pesan steganografi pada format lossless (PNG, BMP) versus format lossy transform-domain "
                       "(JPEG quality=95), serta mengukur Bit Error Rate (BER).")
    builder.add_bullet("Steganalisis Visual dan Uji Chi-Square (Bonus)", 
                       "Mengekstraksi bidang bit LSB pada muatan 50% kapasitas, menganalisis garis demarkasi visual, dan membuktikan "
                       "kerentanan statistik menggunakan uji Chi-Square Pairs of Values (PoV).")
    
    # -------------------------------------------------------------
    # BAB 3: LINGKUNGAN DAN PERANGKAT
    # -------------------------------------------------------------
    builder.add_chapter_heading("BAB 3", "LINGKUNGAN DAN PERANGKAT")
    builder.add_section_heading("3.1 Spesifikasi Perangkat Keras dan Lunak")
    builder.add_paragraph("Seluruh eksperimen dijalankan pada workstation komputasi dengan spesifikasi terstandarisasi:")
    
    env_headers = ["Komponen", "Spesifikasi / Versi", "Peranan dalam Eksperimen"]
    env_rows = [
        ["Sistem Operasi", "Microsoft Windows 11 Enterprise (64-bit)", "Platform eksekusi utama"],
        ["Bahasa Pemrograman", "Python 3.13.2 (Official 64-bit Build)", "Runtime engine komputasi"],
        ["NumPy", "Versi 2.2.3", "Komputasi matriks n-dimensi & PRNG deterministik"],
        ["Pillow (PIL)", "Versi 11.1.0", "I/O citra digital PNG, BMP, JPEG lossless/lossy"],
        ["PyMuPDF (fitz)", "Versi 1.27.2.3", "Kompilasi layout dokumen akademik PDF"],
        ["Matplotlib", "Versi 3.10.1", "Visualisasi change map biner dan grafik degradasi PSNR"]
    ]
    builder.add_table(env_headers, env_rows, [110.0, 160.0, 217.28], [fitz.TEXT_ALIGN_LEFT, fitz.TEXT_ALIGN_LEFT, fitz.TEXT_ALIGN_LEFT])
    
    builder.add_section_heading("3.2 Arsitektur Modul Kode Sumber")
    builder.add_paragraph("Implementasi perangkat lunak dirancang dengan pola modular pada folder `src/`, memisahkan "
                          "komponen utilitas sentral, modul eksperimen terisolasi, dan pipeline orkestrasi otomatis:")
    
    mod_headers = ["File Modul", "Fungsi Utama", "Output Utama"]
    mod_rows = [
        ["src/common.py", "Konversi biner, validasi I/O, metrik MSE/PSNR/BER", "Fungsi utilitas global"],
        ["src/p1_baseline.py", "Eksekusi kode dasar slide 74-77 & diagnostik bug", "outputs/p1/, p1_baseline_metrics.json"],
        ["src/p1_fixed.py", "Implementasi bitwise 3-kanal & 32-bit header", "outputs/p1/, p1_fixed_metrics.json"],
        ["src/p2_random_lsb.py", "LSB acak permutasi PRNG stego-key NIM", "outputs/p2/, p2_metrics.json"],
        ["src/p3_mbit_lsb.py", "Eksperimen multi-bit m=1..4 kapasitas 100%", "outputs/p3/, p3_results.csv, grafik"],
        ["src/p4_crypto_stego.py", "Integrasi enkripsi stream XOR + LSB acak", "outputs/p4/, p4_results.json"],
        ["src/p5_formats.py", "Pengujian format PNG, BMP, JPEG (quality=95)", "outputs/p5/, p5_ber.csv"],
        ["src/bonus_steganalysis.py", "Ekstraksi bidang bit LSB & Uji Chi-Square PoV", "figures/bonus_lsb_planes.png"],
        ["src/run_all.py", "Master test suite validasi end-to-end (18/18)", "results/pipeline_summary.json"]
    ]
    builder.add_table(mod_headers, mod_rows, [115.0, 210.0, 162.28], [fitz.TEXT_ALIGN_LEFT, fitz.TEXT_ALIGN_LEFT, fitz.TEXT_ALIGN_LEFT])
    
    # -------------------------------------------------------------
    # BAB 4: DATASET DAN CITRA COVER
    # -------------------------------------------------------------
    builder.add_chapter_heading("BAB 4", "DATASET DAN CITRA COVER")
    builder.add_section_heading("4.1 Spesifikasi Citra Cover Mahasiswa")
    builder.add_paragraph("Sesuai instruksi resmi, citra cover yang digunakan adalah foto selfie asli milik mahasiswa bersangkutan. "
                          "Citra master disimpan dalam format JPEG (`assets/Diva_selfie.jpeg`) dan dikonversi ke format lossless PNG "
                          "(`assets/cover_working.png`) sebagai cover kerja utama guna mencegah distorsi kompresi sebelum proses embedding.")
    
    cover_headers = ["Parameter Citra", "Nilai Eksperimen", "Keterangan Teknis"]
    cover_rows = [
        ["Nama Berkas Master", "Diva_selfie.jpeg", "Foto selfie asli mahasiswa Diva Prayoga Alpariji Putra"],
        ["Nama Berkas Kerja", "cover_working.png", "Salinan format lossless PNG tanpa kompresi artefak"],
        ["Dimensi Spasial", "720 piksel (W) x 1280 piksel (H)", "Rasio aspek 9:16 (format potret kamera)"],
        ["Total Piksel", "921.600 piksel", "Lebar dikalikan tinggi citra"],
        ["Kedalaman Warna", "24-bit TrueColor (RGB)", "8-bit Red, 8-bit Green, 8-bit Blue"],
        ["Tipe Data Matriks", "uint8 (rentang [0, 255])", "Representasi array 3D NumPy shape (1280, 720, 3)"],
        ["Total Byte Citra", "2.764.800 byte", "Kapasitas fisik penyimpanan matriks citra mentah"],
        ["Kapasitas 1-bit LSB (3 Kanal)", "2.764.800 bit = 337,50 KB", "1 bit muatan per byte kanal warna"]
    ]
    builder.add_table(cover_headers, cover_rows, [130.0, 155.0, 202.28], [fitz.TEXT_ALIGN_LEFT, fitz.TEXT_ALIGN_LEFT, fitz.TEXT_ALIGN_LEFT])
    
    builder.add_section_heading("4.2 Karakteristik Payload Pesan Rahasia")
    builder.add_paragraph("Pesan rahasia standar yang disisipkan dirancang secara deterministik memuat identitas mahasiswa dan parameter tugas:")
    builder.add_callout('"237006173 - Diva Prayoga Alpariji Putra - Praktikum ini menguji bagaimana pesan dapat disembunyikan '
                        'secara aman tanpa mengubah tampilan citra secara signifikan."', title="Pesan Rahasia Standar (Plaintext)", style="info")
    
    builder.add_paragraph("Karakteristik kuantitatif dari payload standar tersebut adalah:", space_after=4)
    builder.add_bullet("Panjang String Plaintext", "160 karakter teks ASCII/UTF-8.")
    builder.add_bullet("Panjang Bit Payload", "160 byte x 8 bit = 1.280 bit.")
    builder.add_bullet("Header Panjang Metadata", "32-bit unsigned integer (merepresentasikan angka 160).")
    builder.add_bullet("Total Muatan Disisipkan", "32 bit header + 1.280 bit payload = 1.312 bit total (164 byte).")
    builder.add_bullet("Rasio Okupansi Spasial", "1.312 bit / 2.764.800 bit kapasitas = 0,0475% dari total kapasitas citra.")
    
    # -------------------------------------------------------------
    # BAB 5: FASE P1 — ANALISIS DAN PERBAIKAN PROGRAM SLIDE
    # -------------------------------------------------------------
    builder.add_chapter_heading("BAB 5", "FASE P1 — ANALISIS DAN PERBAIKAN PROGRAM")
    builder.add_section_heading("5.1 Analisis Masalah Program Slide 74–77 (Baseline)")
    builder.add_paragraph("Program steganografi dasar yang disajikan pada slide perkuliahan 74–77 memiliki kelemahan arsitektural "
                          "dan bug logika kritis yang menyebabkan distorsi citra parah serta kegagalan integritas data:")
    
    builder.add_subsection_heading("A. Bug Kritis String Slicing bin(val)[2:9]")
    builder.add_paragraph("Fungsi bawaan Python `bin(val)` mengembalikan representasi biner tanpa padding nol di depan (leading zeros). "
                          "Untuk nilai piksel >= 128 (8-bit penuh), string biner diawali prefix '0b' diikuti 8 digit biner (total 10 karakter). "
                          "Operasi `bin(val)[2:9]` mengambil indeks 2 hingga 8 (tepat 7 bit MSB). Namun, jika nilai piksel < 128 (misalnya 127 = '0b1111111'), "
                          "panjang string hanya 9 karakter. Slicing `[2:9]` akan mengambil seluruh 7 bit asli. Ketika bit pesan ('0' atau '1') disambungkan "
                          "ke belakang string, nilai piksel melompat menjadi 254 atau 255. Selisih absolut mencapai 127 hingga 128, yang melanggar "
                          "secara fatal prinsip 1-bit LSB (seharusnya delta_max <= 1).")
    
    synth_headers = ["Piksel Asli", "Biner Asli", "Sliced [2:9]", "Bit Pesan", "Piksel Baru", "Biner Baru", "Selisih (|Δ|)"]
    synth_rows = [
        ["127", "0b1111111 (7b)", "1111111", "'0'", "254", "0b11111110", "127 (ANOMALI)"],
        ["127", "0b1111111 (7b)", "1111111", "'1'", "255", "0b11111111", "128 (ANOMALI)"],
        ["64", "0b1000000 (7b)", "1000000", "'0'", "128", "0b10000000", "64 (ANOMALI)"],
        ["64", "0b1000000 (7b)", "1000000", "'1'", "129", "0b10000001", "65 (ANOMALI)"],
        ["128 (>=128)", "0b10000000 (8b)", "1000000", "'1'", "129", "0b10000001", "1 (Normal)"]
    ]
    builder.add_table(synth_headers, synth_rows, [60.0, 75.0, 70.0, 50.0, 60.0, 80.0, 92.28], 
                      [fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_CENTER, 
                       fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_CENTER])
    
    builder.add_subsection_heading("B. Pembatasan Kanal Warna range(0, 2)")
    builder.add_paragraph("Perulangan pada program slide menggunakan `for q in range(0, 2)`, yang hanya mengakses kanal indeks 0 (Red) "
                          "dan indeks 1 (Green), sama sekali mengabaikan kanal indeks 2 (Blue). Hal ini menyebabkan pemborosan sepertiga "
                          "ruang penyimpanan. Kapasitas aktual hanya 1.843.200 bit (225 KB / 66,67% utilisasi) dari kapasitas teoritis 2.764.800 bit (337,5 KB).")
    
    builder.add_subsection_heading("C. Kerentanan Delimiter String 'stego'")
    builder.add_paragraph("Program slide mencari kemunculan kata penanda 'stego' untuk menghentikan ekstraksi. Pendekatan ini memiliki "
                          "dua kelemahan fatal: (1) false positive early truncation apabila pesan plaintext memuat kata 'stego', dan (2) "
                          "infinite loop overflow apabila delimiter terdistorsi akibat noise transmisi.")
    
    builder.add_section_heading("5.2 Implementasi Program Perbaikan (Fixed)")
    builder.add_paragraph("Untuk mengatasi ketiga kelemahan fundamental di atas, dirancang modul `src/p1_fixed.py` dengan perbaikan arsitektural:")
    builder.add_bullet("Manipulasi Bitwise Murni", "Mengganti konversi string dengan ekspresi `stego_val = (cover_val & ~1) | bit`. "
                                                   "Operasi ini menjamin secara matematis delta_max <= 1 untuk semua nilai piksel [0, 255].")
    builder.add_bullet("Utilisasi Penuh Tiga Kanal", "Mengubah perulangan menjadi `for q in range(0, 3)` untuk memanfaatkan seluruh kanal R, G, B (utilisasi 100%).")
    builder.add_bullet("Header Panjang 32-Bit", "Menyematkan 32-bit unsigned integer di awal aliran bit stego. Ekstraktor membaca tepat 32 bit pertama, "
                                                "mengonversinya menjadi integer panjang byte payload, lalu mengekstrak byte pesan tanpa delimiter string.")
    
    builder.add_section_heading("5.3 Hasil Eksperimen dan Komparasi Kuantitatif")
    p1_headers = ["Parameter Pengujian", "P1 Baseline (Slide)", "P1 Fixed (Perbaikan)", "Keterangan Evaluasi"]
    p1_rows = [
        ["Max Absolute Difference", f"{p1_base['max_diff_test_message']}", f"{p1_fixed['max_diff']}", "Fixed menjamin |Δ| <= 1 matematis"],
        ["Jumlah Byte Berubah", f"{p1_base['changed_bytes']:,} byte", f"{p1_fixed['changed_bytes']:,} byte", "Fixed memodifikasi bit secara presisi"],
        ["Kanal Warna Dipakai", "Red, Green (2 kanal)", "Red, Green, Blue (3 kanal)", "Peningkatan utilisasi 1.5x lipat"],
        ["Kapasitas Teoritis", "1.843.200 bit (225,0 KB)", "2.764.800 bit (337,5 KB)", "Kapasitas penuh 100% citra cover"],
        ["Metode Terminasi", "Delimiter String ('stego')", "Header Panjang (32-bit uint)", "Bebas false positive & truncation"],
        ["Uji Kata 'stego' di Pesan", "Gagal / Terpotong Dini", "Lulus 100% Sempurna", "Fixed membaca payload secara eksak"],
        ["PSNR Citra Stego", f"{p1_base['psnr']:.2f} dB", f"{p1_fixed['psnr']:.2f} dB", "Kualitas imperceptible sempurna"]
    ]
    builder.add_table(p1_headers, p1_rows, [125.0, 115.0, 125.0, 122.28], 
                      [fitz.TEXT_ALIGN_LEFT, fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_LEFT])
    
    builder.add_section_heading("5.4 Dokumentasi Tangkapan Layar Eksekusi P1")
    builder.add_image(os.path.join(base_dir, "screenshots", "p1", "01_baseline_embedding.png"), 
                      "Gambar 5.1 Tangkapan Layar Terminal: Proses Penyisipan Baseline Program Slide 74–77", max_h=110.0)
    builder.add_image(os.path.join(base_dir, "screenshots", "p1", "02_baseline_extraction.png"), 
                      "Gambar 5.2 Tangkapan Layar Terminal: Ekstraksi Baseline Menggunakan Delimiter 'stego'", max_h=95.0)
    builder.add_image(os.path.join(base_dir, "screenshots", "p1", "03_byte_change_metrics.png"), 
                      "Gambar 5.3 Tangkapan Layar Terminal: Bukti Empiris Bug String Slicing Nilai Piksel < 128", max_h=130.0)
    builder.add_image(os.path.join(base_dir, "screenshots", "p1", "04_fixed_embedding.png"), 
                      "Gambar 5.4 Tangkapan Layar Terminal: Penyisipan Fixed Menggunakan Bitwise & Header 32-Bit", max_h=110.0)
    builder.add_image(os.path.join(base_dir, "screenshots", "p1", "05_fixed_extraction.png"), 
                      "Gambar 5.5 Tangkapan Layar Terminal: Ekstraksi Fixed Berhasil 100% Termasuk Uji Kata 'stego'", max_h=105.0)
    
    # -------------------------------------------------------------
    # BAB 6: FASE P2 — LSB ACAK DENGAN STEGO-KEY
    # -------------------------------------------------------------
    builder.add_chapter_heading("BAB 6", "FASE P2 — LSB ACAK DENGAN STEGO-KEY")
    builder.add_section_heading("6.1 Landasan Teori Permutasi Pseudorandom")
    builder.add_paragraph("Penyisipan LSB sekuensial (baris per baris dari sudut kiri atas) menciptakan kelemahan struktural yang nyata: "
                          "modifikasi piksel terkonsentrasi secara lokal pada area awal citra, sehingga sangat mudah diidentifikasi "
                          "oleh analis stego. Untuk mengatasinya, digunakan stego-key berbasis PRNG deterministik.")
    
    builder.add_paragraph("Generator bilangan acak semu `np.random.default_rng(seed)` digunakan untuk menghasilkan urutan permutasi posisi "
                          "byte citra tanpa pengembalian (sampling without replacement): `permutation = rng.permutation(total_available_bytes)`. "
                          "Pendekatan permutasi menjamin secara matematis tidak terjadi tabrakan (zero collision), di mana setiap lokasi byte "
                          "dikunjungi tepat satu kali.")
    
    builder.add_section_heading("6.2 Evaluasi Dua Skenario Kunci (Seed Benar vs Seed Salah)")
    builder.add_paragraph("Sesuai spesifikasi NIM 237006173, dilakukan pengujian ekstraksi terhadap dua kondisi:")
    builder.add_bullet("Skenario 1 (Kunci Benar: Seed = 237006173)", 
                       "Generator PRNG merekonstruksi permutasi koordinat yang persis identik dengan saat penyisipan. "
                       "Header 32-bit terbaca tepat 160 byte payload, dan pesan berhasil dipulihkan secara bit-exact (100% cocok).")
    builder.add_bullet("Skenario 2 (Kunci Salah: Seed = 237006174)", 
                       "Generator menghasilkan urutan permutasi acak yang berbeda total. 32 bit pertama menghasilkan nilai integer acak "
                       f"1.486.381.633 byte (jauh melampaui kapasitas citra {p1_fixed['total_bytes']:,} byte). Ekstraksi gagal total dan "
                       "hanya menghasilkan karakter rusak (gibberish/corrupted).")
    
    builder.add_section_heading("6.3 Analisis Komparasi Peta Perubahan (Change Map)")
    builder.add_paragraph("Peta perubahan biner dibentuk dengan memberikan intensitas putih (255) pada piksel yang nilainya berubah "
                          "dan hitam (0) pada piksel yang tidak berubah. Perbandingan karakteristik spasial disajikan pada tabel berikut:")
    
    cmap_headers = ["Karakteristik", "Sekuensial", "Random (Stego-Key)", "Analisis Komparasi"]
    cmap_rows = [
        ["Jumlah Piksel Berubah", f"{p2_data['change_map_analysis']['changed_pixels_seq']} piksel", f"{p2_data['change_map_analysis']['changed_pixels_rand']} piksel", "Proporsi perubahan mendekati 50% bit"],
        ["Koordinat Y (Tinggi)", "y in [0, 0] (Baris 0)", "y in [2, 1279] (Hampir seluruh tinggi)", "Sekuensial terlokalisir pada 1 baris"],
        ["Koordinat X (Lebar)", "x in [0, 437] (Kolom 0..437)", "x in [1, 719] (Seluruh rentang lebar)", "Acak tersebar di seluruh area citra"],
        ["Dimensi Bounding Box", "1 px (Tinggi) x 438 px (Lebar)", "1278 px (Tinggi) x 719 px (Lebar)", "Penyebaran acak mencakup 99,8% citra"],
        ["Kepadatan Kluster", "Sangat Padat (Lokal Baris 0)", "Sangat Rendah (Tersebar Rata)", "Mengeliminasi pola kluster terpusat"],
        ["Kerentanan Spasial", "Tinggi (Mudah Dideteksi)", "Rendah (Menyerupai Derau Sensor)", "Mengaburkan batas area embedding"]
    ]
    builder.add_table(cmap_headers, cmap_rows, [105.0, 105.0, 115.0, 162.28], 
                      [fitz.TEXT_ALIGN_LEFT, fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_LEFT])
    
    builder.add_callout("Catatan Analisis Ilmiah: Walaupun penyisipan acak berhasil menghilangkan pola kluster spasial yang mencolok, "
                        "hal ini tidak berarti bahwa citra otomatis kebal terhadap teknik steganalisis statistik makro (seperti uji histogram Chi-Square). "
                        "Penyebaran acak hanya menyulitkan rekonstruksi payload tanpa kunci yang sah.", title="Batasan Keamanan", style="info")
    
    builder.add_section_heading("6.4 Dokumentasi Visual dan Tangkapan Layar P2")
    builder.add_image(os.path.join(base_dir, "figures", "p2_change_map_comparison.png"), 
                      "Gambar 6.1 Komparasi Change Map Biner: Sekuensial (Terkonsentrasi Baris 0) vs Random Permutasi (Tersebar Merata)", max_h=190.0)
    builder.add_image(os.path.join(base_dir, "screenshots", "p2", "01_correct_seed_extraction.png"), 
                      "Gambar 6.2 Tangkapan Layar Terminal: Ekstraksi LSB Acak Berhasil Menggunakan Kunci Sah (Seed = 237006173)", max_h=105.0)
    builder.add_image(os.path.join(base_dir, "screenshots", "p2", "02_wrong_seed_extraction.png"), 
                      "Gambar 6.3 Tangkapan Layar Terminal: Ekstraksi Menggunakan Kunci Salah (Seed = 237006174) Gagal Total", max_h=120.0)
    
    # -------------------------------------------------------------
    # BAB 7: FASE P3 — EKSPERIMEN m-bit LSB DAN KUALITAS CITRA
    # -------------------------------------------------------------
    builder.add_chapter_heading("BAB 7", "FASE P3 — EKSPERIMEN m-bit LSB DAN KUALITAS")
    builder.add_section_heading("7.1 Teori Multi-Bit LSB Embedding dan Formulasi Matematika")
    builder.add_paragraph("Teknik multi-bit LSB menyisipkan m bit pesan (m in {1, 2, 3, 4}) ke dalam bit-bit terendah setiap byte piksel. "
                          "Operasi modulasi bitwise dirumuskan sebagai: `stego_byte = (cover_byte & ~((1 << m) - 1)) | chunk_m_bit`.")
    
    builder.add_paragraph("Pembuktian Batas Perubahan Maksimum: Karena potongan pesan chunk_m_bit memiliki nilai dalam rentang desimal [0, 2^m - 1], "
                          "dan bit-bit LSB asli sebelum diganti juga bernilai [0, 2^m - 1], maka selisih absolut maksimum yang dapat terjadi pada satu byte adalah:")
    builder.add_callout("Δ_max = 2^m - 1   --->   m=1: Δ=1 | m=2: Δ=3 | m=3: Δ=7 | m=4: Δ=15", title="Teorema Selisih Maksimum m-bit", style="info")
    
    builder.add_paragraph("Metrik Kualitas Citra: Evaluasi distorsi dihitung menggunakan Mean Squared Error (MSE) dan Peak Signal-to-Noise Ratio (PSNR):")
    builder.add_paragraph("• MSE = (1 / 3MN) * sum_{c=0}^2 sum_{y=0}^{M-1} sum_{x=0}^{N-1} [I_cover(x, y, c) - I_stego(x, y, c)]^2\n"
                          "• PSNR = 10 * log10 (255^2 / MSE) [dB]")
    
    builder.add_section_heading("7.2 Hasil Empiris Eksperimen Kapasitas Penuh (100%)")
    builder.add_paragraph("Setiap variasi nilai m diuji pada muatan kapasitas maksimum (100% utilisasi ruang yang tersedia). "
                          "Seluruh metrik dihitung secara empiris dari citra cover dan citra stego hasil generasi:")
    
    p3_headers = ["m-bit", "Kapasitas", "Δ_teori", "Δ_aktual", "Byte Berubah", "Rasio (%)", "MSE", "PSNR (dB)"]
    p3_rows = []
    for item in p3_data:
        p3_rows.append([
            f"m = {item['m']}",
            f"{item['Capacity_KB']:.1f} KB",
            f"{item['Max_Diff_Theory']}",
            f"{item['Max_Diff_Actual']}",
            f"{item['Changed_Bytes']:,}",
            f"{item['Change_Ratio_Pct']:.2f}%",
            f"{item['MSE']:.4f}",
            f"{item['PSNR_dB']:.2f} dB"
        ])
    builder.add_table(p3_headers, p3_rows, [45.0, 65.0, 48.0, 48.0, 75.0, 55.0, 52.0, 99.28], 
                      [fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_RIGHT, fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_CENTER, 
                       fitz.TEXT_ALIGN_RIGHT, fitz.TEXT_ALIGN_RIGHT, fitz.TEXT_ALIGN_RIGHT, fitz.TEXT_ALIGN_RIGHT])
    
    builder.add_section_heading("7.3 Analisis Trade-Off Kapasitas vs Kualitas Visual")
    builder.add_paragraph("Data empiris menunjukkan kurva trade-off yang sangat konsisten antara kapasitas dan distorsi:")
    builder.add_bullet("m = 1 bit (Kapasitas 337,5 KB, PSNR 51,14 dB)", 
                       "Kualitas visual sempurna tanpa distorsi yang dapat dideteksi mata manusia. "
                       "Nilai PSNR melampaui standar emas citra berkualitas tinggi (> 40 dB).")
    builder.add_bullet("m = 2 bit (Kapasitas 675,0 KB, PSNR 44,14 dB)", 
                       "Kapasitas muatan berlipat ganda menjadi 675 KB. PSNR tetap berada di atas 40 dB, "
                       "sehingga citra masih dikategorikan imperceptible secara visual.")
    builder.add_bullet("m = 3 bit (Kapasitas 1.012,5 KB, PSNR 37,88 dB)", 
                       "PSNR turun di bawah 40 dB. Mulai muncul noise halus berupa bintik-bintik mikro "
                       "pada area gradasi warna lembut (seperti area kulit dan latar belakang terang).")
    builder.add_bullet("m = 4 bit (Kapasitas 1.350,0 KB, PSNR 31,97 dB)", 
                       "Distorsi visual sangat nyata. Fluktuasi nilai piksel hingga delta = 15 menghasilkan "
                       "artefak false contouring, grain noise yang kasar, dan pergeseran saturasi warna.")
    
    builder.add_section_heading("7.4 Dokumentasi Visual dan Grafik Degradasi P3")
    builder.add_image(os.path.join(base_dir, "figures", "p3_psnr_vs_m.png"), 
                      "Gambar 7.1 Grafik Penurunan PSNR (dB) dan Kenaikan Kapasitas (KB) terhadap Jumlah Bit LSB (m = 1 s.d. 4)", max_h=180.0)
    builder.add_image(os.path.join(base_dir, "figures", "p3_stego_grid.png"), 
                      "Gambar 7.2 Grid Komparasi Citra Stego: Cover Asli vs m=1 (51.14 dB), m=2 (44.14 dB), m=3 (37.88 dB), m=4 (31.97 dB)", max_h=190.0)
    builder.add_image(os.path.join(base_dir, "screenshots", "p3", "05_results_table.png"), 
                      "Gambar 7.3 Tangkapan Layar Terminal: Rekapitulasi Metrik MSE dan PSNR untuk Seluruh Nilai m", max_h=120.0)
    
    # -------------------------------------------------------------
    # BAB 8: FASE P4 — KOMBINASI KRIPTOGRAFI DAN STEGANOGRAFI
    # -------------------------------------------------------------
    builder.add_chapter_heading("BAB 8", "FASE P4 — KOMBINASI KRIPTO-STEGANOGRAFI")
    builder.add_section_heading("8.1 Arsitektur Pertahanan Berlapis (Defense-in-Depth)")
    builder.add_paragraph("Kelemahan mendasar dari steganografi murni adalah tidak adanya proteksi kerahasiaan isi: jika lawan berhasil "
                          "mendeteksi dan mengekstrak bit-bit payload, isi pesan plaintext langsung terbongkar. Sebaliknya, kriptografi murni "
                          "menghasilkan ciphertext yang menarik perhatian pengawas komunikasi.")
    
    builder.add_paragraph("Sistem Kripto-Steganografi mengintegrasikan kedua teknik ke dalam arsitektur dua lapis (Defense-in-Depth):")
    builder.add_callout("Plaintext ---> [Enkripsi Stream Cipher XOR (K_enc)] ---> Ciphertext ---> [LSB Acak Permutasi (K_pos)] ---> Stego-Image", 
                        title="Alur Pemrosesan Dua Lapis", style="info")
    
    builder.add_paragraph("Sistem menggunakan dua kunci independen: (1) K_encryption = 987654321 untuk membangkitkan keystream XOR pseudorandom, "
                          "dan (2) K_position = 237006173 (NIM) untuk membangkitkan permutasi koordinat spasial penyisipan.")
    
    builder.add_section_heading("8.2 Pengujian dan Pembuktian Tiga Skenario Kunci")
    p4_headers = ["Skenario Pengujian", "K_position", "K_encryption", "Status Ekstraksi", "Integritas Plaintext", "Hasil Observasi"]
    p4_rows = [
        ["Skenario A", "Benar (237006173)", "Benar (987654321)", "SUKSES", "100% Identik", "Payload dan plaintext dipulihkan sempurna"],
        ["Skenario B", "Benar (237006173)", "Salah (987654322)", "CIPHERTEXT DAPAT", "0% (Gibberish)", "Ciphertext utuh, dekripsi menghasilkan derau acak"],
        ["Skenario C", "Salah (237006174)", "Benar / Sembarang", "GAGAL TOTAL", "0% (Header Rusak)", "Header invalid (1.486.381.633 byte), proses terhenti"]
    ]
    builder.add_table(p4_headers, p4_rows, [70.0, 85.0, 85.0, 80.0, 75.0, 92.28], 
                      [fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_CENTER, 
                       fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_LEFT])
    
    builder.add_subsection_heading("Analisis Perilaku Keamanan:")
    builder.add_bullet("Bukti Kerahasiaan (Skenario B)", 
                       "Meskipun pihak ketiga mengetahui algoritma dan menemukan kunci posisi (stego-key), "
                       "pihak tersebut hanya memperoleh ciphertext pseudorandom. Ketiadaan K_encryption mencegah "
                       "rekonstruksi informasi rahasia. Prinsip Kerckhoffs terpenuhi.")
    builder.add_bullet("Bukti Ketidaktampakan Eksistensi (Skenario C)", 
                       "Jika pihak ketiga mencoba mengekstrak tanpa kunci posisi yang benar, pembacaan bit menghasilkan "
                       "header panjang acak yang tidak valid. Pihak ketiga bahkan tidak dapat memastikan apakah citra "
                       "tersebut memuat pesan rahasia atau sekadar citra biasa.")
    
    builder.add_section_heading("8.3 Dokumentasi Tangkapan Layar Eksekusi P4")
    builder.add_image(os.path.join(base_dir, "screenshots", "p4", "01_scenario_a_both_correct.png"), 
                      "Gambar 8.1 Tangkapan Layar Terminal: Skenario A (Kedua Kunci Benar) — Dekripsi Plaintext Berhasil 100%", max_h=110.0)
    builder.add_image(os.path.join(base_dir, "screenshots", "p4", "02_scenario_b_wrong_encryption.png"), 
                      "Gambar 8.2 Tangkapan Layar Terminal: Skenario B (Kunci Enkripsi Salah) — Ciphertext Ditemukan namun Dekripsi Gagal", max_h=120.0)
    builder.add_image(os.path.join(base_dir, "screenshots", "p4", "03_scenario_c_wrong_position.png"), 
                      "Gambar 8.3 Tangkapan Layar Terminal: Skenario C (Kunci Posisi Salah) — Header Invalid & Ekstraksi Gagal Total", max_h=120.0)
    
    # -------------------------------------------------------------
    # BAB 9: FASE P5 — PENGARUH FORMAT FILE DAN KETAHANAN
    # -------------------------------------------------------------
    builder.add_chapter_heading("BAB 9", "FASE P5 — PENGARUH FORMAT FILE")
    builder.add_section_heading("9.1 Metodologi Pengujian dan Pengukuran BER")
    builder.add_paragraph("Citra stego yang memuat payload 1.312 bit disimpan ke dalam tiga wadah format berkas citra digital yang berbeda: "
                          "PNG (Portable Network Graphics), BMP (Bitmap), dan JPEG (Joint Photographic Experts Group) dengan parameter quality=95. "
                          "Setiap berkas kemudian dibaca ulang untuk mengekstrak bit dan mengukur Bit Error Rate (BER):")
    builder.add_callout("BER = (Jumlah Bit Eror / Total Bit Disisipkan) x 100%", title="Formula Bit Error Rate (BER)", style="info")
    
    builder.add_section_heading("9.2 Data Empiris Hasil Ekstraksi Berkas")
    p5_headers = ["Format Berkas", "Kompresi / Quality", "Ukuran File", "Bit Error", "Total Bit", "BER (%)", "Status Ekstraksi Teks"]
    p5_rows = [
        ["PNG", "Lossless Deflate", f"{p5_data['PNG']['file_size_bytes'] / 1024.0:.1f} KB", 
         f"{p5_data['PNG']['bit_errors']}", f"{p5_data['PNG']['total_bits']}", f"{p5_data['PNG']['ber_percent']:.2f}%", "Terekstrak Sempurna (100%)"],
        ["BMP", "Uncompressed Raw", f"{p5_data['BMP']['file_size_bytes'] / 1024.0:.1f} KB", 
         f"{p5_data['BMP']['bit_errors']}", f"{p5_data['BMP']['total_bits']}", f"{p5_data['BMP']['ber_percent']:.2f}%", "Terekstrak Sempurna (100%)"],
        ["JPEG", "Lossy DCT (q=95)", f"{p5_data['JPEG']['file_size_bytes'] / 1024.0:.1f} KB", 
         f"{p5_data['JPEG']['bit_errors']}", f"{p5_data['JPEG']['total_bits']}", f"{p5_data['JPEG']['ber_percent']:.2f}%", "Teks Terkorupsi Total (Gagal)"]
    ]
    builder.add_table(p5_headers, p5_rows, [60.0, 85.0, 65.0, 50.0, 50.0, 50.0, 127.28], 
                      [fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_RIGHT, 
                       fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_LEFT])
    
    builder.add_section_heading("9.3 Analisis Teori: Domain Spasial vs Domain Transformasi")
    builder.add_paragraph("Hasil eksperimen menunjukkan perbedaan kontras: format PNG dan BMP menghasilkan BER 0,00%, "
                          "sedangkan format JPEG menghasilkan BER 48,02% (630 bit eror dari 1.312 bit) yang menghancurkan seluruh pesan. "
                          "Penyebab ilmiah di balik fenomena ini adalah:")
    
    builder.add_subsection_heading("A. Mekanisme Kompresi Lossless (PNG & BMP)")
    builder.add_paragraph("Format PNG menggunakan algoritma Deflate (kombinasi LZ77 dan Huffman coding) yang hanya memadatkan representasi biner "
                          "tanpa pernah mengubah satu pun nilai intensitas piksel. Format BMP menyimpan data matriks piksel mentah tanpa kompresi sama sekali. "
                          "Oleh karena itu, seluruh bit LSB yang disisipkan pada domain spasial tetap terpelihara secara bit-exact.")
    
    builder.add_subsection_heading("B. Mekanisme Transform-Domain Lossy JPEG")
    builder.add_paragraph("Format JPEG bekerja dengan tahapan: (1) konversi ruang warna ke YCbCr dan subsampling chrominance, "
                          "(2) partisi citra ke dalam blok 8x8 piksel, (3) transformasi Discrete Cosine Transform (DCT) dari domain spasial ke domain frekuensi, "
                          "(4) kuantisasi koefisien frekuensi tinggi menggunakan tabel kuantisasi lossy, dan (5) rekonstruksi melalui Inverse DCT (IDCT).")
    
    builder.add_paragraph("Proses kuantisasi frekuensi tinggi memotong presisi desimal secara permanen. Ketika blok 8x8 direkonstruksi kembali "
                          "ke intensitas spasial melalui IDCT, terjadi pembulatan floating-point yang mengubah nilai intensitas piksel sebesar "
                          "+-1 hingga +-5 unit. Karena informasi steganografi LSB hanya bertumpu pada bit ke-0 (bobot 1), fluktuasi intensitas "
                          "ini membalikkan (flip) nilai bit LSB secara masif, merusak header 32-bit (menghasilkan angka semu 2.453.070.957 byte), "
                          "dan membuat pesan tidak dapat dipulihkan.")
    
    builder.add_section_heading("9.4 Dokumentasi Tangkapan Layar Eksekusi P5")
    builder.add_image(os.path.join(base_dir, "screenshots", "p5", "01_png_extraction.png"), 
                      "Gambar 9.1 Tangkapan Layar Terminal: Ekstraksi Format PNG Berhasil 100% dengan BER 0.00%", max_h=100.0)
    builder.add_image(os.path.join(base_dir, "screenshots", "p5", "02_bmp_extraction.png"), 
                      "Gambar 9.2 Tangkapan Layar Terminal: Ekstraksi Format BMP Berhasil 100% dengan BER 0.00%", max_h=100.0)
    builder.add_image(os.path.join(base_dir, "screenshots", "p5", "03_jpeg_extraction.png"), 
                      "Gambar 9.3 Tangkapan Layar Terminal: Ekstraksi Format JPEG (Quality 95) Mengalami Kegagalan dengan BER 48.02%", max_h=115.0)
    builder.add_image(os.path.join(base_dir, "screenshots", "p5", "04_ber_table.png"), 
                      "Gambar 9.4 Tangkapan Layar Terminal: Rekapitulasi Tabel Komparasi Bit Error Rate (BER) Antar-Format", max_h=110.0)
    
    # -------------------------------------------------------------
    # BAB 10: BONUS — STEGANALISIS VISUAL DAN UJI CHI-SQUARE
    # -------------------------------------------------------------
    builder.add_chapter_heading("BAB 10", "BONUS — STEGANALISIS VISUAL DAN CHI-SQUARE")
    builder.add_section_heading("10.1 Metodologi Ekstraksi Bidang Bit LSB (LSB Plane)")
    builder.add_paragraph("Steganalisis visual dilakukan dengan mengisolasi bidang bit LSB dari seluruh kanal citra: "
                          "`lsb_plane = (image & 1) * 255`. Untuk menguji sensitivitas deteksi, disisipkan payload sebesar "
                          "50% dari kapasitas maksimum citra (1.382.400 bit) secara sekuensial. Payload ini mengisi tepat 640 baris "
                          "teratas citra (y in [0, 639]), sedangkan 640 baris terbawah (y in [640, 1279]) dibiarkan sebagai cover asli.")
    
    builder.add_section_heading("10.2 Analisis Inspeksi Visual Bidang Bit")
    builder.add_paragraph("Pada citra stego berwarna normal (RGB), perubahan sama sekali tidak tampak oleh mata manusia (PSNR mencapai 54,14 dB). "
                          "Namun, pada visualisasi bidang bit LSB, terlihat anomali visual yang sangat mencolok:")
    builder.add_bullet("Garis Batas Horizontal (Demarcation Line)", 
                       "Terlihat garis batas horizontal yang sangat tajam dan kontras tepat pada baris y = 640.")
    builder.add_bullet("Area Terisi Payload (y in [0, 639])", 
                       "Menampilkan pola derau putih acak seragam (uniform random pseudo-noise) tanpa struktur, "
                       "akibat penggantian LSB dengan bit payload acak independen.")
    builder.add_bullet("Area Alami Citra Cover (y in [640, 1279])", 
                       "Memperlihatkan siluet kontur alami wajah, rambut, dan latar belakang, "
                       "karena pada citra alami bit LSB masih memiliki korelasi spasial lokal dengan piksel tetangga.")
    
    builder.add_section_heading("10.3 Pembuktian Statistik: Teori Pairs of Values (PoV) dan Chi-Square")
    builder.add_paragraph("Inspeksi visual membuktikan adanya penyisipan, namun sistem otomatis membutuhkan deteksi statistik matematis. "
                          "Steganalisis statistik Pairs of Values (PoV) yang dirumuskan oleh Westfeld & Pfitzmann (1999) mengevaluasi "
                          "pasangan nilai intensitas piksel berdekatan (2k, 2k+1):")
    
    builder.add_paragraph("Pada citra alami, frekuensi kemunculan nilai genap 2k dan nilai ganjil 2k+1 bervariasi bergantung pada tekstur. "
                          "Namun, ketika bit LSB digantikan oleh bit acak dengan probabilitas 0 dan 1 yang seimbang (50%), frekuensi pasangan "
                          "tersebut dipaksa menjadi sama rata: h*(2k) = h*(2k+1) = (h(2k) + h(2k+1)) / 2.")
    
    builder.add_paragraph("Uji Chi-Square (χ^2) mengukur penyimpangan frekuensi observasi terhadap nilai rata-rata pasangan:")
    builder.add_callout("χ^2 = sum_{k=0}^{127} [h(2k) - h*(2k)]^2 / h*(2k)", title="Rumus Statistik Chi-Square PoV", style="info")
    
    chi_headers = ["Wilayah Citra", "Cover Asli (χ²)", "Stego 50% (χ²)", "Perubahan", "Interpretasi Statistik"]
    chi_rows = [
        ["Separuh Atas (y in [0, 639])", f"{bonus_data['chi_square_pov']['top_half_cover_chi2']:,.2f}", 
         f"{bonus_data['chi_square_pov']['top_half_stego_chi2']:,.2f}", f"Anjlok -{bonus_data['chi_square_pov']['top_half_chi2_drop_pct']:.2f}%", 
         "Penyisipan LSB meratakan pasangan (2k, 2k+1)"],
        ["Separuh Bawah (y in [640, 1279])", f"{bonus_data['chi_square_pov']['bottom_half_cover_chi2']:,.2f}", 
         f"{bonus_data['chi_square_pov']['bottom_half_stego_chi2']:,.2f}", "0.00% (Identik)", 
         "Korelasi alami pasangan piksel tetap terjaga"]
    ]
    builder.add_table(chi_headers, chi_rows, [115.0, 80.0, 80.0, 70.0, 142.28], 
                      [fitz.TEXT_ALIGN_LEFT, fitz.TEXT_ALIGN_RIGHT, fitz.TEXT_ALIGN_RIGHT, fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_LEFT])
    
    builder.add_callout("Kesimpulan Ilmiah Fundamental: Ketiadaan perubahan kasat mata pada inspeksi visual TIDAK menjamin keamanan steganografi! "
                        "Nilai Chi-Square pada separuh atas yang anjlok 97,60% (dari 3.758,10 ke 90,20) membuktikan bahwa algoritma LSB sekuensial "
                        "sangat rentan terhadap deteksi otomatis melalui analisis distribusi frekuensi pasangan nilai.", 
                        title="Temuan Kunci Steganalisis", style="alert")
    
    builder.add_section_heading("10.4 Dokumentasi Gambar Steganalisis LSB")
    builder.add_image(os.path.join(base_dir, "figures", "bonus_lsb_planes.png"), 
                      "Gambar 10.1 Visualisasi Bidang Bit LSB: Perbandingan Cover Asli vs Stego 50% Kapasitas Menampilkan Garis Batas Baris 640", max_h=220.0)
    
    # -------------------------------------------------------------
    # BAB 11: PEMBAHASAN UMUM DAN SINTESIS
    # -------------------------------------------------------------
    builder.add_chapter_heading("BAB 11", "PEMBAHASAN UMUM DAN SINTESIS")
    builder.add_section_heading("11.1 The Steganographic Triangle (Segitiga Steganografi)")
    builder.add_paragraph("Seluruh rangkaian eksperimen P1 hingga P5 dan Bonus mengonfirmasi hukum kompromi fundamental dalam steganografi, "
                          "yaitu Segitiga Steganografi yang menghubungkan tiga parameter saling bertentangan:")
    
    builder.add_bullet("Imperceptibility (Kualitas Visual)", 
                       "Kemampuan stego-image untuk menyerupai citra cover tanpa distorsi yang kasat mata. "
                       "Tercapai optimal pada m = 1 (PSNR 51,14 dB), namun menurun drastis pada m = 4 (PSNR 31,97 dB).")
    builder.add_bullet("Payload Capacity (Kapasitas Muatan)", 
                       "Volume data rahasia yang dapat disematkan. Peningkatan m dari 1 ke 4 melipatgandakan kapasitas dari 337,5 KB "
                       "menjadi 1.350,0 KB, namun mengorbankan kualitas visual secara signifikan.")
    builder.add_bullet("Robustness (Ketahanan Terhadap Gangguan)", 
                       "Ketahanan informasi steganografi terhadap manipulasi media. Eksperimen P5 membuktikan bahwa steganografi LSB "
                       "domain spasial memiliki ketahanan nol (fragile) terhadap kompresi lossy transform-domain JPEG (BER 48,02%).")
    
    builder.add_section_heading("11.2 Matriks Komparasi Algoritma")
    comp_headers = ["Metode / Arsitektur", "Kapasitas (KB)", "PSNR (dB)", "Proteksi Posisi", "Kerahasiaan Isi", "Ketahanan JPEG"]
    comp_rows = [
        ["Baseline (Slide 74-77)", "225.0 KB (2 Kanal)", "84.25 dB*", "Tidak (Sekuensial)", "Plaintext Terbuka", "Rentan (Hancur)"],
        ["Fixed 1-bit LSB (P1)", "337.5 KB (3 Kanal)", "84.42 dB*", "Tidak (Sekuensial)", "Plaintext Terbuka", "Rentan (Hancur)"],
        ["Random LSB Key (P2)", "337.5 KB (3 Kanal)", "84.38 dB*", "Ya (PRNG Permutasi)", "Plaintext Terbuka", "Rentan (Hancur)"],
        ["Multi-Bit m=4 LSB (P3)", "1.350.0 KB (Kapasitas 4x)", "31.97 dB", "Tidak (Sekuensial)", "Plaintext Terbuka", "Rentan (Hancur)"],
        ["Crypto-Stego 2-Key (P4)", "337.5 KB (3 Kanal)", "84.46 dB*", "Ya (K_pos)", "Ya (XOR Ciphertext)", "Rentan (Hancur)"]
    ]
    builder.add_table(comp_headers, comp_rows, [110.0, 75.0, 60.0, 85.0, 85.0, 72.28], 
                      [fitz.TEXT_ALIGN_LEFT, fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_CENTER, 
                       fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_CENTER])
    builder.add_paragraph("*) Catatan: Nilai PSNR > 80 dB terjadi pada muatan payload standar (1.312 bit) yang hanya mengisi 0,0475% kapasitas citra.", 
                          fontsize=8.0, color=builder.c_muted)
    
    # -------------------------------------------------------------
    # BAB 12: KESIMPULAN
    # -------------------------------------------------------------
    builder.add_chapter_heading("BAB 12", "KESIMPULAN")
    builder.add_paragraph("Berdasarkan seluruh hasil analisis teoritis dan eksperimen empiris yang telah dilakukan, dapat ditarik beberapa kesimpulan kunci:")
    
    builder.add_bullet("1. Perbaikan Bug Program Baseline", 
                       "Program baseline slide 74–77 terbukti memiliki cacat logika string slicing bin()[2:9] yang menyebabkan lonjakan "
                       "nilai piksel hingga delta = 128 pada piksel < 128. Implementasi modul fixed berhasil mengeliminasi bug melalui "
                       "operasi bitwise murni (menjamin |Δ| <= 1), memanfaatkan seluruh kanal RGB (kapasitas 337,5 KB / 100%), dan "
                       "menggantikan delimiter string dengan 32-bit length header.")
    
    builder.add_bullet("2. Keunggulan Stego-Key Pseudorandom", 
                       "Penyisipan LSB acak berbasis permutasi PRNG deterministik (NIM 237006173) berhasil menyebarkan perubahan secara "
                       "merata di seluruh dimensi citra (bounding box 1278x719 piksel), mengeliminasi kluster spasial sekuensial yang mudah terdeteksi. "
                       "Uji kunci salah membuktikan kegagalan ekstraksi struktural total.")
    
    builder.add_bullet("3. Validasi Hukum Kompromi Multi-Bit LSB", 
                       "Eksperimen m in {1, 2, 3, 4} membuktikan rumus teoritis selisih maksimum Δ_max = 2^m - 1. Nilai m = 1 dan m = 2 "
                       "memberikan kualitas imperceptible (PSNR > 40 dB), sedangkan m = 4 menimbulkan distorsi visual nyata (PSNR 31,97 dB).")
    
    builder.add_bullet("4. Efektivitas Pertahanan Berlapis (Defense-in-Depth)", 
                       "Kombinasi stream cipher XOR PRNG dan LSB acak terbukti tangguh pada tiga skenario kunci. Kegagalan kunci enkripsi "
                       "hanya mengungkap ciphertext tanpa membuka plaintext, sedangkan kegagalan kunci posisi mencegah akses ke payload.")
    
    builder.add_bullet("5. Kerentanan Terhadap Kompresi Transform-Domain", 
                       "Format PNG dan BMP mempertahankan integritas bit dengan BER 0,00%, sedangkan format JPEG quality=95 merusak "
                       "48,02% bit akibat kuantisasi koefisien frekuensi tinggi pada DCT blok 8x8.")
    
    builder.add_bullet("6. Bukti Empiris Steganalisis Chi-Square", 
                       "Inspeksi bidang bit LSB mengungkap garis batas tajam pada baris 640. Uji Chi-Square PoV membuktikan bahwa penyisipan LSB "
                       "meratakan frekuensi pasangan nilai (2k, 2k+1) sehingga nilai Chi-Square anjlok 97,60%, membuktikan kerentanan statistik LSB.")
    
    # -------------------------------------------------------------
    # BAB 13: REFERENSI
    # -------------------------------------------------------------
    builder.add_chapter_heading("BAB 13", "REFERENSI")
    ref_list = [
        "[1] Bahan Ajar Perkuliahan Kriptografi, 'Slide 6 - Steganografi', Program Studi Teknik Informatika, Fakultas Teknik, Universitas Siliwangi, 2026.",
        "[2] Tim Dosen Kriptografi, 'Petunjuk & Modul Latihan Praktikum Steganografi', Jurusan Teknik Informatika, Universitas Siliwangi, 2026.",
        "[3] Simmons, G. J., 'The Prisoners' Problem and the Subliminal Channel', in Proceedings of CRYPTO '83, Plenum Press, pp. 51-67, 1984.",
        "[4] Westfeld, A., & Pfitzmann, A., 'Attacks on Steganographic Systems: Breaking the Stegovanished Channel', in Information Hiding: 3rd International Workshop, LNCS 1768, Springer, pp. 61-76, 1999.",
        "[5] Johnson, N. F., & Jajodia, S., 'Exploring Steganography: Seeing the Unseen', IEEE Computer, Vol. 31, No. 2, pp. 26-34, 1998.",
        "[6] National Institute of Standards and Technology (NIST), 'Computer Security Resource Center (CSRC) Glossary: Steganography', U.S. Department of Commerce, 2024.",
        "[7] NumPy Developers, 'NumPy Documentation: Random Generator and Permutations (numpy.random.default_rng)', Versi 2.2, 2025.",
        "[8] Clark, A., et al., 'Pillow (PIL Fork) Documentation: Image File Formats and Compression Schemes', Versi 11.1, 2025."
    ]
    for ref_str in ref_list:
        builder.add_paragraph(ref_str, space_after=6.0, fontsize=8.6)
        
    # -------------------------------------------------------------
    # BAB 14: LAMPIRAN
    # -------------------------------------------------------------
    builder.add_chapter_heading("BAB 14", "LAMPIRAN")
    builder.add_section_heading("14.1 Log Hasil Validasi Otomatis (Master Test Suite run_all.py)")
    builder.add_paragraph("Seluruh pipeline pengujian telah dieksekusi secara otomatis dan divalidasi end-to-end dengan hasil 100% PASS:")
    
    pipe_headers = ["ID Modul", "Deskripsi Pengujian Unit", "Status Verifikasi", "Nilai Metrik Kunci"]
    pipe_rows = [
        ["VAL-01", "Validasi Dimensi Citra Cover (720x1280)", "PASS (100%)", "2.764.800 Bytes uint8"],
        ["VAL-02", "P1 Baseline Bug Reproduction (bin()[2:9])", "PASS (100%)", "|Δ| = 128 pada piksel 127"],
        ["VAL-03", "P1 Fixed Bitwise & 32-bit Header Length", "PASS (100%)", "Exact Match (160 Bytes)"],
        ["VAL-04", "P1 Kapasitas 3 Kanal Penuh (range(0,3))", "PASS (100%)", "337.5 KB (100% Utilisasi)"],
        ["VAL-05", "P2 Stego-Key Benar (Seed = 237006173)", "PASS (100%)", "Exact Match (160 Bytes)"],
        ["VAL-06", "P2 Stego-Key Salah (Seed = 237006174)", "PASS (100%)", "Corrupted Text / Invalid Header"],
        ["VAL-07", "P2 Change Map Bounding Box Analysis", "PASS (100%)", "Seq: 1x438 vs Rand: 1278x719"],
        ["VAL-08", "P3 Multi-Bit LSB m=1 Kapasitas 100%", "PASS (100%)", "PSNR 51.14 dB | Max Diff 1"],
        ["VAL-09", "P3 Multi-Bit LSB m=2 Kapasitas 100%", "PASS (100%)", "PSNR 44.14 dB | Max Diff 3"],
        ["VAL-10", "P3 Multi-Bit LSB m=3 Kapasitas 100%", "PASS (100%)", "PSNR 37.88 dB | Max Diff 7"],
        ["VAL-11", "P3 Multi-Bit LSB m=4 Kapasitas 100%", "PASS (100%)", "PSNR 31.97 dB | Max Diff 15"],
        ["VAL-12", "P4 Kripto-Stego Skenario A (Kedua Kunci Benar)", "PASS (100%)", "Plaintext 100% Pulih"],
        ["VAL-13", "P4 Kripto-Stego Skenario B (Kunci Enkripsi Salah)", "PASS (100%)", "Ciphertext Terbaca, Plaintext Acak"],
        ["VAL-14", "P4 Kripto-Stego Skenario C (Kunci Posisi Salah)", "PASS (100%)", "Header Gagal / Ekstraksi Batal"],
        ["VAL-15", "P5 Format Lossless PNG Ekstraksi", "PASS (100%)", "BER 0.00% (0 Bit Error)"],
        ["VAL-16", "P5 Format Uncompressed BMP Ekstraksi", "PASS (100%)", "BER 0.00% (0 Bit Error)"],
        ["VAL-17", "P5 Format Lossy JPEG (q=95) Ekstraksi", "PASS (100%)", "BER 48.02% (630 Bit Error)"],
        ["VAL-18", "Bonus Steganalisis Visual & Chi-Square Drop", "PASS (100%)", "Garis Baris 640 & Chi2 Anjlok 97.6%"]
    ]
    builder.add_table(pipe_headers, pipe_rows, [60.0, 185.0, 95.0, 147.28], 
                      [fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_LEFT, fitz.TEXT_ALIGN_CENTER, fitz.TEXT_ALIGN_LEFT])
    
    builder.add_section_heading("14.2 Cuplikan Kode Sumber Inti (Fixed LSB Embedding)")
    core_code = (
        "# Cuplikan Implementasi Penyisipan Bitwise Bebas Bug (src/p1_fixed.py)\n"
        "def embed_message_fixed(cover_path, secret_message, out_path):\n"
        "    cover_img = Image.open(cover_path).convert('RGB')\n"
        "    arr = np.array(cover_img, dtype=np.uint8)\n"
        "    flat = arr.reshape(-1)\n"
        "    \n"
        "    # 32-bit Length Header + UTF-8 Payload\n"
        "    payload_bytes = secret_message.encode('utf-8')\n"
        "    header_bits = [int(b) for b in f\"{len(payload_bytes):032b}\"]\n"
        "    payload_bits = []\n"
        "    for byte in payload_bytes:\n"
        "        payload_bits.extend([int(b) for b in f\"{byte:08b}\"])\n"
        "    total_bits = header_bits + payload_bits\n"
        "    \n"
        "    # Manipulasi Bitwise Murni (Menjamin |Δ| <= 1 untuk semua nilai [0, 255])\n"
        "    for i, bit in enumerate(total_bits):\n"
        "        flat[i] = (flat[i] & ~1) | bit\n"
        "    \n"
        "    stego_img = Image.fromarray(flat.reshape(arr.shape))\n"
        "    stego_img.save(out_path, format='PNG')\n"
        "    return out_path\n"
    )
    builder.add_code_block(core_code, caption="Listing 14.1 Kode Fungsi Penyisipan LSB Fixed (Bitwise & 32-bit Header)")
    
    # Finalize document
    builder.finalize_document()

if __name__ == "__main__":
    build_full_report()
