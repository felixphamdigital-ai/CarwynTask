# -*- coding: utf-8 -*-
"""Tao mockup HTML dashboard (giao dien app trading), co the edit truc tiep
tren trinh duyet (contenteditable) va tai lai ban da sua thanh file HTML moi
de gui cho nguoi khac tu chinh sua tiep - khong can server/hosting gi ca."""

EXPORT_SCRIPT_SNIPPET = """
    document.getElementById("exportBtn").addEventListener("click", function () {
      var doctype = "<!DOCTYPE html>\\n";
      var html = doctype + "<html>" + document.documentElement.innerHTML + "</html>";
      var blob = new Blob([html], { type: "text/html;charset=utf-8" });
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a");
      a.href = url;
      a.download = "__FILENAME__";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
"""

EXPORT_BUTTON_HTML = """
  <button class="export-btn" type="button" id="exportBtn">💾 Tải bản đã sửa (.html) để gửi cho người khác</button>
"""

EXPORT_BUTTON_CSS = """
  .export-btn {
    width: 100%;
    padding: 12px;
    border-radius: 12px;
    border: 1.5px solid var(--accent-dim);
    background: var(--accent-wash);
    color: var(--accent);
    font: inherit;
    font-weight: 700;
    font-size: 13px;
    cursor: pointer;
    margin-top: 14px;
  }
  .export-btn:hover { background: var(--accent); color: __TEXT_ON_ACCENT__; }
"""


def _clamp(v):
    return max(0, min(255, int(round(v))))


def darken_hex(hex_color: str, factor: float) -> str:
    """factor < 1 lam toi mau (dung cho accent_dim/accent_wash)."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    r = _clamp(r * factor)
    g = _clamp(g * factor)
    b = _clamp(b * factor)
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def _text_on_accent(accent_hex: str) -> str:
    """Chon mau chu tren nen accent: toi neu accent sang, sang neu accent toi."""
    hex_color = accent_hex.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#171310" if luminance > 0.55 else "#f5f1e6"


def _brand_letter(brand_name: str) -> str:
    return (brand_name.strip()[:1] or "W").upper()


def _common_tokens(brand_name: str, accent_hex: str, filename: str) -> dict:
    return {
        "__BRAND_NAME__": brand_name,
        "__BRAND_LETTER__": _brand_letter(brand_name),
        "__ACCENT__": accent_hex,
        "__ACCENT_DIM__": darken_hex(accent_hex, 0.55),
        "__ACCENT_WASH__": darken_hex(accent_hex, 0.20),
        "__TEXT_ON_ACCENT__": _text_on_accent(accent_hex),
        "__FILENAME__": filename,
    }


def _apply_tokens(template: str, tokens: dict) -> str:
    for key, val in tokens.items():
        template = template.replace(key, val)
    return template


BASE_CSS = """
  :root {
    --bg: #0d0b08;
    --surface: #1a1610;
    --surface-2: #221c13;
    --border: #342c1c;
    --accent: __ACCENT__;
    --accent-dim: __ACCENT_DIM__;
    --accent-wash: __ACCENT_WASH__;
    --text: #f3efe4;
    --text-muted: #9c927c;
    --text-faint: #6e6552;
    --success: #5fae6a;
    --success-wash: #17241a;
    --danger: #c0524a;
    --danger-wash: #2a1815;
    --radius: 16px;
  }

  * { box-sizing: border-box; }

  html, body {
    margin: 0;
    padding: 0;
    background: var(--bg);
    color: var(--text);
  }

  body {
    font-family: -apple-system, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 15px;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    padding: 0 0 80px;
  }

  .top-bar {
    height: 6px;
    background: linear-gradient(90deg, var(--accent-dim), var(--accent), var(--accent-dim));
  }

  .page {
    max-width: 460px;
    margin: 0 auto;
    padding: 28px 18px 0;
  }

  .edit-hint {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    background: var(--accent-wash);
    border: 1px solid var(--accent-dim);
    color: var(--text);
    font-size: 12.5px;
    padding: 10px 13px;
    border-radius: 10px;
    margin-bottom: 22px;
  }

  .edit-hint strong { color: var(--accent); }

  .brand-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 22px;
  }

  .brand-mark {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: linear-gradient(155deg, var(--accent), var(--accent-dim));
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 14px;
    color: __TEXT_ON_ACCENT__;
    letter-spacing: -0.02em;
    flex: none;
  }

  .brand-name {
    font-size: 16px;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: var(--text);
  }

  .brand-name span { color: var(--accent); }

  [contenteditable="true"] {
    border-radius: 4px;
    padding: 1px 4px;
    margin: -1px -4px;
    outline: none;
  }

  [contenteditable="true"]:hover {
    background: rgba(255, 255, 255, 0.06);
    box-shadow: 0 0 0 1px var(--accent-dim);
  }

  [contenteditable="true"]:focus {
    background: rgba(255, 255, 255, 0.08);
    box-shadow: 0 0 0 2px var(--accent);
  }

  .card-remove {
    position: absolute;
    top: 12px;
    right: 12px;
    width: 22px;
    height: 22px;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: var(--surface-2);
    color: var(--text-faint);
    font-size: 13px;
    line-height: 1;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .card-remove:hover { color: var(--danger); border-color: var(--danger); }

  .add-row { margin-top: 4px; }

  .add-btn {
    width: 100%;
    padding: 12px;
    border-radius: var(--radius);
    border: 1.5px dashed var(--border);
    background: none;
    color: var(--text-muted);
    font: inherit;
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
  }

  .add-btn:hover { border-color: var(--accent-dim); color: var(--accent); }

  .footnote {
    margin-top: 22px;
    font-size: 11.5px;
    color: var(--text-faint);
    text-align: center;
    letter-spacing: 0.01em;
    padding-bottom: 10px;
  }
"""

SHARED_JS_HELPERS = """
    function wireEditable(root) {
      root.querySelectorAll('[contenteditable="true"]').forEach(function (el) {
        if (el.dataset.wired) return;
        el.dataset.wired = "1";
        el.addEventListener("focus", function () {
          var range = document.createRange();
          range.selectNodeContents(el);
          var sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(range);
        });
        el.addEventListener("keydown", function (e) {
          if (e.key === "Enter") {
            e.preventDefault();
            el.blur();
          }
        });
      });
    }
"""

# ==============================================================================
# TEMPLATE 1: ACCOUNT LIST (kieu FundedNext - danh sach nhieu the tai khoan)
# ==============================================================================

_ACCOUNT_LIST_TEMPLATE = """<title>__BRAND_NAME__ — My Accounts</title>
<style>
__BASE_CSS__

  .tabs {
    display: flex;
    gap: 28px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 22px;
  }

  .tab {
    background: none;
    border: none;
    font: inherit;
    color: var(--text-faint);
    font-size: 15px;
    font-weight: 600;
    padding: 0 0 12px;
    cursor: pointer;
    position: relative;
    letter-spacing: -0.01em;
  }

  .tab.is-active { color: var(--text); cursor: default; }

  .tab.is-active::after {
    content: "";
    position: absolute;
    left: 0; right: 0; bottom: -1px;
    height: 2px;
    background: var(--accent);
    border-radius: 2px 2px 0 0;
  }

  .segmented {
    display: inline-flex;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 4px;
    gap: 2px;
    margin-bottom: 26px;
  }

  .segment {
    border: none;
    font: inherit;
    font-size: 13.5px;
    font-weight: 600;
    padding: 7px 18px;
    border-radius: 999px;
    color: var(--text-muted);
    background: none;
    cursor: pointer;
    letter-spacing: 0.01em;
  }

  .segment.is-active { background: var(--accent); color: __TEXT_ON_ACCENT__; cursor: default; }

  .section-label {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: var(--text-faint);
    margin: 0 0 14px 2px;
  }

  .account-list { display: flex; flex-direction: column; gap: 12px; }

  .account-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px 20px;
    position: relative;
  }

  .account-head {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 14px;
    padding-right: 22px;
  }

  .account-title { font-weight: 700; font-size: 14.5px; color: var(--text); letter-spacing: -0.005em; }
  .account-title .divider { color: var(--text-faint); margin: 0 7px; font-weight: 400; }
  .account-title .size-badge { color: var(--accent); }

  .account-id-label { font-size: 12px; color: var(--text-faint); margin-right: 2px; }

  .redact-chip {
    height: 15px; width: 118px; border-radius: 4px;
    background: repeating-linear-gradient(135deg, var(--accent-dim), var(--accent-dim) 5px, var(--accent-wash) 5px, var(--accent-wash) 10px);
    display: inline-block; vertical-align: middle; flex: none;
  }

  .account-meta {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 9px 20px;
    border-top: 1px solid var(--border);
    padding-top: 13px;
  }

  .meta-item { display: flex; align-items: baseline; gap: 6px; font-size: 13.5px; white-space: nowrap; overflow: hidden; }
  .meta-item .k { color: var(--text-faint); flex: none; }
  .meta-item .v { color: var(--text); font-weight: 600; font-variant-numeric: tabular-nums; overflow: hidden; text-overflow: ellipsis; }
  .meta-item .v.gain { color: var(--accent); }

__EXPORT_BUTTON_CSS__

  @media (max-width: 480px) { .account-meta { grid-template-columns: 1fr; } }
</style>

<div class="top-bar"></div>
<div class="page">

  <div class="edit-hint">
    💡 <span><strong>Bấm trực tiếp</strong> vào bất kỳ số/chữ nào để sửa. Dùng nút <strong>+ Thêm account</strong> hoặc <strong>×</strong> để thêm/xoá thẻ. Sửa xong bấm nút tải bên dưới để lưu file gửi cho người khác.</span>
  </div>

  <div class="brand-row">
    <div class="brand-mark">__BRAND_LETTER__</div>
    <div class="brand-name">__BRAND_NAME__</div>
  </div>

  <div class="tabs">
    <button class="tab" type="button">CFDs</button>
    <button class="tab is-active" type="button">Futures</button>
  </div>

  <div class="segmented">
    <button class="segment is-active" type="button">Active</button>
    <button class="segment" type="button">Inactive</button>
    <button class="segment" type="button">Breached</button>
  </div>

  <div class="section-label">General Account</div>

  <div class="account-list" id="accountList">
    __ACCOUNT_CARDS__
  </div>

  <div class="add-row">
    <button class="add-btn" type="button" id="addAccountBtn">+ Thêm account</button>
  </div>

__EXPORT_BUTTON_HTML__

  <div class="footnote">Mockup dashboard — số liệu minh hoạ, không phải dữ liệu thật.</div>

</div>

<script>
  (function () {
__SHARED_JS__

    function wireTabsAndSegments(root) {
      root.querySelectorAll(".tabs .tab").forEach(function (btn) {
        btn.addEventListener("click", function () {
          root.querySelectorAll(".tabs .tab").forEach(function (b) { b.classList.remove("is-active"); });
          btn.classList.add("is-active");
        });
      });
      root.querySelectorAll(".segmented .segment").forEach(function (btn) {
        btn.addEventListener("click", function () {
          root.querySelectorAll(".segmented .segment").forEach(function (b) { b.classList.remove("is-active"); });
          btn.classList.add("is-active");
        });
      });
    }

    wireEditable(document);
    wireTabsAndSegments(document);

    document.getElementById("addAccountBtn").addEventListener("click", function () {
      var list = document.getElementById("accountList");
      var template = list.querySelector(".account-card");
      var clone = template.cloneNode(true);
      clone.querySelectorAll("[data-wired]").forEach(function (el) { delete el.dataset.wired; });
      var equity = clone.querySelector(".v.gain");
      if (equity) equity.textContent = "$0.00";
      var vs = clone.querySelectorAll(".v");
      if (vs[2]) vs[2].textContent = "$0.00";
      list.appendChild(clone);
      wireEditable(clone);
    });

__EXPORT_SCRIPT__
  })();
</script>
"""

_ACCOUNT_CARD_SNIPPET = """
    <div class="account-card">
      <button class="card-remove" type="button" title="Xoá account này" onclick="this.closest('.account-card').remove()">×</button>
      <div class="account-head">
        <div class="account-title">Futures Flex __BRAND_NAME__ Account<span class="divider">|</span><span class="size-badge" contenteditable="true" spellcheck="false">50K</span></div>
        <span class="account-id-label">Account:</span>
        <span class="redact-chip"></span>
      </div>
      <div class="account-meta">
        <div class="meta-item"><span class="k">Server Type:</span><span class="v" contenteditable="true" spellcheck="false">TRADOVATE</span></div>
        <div class="meta-item"><span class="k">Equity:</span><span class="v gain" contenteditable="true" spellcheck="false">__EQUITY__</span></div>
        <div class="meta-item"><span class="k">Balance:</span><span class="v" contenteditable="true" spellcheck="false">__EQUITY__</span></div>
        <div class="meta-item"><span class="k">Account Type:</span><span class="v" contenteditable="true" spellcheck="false">__BRAND_NAME__ Account</span></div>
      </div>
    </div>
"""

_DEFAULT_EQUITIES = ["$51,506.32", "$51,433.67", "$51,432.42", "$51,433.67", "$51,467.42"]


def build_account_list_html(brand_name: str = "WeMasterTrade", accent_hex: str = "#f5b400", num_cards: int = 5) -> str:
    filename = brand_name.lower().replace(" ", "_") + "_accounts_mockup.html"
    tokens = _common_tokens(brand_name, accent_hex, filename)

    cards_html = ""
    for i in range(num_cards):
        equity = _DEFAULT_EQUITIES[i % len(_DEFAULT_EQUITIES)]
        card = _ACCOUNT_CARD_SNIPPET.replace("__EQUITY__", equity)
        cards_html += card

    html = _ACCOUNT_LIST_TEMPLATE
    html = html.replace("__BASE_CSS__", BASE_CSS)
    html = html.replace("__EXPORT_BUTTON_CSS__", EXPORT_BUTTON_CSS)
    html = html.replace("__EXPORT_BUTTON_HTML__", EXPORT_BUTTON_HTML)
    html = html.replace("__SHARED_JS__", SHARED_JS_HELPERS)
    html = html.replace("__EXPORT_SCRIPT__", EXPORT_SCRIPT_SNIPPET)
    html = html.replace("__ACCOUNT_CARDS__", cards_html)
    html = _apply_tokens(html, tokens)
    return html


# ==============================================================================
# TEMPLATE 2: ACCOUNT OVERVIEW (kieu FundingPips - tong quan + challenge card)
# ==============================================================================

_ACCOUNT_OVERVIEW_TEMPLATE = """<title>__BRAND_NAME__ — Account Overview</title>
<style>
__BASE_CSS__

  .overview-card {
    position: relative;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 22px 22px 20px;
    overflow: hidden;
    margin-bottom: 18px;
  }

  .overview-watermark {
    position: absolute; top: -14px; right: -8px;
    font-size: 96px; opacity: 0.12;
    filter: grayscale(1) brightness(2.2) sepia(1) hue-rotate(-8deg) saturate(4);
    pointer-events: none; line-height: 1;
  }

  .greeting { font-size: 19px; font-weight: 700; margin: 0 0 4px; letter-spacing: -0.01em; position: relative; }
  .greeting-sub { font-size: 13px; color: var(--text-muted); margin: 0 0 18px; position: relative; }

  .stat-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; position: relative; }
  .stat-label { font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-faint); margin-bottom: 7px; }

  .rank-pill {
    display: inline-block; background: var(--accent-wash); color: var(--accent);
    border: 1px solid var(--accent-dim); font-size: 12.5px; font-weight: 700;
    padding: 4px 12px; border-radius: 999px;
  }

  .stat-value { font-size: 15px; font-weight: 700; font-variant-numeric: tabular-nums; }

  .buy-btn {
    width: 100%; background: var(--accent); color: __TEXT_ON_ACCENT__; border: none;
    border-radius: 12px; padding: 14px; font-size: 14.5px; font-weight: 800;
    letter-spacing: 0.03em; cursor: pointer; margin-bottom: 16px;
  }
  .buy-btn:hover { filter: brightness(1.08); }

  .filter-row { display: flex; gap: 8px; margin-bottom: 12px; }
  .filter-pill {
    flex: 1; display: flex; align-items: center; justify-content: space-between; gap: 6px;
    background: var(--surface); border: 1px solid var(--border); color: var(--text-muted);
    font-size: 12.5px; font-weight: 600; padding: 8px 11px; border-radius: 10px;
    cursor: pointer; white-space: nowrap; overflow: hidden;
  }
  .filter-pill span:first-child { overflow: hidden; text-overflow: ellipsis; }
  .filter-pill:hover { border-color: var(--accent-dim); color: var(--text); }
  .filter-pill .chev { color: var(--text-faint); flex: none; }

  .view-toggle-row { display: flex; justify-content: flex-end; gap: 8px; margin-bottom: 18px; }
  .view-icon-btn {
    display: flex; align-items: center; gap: 5px; background: var(--surface);
    border: 1px solid var(--border); color: var(--text-faint); border-radius: 8px;
    padding: 5px 9px; font-size: 13px; cursor: pointer;
  }
  .view-icon-btn .dot { width: 5px; height: 5px; border-radius: 50%; background: var(--text-faint); }
  .view-icon-btn:hover { color: var(--accent); border-color: var(--accent-dim); }
  .view-icon-btn:hover .dot { background: var(--accent); }

  .challenge-list { display: flex; flex-direction: column; gap: 12px; }
  .challenge-card { position: relative; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 18px 20px; }
  .challenge-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; padding-right: 22px; }
  .challenge-id { display: flex; align-items: center; gap: 7px; font-weight: 700; font-size: 15px; }
  .challenge-head-right { display: flex; align-items: center; gap: 8px; }

  .status-pill { font-size: 12px; font-weight: 700; padding: 4px 11px; border-radius: 999px; cursor: pointer; border: 1px solid transparent; }
  .status-pill.st-fail { background: var(--danger-wash); color: var(--danger); border-color: #4a2420; }
  .status-pill.st-pass { background: var(--success-wash); color: var(--success); border-color: #244a2c; }
  .status-pill.st-progress { background: var(--accent-wash); color: var(--accent); border-color: var(--accent-dim); }

  .more-btn { color: var(--text-faint); font-size: 16px; cursor: default; line-height: 1; padding: 2px 4px; }

  .challenge-sub { font-size: 13px; color: var(--text-muted); margin-bottom: 14px; padding-bottom: 14px; border-bottom: 1px solid var(--border); }
  .challenge-meta { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 20px; }
  .meta-block .k { font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-faint); margin-bottom: 4px; display: block; }
  .meta-block .v { font-size: 14.5px; font-weight: 700; font-variant-numeric: tabular-nums; }
  .meta-block .v.positive { color: var(--success); }
  .meta-block .v.negative { color: var(--danger); }

__EXPORT_BUTTON_CSS__
</style>

<div class="top-bar"></div>
<div class="page">

  <div class="edit-hint">
    💡 <span><strong>Bấm trực tiếp</strong> vào tên, số liệu, ID, trạng thái để sửa. Bấm vào pill trạng thái để đổi màu. Dùng <strong>+ Thêm challenge</strong> hoặc <strong>×</strong> để thêm/xoá thẻ. Sửa xong bấm nút tải bên dưới để lưu file gửi cho người khác.</span>
  </div>

  <div class="brand-row">
    <div class="brand-mark">__BRAND_LETTER__</div>
    <div class="brand-name">__BRAND_NAME__</div>
  </div>

  <div class="overview-card">
    <div class="overview-watermark">🏆</div>
    <p class="greeting">Hey, <span contenteditable="true" spellcheck="false">trader</span></p>
    <p class="greeting-sub">Your __BRAND_NAME__ account overview</p>
    <div class="stat-row">
      <div>
        <div class="stat-label">Trader Rank</div>
        <span class="rank-pill" contenteditable="true" spellcheck="false">Bronze Tier</span>
      </div>
      <div>
        <div class="stat-label">Reward Count</div>
        <div class="stat-value" contenteditable="true" spellcheck="false">0</div>
      </div>
      <div>
        <div class="stat-label">Total Rewards</div>
        <div class="stat-value" contenteditable="true" spellcheck="false">$0.00</div>
      </div>
    </div>
  </div>

  <button class="buy-btn" type="button">🚀 BUY CHALLENGE</button>

  <div class="filter-row">
    <div class="filter-pill"><span>All Types</span><span class="chev">⌄</span></div>
    <div class="filter-pill"><span>All Status</span><span class="chev">⌄</span></div>
    <div class="filter-pill"><span>All Phase</span><span class="chev">⌄</span></div>
  </div>

  <div class="view-toggle-row">
    <div class="view-icon-btn">▦<span class="dot"></span></div>
    <div class="view-icon-btn">☰<span class="dot"></span></div>
  </div>

  <div class="challenge-list" id="challengeList">

    <div class="challenge-card">
      <button class="card-remove" type="button" title="Xoá challenge này" onclick="this.closest('.challenge-card').remove()">×</button>
      <div class="challenge-head">
        <div class="challenge-id">👑 <span contenteditable="true" spellcheck="false">#20051777</span></div>
        <div class="challenge-head-right">
          <span class="status-pill st-fail" data-state="fail" contenteditable="true" spellcheck="false">Not Passed</span>
          <span class="more-btn">⋮</span>
        </div>
      </div>
      <div class="challenge-sub" contenteditable="true" spellcheck="false">$5k • 2 Step Standard • Max Drawdown 10%</div>
      <div class="challenge-meta">
        <div class="meta-block"><span class="k">Balance</span><span class="v" contenteditable="true" spellcheck="false">$5,034.79</span></div>
        <div class="meta-block"><span class="k">Next Reward</span><span class="v" contenteditable="true" spellcheck="false">Not scheduled</span></div>
        <div class="meta-block"><span class="k">P&amp;L</span><span class="v positive auto-sign" contenteditable="true" spellcheck="false">+$34.79</span></div>
        <div class="meta-block"><span class="k">Profit %</span><span class="v positive auto-sign" contenteditable="true" spellcheck="false">+0.7%</span></div>
      </div>
    </div>

  </div>

  <div class="add-row">
    <button class="add-btn" type="button" id="addChallengeBtn">+ Thêm challenge</button>
  </div>

__EXPORT_BUTTON_HTML__

  <div class="footnote">Mockup dashboard — số liệu minh hoạ, không phải dữ liệu thật.</div>

</div>

<script>
  (function () {
    var STATES = ["fail", "pass", "progress"];
    var STATE_LABEL = { fail: "Not Passed", pass: "Passed", progress: "In Progress" };

__SHARED_JS__

    function setPillState(pill, state) {
      pill.dataset.state = state;
      pill.classList.remove("st-fail", "st-pass", "st-progress");
      pill.classList.add("st-" + state);
    }

    function detectStateFromText(text) {
      var t = text.trim().toLowerCase();
      if (t.indexOf("not") !== -1 || t.indexOf("fail") !== -1 || t.indexOf("breach") !== -1 || t.indexOf("reject") !== -1) return "fail";
      if (t.indexOf("pass") !== -1 || t.indexOf("success") !== -1 || t.indexOf("approved") !== -1) return "pass";
      if (t.indexOf("progress") !== -1 || t.indexOf("pending") !== -1 || t.indexOf("active") !== -1 || t.indexOf("review") !== -1) return "progress";
      return null;
    }

    function wireStatusPill(pill) {
      if (pill.dataset.wiredClick) return;
      pill.dataset.wiredClick = "1";
      pill.addEventListener("click", function () {
        if (document.activeElement === pill) return;
        var current = pill.dataset.state || "fail";
        var next = STATES[(STATES.indexOf(current) + 1) % STATES.length];
        setPillState(pill, next);
        pill.textContent = STATE_LABEL[next];
      });
      pill.addEventListener("input", function () {
        var detected = detectStateFromText(pill.textContent);
        if (detected) setPillState(pill, detected);
      });
    }

    function wireFilters(root) {
      root.querySelectorAll(".filter-pill, .view-icon-btn").forEach(function (btn) {
        if (btn.dataset.wired) return;
        btn.dataset.wired = "1";
        btn.addEventListener("click", function () { btn.classList.toggle("is-active"); });
      });
    }

    function updateSign(el) {
      var t = el.textContent;
      el.classList.remove("positive", "negative");
      if (t.indexOf("-") !== -1) el.classList.add("negative");
      else if (t.indexOf("+") !== -1) el.classList.add("positive");
    }

    function wireAutoSign(root) {
      root.querySelectorAll(".auto-sign").forEach(function (el) {
        if (el.dataset.wiredSign) return;
        el.dataset.wiredSign = "1";
        el.addEventListener("input", function () { updateSign(el); });
      });
    }

    wireEditable(document);
    wireFilters(document);
    wireAutoSign(document);
    document.querySelectorAll(".status-pill").forEach(wireStatusPill);

    document.getElementById("addChallengeBtn").addEventListener("click", function () {
      var list = document.getElementById("challengeList");
      var template = list.querySelector(".challenge-card");
      var clone = template.cloneNode(true);
      clone.querySelectorAll("[data-wired]").forEach(function (el) { delete el.dataset.wired; });
      clone.querySelectorAll("[data-wired-click]").forEach(function (el) { delete el.dataset.wiredClick; });
      clone.querySelectorAll("[data-wired-sign]").forEach(function (el) { delete el.dataset.wiredSign; });
      var pill = clone.querySelector(".status-pill");
      pill.dataset.state = "fail";
      pill.className = "status-pill st-fail";
      pill.textContent = "Not Passed";
      clone.querySelectorAll(".auto-sign").forEach(updateSign);
      list.appendChild(clone);
      wireEditable(clone);
      wireAutoSign(clone);
      wireStatusPill(clone.querySelector(".status-pill"));
    });

__EXPORT_SCRIPT__
  })();
</script>
"""


def build_account_overview_html(brand_name: str = "WeMasterTrade", accent_hex: str = "#f5b400") -> str:
    filename = brand_name.lower().replace(" ", "_") + "_overview_mockup.html"
    tokens = _common_tokens(brand_name, accent_hex, filename)

    html = _ACCOUNT_OVERVIEW_TEMPLATE
    html = html.replace("__BASE_CSS__", BASE_CSS)
    html = html.replace("__EXPORT_BUTTON_CSS__", EXPORT_BUTTON_CSS)
    html = html.replace("__EXPORT_BUTTON_HTML__", EXPORT_BUTTON_HTML)
    html = html.replace("__SHARED_JS__", SHARED_JS_HELPERS)
    html = html.replace("__EXPORT_SCRIPT__", EXPORT_SCRIPT_SNIPPET)
    html = _apply_tokens(html, tokens)
    return html


MOCKUP_TEMPLATES = {
    "Account List (nhiều thẻ tài khoản — kiểu FundedNext)": build_account_list_html,
    "Account Overview (tổng quan + challenge — kiểu FundingPips)": build_account_overview_html,
}
