"""
Horizontal Bar Charts for Scouting Rankings
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_ranking_bar_chart(
    df: pd.DataFrame,
    title: str,
    score_col: str = "verified_rr_scouting_score",
    name_col: str = "player_name",
    role: str = "batter"
) -> go.Figure:
    """
    Generate horizontal bar chart of final shortlist scores with RR pink/blue theme.
    """
    plot_df = df.copy().sort_values(by=score_col, ascending=True)

    # Highlight Top 3 with Gold / Hot Pink
    colors = []
    ranks = plot_df['final_verified_rank'].tolist()
    for r in ranks:
        if r == 1:
            colors.append('#F59E0B')  # Gold for #1
        elif r in (2, 3):
            colors.append('#EA1B86')  # RR Pink for #2 & #3
        else:
            colors.append('#004BA0')  # Royal Blue for 4-10

    fig = go.Figure(go.Bar(
        x=plot_df[score_col],
        y=plot_df[name_col],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(255, 255, 255, 0.2)', width=1)
        ),
        text=plot_df[score_col].apply(lambda x: f"{x:.2f}"),
        textposition='outside',
        textfont=dict(color='#F8FAFC', size=12, family='Segoe UI'),
        hovertemplate="<b>%{y}</b><br>RR Scouting Score: %{x:.2f}<br>Rank: %{customdata[0]}<br>Age: %{customdata[1]}<br>Category: %{customdata[2]}<extra></extra>",
        customdata=plot_df[['final_verified_rank', 'age_as_of_2027_04_01', 'development_category']]
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=18, color='#FFFFFF', family='Segoe UI')
        ),
        paper_bgcolor='#0B132B',
        plot_bgcolor='#1C2541',
        margin=dict(l=20, r=40, t=50, b=30),
        xaxis=dict(
            title="RR Scouting Priority Score (40/30/20/10)",
            titlefont=dict(size=12, color='#94A3B8'),
            tickfont=dict(color='#94A3B8'),
            gridcolor='rgba(255, 255, 255, 0.08)',
            range=[0, 105]
        ),
        yaxis=dict(
            tickfont=dict(color='#FFFFFF', size=12),
            gridcolor='rgba(255, 255, 255, 0.04)'
        ),
        height=450
    )
    return fig
