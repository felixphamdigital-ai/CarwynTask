# -*- coding: utf-8 -*-
"""Goi Gemini API de brainstorm bai dang gioi thieu/quang ba su kien offline."""

import json
from typing import List

from pydantic import BaseModel, Field
from google import genai
from google.genai import types

from guideline_data import EVENT_GUIDELINE_VI, BRANDS


class LocalizedEventText(BaseModel):
    language: str = Field(description="Ten ngon ngu ban dia hoa, giu dung nguyen ten da yeu cau")
    headline_adapt: str = Field(description="Ban localize cua headline sang ngon ngu nay")
    content_adapt: str = Field(
        description="Ban localize cua toan bo content sang ngon ngu nay. BAT BUOC dung ky tu xuong dong "
        "that su (\\n) giua headline / doan mo ta / 'Event Details:' / tung dong bullet Event Details / "
        "dong urgency / dong CTA - giong HET cau truc xuong dong cua ban tieng Anh, KHONG duoc dinh lien "
        "thanh 1 doan van duy nhat."
    )


class EventPost(BaseModel):
    angle_vi: str = Field(description="Goc trien khai cua bai nay, BAT BUOC viet bang TIENG VIET (vd: nhan manh lucky draw)")
    headline_en: str = Field(description="Headline/hook mo dau, tieng Anh, co emoji")
    content_en: str = Field(
        description="Toan bo noi dung bai post bang tieng Anh, dung cau truc trong guideline (headline, mo "
        "ta, Event Details, urgency, CTA). BAT BUOC dung ky tu xuong dong that su (\\n) de tach: headline "
        "rieng 1 dong, dong trong, doan mo ta (co the 1-2 doan, moi doan cach nhau 1 dong trong), dong trong, "
        "'Event Details:' rieng 1 dong, MOI bullet (📍 Date/Time/Venue, 📝 Registration) tren 1 dong RIENG "
        "BIET, dong trong, dong urgency (🔥) rieng 1 dong, dong trong, dong CTA (👉 Sign Up Here: link) rieng "
        "1 dong. KHONG duoc dinh lien tat ca thanh 1 doan van duy nhat - phai xuong dong giong HET bai mau "
        "tham khao duoc dua trong phan THONG TIN SU KIEN."
    )
    localizations: List[LocalizedEventText] = Field(
        description="Danh sach ban localize cho TUNG ngon ngu duoc yeu cau. De list rong [] neu khong can localize."
    )
    hashtags: str = Field(description="Danh sach hashtag, cach nhau boi dau cach, giu tieng Anh")
    image_note: str = Field(description="Ghi chu ngan (tieng Viet) ve anh/hinh minh hoa neu can, hoac 'Không cần ảnh'. KHONG duoc la URL/link.")
    note: str = Field(description="Luu y ngan (tieng Viet) cho nguoi duyet noi dung")


class EventGenerateResult(BaseModel):
    posts: List[EventPost]


def _build_event_prompt(
    brand: str,
    region: str,
    localize_languages: List[str],
    event_info: str,
    num_posts: int,
) -> str:
    cfg = BRANDS[brand]

    if localize_languages:
        langs_str = ", ".join(localize_languages)
        localize_instruction = f"""
BAT BUOC dien truong "localizations" cho MOI bai voi DUNG {len(localize_languages)}
phan tu, moi phan tu tuong ung 1 ngon ngu sau (giu dung ten ngon ngu, khong
doi ten): {langs_str}.
Ban localize phai tu nhien nhu nguoi ban xu noi (khong dich word-by-word),
van giu nguyen thong tin ngay/gio/dia diem/link CHINH XAC nhu ban tieng Anh.
"""
    else:
        localize_instruction = """
Khong can ban localize ngon ngu nao. De "localizations" la list rong [].
"""

    return f"""
Ban la 1 content creator chuyen viet bai dang social gioi thieu/quang ba su
kien offline cho brand tai chinh/trading {brand}. Ban PHAI tuan thu chinh xac
guideline noi bo sau day:

=== GUIDELINE NOI BO EVENT ANNOUNCEMENT (BAT BUOC TUAN THU) ===
{EVENT_GUIDELINE_VI}
=== HET GUIDELINE ===

Website chinh thuc cua brand (neu can nhac toi, KHONG dung de thay the link
dang ky that): {cfg['official_site']}

--- THONG TIN SU KIEN THAT (NGUON DU LIEU DUY NHAT, PHAI CHINH XAC) ---
{event_info}
--- HET THONG TIN SU KIEN ---

Khu vuc/thi truong muc tieu cua bai dang: {region}
{localize_instruction}

YEU CAU OUTPUT:
- Tao DUNG {num_posts} bai post, moi bai la 1 phan tu trong "posts".
- Moi bai PHAI khac angle/goc nhan manh (xem goi y trong guideline), KHONG
  duoc trung y tuong hay dung chung cau mo dau.
- Ngay/gio/dia diem/link dang ky PHAI lay CHINH XAC tu phan "THONG TIN SU
  KIEN THAT" o tren, TUYET DOI KHONG duoc bia them hay doi sai.
- Tuan thu CHINH XAC phan "QUY TAC" trong guideline - khong duoc vi pham.
- QUAN TRONG VE DINH DANG: truong content_en va content_adapt BAT BUOC phai
  co ky tu xuong dong that su (\\n) giua cac phan (headline / doan mo ta /
  Event Details / tung bullet / urgency / CTA), moi bullet trong Event
  Details nam tren 1 dong rieng. KHONG duoc tra ve toan bo noi dung dinh lien
  thanh 1 doan van duy nhat khong xuong dong - day la loi rat hay gap, phai
  tranh tuyet doi.
"""


class EventContentService:
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate(
        self,
        brand: str,
        region: str,
        localize_languages: List[str],
        event_info: str,
        num_posts: int,
    ) -> EventGenerateResult:
        prompt = _build_event_prompt(
            brand=brand,
            region=region,
            localize_languages=localize_languages,
            event_info=event_info,
            num_posts=num_posts,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=EventGenerateResult,
                temperature=0.9,
            ),
        )

        if response.parsed is not None:
            return response.parsed
        return EventGenerateResult(**json.loads(response.text))
