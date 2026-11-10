# -*- coding: utf-8 -*-
"""Goi Gemini API de brainstorm content Reddit (dong vai khach hang/trader that)."""

import json
from typing import List

from pydantic import BaseModel, Field
from google import genai
from google.genai import types

from guideline_data import REDDIT_GUIDELINE_VI, BRANDS


class RedditPost(BaseModel):
    format: str = Field(description="Format cua bai post, giu dung 1 trong cac format da yeu cau")
    content_angle: str = Field(description="Goc trien khai cu the trong format nay, tieng Anh, ngan gon (vd 'Trading mistake and lesson learned')")
    topic: str = Field(description="Tieu de bai Reddit post, tieng Anh, tu nhien, KHONG viet hoa toan bo, KHONG giat gan")
    content: str = Field(description="Toan bo noi dung bai post, tieng Anh, ngoi thu nhat, van phong ca nhan tu nhien, ket bang 1 cau hoi mo")
    image_note: str = Field(description="Ghi chu ngan (tieng Viet) ve anh minh hoa neu can, hoac 'Không cần ảnh' neu khong can. KHONG duoc la URL/link.")
    note: str = Field(description="Luu y ngan (tieng Viet) ve van phong/cach the hien cho nguoi duyet noi dung")


class RedditGenerateResult(BaseModel):
    posts: List[RedditPost]


def _build_reddit_prompt(
    brand: str,
    formats: List[str],
    extra_brief: str,
    num_posts: int,
) -> str:
    cfg = BRANDS[brand]
    formats_str = ", ".join(formats) if formats else "tu chon format phu hop nhat"

    extra_brief_block = ""
    if extra_brief and extra_brief.strip():
        extra_brief_block = f"""
Chu de/y tuong goi y them tu nguoi dung (bam sat neu co, day la ngu canh quan
trong nhat):
\"\"\"{extra_brief.strip()}\"\"\"
"""
    else:
        extra_brief_block = """
Nguoi dung khong dua chu de cu the - hay tu brainstorm cac tinh huong/trai
nghiem da dang, thuc te, lien quan toi trading/prop firm/{brand} sao cho da
dang, khong trung lap y tuong giua cac bai.
""".format(brand=brand)

    return f"""
Ban la 1 nguoi viet content social chuyen brainstorm bai dang Reddit cho cong
dong trader, cho brand {brand}. Ban PHAI tuan thu chinh xac guideline noi bo
sau day:

=== GUIDELINE NOI BO REDDIT (BAT BUOC TUAN THU) ===
{REDDIT_GUIDELINE_VI}
=== HET GUIDELINE ===

Neu co nhac ten brand trong bai, dung dung ten: {brand}. Website chinh thuc
(chi nhac neu that tu nhien, KHONG chen link): {cfg['official_site']}

--- YEU CAU CU THE CHO LAN BRAINSTORM NAY ---
Cac Format duoc yeu cau su dung (phan bo deu, moi format nen xuat hien it
nhat 1 lan neu so luong bai cho phep): {formats_str}
{extra_brief_block}

YEU CAU OUTPUT:
- Tao DUNG {num_posts} bai post, moi bai la 1 phan tu trong "posts".
- Moi bai PHAI khac nhau ve tinh huong/trai nghiem/content_angle - KHONG duoc
  trung y tuong hay dung chung 1 cau mo dau giua cac bai.
- Truong "content" PHAI viet tieng Anh, ngoi thu nhat, tu nhien nhu 1 trader
  that dang chia se, ket bang 1 cau hoi mo. Dong dau cua "content" nen lap lai
  dung "topic" (giong nhu tieu de bai Reddit), sau do xuong dong roi moi den
  noi dung.
- Truong "format" phai lay tu danh sach Format da yeu cau o tren (neu co).
- Tuan thu CHINH XAC phan "TRANH lam" trong guideline - khong duoc vi pham.
"""


class RedditContentService:
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate(
        self,
        brand: str,
        formats: List[str],
        extra_brief: str,
        num_posts: int,
    ) -> RedditGenerateResult:
        prompt = _build_reddit_prompt(
            brand=brand,
            formats=formats,
            extra_brief=extra_brief,
            num_posts=num_posts,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RedditGenerateResult,
                temperature=1.0,
            ),
        )

        if response.parsed is not None:
            return response.parsed
        return RedditGenerateResult(**json.loads(response.text))
