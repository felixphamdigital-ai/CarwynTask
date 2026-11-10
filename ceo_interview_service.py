# -*- coding: utf-8 -*-
"""Goi Gemini API de brainstorm 1 tap trong series phong van CEO (thay AI
speaker bang nguoi that / CEO), theo dung format "Inside the Golden Mind"."""

import json
from typing import List

from pydantic import BaseModel, Field
from google import genai
from google.genai import types

from guideline_data import (
    CEO_INTERVIEW_GUIDELINE_VI,
    CEO_SECTION_STRUCTURE,
    CEO_DEFAULT_SERIES_NAME,
    CEO_DEFAULT_TALENT,
    CEO_DEFAULT_DURATION,
    CEO_DEFAULT_DISCLAIMER_EN,
    CEO_PILLARS,
)


class CEOSectionOut(BaseModel):
    section: str = Field(description="Ten section, giu dung ten trong cau truc co dinh (Hook/Intro/Problem/CEO Perspective/Solution/Key Takeaway/Conclusion/Outro)")
    ceo_script: str = Field(description="Loi CEO noi (tieng Anh, ngoi thu nhat). De chuoi rong '' cho Intro va Outro (2 section nay khong co CEO noi).")
    onscreen_text: str = Field(description="Text hien tren man hinh, tieng Anh, ngan gon. De chuoi rong '' neu khong can.")
    visual_direction: str = Field(description="Mo ta chi tiet bang tieng Viet ve boi canh/goc quay/chuyen dong camera/thoi diem xuat hien text cho editor")
    ref: str = Field(description="Mo ta ngan (tieng Viet) phong cach video tham khao (KHONG phai URL/link that)")


class CEOEpisodeOut(BaseModel):
    series_name: str
    talent: str
    pillar: str
    duration: str
    topic_title: str
    episode_key: str
    next_episode_key: str
    sections: List[CEOSectionOut]


class _RawCEOOption(BaseModel):
    """Chi lay phan Gemini THAT SU can brainstorm (sections). Cac truong
    metadata co dinh (series_name/talent/pillar/duration/topic_title/
    episode_key/next_episode_key) la INPUT nguoi dung da cho san, KHONG hoi
    lai Gemini vi model hay tu dong rut gon/dien giai lai (da gap truong hop
    "45-60 seconds - Reels" bi rut thanh "45-60 seconds") - de dam bao chinh
    xac 100%, code Python tu ghep lai cac truong nay thay vi tin model echo
    lai dung nguyen van."""
    sections: List[CEOSectionOut] = Field(description="Danh sach DUNG 8 section theo dung thu tu co dinh: Hook, Intro, Problem, CEO Perspective, Solution, Key Takeaway, Conclusion, Outro")


class _RawCEOResult(BaseModel):
    options: List[_RawCEOOption]


class CEOGenerateResult(BaseModel):
    episodes: List[CEOEpisodeOut]


def _build_ceo_prompt(
    series_name: str,
    talent: str,
    pillar: str,
    duration: str,
    topic_title: str,
    episode_key_context: str,
    next_episode_key: str,
    source_content: str,
    num_options: int,
) -> str:
    section_list_str = "\n".join(
        f"{i+1}. {s['section']} - {s['desc']}" for i, s in enumerate(CEO_SECTION_STRUCTURE)
    )
    pillar_desc = CEO_PILLARS.get(pillar, "")

    return f"""
Ban la Creative Strategist chuyen viet kich ban video Reels ngan (45-60s)
cho series thought-leadership do CEO dan dat, thay the hoan toan AI speaker
bang NGUOI THAT (CEO). Ban PHAI tuan thu chinh xac guideline noi bo sau day:

=== GUIDELINE NOI BO SERIES (BAT BUOC TUAN THU CHINH XAC) ===
{CEO_INTERVIEW_GUIDELINE_VI}
=== HET GUIDELINE ===

Cau truc kich ban BAT BUOC dung DUNG 8 section theo dung thu tu sau (khong
them bot, khong doi ten section):
{section_list_str}

--- THONG TIN TAP NAY ---
Series: {series_name}
Talent (nguoi noi): {talent}
Pillar (core value): {pillar} - {pillar_desc}
Duration: {duration}
Topic/Angle cua tap nay: {topic_title}

Episode Key (bai hoc/thong diep cot loi tap nay PHAI truyen tai, bam sat
CHINH XAC noi dung sau, day la du lieu da duoc chot san, KHONG duoc bien
tau sang y khac): {episode_key_context}

Next Episode Key (cau hoi BAT BUOC phai xuat hien o scene Conclusion de dan
sang tap tiep theo, giu CHINH XAC): {next_episode_key}

Noi dung nguon / ghi chu bo sung tu nguoi dung (tham khao them de bam sat
dung tinh than, giong dieu, cac diem chinh can nhac toi):
\"\"\"{source_content}\"\"\"

YEU CAU OUTPUT:
- Tao DUNG {num_options} phuong an kich ban cho CUNG 1 tap nay, khac nhau ve
  cach trien khai CEO Script/Visual Direction cu the, nhung PHAI CUNG bam sat
  dung Episode Key/Next Episode Key/Pillar/Topic da cho o tren (khong can
  echo lai cac gia tri nay trong output - chi can dam bao NOI DUNG cac
  section the hien dung tinh than cua chung).
- CEO Script viet ngoi thu nhat, tu nhien, dung dung Persona & Tone trong
  guideline (Premium, calm, insightful, personal). KHONG duoc doc nhu quang
  cao.
- Section "Intro" va "Outro" De ceo_script la chuoi rong '' (2 section nay
  KHONG co CEO noi, chi la bumper/CTA graphic).
- Onscreen_text cho "Outro" BAT BUOC theo dinh dang: "CTA: ...\\nDC: {CEO_DEFAULT_DISCLAIMER_EN}"
  (neu nguoi dung khong yeu cau CTA khac).
- Visual Direction va Ref viet TIENG VIET, chi tiet, thuc te (bam theo dung
  FORMAT & FILMING trong guideline: quay tai van phong WeGolden, CEO la chu
  the chinh, B-roll ngan neu can). Ref la mo ta phong cach, KHONG duoc la
  URL/link that (Gemini khong the xac minh link that ton tai).
- Noi dung cac section (dac biet Problem va Conclusion) PHAI THE HIEN DUNG Y
  NGHIA cua Episode Key va Next Episode Key da cho o tren, nhung khong bat
  buoc phai lap lai y het tung chu.
"""


class CEOInterviewService:
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate(
        self,
        pillar: str,
        topic_title: str,
        episode_key_context: str,
        next_episode_key: str,
        source_content: str = "",
        series_name: str = CEO_DEFAULT_SERIES_NAME,
        talent: str = CEO_DEFAULT_TALENT,
        duration: str = CEO_DEFAULT_DURATION,
        num_options: int = 1,
    ) -> CEOGenerateResult:
        prompt = _build_ceo_prompt(
            series_name=series_name,
            talent=talent,
            pillar=pillar,
            duration=duration,
            topic_title=topic_title,
            episode_key_context=episode_key_context,
            next_episode_key=next_episode_key,
            source_content=source_content,
            num_options=num_options,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=_RawCEOResult,
                temperature=0.8,
            ),
        )

        if response.parsed is not None:
            raw_result = response.parsed
        else:
            raw_result = _RawCEOResult(**json.loads(response.text))

        # Ghep metadata co dinh (da cho san tu input) bang code, KHONG dua
        # vao Gemini echo lai - tranh loi rut gon/dien giai sai gia tri.
        episodes = [
            CEOEpisodeOut(
                series_name=series_name,
                talent=talent,
                pillar=pillar,
                duration=duration,
                topic_title=topic_title,
                episode_key=episode_key_context,
                next_episode_key=next_episode_key,
                sections=raw_opt.sections,
            )
            for raw_opt in raw_result.options
        ]
        return CEOGenerateResult(episodes=episodes)
