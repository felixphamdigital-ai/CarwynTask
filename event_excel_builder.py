# -*- coding: utf-8 -*-
"""Build file Excel cho Event Announcement content: bang phang 1 sheet, cot
Headline/Content da ngon ngu (dong mau theo ngon ngu giong video mode)."""

from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from guideline_data import BRANDS, get_language_code, LANGUAGE_COLOR_PALETTE

FONT_NAME = "Be Vietnam Pro"


def _fill(hex_color):
    return PatternFill(start_color=hex_color, end_color=hex_color, fill_type="solid")


def _localized_lookup(post):
    return {loc.language.strip().lower(): loc for loc in post.localizations}


def build_event_workbook(brand: str, posts: list, languages: list = None) -> BytesIO:
    """posts: list of EventPost (pydantic) da generate tu Gemini."""
    cfg = BRANDS[brand]
    wb = Workbook()
    ws = wb.active
    ws.title = "Event Announcement"

    langs = list(languages) if languages else (
        [loc.language for loc in posts[0].localizations] if posts and posts[0].localizations else []
    )
    lang_colors = {
        lang: LANGUAGE_COLOR_PALETTE[i % len(LANGUAGE_COLOR_PALETTE)]
        for i, lang in enumerate(langs)
    }
    lang_codes = {lang: get_language_code(lang) for lang in langs}

    headers = ["No", "Angle", "Headline (EN)"]
    headers += [f"Headline ({lang_codes[lang]})" for lang in langs]
    headers.append("Content (EN)")
    headers += [f"Content ({lang_codes[lang]})" for lang in langs]
    headers += ["Hashtags", "Image", "Note"]

    col_lang = [None, None, None]
    col_lang += list(langs)
    col_lang.append(None)
    col_lang += list(langs)
    col_lang += [None, None, None]

    widths = [6, 26, 40] + [40] * len(langs) + [55] + [55] * len(langs) + [34, 30, 30]
    for col_idx, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = w

    for col_idx, h in enumerate(headers, start=1):
        lang = col_lang[col_idx - 1]
        c = ws.cell(row=1, column=col_idx, value=h)
        if lang:
            c.font = Font(name=FONT_NAME, bold=True, color="FFFFFF")
            c.fill = _fill(lang_colors[lang]["header"])
        else:
            c.font = Font(name=FONT_NAME, bold=True, color="FFFFFF")
            c.fill = _fill(cfg["header_fill"])
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    ws.row_dimensions[1].height = 22

    row = 2
    for idx, post in enumerate(posts, start=1):
        loc_map = _localized_lookup(post)

        values = [idx, post.angle_vi, post.headline_en]
        for lang in langs:
            loc = loc_map.get(lang.strip().lower())
            values.append(loc.headline_adapt if loc else "")

        values.append(post.content_en)
        for lang in langs:
            loc = loc_map.get(lang.strip().lower())
            values.append(loc.content_adapt if loc else "")

        values += [post.hashtags, post.image_note, post.note]

        for col_idx, val in enumerate(values, start=1):
            lang = col_lang[col_idx - 1]
            c = ws.cell(row=row, column=col_idx, value=val)
            c.font = Font(name=FONT_NAME)
            c.alignment = Alignment(wrap_text=True, vertical="top", horizontal="left")
            if lang:
                c.fill = _fill(lang_colors[lang]["cell"])
        ws.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical="top", horizontal="center")
        ws.row_dimensions[row].height = 240
        row += 1

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
