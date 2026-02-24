# 🎵 Spotify Keyword Intelligence Dashboard

> **Recruitment Assignment Submission**  
> Music Streaming App · Keyword Search Analysis · Jan 2022 – Dec 2025  
> 2,939 keywords · 3 themes · 50 sub-types · 48 months

---

## 📂 Project Structure

```
spotify_dashboard/
│
├── app.py                   ← Streamlit dashboard (main deliverable)
├── analysis.py              ← Standalone Python EDA script (console output)
├── requirements.txt         ← All Python dependencies
├── README.md                ← This file
└── Keyword_Searches.xlsx    ← Source data file (place here before running)
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the interactive dashboard

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

### 3. Run the full analysis script (console output)

```bash
python analysis.py
```

---

## 🖥️ Dashboard Overview

The Streamlit app contains **7 interactive tabs** covering all 5 assignment parts:

| Tab | Content | Assignment Part |
|-----|---------|----------------|
| 📊 Summary & Data Quality | 6 quality checks, KPIs, descriptive stats, initial observations | Part 1 |
| 📈 Trends | Monthly time series, YoY growth, seasonality, heatmap, spikes | Part 2 |
| 🎨 Themes & Categories | Theme share, sub-type breakdown, podcast vs music, genre trends | Part 2 |
| ⚔️ Competition | Competitor SoV, correlation analysis, YoY growth rates | Part 2 |
| 🔬 Advanced Analytics | Rising stars, segmentation, intent, pain points, MoM growth | Part 3 |
| 🔍 Keyword Explorer | Searchable/sortable keyword table + individual drill-down | Part 4 |
| 🎯 Strategy | 4-category recommendations + prioritisation matrix | Part 5 |

### Global Sidebar Filters (affect all charts)

- **Year Range** — select any 2022–2025 window
- **Themes** — toggle Brand / Category / Competition
- **Sub-Type Search** — text filter by sub-type name
- **Volume Slider** — filter by avg monthly search volume range

---

## 📊 Dataset Description

```
File    : Keyword_Searches.xlsx
Sheet   : Copy of Spotify_Keywords_Resear
Rows    : 2,939 keywords
Cols    : 52 total
  - Keyword              : search term string
  - Theme                : Brand | Category | Competition (typo 'Competiton' auto-fixed)
  - Sub Type             : 50 unique sub-categories
  - Avg. monthly searches: rolling average search volume
  - 2022-01 ... 2025-12  : 48 monthly volume columns (datetime format)
```

---

## 🔍 Data Quality Summary

| Check | Status | Detail |
|-------|--------|--------|
| Missing values | ✅ Clean | 0 missing across all cells |
| Theme typo | ✅ Fixed | "Competiton" → "Competition" |
| Zero values | ✅ Valid | Legitimate low-search months, min=10 |
| Outliers | ⚠️ Noted | "spotify"=2.24M (507× median), retained |
| Distribution | ⚠️ Noted | Right-skewed (mean=4,428, median=210) |
| Time series | ✅ Clean | All 48 months present for all 2,939 keywords |

---

## 📈 Key Findings

### Brand
- **+98% growth** from 2022 to 2025 (23.5M → 46.7M annual volume)
- Biggest single-year jump: **+47% in 2022→23**
- Clear seasonality peaks in **December** (Spotify Wrapped) and **January**

### Category
- **−21% decline** over 4 years (78.5M → 61.7M)
- Indicates users are navigating directly to Spotify (brand maturity)
- Hindi/Bollywood remains #1 content intent (3.1M searches/mo)

### Competition
- YouTube Music commands **40.1%** of all competitor search volume
- JioSaavn and Gaana are both declining — opportunity to capture their users
- **KukuFM & PocketFM** are emerging audio competitors in the podcast space

### Key Numbers
| Metric | Value |
|--------|-------|
| Top keyword (avg/mo) | "spotify" — 2,240,000 |
| Fastest growing keyword | "make ppt using ai" — +54,150% |
| Brand share of voice | 44.5% |
| Competitor correlation | r = −0.076 (independent of brand) |
| Pain-point keywords | 203 (ad-free, offline, free download) |

---

## 🔬 Advanced Analytics Methods

### Growth Rate Calculation
```python
growth_pct = (vol_2025 - vol_2022) / vol_2022 * 100
# Applied to keywords with vol_2022 > 100 to exclude noise
```

### Keyword Segmentation (2×2 Matrix)
```
                │  Low Growth   │  High Growth
─────────────────┼───────────────┼───────────────
High Volume     │  Cash Cows 💰 │  Stars ⭐
Low Volume      │  Dogs 🐕      │  Rising Stars 🚀
─────────────────┴───────────────┴───────────────
Split at: median volume (210) and median growth (%)
```

### User Intent Classification
```python
# Rule-based keyword parsing
Navigational  ← contains brand names (spotify, gaana, etc.)
Transactional ← contains (free, premium, download, offline, etc.)
Informational ← everything else (default)
```

### Correlation Analysis
```python
# Pearson and Spearman correlations between monthly brand & competition sums
pearson_r  = brand_monthly.corr(competition_monthly)     # = −0.076
spearman_r = scipy.stats.spearmanr(brand, competition)   # ≈ 0 (p>0.05)
```

---

## 🎯 Strategic Recommendations Summary

### Product
- Ad-free freemium tier (top pain point: 200+ frustration keywords)
- Hindi/Bollywood discovery features (3.1M searches/mo unmet)
- Podcast discovery UX hub (+35,000% motivational podcast growth)
- Offline mode UX improvements

### Marketing  
- Branded SEO investment (compounding 47% YoY returns)
- December/January seasonal campaign amplification
- Free → Premium conversion messaging

### Competitive
- Counter YouTube Music directly (40% of competitor volume)
- Capture declining JioSaavn/Gaana user base
- Watch KukuFM & PocketFM (Hindi podcast competitors)

### Growth Opportunities
1. Motivational/inspirational podcasts — 801K searches, +35,000%
2. Punjabi music editorial strategy
3. Celebrity podcast deals (Nikhil Kamath pattern)
4. Price-sensitive premium tier
5. AI creator tools for podcasters

---

## 📋 Assumptions & Limitations

### Assumptions
- "Competiton" (sic) in Theme column = "Competition" — auto-corrected
- Zero monthly values = legitimate low-search months, not missing data
- Geographic context assumed to be India (based on Hindi/Bollywood keyword prominence)
- "Avg. monthly searches" = rolling average, not real-time snapshot
- Intent classification uses heuristic rules (not ML-validated)

### Limitations
- Search volume ≠ actual streaming behaviour
- No CTR, conversion, or revenue data available
- Cannot link keyword trends directly to business outcomes
- User intent rules may misclassify edge cases
- Brand/Competition keyword classification is based on dataset labelling, not independently verified

---

## 🛠️ Technical Notes

- **Caching**: `@st.cache_data` on the data loader — reload once, instant tab switching
- **Long-format**: Data is melted to long format for Plotly time series efficiency
- **Plotly dark theme**: Consistent `plotly_dark` template with custom colour palette
- **Responsive**: All charts use `use_container_width=True` for any screen width

---

*By Ankit (AI Intelligence Data Analyst)*
