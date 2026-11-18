"""
KPI Cards Component
"""

import streamlit as st


def render_kpi_card(label: str, value: str, subtext: str = "", border_color: str = "#EA1B86"):
    """Render a styled KPI metric card."""
    html = f"""
    <div style="background: #1C2541; border-radius: 12px; padding: 18px 20px; 
                border-top: 3px solid {border_color}; border: 1px solid rgba(255, 255, 255, 0.08);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35); margin-bottom: 12px;">
        <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.8px; 
                    color: #94A3B8; font-weight: 600; margin-bottom: 4px;">{label}</div>
        <div style="font-size: 1.8rem; font-weight: 800; color: #FFFFFF; line-height: 1.1;">{value}</div>
        <div style="font-size: 0.75rem; color: {border_color}; margin-top: 4px; font-weight: 500;">{subtext}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

