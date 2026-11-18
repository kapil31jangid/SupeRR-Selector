"""
Individual Player Scouting Profile Card
"""

from typing import Dict, Any
import streamlit as st
from dashboard.utils.formatting import (
    format_category_badge,
    format_nationality_badge,
    format_form_badge,
    RR_PINK,
    RR_ROYAL_BLUE
)


def render_player_scouting_card(p: Dict[str, Any], tactical_guideline: Any = None):
    """
    Render a comprehensive franchise war-room player profile card.
    Guarantees zero-indent HTML so Streamlit Markdown parser never renders code blocks.
    """
    cat_badge = format_category_badge(p.get('development_category', ''))
    nat_badge = format_nationality_badge(p.get('nationality', ''))
    form_badge = format_form_badge(p.get('current_form_rating', ''))

    restriction_html = ""
    if tactical_guideline and getattr(tactical_guideline, 'restricted_phases', None):
        restr_list = ", ".join(tactical_guideline.restricted_phases)
        restriction_html = f"""
<div style="background-color: rgba(239, 68, 68, 0.15); border-left: 4px solid #EF4444; padding: 8px 12px; border-radius: 4px; margin-top: 10px; font-size: 0.8rem; color: #FCA5A5;">
⚠️ <b>DEPLOYMENT RESTRICTION:</b> Prohibited from {restr_list} in Year 1.
<div style="font-size: 0.75rem; margin-top: 2px;">{tactical_guideline.tactical_rationale}</div>
</div>
"""

    card_html = f"""
<div style="background: #1C2541; border-radius: 12px; padding: 16px; border: 1px solid rgba(234, 27, 134, 0.3); box-shadow: 0 6px 16px rgba(0,0,0,0.4); margin-bottom: 14px;">
<div style="border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">
<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;">
<span style="font-size: 1.25rem; font-weight: 800; color: #FFFFFF;">{p.get('player_name', '')}</span>
<span style="font-size: 0.8rem; color: #94A3B8;">{p.get('country', '')} · ID: {p.get('player_id', '')}</span>
</div>
<div style="display: flex; flex-wrap: wrap; gap: 4px; align-items: center;">
{nat_badge} {cat_badge} {form_badge}
</div>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 12px; text-align: center;">
<div style="background: rgba(11, 19, 43, 0.6); padding: 8px 6px; border-radius: 8px;">
<div style="font-size: 0.65rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;">RR Scouting Score</div>
<div style="font-size: 1.35rem; font-weight: 800; color: {RR_PINK}; margin-top: 2px;">{float(p.get('verified_rr_scouting_score', 0)):.2f}</div>
</div>
<div style="background: rgba(11, 19, 43, 0.6); padding: 8px 6px; border-radius: 8px;">
<div style="font-size: 0.65rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;">Pressure / EQ Base</div>
<div style="font-size: 1.35rem; font-weight: 700; color: #FFFFFF; margin-top: 2px;">{float(p.get('validated_historical_pressure_score', p.get('validated_evidence_qualified_score', p.get('pressure_or_eq_score', 0)))):.2f}</div>
</div>
<div style="background: rgba(11, 19, 43, 0.6); padding: 8px 6px; border-radius: 8px;">
<div style="font-size: 0.65rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;">Age (Apr 2027)</div>
<div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-top: 2px;">{p.get('age_as_of_2027_04_01', '')} yrs</div>
</div>
<div style="background: rgba(11, 19, 43, 0.6); padding: 8px 6px; border-radius: 8px;">
<div style="font-size: 0.65rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;">Auction Status</div>
<div style="font-size: 1.05rem; font-weight: 700; color: #10B981; margin-top: 2px;">{p.get('eligibility_status', 'ELIGIBLE')}</div>
</div>
</div>
{restriction_html}
</div>
"""
    clean_html = "\n".join(line.strip() for line in card_html.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)

