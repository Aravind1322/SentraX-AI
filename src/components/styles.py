import streamlit as st

def load_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }

    .stApp {
        background-color: #030712;
        background-image: 
            radial-gradient(at 0% 0%, rgba(0, 240, 255, 0.08) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(255, 0, 127, 0.06) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(0, 240, 255, 0.05) 0px, transparent 50%),
            linear-gradient(to right, rgba(255, 255, 255, 0.005) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.005) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 100% 100%, 40px 40px, 40px 40px;
    }

    /* Cyber Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 0.5px !important;
        color: #ffffff !important;
    }
    h1 {
        text-shadow: 0 0 15px rgba(0, 240, 255, 0.15) !important;
        font-weight: 700 !important;
    }

    /* Brand Header Styles */
    .brand {
        font-family: 'Orbitron', sans-serif;
        text-align: center;
        font-size: 54px;
        font-weight: 900;
        background: linear-gradient(90deg, #00f0ff, #8be8ff, #ff007f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 35px rgba(0,240,255,.3);
        letter-spacing: 2px;
        margin-top: 10px;
        margin-bottom: 5px;
    }

    .tag {
        text-align: center;
        color: #8be8ff;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-bottom: 30px;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.2);
    }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #020617 !important;
        border-right: 1px solid rgba(0, 240, 255, 0.12) !important;
        box-shadow: 5px 0 25px rgba(0, 0, 0, 0.5) !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] .brand {
        font-family: 'Orbitron', sans-serif !important;
        background: linear-gradient(90deg, #00f0ff, #ff007f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: none !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }

    /* Radio button navigation inside sidebar */
    div.row-widget.stRadio > div {
        background: rgba(6, 18, 36, 0.4) !important;
        border: 1px solid rgba(0, 240, 255, 0.1) !important;
        border-radius: 12px;
        padding: 10px !important;
    }
    div.row-widget.stRadio label {
        font-family: 'Inter', sans-serif;
        color: #d9f7ff !important;
        font-size: 14px !important;
        padding: 8px 12px !important;
        border-radius: 8px;
        transition: all 0.3s ease;
        margin-bottom: 4px !important;
        cursor: pointer;
    }
    div.row-widget.stRadio label:hover {
        background: rgba(0, 240, 255, 0.08) !important;
        color: #00f0ff !important;
        padding-left: 16px !important;
    }
    div.row-widget.stRadio label[data-checked="true"] {
        background: linear-gradient(90deg, rgba(0, 240, 255, 0.15), rgba(255, 0, 127, 0.05)) !important;
        border-left: 3px solid #00f0ff !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Glassmorphism Container */
    .glass {
        background: rgba(6, 18, 36, 0.45);
        border: 1px solid rgba(0, 240, 255, 0.15);
        border-radius: 20px;
        padding: 30px;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px rgba(0, 240, 255, 0.05);
        transition: all 0.3s ease;
        margin-bottom: 25px;
    }
    .glass:hover {
        border-color: rgba(0, 240, 255, 0.25);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5), 0 0 25px rgba(0, 240, 255, 0.08);
    }

    /* Buttons override */
    .stButton > button {
        background: rgba(6, 18, 36, 0.6) !important;
        color: #00f0ff !important;
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
        border-radius: 10px !important;
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 1.5px;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.05) !important;
        text-transform: uppercase;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.15), rgba(255, 0, 127, 0.1)) !important;
        color: #ffffff !important;
        border-color: #00f0ff !important;
        box-shadow: 0 0 18px rgba(0, 240, 255, 0.25) !important;
        transform: translateY(-2px);
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* Inputs & Textareas override */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: rgba(6, 18, 36, 0.4) !important;
        color: #ffffff !important;
        border: 1px solid rgba(0, 240, 255, 0.15) !important;
        border-radius: 10px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.5) !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #00f0ff !important;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.25), inset 0 2px 4px rgba(0, 0, 0, 0.5) !important;
        outline: none !important;
    }

    /* Metric Cards overriding */
    [data-testid="stMetric"] {
        background: rgba(6, 18, 36, 0.45) !important;
        border: 1px solid rgba(0, 240, 255, 0.15) !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25), 0 0 15px rgba(0, 240, 255, 0.03) !important;
        transition: all 0.3s ease !important;
        border-left: 4px solid #00f0ff !important;
    }
    [data-testid="stMetric"]:hover {
        border-color: #ff007f !important;
        border-left-color: #ff007f !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35), 0 0 20px rgba(255, 0, 127, 0.1) !important;
        transform: translateY(-2px);
    }
    [data-testid="stMetricValue"] > div {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.15) !important;
    }
    [data-testid="stMetricLabel"] > div {
        font-family: 'Inter', sans-serif !important;
        font-size: 13px !important;
        color: #8be8ff !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    [data-testid="stMetricDelta"] > div {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
    }

    /* Danger / Safe alerts overriding */
    .result-danger {
        background: rgba(255, 59, 48, 0.08) !important;
        border: 1px solid rgba(255, 59, 48, 0.3) !important;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 0 25px rgba(255, 59, 48, 0.15);
        margin-top: 20px;
        border-left: 5px solid #ff3b30 !important;
    }
    .result-safe {
        background: rgba(0, 255, 135, 0.05) !important;
        border: 1px solid rgba(0, 255, 135, 0.25) !important;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 0 25px rgba(0, 255, 135, 0.1);
        margin-top: 20px;
        border-left: 5px solid #00ff87 !important;
    }

    .reason-chip {
        background: rgba(6, 18, 36, 0.5);
        border: 1px solid rgba(0, 240, 255, 0.15);
        border-radius: 12px;
        padding: 12px 18px;
        margin: 10px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #d9f7ff;
        transition: all 0.2s ease;
    }
    .reason-chip:hover {
        border-color: rgba(255, 0, 127, 0.3);
        background: rgba(6, 18, 36, 0.7);
        padding-left: 22px;
    }

    .recommend-card {
        background: rgba(6, 18, 36, 0.4);
        border: 1px solid rgba(0, 240, 255, 0.15);
        border-radius: 16px;
        padding: 20px;
        margin-top: 20px;
        border-left: 4px solid #ffd60a;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #020617;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 240, 255, 0.2);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 240, 255, 0.4);
    }

    /* Progress Bar override */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00f0ff, #ff007f) !important;
    }

    /* ── V4.3 Global Keyframes ─────────────────────────────────────── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0);    }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 10px rgba(0, 240, 255, 0.10); }
        50%       { box-shadow: 0 0 22px rgba(0, 240, 255, 0.28); }
    }
    @keyframes shimmer {
        0%   { background-position: -400px 0; }
        100% { background-position:  400px 0; }
    }
    @keyframes scanLine {
        0%   { top: 0%; opacity: 0.6; }
        100% { top: 100%; opacity: 0;  }
    }

    /* ── Glass card enhanced hover ─────────────────────────────────── */
    .glass {
        transition: border-color 0.35s ease, box-shadow 0.35s ease, transform 0.25s ease !important;
    }
    .glass:hover {
        border-color: rgba(0, 240, 255, 0.30) !important;
        box-shadow: 0 14px 44px rgba(0, 0, 0, 0.55), 0 0 32px rgba(0, 240, 255, 0.10) !important;
        transform: translateY(-2px);
    }

    /* ── Metric tile hover ─────────────────────────────────────────── */
    [data-testid="stMetric"] {
        transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.25s ease !important;
    }
    [data-testid="stMetric"]:hover {
        border-color: rgba(0, 240, 255, 0.38) !important;
        border-left-color: #ff007f !important;
        box-shadow: 0 10px 36px rgba(0, 0, 0, 0.40), 0 0 24px rgba(255, 0, 127, 0.12) !important;
        transform: translateY(-3px);
    }

    /* ── Button hover refinement ───────────────────────────────────── */
    .stButton > button {
        transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
    }
    .stButton > button::after {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(120deg,
            transparent 0%, rgba(0, 240, 255, 0.07) 50%, transparent 100%);
        background-size: 200% 100%;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .stButton > button:hover::after {
        opacity: 1;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(0,240,255,0.16), rgba(255,0,127,0.10)) !important;
        color: #ffffff !important;
        border-color: #00f0ff !important;
        box-shadow: 0 0 22px rgba(0, 240, 255, 0.28) !important;
        transform: translateY(-2px) !important;
        letter-spacing: 2px !important;
    }

    /* ── Download button hover ─────────────────────────────────────── */
    .stDownloadButton > button {
        background: rgba(6, 18, 36, 0.6) !important;
        color: #00f0ff !important;
        border: 1px solid rgba(0, 240, 255, 0.25) !important;
        border-radius: 10px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 12px !important;
        letter-spacing: 1px !important;
        transition: all 0.28s ease !important;
        text-transform: uppercase;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, rgba(0,240,255,0.12), rgba(255,0,127,0.08)) !important;
        border-color: #00f0ff !important;
        box-shadow: 0 0 18px rgba(0, 240, 255, 0.20) !important;
        transform: translateY(-2px) !important;
        color: #ffffff !important;
    }

    /* ── reason-chip hover refinement ──────────────────────────────── */
    .reason-chip {
        transition: all 0.25s ease, padding-left 0.25s ease !important;
    }
    .reason-chip:hover {
        border-color: rgba(255, 0, 127, 0.40) !important;
        background: rgba(6, 18, 36, 0.75) !important;
        padding-left: 24px !important;
        box-shadow: 0 0 14px rgba(255, 0, 127, 0.10) !important;
    }

    /* ── telemetry-card hover ───────────────────────────────────────── */
    .telemetry-card {
        transition: all 0.30s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .telemetry-card:hover {
        border-color: rgba(0, 240, 255, 0.40) !important;
        box-shadow: 0 10px 34px rgba(0, 240, 255, 0.10) !important;
        transform: translateY(-3px) !important;
    }

    /* ── Sidebar nav label hover ────────────────────────────────────── */
    div.row-widget.stRadio label {
        transition: all 0.25s ease, padding-left 0.2s ease !important;
    }

    /* ── V4.3 Success notification card ─────────────────────────────── */
    .v43-notify {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 18px;
        border-radius: 12px;
        margin: 6px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        animation: fadeInUp 0.4s ease both;
    }
    .v43-notify-success {
        background: rgba(0, 255, 135, 0.06);
        border: 1px solid rgba(0, 255, 135, 0.25);
        border-left: 4px solid #00ff87;
        color: #a1ffcc;
    }
    .v43-notify-info {
        background: rgba(0, 240, 255, 0.06);
        border: 1px solid rgba(0, 240, 255, 0.22);
        border-left: 4px solid #00f0ff;
        color: #8be8ff;
    }
    .v43-notify-warn {
        background: rgba(255, 214, 10, 0.05);
        border: 1px solid rgba(255, 214, 10, 0.22);
        border-left: 4px solid #ffd60a;
        color: #ffe680;
    }

    /* ── V4.3 Empty state card ──────────────────────────────────────── */
    .v43-empty {
        text-align: center;
        padding: 60px 24px;
        background: rgba(6, 18, 36, 0.45);
        border: 1px solid rgba(0, 240, 255, 0.10);
        border-radius: 20px;
        margin: 20px 0;
        animation: fadeInUp 0.5s ease both;
    }
    .v43-empty-icon {
        font-size: 48px;
        margin-bottom: 16px;
        opacity: 0.6;
    }
    .v43-empty-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 15px;
        font-weight: 700;
        color: #8be8ff;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .v43-empty-body {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #4a6075;
        line-height: 1.8;
    }

    /* ── V4.3 Threat Gauge ──────────────────────────────────────────── */
    .v43-gauge-wrap {
        background: rgba(6, 18, 36, 0.55);
        border: 1px solid rgba(0, 240, 255, 0.12);
        border-radius: 16px;
        padding: 20px 24px;
        margin: 18px 0;
        animation: fadeInUp 0.45s ease both;
    }
    .v43-gauge-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        color: #63768f;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
    }
    .v43-gauge-score {
        font-family: 'Orbitron', sans-serif;
        font-size: 36px;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 10px;
    }
    .v43-gauge-bar-track {
        width: 100%;
        height: 10px;
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.08);
        overflow: hidden;
        margin-bottom: 8px;
    }
    .v43-gauge-bar-fill {
        height: 100%;
        border-radius: 8px;
        transition: width 0.6s ease;
    }
    .v43-gauge-tier {
        font-family: 'Orbitron', sans-serif;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        padding: 3px 10px;
        border-radius: 6px;
        display: inline-block;
    }

    /* ── V4.3 Loading stage indicator ───────────────────────────────── */
    .v43-stage {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 14px;
        border-radius: 8px;
        margin: 4px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        animation: fadeInUp 0.3s ease both;
    }
    .v43-stage-active {
        background: rgba(0, 240, 255, 0.07);
        border-left: 3px solid #00f0ff;
        color: #00f0ff;
    }
    .v43-stage-done {
        background: rgba(0, 255, 135, 0.05);
        border-left: 3px solid #00ff87;
        color: #00ff87;
    }
    .v43-stage-pending {
        color: #2a3a4a;
        border-left: 3px solid #1a2a3a;
    }

    </style>
    """, unsafe_allow_html=True)