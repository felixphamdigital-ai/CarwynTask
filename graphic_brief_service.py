# -*- coding: utf-8 -*-
"""
Goi Gemini API de brainstorm Brief Thiet Ke Hinh Anh / Poster / Card Social Media
theo dung chuan form WeMasterTrade & WeGolden:
- Ho tro 2 KIEU HIEN THI:
  1. Checklist / Tips (Dang gach dau dong 3-5 y co dong 2-4 tu)
  2. Stat Boxes / Promotion Grid (Dang cac o hop chu so to noi bat: 20%, 5K USD, 60 days, ECN & Standard...)
- Sub-headline: GIOI HAN TOI DA 6 TU (MAX 6 WORDS).
- CTA Compliance: TUYET DOI KHONG dung 'earning', 'earn', 'money', 'profit share', 'guarantee', 'commit', '$'.
- 3 cot song song: Goc (EN) - KZ (Kazakhstan) - Latam (Spanish).
"""

import re
from typing import List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

from guideline_data import BRANDS

BANNED_CTA_PATTERNS = ["earning", "earn", "money", "profit share", "profit", "guarantee", "commit", "$"]


def sanitize_cta(cta: str, lang: str = "en") -> str:
    """Loai bo cac tu cam quang cao trong CTA va thay the bang CTA chuan an toan."""
    cta_lower = (cta or "").lower()
    if any(p in cta_lower for p in BANNED_CTA_PATTERNS):
        if "kazakh" in lang.lower():
            return "Қосылу"
        elif "spanish" in lang.lower() or "latam" in lang.lower():
            return "Únete Ahora"
        return "Join Now"
    return cta or ("Join Now" if lang == "en" else "Толығырақ")


def sanitize_subheadline(text: str, max_words: int = 6) -> str:
    """Cat ngan Sub-headline ve toi da 6 tu va lam sach dau cau thua."""
    if not text:
        return ""
    clean = text.strip()
    words = clean.split()
    if len(words) > max_words:
        for delim in [" - ", " – ", " — ", ": ", ", "]:
            if delim in clean:
                part = clean.split(delim)[0].strip()
                if 2 <= len(part.split()) <= max_words:
                    return part.rstrip(" -–—:,.")
        return " ".join(words[:max_words]).rstrip(" -–—:,.")
    return clean.rstrip(" -–—:,.")


def detect_bullet_count(text: str) -> Optional[int]:
    """Tu dong dem so gach dau dong / y chinh trong van ban dua tren emoji hoac ky tu bullet."""
    if not text or not text.strip():
        return None
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) < 2:
        return None
    bullet_lines = []
    for l in lines[1:]:
        if re.match(r'^(?:[\u2022\u2023\u25E6\u2043\u2219\-\*▪▫►]|[\d]+[\.\)]|[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF])\s+', l):
            l_lower = l.lower()
            if not any(l_lower.startswith(x) for x in ['http', '#', '👉', 'develop', 'explore', 'elevate', 'build', 'claim']):
                bullet_lines.append(l)

    if 2 <= len(bullet_lines) <= 8:
        return len(bullet_lines)
    return None


def detect_is_stat_promotion(text: str) -> bool:
    """Kiem tra xem bai viet co phai la bai Promotion / Bonus / Co nhieu so lieu khong."""
    if not text:
        return False
    stat_signals = len(re.findall(r'(\d+%|\$\d+|\d+\s*USD|\bbonus\b|\bleverage\b|\bdeposit\b|\bmt5\b|\becn\b|\bcap\b|\bvalid\b)', text, re.IGNORECASE))
    return stat_signals >= 2


class StatBoxItem(BaseModel):
    stat_highlight: str = Field(
        description="Chu so hoac thong so cot loi in to, dam, noi bat (vi du: '100%', '20%', '3K USD', '88K USD', '20+', '3 Months', 'MT5')"
    )
    label: str = Field(
        description="Nhan mo ta ngan gon 1-3 tu ben duoi chu so (vi du: 'Cash Reward', 'Net Deposit', 'Qualified Clients', 'Milestone Period', 'Deposit bonus')"
    )


class LocalizedCardBrief(BaseModel):
    language: str = Field(description="Ten ngon ngu, vi du: 'Kazakh', 'Spanish (Latin America)'")
    headline: str = Field(description="Headline ngan gon, an tuong bang ngon ngu nay")
    sub_headline: str = Field(description="Sub-headline hanh dong ro rang bang ngon ngu nay, BAT BUOC TOI DA 6 TU (MAX 6 WORDS)")
    bullet_points: List[str] = Field(
        default_factory=list,
        description="Danh sach bullet points neu la dang checklist (moi y 2-4 tu)"
    )
    stat_boxes: List[StatBoxItem] = Field(
        default_factory=list,
        description="Danh sach cac o hop so lieu neu la dang stat_boxes (moi hop gom stat_highlight va label da duoc localize sang ngon ngu nay)"
    )
    cta_text: str = Field(
        description="Nut CTA bang ngon ngu nay. TUYET DOI KHONG dung cac tu 'earning', 'money', 'profit', 'guarantee', '$'. Vi du: 'Толығырақ', 'Қосылу', 'Descubre Más', 'Únete Ahora'"
    )


class GraphicBriefOption(BaseModel):
    concept_name: str = Field(description="Ten concept bang tieng Viet (vi du: 'Concept 1: Luoi o so lieu 2x2 noi bat', 'Concept 2: The so lieu so le')")
    layout_type: str = Field(
        description="'stat_boxes' (neu la bai Promotion/Bonus/Uu dai co chu so to) hoac 'checklist' (neu la bai Tips/Nguyen tac co gach dau dong)"
    )
    badge_number: str = Field(
        description="So dem lon o dau the (vi du '5', '4') KHI VA CHI KHI tieu de bai goc co so (vd: '5 Questions...'). Neu la bai stat_boxes hoac khong co so o tieu de, BAT BUOC de chuoi rong ''!"
    )
    headline_en: str = Field(
        description="Main catchy headline in English (Accent/Gold text), 2-4 words (e.g. 'Welcome IB Reward', 'Trade with Extra Equity Boost', 'Stay Disciplined')"
    )
    sub_headline_en: str = Field(
        description="Sub-headline in English. BAT BUOC TOI DA 6 TU (MAX 6 WORDS). Vi du: 'Grow Your Network Faster', 'Turn Referrals Into Rewards', 'One Win, Same Rules', 'Double Your Margin Today'."
    )
    bullet_points_en: List[str] = Field(
        default_factory=list,
        description="Danh sach 3-5 gach dau dong ngan (neu layout_type == 'checklist')"
    )
    stat_boxes_en: List[StatBoxItem] = Field(
        default_factory=list,
        description="Danh sach 3-4 o hop so lieu noi bat (neu layout_type == 'stat_boxes'). Vi du: [{'stat_highlight': '3K USD', 'label': 'Cash Reward'}, {'stat_highlight': '88K USD', 'label': 'Net Deposit'}, ...]"
    )
    cta_text_en: str = Field(
        description="CTA button text in English. QUY TAC TUAN THU (COMPLIANCE): TUYET DOI KHONG dung cac tu 'earning', 'earn', 'money', 'profit share', 'guarantee', 'commit' va KHONG dung ky hieu '$'. CHI dung cac CTA an toan nhu: 'Learn More', 'Join Now', 'Explore Now', 'Get Started', 'Claim Reward', 'View Details'."
    )
    localizations: List[LocalizedCardBrief] = Field(
        default_factory=list,
        description="Danh sach ban localize cho cac ngon ngu duoc yeu cau (KZ, Latam...). De list rong [] neu chi lam tieng Anh."
    )
    visual_layout_concept: str = Field(
        description="Mo ta y tuong bo cuc hinh anh chi tiet bang tieng Viet cho Designer"
    )
    element_references: str = Field(
        description="Goi y cac element do hoa tham khao bang tieng Viet (vi du: hop qua 3D, dong xu vang 3D, the voucher noi, ruy bang vang)"
    )
    ai_image_prompt: str = Field(
        description="Detailed English prompt for Midjourney / DALL-E / Flux / Imagen 3"
    )
    design_notes: str = Field(
        description="Ghi chu them ve mau sac, vi tri logo, font chu va do tuong phan bang tieng Viet"
    )


class GraphicBriefResult(BaseModel):
    options: List[GraphicBriefOption]


GRAPHIC_BRIEF_SYSTEM_INSTRUCTION = """
Ban la Giam doc Sang tao (Creative Director) va Senior Visual Copywriter hang dau cho san giao dich WeMasterTrade / WeGolden.
Nhiem vu cua ban la tiep nhan noi dung va chuyen the thanh BAN BRIEF THIET KE HINH ANH (Card Visual Brief).

CO 2 KIEU DINH DANG THE (LAYOUT TYPE):
1. DINH DANG 'stat_boxes' (THE O SO LIEU NOI BAT - Chuyen dung cho bai Promotion, Bonus, Uu dai, San pham):
   - Bo cuc the gom 3 den 4 O HOP HINH CHU NHAT (Grid 2x2 hoac sap xep so le).
   - Trong moi hop gom:
     + stat_highlight: Chu so to, dam, an tuong nhat (vd: '100%', '20%', '3K USD', '88K USD', '20+', '3 Months', 'MT5').
     + label: Nhan mo ta ngan gon 1-3 tu ben duoi (vd: 'Cash Reward', 'Net Deposit', 'Qualified Clients', 'Milestone Period', 'Deposit bonus').
   - Headline: Tap trung vao Ten chuong trinh & Ty le % (vd: 'Welcome IB Reward', '100% Bonus Deposit').

2. DINH DANG 'checklist' (THE GACH DAU DONG HANH DONG - Chuyen dung cho bai Tips trading, Tam ly, Kien thuc):
   - Bo cuc the gom 3 den 5 gach dau dong cuc ky co dong (2-4 tu moi y, Title-case).

QUY TAC RAT QUAN TRONG VE SUB-HEADLINE & CTA (BAT BUOC TUAN THU 100%):
1. SUB-HEADLINE GIOI HAN TOI DA 6 TU (MAXIMUM 6 WORDS):
   - Sub-headline phai cuc ky ngan gon, danh thep, khong viet thanh ca cau dai dong.
   - Vi du tot: "Grow Your Network Faster" (4 tu), "Turn Referrals Into Rewards" (4 tu), "One Win, Same Rules" (4 tu), "Double Your Margin Today" (4 tu).
   - Vi du xau bi cam: "Unlock $3K Cash - Grow Your Network Faster" (8 tu -> Qua dai!).

2. NGUYEN TAC TUAN THU QUANG CAO CHO CTA (COMPLIANCE RULE):
   - TUYET DOI KHONG su dung cac tu sau trong nut CTA (ca ban tieng Anh va ban dich):
     ❌ "earning", "earn", "money", "profit share", "profit", "guarantee", "commit", ky hieu "$"
   - CHUNG TA CHI DUNG CAC CTA AN TOAN CHUAN CHUYEN NGHIEP:
     ✅ Tieng Anh: "Learn More", "Explore Now", "Join Now", "Get Started", "Claim Reward", "View Details"
     ✅ Tieng Kazakh: "Толығырақ", "Қосылу", "Толығырақ білу", "Қазір бастаңыз"
     ✅ Tieng Spanish: "Descubre Más", "Conoce Más", "Únete Ahora", "Empieza Hoy"
""".strip()


class GraphicBriefService:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def generate(
        self,
        brand: str,
        content_input: str,
        localize_languages: List[str],
        forced_layout_type: Optional[str] = None,
        num_points: Optional[int] = None,
        num_options: int = 2,
    ) -> GraphicBriefResult:
        cfg = BRANDS.get(brand, BRANDS["WeMasterTrade"])

        langs_instruction = ""
        if localize_languages:
            langs_instruction = f"""
YEU CAU BAN DIA HOA (LOCALIZE):
Ngoai ban tieng Anh goc (English), ban BAT BUOC phai tao ban thiet ke song song cho cac ngon ngu sau:
{', '.join(localize_languages)}
- Khong dich word-by-word may moc, ma localize tu nhien theo dung van phong trader ban xu o khu vuc do.
- Dong bo 100% cau truc giua cac ngon ngu: cung so luong o hop/points, sub-headline duoi 6 tu, CTA an toan (khong dung earning/money/profit/$).
"""
        else:
            langs_instruction = "CHI YEU CAU BAN TIENG ANH GOC (khong can tao localizations)."

        layout_instruction = ""
        if forced_layout_type == "stat_boxes":
            layout_instruction = "BAT BUOC SU DUNG KIEU 'stat_boxes': Tao 3 den 4 o hop so lieu (stat_boxes_en) voi chu so to dam noi bat va nhan mo ta ngan gon (vd: 3K USD, 88K USD, 20+, 3 Months)."
        elif forced_layout_type == "checklist":
            pts = num_points if num_points else 4
            layout_instruction = f"BAT BUOC SU DUNG KIEU 'checklist': Tao dung {pts} gach dau dong co dong (2-4 tu/y) tuong ung voi bai goc."
        else:
            layout_instruction = "TU DONG NHAN DIEN: Neu bai viet la ve Promotion, Bonus, Uu dai co nhieu con so (%, USD, ngay...) hay dung 'stat_boxes'. Neu bai viet la Tips, Kien thuc trading, hay dung 'checklist'."

        prompt = f"""
BRAND: {brand}
CAM HUONG THIET KE & MAU SAC:
- Brand color chu dao: {cfg.get('header_fill', '#1F4E79')}
- Tone: Chuyen nghiep, tinh te, cao cap (Fintech / Prop Trading / Broker).

{langs_instruction}

{layout_instruction}

SO PHUONG AN CONCEPT CAN TAO: {num_options} phuong an.

NOI DUNG BAI GOC (DOC KY VA BAM SAT 100% VAO CHU DE & SO LIEU NAY):
\"\"\"
{content_input.strip()}
\"\"\"

Hay tao ket qua JSON hop le theo dung schema da dinh nghia.
LUU Y: Sub-headline TOI DA 6 TU. CTA TUYET DOI KHONG dung 'earning', 'money', 'profit share', 'guarantee', '$'.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=GRAPHIC_BRIEF_SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=GraphicBriefResult,
                temperature=0.3,
            ),
        )

        result = GraphicBriefResult.model_validate_json(response.text)

        # Post-processing Sanity Check: Dam bao Sub-headline <= 6 tu va CTA luon an toan tuyet doi
        for opt in result.options:
            opt.sub_headline_en = sanitize_subheadline(opt.sub_headline_en, max_words=6)
            opt.cta_text_en = sanitize_cta(opt.cta_text_en, lang="en")
            for loc in opt.localizations:
                loc.sub_headline = sanitize_subheadline(loc.sub_headline, max_words=6)
                loc.cta_text = sanitize_cta(loc.cta_text, lang=loc.language)

        return result
