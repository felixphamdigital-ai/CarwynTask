# -*- coding: utf-8 -*-
"""
Build file Excel xuat Brief Thiet Ke Hinh Anh / Card Post cho WeMasterTrade & WeGolden.
Dinh dang dep mat, co cot ro rang cho Goc (EN) va cac ban ban dia hoa (KZ, Latam...),
kem mo ta Visual Layout, Element tham khao va Prompt AI.
Ho tro ca 2 layout: Checklist va Stat Boxes.
"""

from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from guideline_data import BRANDS

FONT_NAME = "Be Vietnam Pro"


def _fill(hex_color: str):
    clean_hex = hex_color.replace("#", "")
    return PatternFill(start_color=clean_hex, end_color=clean_hex, fill_type="solid")


def _thin_border():
    thin = Side(border_style="thin", color="D9D9D9")
    return Border(left=thin, right=thin, top=thin, bottom=thin)


def _format_card_text(
    headline: str,
    sub_headline: str,
    bullets: list = None,
    stat_boxes: list = None,
    cta: str = "",
    badge_number: str = "",
) -> str:
    parts = ["[ Logo ]"]
    if badge_number:
        parts.append(f"[{badge_number}] {headline}")
    else:
        parts.append(headline)
    if sub_headline:
        parts.append(sub_headline)
    parts.append("")  # Empty line

    if stat_boxes:
        parts.append("[ CÁC KHỐI SỐ LIỆU / STAT BOXES ]")
        for box in stat_boxes:
            highlight = getattr(box, "stat_highlight", "") if hasattr(box, "stat_highlight") else str(box)
            lbl = getattr(box, "label", "") if hasattr(box, "label") else ""
            parts.append(f"▪ [{highlight}] {lbl}")
    elif bullets:
        for b in bullets:
            parts.append(b)

    parts.append("")  # Empty line
    parts.append(f"CTA: {cta}")
    return "\n".join(parts)


def build_graphic_brief_workbook(brand: str, options: list, languages: list = None) -> BytesIO:
    """options: list of GraphicBriefOption (pydantic) da generate tu Gemini."""
    cfg = BRANDS.get(brand, BRANDS["WeMasterTrade"])
    wb = Workbook()
    ws = wb.active
    ws.title = "Graphic Briefs"

    # Xac dinh danh sach cot
    lang_headers = []
    if languages:
        for l in languages:
            if "kazakh" in l.lower():
                lang_headers.append((f"Bản địa hoá - KZ ({l})", l))
            elif "spanish" in l.lower() or "latam" in l.lower():
                lang_headers.append((f"Bản địa hoá - Latam ({l})", l))
            else:
                lang_headers.append((f"Bản địa hoá - {l}", l))

    headers = ["No", "Concept", "Kiểu Thẻ", "Thẻ Gốc (English)"]
    for lh, _ in lang_headers:
        headers.append(lh)
    headers.extend([
        "Ý Tưởng Visual Layout (Bố cục)",
        "Element Tham Khảo",
        "Prompt AI Tạo Hình (Midjourney / Flux)",
        "Lưu Ý Designer"
    ])

    widths = [6, 24, 16, 45]
    for _ in lang_headers:
        widths.append(45)
    widths.extend([40, 30, 45, 30])

    # Header styling
    for col_idx, (h, w) in enumerate(zip(headers, widths), start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = w
        c = ws.cell(row=1, column=col_idx, value=h)
        c.font = Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")
        c.fill = _fill(cfg.get("header_fill", "#1F4E79"))
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    ws.row_dimensions[1].height = 28

    row = 2
    for idx, opt in enumerate(options, start=1):
        layout_name = "Thẻ Số Liệu (Boxes)" if opt.layout_type == "stat_boxes" else "Thẻ Checklist (Gạch đầu dòng)"
        en_text = _format_card_text(
            headline=opt.headline_en,
            sub_headline=opt.sub_headline_en,
            bullets=opt.bullet_points_en,
            stat_boxes=opt.stat_boxes_en if opt.layout_type == "stat_boxes" else None,
            cta=opt.cta_text_en,
            badge_number=opt.badge_number,
        )

        row_values = [idx, opt.concept_name, layout_name, en_text]

        # Map localizations
        loc_map = {loc.language.lower(): loc for loc in opt.localizations}
        for _, l_name in lang_headers:
            matched_loc = None
            for key, loc_obj in loc_map.items():
                if l_name.lower() in key or key in l_name.lower():
                    matched_loc = loc_obj
                    break
            if matched_loc:
                loc_text = _format_card_text(
                    headline=matched_loc.headline,
                    sub_headline=matched_loc.sub_headline,
                    bullets=matched_loc.bullet_points,
                    stat_boxes=matched_loc.stat_boxes if opt.layout_type == "stat_boxes" else None,
                    cta=matched_loc.cta_text,
                    badge_number=opt.badge_number,
                )
                row_values.append(loc_text)
            else:
                row_values.append("")

        row_values.extend([
            opt.visual_layout_concept,
            opt.element_references,
            opt.ai_image_prompt,
            opt.design_notes,
        ])

        for col_idx, val in enumerate(row_values, start=1):
            c = ws.cell(row=row, column=col_idx, value=val)
            c.font = Font(name=FONT_NAME, size=10)
            c.border = _thin_border()
            c.alignment = Alignment(wrap_text=True, vertical="top", horizontal="left")

        # Can giua cot No va Kieu The
        ws.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical="top", horizontal="center")
        ws.cell(row=row, column=3).alignment = Alignment(wrap_text=True, vertical="top", horizontal="center")
        ws.row_dimensions[row].height = 220
        row += 1

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
