# -*- coding: utf-8 -*-
"""Doc 1 file Excel reel-brief da co san (bat ky brand/layout nao gan giong
form cua tool nay) va dich cot Voiceover + On-screen Text sang ngon ngu khac,
dam bao dung ngu canh (transcreation, khong dich word-by-word)."""

import json
from typing import List, Dict, Optional

import openpyxl
from pydantic import BaseModel, Field
from google import genai
from google.genai import types


class SheetData:
    def __init__(self, sheet_name, info_rows, headers, scene_rows, voiceover_col, onscreen_col):
        self.sheet_name = sheet_name
        self.info_rows = info_rows  # list of (label, value)
        self.headers = headers  # list of str, dung header goc trong file
        self.scene_rows = scene_rows  # list of dict {header: value}
        self.voiceover_col = voiceover_col  # ten header goc chua Voiceover
        self.onscreen_col = onscreen_col  # ten header goc chua On-screen Text


def _find_header_name(headers, *candidates):
    for h in headers:
        if not h:
            continue
        h_norm = str(h).strip().lower().replace("-", "").replace(" ", "")
        for cand in candidates:
            if cand in h_norm:
                return h
    return None


def parse_reel_brief_excel(file_like) -> List[SheetData]:
    """file_like: path hoac file-object (tu st.file_uploader) tro toi file .xlsx."""
    wb = openpyxl.load_workbook(file_like, data_only=True)
    sheets = []

    for ws in wb.worksheets:
        max_row = ws.max_row
        max_col = ws.max_column

        header_row_idx = None
        for r in range(1, max_row + 1):
            for c in range(1, min(max_col, 4) + 1):
                val = ws.cell(row=r, column=c).value
                if val and str(val).strip().lower() == "time":
                    header_row_idx = r
                    break
            if header_row_idx:
                break

        if not header_row_idx:
            continue  # sheet nay khong co bang scene, bo qua

        # thu thap info_rows (label o cot B, value o cot C) phia tren header row
        info_rows = []
        for r in range(1, header_row_idx):
            label = ws.cell(row=r, column=2).value
            value = ws.cell(row=r, column=3).value
            if label and str(label).strip() and str(label).strip().lower() != "item":
                info_rows.append((str(label).strip(), value if value is not None else ""))

        # headers: doc tu cot 1 tro di tai header_row_idx, den khi het non-empty (cho phep 1 khoang trong roi dung)
        headers = []
        c = 1
        while c <= max_col:
            val = ws.cell(row=header_row_idx, column=c).value
            if val is None or str(val).strip() == "":
                if headers:
                    break
                c += 1
                continue
            headers.append(str(val).strip())
            c += 1
        n_cols = len(headers)

        voiceover_col = _find_header_name(headers, "voiceover")
        onscreen_col = _find_header_name(headers, "onscreentext", "onscreen")

        scene_rows = []
        r = header_row_idx + 1
        while r <= max_row:
            row_vals = [ws.cell(row=r, column=c).value for c in range(1, n_cols + 1)]
            if all(v is None or str(v).strip() == "" for v in row_vals):
                break
            row_dict = {headers[i]: (row_vals[i] if row_vals[i] is not None else "") for i in range(n_cols)}
            scene_rows.append(row_dict)
            r += 1

        sheets.append(SheetData(ws.title, info_rows, headers, scene_rows, voiceover_col, onscreen_col))

    return sheets


class TranslatedPair(BaseModel):
    voiceover_translated: str
    onscreen_text_translated: str


class TranslatedLines(BaseModel):
    lines: List[str] = Field(
        description="Ban dich cho TUNG dong trong danh sach duoc danh so, DUNG SO LUONG va DUNG THU TU. "
        "Moi phan tu trong list nay tuong ung 1 dong duoc danh so trong DANH SACH CAN DICH, KHONG duoc gop "
        "nhieu dong thanh 1, KHONG duoc bo sot dong nao."
    )


def _split_lines(text) -> List[str]:
    text = str(text) if text is not None else ""
    return text.split("\n")


def _build_lines_prompt(numbered_lines: List[str], full_context: str, language: str) -> str:
    lines_block = "\n".join(f"{i+1}. \"{line}\"" for i, line in enumerate(numbered_lines))
    return f"""
Ban la 1 chuyen gia localization/transcreation video marketing cho nganh tai
chinh/trading, dich noi dung sang ngon ngu: {language}.

{full_context}

YEU CAU BAT BUOC:
- Day la TRANSCREATION, KHONG PHAI dich word-by-word. Phai giu dung Y NGHIA,
  CAM XUC, TONE va MUC DICH cua cau (doc phan boi canh o tren de hieu dung
  mach chuyen), sao cho nghe tu nhien nhu nguoi ban xu {language} viet ra,
  phu hop van hoa dia phuong.
- On-screen Text (neu co) phai NGAN GON nhu ban goc (la text hien tren man
  hinh, khong phai cau van dai).
- Cac ten rieng/brand (WeMasterTrade, WeGolden...), so tien, %, ngay thang,
  link PHAI giu nguyen KHONG dich, KHONG doi don vi.
- DUOI DAY la danh sach CAC DONG rieng le da duoc danh so (moi dong co the la
  1 cau, 1 cum tu, hoac co the la chuoi rong). BAT BUOC dich TUNG DONG mot,
  tra ve DUNG {len(numbered_lines)} phan tu trong "lines", DUNG THU TU voi
  danh sach duoi day. Neu dong nao la chuoi rong "" thi giu nguyen chuoi
  rong "" trong ket qua (KHONG dich, KHONG bo qua, van phai co du so luong
  phan tu). KHONG duoc gop 2 dong lai thanh 1, vi day se pha vo dinh dang
  xuong dong cua ban goc khi ghep lai.

DANH SACH CAC DONG CAN DICH ({len(numbered_lines)} dong):
{lines_block}
"""


class TranslationService:
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def _translate_lines(self, lines: List[str], full_context: str, language: str) -> List[str]:
        prompt = _build_lines_prompt(lines, full_context, language)
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TranslatedLines,
                temperature=0.6,
            ),
        )
        if response.parsed is not None:
            result = response.parsed
        else:
            result = TranslatedLines(**json.loads(response.text))

        if len(result.lines) != len(lines):
            raise ValueError(
                f"Gemini tra ve {len(result.lines)} dong nhung gui di {len(lines)} dong (ngon ngu: {language}). "
                f"Vui long thu lai."
            )
        return result.lines

    def translate_sheet(self, sheet: SheetData, language: str, context_note: str = "") -> List[TranslatedPair]:
        if not sheet.scene_rows:
            return []

        context_block = ""
        if sheet.info_rows:
            ctx_lines = "\n".join(f"- {label}: {value}" for label, value in sheet.info_rows)
            context_block += f"""
Boi canh chung cua video (de dich dung tone/y nghia, KHONG can dich lai phan
nay):
{ctx_lines}
"""
        scene_ctx = "\n".join(
            f"- Scene {i+1} ({row.get('Scene', '')}, {row.get('Time', '')}): "
            f"Voiceover goc: \"{row.get(sheet.voiceover_col, '')}\" | "
            f"On-screen Text goc: \"{row.get(sheet.onscreen_col, '')}\""
            for i, row in enumerate(sheet.scene_rows)
        )
        full_context = f"{context_block}\nToan bo kich ban goc de nam duoc mach truyen tai xuyen suot cac scene:\n{scene_ctx}"

        # Tach tung dong (giu nguyen dong rong de bao toan cau truc xuong dong),
        # gom tat ca dong CAN dich (khong rong) cua ca sheet vao 1 danh sach de
        # goi Gemini 1 lan, tranh mat dinh dang khi model tu gop doan lai.
        split_cache = {}  # (row_idx, field) -> list cac dong (bao gom rong)
        to_translate = []  # danh sach text can dich
        positions = []  # (row_idx, field, line_idx) tuong ung voi to_translate

        for row_idx, row in enumerate(sheet.scene_rows):
            for field, col_name in (("voiceover", sheet.voiceover_col), ("onscreen", sheet.onscreen_col)):
                raw_lines = _split_lines(row.get(col_name, ""))
                split_cache[(row_idx, field)] = raw_lines
                for line_idx, line in enumerate(raw_lines):
                    if line.strip():
                        to_translate.append(line)
                        positions.append((row_idx, field, line_idx))

        if to_translate:
            translated_lines = self._translate_lines(to_translate, full_context, language)
            for (row_idx, field, line_idx), translated in zip(positions, translated_lines):
                split_cache[(row_idx, field)][line_idx] = translated

        rows_out = []
        for row_idx in range(len(sheet.scene_rows)):
            vo_lines = split_cache[(row_idx, "voiceover")]
            os_lines = split_cache[(row_idx, "onscreen")]
            rows_out.append(TranslatedPair(
                voiceover_translated="\n".join(vo_lines),
                onscreen_text_translated="\n".join(os_lines),
            ))
        return rows_out
