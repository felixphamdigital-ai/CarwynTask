# -*- coding: utf-8 -*-
"""
Guideline co dinh, trich tu file input chuan nhat "Brief video.docx" (ban moi,
cau truc tieng Anh, tai Desktop) + cac fix da chot qua qua trinh lam viec:
- Bo freeze panes trong file Excel
- Voiceover phai tu nhien, co cau noi chuyen y muot giua cac scene
- Visual Direction: moi scene CHI mot mode - AI speaker DUY NHAT, hoac
  screen recording/UGC DUY NHAT - khong tron lan, khong motion graphic phuc tap
- WeGolden: mascot xuat hien cameo ngan trong 2-3 scene
- Reference: mo ta phong cach tham khao, KHONG bia link that (Gemini khong
  the dung Google Search grounding cung luc voi structured JSON output, nen
  moi link tu sinh deu co the la link gia -> khong dung link, chi mo ta)
"""

# ----------------------------------------------------------------------------
# 1. INFORMATION / VIDEO OBJECTIVE / VIDEO FORMAT (theo dung docx chuan)
# ----------------------------------------------------------------------------
TARGET_AUDIENCE_OPTIONS = [
    "New users discovering the brand",
    "Hesitant prospects",
    "New traders wanting an easy start",
    "Traders needing a simple explanation",
]

VIDEO_OBJECTIVE_VI = """
- Focus: chi 1 core topic duy nhat, khong lac de.
- Message: chi 1 main takeaway duy nhat.
- CTA: chi 1 primary action duy nhat.
- Curiosity: FOMO nhe, KHONG duoc clickbait.
- Clarity: phai ro rang what it is / how it works / who it's for.
- Goal: khuyen khich nguoi xem kham pha them tren website chinh thuc.
""".strip()

VIDEO_FORMAT_VI = """
- Duration: 40 giay (co dinh).
- Aspect ratio: Vertical 9:16.
- Style: Modern UGC voi AI presenter.
- Elements duoc phep: AI presenter, screen recording, product visuals,
  b-roll, animated text overlays, AI voiceover.
""".strip()

# ----------------------------------------------------------------------------
# 2. NARRATIVE STRUCTURE - 6 scene co dinh, time-block co dinh theo docx chuan
# ----------------------------------------------------------------------------
SCENE_STRUCTURE = [
    {
        "time": "0-4s",
        "scene": "Hook",
        "desc": (
            "Mo dau bang 1 cau/cau hoi truc tiep, gay to mo, lien quan toi "
            "topic. Nhac ten san pham/chuong trinh/brand som. KHONG duoc "
            "clickbait gay hieu lam."
        ),
    },
    {
        "time": "5-10s",
        "scene": "Pain Point",
        "desc": (
            "Neu 1 van de/su boi roi/moi lo ro rang ma target audience dang "
            "gap phai, lien quan truc tiep toi topic."
        ),
    },
    {
        "time": "11-18s",
        "scene": "Main Content",
        "desc": (
            "Trinh bay thong tin cot loi ve san pham/dich vu/tips trading/"
            "chuong trinh/promotion. Chi tap trung vao cac chi tiet lien "
            "quan nhat, giai thich ro rang, ngan gon, de hieu."
        ),
    },
    {
        "time": "19-28s",
        "scene": "Solution",
        "desc": (
            "Giai thich WeMasterTrade/WeGolden giup giai quyet van de o Pain "
            "Point nhu the nao. Ket noi ro rang giai phap voi moi lo cua "
            "nguoi xem, highlight TOI DA 3 loi ich/tinh nang lien quan."
        ),
    },
    {
        "time": "29-34s",
        "scene": "Conclusion",
        "desc": (
            "Tom tat ngan gon key message va nhac lai main takeaway. Ngan "
            "gon, ro rang, ket noi tu nhien sang CTA."
        ),
    },
    {
        "time": "35-40s",
        "scene": "CTA + Disclaimer",
        "desc": (
            "Ket bang 1 CTA ro rang, tu nhien (tim hieu them / truy cap "
            "website chinh thuc / dang ky chuong trinh / kham pha san pham). "
            "Kem disclaimer rui ro ngan gon, hien thi ro rang tren man hinh."
        ),
    },
]

DEFAULT_DISCLAIMER_VI = (
    "Mọi nội dung chỉ mang tính tham khảo và giải trí, tuyệt đối không phải là "
    "lời khuyên tài chính hay đầu tư; thị trường luôn có rủi ro mất vốn và bạn "
    "phải tự chịu trách nhiệm hoàn toàn cho mọi quyết định của mình."
)

# ----------------------------------------------------------------------------
# 3. CONTENT AND COMPLIANCE RULES (moi, bat buoc tuan thu nghiem ngat)
# ----------------------------------------------------------------------------
COMPLIANCE_RULES_VI = """
- No Guarantees: KHONG BAO GIO hua hen profit, payout, hay thanh cong.
- No Forbidden Terms: TRANH cac tu "risk-free", "guaranteed income",
  "easy money" hoac tuong duong tieng Viet ("khong rui ro", "loi nhuan dam
  bao", "kiem tien de dang").
- No Financial Advice: KHONG BAO GIO dua ra loi khuyen dau tu/tai chinh ca
  nhan.
- No Exaggerated Claims: TRANH claim vuot troi khong co can cu, hinh anh
  giau co phong dai.
- Simple & Professional: ngon ngu ro rang, tone than thien, dang tin cay.
- Accurate Details: cac rule/gia/ngay thang phai chinh xac dung nhu thong
  tin duoc cung cap, dan link ve website chinh thuc (wemastertrade.com hoac
  wegolden.com) de xem day du dieu khoan.
""".strip()

# ----------------------------------------------------------------------------
# 4. VOICEOVER STYLE GUIDE (theo dung docx chuan + fix da chot: cau noi muot)
# ----------------------------------------------------------------------------
VOICEOVER_STYLE_VI = """
- Tone: Natural, friendly, trustworthy, professional - nhu mot mentor co
  kinh nghiem, thien ve educational hon la promotional.
- Vibe: Conversational, gan gui, KHONG duoc qua trang trong hay sales.
- Phrasing: truc tiep, tu nhien (vi du: "Here's what you should know,"
  "Let's break it down").
- Pacing: cau ngan, chuyen y muot ma, nang luong cuon hut nhung khong phong
  dai.
- Tranh: van phong robot/cung nhac, thuat ngu phuc tap, claim khong co can
  cu, CTA hung han/ep buoc.
- QUAN TRONG (fix da chot): toan bo voiceover 6 scene khi doc lien tiep phai
  nghe nhu MOT NGUOI DUY NHAT dang noi chuyen lien tuc, KHONG duoc roi rac
  tung doan doc lap. Moi scene (tru Hook) PHAI mo dau bang 1 cum tu noi/
  chuyen y tu scene truoc (vi du: "But here's the thing...", "So here's
  what most people miss...", "That's exactly why...", "Now, here's the good
  news...").
""".strip()

# ----------------------------------------------------------------------------
# 5. AI PRESENTER BASE (theo docx chuan) - se duoc adapt theo region trong prompt
# ----------------------------------------------------------------------------
AI_PRESENTER_BASE_VI = """
- Age: 28-38 tuoi.
- Expression: am ap, gan gui, tu tin.
- Attire: smart-casual.
- Body Language: cu chi tay tu nhien, giao tiep bang mat truc tiep voi
  camera.
- Setting: modern trading office.
(Luu y: ngoai hinh/dac diem chung toc phai duoc ADAPT theo khu vuc/thi
truong muc tieu cua video nay - vi du chau A thi toc den mat nau, Latin
America thi dac diem nguoi Latin, v.v.)
""".strip()

# ----------------------------------------------------------------------------
# 6. VISUAL DIRECTION RULES (docx chuan ve do chi tiet + fix da chot ve tach
#    biet AI speaker / screen-recording-UGC nghiem ngat)
# ----------------------------------------------------------------------------
VISUAL_DIRECTION_RULES_VI = """
Moi scene phai mo ta du 4 phan (theo docx chuan), nhung PHAI tuan thu nghiem
ngat nguyen tac tach biet mode (fix da chot tu phan hoi thuc te):

Moi scene CHI duoc chon DUNG MOT trong hai mode, KHONG duoc tron lan trong
cung 1 scene:

MODE A - AI speaker: dung/ngoi mot cho, nhin thang camera hoac ban 3/4, chi
noi chuyen. KHONG co yeu to nao khac xuat hien cung luc (khong UGC, khong
screen recording, khong picture-in-picture cua bat ky thu gi khac).

MODE B - Screen recording HOAC UGC/b-roll: quay man hinh (dashboard, product
card, chart, app) HOAC canh quay doi thuc mot trader dang the hien cam xuc/
hanh dong don gian. TUYET DOI KHONG chen AI speaker vao (khong PIP). Khong
them nhan vat phu nao khac "dien".

Rieng WeGolden: mascot duoc PHEP xuat hien cameo NGAN (gat dau/gio tay/chi
nhe, 1-2 giay) trong ca 2 mode, o 2-3 scene khong lien tiep, nhung khong
duoc bien scene thanh "nhieu nhan vat cung dien" - mascot chi la brand cue,
khong phai nhan vat chinh.

Voi moi scene, mo ta ro 4 phan sau (khong can ghi nhan "Mode A/B" ra output,
chi can mo ta tu nhien):
1. AI Speaker (neu la Mode A): vi tri, bieu cam, cu chi, huong nhin, hanh
   dong.
2. On-screen Text: wording chinh xac (dung dung noi dung cot onscreen_text),
   thoi diem xuat hien, vi tri, tu nao duoc highlight, kieu animation don
   gian (fade/pop-up, KHONG dung hieu ung phuc tap).
3. Supporting Visuals (neu la Mode B): screen recording/dashboard/product
   card/chart/b-roll/icon - phai la NOI DUNG THAT tren 1 man hinh duy nhat,
   KHONG phai nhieu lop do hoa dong chong len nhau.
4. Editing: khung hinh, thu tu hinh anh, kieu chuyen canh (cut cung, khong
   dung hieu ung phuc tap nhu vong lap chu chay/card 3D xoay/particle bay).

KHONG mo ta cac hieu ung nhu "vong lap chu chay", "card 3D xoay", "particle
bay", "chart 3D animation phuc tap", "AI speaker picture-in-picture" - giu
that don gian, quay duoc thuc te, dung 1 layer hinh anh chinh cho moi scene.
""".strip()

# ----------------------------------------------------------------------------
# 7. REFERENCE NOTE (khong dung link that - xem ly do o dau file)
# ----------------------------------------------------------------------------
REFERENCE_NOTE_RULE_VI = """
Cot Reference: KHONG duoc bia link video (Gemini khong the tra cuu internet
that trong cung 1 lan goi structured output, moi link tu sinh deu co nguy co
la link gia/sai). Thay vao do, mo ta NGAN GON phong cach video tham khao ma
editor nen tu tim tren TikTok/YouTube Shorts/Instagram Reels de dung theo
(vi du: "Tim video AI speaker mentor-style, nhin thang camera, background
van phong tai chinh hien dai" hoac "Tim UGC clip trader that dang xem chart
tren dien thoai, anh sang tu nhien"). KHONG duoc dien bat ky URL/link nao.
""".strip()

# ----------------------------------------------------------------------------
# 8. Full core guideline text (dung de nhoi vao prompt Gemini)
# ----------------------------------------------------------------------------
CORE_GUIDELINE_VI = f"""
=== INFORMATION ===
Brand: WeMasterTrade hoac WeGolden.
Core topic: 1 package/promotion/programme/trading tip cu the (do nguoi dung
brief).
Target audience (chon nhom phu hop nhat voi topic, co the ket hop nhieu
nhom): {", ".join(TARGET_AUDIENCE_OPTIONS)}.

=== VIDEO OBJECTIVE ===
{VIDEO_OBJECTIVE_VI}

=== VIDEO FORMAT ===
{VIDEO_FORMAT_VI}

=== VOICEOVER STYLE GUIDE ===
{VOICEOVER_STYLE_VI}

=== AI PRESENTER BASE (adapt theo region) ===
{AI_PRESENTER_BASE_VI}

=== VISUAL DIRECTION RULES ===
{VISUAL_DIRECTION_RULES_VI}

=== REFERENCE NOTE RULE ===
{REFERENCE_NOTE_RULE_VI}

=== CONTENT AND COMPLIANCE RULES (bat buoc tuan thu nghiem ngat) ===
{COMPLIANCE_RULES_VI}

=== RIENG CHO WEGOLDEN ===
Phai kheo leo long ghep mascot cua brand vao Visual Direction de tang do
nhan dien, chi can xuat hien cameo ngan o 2-3 scene (xem chi tiet o phan
VISUAL DIRECTION RULES).
""".strip()

# ----------------------------------------------------------------------------
# Brand config: quyet dinh cot nao xuat hien trong bang Excel + accent color
# ----------------------------------------------------------------------------
BRANDS = {
    "WeMasterTrade": {
        "key": "wemastertrade",
        "mascot": False,
        "localizable": True,  # co the co cot Voice adapt / Text adapt
        "header_fill": "F9CB9C",   # cam dam (dong Item/Guideline)
        "label_fill": "FCE5CD",    # cam nhat (cac dong label)
        "table_header_fill": "FCE5CD",
        "adapt_fill": "F5F3E4",
        "official_site": "wemastertrade.com",
        "sample_ai_speaker_note": (
            "A warm, approachable 32-year-old Latin American man, friendly and "
            "confident expression, short dark hair with light stubble. Wearing a "
            "casual navy blazer over a white T-shirt, no tie. Modern trading office "
            "background, soft warm lighting, subtle city skyline through the window. "
            "Cinematic lighting on face, 4k resolution, professional but relatable "
            "studio quality, trustworthy and encouraging expression."
        ),
    },
    "WeGolden": {
        "key": "wegolden",
        "mascot": True,
        "localizable": False,
        "header_fill": "A2C4C9",   # xanh teal dam
        "label_fill": "A2C4C9",
        "table_header_fill": "D0E0E3",
        "adapt_fill": "F5F3E4",
        "official_site": "wegolden.com",
        "sample_ai_speaker_note": (
            "A professional male financial market presenter, 30-35 years old, "
            "confident and trustworthy, wearing a dark navy blazer with a white "
            "shirt, no tie. Modern trading office background with screens showing "
            "market charts, clean fintech style, cinematic lighting, medium shot "
            "from waist up, looking directly at the camera. Calm mentor-like "
            "expression, natural hand gesture, vertical 9:16, high-quality studio "
            "look.\n\nNegative Prompt:\nNo luxury lifestyle, no cash, no exaggerated "
            "profit visuals, no aggressive sales expression, no crowded background, "
            "no blurry face, no unrealistic skin texture."
        ),
    },
}

GEMINI_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
]

PLATFORMS = ["Facebook", "TikTok", "Instagram Reels"]

# ----------------------------------------------------------------------------
# Ngon ngu ban dia hoa: danh sach mau de chon nhanh tren UI (dropdown), thay vi
# go tay tu do - tranh go sai ten ngon ngu.
# ----------------------------------------------------------------------------
LANGUAGE_PRESETS = [
    "Spanish (Latin America)",
    "Portuguese (Brazil)",
    "Uzbek",
    "Kazakh",
    "Arabic",
    "Hindi",
    "Indonesian",
    "Thai",
    "French",
]

# Mot so thi truong bat buoc phai kem them ngon ngu khac (vi du: Kazakhstan
# thuong dung chung campaign voi Uzbekistan). Khi user chon ngon ngu o key,
# tu dong bo sung them cac ngon ngu trong value (khong trung lap).
LANGUAGE_AUTO_INCLUDE = {
    "Kazakh": ["Uzbek"],
}

# Ma ngan cho ten ngon ngu, dung lam nhan cot trong Excel (vd "Voice adapt
# (KZ)") cho gon, thay vi ghi day du ten.
LANGUAGE_CODES = {
    "spanish (latin america)": "ES",
    "portuguese (brazil)": "PT",
    "uzbek": "UZ",
    "kazakh": "KZ",
    "arabic": "AR",
    "hindi": "HI",
    "indonesian": "ID",
    "thai": "TH",
    "french": "FR",
}


def get_language_code(language: str) -> str:
    key = language.strip().lower()
    if key in LANGUAGE_CODES:
        return LANGUAGE_CODES[key]
    letters = "".join(ch for ch in language if ch.isalpha())
    return (letters[:2] or language[:2]).upper()


# Bang mau: moi ngon ngu duoc gan 1 mau rieng (header dam + nen o nhat), lap
# lai theo vong neu co nhieu ngon ngu hon so mau. Dung xuyen suot ca cot Voice
# adapt va Text adapt cua cung 1 ngon ngu de de phan biet bang mat.
LANGUAGE_COLOR_PALETTE = [
    {"header": "2E5C8A", "cell": "D9E5F5"},  # xanh duong
    {"header": "A94442", "cell": "F5DADA"},  # do/hong
    {"header": "3D7A3D", "cell": "DCF0DC"},  # xanh la
    {"header": "B8860B", "cell": "FBF0D9"},  # vang gold
    {"header": "6A3D9A", "cell": "E8DCF5"},  # tim
    {"header": "1F7A8C", "cell": "D9F0F3"},  # teal
]

# ==============================================================================
# REDDIT CONTENT MODE
# Trich tu "Reddit research.xlsx" (sheet "Content cho khách") - viet duoi giong
# mot trader/khach hang THAT dang chia se trai nghiem ca nhan, KHONG phai tai
# khoan chinh thuc cua brand (khong co dong "Disclosure: I work with..."), phu
# hop dung tinh chat "dong vai 1 nguoi choi thuc thu dang choi".
# ==============================================================================

REDDIT_FORMATS = [
    "Experience Post",
    "Insight Post",
    "Discussion Post",
    "First-Impression Post",
    "Community Question",
    "Advice-Seeking Post",
    "Educational Post",
]

REDDIT_GUIDELINE_VI = """
VAI TRO: Ban dang viet content Reddit DUOI GIONG MOT KHACH HANG/TRADER THAT su
dung san pham cua brand, KHONG PHAI tai khoan chinh thuc cua cong ty. Vi vay
KHONG duoc them dong disclosure kieu "I work with WeMasterTrade" - bai viet
phai doc tu nhien nhu 1 nguoi dung that dang chia se trai nghiem ca nhan tren
subreddit ve trading/prop firm.

NEN lam:
- Viet o ngoi thu nhat ("I"), van phong thoai mai, tu nhien, giong dang tam su
  that long voi cong dong, khong sales, khong marketing.
- Neu ro boi canh cu the: chuyen gi xay ra, cam xuc/suy nghi luc do, bai hoc
  rut ra hoac dieu chua hoan hao/gioi han cua trai nghiem (khong chi toan loi
  khen mot chieu).
- Ket bai bang 1 cau hoi mo de moi cong dong thao luan/chia se lai (hau het
  bai mau deu ket bang cau hoi).
- Neu co nhac ten brand (WeMasterTrade/WeGolden), phai nhac 1 cach tu nhien,
  trong ngu canh trai nghiem ca nhan, KHONG chèn link ban hang.
- Tieu de (Topic) khong duoc viet hoa toan bo, khong giat gan, khong hua hen
  ket qua ("guaranteed", "100% profit"...).

TRANH lam:
- Khong duoc gan link website/link ban hang trong noi dung.
- Khong duoc dung tu ngu qua trang trong/PR, khong dung nhieu emoji/hashtag
  (khac voi content Facebook/TikTok - Reddit rat ky content mang tinh quang
  cao lo lieu).
- Khong duoc hua hen loi nhuan/ket qua chac chan (dung CONTENT AND COMPLIANCE
  RULES nhu voi video).
- Khong duoc lap lai dung 1 cau mo dau/cau truc cho nhieu bai (moi bai phai
  co giong dieu, tinh huong rieng, tranh cam giac "cung 1 khuon").

CAC FORMAT PHO BIEN (co the dung lam goi y, khong bat buoc chi dung dung 7
loai nay):
- Experience Post: ke lai 1 trai nghiem/tinh huong cu the da xay ra.
- Insight Post: chia se 1 bai hoc/nhan ra dieu gi do sau khi trade.
- Discussion Post: dat van de de cong dong cung ban luan.
- First-Impression Post: cam nhan ban dau khi moi dung san pham/dich vu.
- Community Question: hoi cong dong ve 1 chu de lien quan.
- Advice-Seeking Post: xin loi khuyen tu cong dong ve 1 tinh huong dang gap.
- Educational Post: chia se kien thuc/checklist huu ich (van o goc do ca
  nhan, khong phai giong huan luyen vien).

COT "IMAGE": phan lon bai KHONG can anh (chi la text discussion). Neu can, chi
ghi chu ngan loai anh nen dung (vi du: "Screenshot dashboard co che thong tin
ca nhan", "Khong can anh vi chu yeu la discussion"), KHONG bia link/URL anh.
""".strip()

# ==============================================================================
# EVENT ANNOUNCEMENT MODE
# Bai dang social gioi thieu/quang ba 1 su kien offline (meetup, hoi thao...)
# ==============================================================================

EVENT_GUIDELINE_VI = """
Muc dich: viet bai dang social (Facebook/Instagram/Telegram) GIOI THIEU/QUANG
BA 1 su kien offline cua brand (vi du: meetup, hoi thao, networking event).

CAU TRUC BAT BUOC (dung theo dung thu tu, giong mau da duyet):
1. Headline/Hook: 1 dong mo dau co emoji, gay hao hung/FOMO nhe, neu ten su
   kien + ngam y "sap dien ra" (vi du: "Is Coming!", "Sap dien ra!").
2. Doan mo ta ngan (1-2 doan): gioi thieu ngan gon su kien mang lai gia tri
   gi cho nguoi tham du (ket noi, hoc hoi, gap go doi ngu/cong dong, cac
   hoat dong noi bat cua chuong trinh).
3. "Event Details:" - liet ke CHINH XAC theo thong tin duoc cung cap (TUYET
   DOI KHONG duoc bia them/doi sai ngay gio dia diem): Date, Time, Venue,
   Registration Opens, Registration Closes (dung emoji 📍 cho thong tin dia
   diem/thoi gian, 📝 cho thong tin dang ky).
4. 1 dong tao urgency/FOMO ve viec slot co han, khuyen khich dang ky ngay
   (dung emoji 🔥).
5. CTA dang ky: "Sign Up Here: [link]" (dung emoji 👉), dung DUNG link duoc
   cung cap, TUYET DOI KHONG duoc bia link khac.
6. Hashtag: 5-8 hashtag lien quan brand + ten su kien + dia diem + chu de
   nganh (prop trading/trading community/trading education), giu nguyen
   tieng Anh du bai viet bang ngon ngu khac (hashtag la quy uoc chung, khong
   can dich).

QUY TAC:
- Thong tin ngay/gio/dia diem/link PHAI CHINH XAC 100% theo du lieu duoc
  cung cap, KHONG duoc tu suy dien hay lam tron sai.
- Tone: hao hung, chuyen nghiep, mang tinh cong dong - KHONG duoc claim loi
  nhuan/hua hen ket qua giao dich (van ap dung CONTENT AND COMPLIANCE RULES
  nhu video).
- Moi bai phai co goc do (angle) trien khai rieng, KHONG lap lai y het nhau
  (vi du: 1 bai nhan manh phan thuong bocam thang/lucky draw, 1 bai nhan
  manh co hoi ket noi voi cong dong/dien gia khach moi, 1 bai nhan manh
  deadline dang ky sap het, 1 bai nhan manh duoc gap doi ngu WeMasterTrade
  truc tiep, 1 bai nhan manh cac hoat dong/lich trinh su kien...).
""".strip()

# ==============================================================================
# CEO INTERVIEW SERIES MODE
# Trich tu "WeGolden Video Research - CW.xlsx" (sheet Overview + Plan reels +
# EP01/EP04/EP05) - khac voi mode Video Reel Script (AI speaker), mode nay
# dung CEO/nhan vat that lam nguoi noi (KHONG phai AI speaker), theo dung
# format series "Inside the Golden Mind" cua WeGolden.
# ==============================================================================

CEO_DEFAULT_SERIES_NAME = "Inside the Golden Mind"
CEO_DEFAULT_TALENT = "David - CEO (WeGolden)"
CEO_DEFAULT_DURATION = "45-60 seconds - Reels"
CEO_DEFAULT_DISCLAIMER_EN = "Shared for educational purposes only. Trading involves risk and may not be suitable for everyone."

CEO_PILLARS = {
    "Gold Trading Compass": "Cẩm nang giao dịch vàng, mẹo chọn sàn uy tín và cách né bẫy lừa đảo.",
    "Gold Lens": "Góc nhìn vĩ mô, biến động và phân tích thị trường vàng.",
    "Behind the Platform": "Công nghệ, copy trade, khớp lệnh và trải nghiệm trader.",
    "Built on Trust": "Tầm nhìn, sứ mệnh, câu chuyện thương hiệu và triết lý minh bạch.",
}

# 8 section co dinh, dung THEO DUNG thu tu va ten trong 3 tap mau da lam
# (EP01/EP04/EP05) - day la "form co dinh" cho mode nay.
CEO_SECTION_STRUCTURE = [
    {
        "section": "Hook",
        "desc": (
            "Mo dau TRUC TIEP bang 1 cau/cau hoi tao tension hoac thach thuc 1 "
            "gia dinh quen thuoc. KHONG chao hoi thong thuong. CEO noi thang "
            "vao camera, medium close-up, eye-level."
        ),
    },
    {
        "section": "Intro",
        "desc": (
            "Chi la bumper graphic ten series ('Inside the Golden Mind'), "
            "KHONG co CEO Script (de rong). On-screen Text = ten series. "
            "Visual Direction ngan gon vi Intro/Outro da co san template rieng."
        ),
    },
    {
        "section": "Problem",
        "desc": (
            "Nhac lai/giai quyet Episode Key cua tap TRUOC (theo dung Series "
            "Story Rule), roi neu ra van de/cau hoi cot loi cua TAP NAY. Giu "
            "CEO la chu the chinh, co the cat rat ngan sang B-roll minh hoa "
            "roi quay lai CEO."
        ),
    },
    {
        "section": "CEO Perspective",
        "desc": (
            "Quan diem CA NHAN cua CEO ve van de vua neu, dung ngoi thu nhat "
            "('For me...', 'Here's the thing...', 'I believe...'). Giu CEO "
            "tren hinh xuyen suot phan nay (khong B-roll) vi day la goc nhin "
            "ca nhan. On-screen text co the hien tu khoa dong bo theo nhip "
            "voice (vi du 3 tu khoa xuat hien lan luot)."
        ),
    },
    {
        "section": "Solution",
        "desc": (
            "Ket noi quan diem sang cach WeGolden tiep can van de - GIAI "
            "THICH TAI SAO truoc khi noi CAI GI ('That's also how I think "
            "about WeGolden...'), KHONG duoc liet ke tinh nang kieu quang "
            "cao. Co the cat ngan sang B-roll san pham/nen tang."
        ),
    },
    {
        "section": "Key Takeaway",
        "desc": (
            "Chot lai bai hoc cot loi cua tap nay theo huong 'Golden Mind' "
            "(tu duy/triet ly), ngan gon, de nho. Close-up nhan manh su chan "
            "thanh cua CEO."
        ),
    },
    {
        "section": "Conclusion",
        "desc": (
            "Bac cau sang Next Episode Key (cau hoi mo dan vao tap tiep "
            "theo). Thuong dung goc rong/pull-back de tao cam giac khep lai "
            "1 nhip."
        ),
    },
    {
        "section": "Outro",
        "desc": (
            "Chi co On-screen Text dang 'CTA: ...' va 'DC: ...' (disclaimer), "
            "KHONG co CEO Script. Outro da co template rieng san."
        ),
    },
]

CEO_INTERVIEW_GUIDELINE_VI = """
=== KEY PERSONA & DELIVERY STYLE ===
CEO/Talent la nguoi noi chinh xuyen suot ca series (KHONG PHAI AI speaker),
dong vai thought leader chia se insight, chuyen mon va triet ly ve trading
va ve brand. Tone: Premium, calm, insightful, personal, leadership-driven.
Uu tien van phong ngoi thu nhat: "From my experience", "I believe", "Here's
the thing", "For me...". Cau ngan gon, co pause tu nhien, giao tiep bang mat
truc tiep, KHONG doc kich ban cung nhac.

=== MAIN OBJECTIVE & BRAND ROLE ===
Xay dung series thought leadership do CEO dan dat de xay dung niem tin, nhan
dien thuong hieu va tieng noi rieng cho WeGolden. Video giup nguoi xem hieu
cach 1 chuyen gia trong nganh nghi ve Gold, boi canh thi truong, danh gia
nen tang, cong nghe, minh bach, rui ro va niem tin - KHONG bien CEO thanh
nguoi ban hang. Brand la nen tang cung co cho quan diem CEO chia se, KHONG
phai chu the chinh.

=== CORE CONCEPT ===
Trading khong bat dau tu 1 danh sach tinh nang hay 1 thi truong don le. No
bat dau tu viec hieu ban dang trade cai gi, trade o dau, co the verify duoc
gi, va ra quyet dinh nhu the nao. "Golden Mind" dai dien cho goc nhin ro
rang hon, cau hoi tot hon, y thuc quan ly rui ro va hoc hoi lien tuc qua
tung quyet dinh.

=== TARGET AUDIENCE ===
Trader moi den trung cap, quen thuoc co ban ve Forex/Gold nhung chua chac
chan cach danh gia boi canh thi truong hay nen tang giao dich; quan tam den
rui ro, minh bach, chien luoc va cong nghe; de bi FOMO hoac phu thuoc qua
muc vao tool/tin hieu; dang tim hieu nen tang nhung khong thich content ban
hang lo lieu.

=== CONTENT MIX / RATIO ===
Khoang 70-80% la Education/Insight/Experience, chi 20-30% la Brand Bridge.
Bai hoc phai den TRUOC, WeGolden xuat hien tu nhien nhu 1 phan cua cau
chuyen, KHONG mo dau bang brand.

=== SERIES STORY RULE (BAT BUOC) ===
Moi tap PHAI lam 3 viec: 1) Giai quyet cau hoi/key cua tap TRUOC. 2) Truyen
tai DUNG 1 bai hoc/key rieng cho tap nay. 3) Mo ra DUNG 1 cau hoi/key moi
dan tu nhien sang tap tiep theo. Series spine: Explore → Understand →
Evaluate → Verify → Trust → Interpret → Manage Risk → Decide.

=== VIDEO OPENING / HOOK RULE ===
Mo dau NGAY bang 1 cau tao tension hoac thach thuc 1 gia dinh quen thuoc.
Hook luon dat TRUOC phan gioi thieu series. Tranh loi chao hoi chung chung
tru khi no tao dau an ca tinh.

=== WEGOLDEN BRAND INTEGRATION ===
Tranh liet ke tinh nang kieu "WeGolden co A, B, C". Giai thich TAI SAO truoc
CAI GI: "That belief is one reason we focus on...", "When we built
WeGolden, we wanted...". Nhac san pham chi de ho tro bai hoc, KHONG duoc
bien san pham thanh trong tam.

=== PRODUCT & TECH / COPY TRADING ORIENTATION ===
Khi noi ve cong nghe/nen tang, tap trung vao trai nghiem trader (ro rang,
giam ma sat, minh bach, linh hoat), tranh y "cang nhieu tinh nang cang tot".
Khi noi ve Copy Trading, KHONG mo ta no nhu cach loai bo rui ro - huong dan
nguoi xem danh gia drawdown, tinh nhat quan, phong cach trade, lich su hieu
suat va rui ro thay vi chi nhin loi nhuan tieu de.

=== FORMAT & FILMING ===
Social short-form, uu tien Reels/Shorts, ~45-60 giay. Quay truc tiep tai van
phong WeGolden, background sach, depth-of-field ro, anh sang manh, logo
WeGolden xuat hien tu nhien phia sau (nhan dien khong gian nhung khong lan
at khung hinh).

=== ON-SCREEN TEXT ===
Ngan gon, gan sat voi cau CEO dang noi. Moi nhip dung 1-3 tu khoa hoac 1 cum
ngan. Neu co nhieu tu khoa, phai xuat hien LAN LUOT dong bo theo nhip
voice (KHONG hien cung luc).

=== SERIES INTRO/OUTRO & CTA ===
Hook luon truoc, sau do la Intro series ngan (bumper graphic ten series +
logo), giong het nhau moi tap de tao ghi nho. Outro giu dong bo voi Intro:
ten series, WeGolden, 1 CTA nhe va disclaimer chuan. CTA cho tap giao duc:
"Follow for more" / "Follow Inside the Golden Mind". CTA cho tap huong san
pham: "Discover More" hoac dan ve website.

=== DISCLAIMER MAC DINH (outro, giu nguyen tieng Anh) ===
"{disclaimer}"

=== WHAT TO AVOID (TUYET DOI KHONG) ===
Bien CEO thanh nguoi ban hang; nhoi qua nhieu USP vao 1 video; tao ky vong
loi nhuan; du doan thi truong qua tu tin; dung ngon ngu "guaranteed result";
goi dich danh 1 nen tang cu the la "scam" ma khong co bang chung; lam dung
hieu ung thi giac lam giam do tin cay lanh dao.
""".strip().format(disclaimer=CEO_DEFAULT_DISCLAIMER_EN)
