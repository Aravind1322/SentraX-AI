"""
SentraX Premium SOC Analytics Dashboard
========================================
Consumes get_recent_scans() exclusively.
All charts built with Altair + Pandas — no external API calls.
"""

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from src.utils.database import get_recent_scans


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _load_data() -> pd.DataFrame:
    """Pull all scans from the database and return a clean DataFrame."""
    rows = get_recent_scans(limit=200)
    if not rows:
        return pd.DataFrame(columns=["url", "label", "score", "timestamp"])
    df = pd.DataFrame(rows, columns=["url", "label", "score", "timestamp"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour
    df["is_threat"] = df["label"] == "Fraud / Phishing"
    df["short_url"] = df["url"].str[:45] + df["url"].str[45:].apply(lambda x: "…" if x else "")
    return df


def _score_color(score: int) -> str:
    if score >= 70:
        return "#ff3b30"
    if score >= 50:
        return "#ffd60a"
    return "#00ff87"


def _stat_card(title: str, value, subtitle: str = "", accent: str = "#00f0ff") -> str:
    return f"""
    <div style="
        background: rgba(6,18,36,0.6);
        border: 1px solid rgba(0,240,255,0.12);
        border-left: 4px solid {accent};
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.35);
        transition: all 0.3s ease;
        height: 100%;
    ">
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                    color:#63768f;text-transform:uppercase;letter-spacing:1.5px;
                    margin-bottom:8px;">{title}</div>
        <div style="font-family:'Orbitron',sans-serif;font-size:28px;
                    font-weight:700;color:#ffffff;line-height:1;">{value}</div>
        {"<div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#8be8ff;margin-top:6px;'>" + subtitle + "</div>" if subtitle else ""}
    </div>"""


def _section_header(icon: str, title: str, tag: str = "") -> str:
    return f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                margin:32px 0 16px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:18px;">{icon}</span>
            <span style="font-family:'Orbitron',sans-serif;font-size:14px;
                         font-weight:700;color:#ffffff;letter-spacing:2px;
                         text-transform:uppercase;">{title}</span>
        </div>
        {"<span style='font-family:JetBrains Mono,monospace;font-size:10px;color:#63768f;'>" + tag + "</span>" if tag else ""}
    </div>
    <hr style="border:0;border-top:1px solid rgba(0,240,255,0.12);margin-bottom:20px;">"""


# ─────────────────────────────────────────────────────────────────────────────
# Chart builders (all Altair, themed for dark SOC aesthetic)
# ─────────────────────────────────────────────────────────────────────────────

_CHART_CONFIG = {
    "background": "transparent",
    "view": {"stroke": "transparent"},
    "axis": {
        "labelColor": "#63768f",
        "titleColor": "#8be8ff",
        "gridColor": "rgba(0,240,255,0.06)",
        "labelFont": "JetBrains Mono",
        "titleFont": "JetBrains Mono",
        "labelFontSize": 10,
        "titleFontSize": 11,
    },
    "legend": {
        "labelColor": "#8be8ff",
        "titleColor": "#8be8ff",
        "labelFont": "JetBrains Mono",
        "titleFont": "JetBrains Mono",
        "labelFontSize": 10,
    },
    "title": {"color": "#ffffff", "font": "JetBrains Mono", "fontSize": 12},
}


def _chart_threat_trend(df: pd.DataFrame):
    """Daily scan count split by label — area + line combo."""
    daily = (
        df.groupby(["date", "label"])
        .size()
        .reset_index(name="count")
    )
    if daily.empty:
        return None
    daily["date"] = pd.to_datetime(daily["date"])

    color_scale = alt.Scale(
        domain=["Fraud / Phishing", "Safe"],
        range=["#ff3b30", "#00ff87"],
    )

    area = (
        alt.Chart(daily)
        .mark_area(opacity=0.15, interpolate="monotone")
        .encode(
            x=alt.X("date:T", title="Date", axis=alt.Axis(format="%b %d")),
            y=alt.Y("count:Q", title="Scans", stack=None),
            color=alt.Color("label:N", scale=color_scale, legend=alt.Legend(title="Classification")),
        )
    )
    line = (
        alt.Chart(daily)
        .mark_line(point=True, interpolate="monotone", strokeWidth=2)
        .encode(
            x=alt.X("date:T"),
            y=alt.Y("count:Q", stack=None),
            color=alt.Color("label:N", scale=color_scale),
            tooltip=[
                alt.Tooltip("date:T", title="Date", format="%Y-%m-%d"),
                alt.Tooltip("label:N", title="Label"),
                alt.Tooltip("count:Q", title="Scans"),
            ],
        )
    )
    return (
        (area + line)
        .properties(height=220, title="Daily Scan Trend by Classification")
        .configure(**_CHART_CONFIG)
        .interactive()
    )


def _chart_score_distribution(df: pd.DataFrame):
    """Histogram of threat scores across all scans.

    Altair v6 removed support for nested alt.condition().
    Instead we derive a categorical 'risk_tier' column and map colors
    through an explicit ordinal Scale — fully compatible with Altair v6.
    """
    if df.empty:
        return None

    # Derive risk tier as a plain string column — no alt.condition needed
    plot_df = df[["score"]].copy()
    plot_df["risk_tier"] = pd.cut(
        plot_df["score"],
        bins=[-1, 49, 69, 100],
        labels=["Low (<50)", "Moderate (50-69)", "High (≥70)"],
    ).astype(str)

    tier_color_scale = alt.Scale(
        domain=["Low (<50)", "Moderate (50-69)", "High (≥70)"],
        range=["#00ff87",  "#ffd60a",            "#ff3b30"],
    )

    hist = (
        alt.Chart(plot_df)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("score:Q", bin=alt.Bin(step=10), title="Threat Score Bucket"),
            y=alt.Y("count():Q", title="Scan Count"),
            color=alt.Color(
                "risk_tier:N",
                scale=tier_color_scale,
                legend=alt.Legend(title="Risk Tier"),
            ),
            tooltip=[
                alt.Tooltip("score:Q", bin=alt.Bin(step=10), title="Score Range"),
                alt.Tooltip("risk_tier:N", title="Risk Tier"),
                alt.Tooltip("count():Q", title="Count"),
            ],
        )
        .properties(height=200, title="Threat Score Distribution")
        .configure(**_CHART_CONFIG)
    )
    return hist


def _chart_donut(df: pd.DataFrame):
    """Safe vs Threat donut chart."""
    if df.empty:
        return None

    counts = df["label"].value_counts().reset_index()
    counts.columns = ["label", "count"]

    color_scale = alt.Scale(
        domain=["Fraud / Phishing", "Safe"],
        range=["#ff3b30", "#00ff87"],
    )

    donut = (
        alt.Chart(counts)
        .mark_arc(innerRadius=55, outerRadius=90, cornerRadius=4)
        .encode(
            theta=alt.Theta("count:Q"),
            color=alt.Color("label:N", scale=color_scale,
                            legend=alt.Legend(title="Classification", orient="bottom")),
            tooltip=[
                alt.Tooltip("label:N", title="Type"),
                alt.Tooltip("count:Q", title="Count"),
            ],
        )
        .properties(height=220, title="Safe vs Threat Ratio")
        .configure(**_CHART_CONFIG)
    )
    return donut


def _chart_hourly_heatmap(df: pd.DataFrame):
    """Hour-of-day scan activity bar showing when threats are most frequent."""
    if df.empty or df["hour"].isna().all():
        return None

    hourly = (
        df.groupby(["hour", "label"])
        .size()
        .reset_index(name="count")
    )

    color_scale = alt.Scale(
        domain=["Fraud / Phishing", "Safe"],
        range=["#ff3b30", "#00ff87"],
    )

    bars = (
        alt.Chart(hourly)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("hour:O", title="Hour of Day (0–23)"),
            y=alt.Y("count:Q", title="Scans", stack="normalize",
                    axis=alt.Axis(format="%")),
            color=alt.Color("label:N", scale=color_scale,
                            legend=alt.Legend(title="Type")),
            tooltip=[
                alt.Tooltip("hour:O", title="Hour"),
                alt.Tooltip("label:N", title="Type"),
                alt.Tooltip("count:Q", title="Count"),
            ],
        )
        .properties(height=180, title="Scan Activity by Hour of Day")
        .configure(**_CHART_CONFIG)
    )
    return bars


def _chart_top_risky(df: pd.DataFrame):
    """Horizontal bar chart of top 8 highest-score URLs."""
    top = df.nlargest(8, "score")[["short_url", "score", "label"]].copy()
    if top.empty:
        return None

    color_scale = alt.Scale(
        domain=["Fraud / Phishing", "Safe"],
        range=["#ff3b30", "#00ff87"],
    )

    bars = (
        alt.Chart(top)
        .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
        .encode(
            y=alt.Y("short_url:N", sort="-x", title=None,
                    axis=alt.Axis(labelLimit=260)),
            x=alt.X("score:Q", title="Threat Score", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("label:N", scale=color_scale, legend=None),
            tooltip=[
                alt.Tooltip("short_url:N", title="URL"),
                alt.Tooltip("score:Q", title="Score"),
                alt.Tooltip("label:N", title="Label"),
            ],
        )
        .properties(height=260, title="Top 8 Highest Risk URLs")
        .configure(**_CHART_CONFIG)
    )
    return bars


# ─────────────────────────────────────────────────────────────────────────────
# Main renderer
# ─────────────────────────────────────────────────────────────────────────────

def render_dashboard():

    # ── Page-level CSS ────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0);  }
    }
    .dash-section { animation: fadeInUp 0.4s ease both; }

    /* Metric card hover glow */
    .stat-wrap > div:hover {
        border-color: rgba(0,240,255,0.35) !important;
        box-shadow: 0 8px 32px rgba(0,240,255,0.10) !important;
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }

    /* Alert row */
    .alert-row {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 8px;
        background: rgba(6,18,36,0.55);
        border: 1px solid rgba(0,240,255,0.08);
        transition: all 0.2s ease;
    }
    .alert-row:hover {
        border-color: rgba(0,240,255,0.22);
        background: rgba(6,18,36,0.75);
    }

    /* Altair chart container */
    .vega-embed { border-radius: 12px !important; }
    .vega-embed canvas { border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="dash-section" style="margin-bottom:8px;">
        <div class="brand">Threat Dashboard</div>
        <div class="tag">// SOC ANALYTICS & THREAT INTELLIGENCE CENTER</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Load data ─────────────────────────────────────────────────────────────
    df = _load_data()
    has_data = not df.empty

    # ── KPI Metrics Row ───────────────────────────────────────────────────────
    st.markdown(
        _section_header("📊", "Threat Intelligence Metrics",
                         f"LAST UPDATED: {datetime.now().strftime('%H:%M:%S')}"),
        unsafe_allow_html=True,
    )

    if has_data:
        total      = len(df)
        threats    = int(df["is_threat"].sum())
        safe       = total - threats
        avg_score  = round(df["score"].mean(), 1)
        max_score  = int(df["score"].max())
        threat_rate = round((threats / total) * 100, 1) if total else 0

        high_risk  = int((df["score"] >= 70).sum())
        med_risk   = int(((df["score"] >= 50) & (df["score"] < 70)).sum())
        low_risk   = int((df["score"] < 50).sum())
    else:
        total = threats = safe = high_risk = med_risk = low_risk = 0
        avg_score = max_score = threat_rate = 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    cards = [
        (c1, "Total Scans",      total,       f"All time logs",         "#00f0ff"),
        (c2, "Threats Detected", threats,     f"{threat_rate}% of scans", "#ff3b30"),
        (c3, "Safe URLs",        safe,         "Verified clean",         "#00ff87"),
        (c4, "Avg Risk Score",   f"{avg_score}/100", "Across all scans", "#8be8ff"),
        (c5, "High Risk (≥70)",  high_risk,   "Critical alerts",        "#ff3b30"),
        (c6, "Max Score Seen",   f"{max_score}/100",  "Highest threat",  "#ffd60a"),
    ]
    for col, title, val, sub, accent in cards:
        col.markdown(
            f'<div class="stat-wrap">{_stat_card(title, val, sub, accent)}</div>',
            unsafe_allow_html=True,
        )

    st.write("")

    if not has_data:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#63768f;
                    font-family:'JetBrains Mono',monospace;font-size:14px;">
            📡 No scan data yet.<br><br>
            Use the <b style="color:#8be8ff;">🔍 Scanner</b> page to start scanning URLs.
            All results will appear here automatically.
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Risk tier indicator row ───────────────────────────────────────────────
    st.markdown("""<div style="height:1px;background:rgba(0,240,255,0.08);margin:8px 0 20px;"></div>""",
                unsafe_allow_html=True)

    t1, t2, t3 = st.columns(3)
    tier_cards = [
        (t1, "🔴 Critical Risk ≥70", high_risk, "#ff3b30"),
        (t2, "🟡 Moderate Risk 50–69", med_risk, "#ffd60a"),
        (t3, "🟢 Low Risk &lt;50", low_risk, "#00ff87"),
    ]
    for col, label, count, color in tier_cards:
        col.markdown(f"""
        <div style="background:rgba(6,18,36,0.5);border:1px solid {color}22;
                    border-top:3px solid {color};border-radius:10px;
                    padding:14px 18px;text-align:center;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                        color:#8be8ff;letter-spacing:1px;">{label}</div>
            <div style="font-family:'Orbitron',sans-serif;font-size:32px;
                        font-weight:700;color:{color};margin-top:6px;">{count}</div>
        </div>""", unsafe_allow_html=True)

    # ── Trend chart + Donut ───────────────────────────────────────────────────
    st.markdown(
        _section_header("📈", "Threat Trend Analysis", "TIME-SERIES TELEMETRY"),
        unsafe_allow_html=True,
    )

    chart_col, donut_col = st.columns([3, 1])
    with chart_col:
        trend = _chart_threat_trend(df)
        if trend:
            st.altair_chart(trend, use_container_width=True)
        else:
            st.info("Not enough date variation to render trend. Scan more URLs over multiple days.")

    with donut_col:
        donut = _chart_donut(df)
        if donut:
            st.altair_chart(donut, use_container_width=True)

    # ── Score distribution + Hourly activity ─────────────────────────────────
    st.markdown(
        _section_header("🎯", "Score & Activity Analysis", "HEURISTICS BREAKDOWN"),
        unsafe_allow_html=True,
    )

    dist_col, hour_col = st.columns([1, 1])
    with dist_col:
        dist = _chart_score_distribution(df)
        if dist:
            st.altair_chart(dist, use_container_width=True)

    with hour_col:
        hourly = _chart_hourly_heatmap(df)
        if hourly:
            st.altair_chart(hourly, use_container_width=True)

    # ── Top risky URLs ────────────────────────────────────────────────────────
    st.markdown(
        _section_header("🚨", "Top Risk Indicators", "HIGHEST THREAT SCORE TARGETS"),
        unsafe_allow_html=True,
    )

    top_chart = _chart_top_risky(df)
    if top_chart:
        st.altair_chart(top_chart, use_container_width=True)

    # ── Recent Alert Timeline ─────────────────────────────────────────────────
    st.markdown(
        _section_header("⏱️", "Recent Alert Timeline", f"LATEST {min(len(df), 15)} EVENTS"),
        unsafe_allow_html=True,
    )

    recent = df.head(15)
    for _, row in recent.iterrows():
        color  = _score_color(int(row["score"]))
        bg     = f"rgba({','.join(str(int(color.lstrip('#')[i:i+2], 16)) for i in (0,2,4))},0.06)"
        ts_str = row["timestamp"].strftime("%Y-%m-%d %H:%M") if pd.notna(row["timestamp"]) else "—"

        st.markdown(f"""
        <div class="alert-row" style="border-left:4px solid {color};background:{bg};">
            <div style="flex:1;min-width:0;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:12px;
                            color:#ffffff;overflow:hidden;text-overflow:ellipsis;
                            white-space:nowrap;" title="{row['url']}">
                    {row['short_url']}
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                            color:#63768f;margin-top:3px;">{ts_str}</div>
            </div>
            <div style="text-align:right;flex-shrink:0;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                            font-weight:700;color:{color};">{row['score']}/100</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
                            padding:2px 8px;border:1px solid {color};
                            border-radius:4px;color:{color};margin-top:4px;
                            background:rgba(0,0,0,0.3);">
                    {row['label'].upper()}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Raw data expander ─────────────────────────────────────────────────────
    with st.expander("🗃️  View Raw Scan Log Table", expanded=False):
        display_df = df[["url", "label", "score", "timestamp"]].copy()
        display_df.columns = ["URL", "Classification", "Risk Score", "Timestamp"]
        display_df["Risk Score"] = display_df["Risk Score"].astype(str) + " / 100"
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-top:40px;padding-top:20px;
                border-top:1px solid rgba(0,240,255,0.08);
                text-align:center;font-family:'JetBrains Mono',monospace;
                font-size:10px;color:#63768f;">
        SENTRAX SOC ANALYTICS — {total} TOTAL LOGS — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)