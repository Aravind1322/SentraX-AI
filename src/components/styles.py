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
    </style>
    """, unsafe_allow_html=True)