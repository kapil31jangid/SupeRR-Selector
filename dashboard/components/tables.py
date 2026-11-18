"""
Styled Data Table Renderers for Dashboard
"""

import pandas as pd
import streamlit as st
from dashboard.utils.formatting import (
    format_category_badge,
    format_nationality_badge,
    format_form_badge
)


def render_interactive_batter_table(df: pd.DataFrame):
    """Render the verified Top 10 Batters table."""
    display_df = df.copy()

    # Format numeric columns
    display_df['Rank'] = display_df['final_verified_rank']
    display_df['Player'] = display_df['player_name']
    display_df['Country'] = display_df['country']
    display_df['Nationality'] = display_df['nationality']
    display_df['Age (2027)'] = display_df['age_as_of_2027_04_01']
    display_df['Career Stage'] = display_df['development_category']
    display_df['Pressure Score (40%)'] = display_df['validated_historical_pressure_score'].map('{:.2f}'.format)
    display_df['RR Scouting Score'] = display_df['verified_rr_scouting_score'].map('{:.2f}'.format)
    display_df['2026 Form'] = display_df['current_form_rating']

    cols = ['Rank', 'Player', 'Country', 'Nationality', 'Age (2027)', 'Career Stage',
            'Pressure Score (40%)', 'RR Scouting Score', '2026 Form']

    st.dataframe(
        display_df[cols],
        hide_index=True,
        use_container_width=True
    )


def render_interactive_bowler_table(df: pd.DataFrame):
    """Render the verified Top 10 Bowlers table."""
    display_df = df.copy()

    display_df['Rank'] = display_df['final_verified_rank']
    display_df['Player'] = display_df['player_name']
    display_df['Country'] = display_df['country']
    display_df['Nationality'] = display_df['nationality']
    display_df['Age (2027)'] = display_df['age_as_of_2027_04_01']
    display_df['Career Stage'] = display_df['development_category']
    display_df['EQ Bowling Score (40%)'] = display_df['validated_evidence_qualified_score'].map('{:.2f}'.format)
    display_df['RR Scouting Score'] = display_df['verified_rr_scouting_score'].map('{:.2f}'.format)
    display_df['2026 Form'] = display_df['current_form_rating']

    cols = ['Rank', 'Player', 'Country', 'Nationality', 'Age (2027)', 'Career Stage',
            'EQ Bowling Score (40%)', 'RR Scouting Score', '2026 Form']

    st.dataframe(
        display_df[cols],
        hide_index=True,
        use_container_width=True
    )
