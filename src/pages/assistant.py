"""
SentraX Copilot — Database-Aware Security Assistant
====================================================
Every response is driven by live data from:
  • src.utils.database  → get_recent_scans()
  • src.utils.detector  → predict_url(), predict_sms()

No static rule-based responses. All answers are generated from
actual scan results, real threat scores, and live analysis.
"""

import re
import streamlit as st

from src.utils.detector import predict_url, predict_sms
from src.utils.database import get_recent_scans

# ---------------------------------------------------------------------------
# Shared robot SVG asset — single definition, reused everywhere
# ---------------------------------------------------------------------------
_BOT_ICON_CYAN = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2300f0ff'>"
    "<path d='M19 8h-1.07C17.48 5.72 14.97 4 12 4s-5.48 1.72-5.93 4H5c-1.1 0-2 "
    ".9-2 2v4c0 1.1.9 2 2 2h1.07C6.52 18.28 9.03 20 12 20s5.48-1.72 5.93-4H19c1.1 "
    "0 2-.9 2-2v-4c0-1.1-.9-2-2-2zM9 14c-.55 0-1-.45-1-1v-2c0-.55.45-1 1-1s1 .45 "
    "1 1v2c0 .55-.45 1-1 1zm6 0c-.55 0-1-.45-1-1v-2c0-.55.45-1 1-1s1 .45 1 1v2c0 "
    ".55-.45 1-1 1z'/></svg>"
)
_BOT_ICON_PINK = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23ff007f'>"
    "<path d='M19 8h-1.07C17.48 5.72 14.97 4 12 4s-5.48 1.72-5.93 4H5c-1.1 0-2 "
    ".9-2 2v4c0 1.1.9 2 2 2h1.07C6.52 18.28 9.03 20 12 20s5.48-1.72 5.93-4H19c1.1 "
    "0 2-.9 2-2v-4c0-1.1-.9-2-2-2zM9 14c-.55 0-1-.45-1-1v-2c0-.55.45-1 1-1s1 .45 "
    "1 1v2c0 .55-.45 1-1 1zm6 0c-.55 0-1-.45-1-1v-2c0-.55.45-1 1-1s1 .45 1 1v2c0 "
    ".55-.45 1-1 1z'/></svg>"
)

# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def _score_color(score: int) -> str:
    if score >= 70:
        return "#ff3b30"
    if score >= 50:
        return "#ffd60a"
    return "#00ff87"


def _label_badge(label: str, score: int) -> str:
    color = _score_color(score)
    bg = f"rgba({','.join(str(int(color.lstrip('#')[i:i+2], 16)) for i in (0,2,4))},0.12)"
    return (
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;'
        f'font-weight:700;padding:2px 8px;border:1px solid {color};'
        f'border-radius:4px;color:{color};background:{bg};">'
        f'{label.upper()}</span>'
    )


def _mini_bar(score: int) -> str:
    color = _score_color(score)
    return (
        f'<div style="width:100%;background:rgba(255,255,255,0.05);border-radius:6px;'
        f'height:8px;overflow:hidden;margin:6px 0 2px;">'
        f'<div style="width:{score}%;background:linear-gradient(90deg,#00f0ff,{color});'
        f'height:100%;box-shadow:0 0 6px {color};"></div></div>'
        f'<span style="font-size:10px;color:{color};">{score}/100</span>'
    )


def _reason_list(reasons: list) -> str:
    if not reasons:
        return '<span style="color:#00ff87;">No threat indicators detected.</span>'
    items = "".join(f"<li>{r}</li>" for r in reasons)
    return f"<ul style='margin:4px 0;padding-left:18px;'>{items}</ul>"


# ---------------------------------------------------------------------------
# Response builders — each calls a real project function and formats the result
# ---------------------------------------------------------------------------

def _respond_url_analysis(url: str) -> str:
    """Call predict_url() and build a full formatted response from real data."""
    normalized = url if url.startswith(("http://", "https://")) else f"http://{url}"
    try:
        result = predict_url(normalized)
    except Exception as exc:
        return (
            f"<b>[SENTRAX-COPI] // SCAN ERROR</b><br><br>"
            f"Could not reach <code>{url}</code>.<br>"
            f"Reason: <code>{exc}</code>"
        )

    score  = result["score"]
    label  = result["label"]
    tech   = result["technical"]
    color  = _score_color(score)

    rec = (
        "🚨 HIGH RISK — Do <b>not</b> enter credentials or click any links."
        if score >= 70 else
        "⚠️ MODERATE RISK — Verify domain ownership before proceeding."
        if score >= 50 else
        "✅ LOW RISK — No major threats detected. Stay generally cautious."
    )

    return f"""
<b>[SENTRAX-COPI] // URL THREAT ANALYSIS</b><br><br>
<code style="color:#8be8ff;">{url}</code><br><br>
{_label_badge(label, score)}&nbsp;&nbsp;
<span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:{color};">
  Score: {score}/100
</span><br>
{_mini_bar(score)}<br>
<b style="font-size:11px;">Threat Indicators:</b><br>
{_reason_list(result["reasons"])}
<b style="font-size:11px;">Technical Details:</b><br>
<span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#8be8ff;">
SSL: <b>{tech["SSL"]}</b> &nbsp;|&nbsp;
HTTPS: <b>{tech["HTTPS"]}</b> &nbsp;|&nbsp;
Redirects: <b>{tech["Redirects"]}</b><br>
IP-Based: <b>{tech["IP Based"]}</b> &nbsp;|&nbsp;
Keywords Hit: <b>{tech["Keyword Hits"]}</b> &nbsp;|&nbsp;
URL Length: <b>{tech["Length"]} chars</b>
</span><br><br>
<i style="color:#8be8ff;">{rec}</i>
"""


def _respond_sms_analysis(sms_text: str) -> str:
    """Call predict_sms() and build a formatted response from real data."""
    if not sms_text.strip():
        return (
            "<b>[SENTRAX-COPI]</b><br><br>"
            "Please provide the SMS text to analyze.<br>"
            "Example: <i>Analyze this SMS: You won a prize, claim now!</i>"
        )
    try:
        result = predict_sms(sms_text)
    except Exception as exc:
        return f"<b>[SENTRAX-COPI] // SMS SCAN ERROR</b><br><br>Error: <code>{exc}</code>"

    score = result["score"]
    label = result["label"]
    color = _score_color(score)

    verdict = (
        "🚨 Do <b>not</b> call numbers or click links in this message."
        if score >= 50 else
        "✅ Message appears clean. Stay cautious regardless."
    )

    return f"""
<b>[SENTRAX-COPI] // SMS SCAM ANALYSIS</b><br><br>
<i style="color:#8be8ff;">Message analyzed:</i><br>
<code style="font-size:10px;">"{sms_text[:120]}{'...' if len(sms_text)>120 else ''}"</code><br><br>
{_label_badge(label, score)}&nbsp;&nbsp;
<span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:{color};">
  Score: {score}/100
</span><br>
{_mini_bar(score)}<br>
<b style="font-size:11px;">Matched Scam Indicators:</b><br>
{_reason_list(result["reasons"])}
<i style="color:#8be8ff;">{verdict}</i>
"""


def _respond_last_scan() -> str:
    """Fetch the single most recent scan from the database and explain it."""
    try:
        rows = get_recent_scans(limit=1)
    except Exception as exc:
        return f"<b>[SENTRAX-COPI]</b><br>Database error: <code>{exc}</code>"

    if not rows:
        return (
            "<b>[SENTRAX-COPI] // NO SCAN HISTORY</b><br><br>"
            "No scans have been logged yet.<br>"
            "Use the <b>🔍 Scanner</b> page to scan a URL first, then ask me here."
        )

    url, label, score, ts = rows[0]
    color = _score_color(score)

    return f"""
<b>[SENTRAX-COPI] // LAST SCAN RESULT</b><br><br>
<code style="color:#8be8ff;">{url}</code><br><br>
{_label_badge(label, score)}&nbsp;&nbsp;
<span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:{color};">
  Score: {score}/100
</span><br>
{_mini_bar(score)}<br>
<span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#63768f;">
  Logged: {ts}
</span><br><br>
To get a full live breakdown, paste the URL directly in this chat.
"""


def _respond_recent_scans(limit: int = 5, threats_only: bool = False) -> str:
    """Fetch recent scans from the database and render them as a structured list."""
    try:
        rows = get_recent_scans(limit=limit)
    except Exception as exc:
        return f"<b>[SENTRAX-COPI]</b><br>Database error: <code>{exc}</code>"

    if not rows:
        return (
            "<b>[SENTRAX-COPI] // NO SCAN HISTORY</b><br><br>"
            "No scans have been logged yet.<br>"
            "Use the <b>🔍 Scanner</b> page to populate the database."
        )

    if threats_only:
        rows = [r for r in rows if r[1] == "Fraud / Phishing"]
        if not rows:
            return (
                "<b>[SENTRAX-COPI] // NO THREATS FOUND</b><br><br>"
                "No malicious URLs detected in recent scan history. ✅"
            )
        title = "RECENT THREATS DETECTED"
    else:
        title = f"RECENT {len(rows)} SCANS"

    total   = len(rows)
    fraud   = sum(1 for r in rows if r[1] == "Fraud / Phishing")
    safe    = total - fraud

    rows_html = ""
    for url, label, score, ts in rows:
        color = _score_color(score)
        rows_html += (
            f'<div style="border-left:3px solid {color};padding:6px 10px;'
            f'margin-bottom:8px;background:rgba(255,255,255,0.02);border-radius:0 6px 6px 0;">'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
            f'color:#fff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:280px;">'
            f'{url}</div>'
            f'<div style="display:flex;justify-content:space-between;margin-top:3px;">'
            f'<span style="font-size:10px;color:{color};">{label} — {score}/100</span>'
            f'<span style="font-size:10px;color:#63768f;">{ts}</span>'
            f'</div></div>'
        )

    summary = (
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#8be8ff;">'
        f'Total: <b>{total}</b> &nbsp;|&nbsp; '
        f'<span style="color:#ff3b30;">Malicious: <b>{fraud}</b></span> &nbsp;|&nbsp; '
        f'<span style="color:#00ff87;">Safe: <b>{safe}</b></span>'
        f'</span><br><br>'
    )

    return (
        f"<b>[SENTRAX-COPI] // {title}</b><br><br>"
        f"{summary}"
        f"{rows_html}"
    )


def _respond_db_summary() -> str:
    """Return overall database statistics using get_recent_scans()."""
    try:
        rows = get_recent_scans(limit=100)
    except Exception as exc:
        return f"<b>[SENTRAX-COPI]</b><br>Database error: <code>{exc}</code>"

    total = len(rows)
    if total == 0:
        return (
            "<b>[SENTRAX-COPI] // DATABASE STATUS</b><br><br>"
            "Database is empty — no scans logged yet.<br>"
            "Start scanning URLs on the <b>🔍 Scanner</b> page."
        )

    fraud = sum(1 for r in rows if r[1] == "Fraud / Phishing")
    safe  = total - fraud
    avg   = round(sum(r[2] for r in rows) / total, 1)
    rate  = round((fraud / total) * 100, 1)
    highest = max(rows, key=lambda r: r[2])

    return f"""
<b>[SENTRAX-COPI] // DATABASE SUMMARY</b><br><br>
<span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#8be8ff;">
  Total Scans Logged: <b style="color:#fff;">{total}</b><br>
  Malicious Detected: <b style="color:#ff3b30;">{fraud}</b><br>
  Safe / Clean: <b style="color:#00ff87;">{safe}</b><br>
  Threat Rate: <b style="color:#ffd60a;">{rate}%</b><br>
  Average Risk Score: <b style="color:#fff;">{avg}/100</b>
</span><br><br>
<b style="font-size:11px;">Highest Risk Scan:</b><br>
<div style="border-left:3px solid #ff3b30;padding:5px 10px;
            background:rgba(255,59,48,0.04);border-radius:0 6px 6px 0;">
  <code style="font-size:10px;color:#8be8ff;">{highest[0]}</code><br>
  <span style="font-size:10px;color:#ff3b30;">
    {highest[1]} — Score: {highest[2]}/100
  </span>
</div>
"""


def _respond_help() -> str:
    return """
<b>[SENTRAX-COPI] // ONLINE</b><br><br>
I am your <b>SentraX Security Assistant</b> — powered by live project data.<br><br>
<b>What I can do:</b><br>
<span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#8be8ff;">
▸ Analyze any URL you paste (live scan)<br>
▸ Analyze any SMS text for scam indicators<br>
▸ Show your last scan result from the database<br>
▸ Show recent scans and threat history<br>
▸ Show recent threats only<br>
▸ Show database summary and statistics<br>
</span><br>
<b>Example commands:</b><br>
<span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#63768f;">
• <i>Analyze https://suspicious-login.com</i><br>
• <i>Analyze this SMS: Claim your prize now!</i><br>
• <i>What was my last scan?</i><br>
• <i>Show recent threats</i><br>
• <i>Show recent scans</i><br>
• <i>Database summary</i>
</span>
"""


# ---------------------------------------------------------------------------
# Intent router — maps user input to project function calls, no static content
# ---------------------------------------------------------------------------

_URL_RE = re.compile(
    r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)'
)

# Keywords that indicate SMS analysis intent
_SMS_TRIGGERS = re.compile(
    r'(analyze\s+(this\s+)?sms|check\s+(this\s+)?sms|scan\s+(this\s+)?sms|'
    r'is\s+this\s+(sms|message|text)\s+(safe|scam|legit)|'
    r'analyze\s+(this\s+)?message|check\s+(this\s+)?message)',
    re.IGNORECASE
)

# Keywords for scan history queries
_LAST_SCAN_RE    = re.compile(r'\b(last\s+scan|most\s+recent\s+scan|latest\s+scan)\b', re.IGNORECASE)
_RECENT_SCANS_RE = re.compile(r'\b(recent\s+scans|scan\s+history|show\s+scans|all\s+scans)\b', re.IGNORECASE)
_THREATS_ONLY_RE = re.compile(r'\b(recent\s+threats|show\s+threats|malicious|phishing\s+results)\b', re.IGNORECASE)
_DB_SUMMARY_RE   = re.compile(r'\b(database|db\s+summary|statistics|stats|how\s+many\s+scans|total\s+scans)\b', re.IGNORECASE)
_GREET_RE        = re.compile(r'^\s*(hi|hello|hey|greetings|start|help|what\s+can\s+you\s+do)\b', re.IGNORECASE)


def get_assistant_response(query: str) -> str:
    """
    Route the user query to the correct project function.
    Priority: URL → SMS → last scan → threats → recent scans → db summary → greet → fallback
    """
    q = query.strip()

    # ── Detect SMS analysis (must check before URL, as SMS body may contain URLs) ──
    sms_match = _SMS_TRIGGERS.search(q)
    if sms_match:
        # Extract everything after the trigger phrase as the SMS body
        body_start = sms_match.end()
        sms_body = q[body_start:].lstrip(": \n\t")
        return _respond_sms_analysis(sms_body)

    # ── Detect URL anywhere in query ──────────────────────────────────────────
    url_matches = _URL_RE.findall(q)
    if url_matches:
        # Filter out common false positives (very short tokens)
        candidates = [u for u in url_matches if '.' in u and len(u) > 5]
        if candidates:
            return _respond_url_analysis(candidates[0])

    # ── Database queries ──────────────────────────────────────────────────────
    if _LAST_SCAN_RE.search(q):
        return _respond_last_scan()

    if _THREATS_ONLY_RE.search(q):
        return _respond_recent_scans(limit=10, threats_only=True)

    if _RECENT_SCANS_RE.search(q):
        return _respond_recent_scans(limit=5, threats_only=False)

    if _DB_SUMMARY_RE.search(q):
        return _respond_db_summary()

    # ── Greeting / help ───────────────────────────────────────────────────────
    if _GREET_RE.search(q):
        return _respond_help()

    # ── Fallback ──────────────────────────────────────────────────────────────
    return (
        "<b>[SENTRAX-COPI] // UNRECOGNIZED QUERY</b><br><br>"
        "I could not match your request to a known command. Try:<br>"
        "<span style='font-family:\"JetBrains Mono\",monospace;font-size:10px;color:#8be8ff;'>"
        "▸ Paste a URL to scan it live<br>"
        "▸ <i>Analyze this SMS: [your message]</i><br>"
        "▸ <i>What was my last scan?</i><br>"
        "▸ <i>Show recent threats</i><br>"
        "▸ <i>Database summary</i>"
        "</span>"
    )


# ---------------------------------------------------------------------------
# Copilot UI — floating panel (UI structure unchanged from original)
# ---------------------------------------------------------------------------

def render_copilot():

    # ── CSS ──────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <style>
    @keyframes pulse-glow {{
        0%   {{ box-shadow: 0 0 15px rgba(0,240,255,0.4); }}
        50%  {{ box-shadow: 0 0 26px rgba(0,240,255,0.7); }}
        100% {{ box-shadow: 0 0 15px rgba(0,240,255,0.4); }}
    }}

    /* Floating trigger — single CSS selector targeting the Streamlit key */
    div[data-testid="stButton"]:has(button[key="floating_copilot_trigger"]) button {{
        position: fixed !important; bottom: 25px !important; right: 25px !important;
        z-index: 999999 !important; width: 68px !important; height: 68px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, rgba(6,18,36,0.95), rgba(0,240,255,0.2)) !important;
        border: 1.5px solid rgba(0,240,255,0.4) !important;
        animation: pulse-glow 2.5s infinite ease-in-out !important;
        cursor: pointer !important; padding: 0 !important;
        color: transparent !important; font-size: 0 !important;
        background-image: url('{_BOT_ICON_CYAN}') !important;
        background-repeat: no-repeat !important;
        background-position: center !important; background-size: 32px !important;
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
    }}
    div[data-testid="stButton"]:has(button[key="floating_copilot_trigger"]) button:hover {{
        transform: scale(1.08) rotate(5deg) !important;
        border-color: #ff007f !important;
        box-shadow: 0 0 22px rgba(255,0,127,0.5) !important;
        background-image: url('{_BOT_ICON_PINK}') !important;
    }}

    /* Panel */
    .copilot-panel {{
        position: fixed !important; bottom: 105px !important; right: 25px !important;
        width: 360px !important; max-height: 530px !important;
        z-index: 999998 !important;
        background: rgba(4,12,24,0.97) !important;
        border: 1px solid rgba(0,240,255,0.22) !important;
        border-radius: 16px !important; backdrop-filter: blur(20px) !important;
        box-shadow: 0 10px 35px rgba(0,0,0,0.6), 0 0 20px rgba(0,240,255,0.1) !important;
        padding: 16px !important; display: flex !important;
        flex-direction: column !important; overflow: hidden !important;
    }}

    /* Chat area */
    .copilot-chat-area {{
        flex-grow: 1 !important; overflow-y: auto !important;
        max-height: 290px !important; margin-bottom: 8px !important;
        padding-right: 4px !important;
        scrollbar-width: thin !important;
        scrollbar-color: rgba(0,240,255,0.2) transparent !important;
    }}

    /* Bubbles */
    .copilot-bubble-user {{
        background: rgba(0,240,255,0.05) !important;
        border: 1px solid rgba(0,240,255,0.18) !important;
        border-radius: 10px 10px 2px 10px !important;
        padding: 8px 12px !important; margin: 0 0 8px 12% !important;
        font-size: 12px !important; color: #fff !important;
    }}
    .copilot-bubble-bot {{
        background: rgba(255,0,127,0.04) !important;
        border: 1px solid rgba(255,0,127,0.14) !important;
        border-radius: 10px 10px 10px 2px !important;
        padding: 8px 12px !important; margin: 0 12% 8px 0 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important; color: #d9f7ff !important;
        line-height: 1.5 !important;
    }}

    /* Close button */
    div[data-testid="stButton"]:has(button[key="close_copilot_btn"]) button {{
        position: fixed !important; bottom: 583px !important; right: 38px !important;
        z-index: 999999 !important; background: transparent !important;
        border: none !important; color: #63768f !important; font-size: 13px !important;
        padding: 0 !important; width: 22px !important; height: 22px !important;
        min-height: 22px !important; box-shadow: none !important; cursor: pointer !important;
        transition: color 0.2s ease !important;
    }}
    div[data-testid="stButton"]:has(button[key="close_copilot_btn"]) button:hover {{
        color: #ff007f !important; transform: none !important;
    }}

    /* Quick-prompt pills */
    div.element-container:has(button[key="q_last"])   {{ position:fixed !important; bottom:232px !important; right:198px !important; width:148px !important; z-index:999999 !important; }}
    div.element-container:has(button[key="q_threats"]){{ position:fixed !important; bottom:232px !important; right:38px  !important; width:148px !important; z-index:999999 !important; }}
    div.element-container:has(button[key="q_scans"])  {{ position:fixed !important; bottom:196px !important; right:198px !important; width:148px !important; z-index:999999 !important; }}
    div.element-container:has(button[key="q_stats"])  {{ position:fixed !important; bottom:196px !important; right:38px  !important; width:148px !important; z-index:999999 !important; }}

    div.element-container:has(button[key^="q_"]) button {{
        background: rgba(0,240,255,0.04) !important;
        border: 1px solid rgba(0,240,255,0.18) !important;
        color: #8be8ff !important; border-radius: 20px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 10px !important; padding: 4px 8px !important;
        min-height: 26px !important; box-shadow: none !important;
        width: 100% !important; transition: all 0.2s ease !important;
    }}
    div.element-container:has(button[key^="q_"]) button:hover {{
        background: rgba(255,0,127,0.08) !important;
        border-color: #ff007f !important; color: #fff !important;
        transform: translateY(-1px) !important;
    }}

    /* Input form */
    div.stForm:has(input[placeholder="Message SentraX Copilot..."]) {{
        position: fixed !important; bottom: 115px !important; right: 38px !important;
        width: 320px !important; z-index: 999999 !important;
        background: transparent !important; border: none !important;
        padding: 0 !important; margin: 0 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # ── Persistent session state — initialized once, never reset ─────────────
    if "copilot_messages" not in st.session_state:
        st.session_state.copilot_messages = [
            {"role": "assistant", "content": _respond_help()}
        ]
    if "copilot_open" not in st.session_state:
        st.session_state.copilot_open = False

    # ── Render open panel ────────────────────────────────────────────────────
    if st.session_state.copilot_open:

        # Build full chat HTML from all persisted messages
        chat_bubbles = ""
        for msg in st.session_state.copilot_messages:
            if msg["role"] == "user":
                chat_bubbles += (
                    f'<div class="copilot-bubble-user">'
                    f'<span style="font-family:\'JetBrains Mono\',monospace;'
                    f'font-size:10px;color:#8be8ff;">[YOU]</span><br>'
                    f'{msg["content"]}</div>'
                )
            else:
                chat_bubbles += (
                    f'<div class="copilot-bubble-bot">{msg["content"]}</div>'
                )

        st.markdown(f"""
        <div class="copilot-panel">
          <div style="display:flex;align-items:center;justify-content:space-between;
                      margin-bottom:12px;border-bottom:1px solid rgba(0,240,255,0.15);
                      padding-bottom:8px;">
            <div style="display:flex;align-items:center;gap:8px;">
              <img src="{_BOT_ICON_CYAN}" width="18" height="18"
                   style="filter:drop-shadow(0 0 4px #00f0ff);" />
              <span style="font-family:'Orbitron',sans-serif;font-size:12px;
                           font-weight:700;color:#fff;letter-spacing:1px;">
                SENTRAX COPILOT
              </span>
            </div>
            <span style="font-family:'JetBrains Mono',monospace;font-size:9px;
                         color:#00ff87;margin-right:26px;">● ONLINE</span>
          </div>
          <div class="copilot-chat-area" id="sentrax-chat-area">
            {chat_bubbles}
          </div>
        </div>
        <script>
          (function() {{
            var el = document.getElementById('sentrax-chat-area');
            if (el) el.scrollTop = el.scrollHeight;
          }})();
        </script>
        """, unsafe_allow_html=True)

        # Close button
        if st.button("✕", key="close_copilot_btn"):
            st.session_state.copilot_open = False
            st.rerun()

        # ── Quick-prompt pills (each calls a live project function) ───────────
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Last Scan", key="q_last"):
                st.session_state.copilot_messages.append(
                    {"role": "user", "content": "What was my last scan?"}
                )
                st.session_state.copilot_messages.append(
                    {"role": "assistant", "content": _respond_last_scan()}
                )
                st.rerun()
        with col2:
            if st.button("🚨 Recent Threats", key="q_threats"):
                st.session_state.copilot_messages.append(
                    {"role": "user", "content": "Show recent threats"}
                )
                st.session_state.copilot_messages.append(
                    {"role": "assistant", "content": _respond_recent_scans(limit=10, threats_only=True)}
                )
                st.rerun()

        col3, col4 = st.columns(2)
        with col3:
            if st.button("📂 Recent Scans", key="q_scans"):
                st.session_state.copilot_messages.append(
                    {"role": "user", "content": "Show recent scans"}
                )
                st.session_state.copilot_messages.append(
                    {"role": "assistant", "content": _respond_recent_scans(limit=5)}
                )
                st.rerun()
        with col4:
            if st.button("📊 DB Summary", key="q_stats"):
                st.session_state.copilot_messages.append(
                    {"role": "user", "content": "Database summary"}
                )
                st.session_state.copilot_messages.append(
                    {"role": "assistant", "content": _respond_db_summary()}
                )
                st.rerun()

        # ── Text input form ───────────────────────────────────────────────────
        with st.form("copilot_form", clear_on_submit=True):
            col_in, col_btn = st.columns([4, 1])
            with col_in:
                user_input = st.text_input(
                    "msg",
                    placeholder="Message SentraX Copilot...",
                    label_visibility="collapsed"
                )
            with col_btn:
                submitted = st.form_submit_button("⚡")

        if submitted and user_input.strip():
            st.session_state.copilot_messages.append(
                {"role": "user", "content": user_input.strip()}
            )
            st.session_state.copilot_messages.append(
                {"role": "assistant", "content": get_assistant_response(user_input.strip())}
            )
            st.rerun()

    # ── Floating trigger (single button, zero duplicates) ────────────────────
    if st.button("🤖", key="floating_copilot_trigger"):
        st.session_state.copilot_open = not st.session_state.copilot_open
        st.rerun()
