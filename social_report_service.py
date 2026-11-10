# -*- coding: utf-8 -*-
"""
Social Media Monthly Report Generator for Facebook Pages (WeMasterTrade / WeGolden)
Chuyen doi du lieu export tu Facebook Page Analytics (file CSV) thanh:
1. File Excel (.xlsx) form chuan mau (Header mau vang kem #FFF2CC, merge o Thang/Page/So bai)
2. File PDF (.pdf) kho A4 Landscape chuan dep giong het mau Report_social_WeMasterTrade_September_2026.pdf
"""

import io
import os
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ReportLab cho xuat file PDF
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Dang ky font ho tro tieng Viet
FONT_NAME = "Arial"
try:
    if os.path.exists("C:/Windows/Fonts/arial.ttf"):
        pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
    if os.path.exists("C:/Windows/Fonts/arialbd.ttf"):
        pdfmetrics.registerFont(TTFont("Arial-Bold", "C:/Windows/Fonts/arialbd.ttf"))
except Exception:
    FONT_NAME = "Helvetica"


HEADER_FILL_COLOR = "FFF2CC"  # Mau vang kem giong het hinh mau


def _thin_border():
    thin = Side(border_style="thin", color="000000")
    return Border(left=thin, right=thin, top=thin, bottom=thin)


def parse_facebook_csvs(file_inputs: List[Any]) -> pd.DataFrame:
    """Doc 1 hoac nhieu file CSV duoc upload hoac truyen vao, gop va loai bo trung lap."""
    dfs = []
    for item in file_inputs:
        try:
            if isinstance(item, (str, Path)):
                df = pd.read_csv(item)
            else:
                # File upload tu Streamlit
                df = pd.read_csv(item)
            dfs.append(df)
        except Exception as e:
            continue

    if not dfs:
        return pd.DataFrame()

    all_df = pd.concat(dfs, ignore_index=True)

    # Loai bo duplicate theo ID bai viet hoac Link bai
    if "ID bài viết" in all_df.columns:
        all_df = all_df.drop_duplicates(subset=["ID bài viết"])
    elif "Liên kết vĩnh viễn" in all_df.columns:
        all_df = all_df.drop_duplicates(subset=["Liên kết vĩnh viễn"])

    # Parse thoi gian dang
    time_col = None
    for c in ["Thời gian đăng", "Created Time", "Publish Time", "Ngày đăng"]:
        if c in all_df.columns:
            time_col = c
            break

    if time_col:
        # Xu ly dinh dang thoi gian (MM/DD/YYYY hoac DD/MM/YYYY)
        all_df["parsed_dt"] = pd.to_datetime(all_df[time_col], errors="coerce")
        all_df["report_month"] = all_df["parsed_dt"].dt.month
        all_df["report_year"] = all_df["parsed_dt"].dt.year
    else:
        all_df["report_month"] = 10
        all_df["report_year"] = 2026

    # Chuan hoa ten cac cot
    all_df["clean_page"] = all_df["Tên Trang"] if "Tên Trang" in all_df.columns else "Wemastertrade AU"
    all_df["clean_link"] = all_df["Liên kết vĩnh viễn"] if "Liên kết vĩnh viễn" in all_df.columns else ""
    all_df["clean_like"] = pd.to_numeric(all_df["Cảm xúc"] if "Cảm xúc" in all_df.columns else 0, errors="coerce").fillna(0).astype(int)
    all_df["clean_comment"] = pd.to_numeric(all_df["Bình luận"] if "Bình luận" in all_df.columns else 0, errors="coerce").fillna(0).astype(int)
    all_df["clean_view"] = pd.to_numeric(all_df["Lượt xem"] if "Lượt xem" in all_df.columns else 0, errors="coerce").fillna(0).astype(int)
    
    # Engagement & Interaction
    if "Cảm xúc, bình luận và lượt chia sẻ" in all_df.columns:
        all_df["clean_engagement"] = pd.to_numeric(all_df["Cảm xúc, bình luận và lượt chia sẻ"], errors="coerce").fillna(0).astype(int)
        all_df["clean_interaction"] = all_df["clean_engagement"]
    else:
        all_df["clean_engagement"] = all_df["clean_like"] + all_df["clean_comment"]
        all_df["clean_interaction"] = all_df["clean_engagement"]

    return all_df


def build_social_report_excel(df: pd.DataFrame, month_num: int, page_name: str) -> io.BytesIO:
    """Xuat file Excel dung form giong het anh mau (kem merge cell), ho tro 1 page hoac tat ca cac page."""
    wb = Workbook()
    ws = wb.active
    tab_title = f"{page_name[:20]}_T{month_num}".replace("🌟", "").strip()
    ws.title = tab_title or f"Report_T{month_num}"

    headers = [
        "Tháng",
        "Page",
        "Số bài đăng trong\ntháng",
        "Link bài",
        "Lượt Like",
        "Comments",
        "Engagement",
        "View",
        "Interaction\n(Tương tác)",
    ]
    widths = [10, 26, 20, 75, 12, 12, 14, 10, 16]

    # Header row
    for col_idx, (h, w) in enumerate(zip(headers, widths), start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = w
        c = ws.cell(row=1, column=col_idx, value=h)
        c.font = Font(name="Arial", size=10, bold=True, color="000000")
        c.fill = PatternFill(start_color=HEADER_FILL_COLOR, end_color=HEADER_FILL_COLOR, fill_type="solid")
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        c.border = _thin_border()
    ws.row_dimensions[1].height = 28

    if "clean_page" in df.columns:
        page_groups = [(p, grp) for p, grp in df.groupby("clean_page", sort=False)]
    else:
        page_groups = [(page_name, df)]

    start_row = 2
    for p_name, p_df in page_groups:
        grp_rows = len(p_df)
        grp_start_row = start_row

        for i, (_, r) in enumerate(p_df.iterrows()):
            curr_row = start_row + i
            link_val = str(r["clean_link"]).strip()
            like_val = int(r["clean_like"])
            comm_val = int(r["clean_comment"])
            eng_val = int(r["clean_engagement"])
            view_val = int(r["clean_view"])
            inter_val = int(r["clean_interaction"])

            # Dien du lieu tung cot
            c_thang = ws.cell(row=curr_row, column=1, value=month_num)
            c_page = ws.cell(row=curr_row, column=2, value=p_name)
            c_count = ws.cell(row=curr_row, column=3, value=grp_rows)

            c_link = ws.cell(row=curr_row, column=4, value=link_val)
            c_link.hyperlink = link_val
            c_link.font = Font(name="Arial", size=9, color="1155CC", underline="single")
            c_link.alignment = Alignment(vertical="center", horizontal="left")

            c_like = ws.cell(row=curr_row, column=5, value=like_val)
            c_comm = ws.cell(row=curr_row, column=6, value=comm_val)
            c_eng = ws.cell(row=curr_row, column=7, value=eng_val)
            c_view = ws.cell(row=curr_row, column=8, value=view_val)
            c_inter = ws.cell(row=curr_row, column=9, value=inter_val)

            for col_idx in [1, 2, 3, 5, 6, 7, 8, 9]:
                cell = ws.cell(row=curr_row, column=col_idx)
                cell.font = Font(name="Arial", size=9)
                cell.alignment = Alignment(vertical="center", horizontal="center")

            for col_idx in range(1, 10):
                ws.cell(row=curr_row, column=col_idx).border = _thin_border()

            ws.row_dimensions[curr_row].height = 20

        # Merge cac cot Thang, Page, So bai dang trong thang cua group nay
        if grp_rows > 1:
            grp_end_row = grp_start_row + grp_rows - 1
            ws.merge_cells(start_row=grp_start_row, start_column=1, end_row=grp_end_row, end_column=1)
            ws.merge_cells(start_row=grp_start_row, start_column=2, end_row=grp_end_row, end_column=2)
            ws.merge_cells(start_row=grp_start_row, start_column=3, end_row=grp_end_row, end_column=3)

        start_row += grp_rows

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def build_social_report_pdf(df: pd.DataFrame, month_num: int, page_name: str) -> io.BytesIO:
    """Xuat file PDF kho A4 Landscape giong het mau Report_social_WeMasterTrade_September_2026."""
    headers = [
        "Tháng",
        "Page",
        "Số bài đăng trong\ntháng",
        "Link bài",
        "Lượt Like",
        "Comments",
        "Engagement",
        "View",
        "Interaction\n(Tương tác)",
    ]

    header_style = ParagraphStyle(
        "HdrStyle",
        fontName="Arial-Bold" if "Arial-Bold" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold",
        fontSize=8,
        alignment=1,  # Center
        leading=10,
        textColor=colors.black,
    )
    cell_style = ParagraphStyle(
        "CellStyle",
        fontName="Arial" if "Arial" in pdfmetrics.getRegisteredFontNames() else "Helvetica",
        fontSize=7.5,
        alignment=1,  # Center
        leading=9,
        textColor=colors.black,
    )
    link_style = ParagraphStyle(
        "LinkStyle",
        fontName="Arial" if "Arial" in pdfmetrics.getRegisteredFontNames() else "Helvetica",
        fontSize=6.5,
        alignment=0,  # Left
        leading=8,
        textColor=colors.HexColor("#1155CC"),
    )

    table_data = [[Paragraph(h.replace("\n", "<br/>"), header_style) for h in headers]]

    if "clean_page" in df.columns:
        page_groups = [(p, grp) for p, grp in df.groupby("clean_page", sort=False)]
    else:
        page_groups = [(page_name, df)]

    month_val = str(month_num)
    col_widths = [42, 98, 72, 280, 48, 58, 68, 42, 72]
    story = []
    CHUNK_SIZE = 16  # Toi da 16 dong tren 1 trang A4 Landscape dam bao 100% khong bao gio tran trang

    for p_name, p_df in page_groups:
        total_grp_rows = len(p_df)
        grp_count_val = str(total_grp_rows)

        # Chia nho thanh tung trang de khong bao gio bi tran trang (LayoutError)
        for start_idx in range(0, total_grp_rows, CHUNK_SIZE):
            chunk_df = p_df.iloc[start_idx : start_idx + CHUNK_SIZE]
            chunk_len = len(chunk_df)

            table_data = [[Paragraph(h.replace("\n", "<br/>"), header_style) for h in headers]]

            for i, (_, r) in enumerate(chunk_df.iterrows()):
                link_url = str(r["clean_link"]).strip()
                link_p = Paragraph(f'<a href="{link_url}">{link_url}</a>', link_style)

                t_val = Paragraph(month_val, cell_style) if i == 0 else ""
                p_val = Paragraph(p_name, cell_style) if i == 0 else ""
                c_val = Paragraph(grp_count_val, cell_style) if i == 0 else ""

                like_p = Paragraph(str(int(r["clean_like"])), cell_style)
                comm_p = Paragraph(str(int(r["clean_comment"])), cell_style)
                eng_p = Paragraph(str(int(r["clean_engagement"])), cell_style)
                view_p = Paragraph(str(int(r["clean_view"])), cell_style)
                inter_p = Paragraph(str(int(r["clean_interaction"])), cell_style)

                table_data.append([t_val, p_val, c_val, link_p, like_p, comm_p, eng_p, view_p, inter_p])

            t = Table(table_data, colWidths=col_widths)
            t_style = [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(f"#{HEADER_FILL_COLOR}")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#000000")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
            ]

            # Merge cell cho 3 cot dau tien trong trang nay
            if chunk_len > 1:
                t_style.append(("SPAN", (0, 1), (0, chunk_len)))
                t_style.append(("SPAN", (1, 1), (1, chunk_len)))
                t_style.append(("SPAN", (2, 1), (2, chunk_len)))
                t_style.append(("VALIGN", (0, 1), (2, chunk_len), "MIDDLE"))
                t_style.append(("ALIGN", (0, 1), (2, chunk_len), "CENTER"))

            t.setStyle(TableStyle(t_style))
            story.append(t)
            story.append(PageBreak())

    if story and isinstance(story[-1], PageBreak):
        story.pop()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(A4),
        leftMargin=25,
        rightMargin=25,
        topMargin=20,
        bottomMargin=20,
    )
    doc.build(story)
    buf.seek(0)
    return buf
