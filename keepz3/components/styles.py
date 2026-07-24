"""Global blue SaaS theme and lightweight HTML components."""

import streamlit as st

from core.constants import AMBER, GREEN, RED


def apply_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .stApp { background: #F4F7FB; color: #12213F; }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #07142F 0%, #0D2451 100%);
            border-right: 0;
        }
        section[data-testid="stSidebar"] * { color: #D9E6FF; }
        section[data-testid="stSidebar"] hr { border-color: #263B62; }
        section[data-testid="stSidebar"] [data-testid="stRadio"] label {
            padding: .48rem .65rem; border-radius: 9px;
        }
        section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
            background: rgba(65, 126, 255, .14);
        }
        .block-container { max-width: 1500px; padding: 2rem 2.4rem 3rem; }
        h1, h2, h3 { color: #102044; letter-spacing: -.025em; }
        .eyebrow { color: #2563EB; font-size: .72rem; font-weight: 800;
            letter-spacing: .12em; text-transform: uppercase; margin-bottom: .3rem; }
        .page-title { font-size: 2rem; font-weight: 800; color: #102044; line-height: 1.15; }
        .page-subtitle { color: #667085; margin: .35rem 0 1.4rem; }
        .metric-card, .info-card {
            background: white; border: 1px solid #E5ECF6; border-radius: 16px;
            padding: 1.15rem 1.25rem; box-shadow: 0 5px 18px rgba(31, 65, 116, .055);
        }
        .metric-label { color: #718096; font-size: .76rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: .045em; }
        .metric-value { color: #102044; font-size: 1.75rem; font-weight: 800; margin-top: .3rem; }
        .metric-note { color: #7B879B; font-size: .75rem; margin-top: .25rem; }
        .good { color: %s !important; } .risk { color: %s !important; }
        .watch { color: %s !important; }
        .section-title { font-size: 1rem; font-weight: 750; color: #1B2D50; margin: 1.2rem 0 .4rem; }
        .insight { background: #EAF2FF; border-left: 4px solid #2563EB;
            padding: 1rem 1.1rem; border-radius: 0 12px 12px 0; color: #284267; }
        .sidebar-brand { font-size: 1.55rem; font-weight: 800; color: white; margin: .4rem 0 .1rem; }
        .sidebar-brand span { color: #64A0FF; }
        .sidebar-tag { color: #8EA9D6 !important; font-size: .72rem; margin-bottom: 1.5rem; }
        .sidebar-note { color: #9FB2D3; font-size: .76rem; line-height: 1.55; }
        div[data-testid="stDataFrame"] { border: 1px solid #E5ECF6; border-radius: 14px; overflow: hidden; }
        div[data-testid="stSelectbox"] > div > div { border-radius: 10px; }
        </style>
        """ % (GREEN, RED, AMBER),
        unsafe_allow_html=True,
    )


def render_sidebar_brand():
    st.markdown("<div class='sidebar-brand'>◆ <span>Keep</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-tag'>RETENTION INTELLIGENCE</div>", unsafe_allow_html=True)


def page_header(kicker, title, subtitle):
    st.markdown(
        f"<div class='eyebrow'>{kicker}</div><div class='page-title'>{title}</div>"
        f"<div class='page-subtitle'>{subtitle}</div>",
        unsafe_allow_html=True,
    )


def metric_card(label, value, note="", tone=""):
    st.markdown(
        f"<div class='metric-card'><div class='metric-label'>{label}</div>"
        f"<div class='metric-value {tone}'>{value}</div>"
        f"<div class='metric-note'>{note}</div></div>",
        unsafe_allow_html=True,
    )
