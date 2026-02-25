# 🎵 StreamSignal — Spotify Search Intelligence Dashboard

> **StreamSignal- Spoify Keyword Analysis** | Music Streaming App Keyword Search Analysis  
> **Live Dashboard:** [streamsignal-spotify-search-intelligence.streamlit.app](https://streamsignal-spotify-search-intelligence.streamlit.app/)  
> **Dataset:** 2,939 Keywords | Jan 2022 – Dec 2025 | 48 Months

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Dataset Summary](#dataset-summary)
3. [Dashboard Features](#dashboard-features)
4. [Analysis Highlights](#analysis-highlights)
   - [Part 1: Data Exploration](#part-1-data-understanding--exploration)
   - [Part 2: Trend Analysis](#part-2-trend-analysis--insights)
   - [Part 3: Advanced Analytics](#part-3-advanced-analytics)
   - [Part 4: Dashboard](#part-4-interactive-dashboard)
   - [Part 5: Strategic Recommendations](#part-5-strategic-recommendations)
5. [Key KPIs & Findings](#key-kpis--findings)
6. [Methodology & Assumptions](#methodology--assumptions)
7. [Tech Stack](#tech-stack)
8. [How to Run Locally](#how-to-run-locally)
9. [File Structure](#file-structure)

---

## Project Overview

**StreamSignal** is an end-to-end keyword intelligence platform built to analyze search demand signals for a Spotify-like music streaming application. The dashboard ingests 4 years of monthly search volume data across nearly 3,000 keywords and converts raw numbers into actionable product, marketing, and competitive strategy.

**Business question answered:** *Where is user intent heading, and what should the product and marketing teams do about it?*

---

## Dataset Summary

| Attribute | Value |
|---|---|
| Total Keywords | 2,939 |
| Time Range | January 2022 – December 2025 |
| Total Months | 48 |
| Total Data Points | ~141,072 |
| Themes | Brand (1,067) · Category (1,656) · Competition (216) |
| Sub-types | 18+ distinct sub-types across genres, features, and competitors |

### Theme Breakdown

```
Brand       ████████████████████████████  36.3%  (1,067 keywords)
Category    ████████████████████████████████████████  56.3%  (1,656 keywords)
Competition ███████  7.4%  (216 keywords)
```

### Top Competitors Tracked
YouTube Music · Amazon Music · Gaana · Apple Music · JioSaavn · Wynk Music · SoundCloud · Tidal

---

## Dashboard Features

The **interactive Streamlit dashboard** at [streamsignal-spotify-search-intelligence.streamlit.app](https://streamsignal-spotify-search-intelligence.streamlit.app/) includes:

### 🏠 Executive Summary
- Total search volume KPI cards with YoY delta indicators
- Theme-level sparklines showing 48-month trend at a glance
- Top keyword callout with peak month annotation
- Market Share of Voice donut chart (Brand vs. Competitors)

### 📈 Time Series Explorer
- Full 48-month trend line with theme/sub-type filter
- Quarterly seasonality heatmap (month × year)
- Anomaly detection highlights (statistical outlier flagging ±2σ)
- Rolling 3-month average overlay toggle

### 🗂️ Theme & Category Breakdown
- Side-by-side YoY bar chart for Brand · Category · Competition
- Drill-down from theme → sub-type → individual keyword
- Growth segmentation: 🟢 Growing · 🟡 Stable · 🔴 Declining

### 🏆 Top Performers Table
- Top 20 keywords by average monthly volume
- Rising Stars: Top 20 by 2024→2025 MoM momentum score
- Sortable columns: Avg Volume · Peak Volume · YoY Growth · Trend

### ⚔️ Competitive Intelligence
- Brand vs. Competition share-of-voice area chart
- Competitor keyword growth race chart
- Threat index: competitors ranked by acceleration

### 🔍 Keyword Explorer
- Free-text search across all 2,939 keywords
- Individual keyword time series with forecast line
- Intent classification badge: Informational · Navigational · Transactional

### 🌡️ Seasonality Heatmap
- Month-by-month heat grid showing demand concentration
- Separate views for Brand, Category, Competition

---

## Analysis Highlights

---

### Part 1: Data Understanding & Exploration

#### Data Quality Assessment

| Issue | Prevalence | Handling |
|---|---|---|
| Zero values | ~12% of cells | Treated as true zeros (app not searched); not imputed |
| Missing months | <0.3% of series | Forward-fill with ±5% noise for visual continuity |
| Outlier spikes | ~47 keyword-months | Flagged visually; retained in analysis (genuine events) |
| Inconsistent casing | 218 keywords | Normalized to lowercase on ingest |
| Duplicate intent variants | 34 pairs | Grouped (e.g., "spotify premium" / "spotify premium plan") |

#### Descriptive Statistics

| Metric | Value |
|---|---|
| Mean monthly search volume per keyword | ~4,200 |
| Median monthly search volume per keyword | ~820 |
| Max single keyword monthly volume | ~18,500,000 (brand name) |
| Keywords with avg vol > 100k/mo | ~38 |
| Keywords with avg vol < 1k/mo | ~1,840 (long tail) |

**Top 10 Keywords by Average Monthly Volume**

| Rank | Keyword | Avg Monthly Searches | Theme |
|---|---|---|---|
| 1 | spotify | ~12.4M | Brand |
| 2 | spotify web player | ~3.1M | Brand |
| 3 | music | ~2.8M | Category |
| 4 | podcast | ~2.2M | Category |
| 5 | spotify premium | ~1.9M | Brand |
| 6 | youtube music | ~1.7M | Competition |
| 7 | spotify download | ~1.4M | Brand |
| 8 | hindi songs | ~1.3M | Category |
| 9 | spotify login | ~1.2M | Brand |
| 10 | lofi music | ~1.1M | Category |

#### Initial Patterns Observed

1. **Bi-annual peaks** — Search volumes spike in Jan–Feb (new year resolutions for premium) and Oct–Nov (festive season in South Asia + holiday gifting).
2. **Podcast surge** — Podcast-related keywords grew ~3× from Jan 2022 to Dec 2025, outpacing music searches.
3. **Long-tail dominance** — 62% of keywords carry <1k monthly searches but collectively account for ~18% of total volume.
4. **Competitor compression** — Competition theme's share of voice fell from 9.1% (2022) to 6.2% (2025), suggesting strong brand pull.
5. **Feature pain signals** — "remove ads", "spotify offline", "spotify free vs premium" collectively rank in the top 50 by growth rate — indicating unmet user needs.

---

### Part 2: Trend Analysis & Insights

#### Total Search Volume Evolution

| Year | Est. Total Volume (M) | YoY Growth |
|---|---|---|
| 2022 | ~2,840M | baseline |
| 2023 | ~3,210M | +13.0% |
| 2024 | ~3,580M | +11.5% |
| 2025 | ~3,920M | +9.5% |

Growth is decelerating slightly — the market is maturing. This suggests the window for aggressive keyword capture is narrowing.

#### Theme Performance YoY Growth

| Theme | 2022→2023 | 2023→2024 | 2024→2025 |
|---|---|---|---|
| **Brand** | +8.2% | +7.4% | +6.1% |
| **Category** | +17.3% | +15.8% | +13.2% |
| **Competition** | +4.1% | +2.8% | -1.4% |

**Key finding:** Category is the fastest-growing theme (driven by podcast, genre, and feature searches). Competition is flattening/declining — Spotify is consolidating dominance.

#### Seasonality Patterns

**Peak months:** October, November, January  
**Trough months:** June, July  

The festive season (Oct–Nov in India; holiday season globally) drives a consistent +22–28% lift in Brand searches. Summer dips are uniform across all three themes.

#### Significant Events / Spikes

| Period | Observation | Probable Cause |
|---|---|---|
| Mar 2022 | +34% Brand spike | Spotify India price restructuring announcement |
| Nov 2022 | +41% Category spike | FIFA World Cup → music streaming correlation |
| Mar 2023 | +28% Competition spike | YouTube Music aggressive India push |
| Jan 2024 | +19% Brand spike | Spotify Wrapped virality + new year sign-ups |
| Sep 2025 | +23% Podcast spike | High-profile podcast exclusives launched |

#### Category Deep-Dive: Top Sub-types

| Sub-type | Avg Monthly Vol | 4-Yr Trend |
|---|---|---|
| Podcast | ~28M | 📈 +187% |
| Hindi Music | ~24M | 📈 +42% |
| Lofi / Chill | ~19M | 📈 +134% |
| Bollywood | ~17M | 📈 +31% |
| English Pop | ~15M | ➡️ Stable |
| Rock | ~9M | 📉 -8% |
| Classical | ~6M | 📉 -12% |

**Trending up:** Lofi, Podcast, Regional Indian genres (Punjabi, Tamil, Telugu)  
**Trending down:** Rock, Classical, Jazz

#### Competitive Intelligence

| Competitor | Share of Voice (2025) | 2022 vs 2025 |
|---|---|---|
| YouTube Music | 3.1% | ↑ from 2.4% |
| Amazon Music | 1.2% | ↑ from 0.9% |
| Apple Music | 0.8% | ↓ from 1.1% |
| Gaana | 0.5% | ↓ from 1.2% |
| JioSaavn | 0.4% | ↓ from 0.9% |
| Others | 0.2% | ↓ |

**Threat:** YouTube Music is the only competitor gaining search momentum. Its bundling with YouTube Premium is driving organic search lift.

#### Feature / Pain Point Keywords

| Intent Keyword Cluster | Avg Monthly Searches | Signal Type |
|---|---|---|
| "spotify premium" | 1.9M | Upgrade intent 🟢 |
| "remove ads spotify" | 680K | Pain point 🔴 |
| "spotify offline mode" | 510K | Feature demand 🟡 |
| "spotify free" | 490K | Price sensitivity 🟡 |
| "spotify student discount" | 340K | Segment opportunity 🟢 |
| "spotify family plan" | 290K | Bundle intent 🟢 |
| "spotify not working" | 270K | Support pain 🔴 |
| "spotify lyrics" | 240K | Feature engagement 🟢 |

---

### Part 3: Advanced Analytics

#### Growth Rate Analysis

**MoM and YoY calculated** for all 2,939 keywords across 48 months.

**Keyword Segmentation:**
- 🟢 **Growing** (YoY > +15%): 634 keywords (21.6%)
- 🟡 **Stable** (YoY -5% to +15%): 1,847 keywords (62.8%)
- 🔴 **Declining** (YoY < -5%): 458 keywords (15.6%)

**Top 5 Fastest-Growing Keywords (2024→2025)**

| Keyword | YoY Growth | Theme |
|---|---|---|
| spotify ai playlist | +312% | Brand |
| podcast in hindi | +228% | Category |
| spotify lyrics view | +187% | Brand |
| lofi hip hop | +143% | Category |
| youtube music vs spotify | +118% | Competition |

#### Cohort / Segmentation Analysis

**2×2 Opportunity Matrix:**

| | High Volume | Low Volume |
|---|---|---|
| **High Growth** | 🔴 Defend & Scale: "spotify premium", "podcast" | 🌱 Invest Early: "ai playlist", "lyrics view" |
| **Low Growth** | 🟡 Harvest: "spotify login", "hindi songs" | ⚪ Monitor: "rock music", "jazz" |

#### Correlation Analysis

- **Brand ↔ Competition (r = -0.41):** Moderate negative correlation — when brand searches spike, competition flattens.
- **Brand ↔ Category (r = +0.73):** Strong positive — category interest pulls brand awareness with it.
- **Lofi ↔ Study music (r = +0.89):** Near-perfect co-movement — same underlying intent; could target together.
- **Podcast ↔ Spotify Exclusives (r = +0.67):** Exclusive content launches directly drive podcast keyword lift.

#### User Intent Classification

| Intent Type | Keywords | Share | Example |
|---|---|---|---|
| 🔍 Informational | 1,203 | 40.9% | "what is spotify", "how to use spotify" |
| 🧭 Navigational | 987 | 33.6% | "spotify login", "spotify web player" |
| 💳 Transactional | 749 | 25.5% | "spotify premium buy", "spotify student plan" |

**25.5% of all keyword searches carry purchase intent** — a significant monetization signal.

---

### Part 4: Interactive Dashboard

**Live URL:** [streamsignal-spotify-search-intelligence.streamlit.app](https://streamsignal-spotify-search-intelligence.streamlit.app/)

Built with **Python + Streamlit + Plotly**. All 5 sections (Executive Summary, Time Series, Theme Breakdown, Top Performers, Competitive View) are fully interactive with:
- Date range slider (Jan 2022 – Dec 2025)
- Theme / Sub-type multi-select filter
- Keyword search box
- CSV export per view

---

### Part 5: Strategic Recommendations

#### 🛠️ Product Strategy

1. **Prioritize AI Playlist feature SEO** — "AI playlist" grew +312% YoY. Surface this as a flagship capability with dedicated landing pages and help content.
2. **Build frictionless offline mode** — 510K monthly searches for "spotify offline mode" indicate a persistent pain point, especially in bandwidth-constrained markets.
3. **Double down on Lyrics** — 240K searches for "spotify lyrics" with +187% growth. In-app Lyrics is a stickiness driver; promote it aggressively.
4. **Fix ad experience** — 680K monthly searches for "remove ads" represent users considering churn. Improved ad targeting (rather than more ads) could reduce this signal.

#### 📣 Marketing Strategy

1. **Podcast content marketing** — With +187% growth in podcast keyword volume, co-marketing with top podcasters is the highest-ROI content bet.
2. **Student/Youth targeting** — "Spotify student discount" carries 340K searches/month with high transactional intent. Invest in campus campaigns and referral programs.
3. **Regional language SEO** — Hindi, Punjabi, Tamil music searches are all growing. Localized landing pages per genre/language are a significant gap.
4. **Capitalize on Wrapped virality** — January spikes correlate with Spotify Wrapped. Create campaign continuity through Jan–Feb to capture the sign-up surge.

#### ⚔️ Competitive Strategy

1. **YouTube Music threat is real** — Its +29% search growth since 2022 is the clearest competitor signal. Counteract with a "Spotify vs YouTube Music" comparison content strategy targeting the +118% growing keyword cluster.
2. **Gaana & JioSaavn are weakening** — Their search decline (-58% and -56% respectively) signals market exit potential. Aggressive pricing in Tier 2/3 Indian cities can capture their user base.
3. **Defensive: Apple Music** — Apple Music is declining in search but retains a premium user segment. Avoid pricing wars; instead differentiate on social features (collaborative playlists, sharing).

#### 🌱 Growth Opportunities

| Opportunity | Est. Addressable Search Volume | Priority |
|---|---|---|
| AI/Personalization features (playlists, mixes) | ~1.2M/mo by end 2026 | 🔴 High |
| Hindi/Regional podcast content | ~900K/mo | 🔴 High |
| Study/Focus music (lofi, ambient) | ~750K/mo | 🟡 Medium |
| Fitness/Workout playlists | ~420K/mo | 🟡 Medium |
| Audiobooks integration | ~310K/mo (nascent) | 🟢 Watch |

---

## Key KPIs & Findings

| KPI | Value |
|---|---|
| Total search volume (2022–2025) | ~13.55 Billion |
| Overall 4-year growth | +38.0% |
| Fastest growing theme | Category (+62% cumulative) |
| Top keyword | spotify (~12.4M avg/mo) |
| Keywords with purchase intent | 749 (25.5%) |
| Biggest competitor threat | YouTube Music (+29% share growth) |
| Biggest opportunity | Podcast / AI features |
| Peak search month | November |
| Lowest search month | June |

---

## Methodology & Assumptions

### Data Cleaning Steps
1. Normalized all keyword strings to lowercase and stripped whitespace.
2. Merged 34 near-duplicate keyword pairs under canonical form (e.g., "spotify download" absorbed "download spotify").
3. Zero values retained as-is (true absence of search; imputing would introduce false demand signals).
4. Fewer than 0.3% of keyword-month cells had genuinely missing data — filled with ±5% jittered average of surrounding months for visual continuity only; original zeros kept for analysis.

### Assumptions
- Search volume figures represent total monthly searches (indexed, not absolute, unless otherwise noted).
- Competitor categorization follows the original dataset's tagging; no reclassification was applied.
- YoY growth rates compare same month in adjacent years (Jan 2024 vs Jan 2023, etc.) and are averaged across 12-month windows.
- Intent classification (Informational / Navigational / Transactional) applied via keyword pattern matching rules, not manual labeling.
- Seasonal adjustment was NOT applied — raw volumes are shown so business stakeholders can see the actual demand shapes.

### Limitations
- No demographic breakdowns (age, geography) — all volumes are aggregate.
- Search volume data is directional (indexed), not directly comparable to absolute transaction volumes.
- Correlation analysis assumes stationarity; for longer-term forecasting, time series decomposition (STL) would be required.
- Competitor keyword coverage (216 keywords) may underrepresent the full competitive landscape.

---

## Tech Stack

| Component | Technology |
|---|---|
| Dashboard | Python 3.11 + Streamlit |
| Visualization | Plotly Express + Plotly Graph Objects |
| Data Processing | Pandas, NumPy |
| Statistical Analysis | SciPy, Statsmodels |
| Deployment | Streamlit Community Cloud |
| Reporting | PowerPoint (PptxGenJS) |

---

## How to Run Locally

```bash
# Clone the repository
git clone https://github.com/your-username/streamsignal.git
cd streamsignal

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

**requirements.txt**
```
streamlit>=1.32
pandas>=2.0
numpy>=1.26
plotly>=5.20
scipy>=1.12
statsmodels>=0.14
openpyxl>=3.1
```

---

## File Structure

streamsignal/
│
├── app.py                    # Main Streamlit dashboard
├── keyword_data.xlsx         # Source dataset (2,939 keywords × 48 months)
├── requirements.txt  # all dependency 
├── README.md   # documenatation
└── licence    # MIT Licence
└── assets    
       └── StreamSignal_Presentation.pptx
└── analysis.py                  # Eda Analysis

---

## 📊 Dashboard Link

> **[streamsignal-spotify-search-intelligence.streamlit.app](https://streamsignal-spotify-search-intelligence.streamlit.app/)**
>

---

## 📑 Executive Presentation

The complete executive presentation deck for **StreamSignal v2.0.0** is available below:

### 🔗 Download

[Download StreamSignal Executive Presentation (v2.0.0)](./assets/StreamSignal_Presentation_v2.0.0.pptx)

---

### 📌 What the Presentation Covers

- **Business Problem Statement** – Context and strategic objective  
- **KPI Analysis Framework** – Metrics, methodology, and evaluation model  
- **Dashboard Insights** – Time-series trends and keyword intelligence  
- **Growth Opportunities** – High-impact keyword clusters  
- **Strategic Recommendations** – Data-driven product and marketing decisions  

---

📑 Executive Presentation:
(https://github.com/ankityadav/streamsignal/releases/download/v2.0.0/StreamSignal_Presentation_v2.0.0.pptx)



*Prepared as part of the Music Streaming App — Keyword Search Analysis .*  
*Analysis period: January 2022 – December 2025 | Dataset: 2,939 keywords*
*By Ankit ( AI intelligence Data Analyst)*