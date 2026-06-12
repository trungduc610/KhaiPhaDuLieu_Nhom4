"""
Custom CSS styles cho ứng dụng HR Analytics.
"""

import streamlit as st


def apply_styles():
    """Inject custom CSS vào trang Streamlit."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* === GLOBAL === */
    /* Remove global font override to avoid breaking Material Icons */

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a3e 50%, #0d1b2a 100%) !important;
        border-right: 1px solid rgba(99,102,241,0.2);
    }
    [data-testid="stSidebar"] .stMarkdown p {
        color: #a5b4fc !important;
        font-size: 0.8rem;
    }
    [data-testid="stSidebarNav"] a {
        color: #cbd5e1 !important;
        border-radius: 10px;
        transition: all 0.2s;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: rgba(99,102,241,0.2) !important;
        color: #a5b4fc !important;
    }
    [data-testid="stSidebarNav"] a[aria-selected="true"] {
        background: linear-gradient(135deg,rgba(99,102,241,0.4),rgba(6,182,212,0.2)) !important;
        color: #fff !important;
        border-left: 3px solid #6366f1;
    }

    /* === METRIC CARDS === */
    .metric-card {
        background: linear-gradient(135deg, rgba(30,30,60,0.8), rgba(15,15,30,0.9));
        border: 1px solid rgba(99,102,241,0.25);
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
        backdrop-filter: blur(10px);
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 32px rgba(99,102,241,0.25);
    }
    .metric-card .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.1;
    }
    .metric-card .metric-label {
        font-size: 0.82rem;
        color: #94a3b8;
        margin-top: 0.3rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-card .metric-icon {
        font-size: 1.8rem;
        margin-bottom: 0.4rem;
    }

    /* === RISK BADGES === */
    .badge-high {
        background: rgba(239,68,68,0.15);
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.3);
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-medium {
        background: rgba(245,158,11,0.15);
        color: #fbbf24;
        border: 1px solid rgba(245,158,11,0.3);
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-low {
        background: rgba(16,185,129,0.15);
        color: #34d399;
        border: 1px solid rgba(16,185,129,0.3);
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* === PAGE HEADER === */
    .page-header {
        background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(6,182,212,0.1));
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    .page-header h1 {
        margin: 0;
        font-size: 1.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #a5b4fc, #67e8f9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .page-header p {
        margin: 0.3rem 0 0;
        color: #94a3b8;
        font-size: 0.9rem;
    }

    /* === SECTION HEADER === */
    .section-header {
        font-size: 1rem;
        font-weight: 600;
        color: #a5b4fc;
        margin: 1.2rem 0 0.6rem;
        padding-left: 0.5rem;
        border-left: 3px solid #6366f1;
    }

    /* === PREDICTION RESULT === */
    .result-card-attrition {
        background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(239,68,68,0.05));
        border: 1px solid rgba(239,68,68,0.35);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    }
    .result-card-no-attrition {
        background: linear-gradient(135deg, rgba(16,185,129,0.15), rgba(16,185,129,0.05));
        border: 1px solid rgba(16,185,129,0.35);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    }
    .result-label {
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .result-prob {
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1;
    }
    .result-subtitle { color: #94a3b8; font-size: 0.85rem; }

    /* === DECISION PATH === */
    .decision-rule {
        background: rgba(99,102,241,0.08);
        border-left: 3px solid #6366f1;
        border-radius: 0 8px 8px 0;
        padding: 0.5rem 1rem;
        margin: 0.3rem 0;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        color: #c7d2fe;
    }
    .decision-final {
        background: rgba(6,182,212,0.12);
        border-left: 3px solid #06b6d4;
        border-radius: 0 8px 8px 0;
        padding: 0.5rem 1rem;
        margin: 0.3rem 0;
        font-size: 0.9rem;
        font-weight: 600;
        color: #67e8f9;
    }

    /* === WHATIF COMPARISON === */
    .compare-card {
        border-radius: 12px;
        padding: 1rem 1.5rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .compare-before { background: rgba(239,68,68,0.1); border-color: rgba(239,68,68,0.25); }
    .compare-after  { background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.25); }

    /* === TABLES === */
    [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

    /* === BUTTONS === */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(99,102,241,0.4); }

    /* === FORM === */
    .stForm { background: rgba(26,26,46,0.5); border-radius: 16px; border: 1px solid rgba(99,102,241,0.15); }

    /* === ALERTS === */
    .info-box {
        background: rgba(6,182,212,0.1);
        border: 1px solid rgba(6,182,212,0.3);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        color: #67e8f9;
        font-size: 0.85rem;
        margin: 0.5rem 0;
    }
    .warning-box {
        background: rgba(245,158,11,0.1);
        border: 1px solid rgba(245,158,11,0.3);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        color: #fbbf24;
        font-size: 0.85rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background: rgba(16,185,129,0.1);
        border: 1px solid rgba(16,185,129,0.3);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        color: #34d399;
        font-size: 0.85rem;
        margin: 0.5rem 0;
    }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: rgba(15,15,26,0.5); }
    ::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.5); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.8); }

    /* Hide Streamlit default header/footer */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)


def metric_card(icon, value, label, color=None):
    """Render một metric card đẹp."""
    color_style = f"color: {color} !important; -webkit-text-fill-color: {color} !important;" if color else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value" style="{color_style}">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def page_header(title, subtitle=""):
    """Render page header."""
    st.markdown(f"""
    <div class="page-header">
        <h1>{title}</h1>
        {"<p>" + subtitle + "</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def section_header(text):
    """Render section header với border trái."""
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


def risk_badge(level):
    """Render badge mức rủi ro."""
    cls = {'Cao': 'badge-high', 'Trung bình': 'badge-medium', 'Thấp': 'badge-low'}.get(level, 'badge-low')
    return f'<span class="{cls}">{level}</span>'
