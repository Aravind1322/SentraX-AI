import streamlit as st


def render_about():
    # ─────────────────────────────────────────────────────────────────────
    # Page-scoped additional styles
    # ─────────────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    /* ── Hero badges ── */
    .about-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(0, 240, 255, 0.07);
        border: 1px solid rgba(0, 240, 255, 0.22);
        border-radius: 30px;
        padding: 8px 18px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #8be8ff;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin: 6px;
        transition: all 0.3s ease;
        box-shadow: 0 0 12px rgba(0,240,255,0.06);
    }
    .about-badge:hover {
        background: rgba(0,240,255,0.13);
        border-color: #00f0ff;
        color: #ffffff;
        box-shadow: 0 0 20px rgba(0,240,255,0.18);
    }

    /* ── Overview cards ── */
    .ov-card {
        background: rgba(6, 18, 36, 0.50);
        border: 1px solid rgba(0, 240, 255, 0.14);
        border-radius: 18px;
        padding: 26px 24px;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 18px rgba(0,240,255,0.04);
        transition: all 0.3s ease;
        height: 100%;
    }
    .ov-card:hover {
        border-color: rgba(0,240,255,0.28);
        box-shadow: 0 12px 42px rgba(0,0,0,0.5), 0 0 26px rgba(0,240,255,0.09);
        transform: translateY(-3px);
    }
    .ov-card-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: #00f0ff;
        margin-bottom: 14px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(0,240,255,0.12);
    }
    .ov-card-body {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        color: #c9e8f5;
        line-height: 1.75;
    }
    .ov-bullet {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        margin: 7px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #c9e8f5;
    }
    .ov-bullet-dot {
        color: #00f0ff;
        font-weight: 700;
        flex-shrink: 0;
        margin-top: 1px;
    }

    /* ── Section header ── */
    .section-head {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 40px 0 6px;
    }
    .section-head-icon {
        font-size: 18px;
    }
    .section-head-label {
        font-family: 'Orbitron', sans-serif;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #ffffff;
    }
    .section-divider {
        border: 0;
        border-top: 1px solid rgba(0,240,255,0.12);
        margin: 8px 0 20px;
    }

    /* ── Tech stack card ── */
    .tech-card {
        background: rgba(6,18,36,0.50);
        border: 1px solid rgba(0,240,255,0.13);
        border-radius: 14px;
        padding: 20px 22px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    .tech-card:hover {
        border-color: rgba(0,240,255,0.28);
        box-shadow: 0 0 22px rgba(0,240,255,0.07);
        transform: translateY(-2px);
    }
    .tech-cat {
        font-family: 'Orbitron', sans-serif;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #ff007f;
        margin-bottom: 12px;
    }
    .tech-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #8be8ff;
        margin: 5px 0;
    }
    .tech-dot {
        width: 6px;
        height: 6px;
        background: #00f0ff;
        border-radius: 50%;
        box-shadow: 0 0 6px #00f0ff;
        flex-shrink: 0;
    }

    /* ── Architecture flow ── */
    .arch-flow {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0;
        margin: 10px 0;
    }
    .arch-node {
        background: rgba(6,18,36,0.65);
        border: 1px solid rgba(0,240,255,0.22);
        border-radius: 12px;
        padding: 14px 36px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        font-weight: 600;
        color: #00f0ff;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        text-align: center;
        box-shadow: 0 0 18px rgba(0,240,255,0.07);
        transition: all 0.3s ease;
        width: 320px;
    }
    .arch-node:hover {
        background: rgba(0,240,255,0.08);
        border-color: #00f0ff;
        box-shadow: 0 0 28px rgba(0,240,255,0.18);
    }
    .arch-arrow {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0;
        margin: 0;
    }
    .arch-line {
        width: 2px;
        height: 20px;
        background: linear-gradient(to bottom, rgba(0,240,255,0.5), rgba(255,0,127,0.4));
    }
    .arch-arrowhead {
        width: 0;
        height: 0;
        border-left: 7px solid transparent;
        border-right: 7px solid transparent;
        border-top: 10px solid rgba(255,0,127,0.7);
    }

    /* ── Stat cards ── */
    .stat-card {
        background: rgba(6,18,36,0.60);
        border: 1px solid rgba(0,240,255,0.12);
        border-left: 4px solid #00f0ff;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.35);
        transition: all 0.3s ease;
        height: 100%;
    }
    .stat-card:hover {
        border-color: rgba(255,0,127,0.5);
        border-left-color: #ff007f;
        box-shadow: 0 8px 32px rgba(255,0,127,0.12);
        transform: translateY(-2px);
    }
    .stat-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        color: #63768f;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
    }
    .stat-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.15;
    }
    .stat-sub {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #8be8ff;
        margin-top: 6px;
    }

    /* ── Roadmap ── */
    .roadmap-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 10px 14px;
        border-radius: 10px;
        margin: 6px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        transition: all 0.25s ease;
    }
    .roadmap-item:hover {
        background: rgba(0,240,255,0.04);
        padding-left: 18px;
    }
    .roadmap-done {
        color: #00ff87;
        border-left: 3px solid rgba(0,255,135,0.3);
    }
    .roadmap-pending {
        color: #8be8ff;
        border-left: 3px solid rgba(255,0,127,0.3);
    }
    .roadmap-icon {
        font-size: 15px;
        flex-shrink: 0;
        margin-top: 1px;
    }

    /* ── Developer card ── */
    .dev-card {
        background: rgba(6,18,36,0.55);
        border: 1px solid rgba(0,240,255,0.16);
        border-radius: 20px;
        padding: 36px 32px;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 36px rgba(0,0,0,0.45), 0 0 24px rgba(0,240,255,0.06);
        text-align: center;
    }
    .dev-avatar {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        background: linear-gradient(135deg, #00f0ff, #ff007f);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        margin: 0 auto 18px;
        box-shadow: 0 0 28px rgba(0,240,255,0.25);
    }
    .dev-name {
        font-family: 'Orbitron', sans-serif;
        font-size: 20px;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 1.5px;
        margin-bottom: 6px;
    }
    .dev-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #8be8ff;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }
    .dev-project {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #63768f;
        margin-top: 14px;
        line-height: 1.8;
    }
    .dev-project span {
        color: #00f0ff;
    }
    .cyber-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(6,18,36,0.6);
        color: #00f0ff;
        border: 1px solid rgba(0,240,255,0.30);
        border-radius: 10px;
        font-family: 'Orbitron', sans-serif;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        padding: 11px 22px;
        text-decoration: none;
        transition: all 0.3s ease;
        margin: 6px;
        box-shadow: 0 0 10px rgba(0,240,255,0.05);
    }
    .cyber-btn:hover {
        background: linear-gradient(135deg, rgba(0,240,255,0.15), rgba(255,0,127,0.10));
        color: #ffffff;
        border-color: #00f0ff;
        box-shadow: 0 0 20px rgba(0,240,255,0.25);
        text-decoration: none;
    }
    .cyber-btn-pink {
        border-color: rgba(255,0,127,0.30);
        color: #ff007f;
    }
    .cyber-btn-pink:hover {
        border-color: #ff007f;
        background: linear-gradient(135deg, rgba(255,0,127,0.12), rgba(0,240,255,0.06));
        color: #ffffff;
        box-shadow: 0 0 20px rgba(255,0,127,0.22);
    }

    /* ── Footer ── */
    .about-footer {
        text-align: center;
        margin-top: 52px;
        padding: 30px 20px 20px;
        border-top: 1px solid rgba(0,240,255,0.10);
    }
    .footer-brand {
        font-family: 'Orbitron', sans-serif;
        font-size: 18px;
        font-weight: 800;
        background: linear-gradient(90deg, #00f0ff, #8be8ff, #ff007f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 3px;
        margin-bottom: 4px;
    }
    .footer-version {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #ff007f;
        letter-spacing: 2px;
        margin-bottom: 6px;
    }
    .footer-tagline {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #63768f;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    .footer-copy {
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        color: #3a4a5a;
        margin-top: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    # =========================================================================
    # SECTION 1 — Hero Banner
    # =========================================================================
    st.markdown('<div class="brand">About SentraX</div>', unsafe_allow_html=True)
    st.markdown('<div class="tag">// ENTERPRISE CYBER THREAT INTELLIGENCE PLATFORM</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="glass" style="text-align:center; padding: 36px 32px 28px;">
        <p style="font-family:'Inter',sans-serif; font-size:17px; color:#c9e8f5;
                  line-height:1.8; max-width:780px; margin:0 auto 28px; font-weight:400;">
            SentraX AI is an AI-powered cybersecurity and fraud intelligence platform designed to
            <span style="color:#00f0ff;font-weight:600;">detect</span>,
            <span style="color:#ff007f;font-weight:600;">analyze</span>, and
            <span style="color:#8be8ff;font-weight:600;">mitigate</span>
            digital threats across enterprise environments.
        </p>
        <div style="display:flex; flex-wrap:wrap; justify-content:center; gap:4px; margin-top:10px;">
            <span class="about-badge">🛡 Threat Intelligence</span>
            <span class="about-badge">⚡ AI Detection</span>
            <span class="about-badge">📊 Analytics Dashboard</span>
            <span class="about-badge">📄 Executive Reporting</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # SECTION 2 — Platform Overview (2 × 2 cards)
    # =========================================================================
    st.markdown("""
    <div class="section-head">
        <span class="section-head-icon">🔭</span>
        <span class="section-head-label">Platform Overview</span>
    </div>
    <hr class="section-divider">
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("""
        <div class="ov-card">
            <div class="ov-card-title">🎯 Mission</div>
            <div class="ov-card-body">
                Protect organizations from phishing, scam messages, fraudulent transactions,
                and cyber threats using intelligent automated analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="ov-card">
            <div class="ov-card-title">🚀 Vision</div>
            <div class="ov-card-body">
                Build an enterprise-grade cyber defense platform capable of assisting SOC teams
                with fast threat identification and reporting.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    col3, col4 = st.columns(2, gap="medium")

    with col3:
        st.markdown("""
        <div class="ov-card">
            <div class="ov-card-title">⚙️ Core Features</div>
            <div class="ov-bullet"><span class="ov-bullet-dot">▸</span>URL Threat Detection</div>
            <div class="ov-bullet"><span class="ov-bullet-dot">▸</span>SMS Scam Analysis</div>
            <div class="ov-bullet"><span class="ov-bullet-dot">▸</span>Universal Quick Scan</div>
            <div class="ov-bullet"><span class="ov-bullet-dot">▸</span>Fraud Risk Detection</div>
            <div class="ov-bullet"><span class="ov-bullet-dot">▸</span>Executive PDF Reports</div>
            <div class="ov-bullet"><span class="ov-bullet-dot">▸</span>Threat Analytics Dashboard</div>
            <div class="ov-bullet"><span class="ov-bullet-dot">▸</span>Enterprise Shield</div>
            <div class="ov-bullet"><span class="ov-bullet-dot">▸</span>Scan History Logging</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="ov-card">
            <div class="ov-card-title">👥 Target Users</div>
            <div class="ov-bullet"><span class="ov-bullet-dot">▸</span>Security Analysts</div>
            <div class="ov-bullet"><span class="ov-bullet-dot">▸</span>SOC Teams</div>
            <div class="ov-bullet"><span class="ov-bullet-dot">▸</span>Enterprises</div>
            <div class="ov-bullet"><span class="ov-bullet-dot">▸</span>Financial Organizations</div>
            <div class="ov-bullet"><span class="ov-bullet-dot">▸</span>Educational Institutions</div>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # SECTION 3 — Technology Stack (2-col)
    # =========================================================================
    st.markdown("""
    <div class="section-head">
        <span class="section-head-icon">💻</span>
        <span class="section-head-label">Technology Stack</span>
    </div>
    <hr class="section-divider">
    """, unsafe_allow_html=True)

    tc1, tc2 = st.columns(2, gap="medium")

    with tc1:
        st.markdown("""
        <div class="tech-card">
            <div class="tech-cat">🖥 Frontend</div>
            <div class="tech-item"><span class="tech-dot"></span>Streamlit</div>
            <div class="tech-item"><span class="tech-dot"></span>Python</div>
        </div>
        <div class="tech-card">
            <div class="tech-cat">🗄 Backend</div>
            <div class="tech-item"><span class="tech-dot"></span>SQLite Database</div>
            <div class="tech-item"><span class="tech-dot"></span>ReportLab</div>
            <div class="tech-item"><span class="tech-dot"></span>Pandas</div>
        </div>
        """, unsafe_allow_html=True)

    with tc2:
        st.markdown("""
        <div class="tech-card">
            <div class="tech-cat">🤖 AI &amp; Analytics</div>
            <div class="tech-item"><span class="tech-dot"></span>Threat Scoring Engine</div>
            <div class="tech-item"><span class="tech-dot"></span>Rule-Based Detection</div>
            <div class="tech-item"><span class="tech-dot"></span>Threat Analytics</div>
        </div>
        <div class="tech-card">
            <div class="tech-cat">☁️ Deployment</div>
            <div class="tech-item"><span class="tech-dot"></span>Streamlit Cloud</div>
            <div class="tech-item"><span class="tech-dot"></span>GitHub</div>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # SECTION 4 — System Architecture
    # =========================================================================
    st.markdown("""
    <div class="section-head">
        <span class="section-head-icon">🏗</span>
        <span class="section-head-label">System Architecture</span>
    </div>
    <hr class="section-divider">
    """, unsafe_allow_html=True)

    arch_nodes = [
        ("⚡", "Quick Scan"),
        ("🤖", "AI Detection Engine"),
        ("⚠️", "Risk Classification"),
        ("🗄", "Threat History Database"),
        ("📊", "Analytics Dashboard"),
        ("📄", "Executive PDF Reports"),
    ]

    _, arch_col, _ = st.columns([1, 2, 1])
    with arch_col:
        st.markdown("""
        <div style="background:rgba(6,18,36,0.50);border:1px solid rgba(0,240,255,0.14);
                    border-radius:20px;padding:32px 28px;display:flex;
                    flex-direction:column;align-items:center;gap:0;">
        """, unsafe_allow_html=True)
        for i, (icon, label) in enumerate(arch_nodes):
            st.markdown(f"""
            <div style="background:rgba(0,240,255,0.07);border:1px solid rgba(0,240,255,0.22);
                        border-radius:12px;padding:12px 28px;text-align:center;
                        font-family:'Orbitron',sans-serif;font-size:13px;font-weight:700;
                        letter-spacing:1.5px;color:#00f0ff;text-transform:uppercase;
                        box-shadow:0 0 14px rgba(0,240,255,0.08);min-width:260px;">
                {icon}&nbsp;&nbsp;{label}
            </div>
            """, unsafe_allow_html=True)
            if i < len(arch_nodes) - 1:
                st.markdown("""
                <div style="display:flex;flex-direction:column;align-items:center;
                            margin:2px 0;gap:0;">
                    <div style="width:2px;height:20px;
                                background:linear-gradient(180deg,#00f0ff,rgba(0,240,255,0.2));"></div>
                    <div style="width:0;height:0;
                                border-left:7px solid transparent;
                                border-right:7px solid transparent;
                                border-top:9px solid #00f0ff;
                                filter:drop-shadow(0 0 4px #00f0ff);"></div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # SECTION 5 — Project Statistics
    # =========================================================================
    st.markdown("""
    <div class="section-head">
        <span class="section-head-icon">📡</span>
        <span class="section-head-label">Project Statistics</span>
    </div>
    <hr class="section-divider">
    """, unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4, gap="medium")

    with s1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">Supported Modules</div>
            <div class="stat-value">7</div>
            <div class="stat-sub">Active scanner engines</div>
        </div>
        """, unsafe_allow_html=True)

    with s2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">Report Formats</div>
            <div class="stat-value" style="font-size:20px;line-height:1.4;">CSV<br>TXT<br>PDF</div>
            <div class="stat-sub">Export-ready outputs</div>
        </div>
        """, unsafe_allow_html=True)

    with s3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">Detection Engines</div>
            <div class="stat-value">4</div>
            <div class="stat-sub">Threat analysis cores</div>
        </div>
        """, unsafe_allow_html=True)

    with s4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-label">Deployment</div>
            <div class="stat-value" style="font-size:16px;line-height:1.6;color:#00f0ff;">CLOUD<br>READY</div>
            <div class="stat-sub">Streamlit Cloud</div>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # SECTION 6 — Future Roadmap
    # =========================================================================
    st.markdown("""
    <div class="section-head">
        <span class="section-head-icon">🗺</span>
        <span class="section-head-label">Future Roadmap</span>
    </div>
    <hr class="section-divider">
    """, unsafe_allow_html=True)

    r1, r2 = st.columns(2, gap="medium")

    with r1:
        st.markdown("""
        <div class="glass" style="padding:24px 26px;">
            <div style="font-family:'Orbitron',sans-serif;font-size:11px;font-weight:700;
                        letter-spacing:2px;color:#00ff87;text-transform:uppercase;margin-bottom:16px;
                        padding-bottom:10px;border-bottom:1px solid rgba(0,255,135,0.15);">
                ✅ Completed
            </div>
            <div class="roadmap-item roadmap-done"><span class="roadmap-icon">✅</span>URL Scanner</div>
            <div class="roadmap-item roadmap-done"><span class="roadmap-icon">✅</span>SMS Scanner</div>
            <div class="roadmap-item roadmap-done"><span class="roadmap-icon">✅</span>Enterprise Shield</div>
            <div class="roadmap-item roadmap-done"><span class="roadmap-icon">✅</span>Quick Scan</div>
            <div class="roadmap-item roadmap-done"><span class="roadmap-icon">✅</span>Threat Dashboard</div>
            <div class="roadmap-item roadmap-done"><span class="roadmap-icon">✅</span>Executive Reports</div>
        </div>
        """, unsafe_allow_html=True)

    with r2:
        st.markdown("""
        <div class="glass" style="padding:24px 26px;">
            <div style="font-family:'Orbitron',sans-serif;font-size:11px;font-weight:700;
                        letter-spacing:2px;color:#ff007f;text-transform:uppercase;margin-bottom:16px;
                        padding-bottom:10px;border-bottom:1px solid rgba(255,0,127,0.15);">
                🔲 Upcoming
            </div>
            <div class="roadmap-item roadmap-pending"><span class="roadmap-icon">⬜</span>FastAPI Backend</div>
            <div class="roadmap-item roadmap-pending"><span class="roadmap-icon">⬜</span>PostgreSQL</div>
            <div class="roadmap-item roadmap-pending"><span class="roadmap-icon">⬜</span>User Authentication</div>
            <div class="roadmap-item roadmap-pending"><span class="roadmap-icon">⬜</span>ML Detection Models</div>
            <div class="roadmap-item roadmap-pending"><span class="roadmap-icon">⬜</span>Live Threat Feed</div>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # SECTION 7 — Developer Section
    # =========================================================================
    st.markdown("""
    <div class="section-head">
        <span class="section-head-icon">👨‍💻</span>
        <span class="section-head-label">Developer</span>
    </div>
    <hr class="section-divider">
    """, unsafe_allow_html=True)

    _, dev_col, _ = st.columns([1, 2, 1])

    with dev_col:
        st.markdown("""
        <div class="dev-card">
            <div class="dev-avatar">👨‍💻</div>
            <div class="dev-name">Aravind Reddy</div>
            <div class="dev-title">B.Tech CSE — Artificial Intelligence</div>
            <div class="dev-title" style="color:#63768f;">
                Madanapalle Institute of Technology &amp; Science
            </div>
            <div class="dev-project">
                Project: <span>SentraX AI</span><br>
                Enterprise Cyber Threat Intelligence Platform
            </div>
            <div style="margin-top:24px;">
                <a href="https://github.com/Aravind1322/SentraX-AI"
                   target="_blank" class="cyber-btn">
                    🐙 GitHub Repository
                </a>
                <a href="#" class="cyber-btn cyber-btn-pink">
                    🚀 Live Demo
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # SECTION 8 — Footer
    # =========================================================================
    st.markdown("""
    <div class="about-footer">
        <div class="footer-brand">SentraX AI</div>
        <div class="footer-version">Version V4.2</div>
        <div class="footer-tagline">Enterprise Cyber Threat Intelligence Platform</div>
        <div class="footer-copy">© 2026 SentraX AI — All rights reserved.</div>
    </div>
    """, unsafe_allow_html=True)