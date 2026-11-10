# -*- coding: utf-8 -*-
"""
Streamlit app: brainstorm brief video Reels + content Reddit (WeMasterTrade /
WeGolden) bang Gemini API, xuat ra file Excel dung form co dinh.

Chay: streamlit run app.py
"""

import json
import re
from pathlib import Path

import streamlit as st
import pandas as pd

from guideline_data import (
    BRANDS,
    GEMINI_MODELS,
    PLATFORMS,
    LANGUAGE_PRESETS,
    CEO_PILLARS,
    CEO_DEFAULT_SERIES_NAME,
    CEO_DEFAULT_TALENT,
    CEO_DEFAULT_DURATION,
)
from gemini_service import GeminiService, resolve_languages
from excel_builder import build_workbook
from event_service import EventContentService
from event_excel_builder import build_event_workbook
from docx_reader import extract_docx_text
from key_pool import parse_keys, call_with_rotation
from ceo_interview_service import CEOInterviewService
from ceo_interview_excel_builder import build_ceo_episode_workbook
from graphic_brief_service import GraphicBriefService, detect_bullet_count, detect_is_stat_promotion
from graphic_brief_excel_builder import build_graphic_brief_workbook
import importlib
import social_report_service
importlib.reload(social_report_service)
from social_report_service import parse_facebook_csvs, build_social_report_excel, build_social_report_pdf

CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config() -> dict:
    cfg = {}
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}
    # Ho tro Streamlit Cloud Secrets
    try:
        if hasattr(st, "secrets"):
            if "api_keys" in st.secrets:
                keys = st.secrets["api_keys"]
                cfg["api_keys"] = list(keys) if isinstance(keys, (list, tuple)) else [k.strip() for k in str(keys).splitlines() if k.strip()]
            if "model" in st.secrets:
                cfg["model"] = str(st.secrets["model"])
    except Exception:
        pass
    return cfg


def save_config(cfg: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    return re.sub(r"[\s_-]+", "_", text)[:40] or "content"


st.set_page_config(page_title="WMT Brief Video & Pictures", page_icon="🎬", layout="wide")

cfg = load_config()

st.title("🎬🖼️ WMT Brief Video & Pictures")
st.caption("Công cụ đa năng: Brainstorm Brief Hình Ảnh (Card/Poster), Kịch bản Video Reel, CEO Interview, Reddit Post & Sự kiện cho WeMasterTrade / WeGolden bằng Gemini API.")

with st.sidebar:
    st.header("⚙️ Cấu hình Gemini")
    keys_raw = st.text_area(
        "Gemini API Keys (mỗi key 1 dòng — lỗi key nào tự chuyển sang key kế tiếp)",
        value="\n".join(cfg.get("api_keys", [])),
        height=180,
        key="api_keys_raw",
    )
    api_keys = parse_keys(keys_raw)
    st.caption(f"Đang có {len(api_keys)} key.")
    model = st.selectbox(
        "Model",
        GEMINI_MODELS,
        index=GEMINI_MODELS.index(cfg.get("model", GEMINI_MODELS[0])) if cfg.get("model") in GEMINI_MODELS else 0,
    )
    remember = st.checkbox("Lưu API keys + model cho lần sau", value=bool(cfg.get("api_keys")))
    if st.button("💾 Lưu cấu hình"):
        if remember:
            save_config({"api_keys": api_keys, "model": model})
            st.success(f"Đã lưu {len(api_keys)} key.")
        else:
            save_config({})
            st.success("Đã xoá cấu hình đã lưu.")

if "key_index" not in st.session_state:
    st.session_state["key_index"] = 0


def _rotated(fn):
    result, idx = call_with_rotation(api_keys, st.session_state["key_index"], fn)
    st.session_state["key_index"] = idx
    return result

content_mode = st.radio(
    "Loại nội dung muốn tạo",
    ["🖼️ Graphic / Card Brief", "📊 Social Monthly Report", "🎬 Video Reel Script", "🎙️ CEO Interview Series", "📅 Event Announcement"],
    horizontal=True,
)

st.divider()

# ==============================================================================
# MODE: GRAPHIC / CARD BRIEF
# ==============================================================================
if content_mode == "🖼️ Graphic / Card Brief":
    st.subheader("1. Chọn brand & kiểu brief")
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        graphic_brand = st.radio("Brand", list(BRANDS.keys()), horizontal=True, key="graphic_brand")
    with g_col2:
        lang_mode = st.radio(
            "Chế độ ngôn ngữ",
            ["Đa ngôn ngữ chuẩn (Gốc EN + KZ + Latam)", "Chỉ tiếng Anh (English Only)", "Tuỳ chọn khác"],
            key="graphic_lang_mode",
        )

    g_col3, g_col4 = st.columns(2)
    with g_col3:
        layout_style_choice = st.radio(
            "Kiểu thẻ hiển thị (Layout Style)",
            [
                "🤖 Tự động phát hiện (Promotion/Bonus -> Thẻ ô số; Tips -> Gạch đầu dòng)",
                "🔢 Thẻ Ô Số Liệu Nổi Bật (Stat Boxes / Promotion Grid)",
                "📋 Thẻ Gạch Đầu Dòng (Checklist / Tips Trading)",
            ],
            key="graphic_layout_choice",
        )
    with g_col4:
        num_points_choice = st.selectbox(
            "Số gạch đầu dòng (áp dụng cho dạng Checklist)",
            ["Tự động phát hiện theo bài gốc (Khuyên dùng)", "4 điểm cố định", "5 điểm cố định", "3 điểm cố định"],
            key="graphic_num_points_choice",
        )

    graphic_final_languages = []
    if lang_mode == "Đa ngôn ngữ chuẩn (Gốc EN + KZ + Latam)":
        graphic_final_languages = ["Kazakh", "Spanish (Latin America)"]
        st.caption("ℹ️ Hệ thống sẽ tạo đồng thời 3 bản thiết kế: **Gốc (English)**, **KZ (Kazakhstan)**, và **Latam (Spanish Latin America)**.")
    elif lang_mode == "Tuỳ chọn khác":
        custom_langs = st.multiselect(
            "Chọn ngôn ngữ bản địa hoá cần thêm",
            options=LANGUAGE_PRESETS,
            default=["Kazakh", "Spanish (Latin America)"],
            key="graphic_custom_langs",
        )
        graphic_final_languages = resolve_languages(custom_langs)
    else:
        st.caption("ℹ️ Chỉ tạo bản thiết kế bằng **Tiếng Anh (English)**.")

    g_col5, _ = st.columns([1, 2])
    with g_col5:
        graphic_num_options = st.number_input("Số phương án concept brainstorm", min_value=1, max_value=4, value=2, key="graphic_num_options")

    st.subheader("2. Nội dung bài viết / Tips / Brief")

    uploaded_graphic_docx = st.file_uploader(
        "Tải lên file Word (.docx) chứa content (nếu có)",
        type=["docx"],
        key="graphic_docx_uploader",
    )
    if uploaded_graphic_docx is not None:
        if st.session_state.get("graphic_docx_last_id") != uploaded_graphic_docx.file_id:
            st.session_state["graphic_docx_last_id"] = uploaded_graphic_docx.file_id
            try:
                st.session_state["graphic_input_text"] = extract_docx_text(uploaded_graphic_docx)
            except Exception as e:
                st.error(f"Không đọc được file Word: {e}")

    graphic_input_content = st.text_area(
        "Nhập nội dung bài viết, tips trading hoặc outline cần tạo brief hình:",
        height=220,
        placeholder=(
            "Ví dụ:\n"
            "Is Your Strategy Built for This Market?\n"
            "A trading strategy that performs well in a trending environment can quickly underperform when the market shifts into consolidation...\n"
            "Before opening a position, you need to evaluate the structural elements in sync:\n"
            "• Market Structure: Identify whether the market is trending or ranging...\n"
            "• Volatility: Adjust expectations...\n"
            "• Strategy Fit: Only deploy positions...\n"
            "• Execution Discipline: Never force a trade...\n"
        ),
        key="graphic_input_text",
    )

    graphic_generate_clicked = st.button("🚀 Generate Graphic Brief", type="primary", use_container_width=True, key="graphic_generate")

    if "graphic_result" not in st.session_state:
        st.session_state["graphic_result"] = None
        st.session_state["graphic_result_brand"] = None
        st.session_state["graphic_result_languages"] = []

    if graphic_generate_clicked:
        if not api_keys:
            st.error("Vui lòng nhập ít nhất 1 Gemini API Key.")
        elif not graphic_input_content.strip():
            st.error("Vui lòng nhập nội dung bài viết / brief.")
        else:
            forced_layout = None
            if "Ô Số Liệu" in layout_style_choice:
                forced_layout = "stat_boxes"
            elif "Gạch Đầu Dòng" in layout_style_choice:
                forced_layout = "checklist"
            else:
                forced_layout = "stat_boxes" if detect_is_stat_promotion(graphic_input_content) else "checklist"

            detected = detect_bullet_count(graphic_input_content)
            if "4" in num_points_choice:
                target_num_points = 4
            elif "5" in num_points_choice:
                target_num_points = 5
            elif "3" in num_points_choice:
                target_num_points = 3
            else:
                target_num_points = detected

            type_desc = "Thẻ ô số liệu (Stat Boxes)" if forced_layout == "stat_boxes" else f"Thẻ checklist ({target_num_points or 'auto'} ý)"
            with st.spinner(f"Đang phân tích & brainstorm brief ({type_desc}) với Gemini..."):
                try:
                    graphic_result = _rotated(lambda k: GraphicBriefService(api_key=k, model=model).generate(
                        brand=graphic_brand,
                        content_input=graphic_input_content,
                        localize_languages=graphic_final_languages,
                        forced_layout_type=forced_layout,
                        num_points=target_num_points,
                        num_options=int(graphic_num_options),
                    ))
                    st.session_state["graphic_result"] = graphic_result
                    st.session_state["graphic_result_brand"] = graphic_brand
                    st.session_state["graphic_result_languages"] = graphic_final_languages
                except Exception as e:
                    st.error(f"Lỗi khi gọi Gemini API: {e}")

    graphic_result = st.session_state.get("graphic_result")
    graphic_result_brand = st.session_state.get("graphic_result_brand")
    graphic_result_languages = st.session_state.get("graphic_result_languages", [])

    if graphic_result:
        st.subheader("3. Kết quả Brief Hình & Visual Concept")

        for idx, opt in enumerate(graphic_result.options, start=1):
            with st.expander(f"✨ {opt.concept_name} — {opt.headline_en}", expanded=(idx == 1)):
                st.markdown(f"### 🎴 Mô Phỏng Thẻ Thiết Kế (Card Visual Mockup)")

                # Chuan bi du lieu the
                cards_data = []
                cards_data.append({
                    "badge": "GỐC",
                    "badge_bg": "#D92D20",
                    "layout_type": opt.layout_type,
                    "title": opt.headline_en,
                    "subtitle": opt.sub_headline_en,
                    "bullets": opt.bullet_points_en,
                    "stat_boxes": opt.stat_boxes_en,
                    "cta": opt.cta_text_en,
                    "badge_number": opt.badge_number,
                })

                for loc in opt.localizations:
                    badge_label = "KZ" if "kazakh" in loc.language.lower() else ("LATAM" if "spanish" in loc.language.lower() or "latam" in loc.language.lower() else loc.language.upper()[:5])
                    cards_data.append({
                        "badge": badge_label,
                        "badge_bg": "#D92D20",
                        "layout_type": opt.layout_type,
                        "title": loc.headline,
                        "subtitle": loc.sub_headline,
                        "bullets": loc.bullet_points,
                        "stat_boxes": loc.stat_boxes,
                        "cta": loc.cta_text,
                        "badge_number": opt.badge_number,
                    })

                # Render HTML Cards
                card_cols = st.columns(len(cards_data))
                for c_idx, c_data in enumerate(cards_data):
                    with card_cols[c_idx]:
                        if c_data["layout_type"] == "stat_boxes" and c_data.get("stat_boxes"):
                            boxes = c_data["stat_boxes"]
                            if len(boxes) == 4:
                                body_content = "<div style='display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:14px 0;'>"
                                for b in boxes:
                                    body_content += f"""<div style='border:1.5px solid #CBD5E1; background:#FFFFFF; border-radius:6px; padding:12px 6px; text-align:center;'>
<div style='font-size:18px; font-weight:800; color:#0F172A; margin-bottom:3px;'>{b.stat_highlight}</div>
<div style='font-size:12px; color:#475569; font-weight:500;'>{b.label}</div>
</div>"""
                                body_content += "</div>"
                            else:
                                body_content = "<div style='display:flex; flex-direction:column; gap:10px; margin:14px 0;'>"
                                for b_idx, b in enumerate(boxes):
                                    offset = "margin-right:24px;" if b_idx % 2 == 0 else "margin-left:24px;"
                                    body_content += f"""<div style='border:1.5px solid #CBD5E1; background:#FFFFFF; border-radius:6px; padding:10px 14px; text-align:center; {offset}'>
<div style='font-size:18px; font-weight:800; color:#0F172A; margin-bottom:2px;'>{b.stat_highlight}</div>
<div style='font-size:12px; color:#475569; font-weight:500;'>{b.label}</div>
</div>"""
                                body_content += "</div>"
                        else:
                            bullets_html = ""
                            for b_idx, b_text in enumerate(c_data["bullets"], start=1):
                                prefix = f"{b_idx}. " if not b_text.strip().startswith(f"{b_idx}.") and not b_text.strip().startswith("•") else ""
                                bullets_html += f"<div style='margin-bottom:10px;'><strong>{prefix}{b_text}</strong></div>"
                            body_content = f"<div style='font-size:13.5px; color:#1E293B; line-height:1.6; padding:0 4px;'>{bullets_html}</div>"

                        badge_num_html = f"<div style='font-size:26px; font-weight:800; color:#B8860B; margin-bottom:2px;'>{c_data['badge_number']}</div>" if c_data["badge_number"] else ""

                        raw_card_html = f"""<div style="margin-bottom:15px; border-radius:8px; overflow:hidden; border:1px solid #E2E8F0; box-shadow:0 3px 6px rgba(0,0,0,0.06);">
<div style="background:{c_data['badge_bg']}; color:#fff; text-align:center; padding:6px 0; font-weight:bold; font-size:12px; letter-spacing:1px;">{c_data['badge']}</div>
<div style="background:#FAFAFA; padding:18px 16px; font-family:'Segoe UI', Roboto, sans-serif; min-height:440px; display:flex; flex-direction:column; justify-content:space-between;">
<div>
<div style="font-size:13px; color:#64748B; font-weight:600; margin-bottom:14px;">Logo</div>
<div style="text-align:center; margin-bottom:18px;">
{badge_num_html}
<div style="color:#B8860B; font-weight:700; font-size:17px; line-height:1.3; margin-bottom:4px;">{c_data['title']}</div>
<div style="color:#0F172A; font-weight:600; font-size:14px; line-height:1.4;">{c_data['subtitle']}</div>
</div>
{body_content}
</div>
<div style="text-align:center; margin-top:20px; padding-top:10px;">
<span style="display:inline-block; border:1px solid #CBD5E1; background:#FFFFFF; color:#0F172A; padding:6px 18px; border-radius:4px; font-size:12.5px; font-weight:600;">{c_data['cta']}</span>
</div>
</div>
</div>"""
                        st.markdown(raw_card_html, unsafe_allow_html=True)

                st.divider()

                # Visual direction details
                v_col1, v_col2 = st.columns(2)
                with v_col1:
                    st.markdown("#### 📐 Ý Tưởng Visual Layout (Bố cục)")
                    st.info(opt.visual_layout_concept)
                    st.markdown("#### ✨ Element Tham Khảo")
                    st.info(opt.element_references)
                with v_col2:
                    st.markdown("#### 🎨 Prompt AI Tạo Hình (Midjourney / Flux / Imagen)")
                    st.code(opt.ai_image_prompt, language="text")
                    st.markdown("#### 📝 Lưu Ý Cho Graphic Designer")
                    st.info(opt.design_notes)

                # Copy raw text quick box
                with st.expander("📋 Xem & Copy dạng văn bản thuần"):
                    full_text_export = []
                    full_text_export.append(f"=== {opt.concept_name} [{opt.layout_type.upper()}] ===")
                    full_text_export.append(f"\n--- [ GỐC (ENGLISH) ] ---")
                    full_text_export.append(f"Logo")
                    full_text_export.append(f"{opt.badge_number + ' ' if opt.badge_number else ''}{opt.headline_en}")
                    full_text_export.append(f"{opt.sub_headline_en}\n")
                    if opt.layout_type == "stat_boxes":
                        full_text_export.append("[ CÁC Ô SỐ LIỆU / BOXES ]")
                        for box in opt.stat_boxes_en:
                            full_text_export.append(f"▪ [{box.stat_highlight}] {box.label}")
                    else:
                        for b in opt.bullet_points_en:
                            full_text_export.append(b)
                    full_text_export.append(f"\nCTA: {opt.cta_text_en}")

                    for loc in opt.localizations:
                        full_text_export.append(f"\n--- [ {loc.language.upper()} ] ---")
                        full_text_export.append(f"Logo")
                        full_text_export.append(f"{opt.badge_number + ' ' if opt.badge_number else ''}{loc.headline}")
                        full_text_export.append(f"{loc.sub_headline}\n")
                        if opt.layout_type == "stat_boxes":
                            full_text_export.append("[ CÁC Ô SỐ LIỆU / BOXES ]")
                            for box in loc.stat_boxes:
                                full_text_export.append(f"▪ [{box.stat_highlight}] {box.label}")
                        else:
                            for b in loc.bullet_points:
                                full_text_export.append(b)
                        full_text_export.append(f"\nCTA: {loc.cta_text}")

                    st.text_area("Toàn bộ text để gửi designer", value="\n".join(full_text_export), height=180, key=f"graphic_text_export_{idx}")

                with st.expander("📊 Copy bảng Brief để dán vào Google Sheets (Ctrl+V)"):
                    st.caption("Bấm biểu tượng 📋 (Copy) bên dưới, mở Google Sheets chọn ô A1 và bấm **Ctrl + V**:")
                    brief_tsv_lines = ["Hạng mục\tGốc (English)"]
                    for loc in opt.localizations:
                        brief_tsv_lines[0] += f"\t{loc.language}"
                    # Headline
                    h_row = f"Headline\t{opt.headline_en}"
                    for loc in opt.localizations:
                        h_row += f"\t{loc.headline}"
                    brief_tsv_lines.append(h_row)
                    # Sub-headline
                    s_row = f"Sub-headline\t{opt.sub_headline_en}"
                    for loc in opt.localizations:
                        s_row += f"\t{loc.sub_headline}"
                    brief_tsv_lines.append(s_row)
                    # Content
                    if opt.layout_type == "stat_boxes":
                        c_en = " | ".join([f"[{b.stat_highlight}] {b.label}" for b in opt.stat_boxes_en])
                        c_row = f"Nội dung (Ô số liệu)\t{c_en}"
                        for loc in opt.localizations:
                            c_loc = " | ".join([f"[{b.stat_highlight}] {b.label}" for b in loc.stat_boxes])
                            c_row += f"\t{c_loc}"
                    else:
                        c_en = " ; ".join(opt.bullet_points_en)
                        c_row = f"Nội dung (Bullets)\t{c_en}"
                        for loc in opt.localizations:
                            c_loc = " ; ".join(loc.bullet_points)
                            c_row += f"\t{c_loc}"
                    brief_tsv_lines.append(c_row)
                    # CTA
                    cta_row = f"CTA Button\t{opt.cta_text_en}"
                    for loc in opt.localizations:
                        cta_row += f"\t{loc.cta_text}"
                    brief_tsv_lines.append(cta_row)
                    # Layout
                    brief_tsv_lines.append(f"Ý tưởng Layout\t\"{opt.visual_layout_idea}\"")
                    # Prompt AI
                    brief_tsv_lines.append(f"Prompt AI\t\"{opt.ai_image_prompt}\"")
                    st.code("\n".join(brief_tsv_lines), language="text")

        excel_buf = build_graphic_brief_workbook(graphic_result_brand, graphic_result.options, languages=graphic_result_languages)
        st.download_button(
            "⬇️ Tải file Excel Graphic Brief",
            data=excel_buf,
            file_name=f"{graphic_result_brand}_graphic_briefs.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

# ==============================================================================
# MODE: SOCIAL MONTHLY REPORT
# ==============================================================================
elif content_mode == "📊 Social Monthly Report":
    st.subheader("📊 Báo Cáo Social Media Hàng Tháng (Facebook Pages)")
    st.caption("Tổng hợp số liệu từ các file CSV export từ Facebook / Meta Business Suite, gộp và khử trùng lặp bài viết, xuất file PDF (A4 Landscape) & Excel chuẩn WeMasterTrade.")

    default_telegram_dir = Path.home() / "Downloads" / "Telegram Desktop"
    sample_files = []
    if default_telegram_dir.exists():
        sample_files = list(default_telegram_dir.glob("*2026*.csv"))

    if "social_report_raw_files" not in st.session_state:
        st.session_state["social_report_raw_files"] = []

    st.markdown("#### 1. Nạp dữ liệu CSV")
    col_u1, col_u2 = st.columns([3, 2])
    with col_u1:
        uploaded_csvs = st.file_uploader(
            "Tải lên 1 hoặc nhiều file CSV export từ Facebook Page Analytics:",
            type=["csv"],
            accept_multiple_files=True,
            key="social_csv_uploader",
        )
    with col_u2:
        st.markdown("**File mẫu có sẵn trên máy:**")
        if sample_files:
            st.info(f"Tìm thấy {len(sample_files)} file CSV trong thư mục Downloads/Telegram Desktop.")
            if st.button("📂 Nạp nhanh 2 file mẫu từ Telegram Desktop", use_container_width=True):
                st.session_state["social_report_raw_files"] = [str(p) for p in sample_files[:2]]
                st.success("Đã nạp file mẫu thành công!")
        else:
            st.caption("Bạn có thể tải lên file CSV trực tiếp từ máy tính của mình.")

    sources_to_parse = []
    if uploaded_csvs:
        sources_to_parse.extend(uploaded_csvs)
    elif st.session_state.get("social_report_raw_files"):
        sources_to_parse.extend(st.session_state["social_report_raw_files"])

    if sources_to_parse:
        raw_df = parse_facebook_csvs(sources_to_parse)
        if raw_df.empty:
            st.warning("Không tìm thấy dữ liệu bài viết hợp lệ trong các file CSV đã chọn.")
        else:
            st.success(f"✅ Đã xử lý & khử trùng lặp: Tổng cộng **{len(raw_df)}** bài viết.")
            
            st.divider()
            st.markdown("#### 2. Bộ lọc & Thiết lập Báo Cáo")
            
            available_pages = sorted([p for p in raw_df["clean_page"].unique() if p])
            available_months = sorted([int(m) for m in raw_df["report_month"].unique() if pd.notna(m)])
            available_years = sorted([int(y) for y in raw_df["report_year"].unique() if pd.notna(y)])

            ALL_PAGES_OPTION = "🌟 Tất cả các Trang (Xuất chung)"
            page_select_options = [ALL_PAGES_OPTION] + available_pages if len(available_pages) > 1 else available_pages

            def _fmt_page_option(opt):
                if opt == ALL_PAGES_OPTION:
                    return f"{opt} — Tổng {len(raw_df)} bài"
                cnt = len(raw_df[raw_df["clean_page"] == opt])
                return f"{opt} ({cnt} bài)"

            c_f1, c_f2, c_f3, c_f4 = st.columns(4)
            with c_f1:
                sel_page = st.selectbox(
                    "Chọn Trang (Page):",
                    page_select_options,
                    format_func=_fmt_page_option,
                    key="report_sel_page"
                )
            with c_f2:
                sel_month = st.selectbox(
                    "Chọn Tháng:",
                    available_months,
                    format_func=lambda m: f"Tháng {m}",
                    key="report_sel_month",
                )
            with c_f3:
                sel_year = st.selectbox("Năm:", available_years if available_years else [2026], key="report_sel_year")
            with c_f4:
                author_name = st.text_input("Tên người báo cáo (Author):", value="Carwyn", key="report_author_name")

            if sel_page == ALL_PAGES_OPTION:
                filtered_df = raw_df[raw_df["report_month"] == sel_month].copy()
                page_abbr = "ALL_PAGES"
                display_page_title = "Tất cả các Trang"
            else:
                filtered_df = raw_df[(raw_df["clean_page"] == sel_page) & (raw_df["report_month"] == sel_month)].copy()
                page_code_map = {
                    "Wemastertrade AU": "WMT_AU",
                    "Wemastertrade Kazakhstan": "WMT_KZ",
                    "Wemastertrade Singapore": "WMT_SG",
                }
                page_abbr = page_code_map.get(sel_page, slugify(sel_page).upper())
                display_page_title = sel_page

            if "report_year" in filtered_df.columns and sel_year:
                filtered_df = filtered_df[filtered_df["report_year"] == sel_year]

            if "parsed_dt" in filtered_df.columns:
                filtered_df = filtered_df.sort_values(by="parsed_dt", ascending=True)

            month_names_en = {
                1: "January", 2: "February", 3: "March", 4: "April",
                5: "May", 6: "June", 7: "July", 8: "August",
                9: "September", 10: "October", 11: "November", 12: "December"
            }
            month_name_en = month_names_en.get(sel_month, f"Month_{sel_month}")
            base_file_name = f"Report_social_WeMasterTrade_{month_name_en}_{sel_year}_{page_abbr}_{author_name.strip()}"

            st.divider()
            st.markdown(f"#### 3. Tổng quan chỉ số: **{display_page_title}** — Tháng {sel_month}/{sel_year}")

            total_posts = len(filtered_df)
            total_likes = int(filtered_df["clean_like"].sum()) if total_posts else 0
            total_comments = int(filtered_df["clean_comment"].sum()) if total_posts else 0
            total_eng = int(filtered_df["clean_engagement"].sum()) if total_posts else 0
            total_views = int(filtered_df["clean_view"].sum()) if total_posts else 0
            total_inter = int(filtered_df["clean_interaction"].sum()) if total_posts else 0

            m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)
            m_col1.metric("Số bài đăng", f"{total_posts}")
            m_col2.metric("Lượt Like", f"{total_likes:,}")
            m_col3.metric("Comments", f"{total_comments:,}")
            m_col4.metric("Engagement", f"{total_eng:,}")
            m_col5.metric("Tổng Views", f"{total_views:,}")
            m_col6.metric("Tương tác", f"{total_inter:,}")

            st.markdown("#### 4. Xem trước Bảng Báo Cáo (Preview)")
            if total_posts == 0:
                st.warning(f"Không có bài viết nào của page '{sel_page}' trong tháng {sel_month}/{sel_year}.")
            else:
                if "clean_page" in filtered_df.columns:
                    page_grps = [(p, grp) for p, grp in filtered_df.groupby("clean_page", sort=False)]
                else:
                    page_grps = [(display_page_title, filtered_df)]

                preview_rows = []
                for p_name, p_df in page_grps:
                    grp_len = len(p_df)
                    for idx, (_, r) in enumerate(p_df.iterrows()):
                        link_u = str(r["clean_link"]).strip()
                        first_col_tags = ""
                        if idx == 0:
                            first_col_tags = f"""<td rowspan="{grp_len}" style="text-align:center; vertical-align:middle; font-weight:600; border:1px solid #999; padding:6px;">{sel_month}</td>
<td rowspan="{grp_len}" style="text-align:center; vertical-align:middle; font-weight:600; border:1px solid #999; padding:6px;">{p_name}</td>
<td rowspan="{grp_len}" style="text-align:center; vertical-align:middle; font-weight:600; border:1px solid #999; padding:6px;">{grp_len}</td>"""
                        row_html = f"""<tr>
{first_col_tags}
<td style="border:1px solid #999; padding:6px; font-size:12px;"><a href="{link_u}" target="_blank" style="color:#1155CC; text-decoration:underline;">{link_u}</a></td>
<td style="text-align:center; border:1px solid #999; padding:6px;">{int(r['clean_like'])}</td>
<td style="text-align:center; border:1px solid #999; padding:6px;">{int(r['clean_comment'])}</td>
<td style="text-align:center; border:1px solid #999; padding:6px;">{int(r['clean_engagement'])}</td>
<td style="text-align:center; border:1px solid #999; padding:6px;">{int(r['clean_view'])}</td>
<td style="text-align:center; border:1px solid #999; padding:6px;">{int(r['clean_interaction'])}</td>
</tr>"""
                        preview_rows.append(row_html)

                tbody_content = "\n".join(preview_rows)
                html_table = f"""<div style="max-height: 480px; overflow-y: auto; border: 1px solid #ccc; margin-bottom: 20px;">
<table style="width:100%; border-collapse:collapse; font-family:Arial, sans-serif; font-size:13px;">
<thead>
<tr style="background-color:#FFF2CC; color:#000; font-weight:bold; height:38px;">
<th style="border:1px solid #999; padding:8px; width:60px;">Tháng</th>
<th style="border:1px solid #999; padding:8px; width:150px;">Page</th>
<th style="border:1px solid #999; padding:8px; width:110px;">Số bài đăng trong tháng</th>
<th style="border:1px solid #999; padding:8px;">Link bài</th>
<th style="border:1px solid #999; padding:8px; width:75px;">Lượt Like</th>
<th style="border:1px solid #999; padding:8px; width:80px;">Comments</th>
<th style="border:1px solid #999; padding:8px; width:95px;">Engagement</th>
<th style="border:1px solid #999; padding:8px; width:65px;">View</th>
<th style="border:1px solid #999; padding:8px; width:100px;">Interaction (Tương tác)</th>
</tr>
</thead>
<tbody>
{tbody_content}
</tbody>
</table>
</div>"""
                st.markdown(html_table, unsafe_allow_html=True)

                st.divider()
                st.markdown("#### 5. Xuất file Báo Cáo")
                
                exp_col1, exp_col2 = st.columns(2)
                with exp_col1:
                    try:
                        pdf_buf = build_social_report_pdf(filtered_df, sel_month, sel_page)
                        st.download_button(
                            "📄 Tải file PDF Báo Cáo (.pdf)",
                            data=pdf_buf,
                            file_name=f"{base_file_name}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.error(f"Lỗi khi tạo file PDF: {e}")
                with exp_col2:
                    try:
                        excel_buf = build_social_report_excel(filtered_df, sel_month, sel_page)
                        st.download_button(
                            "📊 Tải file Excel Báo Cáo (.xlsx)",
                            data=excel_buf,
                            file_name=f"{base_file_name}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.error(f"Lỗi khi tạo file Excel: {e}")

                st.divider()
                st.markdown("#### 📋 Dữ liệu để Copy trực tiếp vào Google Sheets")
                st.caption("Chỉ cần nhấn biểu tượng **📋 (Copy)** ở góc trên bên phải khung bên dưới, sau đó mở Google Sheet chọn ô **A1** (hoặc bất kỳ) và nhấn **Ctrl + V** là toàn bộ bảng dữ liệu sẽ được phân tách thành từng cột, từng hàng ngay lập tức!")

                tsv_lines_visual = ["Tháng\tPage\tSố bài đăng trong tháng\tLink bài\tLượt Like\tComments\tEngagement\tView\tInteraction (Tương tác)"]
                for p_name, p_df in page_grps:
                    grp_len = len(p_df)
                    for idx, (_, r) in enumerate(p_df.iterrows()):
                        m_val = str(sel_month) if idx == 0 else ""
                        p_val = str(p_name) if idx == 0 else ""
                        c_val = str(grp_len) if idx == 0 else ""
                        tsv_lines_visual.append(f"{m_val}\t{p_val}\t{c_val}\t{r['clean_link']}\t{int(r['clean_like'])}\t{int(r['clean_comment'])}\t{int(r['clean_engagement'])}\t{int(r['clean_view'])}\t{int(r['clean_interaction'])}")
                tsv_text_visual = "\n".join(tsv_lines_visual)

                tsv_lines_all = ["Tháng\tPage\tSố bài đăng trong tháng\tLink bài\tLượt Like\tComments\tEngagement\tView\tInteraction (Tương tác)"]
                for p_name, p_df in page_grps:
                    grp_len = len(p_df)
                    for idx, (_, r) in enumerate(p_df.iterrows()):
                        tsv_lines_all.append(f"{sel_month}\t{p_name}\t{grp_len}\t{r['clean_link']}\t{int(r['clean_like'])}\t{int(r['clean_comment'])}\t{int(r['clean_engagement'])}\t{int(r['clean_view'])}\t{int(r['clean_interaction'])}")
                tsv_text_all = "\n".join(tsv_lines_all)

                sheet_copy_mode = st.radio(
                    "Định dạng copy vào Google Sheet:",
                    [
                        "Dạng chuẩn form (Dòng đầu ghi Tháng/Page/Số bài, các dòng dưới để trống)",
                        "Dạng lặp lại dữ liệu (Mỗi dòng đều ghi rõ Tháng & Page, tiện để Sort/Filter)",
                    ],
                    key="sheet_copy_mode",
                    horizontal=True,
                )
                chosen_tsv = tsv_text_visual if "chuẩn form" in sheet_copy_mode else tsv_text_all
                st.code(chosen_tsv, language="text")
    else:
        st.info("👆 Vui lòng tải lên file CSV hoặc bấm 'Nạp nhanh file mẫu' ở trên để bắt đầu tạo báo cáo.")

# ==============================================================================
# MODE 1: VIDEO REEL SCRIPT
# ==============================================================================
elif content_mode == "🎬 Video Reel Script":
    st.subheader("1. Chọn brand & bối cảnh")
    col1, col2, col3 = st.columns(3)
    with col1:
        brand = st.radio("Brand", list(BRANDS.keys()), horizontal=True, key="reel_brand")
    with col2:
        platform = st.selectbox("Nền tảng đăng", PLATFORMS, key="reel_platform")
    with col3:
        num_options = st.number_input("Số phương án brainstorm", min_value=1, max_value=4, value=2, key="reel_num_options")

    brand_cfg = BRANDS[brand]

    col4, col5 = st.columns(2)
    with col4:
        region = st.text_input(
            "Khu vực / thị trường mục tiêu",
            value="Latin America" if brand == "WeMasterTrade" else "Vietnam",
            help="Ảnh hưởng tới ngoại hình AI speaker phải adapt theo người bản xứ khu vực này.",
            key="reel_region",
        )
    with col5:
        selected_languages = []
        custom_languages_raw = ""
        if brand_cfg["localizable"]:
            default_langs = ["Spanish (Latin America)"] if region.lower().startswith("latin") else []
            selected_languages = st.multiselect(
                "Ngôn ngữ bản địa hoá (cột Voice adapt / Text adapt)",
                options=LANGUAGE_PRESETS,
                default=default_langs,
                help="Voiceover/On-screen Text gốc luôn có sẵn bằng tiếng Anh. Chọn thêm ngôn ngữ ở đây để có thêm cột bản địa hoá song song. Có thể chọn nhiều ngôn ngữ cùng lúc.",
            )
            custom_languages_raw = st.text_input(
                "Ngôn ngữ khác (không có trong danh sách trên, cách nhau bằng dấu phẩy)",
                value="",
                placeholder="Ví dụ: Mongolian, Turkish",
            )
        else:
            st.text_input(
                "Ngôn ngữ bản địa hoá",
                value="(không áp dụng cho WeGolden)",
                disabled=True,
            )

        custom_languages = [x.strip() for x in custom_languages_raw.split(",") if x.strip()]
        raw_languages = selected_languages + custom_languages
        final_languages = resolve_languages(raw_languages)

        auto_added = [lang for lang in final_languages if lang not in raw_languages]
        if auto_added:
            st.caption(f"➕ Tự động thêm ngôn ngữ liên quan: {', '.join(auto_added)}")
        if final_languages:
            st.caption(f"Cột sẽ tạo: Voice/Text adapt cho — {', '.join(final_languages)} (cộng thêm cột tiếng Anh gốc mặc định).")

    if brand_cfg["mascot"]:
        st.info("Brand WeGolden: Gemini sẽ tự lồng ghép mascot vào 2-3 scene trong Visual Direction.")

    st.subheader("2. Brief / ý tưởng")

    focus_on_numbers = st.checkbox(
        "📊 Tập trung vào số liệu cụ thể (ít lý thuyết marketing)",
        key="reel_focus_numbers",
        help=(
            "Gemini sẽ tự đọc kỹ brief/file bạn đưa vào, tự tìm mọi số liệu cụ thể (tiền, %, cấp độ, ngày, "
            "khối lượng...) và xây kịch bản xoay quanh các số đó. Claim nào không có số liệu đi kèm, hoặc "
            "được ghi chú là 'chưa xác minh'/'chưa có số liệu cụ thể', sẽ bị bỏ qua — không tự bịa số liệu."
        ),
    )

    uploaded_brief_docx = st.file_uploader(
        "Hoặc tải lên file Word (.docx) chứa brief — nội dung sẽ tự điền vào ô bên dưới",
        type=["docx"],
        key="reel_brief_docx_uploader",
    )
    if uploaded_brief_docx is not None:
        if st.session_state.get("reel_brief_docx_last_id") != uploaded_brief_docx.file_id:
            st.session_state["reel_brief_docx_last_id"] = uploaded_brief_docx.file_id
            try:
                st.session_state["reel_brief_text"] = extract_docx_text(uploaded_brief_docx)
            except Exception as e:
                st.error(f"Không đọc được file Word: {e}")

    user_brief = st.text_area(
        "Nhập ý tưởng brief (giống như bạn brief cho một creative), hoặc chỉnh lại nội dung đã tải từ file Word ở trên",
        height=200,
        placeholder=(
            "Ví dụ: Brief cho tôi 1 video reel cho facebook với chủ đề là tips trading cho "
            "người mới gia nhập vào thị trường trading, dạng review các gói sản phẩm "
            "(challenge/các chương trình trong gói instant) + chương trình promotion, về "
            "education như: tips trading / tâm lý của traders."
        ),
        key="reel_brief_text",
    )

    generate_clicked = st.button("🚀 Generate", type="primary", use_container_width=True, key="reel_generate")

    if "result" not in st.session_state:
        st.session_state["result"] = None
        st.session_state["result_brand"] = None
        st.session_state["result_languages"] = []

    if generate_clicked:
        if not api_keys:
            st.error("Vui lòng nhập ít nhất 1 Gemini API Key.")
        elif not user_brief.strip():
            st.error("Vui lòng nhập brief / ý tưởng.")
        else:
            with st.spinner("Đang brainstorm với Gemini..."):
                try:
                    result = _rotated(lambda k: GeminiService(api_key=k, model=model).generate(
                        brand=brand,
                        platform=platform,
                        region=region,
                        localize_languages=final_languages,
                        user_brief=user_brief,
                        num_options=int(num_options),
                        focus_on_numbers=focus_on_numbers,
                    ))
                    st.session_state["result"] = result
                    st.session_state["result_brand"] = brand
                    st.session_state["result_languages"] = final_languages
                except Exception as e:
                    st.error(f"Lỗi khi gọi Gemini API: {e}")

    result = st.session_state.get("result")
    result_brand = st.session_state.get("result_brand")
    result_languages = st.session_state.get("result_languages", [])

    if result:
        st.subheader("3. Kết quả")
        for i, opt in enumerate(result.options, start=1):
            with st.expander(f"Phương án {i}: {opt.topic}", expanded=(i == 1)):
                st.markdown(f"**Angle:** {opt.angle_vi}")
                st.markdown(f"**Target Audience:** {opt.target_audience}")
                st.markdown(f"**Viewer Takeaway:** {opt.viewer_takeaway}")
                st.markdown(f"**Video Length:** {opt.video_length}")
                st.markdown(f"**Format:** {opt.format}")
                st.markdown(f"**Tone:** {opt.tone}")
                st.markdown(f"**Key Message:** {opt.key_message}")
                st.markdown(f"**AI Speaker Note:** {opt.ai_speaker_note}")
                st.markdown("**Scenes:**")
                for sc in opt.scenes:
                    st.markdown(f"- `{sc.time}` **{sc.scene}** — {sc.voiceover}")

        excel_buf = build_workbook(result_brand, result.options, languages=result_languages)
        first_topic = slugify(result.options[0].topic) if result.options else "reel"
        st.download_button(
            "⬇️ Tải file Excel",
            data=excel_buf,
            file_name=f"{result_brand}_{first_topic}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

# ==============================================================================
# MODE 2: CEO INTERVIEW SERIES (nguoi that / CEO thay AI speaker)
# ==============================================================================
elif content_mode == "🎙️ CEO Interview Series":
    st.subheader("1. Thông tin series & tập")
    col1, col2 = st.columns(2)
    with col1:
        ceo_series_name = st.text_input("Series name", value=CEO_DEFAULT_SERIES_NAME, key="ceo_series_name")
        ceo_talent = st.text_input("Talent (CEO/người nói)", value=CEO_DEFAULT_TALENT, key="ceo_talent")
        ceo_episode_label = st.text_input("Mã tập (dùng đặt tên sheet, vd EP03)", value="EP03", key="ceo_episode_label")
    with col2:
        ceo_pillar = st.selectbox("Pillar (core value)", list(CEO_PILLARS.keys()), key="ceo_pillar")
        st.caption(f"💡 {CEO_PILLARS[ceo_pillar]}")
        ceo_duration = st.text_input("Duration", value=CEO_DEFAULT_DURATION, key="ceo_duration")
        ceo_num_options = st.number_input("Số phương án brainstorm", min_value=1, max_value=4, value=2, key="ceo_num_options")

    ceo_topic_title = st.text_input(
        "Topic/Angle của tập này",
        placeholder="Ví dụ: How to Choose a Gold Trading Platform: Trust Signals & Red Flags",
        key="ceo_topic_title",
    )
    ceo_episode_key = st.text_area(
        "Episode Key (bài học/thông điệp cốt lõi tập này PHẢI truyền tải — nên nêu rõ nó giải quyết key của tập trước như thế nào)",
        height=100,
        key="ceo_episode_key",
    )
    ceo_next_episode_key = st.text_input(
        "Next Episode Key (câu hỏi mở dẫn sang tập tiếp theo)",
        key="ceo_next_episode_key",
    )

    st.subheader("2. Nội dung nguồn / ghi chú bổ sung (không bắt buộc)")
    ceo_uploaded_docx = st.file_uploader(
        "Tải lên file Word (.docx) — nội dung sẽ tự điền vào ô bên dưới",
        type=["docx"],
        key="ceo_source_docx_uploader",
    )
    if ceo_uploaded_docx is not None:
        if st.session_state.get("ceo_source_docx_last_id") != ceo_uploaded_docx.file_id:
            st.session_state["ceo_source_docx_last_id"] = ceo_uploaded_docx.file_id
            try:
                st.session_state["ceo_source_content"] = extract_docx_text(ceo_uploaded_docx)
            except Exception as e:
                st.error(f"Không đọc được file Word: {e}")

    ceo_source_content = st.text_area(
        "Caption/nội dung xã hội đã soạn cho tập này, hoặc ghi chú thêm để bám sát giọng điệu",
        height=180,
        key="ceo_source_content",
    )

    ceo_generate_clicked = st.button("🚀 Generate", type="primary", use_container_width=True, key="ceo_generate")

    if "ceo_result" not in st.session_state:
        st.session_state["ceo_result"] = None
        st.session_state["ceo_result_label"] = None

    if ceo_generate_clicked:
        if not api_keys:
            st.error("Vui lòng nhập ít nhất 1 Gemini API Key.")
        elif not ceo_topic_title.strip() or not ceo_episode_key.strip() or not ceo_next_episode_key.strip():
            st.error("Vui lòng nhập đủ Topic/Angle, Episode Key và Next Episode Key.")
        else:
            with st.spinner("Đang brainstorm với Gemini..."):
                try:
                    ceo_result = _rotated(lambda k: CEOInterviewService(api_key=k, model=model).generate(
                        pillar=ceo_pillar,
                        topic_title=ceo_topic_title,
                        episode_key_context=ceo_episode_key,
                        next_episode_key=ceo_next_episode_key,
                        source_content=ceo_source_content,
                        series_name=ceo_series_name,
                        talent=ceo_talent,
                        duration=ceo_duration,
                        num_options=int(ceo_num_options),
                    ))
                    st.session_state["ceo_result"] = ceo_result
                    st.session_state["ceo_result_label"] = ceo_episode_label
                except Exception as e:
                    st.error(f"Lỗi khi gọi Gemini API: {e}")

    ceo_result = st.session_state.get("ceo_result")
    ceo_result_label = st.session_state.get("ceo_result_label")

    if ceo_result:
        st.subheader("3. Kết quả")
        for i, opt in enumerate(ceo_result.episodes, start=1):
            with st.expander(f"Phương án {i}", expanded=(i == 1)):
                for sec in opt.sections:
                    st.markdown(f"**{sec.section}**")
                    if sec.ceo_script:
                        st.markdown(f"CEO: {sec.ceo_script}")
                    if sec.onscreen_text:
                        st.markdown(f"On-screen: {sec.onscreen_text}")

        excel_buf = build_ceo_episode_workbook(ceo_result_label, ceo_result.episodes)
        st.download_button(
            "⬇️ Tải file Excel",
            data=excel_buf,
            file_name=f"WeGolden_InsideTheGoldenMind_{ceo_result_label}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

# ==============================================================================
# MODE: EVENT ANNOUNCEMENT
# ==============================================================================
elif content_mode == "📅 Event Announcement":
    st.subheader("1. Chọn brand & thị trường")
    col1, col2, col3 = st.columns(3)
    with col1:
        event_brand = st.radio("Brand", list(BRANDS.keys()), horizontal=True, key="event_brand")
    with col2:
        event_region = st.text_input("Khu vực / thị trường mục tiêu", value="Kazakhstan", key="event_region")
    with col3:
        event_num_posts = st.number_input("Số bài muốn tạo", min_value=1, max_value=10, value=3, key="event_num_posts")

    event_selected_languages = st.multiselect(
        "Ngôn ngữ bản địa hoá (Headline/Content sẽ có thêm cột song song với bản tiếng Anh gốc)",
        options=LANGUAGE_PRESETS,
        default=["Kazakh"] if event_region.strip().lower() == "kazakhstan" else [],
        key="event_languages",
    )
    event_custom_languages_raw = st.text_input(
        "Ngôn ngữ khác (không có trong danh sách trên, cách nhau bằng dấu phẩy)",
        value="",
        key="event_custom_languages",
    )
    event_custom_languages = [x.strip() for x in event_custom_languages_raw.split(",") if x.strip()]
    event_raw_languages = event_selected_languages + event_custom_languages
    event_final_languages = resolve_languages(event_raw_languages)
    event_auto_added = [lang for lang in event_final_languages if lang not in event_raw_languages]
    if event_auto_added:
        st.caption(f"➕ Tự động thêm ngôn ngữ liên quan: {', '.join(event_auto_added)} (bỏ chọn ngôn ngữ gốc ở trên nếu không cần).")

    st.subheader("2. Thông tin sự kiện")
    event_info = st.text_area(
        "Paste toàn bộ thông tin sự kiện (tên, ngày giờ, địa điểm, đăng ký, hoạt động, giải thưởng, link đăng ký...)",
        height=220,
        placeholder=(
            "Ví dụ: Tên sự kiện: WeMasterTrade Kazakhstan Trading Meetup 2026\n"
            "Ngày: 28/8/2026, 12:30–17:00, tại Hilton Garden Inn Astana\n"
            "Đăng ký: 13/8 – 27/8/2026\n"
            "Link đăng ký: https://...\n"
            "Các hoạt động chính, giải thưởng lucky draw..."
        ),
    )

    event_generate_clicked = st.button("🚀 Generate", type="primary", use_container_width=True, key="event_generate")

    if "event_result" not in st.session_state:
        st.session_state["event_result"] = None
        st.session_state["event_result_brand"] = None
        st.session_state["event_result_languages"] = []

    if event_generate_clicked:
        if not api_keys:
            st.error("Vui lòng nhập ít nhất 1 Gemini API Key.")
        elif not event_info.strip():
            st.error("Vui lòng nhập thông tin sự kiện.")
        else:
            with st.spinner("Đang brainstorm với Gemini..."):
                try:
                    event_result = _rotated(lambda k: EventContentService(api_key=k, model=model).generate(
                        brand=event_brand,
                        region=event_region,
                        localize_languages=event_final_languages,
                        event_info=event_info,
                        num_posts=int(event_num_posts),
                    ))
                    st.session_state["event_result"] = event_result
                    st.session_state["event_result_brand"] = event_brand
                    st.session_state["event_result_languages"] = event_final_languages
                except Exception as e:
                    st.error(f"Lỗi khi gọi Gemini API: {e}")

    event_result = st.session_state.get("event_result")
    event_result_brand = st.session_state.get("event_result_brand")
    event_result_languages = st.session_state.get("event_result_languages", [])

    if event_result:
        st.subheader("3. Kết quả")
        for i, post in enumerate(event_result.posts, start=1):
            with st.expander(f"Bài {i}: {post.headline_en}", expanded=(i == 1)):
                st.markdown(f"**Angle:** {post.angle_vi}")
                st.markdown(f"**Hashtags:** {post.hashtags}")
                st.markdown(f"**Image:** {post.image_note}")
                st.markdown(f"**Lưu ý:** {post.note}")
                st.text_area("Content (EN)", value=post.content_en, height=180, key=f"event_content_en_{i}", disabled=True)
                for loc in post.localizations:
                    st.text_area(f"Content ({loc.language})", value=loc.content_adapt, height=180, key=f"event_content_{loc.language}_{i}", disabled=True)

        excel_buf = build_event_workbook(event_result_brand, event_result.posts, languages=event_result_languages)
        st.download_button(
            "⬇️ Tải file Excel",
            data=excel_buf,
            file_name=f"{event_result_brand}_event_announcement.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
