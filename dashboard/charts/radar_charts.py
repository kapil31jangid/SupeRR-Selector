"""
Radar Chart for Multi-Player Scouting Dimension Comparisons
"""

from typing import List, Dict
import pandas as pd
import plotly.graph_objects as go


def plot_player_radar_comparison(players_data: List[Dict]) -> go.Figure:
    """
    Generate interactive radar chart comparing selected players across 5 normalized dimensions:
    - Pressure Performance (40%)
    - Age & Development Runway (30%)
    - Skill Ceiling (20%)
    - Current Form (10%)
    - Tactical Squad Fit
    """
    categories = [
        'Pressure Execution',
        'Development Runway',
        'Skill Ceiling',
        'Current Form',
        'Tactical Squad Fit'
    ]

    colors = ['#EA1B86', '#004BA0', '#10B981', '#F59E0B', '#8B5CF6']
    fig = go.Figure()

    for idx, p in enumerate(players_data):
        # Normalize metrics to 0-100 scale
        vals = [
            float(p.get('dimA_pressure', 70.0)),
            float(p.get('dimB_age_dev', 60.0)),
            float(p.get('dimC_skill_ceiling', 75.0)),
            float(p.get('dimD_current_form', 70.0)),
            float(p.get('tactical_fit', 85.0))
        ]
        # Close the loop
        vals_closed = vals + [vals[0]]
        cats_closed = categories + [categories[0]]

        c = colors[idx % len(colors)]
        fig.add_trace(go.Scatterpolar(
            r=vals_closed,
            theta=cats_closed,
            fill='toself',
            name=f"{p['player_name']} ({p.get('country', '')})",
            line=dict(color=c, width=2),
            fillcolor=f"rgba({int(c[1:3], 16)}, {int(c[3:5], 16)}, {int(c[5:7], 16)}, 0.25)"
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color='#94A3B8', size=9),
                gridcolor='rgba(255, 255, 255, 0.1)',
                linecolor='rgba(255, 255, 255, 0.2)'
            ),
            angularaxis=dict(
                tickfont=dict(color='#FFFFFF', size=11, family='Segoe UI'),
                gridcolor='rgba(255, 255, 255, 0.1)',
                linecolor='rgba(255, 255, 255, 0.2)'
            ),
            bgcolor='#1C2541'
        ),
        paper_bgcolor='#0B132B',
        legend=dict(
            font=dict(color='#FFFFFF', size=12),
            bgcolor='rgba(12, 35, 64, 0.7)',
            bordercolor='rgba(255, 255, 255, 0.1)',
            borderwidth=1,
            orientation='h',
            yanchor='bottom',
            y=-0.25,
            xanchor='center',
            x=0.5
        ),
        margin=dict(l=40, r=40, t=30, b=50),
        height=450
    )
    return fig
