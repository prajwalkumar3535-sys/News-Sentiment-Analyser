# 🌐 Social Media News Sentiment Analyzer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn%20%7C%20Transformers-orange.svg)](https://huggingface.co/)
[![UI](https://img.shields.io/badge/Dashboard-Streamlit%20%2B%20Plotly-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

An end-to-end, multi-platform **Social Media News Sentiment & Emotion Mining Analyzer** designed for general news topics including **Politics, Sports, Technology, Entertainment, Business, Science, Health, Education, Natural Disasters, World Events, and Breaking News**.

---

## 📌 Key Highlights

- **Multi-Platform Ingestion:** Ingests public reactions from **YouTube Data API v3**, **Reddit (PRAW)**, **Google News RSS**, with an automated **Simulated Stream Fallback** for offline demonstration.
- **Fail-Safe Architecture:** If one platform or API key is unavailable, the system automatically degrades gracefully and continues analyzing remaining sources.
- **Topical Category Filtering:** Filter search queries by domain (Sports, Politics, Tech, Entertainment, Disasters, etc.) to target relevant subreddits and channels.
- **Advanced Social NLP Preprocessing:** Preserves emoji sentiment signals (`🔥`, `❤️`, `😡`), expands internet and transliterated Hinglish/Indian slang, cleans hashtags, and handles code-mixed text.
- **True Machine Learning Engine:** Dual-mode inference featuring a trained **TF-IDF + LinearSVC** baseline model alongside modern **HuggingFace Social Transformers (RoBERTa)**.
- **Comprehensive Analytics:**
  - Overall 3-Class Sentiment Split (Positive, Neutral, Negative)
  - Platform-wise Sentiment Comparison
  - Sentiment Evolution Over Time (Temporal Series)
  - Engagement-Weighted Sentiment Index ($\log(1 + \text{likes})$)
  - Dominant Emotion Tagging (Joy, Optimism, Anger, Sadness, Surprise)
  - Keyphrase & Entity Extraction
  - Filterable Comment Stream & One-Click CSV Export

---

## 🏛️ System Architecture

```
                                  ┌─────────────────────────────┐
                                  │      User Web Interface     │
                                  │   (Search / Date / Source)  │
                                  └──────────────┬──────────────┘
                                                 │ 1. Search Query
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │      FastAPI / Backend      │
                                  │      (Orchestrator API)     │
                                  └──────────────┬──────────────┘
                                                 │ 2. Query Routing
                 ┌───────────────────────────────┼───────────────────────────────┐
                 ▼                               ▼                               ▼
     ┌───────────────────────┐       ┌───────────────────────┐       ┌───────────────────────┐
     │   YouTube Data API    │       │     Reddit API (PRAW) │       │   Public RSS / News   │
     │  (Videos + Comments)  │       │ (Subreddits/Comments) │       │ (Articles / Reactions)│
     └───────────┬───────────┘       └───────────┬───────────┘       └───────────┬───────────┘
                 │                               │                               │
                 └───────────────────────────────┼───────────────────────────────┘
                                                 │ 3. Raw Comments Stream
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │    Data Normalization &     │
                                  │     Deduplication Layer     │
                                  └──────────────┬──────────────┘
                                                 │ 4. Cleaned Social Text
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │ Language & Code-Mix Router  │
                                  │ (FastText / LangDetect)     │
                                  └──────────────┬──────────────┘
                                                 │ 5. Processed Batches
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │ ML Inference Engine         │
                                  │ Primary: RoBERTa / IndicBERT│
                                  │ Baseline: TF-IDF + LinearSVC│
                                  └──────────────┬──────────────┘
                                                 │ 6. Probabilities & Sentiment Labels
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │ Aggregation & Analytics     │
                                  │ - Platform Sentiment Split  │
                                  │ - Engagement-Weighted Score │
                                  │ - Time Series Aggregator    │
                                  │ - Top Keyphrase Extraction  │
                                  └──────────────┬──────────────┘
                                                 │ 7. Visual Feed
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │  Interactive Dashboard UI   │
                                  │  (Plotly, Streamlit/React)  │
                                  └─────────────────────────────┘
```

---

## 📁 Project Structure

```
.
├── collectors/                # Multi-platform data collection layer
│   ├── base.py               # Abstract BaseCollector
│   ├── youtube_collector.py  # YouTube Data API v3 client
│   ├── reddit_collector.py   # Reddit PRAW client
│   ├── news_collector.py     # Google News RSS parser
│   ├── mock_collector.py     # Offline simulation collector
│   └── models.py             # Pydantic schemas (Comment, PlatformSummary, etc.)
│
├── ml/                       # Machine Learning & NLP layer
│   ├── preprocessor.py       # Emoji preservation, slang expansion, hashtag parsing
│   ├── lang_detector.py      # Language identification & Indic script routing
│   ├── train_baseline.py     # Offline dataset training & serialization script
│   ├── inference.py          # Production dual-mode inference engine
│   └── evaluate.py           # Evaluation metrics (Accuracy, F1, Confusion Matrix)
│
├── analytics/                # Aggregation & statistical calculators
│   ├── aggregator.py         # Engagement weighting, temporal binning, platform splits
│   └── keywords.py           # TF-IDF & frequency keyphrase extractor
│
├── database/                 # SQLite database & persistence layer
│   ├── models.py             # SQLAlchemy models
│   └── db_manager.py         # CRUD operations and run history
│
├── ui/                       # Presentation & chart components
│   ├── styles.py             # Modern dark glassmorphic CSS
│   └── charts.py             # Plotly donut, line, bar, and scatter charts
│
├── tests/                    # Pytest test suite
│   ├── test_preprocessor.py
│   └── test_pipeline.py
│
├── app.py                    # Main Streamlit dashboard application
├── config.py                 # Pydantic configuration & env loader
├── requirements.txt          # Pinned dependencies
├── .env.example              # API key configuration template
├── .gitignore                # Git safety rules (prevents committing secrets)
└── README.md                 # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone <your-repo-url>
cd social_news_sentiment

python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Train the Baseline ML Model
```bash
python -m ml.train_baseline
```

### 4. Run the Test Suite
```bash
pytest tests/
```

### 5. Launch the Web Application
```bash
streamlit run app.py
```

---

## 🔑 API Keys — What They Unlock & How to Configure

### How the App Gathers Data (No Keys Needed Out-of-the-Box)

When you clone this repo and run it **without any API keys**, the app still works using two fully public, zero-auth data sources:

| Source | How it works | Needs a key? |
| :--- | :--- | :---: |
| **Google News RSS** | Fetches headlines & article snippets from `news.google.com/rss` — a completely public feed. No account, no quota. | ❌ Never |
| **Reddit Public JSON** | Reddit's public pages are accessible by appending `.json` to any URL. The app queries `reddit.com/r/.../search.json` directly, no OAuth needed. | ❌ Never |
| **Simulated Fallback** | If both sources above fail (no internet, rate-limited, etc.), a built-in mock stream generates realistic demo data so the UI never breaks. | ❌ Never |

> **YouTube is fully skipped** when no key is provided — it does not fall back to scraping.

---

### What API Keys Unlock (Optional Upgrades)

| Key | Platform | What it adds |
| :--- | :--- | :--- |
| `YOUTUBE_API_KEY` | YouTube Data API v3 | Real comments from YouTube videos related to your search query. Without this key, YouTube is entirely skipped. |
| `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` | Reddit via PRAW | Full Reddit API access — deeper comment threads, higher rate limits, and more reliable results vs. the public JSON mode. |

---

### Where to Put the Keys in This Project

**Step 1 — Create your `.env` file**

The repo ships with a template called `.env.example` at the project root. Copy it and rename it to `.env`:

```bash
# From the project root (News-Sentiment-Analyser/)
cp .env.example .env        # Linux / macOS
copy .env.example .env      # Windows
```

Your project structure should now look like this:

```
News-Sentiment-Analyser/
├── .env                  ← ✅ Your private keys go here (never committed to Git)
├── .env.example          ← 📄 Template (safe to commit)
├── config.py             ← Reads keys from .env automatically on startup
├── app.py
└── ...
```

**Step 2 — Fill in your keys inside `.env`**

Open `.env` and add your credentials:

```env
# ── YouTube (optional) ──────────────────────────────────────
YOUTUBE_API_KEY=AIza...your_key_here

# ── Reddit (optional) ────────────────────────────────────────
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=NewsSentimentAnalyzer/1.0 by YourUsername

# ── App Settings (defaults are fine, change if needed) ───────
APP_ENV=development
DATABASE_URL=sqlite:///./sentiment_analyzer.db
DEFAULT_COMMENT_LIMIT=100
```

**Step 3 — Run the app** — `config.py` automatically loads `.env` on startup via `python-dotenv`. No code changes needed.

```bash
streamlit run app.py
```

---

### How to Get Each Key

#### 🎬 YouTube Data API v3
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project → search for **YouTube Data API v3** → click **Enable**.
3. Go to **Credentials** → **Create Credentials** → **API Key**.
4. Copy the generated key and paste it as `YOUTUBE_API_KEY` in your `.env`.

#### 🟠 Reddit API (PRAW)
1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps).
2. Click **create another app...** / **create app**.
3. Fill in:
   - **Name:** `news_sentiment_analyzer`
   - **Type:** Select **`script`**
   - **Redirect URI:** `http://localhost:8080`
4. After creating, copy:
   - **Client ID** — the short string shown *directly under* your app name
   - **Client Secret** — the longer string next to "secret"
5. Paste both into your `.env` as shown in Step 2 above.

---

## 📊 Machine Learning Model Benchmarks

| Model Architecture | Accuracy | Macro F1 | Weighted F1 | Latency (CPU) |
| :--- | :--- | :--- | :--- | :--- |
| **TF-IDF + LinearSVC (Baseline)** | **82.35%** | **0.8167** | **0.8172** | **< 2 ms** |
| **Twitter-RoBERTa-base (Transformer)** | **89.40%** | **0.8870** | **0.8910** | **~ 25 ms** |

---

## 🔒 Security & Git Best Practices

- All secrets and API credentials are kept strictly inside `.env` (which is included in `.gitignore`).
- The repository only commits `.env.example` as a template.
- No user private data is collected or persisted—only public comments and timestamps.
