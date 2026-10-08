import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List
from collectors.models import SearchAnalysisResult, Comment, PlatformSummary

# Clean Editorial Color Palette
COLOR_POS = "#10B981"  # Emerald
COLOR_NEU = "#64748B"  # Slate Neutral
COLOR_NEG = "#EF4444"  # Crimson
BG_COLOR = "rgba(0, 0, 0, 0)"
GRID_COLOR = "rgba(255, 255, 255, 0.06)"
TEXT_COLOR = "#A1A1AA"
FONT_FAMILY = "Inter, -apple-system, sans-serif"


def plot_sentiment_donut(result: SearchAnalysisResult) -> go.Figure:
    """
    Renders a minimalist donut chart of overall sentiment breakdown.
    """
    labels = ["Positive", "Neutral", "Negative"]
    values = [result.positive_count, result.neutral_count, result.negative_count]
    colors = [COLOR_POS, COLOR_NEU, COLOR_NEG]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.72,
                marker=dict(colors=colors, line=dict(color="#141414", width=2)),
                textinfo="percent",
                textposition="outside",
                hoverinfo="label+value+percent",
            )
        ]
    )

    score_prefix = "+" if result.avg_compound_score > 0 else ""
    fig.add_annotation(
        text=f"<b style='font-size:24px;color:#F4F4F5;'>{score_prefix}{result.avg_compound_score}</b><br><span style='font-size:11px;color:#71717A;font-family:JetBrains Mono;'>COMPOUND INDEX</span>",
        x=0.5,
        y=0.5,
        showarrow=False,
    )

    fig.update_layout(
        title=dict(text="<b>Overall Sentiment Distribution</b>", font=dict(color="#F4F4F5", size=14, family=FONT_FAMILY)),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(family=FONT_FAMILY, color=TEXT_COLOR, size=11),
        margin=dict(t=45, b=25, l=25, r=25),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        height=300,
    )
    return fig


def plot_platform_breakdown(platform_summaries: Dict[str, PlatformSummary]) -> go.Figure:
    """
    Renders a grouped bar chart comparing sentiment distributions across platforms.
    """
    platforms = []
    pos_pcts = []
    neu_pcts = []
    neg_pcts = []

    for name, summary in platform_summaries.items():
        if summary.total_comments > 0:
            # Shorten names for clean display
            clean_name = name.replace(" & RSS", "").replace(" Articles", "")
            platforms.append(clean_name)
            pos_pcts.append(summary.positive_pct)
            neu_pcts.append(summary.neutral_pct)
            neg_pcts.append(summary.negative_pct)

    if not platforms:
        platforms = ["Sample Stream"]
        pos_pcts, neu_pcts, neg_pcts = [45], [35], [20]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Positive", x=platforms, y=pos_pcts, marker_color=COLOR_POS))
    fig.add_trace(go.Bar(name="Neutral", x=platforms, y=neu_pcts, marker_color=COLOR_NEU))
    fig.add_trace(go.Bar(name="Negative", x=platforms, y=neg_pcts, marker_color=COLOR_NEG))

    fig.update_layout(
        barmode="group",
        title=dict(text="<b>Sentiment by Social Platform (%)</b>", font=dict(color="#F4F4F5", size=14, family=FONT_FAMILY)),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(family=FONT_FAMILY, color=TEXT_COLOR, size=11),
        xaxis=dict(gridcolor=GRID_COLOR, showline=False),
        yaxis=dict(gridcolor=GRID_COLOR, showline=False, range=[0, 100]),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        margin=dict(t=45, b=25, l=25, r=25),
        height=300,
    )
    return fig


def plot_temporal_sentiment(time_df: pd.DataFrame) -> go.Figure:
    """
    Renders a dual-axis line/bar chart of sentiment index over time alongside comment volume.
    """
    fig = go.Figure()

    if time_df.empty:
        return fig

    # Volume Bar Trace
    fig.add_trace(
        go.Bar(
            x=time_df["timestamp"],
            y=time_df["volume"],
            name="Volume",
            marker_color="rgba(113, 113, 122, 0.35)",
            yaxis="y2",
        )
    )

    # Sentiment Compound Line Trace
    fig.add_trace(
        go.Scatter(
            x=time_df["timestamp"],
            y=time_df["compound_avg"],
            name="Sentiment Index",
            mode="lines+markers",
            line=dict(color="#EA580C", width=2.5, shape="spline"),
            marker=dict(size=6, color="#F97316"),
            yaxis="y",
        )
    )

    fig.update_layout(
        title=dict(text="<b>Sentiment Evolution Over Time</b>", font=dict(color="#F4F4F5", size=14, family=FONT_FAMILY)),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(family=FONT_FAMILY, color=TEXT_COLOR, size=11),
        xaxis=dict(gridcolor=GRID_COLOR, showline=False),
        yaxis=dict(
            gridcolor=GRID_COLOR, 
            showline=False, 
            title="Index (-1 to +1)", 
            range=[-1.05, 1.05]
        ),
        yaxis2=dict(
            showgrid=False,
            title="Volume",
            overlaying="y",
            side="right",
            showline=False
        ),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        margin=dict(t=45, b=25, l=25, r=25),
        height=320,
    )
    return fig


def plot_emotion_breakdown(comments: List[Comment]) -> go.Figure:
    """
    Renders a horizontal bar chart of granular emotion breakdown.
    """
    if not comments:
        return go.Figure()

    emotion_counts = {}
    for c in comments:
        emo = c.dominant_emotion or "Neutral"
        # Clean any emoji from emotion string for crisp presentation
        clean_emo = emo.split()[0] if emo else "Neutral"
        emotion_counts[clean_emo] = emotion_counts.get(clean_emo, 0) + 1

    sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:6]
    labels = [k for k, v in sorted_emotions]
    values = [v for k, v in sorted_emotions]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(
                color=values,
                colorscale="Sunsetdark",
                line=dict(color="rgba(255,255,255,0.1)", width=1)
            ),
        )
    )

    fig.update_layout(
        title=dict(text="<b>Dominant Emotions Detected</b>", font=dict(color="#F4F4F5", size=14, family=FONT_FAMILY)),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(family=FONT_FAMILY, color=TEXT_COLOR, size=11),
        xaxis=dict(gridcolor=GRID_COLOR, showline=False, title="Occurrences"),
        yaxis=dict(autorange="reversed", showline=False),
        margin=dict(t=45, b=25, l=100, r=25),
        height=320,
    )
    return fig


def plot_engagement_scatter(comments: List[Comment]) -> go.Figure:
    """
    Visualizes how sentiment relates to viral engagement (likes/upvotes).
    """
    if not comments:
        return go.Figure()

    data = []
    for c in comments:
        data.append({
            "likes": max(0, c.likes_count),
            "compound": c.compound_score,
            "sentiment": c.sentiment.value if c.sentiment else "Neutral",
            "platform": c.platform.value.replace(" & RSS", "").replace(" Articles", ""),
            "text": (c.raw_text[:75] + "...") if len(c.raw_text) > 75 else c.raw_text
        })

    df = pd.DataFrame(data)
    color_map = {"Positive": COLOR_POS, "Neutral": COLOR_NEU, "Negative": COLOR_NEG}

    fig = px.scatter(
        df,
        x="compound",
        y="likes",
        color="sentiment",
        color_discrete_map=color_map,
        hover_data=["platform", "text"],
        labels={"compound": "Compound Score", "likes": "Engagement (Upvotes / Likes)"},
        title="<b>Engagement vs. Sentiment Intensity</b>"
    )

    fig.update_layout(
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(family=FONT_FAMILY, color=TEXT_COLOR, size=11),
        xaxis=dict(gridcolor=GRID_COLOR, range=[-1.05, 1.05]),
        yaxis=dict(gridcolor=GRID_COLOR),
        margin=dict(t=45, b=25, l=25, r=25),
        height=320,
    )
    return fig
