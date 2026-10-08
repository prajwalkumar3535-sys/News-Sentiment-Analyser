CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400&display=swap');

    /* Global Typography & Reset */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #0c0a09 !important;
        color: #f4f4f5 !important;
    }

    /* Container Spacing */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1320px !important;
    }

    /* Remove Default Streamlit Header Clutter */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Top Brand Header */
    .brand-header-wrapper {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        padding-bottom: 0.75rem;
    }

    .brand-title {
        font-family: 'Newsreader', Georgia, serif;
        font-size: 2.8rem;
        font-weight: 500;
        letter-spacing: -0.02em;
        color: #f5f5f4;
        margin: 0;
        line-height: 1;
    }

    .brand-subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        font-weight: 500;
        color: #ea580c;
        letter-spacing: 0.05em;
    }

    .editorial-divider {
        height: 1px;
        background: #27272a;
        margin: 0.5rem 0 1rem 0;
    }

    /* Live Data Status Bar */
    .live-status-bar {
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #71717a;
        margin-bottom: 0.75rem;
    }

    .live-dot {
        width: 6px;
        height: 6px;
        background-color: #22c55e;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px rgba(34, 197, 94, 0.6);
    }

    /* Live Ticker Marquee */
    .ticker-container {
        background: #141414;
        border: 1px solid #27272a;
        border-radius: 6px;
        padding: 6px 14px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #a1a1aa;
        white-space: nowrap;
        overflow: hidden;
        margin-bottom: 1.5rem;
    }

    .ticker-highlight {
        color: #ea580c;
        font-weight: 600;
        margin-right: 8px;
    }

    /* Category Navigation Bar */
    .category-pills-row {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 1.5rem;
    }

    /* News Editorial Cards */
    .news-card {
        background: #141414;
        border: 1px solid #27272a;
        border-radius: 10px;
        padding: 1.4rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 290px;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
    }

    .news-card:hover {
        border-color: #ea580c;
        transform: translateY(-2px);
        box-shadow: 0 10px 30px -10px rgba(234, 88, 12, 0.15);
    }

    .news-card-active {
        border-color: #ea580c !important;
        box-shadow: 0 0 0 1px #ea580c;
    }

    .news-card-cat {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #ea580c;
        margin-bottom: 0.6rem;
    }

    .news-card-headline {
        font-family: 'Newsreader', Georgia, serif;
        font-size: 1.25rem;
        font-weight: 600;
        line-height: 1.35;
        color: #f4f4f5;
        margin-bottom: 0.75rem;
        letter-spacing: -0.01em;
    }

    .news-card-summary {
        font-size: 0.85rem;
        line-height: 1.55;
        color: #a1a1aa;
        margin-bottom: 1.2rem;
        flex-grow: 1;
    }

    /* Sentiment Progress Multi-Segment Bar */
    .sentiment-track {
        display: flex;
        height: 4px;
        border-radius: 2px;
        overflow: hidden;
        background: #27272a;
        gap: 2px;
        margin-bottom: 0.6rem;
    }

    .seg-pos {
        background-color: #10b981;
    }

    .seg-neu {
        background-color: #475569;
    }

    .seg-neg {
        background-color: #ef4444;
    }

    /* Card Footer */
    .news-card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #71717a;
    }

    /* KPI Stat Cards for Deep Analysis View */
    .stat-card {
        background: #141414;
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 1rem 1.2rem;
    }

    .stat-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #71717a;
        font-weight: 500;
    }

    .stat-value {
        font-size: 1.7rem;
        font-weight: 600;
        margin-top: 0.2rem;
        color: #f4f4f5;
    }

    .stat-subtext {
        font-size: 0.75rem;
        color: #a1a1aa;
        margin-top: 0.15rem;
    }

    /* Comment Cards in Explorer */
    .comment-item {
        background: #141414;
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.65rem;
    }

    .comment-item-text {
        font-size: 0.9rem;
        color: #e4e4e7;
        line-height: 1.5;
        margin-bottom: 0.4rem;
    }

    .comment-item-meta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #71717a;
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
    }

    .badge-pos-clean {
        color: #10b981;
        font-weight: 600;
    }

    .badge-neu-clean {
        color: #94a3b8;
        font-weight: 600;
    }

    .badge-neg-clean {
        color: #ef4444;
        font-weight: 600;
    }

    /* Button Customization */
    div.stButton > button {
        background-color: #18181b !important;
        color: #f4f4f5 !important;
        border: 1px solid #27272a !important;
        border-radius: 6px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 0.45rem 1rem !important;
        transition: all 0.2s ease !important;
    }

    div.stButton > button:hover {
        border-color: #ea580c !important;
        color: #ffffff !important;
        background-color: #27272a !important;
    }

    div.stButton > button[kind="primary"] {
        background-color: #ea580c !important;
        border-color: #ea580c !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #c2410c !important;
        border-color: #c2410c !important;
    }

    /* Text Input Styling */
    div[data-baseweb="input"] {
        background-color: #141414 !important;
        border: 1px solid #27272a !important;
        border-radius: 6px !important;
    }

    div[data-baseweb="input"] input {
        color: #f4f4f5 !important;
        font-size: 0.9rem !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0c0a09 !important;
        border-right: 1px solid #1f1f23 !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem !important;
    }

    /* Tab Customization */
    button[data-baseweb="tab"] {
        color: #71717a !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ea580c !important;
        border-bottom-color: #ea580c !important;
        font-weight: 600 !important;
    }
</style>
"""
