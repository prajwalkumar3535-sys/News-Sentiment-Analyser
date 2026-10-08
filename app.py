import time
from datetime import datetime, timezone
import streamlit as st
import pandas as pd

from config import config, NewsCategory, PlatformType, SentimentLabel
from ui.styles import CUSTOM_CSS
from ui.charts import (
    plot_sentiment_donut,
    plot_platform_breakdown,
    plot_temporal_sentiment,
    plot_emotion_breakdown,
    plot_engagement_scatter,
)
from collectors import SocialMediaCollectorManager
from collectors.trending_news import get_trending_news
from ml.inference import ml_engine
from analytics.aggregator import aggregate_sentiment_results, compute_time_series_sentiment
from analytics.keywords import extract_top_keywords
from database.db_manager import save_search_analysis, get_recent_search_runs

# Page Configuration
st.set_page_config(
    page_title="News Pulse — Reaction Analysis",
    page_icon="🗞️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject Custom Styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize Session State
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "collector_mgr" not in st.session_state:
    st.session_state.collector_mgr = SocialMediaCollectorManager()
if "active_category" not in st.session_state:
    st.session_state.active_category = "all"
if "sample_limit" not in st.session_state:
    st.session_state.sample_limit = 50
if "target_query_to_run" not in st.session_state:
    st.session_state.target_query_to_run = None


# -----------------------------------------------------------------------------
# CORE ANALYSIS RUNNER FUNCTION
# -----------------------------------------------------------------------------
def run_sentiment_pipeline(query_text: str, category_name: str = "All Categories", limit: int = 50):
    start_time = time.time()
    
    # 1. Multi-Platform Data Ingestion
    comments, platform_summaries, active_sources = st.session_state.collector_mgr.collect_all(
        query=query_text.strip(),
        category=category_name,
        limit_per_platform=limit,
        enable_mock_fallback=True
    )

    # 2. NLP Preprocessing & ML Model Inference
    processed_comments = ml_engine.batch_analyze(comments)

    # 3. Statistical & Engagement Aggregation
    exec_duration = time.time() - start_time
    
    # Map category to enum
    try:
        cat_enum = NewsCategory(category_name)
    except Exception:
        cat_enum = NewsCategory.ALL

    result = aggregate_sentiment_results(
        query=query_text.strip(),
        category=cat_enum,
        comments=processed_comments,
        platform_summaries=platform_summaries,
        data_sources_used=active_sources,
        execution_time=exec_duration
    )

    # 4. Extract Top Keywords
    result.top_keywords = extract_top_keywords(processed_comments, top_k=10)

    # 5. Save to Database
    save_search_analysis(result)

    st.session_state.analysis_result = result
    st.session_state.target_query_to_run = None


# Check if a pending topic analysis was triggered
if st.session_state.target_query_to_run:
    with st.spinner(f"Analyzing multi-platform public reactions for '{st.session_state.target_query_to_run}'..."):
        run_sentiment_pipeline(st.session_state.target_query_to_run, limit=st.session_state.sample_limit)
        st.rerun()


# -----------------------------------------------------------------------------
# SIDEBAR (CLEAN, MINIMALIST, USER-FOCUSED)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Settings")
    st.session_state.sample_limit = st.slider(
        "Analysis Sample Depth",
        min_value=20,
        max_value=120,
        value=50,
        step=10,
        help="Volume of public reactions analyzed per platform."
    )
    
    st.divider()
    st.markdown("### Recent Analyses")
    recent_runs = get_recent_search_runs(limit=6)
    if recent_runs:
        for r in recent_runs:
            if st.button(f"{r.query_text}", key=f"hist_{r.id}", use_container_width=True):
                st.session_state.target_query_to_run = r.query_text
                st.rerun()
    else:
        st.caption("No search history yet.")

    st.divider()
    if st.button("Reset / Clear View", use_container_width=True):
        st.session_state.analysis_result = None
        st.session_state.target_query_to_run = None
        st.rerun()


# -----------------------------------------------------------------------------
# TOP EDITORIAL HEADER
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="brand-header-wrapper">
        <div class="brand-title">News Pulse</div>
        <div class="brand-subtitle">reaction analysis</div>
    </div>
    <div class="editorial-divider"></div>
    <div class="live-status-bar">
        <span class="live-dot"></span>
        <span>connected to backend — live data</span>
    </div>
    """,
    unsafe_allow_html=True
)


# -----------------------------------------------------------------------------
# VIEW ROUTING: DETAIL ANALYSIS VIEW vs. NEWS FEED GRID
# -----------------------------------------------------------------------------
res = st.session_state.analysis_result

if res:
    # -------------------------------------------------------------------------
    # DETAIL ANALYSIS DASHBOARD VIEW
    # -------------------------------------------------------------------------
    col_back, col_info = st.columns([2, 8])
    with col_back:
        if st.button("← Back to News Feed", use_container_width=True):
            st.session_state.analysis_result = None
            st.rerun()
            
    with col_info:
        sources_str = ", ".join(res.data_sources_used)
        st.markdown(
            f"<div style='font-family:JetBrains Mono; font-size:0.75rem; color:#71717a; padding-top:8px; text-align:right;'>"
            f"TOPIC: <span style='color:#f4f4f5;'>{res.query}</span> &nbsp;|&nbsp; "
            f"SOURCES: <span style='color:#ea580c;'>{sources_str}</span> &nbsp;|&nbsp; "
            f"TIME: {res.execution_time_seconds}s"
            f"</div>",
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div style="margin-top: 1rem; margin-bottom: 1.5rem;">
            <div class="news-card-cat">{res.category.value.upper()}</div>
            <div style="font-family:'Newsreader', Georgia, serif; font-size:2rem; font-weight:600; color:#f4f4f5; line-height:1.2;">
                {res.query}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. KPI STATS ROW
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(
            f"""<div class="stat-card">
                <div class="stat-label">Total Sampled</div>
                <div class="stat-value">{res.total_comments}</div>
                <div class="stat-subtext">Verified reactions</div>
            </div>""",
            unsafe_allow_html=True
        )
    with k2:
        st.markdown(
            f"""<div class="stat-card">
                <div class="stat-label">Positive</div>
                <div class="stat-value" style="color:#10B981;">{res.positive_pct}%</div>
                <div class="stat-subtext">{res.positive_count} comments</div>
            </div>""",
            unsafe_allow_html=True
        )
    with k3:
        st.markdown(
            f"""<div class="stat-card">
                <div class="stat-label">Neutral</div>
                <div class="stat-value" style="color:#64748B;">{res.neutral_pct}%</div>
                <div class="stat-subtext">{res.neutral_count} comments</div>
            </div>""",
            unsafe_allow_html=True
        )
    with k4:
        st.markdown(
            f"""<div class="stat-card">
                <div class="stat-label">Negative</div>
                <div class="stat-value" style="color:#EF4444;">{res.negative_pct}%</div>
                <div class="stat-subtext">{res.negative_count} comments</div>
            </div>""",
            unsafe_allow_html=True
        )
    with k5:
        score_prefix = "+" if res.weighted_compound_score > 0 else ""
        st.markdown(
            f"""<div class="stat-card">
                <div class="stat-label">Engagement Index</div>
                <div class="stat-value" style="color:#EA580C;">{score_prefix}{res.weighted_compound_score}</div>
                <div class="stat-subtext">{res.dominant_emotion.split()[0]}</div>
            </div>""",
            unsafe_allow_html=True
        )

    st.write("")

    # 2. CHARTS ROW 1 (Donut + Platform Breakdown)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_sentiment_donut(res), use_container_width=True)
    with c2:
        st.plotly_chart(plot_platform_breakdown(res.platform_summaries), use_container_width=True)

    # 3. CHARTS ROW 2 (Temporal Progression + Granular Emotions)
    c3, c4 = st.columns(2)
    with c3:
        time_df = compute_time_series_sentiment(res.comments, bins=8)
        st.plotly_chart(plot_temporal_sentiment(time_df), use_container_width=True)
    with c4:
        st.plotly_chart(plot_emotion_breakdown(res.comments), use_container_width=True)

    # 4. CHARTS ROW 3 (Engagement Scatter & Keywords)
    c5, c6 = st.columns([3, 2])
    with c5:
        st.plotly_chart(plot_engagement_scatter(res.comments), use_container_width=True)
    with c6:
        st.markdown("<div style='font-family:JetBrains Mono; font-size:0.8rem; color:#a1a1aa; text-transform:uppercase; margin-bottom:10px;'>Discussed Keyphrases</div>", unsafe_allow_html=True)
        if res.top_keywords:
            chips_html = '<div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:10px;">'
            for kw in res.top_keywords:
                chips_html += f'<span style="background:#1c1917; color:#f4f4f5; border:1px solid #292524; padding:5px 12px; border-radius:4px; font-size:0.8rem; font-family:JetBrains Mono;">{kw["word"]} <b style="color:#ea580c;">({kw["count"]})</b></span>'
            chips_html += '</div>'
            st.markdown(chips_html, unsafe_allow_html=True)

    st.write("")
    st.markdown("<div class='editorial-divider'></div>", unsafe_allow_html=True)

    # 5. PUBLIC REACTION EXPLORER
    st.markdown("<div style='font-family:JetBrains Mono; font-size:0.85rem; color:#f4f4f5; text-transform:uppercase; margin-bottom:12px;'>Public Comment Stream & Analysis</div>", unsafe_allow_html=True)
    
    t_all, t_pos, t_neu, t_neg, t_viral = st.tabs([
        f"All ({len(res.comments)})",
        f"Positive ({res.positive_count})",
        f"Neutral ({res.neutral_count})",
        f"Negative ({res.negative_count})",
        "Top Engaged"
    ])

    def render_clean_comments(comment_list):
        if not comment_list:
            st.caption("No comments in this section.")
            return

        for c in comment_list[:30]:
            badge_cls = "badge-pos-clean" if c.sentiment == SentimentLabel.POSITIVE else ("badge-neu-clean" if c.sentiment == SentimentLabel.NEUTRAL else "badge-neg-clean")
            score_pfx = "+" if c.compound_score > 0 else ""
            st.markdown(
                f"""
                <div class="comment-item">
                    <div class="comment-item-text">{c.raw_text}</div>
                    <div class="comment-item-meta">
                        <span style="color:#ea580c;">{c.platform.value.replace(" & RSS", "").replace(" Articles", "")}</span>
                        <span class="{badge_cls}">{c.sentiment.value} ({score_pfx}{c.compound_score})</span>
                        <span>{c.dominant_emotion.split()[0]}</span>
                        <span>{c.likes_count} upvotes</span>
                        <span>{c.timestamp.strftime('%Y-%m-%d %H:%M')}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with t_all:
        render_clean_comments(res.comments)
    with t_pos:
        render_clean_comments([c for c in res.comments if c.sentiment == SentimentLabel.POSITIVE])
    with t_neu:
        render_clean_comments([c for c in res.comments if c.sentiment == SentimentLabel.NEUTRAL])
    with t_neg:
        render_clean_comments([c for c in res.comments if c.sentiment == SentimentLabel.NEGATIVE])
    with t_viral:
        viral_comments = sorted(res.comments, key=lambda x: x.likes_count, reverse=True)
        render_clean_comments(viral_comments)

    # 6. EXPORT
    st.write("")
    df_export = pd.DataFrame([
        {
            "Platform": c.platform.value,
            "Comment": c.raw_text,
            "Sentiment": c.sentiment.value if c.sentiment else "Neutral",
            "CompoundScore": c.compound_score,
            "Emotion": c.dominant_emotion,
            "Likes": c.likes_count,
            "Timestamp": c.timestamp,
        }
        for c in res.comments
    ])
    st.download_button(
        label="Download Raw Dataset (CSV)",
        data=df_export.to_csv(index=False).encode("utf-8"),
        file_name=f"sentiment_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )

else:
    # -------------------------------------------------------------------------
    # MAIN EDITORIAL NEWS GRID VIEW
    # -------------------------------------------------------------------------
    
    # 1. Live Headlines Ticker
    st.markdown(
        """
        <div class="ticker-container">
            <span class="ticker-highlight">LIVE TICKER:</span>
            appliance deal paid him $137.5 million &nbsp;·&nbsp; 
            <span style="color:#d4d4d8;">BUSINESS</span> — GST Council to focus only on process reforms in Oct: Sitharaman &nbsp;·&nbsp; 
            <span style="color:#d4d4d8;">TECHNOLOGY</span> — Government unveils AI ecosystem framework &nbsp;·&nbsp; 
            <span style="color:#d4d4d8;">POLITICS</span> — Midterm state election campaigns accelerate
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Category Filter Pills Row
    categories = ["all", "politics", "entertainment", "sports", "business", "technology"]
    
    col_cats = st.columns(len(categories) + 1)
    for idx, cat in enumerate(categories):
        with col_cats[idx]:
            is_active = st.session_state.active_category == cat
            btn_label = f"• {cat.capitalize()}" if is_active else cat.capitalize()
            btn_type = "primary" if is_active else "secondary"
            if st.button(btn_label, key=f"cat_btn_{cat}", type=btn_type, use_container_width=True):
                st.session_state.active_category = cat
                st.rerun()

    st.write("")

    # 3. Custom Topic Search Input
    c_search, c_btn = st.columns([5, 1])
    with c_search:
        custom_query = st.text_input(
            "Search or enter custom topic:",
            placeholder="Search any headline, company, event, or topic to analyze sentiment...",
            label_visibility="collapsed"
        )
    with c_btn:
        if st.button("Analyze Topic", type="primary", use_container_width=True) and custom_query.strip():
            st.session_state.target_query_to_run = custom_query.strip()
            st.rerun()

    st.write("")

    # 4. Fetch Categorized News Cards
    news_items = get_trending_news(category=st.session_state.active_category, limit=9)

    # Render Cards in 3 Columns Grid
    cols = st.columns(3)
    for idx, item in enumerate(news_items):
        col_idx = idx % 3
        with cols[col_idx]:
            # Calculate sentiment bar proportions
            p_pos = item.get("pos", 45)
            p_neu = item.get("neu", 35)
            p_neg = item.get("neg", 20)
            
            # HTML Card structure matching the reference design
            card_html = f"""
            <div class="news-card">
                <div>
                    <div class="news-card-cat">{item['category']}</div>
                    <div class="news-card-headline">{item['title']}</div>
                    <div class="news-card-summary">{item['summary']}</div>
                </div>
                <div>
                    <div class="sentiment-track">
                        <div class="seg-pos" style="width: {p_pos}%;"></div>
                        <div class="seg-neu" style="width: {p_neu}%;"></div>
                        <div class="seg-neg" style="width: {p_neg}%;"></div>
                    </div>
                    <div class="news-card-footer">
                        <span>{item['source']}</span>
                        <span>{item['time_ago']}</span>
                    </div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            # Clickable trigger button for each topic
            if st.button(f"Analyze Reaction →", key=f"analyze_btn_{item['id']}", use_container_width=True):
                st.session_state.target_query_to_run = item['query']
                st.rerun()
            
            st.markdown("<div style='margin-bottom: 1.2rem;'></div>", unsafe_allow_html=True)
