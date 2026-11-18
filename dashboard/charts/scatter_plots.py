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
    available_hover = [c for c in ['country', 'nationality', 'current_form_rating', 'final_verified_rank'] if c in df.columns]
    fig = px.scatter(
        df,
        x=pressure_col,
        y=scouting_col,
        color='development_category',
        size='age_as_of_2027_04_01' if 'age_as_of_2027_04_01' in df.columns else None,
        hover_name='player_name',
        hover_data=available_hover,
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
        textfont=dict(size=11, color='#F8FAFC', family='Segoe UI'),
        marker=dict(line=dict(width=1.5, color='#FFFFFF')),
        cliponaxis=False
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
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=17, color='#FFFFFF', family='Segoe UI'),
            y=0.97,
            x=0.01,
            xanchor='left'
        ),
        paper_bgcolor='#0B132B',
        plot_bgcolor='#1C2541',
        margin=dict(l=30, r=30, t=70, b=75),
        xaxis=dict(
            title=dict(text="Historical Pressure / Evidence-Qualified Score", font=dict(color='#94A3B8', size=12)),
            tickfont=dict(color='#94A3B8', size=11),
            gridcolor='rgba(255, 255, 255, 0.08)'
        ),
        yaxis=dict(
            title=dict(text="RR Scouting Priority Score", font=dict(color='#94A3B8', size=12)),
            tickfont=dict(color='#94A3B8', size=11),
            gridcolor='rgba(255, 255, 255, 0.08)'
        ),
        legend=dict(
            title=dict(text="", font=dict(color='#94A3B8')),
            font=dict(color='#FFFFFF', size=10),
            bgcolor='rgba(12, 35, 64, 0.85)',
            bordercolor='rgba(255, 255, 255, 0.15)',
            borderwidth=1,
            orientation='h',
            y=-0.22,
            x=0.5,
            xanchor='center'
        ),
        height=480
    )
    return fig


def plot_age_vs_scouting(df: pd.DataFrame, title: str) -> go.Figure:
    """
    Scatter plot of Player Age vs RR Scouting Score illustrating development runway.
    Optimized layout with full-width scaling, horizontal bottom legend, and non-overlapping labels.
    """
    fig = px.scatter(
        df,
        x='age_as_of_2027_04_01',
        y='verified_rr_scouting_score',
        color='development_category',
        symbol='nationality',
        text='player_name',
        hover_name='player_name',
        color_discrete_map={
            "Emerging": "#10B981",
            "Young development candidate": "#00D2FF",
            "Prime-age performer": "#8B5CF6",
            "Experienced performer": "#F59E0B"
        },
        symbol_map={'Indian': 'circle', 'Overseas': 'diamond'}
    )

    fig.update_traces(
        textposition='top center',
        textfont=dict(size=11, color='#F8FAFC', family='Segoe UI'),
        marker=dict(size=14, line=dict(width=1.5, color='#FFFFFF')),
        cliponaxis=False
    )

    min_age = max(18.0, df['age_as_of_2027_04_01'].min() - 2.5)
    max_age = df['age_as_of_2027_04_01'].max() + 2.5

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=17, color='#FFFFFF', family='Segoe UI'),
            y=0.97,
            x=0.01,
            xanchor='left'
        ),
        paper_bgcolor='#0B132B',
        plot_bgcolor='#1C2541',
        margin=dict(l=30, r=30, t=70, b=75),
        xaxis=dict(
            title=dict(text="Age as of 1 April 2027 (Years)", font=dict(color='#94A3B8', size=12)),
            tickfont=dict(color='#94A3B8', size=11),
            gridcolor='rgba(255, 255, 255, 0.08)',
            range=[min_age, max_age],
            dtick=2
        ),
        yaxis=dict(
            title=dict(text="RR Scouting Priority Score (40/30/20/10)", font=dict(color='#94A3B8', size=12)),
            tickfont=dict(color='#94A3B8', size=11),
            gridcolor='rgba(255, 255, 255, 0.08)'
        ),
        legend=dict(
            title=dict(text="", font=dict(color='#94A3B8')),
            font=dict(color='#FFFFFF', size=10),
            bgcolor='rgba(12, 35, 64, 0.85)',
            bordercolor='rgba(255, 255, 255, 0.15)',
            borderwidth=1,
            orientation='h',
            y=-0.22,
            x=0.5,
            xanchor='center'
        ),
        height=480
    )
    return fig

