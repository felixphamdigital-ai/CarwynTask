# -*- coding: utf-8 -*-
"""Build file Excel cho tap CEO Interview, dung DUNG layout that cua EP01/
EP04/EP05 trong 'WeGolden Video Research - CW.xlsx':
Header info (SERIES name/Talent/Pillar/Duration/Episode Key/Next Episode
Key) + bang 8 dong (Section/CEO Script/On-screen Text/Visual-Camera
Direction/Ref)."""

from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from guideline_data import BRANDS

FONT_NAME = "Be Vietnam Pro"


def _fill(hex_color):
    return PatternFill(start_color=hex_color, end_color=hex_color, fill_type="solid")


def _sheet_name(episode_label: str, index: int) -> str:
    base = f"{episode_label} - Opt{index}" if index > 1 else episode_label
    return base[:31]


def build_ceo_episode_workbook(episode_label: str, options: list) -> BytesIO:
    """episode_label: vi du 'EP03'. options: list of CEOEpisodeOut (pydantic)."""
    cfg = BRANDS["WeGolden"]
    wb = Workbook()
    wb.remove(wb.active)

    for idx, opt in enumerate(options, start=1):
        ws = wb.create_sheet(title=_sheet_name(episode_label, idx))

        ws.column_dimensions["A"].width = 18
        ws.column_dimensions["B"].width = 55
        ws.column_dimensions["C"].width = 30
        ws.column_dimensions["D"].width = 60
        ws.column_dimensions["E"].width = 34

        row = 1
        c = ws.cell(row=row, column=1, value=episode_label)
        c.font = Font(name=FONT_NAME, bold=True, size=13)
        row += 1

        info_rows = [
            ("SERIES name", opt.series_name),
            ("Talent", opt.talent),
            ("Pillar", opt.pillar),
            ("Duration", opt.duration),
            ("Topic", opt.topic_title),
            ("Episode Key", opt.episode_key),
            ("Next Episode Key", opt.next_episode_key),
        ]
        for label, value in info_rows:
            lc = ws.cell(row=row, column=1, value=label)
            lc.font = Font(name=FONT_NAME, bold=True)
            lc.fill = _fill(cfg["label_fill"])
            lc.alignment = Alignment(wrap_text=True, vertical="center")
            vc = ws.cell(row=row, column=2, value=value)
            vc.font = Font(name=FONT_NAME)
            vc.alignment = Alignment(wrap_text=True, vertical="center")
            ws.row_dimensions[row].height = 45
            row += 1

        header_row = row
        headers = ["Section", "CEO Script", "On-screen Text", "Visual / Camera Direction", "Ref"]
        for col_idx, h in enumerate(headers, start=1):
            c = ws.cell(row=header_row, column=col_idx, value=h)
            c.font = Font(name=FONT_NAME, bold=True, color="FFFFFF")
            c.fill = _fill(cfg["table_header_fill"] if col_idx > 1 else cfg["header_fill"])
            c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        ws.row_dimensions[header_row].height = 22
        row += 1

        for sec in opt.sections:
            values = [sec.section, sec.ceo_script, sec.onscreen_text, sec.visual_direction, sec.ref]
            for col_idx, val in enumerate(values, start=1):
                c = ws.cell(row=row, column=col_idx, value=val)
                c.font = Font(name=FONT_NAME, bold=(col_idx == 1))
                c.alignment = Alignment(
                    wrap_text=True, vertical="center",
                    horizontal="center" if col_idx == 1 else "left",
                )
            ws.row_dimensions[row].height = 140
            row += 1

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
