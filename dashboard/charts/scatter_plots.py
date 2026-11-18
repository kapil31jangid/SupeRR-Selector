"""
Interactive Scatter Plots for Talent Trajectory and Performance vs Scouting
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_pressure_vs_scouting(
    df: pd.DataFrame,
    title: str,
    pressure_col: str,
    scouting_col: str = "verified_rr_scouting_score"
) -> go.Figure:
    """
    Scatter plot comparing historical pressure execution vs long-term scouting priority.
    """
    fig = px.scatter(
        df,
        x=pressure_col,
        y=scouting_col,
        color='development_category',
        size='age_as_of_2027_04_01',
        hover_name='player_name',
        hover_data=['country', 'nationality', 'current_form_rating', 'final_verified_rank'],
        text='player_name',
        color_discrete_map={
            "Emerging": "#10B981",
            "Young development candidate": "#3B82F6",
            "Prime-age performer": "#8B5CF6",
            "Experienced performer": "#F59E0B"
        }
    )

    fig.update_traces(
        textposition='top right',
        textfont=dict(size=10, color='#F8FAFC'),
        marker=dict(line=dict(width=1.5, color='#FFFFFF'))
    )

    # Reference 45-degree diagonal line
    min_val = min(df[pressure_col].min(), df[scouting_col].min()) - 5
    max_val = max(df[pressure_col].max(), df[scouting_col].max()) + 5

    fig.add_shape(
        type='line',
        x0=min_val, y0=min_val, x1=max_val, y1=max_val,
        line=dict(color='rgba(255, 255, 255, 0.2)', dash='dash')
    )

    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=16, color='#FFFFFF')),
        paper_bgcolor='#0B132B',
        plot_bgcolor='#1C2541',
        margin=dict(l=20, r=20, t=50, b=30),
        xaxis=dict(
            title="Historical Pressure / Evidence-Qualified Score",
            titlefont=dict(color='#94A3B8'),
            tickfont=dict(color='#94A3B8'),
            gridcolor='rgba(255, 255, 255, 0.08)'
        ),
        yaxis=dict(
            title="RR Scouting Priority Score",
            titlefont=dict(color='#94A3B8'),
            tickfont=dict(color='#94A3B8'),
            gridcolor='rgba(255, 255, 255, 0.08)'
        ),
        legend=dict(
            title=dict(text="Career Stage", font=dict(color='#94A3B8')),
            font=dict(color='#FFFFFF', size=11),
            bgcolor='rgba(12, 35, 64, 0.7)',
            bordercolor='rgba(255, 255, 255, 0.1)',
            borderwidth=1
        ),
        height=450
    )
    return fig


def plot_age_vs_scouting(df: pd.DataFrame, title: str) -> go.Figure:
    """
    Scatter plot of Player Age vs RR Scouting Score illustrating development runway.
    """
    fig = px.scatter(
        df,
        x='age_as_of_2027_04_01',
        y='verified_rr_scouting_score',
        color='nationality',
        symbol='development_category',
        text='player_name',
        hover_name='player_name',
        color_discrete_map={'Indian': '#10B981', 'Overseas': '#EA1B86'}
    )

    fig.update_traces(
        textposition='top center',
        textfont=dict(size=10, color='#F8FAFC'),
        marker=dict(size=12, line=dict(width=1, color='#FFFFFF'))
    )

    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=16, color='#FFFFFF')),
        paper_bgcolor='#0B132B',
        plot_bgcolor='#1C2541',
        margin=dict(l=20, r=20, t=50, b=30),
        xaxis=dict(
            title="Age as of 1 April 2027",
            titlefont=dict(color='#94A3B8'),
            tickfont=dict(color='#94A3B8'),
            gridcolor='rgba(255, 255, 255, 0.08)'
        ),
        yaxis=dict(
            title="RR Scouting Score",
            titlefont=dict(color='#94A3B8'),
            tickfont=dict(color='#94A3B8'),
            gridcolor='rgba(255, 255, 255, 0.08)'
        ),
        legend=dict(
            font=dict(color='#FFFFFF', size=11),
            bgcolor='rgba(12, 35, 64, 0.7)'
        ),
        height=420
    )
    return fig
