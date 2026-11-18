"""
Formatting and Styling Helpers for Rajasthan Royals Dashboard
"""

import streamlit as st


# RR Signature Color Palette
RR_PINK = "#EA1B86"
RR_ROYAL_BLUE = "#004BA0"
RR_DARK_NAVY = "#0B132B"
RR_NAVY_CARD = "#1C2541"
RR_GOLD = "#F59E0B"
RR_TEXT_LIGHT = "#F8FAFC"
RR_TEXT_MUTED = "#94A3B8"
RR_SUCCESS = "#10B981"
RR_WARNING = "#F59E0B"
RR_DANGER = "#EF4444"


def format_category_badge(category: str) -> str:
    """Return colored pill badge for development category."""
    color_map = {
        "Emerging": ("#10B981", "#064E3B"),
        "Young development candidate": ("#3B82F6", "#1E3A8A"),
        "Prime-age performer": ("#8B5CF6", "#4C1D95"),
        "Experienced performer": ("#F59E0B", "#78350F")
    }
    border, bg = color_map.get(str(category).strip(), ("#6B7280", "#374151"))
    return f"""<span style="background-color: {bg}; color: #FFFFFF; padding: 3px 8px; 
                 border-radius: 12px; font-size: 0.75rem; border: 1px solid {border}; font-weight: 500;">
                 {category}</span>"""


def format_nationality_badge(nationality: str) -> str:
    """Return badge for Indian vs Overseas."""
    if str(nationality).lower() == "indian":
        return """<span style="background-color: #064E3B; color: #34D399; padding: 2px 8px; 
                     border-radius: 10px; font-size: 0.75rem; font-weight: 600;">🇮🇳 Indian</span>"""
    return """<span style="background-color: #1E3A8A; color: #93C5FD; padding: 2px 8px; 
                 border-radius: 10px; font-size: 0.75rem; font-weight: 600;">✈️ Overseas</span>"""


def format_form_badge(rating: str) -> str:
    """Return badge for current form rating."""
    r = str(rating).upper()
    if "STRONG" in r:
        return """<span style="background-color: #065F46; color: #6EE7B7; padding: 2px 8px; 
                     border-radius: 10px; font-size: 0.75rem; font-weight: 600;">🔥 STRONG</span>"""
    elif "POSITIVE" in r:
        return """<span style="background-color: #1E3A8A; color: #93C5FD; padding: 2px 8px; 
                     border-radius: 10px; font-size: 0.75rem; font-weight: 600;">📈 POSITIVE</span>"""
    elif "MIXED" in r:
        return """<span style="background-color: #78350F; color: #FCD34D; padding: 2px 8px; 
                     border-radius: 10px; font-size: 0.75rem; font-weight: 600;">⚖️ MIXED</span>"""
    elif "WEAK" in r:
        return """<span style="background-color: #7F1D1D; color: #FCA5A5; padding: 2px 8px; 
                     border-radius: 10px; font-size: 0.75rem; font-weight: 600;">⚠️ WEAK</span>"""
    else:
        return """<span style="background-color: #374151; color: #D1D5DB; padding: 2px 8px; 
                     border-radius: 10px; font-size: 0.75rem; font-weight: 600;">ℹ️ INSUFFICIENT DATA</span>"""


def apply_custom_css():
    """Inject Rajasthan Royals custom CSS styling."""
    st.markdown(f"""
    <style>
    /* Global Styles */
    .stApp {{
        background-color: #0A1128;
        color: #F8FAFC;
    }}
    
    /* Header & Branding */
    .rr-header-box {{
        background: linear-gradient(135deg, #0A1128 0%, #1C2541 50%, #EA1B86 100%);
        padding: 24px 32px;
        border-radius: 16px;
        border-bottom: 4px solid #EA1B86;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
        margin-bottom: 24px;
    }}
    .rr-title {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        margin: 0;
    }}
    .rr-title span {{
        color: #EA1B86;
    }}
    .rr-subtitle {{
        font-size: 1.0rem;
        color: #94A3B8;
        margin-top: 6px;
        margin-bottom: 0;
    }}

    /* KPI Cards */
    .kpi-card {{
        background: #1C2541;
        border-radius: 12px;
        padding: 18px 20px;
        border: 1px solid rgba(234, 27, 134, 0.2);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        border-color: #EA1B86;
    }}
    .kpi-label {{
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #94A3B8;
        font-weight: 600;
        margin-bottom: 6px;
    }}
    .kpi-value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.2;
    }}
    .kpi-subtext {{
        font-size: 0.75rem;
        color: #EA1B86;
        margin-top: 4px;
        font-weight: 500;
    }}

    /* Callout & Boundary Box */
    .boundary-box {{
        background-color: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #EF4444;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 8px 0;
        font-size: 0.85rem;
        color: #FCA5A5;
    }}
    .insight-box {{
        background-color: rgba(0, 75, 160, 0.15);
        border-left: 4px solid #004BA0;
        padding: 14px 18px;
        border-radius: 0 8px 8px 0;
        margin: 12px 0;
        font-size: 0.9rem;
        color: #93C5FD;
    }}
    </style>
    """, unsafe_allow_html=True)

