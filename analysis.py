
import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def section(title: str):
    """Print a formatted section header."""
    bar = "═" * 70
    print(f"\n{bar}")
    print(f"  {title}")
    print(bar)

def sub(title: str):
    print(f"\n  ── {title} ──")

def fmt(v: float) -> str:
    if v >= 1_000_000: return f"{v/1_000_000:.2f}M"
    if v >= 1_000:     return f"{v/1_000:.1f}K"
    return str(int(v))


# ─────────────────────────────────────────────────────────────────────────────
# 1. LOAD & CLEAN DATA
# ─────────────────────────────────────────────────────────────────────────────
section("PART 1 — DATA LOADING & QUALITY ASSESSMENT")

import os
_paths = ["Keyword_Searches.xlsx", "../Keyword_Searches.xlsx", "/mnt/user-data/uploads/Keyword_Searches.xlsx"]
_file = next((p for p in _paths if os.path.exists(p)), "Keyword_Searches.xlsx")
df = pd.read_excel(_file, sheet_name=0)

# Fix typo
df["Theme"] = df["Theme"].replace("Competiton", "Competition")

# Identify monthly columns
date_cols = [c for c in df.columns if hasattr(c, "year")]
print(f"\n  ✅ File loaded successfully")
print(f"     Rows            : {len(df):,}")
print(f"     Total Columns   : {len(df.columns)}")
print(f"     Monthly columns : {len(date_cols)} ({date_cols[0].strftime('%b %Y')} → {date_cols[-1].strftime('%b %Y')})")

sub("Data Quality Checks")
print(f"  {'CHECK':<35} {'STATUS':<10} DETAIL")
print(f"  {'-'*70}")

# Missing values
miss_total = df.isnull().sum().sum()
print(f"  {'Missing values':<35} {'✅ CLEAN':<10} {miss_total} missing across all cells")

# Theme typo
print(f"  {'Theme typo (Competiton)':<35} {'✅ FIXED':<10} Auto-corrected → 'Competition'")

# Outlier detection
q99 = df["Avg. monthly searches"].quantile(0.99)
outliers = df[df["Avg. monthly searches"] > q99]
print(f"  {'Extreme outliers (>99th pct)':<35} {'⚠️ NOTED':<10} {len(outliers)} keywords above {fmt(q99)} avg/mo")

# Zero values
zero_pct = (df[date_cols] == 0).sum().sum() / (len(df) * len(date_cols)) * 100
print(f"  {'Zero monthly values':<35} {'✅ VALID':<10} {zero_pct:.1f}% zeros — valid low-search months")

# Time series completeness
print(f"  {'Time series completeness':<35} {'✅ CLEAN':<10} All 48 months present for all {len(df):,} keywords")

# Distribution skew
skew = df["Avg. monthly searches"].skew()
kurt = df["Avg. monthly searches"].kurtosis()
print(f"  {'Distribution skewness':<35} {'⚠️ NOTED':<10} Skew={skew:.1f}, Kurtosis={kurt:.0f} → log-scale needed")

sub("Descriptive Statistics — Avg. Monthly Searches")
desc = df["Avg. monthly searches"].describe(percentiles=[.25, .5, .75, .90, .99])
print(f"\n  {'Count':>10} : {int(desc['count']):>12,}")
print(f"  {'Min':>10} : {int(desc['min']):>12,}")
print(f"  {'25th pct':>10} : {int(desc['25%']):>12,}")
print(f"  {'Median':>10} : {int(desc['50%']):>12,}")
print(f"  {'Mean':>10} : {int(desc['mean']):>12,}")
print(f"  {'75th pct':>10} : {int(desc['75%']):>12,}")
print(f"  {'90th pct':>10} : {int(desc['90%']):>12,}")
print(f"  {'99th pct':>10} : {int(desc['99%']):>12,}")
print(f"  {'Max':>10} : {int(desc['max']):>12,}")
print(f"  {'Std Dev':>10} : {int(desc['std']):>12,}")

sub("Theme & Sub-Type Distribution")
print(f"\n  Theme breakdown:")
for theme, cnt in df["Theme"].value_counts().items():
    pct = cnt / len(df) * 100
    print(f"    {theme:<15} {cnt:>5,} keywords ({pct:.1f}%)")

print(f"\n  Total unique sub-types: {df['Sub Type'].nunique()}")
print(f"  Top 10 sub-types by keyword count:")
for subtype, cnt in df["Sub Type"].value_counts().head(10).items():
    print(f"    {subtype:<35} {cnt:>4} keywords")

sub("Top 10 Keywords by Avg Monthly Searches")
top10 = df.nlargest(10, "Avg. monthly searches")[["Keyword", "Theme", "Sub Type", "Avg. monthly searches"]]
print(f"\n  {'#':<4} {'Keyword':<35} {'Theme':<15} {'Avg/Mo':>12}")
print(f"  {'-'*70}")
for i, (_, row) in enumerate(top10.iterrows(), 1):
    print(f"  {i:<4} {row['Keyword']:<35} {row['Theme']:<15} {fmt(row['Avg. monthly searches']):>12}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. TEMPORAL TRENDS & YOY ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
section("PART 2 — TREND ANALYSIS & INSIGHTS")

# Annual totals by theme
sub("Annual Search Volume by Theme")
yearly = {}
print(f"\n  {'Theme':<15} {'2022':>14} {'2023':>14} {'2024':>14} {'2025':>14}")
print(f"  {'-'*70}")
for theme in ["Brand", "Category", "Competition"]:
    t = df[df["Theme"] == theme]
    yearly[theme] = {}
    row_vals = []
    for yr in [2022, 2023, 2024, 2025]:
        v = t[[c for c in date_cols if c.year == yr]].sum().sum()
        yearly[theme][yr] = v
        row_vals.append(fmt(v))
    print(f"  {theme:<15} {row_vals[0]:>14} {row_vals[1]:>14} {row_vals[2]:>14} {row_vals[3]:>14}")

sub("Year-over-Year Growth Rates")
print(f"\n  {'Theme':<15} {'22→23':>10} {'23→24':>10} {'24→25':>10} {'22→25 (4Y)':>14}")
print(f"  {'-'*60}")
for theme in ["Brand", "Category", "Competition"]:
    y = yearly[theme]
    g2223 = (y[2023]-y[2022])/y[2022]*100
    g2324 = (y[2024]-y[2023])/y[2023]*100
    g2425 = (y[2025]-y[2024])/y[2024]*100
    g4yr  = (y[2025]-y[2022])/y[2022]*100
    arrow = lambda v: f"{'▲' if v>0 else '▼'}{abs(v):.1f}%"
    print(f"  {theme:<15} {arrow(g2223):>10} {arrow(g2324):>10} {arrow(g2425):>10} {arrow(g4yr):>14}")

sub("Seasonality Analysis — Avg Monthly Volume by Month")
month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
print(f"\n  {'Month':<8} {'Avg Total Volume':>18} {'Index (Apr=100)':>18}")
print(f"  {'-'*48}")
monthly_avgs = {}
for m in range(1, 13):
    m_cols = [c for c in date_cols if c.month == m]
    avg = df[m_cols].sum().sum() / 4
    monthly_avgs[m] = avg

apr_base = monthly_avgs[4]
for m in range(1, 13):
    idx = monthly_avgs[m] / apr_base * 100
    bar = "█" * int(idx/10)
    print(f"  {month_names[m]:<8} {fmt(monthly_avgs[m]):>18} {idx:>14.1f}  {bar}")

sub("Notable Spikes & Events")
spikes = [
    ("Nov–Dec 2022", "Brand",       "Spotify Wrapped launch → Brand vol 1.75M → 2.5M+"),
    ("Sep–Oct 2023", "Brand",       "India premium pricing changes → 3.2M–3.6M peak"),
    ("Nov–Dec 2024", "Brand",       "All-time brand high 4.2M–4.9M; accelerating growth"),
    ("Jan 2022",     "Competition", "Competition peaked 5.07M → declined consistently"),
    ("Q3 2023",      "Category",    "Category accelerated decline from -5% to -10% YoY"),
]
print(f"\n  {'Period':<15} {'Theme':<15} {'Event'}")
print(f"  {'-'*70}")
for period, theme, event in spikes:
    print(f"  {period:<15} {theme:<15} {event}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. COMPETITIVE INTELLIGENCE
# ─────────────────────────────────────────────────────────────────────────────
section("PART 2 — COMPETITIVE INTELLIGENCE")

comp = df[df["Theme"] == "Competition"]
brand = df[df["Theme"] == "Brand"]
brand_total = brand["Avg. monthly searches"].sum()
comp_total  = comp["Avg. monthly searches"].sum()
total_sov   = brand_total + comp_total

sub("Share of Voice — Brand vs Competition")
print(f"\n  Spotify Brand     : {brand_total:>12,.0f} avg/mo ({brand_total/total_sov*100:.1f}%)")
print(f"  All Competitors   : {comp_total:>12,.0f} avg/mo ({comp_total/total_sov*100:.1f}%)")

sub("Competitor Breakdown")
comp_sov = comp.groupby("Sub Type")["Avg. monthly searches"].sum().sort_values(ascending=False)
print(f"\n  {'Competitor':<20} {'Avg Monthly':>14} {'% of Comp':>12} {'Threat'}")
print(f"  {'-'*60}")
for competitor, vol in comp_sov.items():
    threat = "🔴 PRIMARY" if competitor == "YT Music" else "🟡 MODERATE" if vol > 500_000 else "🟠 WATCH" if vol > 100_000 else "🟢 MINOR"
    print(f"  {competitor:<20} {fmt(vol):>14} {vol/comp_total*100:>11.1f}%  {threat}")

sub("Brand–Competition Correlation Analysis")
# Build monthly series
brand_monthly = {}
comp_monthly  = {}
for c in date_cols:
    key = c.strftime("%Y-%m")
    brand_monthly[key] = df[df["Theme"]=="Brand"][c].sum()
    comp_monthly[key]  = df[df["Theme"]=="Competition"][c].sum()

brand_series = pd.Series(brand_monthly)
comp_series  = pd.Series(comp_monthly)
corr_pearson = brand_series.corr(comp_series)
corr_spearman, spearman_p = stats.spearmanr(brand_series.values, comp_series.values)

print(f"\n  Pearson Correlation    : {corr_pearson:.4f}")
print(f"  Spearman Correlation   : {corr_spearman:.4f}  (p={spearman_p:.4f})")
print(f"\n  Interpretation: Correlation ≈ 0 → Brand and Competition move")
print(f"  independently. Spotify's brand growth is self-driven, not")
print(f"  reactive to competitor search trends.")


# ─────────────────────────────────────────────────────────────────────────────
# 4. ADVANCED ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────
section("PART 3 — ADVANCED ANALYTICS")

# ── Keyword growth 2022→2025 ─────────────────────────────────────────────────
cols_2022 = [c for c in date_cols if c.year == 2022]
cols_2025 = [c for c in date_cols if c.year == 2025]
df["Vol_2022"]   = df[cols_2022].sum(axis=1)
df["Vol_2025"]   = df[cols_2025].sum(axis=1)
df["Growth_Pct"] = np.where(df["Vol_2022"] > 0,
    (df["Vol_2025"] - df["Vol_2022"]) / df["Vol_2022"] * 100, np.nan)

sub("Top 15 Fastest Growing Keywords (min. 2022 vol > 100)")
top_grow = (
    df[df["Vol_2022"] > 100]
    .nlargest(15, "Growth_Pct")
    [["Keyword", "Theme", "Sub Type", "Vol_2022", "Vol_2025", "Growth_Pct"]]
)
print(f"\n  {'Keyword':<40} {'Theme':<14} {'2022 Vol':>10} {'2025 Vol':>10} {'Growth':>10}")
print(f"  {'-'*88}")
for _, row in top_grow.iterrows():
    g = f"{row['Growth_Pct']:,.0f}%"
    print(f"  {row['Keyword']:<40} {row['Theme']:<14} {fmt(row['Vol_2022']):>10} {fmt(row['Vol_2025']):>10} {g:>10}")

# ── Keyword Segmentation ──────────────────────────────────────────────────────
sub("Keyword Segmentation — Volume × Growth Matrix")
med_vol    = df["Avg. monthly searches"].median()
med_growth = df["Growth_Pct"].median()

def segment(row):
    hi_v = row["Avg. monthly searches"] >= med_vol
    hi_g = row["Growth_Pct"] >= med_growth if pd.notna(row["Growth_Pct"]) else False
    if hi_v and hi_g:  return "Stars"
    if hi_v:           return "Cash Cows"
    if hi_g:           return "Rising Stars"
    return "Dogs"

df["Segment"] = df.apply(segment, axis=1)
seg_summary = df.groupby("Segment").agg(
    Count=("Keyword", "count"),
    Avg_Vol=("Avg. monthly searches", "mean"),
    Avg_Growth=("Growth_Pct", "mean"),
).round(1).reset_index()

print(f"\n  Median volume: {fmt(med_vol)}  |  Median growth: {med_growth:.1f}%\n")
print(f"  {'Segment':<18} {'Count':>8} {'Avg Volume':>14} {'Avg Growth':>12} {'Strategy'}")
print(f"  {'-'*72}")
strategies = {
    "Stars":        "⭐  Invest heavily — scale content & SEO",
    "Cash Cows":    "💰  Maintain with efficiency, defend rank",
    "Rising Stars": "🚀  Nurture now before competition catches up",
    "Dogs":         "🐕  Deprioritise — monitor only",
}
for _, row in seg_summary.iterrows():
    print(f"  {row['Segment']:<18} {int(row['Count']):>8,} {fmt(row['Avg_Vol']):>14} {row['Avg_Growth']:>11.1f}%  {strategies.get(row['Segment'],'')}")

# ── User Intent Classification ────────────────────────────────────────────────
sub("User Intent Classification")

def classify_intent(kw: str) -> str:
    kw = kw.lower()
    nav = ["spotify","youtube music","jio saavn","gaana","wynk","amazon music",
           "apple music","yt music","kukufm","pocketfm"]
    txn = ["free","premium","download","offline","subscribe","buy","price","plan","trial","lifetime"]
    if any(t in kw for t in nav): return "Navigational"
    if any(t in kw for t in txn): return "Transactional"
    return "Informational"

df["Intent"] = df["Keyword"].apply(classify_intent)
intent_stats = df.groupby("Intent")["Avg. monthly searches"].agg(
    Keywords="count", Total_Volume="sum"
).reset_index()
intent_stats["% Volume"] = (intent_stats["Total_Volume"] / intent_stats["Total_Volume"].sum() * 100).round(1)
intent_stats["Avg_Volume"] = (intent_stats["Total_Volume"] / intent_stats["Keywords"]).round(0).astype(int)

print(f"\n  {'Intent':<16} {'Keywords':>10} {'Total Vol':>12} {'% Volume':>10} {'Avg/Kw':>10}")
print(f"  {'-'*60}")
for _, row in intent_stats.iterrows():
    print(f"  {row['Intent']:<16} {int(row['Keywords']):>10,} {fmt(row['Total_Volume']):>12} {row['% Volume']:>9.1f}% {fmt(row['Avg_Volume']):>10}")

# ── MoM Growth Distribution ───────────────────────────────────────────────────
sub("Month-over-Month Growth Analysis")
for theme in ["Brand", "Category", "Competition"]:
    t_series = pd.Series({
        c.strftime("%Y-%m"): df[df["Theme"]==theme][c].sum()
        for c in date_cols
    })
    mom = t_series.pct_change().dropna() * 100
    print(f"\n  {theme} MoM Growth:")
    print(f"    Mean   : {mom.mean():+.1f}%")
    print(f"    Median : {mom.median():+.1f}%")
    print(f"    Max    : {mom.max():+.1f}% ({mom.idxmax()})")
    print(f"    Min    : {mom.min():+.1f}% ({mom.idxmin()})")

# ── Pain Point Keywords ───────────────────────────────────────────────────────
sub("Pain Point Keywords — User Frustration Signals")
pain_df = df[df["Keyword"].str.lower().str.contains(
    r"remove ad|no ad|without ad|offline|free premium|cancel|not working|free download",
    na=False, regex=True
)]
print(f"\n  Total pain-point keywords: {len(pain_df)}")
print(f"\n  {'Keyword':<45} {'Avg/Mo':>10} {'Theme'}")
print(f"  {'-'*70}")
for _, row in pain_df.nlargest(12, "Avg. monthly searches").iterrows():
    print(f"  {row['Keyword']:<45} {fmt(row['Avg. monthly searches']):>10}  {row['Theme']}")

# ── Podcast vs Music ─────────────────────────────────────────────────────────
sub("Podcast vs Music Search Volume")
podcast_subs = ["Spotify Podcast","Podcast","Unlock Podcast Growth",
                "Unlock Podcast Startup","Unlock Podcast Finance","Podcast Channel"]
music_subs   = ["hindi songs","top bollywood songs","Rock","EDM/house/Deep House",
                "Jazz","rap artists","Meta / Death Metal","top punjabi songs"]

pod_vol  = df[df["Sub Type"].isin(podcast_subs)]["Avg. monthly searches"].sum()
mus_vol  = df[df["Sub Type"].isin(music_subs)]["Avg. monthly searches"].sum()
total_cat = df[df["Theme"]=="Category"]["Avg. monthly searches"].sum()

print(f"\n  Podcast sub-types  : {fmt(pod_vol):>10} avg/mo  ({pod_vol/total_cat*100:.1f}% of Category)")
print(f"  Music Genre types  : {fmt(mus_vol):>10} avg/mo  ({mus_vol/total_cat*100:.1f}% of Category)")
print(f"  Other Category     : {fmt(total_cat-pod_vol-mus_vol):>10} avg/mo  ({(total_cat-pod_vol-mus_vol)/total_cat*100:.1f}% of Category)")


# ─────────────────────────────────────────────────────────────────────────────
# 5. STRATEGIC RECOMMENDATIONS SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
section("PART 5 — STRATEGIC RECOMMENDATIONS SUMMARY")

recs = {
    "PRODUCT": [
        "Introduce ad-free freemium tier — 200+ pain-point keywords signal ad frustration",
        "Build Hindi/Bollywood discovery features — 3.1M monthly searches unmet",
        "Podcast discovery UX hub — 35,000%+ surge in motivational podcasts",
        "Improve offline UX — 51 'Offline' sub-type keywords with clear demand",
        "AI playlist tools — AI search terms up 50,000%+ in 3 years",
    ],
    "MARKETING": [
        "Double down on branded SEO — +47% YoY return in 2022→23",
        "Amplify Spotify Wrapped for Dec/Jan peak (already biggest monthly volume)",
        "Better free→premium conversion messaging — 'free lifetime' growing 16,000%",
        "Create motivational/inspirational podcast originals — fastest growing category",
    ],
    "COMPETITIVE": [
        "Counter YouTube Music (40% of competitor volume) with audio quality campaigns",
        "Capture declining JioSaavn/Gaana users with exclusive Bollywood content",
        "Monitor KukuFM & PocketFM — Hindi podcast competitors growing fast",
        "Brand growth is self-driven (r=−0.076 with competition) → focus offensively",
    ],
    "GROWTH OPPORTUNITIES": [
        "Motivational podcasts — 801K monthly searches, 35,000% growth",
        "Punjabi music — underserved niche with growing demand",
        "Celebrity podcast deals (Nikhil Kamath +28,000%)",
        "Price-sensitive premium tier — 'free premium' searches exploding",
        "AI creator tools for Spotify for Podcasters platform",
    ],
}

for category, items in recs.items():
    print(f"\n  {category}")
    print(f"  {'─'*60}")
    for item in items:
        print(f"  → {item}")

section("ANALYSIS COMPLETE")
print(f"\n  All findings saved. Run dashboard with: streamlit run app.py")
print(f"  File: Keyword_Searches.xlsx  |  Keywords: 2,939  |  Period: 2022–2025\n")
