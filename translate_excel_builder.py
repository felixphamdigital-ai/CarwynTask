# -*- coding: utf-8 -*-
"""Build lai file Excel reel-brief, giu nguyen toan bo cot/du lieu goc, chi
CHEN THEM 2 cot moi (Voice adapt / Text adapt) ngay sau Voiceover / On-screen
Text, dung mau rieng theo ngon ngu (dong bo voi excel_builder.py cua video mode)."""

from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from guideline_data import BRANDS, get_language_code, LANGUAGE_COLOR_PALETTE

FONT_NAME = "Be Vietnam Pro"


def _fill(hex_color):
    return PatternFill(start_color=hex_color, end_color=hex_color, fill_type="solid")


def build_translated_workbook(sheets, translations_by_sheet: dict, language: str, brand: str) -> BytesIO:
    """sheets: List[SheetData] tu translate_service.parse_reel_brief_excel.
    translations_by_sheet: dict {sheet_name: List[TranslatedPair]} dung thu tu voi sheet.scene_rows.
    """
    cfg = BRANDS.get(brand, BRANDS["WeMasterTrade"])
    lang_code = get_language_code(language)
    colors = LANGUAGE_COLOR_PALETTE[0]
    is_rtl = language.strip().lower() == "arabic"

    wb = Workbook()
    wb.remove(wb.active)

    for sheet in sheets:
        ws = wb.create_sheet(title=sheet.sheet_name[:31])
        translations = translations_by_sheet.get(sheet.sheet_name, [])

        row = 1
        if sheet.info_rows:
            c = ws.cell(row=row, column=2, value="Item")
            c.font = Font(name=FONT_NAME, bold=True)
            c.fill = _fill(cfg["header_fill"])
            c2 = ws.cell(row=row, column=3, value="Guideline")
            c2.font = Font(name=FONT_NAME, bold=True)
            c2.fill = _fill(cfg["header_fill"])
            row += 1

            for label, value in sheet.info_rows:
                lc = ws.cell(row=row, column=2, value=label)
                lc.font = Font(name=FONT_NAME, bold=True)
                lc.fill = _fill(cfg["label_fill"])
                lc.alignment = Alignment(wrap_text=True, vertical="center")
                vc = ws.cell(row=row, column=3, value=value)
                vc.font = Font(name=FONT_NAME)
                vc.alignment = Alignment(wrap_text=True, vertical="center")
                ws.row_dimensions[row].height = 50
                row += 1
            row += 1  # spacer

        # --- xay dung header moi: chen "Voice adapt (CODE)" sau Voiceover,
        # "Text adapt (CODE)" sau On-screen Text ---
        new_headers = []
        col_is_lang = []
        for h in sheet.headers:
            new_headers.append(h)
            col_is_lang.append(False)
            if h == sheet.voiceover_col:
                new_headers.append(f"Voice adapt ({lang_code})")
                col_is_lang.append(True)
            elif h == sheet.onscreen_col:
                new_headers.append(f"Text adapt ({lang_code})")
                col_is_lang.append(True)

        header_row = row
        for col_idx, h in enumerate(new_headers, start=1):
            c = ws.cell(row=header_row, column=col_idx, value=h)
            if col_is_lang[col_idx - 1]:
                c.font = Font(name=FONT_NAME, bold=True, color="FFFFFF")
                c.fill = _fill(colors["header"])
            else:
                c.font = Font(name=FONT_NAME, bold=True)
                c.fill = _fill(cfg["table_header_fill"])
            c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
            ws.column_dimensions[get_column_letter(col_idx)].width = 45 if col_is_lang[col_idx - 1] else 32
        ws.row_dimensions[header_row].height = 22
        row += 1

        for r_idx, scene_row in enumerate(sheet.scene_rows):
            translated = translations[r_idx] if r_idx < len(translations) else None
            col_idx = 1
            for h in sheet.headers:
                val = scene_row.get(h, "")
                c = ws.cell(row=row, column=col_idx, value=val)
                c.font = Font(name=FONT_NAME, bold=(h == "Scene"))
                c.alignment = Alignment(
                    wrap_text=True, vertical="center",
                    horizontal="center" if h in ("Time", "Scene") else "left",
                )
                col_idx += 1

                if h == sheet.voiceover_col:
                    tv = translated.voiceover_translated if translated else ""
                    c2 = ws.cell(row=row, column=col_idx, value=tv)
                    c2.font = Font(name=FONT_NAME)
                    c2.fill = _fill(colors["cell"])
                    c2.alignment = Alignment(wrap_text=True, vertical="center", horizontal=("right" if is_rtl else "left"))
                    col_idx += 1
                elif h == sheet.onscreen_col:
                    tt = translated.onscreen_text_translated if translated else ""
                    c2 = ws.cell(row=row, column=col_idx, value=tt)
                    c2.font = Font(name=FONT_NAME)
                    c2.fill = _fill(colors["cell"])
                    c2.alignment = Alignment(wrap_text=True, vertical="center", horizontal=("right" if is_rtl else "left"))
                    col_idx += 1

            ws.row_dimensions[row].height = 150
            row += 1

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
