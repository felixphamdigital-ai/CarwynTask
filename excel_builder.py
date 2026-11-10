# -*- coding: utf-8 -*-
"""Build file Excel dung form co dinh giong 'Reels Latam.xlsx' / 'Reels WG.xlsx'.

Ho tro dong so cot Voice adapt / Text adapt tuy theo so ngon ngu ban dia hoa
duoc chon (co the 0, 1, hoac nhieu ngon ngu cung luc, vi du Kazakh + Uzbek).
"""

from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from guideline_data import BRANDS, get_language_code, LANGUAGE_COLOR_PALETTE

FONT_NAME = "Be Vietnam Pro"


def _fill(hex_color):
    return PatternFill(start_color=hex_color, end_color=hex_color, fill_type="solid")


def _label_cell(ws, row, col, value, fill_hex, bold=True):
    c = ws.cell(row=row, column=col, value=value)
    c.font = Font(name=FONT_NAME, bold=bold)
    c.fill = _fill(fill_hex)
    c.alignment = Alignment(wrap_text=True, vertical="center")
    return c


def _value_cell(ws, row, col, value, wrap=True, fill_hex=None, valign="center"):
    c = ws.cell(row=row, column=col, value=value)
    c.font = Font(name=FONT_NAME)
    c.alignment = Alignment(wrap_text=wrap, vertical=valign)
    if fill_hex:
        c.fill = _fill(fill_hex)
    return c


def _sheet_name(topic: str, index: int) -> str:
    base = f"Option {index}"
    if topic:
        # excel sheet name max 31 chars, khong duoc chua : \ / ? * [ ]
        safe_topic = "".join(ch for ch in topic if ch not in r':\/?*[]')[:20].strip()
        if safe_topic:
            base = f"{index}. {safe_topic}"
    return base[:31]


def _languages_for_option(opt, languages):
    """Uu tien danh sach languages truyen vao (dung de generate); neu khong co
    thi suy ra tu localizations cua scene dau tien, giu nguyen thu tu."""
    if languages:
        return list(languages)
    if opt.scenes and opt.scenes[0].localizations:
        return [loc.language for loc in opt.scenes[0].localizations]
    return []


def _localized_lookup(scene):
    return {loc.language.strip().lower(): loc for loc in scene.localizations}


def build_workbook(brand: str, options: list, languages: list = None) -> BytesIO:
    """options: list of VideoOption (pydantic) da generate tu Gemini.
    languages: danh sach ngon ngu ban dia hoa da dung khi generate (giu dung
    thu tu cot); neu None se tu suy ra tu du lieu scene."""
    cfg = BRANDS[brand]
    wb = Workbook()
    wb.remove(wb.active)

    for idx, opt in enumerate(options, start=1):
        ws = wb.create_sheet(title=_sheet_name(opt.topic, idx))
        langs = _languages_for_option(opt, languages)
        n_langs = len(langs)

        # --- mau rieng cho tung ngon ngu (dung chung cho Voice adapt + Text adapt) ---
        lang_colors = {
            lang: LANGUAGE_COLOR_PALETTE[i % len(LANGUAGE_COLOR_PALETTE)]
            for i, lang in enumerate(langs)
        }
        lang_codes = {lang: get_language_code(lang) for lang in langs}

        # --- xay dung header dong theo so ngon ngu ---
        headers = ["Time", "Scene", "Voiceover"]
        headers += [f"Voice adapt ({lang_codes[lang]})" for lang in langs]
        headers.append("On-screen Text")
        headers += [f"Text adapt ({lang_codes[lang]})" for lang in langs]
        headers.append("Visual Direction")
        headers.append("Ref")
        if not cfg["localizable"]:
            headers.append("Note")

        # col_lang[i] = ten ngon ngu cua cot i (0-indexed), None neu la cot
        # khong gan ngon ngu nao (Time/Scene/Voiceover/On-screen Text/...)
        col_lang = [None, None, None]
        col_lang += list(langs)
        col_lang.append(None)
        col_lang += list(langs)
        col_lang.append(None)  # Visual Direction
        col_lang.append(None)  # Ref
        if not cfg["localizable"]:
            col_lang.append(None)  # Note

        n_cols = len(headers)

        # --- cot do rong ---
        ws.column_dimensions["B"].width = 20
        ws.column_dimensions["C"].width = 55  # Voiceover (info block cung dung cot C)
        col = 4
        for _ in range(n_langs):
            ws.column_dimensions[get_column_letter(col)].width = 45
            col += 1
        ws.column_dimensions[get_column_letter(col)].width = 26 if n_langs else 55  # On-screen Text
        col += 1
        for _ in range(n_langs):
            ws.column_dimensions[get_column_letter(col)].width = 32
            col += 1
        ws.column_dimensions[get_column_letter(col)].width = 50  # Visual Direction
        col += 1
        ws.column_dimensions[get_column_letter(col)].width = 30  # Ref
        col += 1
        if not cfg["localizable"]:
            ws.column_dimensions[get_column_letter(col)].width = 30  # Note

        row = 1
        _label_cell(ws, row, 2, "Item", cfg["header_fill"])
        _value_cell(ws, row, 3, "Guideline", wrap=True, fill_hex=cfg["header_fill"])
        row += 1

        info_rows = [
            ("Topic", opt.topic),
            ("Angle", opt.angle_vi),
            ("Target Audience", opt.target_audience),
            ("Viewer Takeaway", opt.viewer_takeaway),
            ("Video Length", opt.video_length),
            ("Format", opt.format),
            ("Tone", opt.tone),
            ("Key Message", opt.key_message),
            ("Note", opt.ai_speaker_note),
        ]
        for label, value in info_rows:
            _label_cell(ws, row, 2, label, cfg["label_fill"])
            _value_cell(ws, row, 3, value)
            ws.row_dimensions[row].height = 60
            row += 1

        row += 1  # blank spacer row

        header_row = row
        for col_idx, h in enumerate(headers, start=1):
            lang = col_lang[col_idx - 1]
            c = ws.cell(row=header_row, column=col_idx, value=h)
            if lang:
                c.font = Font(name=FONT_NAME, bold=True, color="FFFFFF")
                c.fill = _fill(lang_colors[lang]["header"])
            else:
                c.font = Font(name=FONT_NAME, bold=True)
                c.fill = _fill(cfg["table_header_fill"])
            c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        ws.row_dimensions[header_row].height = 22
        row += 1

        for scene in opt.scenes:
            loc_map = _localized_lookup(scene)

            values = [scene.time, scene.scene, scene.voiceover]
            for lang in langs:
                loc = loc_map.get(lang.strip().lower())
                values.append(loc.voice_adapt if loc else "")

            values.append(scene.onscreen_text)

            for lang in langs:
                loc = loc_map.get(lang.strip().lower())
                values.append(loc.text_adapt if loc else "")

            values.append(scene.visual_direction)
            values.append(scene.ref or "")
            if not cfg["localizable"]:
                values.append(scene.note or "")

            for col_idx, val in enumerate(values, start=1):
                lang = col_lang[col_idx - 1]
                fill_hex = lang_colors[lang]["cell"] if lang else None
                c = _value_cell(ws, row, col_idx, val, wrap=True, fill_hex=fill_hex)
                if col_idx in (1, 2):
                    c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
                    c.font = Font(name=FONT_NAME, bold=(col_idx == 2))
            ws.row_dimensions[row].height = 150
            row += 1

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
