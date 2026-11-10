# -*- coding: utf-8 -*-
"""Goi Gemini API (goi free tier) de brainstorm brief video theo form co dinh."""

import json
from typing import List

from pydantic import BaseModel, Field
from google import genai
from google.genai import types

from guideline_data import (
    CORE_GUIDELINE_VI,
    SCENE_STRUCTURE,
    DEFAULT_DISCLAIMER_VI,
    BRANDS,
    LANGUAGE_AUTO_INCLUDE,
)


class LocalizedText(BaseModel):
    language: str = Field(description="Ten ngon ngu ban dia hoa, giu dung nguyen ten da yeu cau (vi du 'Kazakh')")
    voice_adapt: str = Field(description="Ban localize (KHONG phai dich word-by-word) cua voiceover sang ngon ngu nay, tu nhien nhu nguoi ban xu noi")
    text_adapt: str = Field(description="Ban localize cua on-screen text sang ngon ngu nay")


class SceneOut(BaseModel):
    time: str = Field(description="Khoang thoi gian cua scene, giu dung theo cau truc co dinh")
    scene: str = Field(description="Ten scene, giu dung ten trong cau truc co dinh (Hook/Pain Point/Main Content/Solution/Conclusion/CTA + Disclaimer)")
    voiceover: str = Field(description="Loi thoai tieng Anh cho scene nay")
    onscreen_text: str = Field(description="Text hien tren man hinh, tieng Anh, ngan gon")
    localizations: List[LocalizedText] = Field(
        description="Danh sach ban localize cho TUNG ngon ngu duoc yeu cau, 1 phan tu/ngon ngu. De list rong [] neu khong can localize ngon ngu nao."
    )
    visual_direction: str = Field(description="Mo ta chi tiet bang tieng Viet cho editor dung hinh, theo dung VISUAL DIRECTION RULES")
    ref: str = Field(description="Mo ta ngan phong cach video tham khao (KHONG phai URL/link), theo dung REFERENCE NOTE RULE")
    note: str = Field(description="Ghi chu them cho editor (vd nhac mascot xuat hien). De chuoi rong '' neu khong co.")


class VideoOption(BaseModel):
    topic: str = Field(description="Video title, tieng Anh, ngan gon, cuon hut")
    angle_vi: str = Field(description="Core angle/goc trien khai cua video, BAT BUOC viet bang TIENG VIET")
    target_audience: str = Field(description="Target audience cu the cho video nay, tieng Anh")
    viewer_takeaway: str = Field(description="Main takeaway nguoi xem nhan duoc sau khi xem video, tieng Anh, 1 cau ngan gon")
    video_length: str = Field(description="Do dai video va luu y ve nhip do, tieng Anh")
    format: str = Field(description="Format quay dung, tieng Anh")
    tone: str = Field(description="Tone giong cua video, tieng Anh")
    key_message: str = Field(description="Key message / main message chinh, tieng Anh")
    ai_speaker_note: str = Field(description="Mo ta visual AI speaker (va mascot neu co), tieng Anh, dua tren AI PRESENTER BASE va adapt theo region")
    scenes: List[SceneOut] = Field(description="Danh sach dung 6 scene theo dung cau truc co dinh: Hook, Pain Point, Main Content, Solution, Conclusion, CTA + Disclaimer")


class GenerateResult(BaseModel):
    options: List[VideoOption]


def resolve_languages(selected_languages: List[str]) -> List[str]:
    """Ap dung LANGUAGE_AUTO_INCLUDE (vd chon Kazakh se tu dong kem Uzbek),
    giu nguyen thu tu, khong trung lap."""
    result = []
    for lang in selected_languages:
        lang = lang.strip()
        if not lang:
            continue
        if lang not in result:
            result.append(lang)
        for extra in LANGUAGE_AUTO_INCLUDE.get(lang, []):
            if extra not in result:
                result.append(extra)
    return result


FOCUS_ON_NUMBERS_INSTRUCTION_VI = """
YEU CAU DAC BIET - TAP TRUNG SO LIEU (nguoi dung da bat tuy chon nay):
Noi dung video nay PHAI tap trung vao SO LIEU CU THE, KHONG duoc dung ngon
ngu ly thuyet/marketing mo ho chung chung ("hang dau", "vuot troi", "tot
nhat"...) ma khong co so di kem. Hay TU DOC KY phan "Y tuong / brief / noi
dung nguon" o duoi, TU TIM RA moi so lieu cu the co trong do (tien, %, so
luong, cap do/tier, ngay thang, khoi luong, thoi gian, ty le...) va XAY DUNG
kich ban XOAY QUANH cac so lieu that do - cang nhieu con so cu the xuat hien
trong voiceover va onscreen_text cang tot, dac biet uu tien dua vao Main
Content va Solution.
Neu trong noi dung nguon co claim/loi ich nao KHONG co so lieu cu the di
kem, hoac ban goc TU GHI CHU ro la "chua xac minh"/"chua co so lieu cu
the"/"chi la hinh anh minh hoa"/tuong tu, thi PHAI BO QUA claim do hoan
toan, KHONG dua vao kich ban, va TUYET DOI KHONG tu bia them so lieu de thay
the cho no.
"""


def _build_prompt(
    brand: str,
    platform: str,
    region: str,
    localize_languages: List[str],
    user_brief: str,
    num_options: int,
    focus_on_numbers: bool = False,
) -> str:
    cfg = BRANDS[brand]
    scene_list_str = "\n".join(
        f"{i+1}. [{s['time']}] {s['scene']} - {s['desc']}" for i, s in enumerate(SCENE_STRUCTURE)
    )
    focus_on_numbers_block = FOCUS_ON_NUMBERS_INSTRUCTION_VI if focus_on_numbers else ""

    if cfg["localizable"] and localize_languages:
        langs_str = ", ".join(localize_languages)
        localize_instruction = f"""
Video nay huong toi thi truong/khu vuc: {region}.
BAT BUOC dien truong "localizations" cho MOI scene voi DUNG {len(localize_languages)}
phan tu, moi phan tu tuong ung 1 ngon ngu trong danh sach sau (giu dung ten
ngon ngu y het, khong doi ten): {langs_str}.
Moi ban localize phai tu nhien nhu nguoi ban xu noi (khong dich word-by-word),
KHONG duoc bo sot ngon ngu nao trong danh sach tren.
"""
    else:
        localize_instruction = """
Video nay KHONG can ban localize ngon ngu nao. De "localizations" la list
rong [] cho tat ca scene.
"""

    mascot_instruction = ""
    if cfg["mascot"]:
        mascot_instruction = """
Day la brand WeGolden: ap dung dung phan "Rieng WeGolden" trong guideline ve
mascot cameo.
"""

    return f"""
Ban la Creative Strategist chuyen viet brief video Reels ngan (40s) cho 2
brand tai chinh/trading: WeMasterTrade va WeGolden. Ban PHAI tuan thu chinh
xac guideline noi bo sau day - day la ban chuan hoa moi nhat, uu tien hon tat
ca kien thuc chung ban co ve content marketing:

=== GUIDELINE NOI BO (BAT BUOC TUAN THU CHINH XAC) ===
{CORE_GUIDELINE_VI}
=== HET GUIDELINE ===

Cau truc kich ban BAT BUOC dung DUNG 6 scene theo dung thu tu va time-block
sau (khong them bot, khong doi ten scene, thoi gian giu dung tru khi co ly do
manh de dieu chinh nhe):
{scene_list_str}

Rieng scene cuoi "CTA + Disclaimer": neu khong co disclaimer rieng nao khac
tu nguoi dung, hay dung cau disclaimer mac dinh nay (giu nguyen tieng Viet,
dat trong phan note hoac ghep vao onscreen_text tuy bo cuc):
"{DEFAULT_DISCLAIMER_VI}"

VE CTA/LINK: Neu brief cua nguoi dung CO cung cap link cu the (link dang ky
su kien, landing page, form...), dia chi/dia diem cu the, hoac deadline cu
the (vi du: brief ve 1 su kien offline, 1 chuong trinh co link rieng), thi
BAT BUOC dung CHINH XAC link/dia chi/deadline DO trong onscreen_text va/hoac
voiceover cua scene CTA - KHONG duoc thay the bang website chung chung. Chi
khi brief KHONG cung cap link/thong tin cu the nao thi moi mac dinh dan
nguoi xem ve website chinh thuc: {cfg['official_site']}.

--- YEU CAU CU THE CHO LAN BRIEF NAY ---
Brand: {brand}
Nen tang dang: {platform}
Khu vuc/thi truong muc tieu (anh huong toi AI PRESENTER BASE phai adapt dac
diem ngoai hinh nguoi ban xu khu vuc nay): {region}
{localize_instruction}
{mascot_instruction}

{focus_on_numbers_block}

Y tuong / brief / noi dung nguon tu nguoi dung (day la thong tin quan trong
nhat, hay bam sat, neu nguoi dung da cho san topic/content cu the thi PHAI
giu dung topic/content do, khong duoc bien tau sang y khac):
\"\"\"{user_brief}\"\"\"

YEU CAU OUTPUT:
- Brainstorm ra {num_options} phuong an video. Neu nguoi dung da cho topic co
  dinh trong brief thi CA {num_options} phuong an deu phai giu dung topic do
  nhung co the khac nhau ve cach trien khai/angle chi tiet; neu nguoi dung chi
  dua y tuong chung thi {num_options} phuong an phai KHAC NHAU ve angle/goc
  trien khai (khong trung y tuong nhau).
- Truong "angle_vi" cua MOI phuong an BAT BUOC viet bang TIENG VIET. Cac
  truong khac (topic, target_audience, viewer_takeaway, video_length, format,
  tone, key_message, ai_speaker_note, voiceover, onscreen_text) viet bang
  TIENG ANH - day chinh la cot tieng Anh goc de nguoi doc hieu duoc noi dung
  du khong biet ngon ngu ban dia hoa. Rieng visual_direction, ref, note viet
  bang TIENG VIET de editor Viet Nam de doc va dung video.
- Tuan thu CHINH XAC CONTENT AND COMPLIANCE RULES - day la yeu cau bat buoc,
  khong duoc vi pham du chi 1 dieu.
- Voiceover phai tu nhien, co cau noi chuyen y muot giua cac scene (xem
  VOICEOVER STYLE GUIDE).
- Visual Direction phai tuan thu nghiem ngat nguyen tac tach Mode A/Mode B
  (xem VISUAL DIRECTION RULES) - khong duoc tron AI speaker voi screen
  recording/UGC trong cung 1 scene.
- Truong "ref" KHONG duoc chua URL/link, chi mo ta phong cach tham khao (xem
  REFERENCE NOTE RULE).
- QUAN TRONG VE CTA: neu brief o tren co nhac toi link/dia chi/deadline cu
  the (vi du link dang ky, dia diem su kien, ngay het han), scene CTA BAT
  BUOC phai ghi CHINH XAC link/dia chi/deadline do (nguyen van, khong sua)
  trong onscreen_text - day la loi hay bi bo sot, phai kiem tra lai truoc
  khi tra ve ket qua.
{"- NHAC LAI: phai tap trung so lieu cu the tu noi dung nguon nhu yeu cau o tren, bo qua moi claim khong co so lieu di kem hoac duoc ghi chu la chua xac minh." if focus_on_numbers else ""}
"""


class GeminiService:
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate(
        self,
        brand: str,
        platform: str,
        region: str,
        localize_languages: List[str],
        user_brief: str,
        num_options: int,
        focus_on_numbers: bool = False,
    ) -> GenerateResult:
        resolved_languages = resolve_languages(localize_languages)
        prompt = _build_prompt(
            brand=brand,
            platform=platform,
            region=region,
            localize_languages=resolved_languages,
            user_brief=user_brief,
            num_options=num_options,
            focus_on_numbers=focus_on_numbers,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GenerateResult,
                temperature=0.9,
            ),
        )

        if response.parsed is not None:
            return response.parsed
        return GenerateResult(**json.loads(response.text))
