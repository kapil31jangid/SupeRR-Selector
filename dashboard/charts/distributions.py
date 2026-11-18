"""
Distribution Visualizations (Age, Nationality, Bowling Evidence)
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_nationality_pie(df: pd.DataFrame, title: str) -> go.Figure:
    """Pie chart showing Indian vs Overseas breakdown."""
    counts = df['nationality'].value_counts().reset_index()
    counts.columns = ['nationality', 'count']

    fig = px.pie(
        counts,
        values='count',
        names='nationality',
        color='nationality',
        color_discrete_map={'Indian': '#10B981', 'Overseas': '#EA1B86'},
        hole=0.45
    )

    fig.update_traces(
        textinfo='percent+label',
        textfont=dict(color='#FFFFFF', size=12),
        marker=dict(line=dict(color='#0A1128', width=2))
    )

    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=15, color='#FFFFFF')),
        paper_bgcolor='#0B132B',
        plot_bgcolor='#1C2541',
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(font=dict(color='#FFFFFF')),
        height=320
    )
    return fig


def plot_career_stage_bar(df: pd.DataFrame, title: str) -> go.Figure:
    """Bar chart of candidate count by Career Stage / Development Category."""
    counts = df['development_category'].value_counts().reset_index()
    counts.columns = ['category', 'count']

    category_order = ["Emerging", "Young development candidate", "Prime-age performer", "Experienced performer"]
    counts['category'] = pd.Categorical(counts['category'], categories=category_order, ordered=True)
    counts = counts.sort_values('category')

    fig = px.bar(
        counts,
        x='category',
        y='count',
        color='category',
        color_discrete_map={
            "Emerging": "#10B981",
            "Young development candidate": "#3B82F6",
            "Prime-age performer": "#8B5CF6",
            "Experienced performer": "#F59E0B"
        },
        text='count'
    )

    fig.update_traces(
        textposition='outside',
        textfont=dict(color='#FFFFFF', size=12)
    )

    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=15, color='#FFFFFF')),
        paper_bgcolor='#0B132B',
        plot_bgcolor='#1C2541',
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(title="", tickfont=dict(color='#94A3B8', size=10)),
        yaxis=dict(title="Player Count", tickfont=dict(color='#94A3B8'), gridcolor='rgba(255,255,255,0.08)'),
        showlegend=False,
        height=320
    )
    return fig


def plot_bowling_phase_evidence(zero_opp_df: pd.DataFrame) -> go.Figure:
    """
    Stacked bar chart displaying observed balls in High-Extreme, Death, and Powerplay phases.
    Transparently reveals missing phase opportunities.
    """
    if zero_opp_df.empty:
        return go.Figure()

    name_col = 'player_name' if 'player_name' in zero_opp_df.columns else ('bowler_name' if 'bowler_name' in zero_opp_df.columns else zero_opp_df.columns[1])
    he_col = 'high_extreme_balls' if 'high_extreme_balls' in zero_opp_df.columns else ('he_balls' if 'he_balls' in zero_opp_df.columns else None)
    death_col = 'death_balls' if 'death_balls' in zero_opp_df.columns else None
    pp_col = 'powerplay_balls' if 'powerplay_balls' in zero_opp_df.columns else ('pp_balls' if 'pp_balls' in zero_opp_df.columns else None)

    fig = go.Figure()

    if he_col:
        fig.add_trace(go.Bar(
            y=zero_opp_df[name_col],
            x=zero_opp_df[he_col],
            name='High-Extreme Pressure Balls',
            orientation='h',
            marker=dict(color='#EF4444')
        ))

    if death_col:
        fig.add_trace(go.Bar(
            y=zero_opp_df[name_col],
            x=zero_opp_df[death_col],
            name='Death Overs Balls (17-20)',
            orientation='h',
            marker=dict(color='#F59E0B')
        ))

    if pp_col:
        fig.add_trace(go.Bar(
            y=zero_opp_df[name_col],
            x=zero_opp_df[pp_col],
            name='Powerplay Balls (1-6)',
            orientation='h',
            marker=dict(color='#3B82F6')
        ))

    fig.update_layout(
        barmode='stack',
        title=dict(
            text="<b>Observed Bowling Deliveries by Phase (Audited Evidence)</b>",
            font=dict(size=16, color='#FFFFFF')
        ),
        paper_bgcolor='#0B132B',
        plot_bgcolor='#1C2541',
        margin=dict(l=20, r=20, t=50, b=30),
        xaxis=dict(
            title=dict(text="Total Observed Balls in Phase", font=dict(color='#94A3B8')),
            tickfont=dict(color='#94A3B8'),
            gridcolor='rgba(255, 255, 255, 0.08)'
        ),
        yaxis=dict(
            tickfont=dict(color='#FFFFFF', size=11),
            autorange='reversed'
        ),
        legend=dict(
            font=dict(color='#FFFFFF', size=10),
            bgcolor='rgba(12, 35, 64, 0.8)',
            orientation='h',
            y=-0.25,
            x=0.5,
            xanchor='center'
        ),
        height=450
    )
    return fig

