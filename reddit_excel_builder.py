# -*- coding: utf-8 -*-
"""Build file Excel cho Reddit content, dung cau truc giong sheet
'Content cho khách' trong Reddit research.xlsx: No | Format | Content Angle |
Topic | Content | Image | Lưu ý."""

from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from guideline_data import BRANDS

FONT_NAME = "Be Vietnam Pro"


def _fill(hex_color):
    return PatternFill(start_color=hex_color, end_color=hex_color, fill_type="solid")


def build_reddit_workbook(brand: str, posts: list) -> BytesIO:
    """posts: list of RedditPost (pydantic) da generate tu Gemini."""
    cfg = BRANDS[brand]
    wb = Workbook()
    ws = wb.active
    ws.title = "Content Reddit"

    headers = ["No", "Format", "Content Angle", "Topic", "Content", "Image", "Lưu ý"]
    widths = [6, 20, 28, 34, 70, 30, 30]
    for col_idx, (h, w) in enumerate(zip(headers, widths), start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = w
        c = ws.cell(row=1, column=col_idx, value=h)
        c.font = Font(name=FONT_NAME, bold=True, color="FFFFFF")
        c.fill = _fill(cfg["header_fill"])
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    ws.row_dimensions[1].height = 22

    row = 2
    for idx, post in enumerate(posts, start=1):
        values = [idx, post.format, post.content_angle, post.topic, post.content, post.image_note, post.note]
        for col_idx, val in enumerate(values, start=1):
            c = ws.cell(row=row, column=col_idx, value=val)
            c.font = Font(name=FONT_NAME)
            c.alignment = Alignment(wrap_text=True, vertical="top", horizontal="left")
        ws.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical="top", horizontal="center")
        ws.row_dimensions[row].height = 220
        row += 1

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
