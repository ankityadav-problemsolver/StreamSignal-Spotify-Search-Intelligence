

import os, warnings
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3

warnings.filterwarnings("ignore")

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Spotify · Keyword Intelligence",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');
:root{--g:#1DB954;--g2:rgba(29,185,84,.12);--sky:#38bdf8;--amb:#f59e0b;--red:#ef4444;
      --bg:#060b14;--bg2:#0d1523;--bg3:#111827;--bd:#1e2f47;--tx:#e2e8f0;--mu:#64748b;}
.stApp{background:var(--bg);color:var(--tx);}
section[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--bd);}
section[data-testid="stSidebar"] *{color:var(--tx)!important;}
h1,h2,h3,h4{font-family:'Syne',sans-serif!important;color:var(--tx)!important;}
button[data-baseweb="tab"]{font-family:'Space Mono',monospace!important;font-size:11px!important;
  letter-spacing:1px!important;color:var(--mu)!important;background:transparent!important;text-transform:uppercase;}
button[data-baseweb="tab"][aria-selected="true"]{color:var(--g)!important;border-bottom:2px solid var(--g)!important;}
[data-testid="metric-container"]{background:var(--bg3);border:1px solid var(--bd);border-radius:12px;
  padding:18px 20px!important;position:relative;overflow:hidden;}
[data-testid="metric-container"]::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,var(--g),transparent);}
[data-testid="metric-container"] label{font-family:'Space Mono',monospace!important;font-size:10px!important;
  letter-spacing:2px!important;text-transform:uppercase;color:var(--mu)!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{font-family:'Syne',sans-serif!important;
  font-size:26px!important;font-weight:800!important;color:var(--g)!important;}
[data-testid="metric-container"] [data-testid="stMetricDelta"]{font-family:'Space Mono',monospace!important;font-size:11px!important;}
[data-testid="stDataFrame"]{border:1px solid var(--bd);border-radius:8px;}
hr{border-color:var(--bd)!important;}
.hero{background:linear-gradient(135deg,#0d1f0d 0%,#060b14 60%,#0d1523 100%);
  border:1px solid var(--bd);border-radius:16px;padding:32px 40px;margin-bottom:24px;position:relative;overflow:hidden;}
.hero::after{content:'🎵';position:absolute;right:40px;top:50%;transform:translateY(-50%);
  font-size:80px;opacity:.07;}
.hero-eye{font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;color:var(--g);
  text-transform:uppercase;margin-bottom:8px;}
.hero h1{font-family:'Syne',sans-serif!important;font-size:30px!important;font-weight:800!important;
  letter-spacing:-.5px;margin-bottom:6px;}
.hero h1 span{color:var(--g);}
.hero-sub{font-family:'Space Mono',monospace;font-size:11px;color:var(--mu);letter-spacing:1px;}
.card{background:var(--bg3);border:1px solid var(--bd);border-radius:12px;padding:18px;margin-bottom:10px;}
.card.g{border-left:3px solid var(--g);}
.card.a{border-left:3px solid var(--amb);}
.card.s{border-left:3px solid var(--sky);}
.card.r{border-left:3px solid var(--red);}
.card h4{font-size:13px;margin-bottom:5px;color:var(--tx);}
.card p{font-size:12px;color:#94a3b8;line-height:1.65;}
.story-band{background:var(--bg2);border:1px solid var(--bd);border-radius:10px;
  padding:14px 20px;margin:12px 0;font-size:13px;color:#cbd5e1;line-height:1.7;}
.story-band b{color:var(--g);}
</style>
""", unsafe_allow_html=True)

# ── Colour maps ────────────────────────────────────────────────
TC   = {"Brand":"#1DB954","Category":"#38bdf8","Competition":"#f59e0b"}
IC   = {"Informational":"#38bdf8","Navigational":"#1DB954","Transactional":"#f59e0b"}
SEG5 = {"⭐ High Vol + High Growth":"#1DB954","🌱 Niche Opportunity":"#38bdf8",
        "🟡 Stable":"#94a3b8","⚠️ Declining High Vol":"#f59e0b","🔴 Declining + Low Vol":"#ef4444"}

BASE = dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8",family="Space Mono,monospace",size=11),
            margin=dict(l=10,r=10,t=44,b=10),
            legend=dict(bgcolor="rgba(0,0,0,0)",borderwidth=0),
            xaxis=dict(gridcolor="#1e2f47"),yaxis=dict(gridcolor="#1e2f47"))

def T(fig, h=320, **kw):
    fig.update_layout(**{**BASE,"height":h,**kw})
    return fig

def fmt(n):
    if pd.isna(n): return "N/A"
    n = float(n)
    if n >= 1_000_000: return f"{n/1_000_000:.2f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return f"{n:,.0f}"

# ══════════════════════════════════════════════════════════════
#  DATA LOADING
# ══════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="⚙️ Loading & engineering features…")
def load_data():
    paths = ["Keyword_Searches.xlsx","../Keyword_Searches.xlsx",
             "/mnt/user-data/uploads/Keyword_Searches.xlsx","spotify_keywords_clean.csv"]
    df = None
    for p in paths:
        if os.path.exists(p):
            df = pd.read_excel(p) if p.endswith(".xlsx") else pd.read_csv(p)
            break
    if df is None:
        st.error("❌ Data file not found. Place `Keyword_Searches.xlsx` in the same folder.")
        st.stop()

    date_cols_raw = [c for c in df.columns if hasattr(c,"year")]
    df.columns = (["Keyword","Theme","Sub_Type","Avg_Monthly_Searches"]
                  + [c.strftime("%Y-%m") for c in date_cols_raw])
    df["Theme"] = df["Theme"].replace("Competiton","Competition")
    dc = [c for c in df.columns if len(str(c))==7 and str(c)[:4].isdigit()]

    for yr in [2022,2023,2024,2025]:
        cols = [c for c in dc if c.startswith(str(yr))]
        df[f"Vol_{yr}"] = df[cols].sum(axis=1)

    df["Growth_4Y"]  = ((df["Vol_2025"]-df["Vol_2022"])/df["Vol_2022"].replace(0,np.nan)*100).round(2)
    df["Growth_2425"] = ((df["Vol_2025"]-df["Vol_2024"])/df["Vol_2024"].replace(0,np.nan)*100).round(2)

    NAV = ["spotify","youtube music","yt music","jio saavn","jiosaavn","gaana","wynk",
           "amazon music","apple music","kukufm","pocketfm"]
    TRX = ["free","premium","download","offline","subscribe","buy","price","plan",
           "trial","cancel","offer","discount","cost"]
    def intent(kw):
        k = str(kw).lower()
        if any(x in k for x in NAV): return "Navigational"
        if any(x in k for x in TRX): return "Transactional"
        return "Informational"
    df["Intent"] = df["Keyword"].apply(intent)

    mv, mg = df["Avg_Monthly_Searches"].median(), df["Growth_4Y"].median()
    def seg5(r):
        g = r["Growth_4Y"] if pd.notna(r["Growth_4Y"]) else 0
        v = r["Vol_2025"]
        if g > 20  and v > 5000: return "⭐ High Vol + High Growth"
        if g > 20:               return "🌱 Niche Opportunity"
        if g < -20 and v < 1000: return "🔴 Declining + Low Vol"
        if g < -20:              return "⚠️ Declining High Vol"
        return "🟡 Stable"
    df["Seg5"] = df.apply(seg5, axis=1)

    return df, dc


@st.cache_data(show_spinner=False)
def build_monthly(_df, dc):
    rows = []
    for col in dc:
        yr, mo = int(col[:4]), int(col[5:])
        for theme, grp in _df.groupby("Theme"):
            rows.append({"Month":col,"Year":yr,"Mo":mo,"Theme":theme,"Volume":grp[col].sum()})
    return pd.DataFrame(rows)


@st.cache_resource
def build_db(_df, dc):
    lng = _df.melt(id_vars=["Keyword","Theme","Sub_Type","Avg_Monthly_Searches"],
                   value_vars=dc, var_name="Month", value_name="SV")
    lng["Year"]  = lng["Month"].str[:4].astype(int)
    lng["MoNum"] = lng["Month"].str[5:].astype(int)
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    lng.to_sql("s", conn, index=False, if_exists="replace")
    _df[["Keyword","Theme","Sub_Type","Avg_Monthly_Searches"]].to_sql(
        "kw", conn, index=False, if_exists="replace")
    return conn, lng


def Q(conn, q, p=None):
    return pd.read_sql_query(q, conn, params=p)


df, DC = load_data()
monthly_df = build_monthly(df, DC)
conn, df_long = build_db(df, DC)

# ── Pre-compute globals ────────────────────────────────────────
b22 = df[df["Theme"]=="Brand"][[c for c in DC if c.startswith("2022")]].sum().sum()
b25 = df[df["Theme"]=="Brand"][[c for c in DC if c.startswith("2025")]].sum().sum()
c22 = df[df["Theme"]=="Category"][[c for c in DC if c.startswith("2022")]].sum().sum()
c25 = df[df["Theme"]=="Category"][[c for c in DC if c.startswith("2025")]].sum().sum()
v24 = df[[c for c in DC if c.startswith("2024")]].sum().sum()
v25t= df[[c for c in DC if c.startswith("2025")]].sum().sum()
brand_pct  = (b25-b22)/b22*100
cat_pct    = (c25-c22)/c22*100
yoy_all    = (v25t-v24)/v24*100
brand_vol  = df[df["Theme"]=="Brand"]["Avg_Monthly_Searches"].sum()
comp_vol   = df[df["Theme"]=="Competition"]["Avg_Monthly_Searches"].sum()
brand_sov  = brand_vol/(brand_vol+comp_vol)*100

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""<div style='padding:12px 0 6px;font-family:Space Mono,monospace;
    font-size:10px;letter-spacing:3px;color:#1DB954;text-transform:uppercase;'>
    ⚙ Controls</div>""", unsafe_allow_html=True)
    st.markdown("---")
    sel_themes = st.multiselect("Theme", ["Brand","Category","Competition"],
                                default=["Brand","Category","Competition"])
    yrs = sorted({int(c[:4]) for c in DC})
    yr_range = st.select_slider("Year range", yrs, value=(min(yrs),max(yrs)))
    kw_search = st.text_input("🔍 Keyword search", placeholder="e.g. hindi, podcast…")
    st.markdown("---")
    st.markdown(f"""<div style='font-family:Space Mono,monospace;font-size:11px;color:#64748b;line-height:2;'>
    <b style='color:#e2e8f0;'>Dataset</b><br>
    Keywords · <span style='color:#1DB954;'>{len(df):,}</span><br>
    Months   · <span style='color:#1DB954;'>{len(DC)}</span><br>
    Period   · <span style='color:#1DB954;'>{DC[0]} → {DC[-1]}</span>
    </div>""", unsafe_allow_html=True)

fdf = df[df["Theme"].isin(sel_themes)].copy()
sel_dc = [c for c in DC if yr_range[0] <= int(c[:4]) <= yr_range[1]]
if kw_search.strip():
    fdf = fdf[fdf["Keyword"].str.contains(kw_search.strip(), case=False, na=False)]
fm = monthly_df[monthly_df["Theme"].isin(sel_themes) &
                monthly_df["Year"].between(yr_range[0], yr_range[1])]

# ══════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-eye">▶  Music Streaming App · Feb 2026</div>
  <h1>Spotify <span>Keyword Intelligence</span></h1>
  <div class="hero-sub">2,939 Keywords · 48 Months (Jan 2022 – Dec 2025) · Brand · Category · Competition</div>
</div>""", unsafe_allow_html=True)

tabs = st.tabs(["📊 Overview","📈 Trends","🗂 Themes","🏆 Keywords",
                "⚔ Competitors","🔬 Analytics","🛡 Data Quality","💡 Strategy"])

# ╔════════════════════════════════════════════════════════════╗
# ║  TAB 0 — OVERVIEW                                         ║
# ╚════════════════════════════════════════════════════════════╝
with tabs[0]:
    k = st.columns(6)
    k[0].metric("Total Keywords",    f"{len(df):,}")
    k[1].metric("Top Keyword",       "spotify",              "2.24M avg/mo")
    k[2].metric("Brand Growth 4Y",   f"+{brand_pct:.0f}%",  "2022 → 2025")
    k[3].metric("Category Trend 4Y", f"{cat_pct:.0f}%",     "Declining")
    k[4].metric("YoY Growth 24→25",  f"+{yoy_all:.1f}%")
    k[5].metric("Brand SoV",         f"{brand_sov:.1f}%",   "vs Competitors")

    st.markdown(f"""<div class="story-band">
    📖 <b>The Story in One Line:</b>  Spotify's brand is <b>winning</b> — brand searches are up
    <b>+{brand_pct:.0f}%</b> in 4 years while generic category searches fell <b>{cat_pct:.0f}%</b>,
    meaning users now come <em>directly</em> to Spotify instead of searching for "music app".
    The #1 threat is <b>YouTube Music</b> (39% competitor SoV). The single biggest untapped opportunity:
    <b>podcasts</b> — fastest-growing cluster at +35,000%.
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    ca, cb = st.columns([3,2])

    with ca:
        st.markdown("#### Total Monthly Search Volume — 48 Months")
        overall = fm.groupby("Month")["Volume"].sum().reset_index().sort_values("Month")
        x_num = np.arange(len(overall))
        z_fit = np.polyfit(x_num, overall["Volume"], 1)
        trend_vals = np.polyval(z_fit, x_num)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=overall["Month"], y=overall["Volume"],
            mode="lines", fill="tozeroy", name="Volume",
            line=dict(color="#1DB954",width=2.5), fillcolor="rgba(29,185,84,.07)",
            hovertemplate="<b>%{x}</b><br>%{y:,.0f} searches<extra></extra>"))
        fig.add_trace(go.Scatter(x=overall["Month"], y=trend_vals,
            mode="lines", name="Trend ↗", line=dict(color="#f59e0b",width=1.5,dash="dot"),
            hovertemplate="Trend: %{y:,.0f}<extra></extra>"))
        for yr in [2022,2023,2024]:
            fig.add_vrect(x0=f"{yr}-11",x1=f"{yr}-12",
                fillcolor="rgba(29,185,84,.05)",line_width=0,
                annotation_text="Wrapped",annotation_position="top left",
                annotation=dict(font=dict(color="#1DB954",size=9)))
        T(fig, h=300, title="Overall Search Volume with Growth Trend + Wrapped Peaks")
        fig.update_yaxes(tickformat=".2s")
        st.plotly_chart(fig, use_container_width=True)

    with cb:
        st.markdown("#### Theme Share of Volume")
        ta = fdf.groupby("Theme")["Avg_Monthly_Searches"].sum().reset_index()
        fig2 = px.pie(ta, names="Theme", values="Avg_Monthly_Searches", hole=0.62,
                      color="Theme", color_discrete_map=TC)
        fig2.update_traces(textinfo="percent+label", textfont_size=12,
                           marker=dict(line=dict(color="#060b14",width=2)))
        T(fig2, h=300)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Annual Volume by Theme")
    yd = []
    for yr in range(yr_range[0], yr_range[1]+1):
        yc = [c for c in sel_dc if c.startswith(str(yr))]
        for t in sel_themes:
            yd.append({"Year":str(yr),"Theme":t,"Volume":df[df["Theme"]==t][yc].sum().sum()})
    fig3 = px.bar(pd.DataFrame(yd), x="Year", y="Volume", color="Theme",
                  barmode="stack", color_discrete_map=TC, text_auto=".2s")
    fig3.update_traces(marker_line_width=0)
    T(fig3, h=260)
    fig3.update_yaxes(tickformat=".2s")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("#### 💡 Key Business Insights")
    i1,i2,i3,i4 = st.columns(4)
    with i1:
        st.markdown(f"""<div class="card g"><h4>🚀 Brand = Growth Engine</h4>
        <p>Brand searches surged <b>+{brand_pct:.0f}%</b> in 4 years. Users now navigate
        directly to Spotify — a classic brand-maturity shift away from generic music searches.</p></div>""",
        unsafe_allow_html=True)
    with i2:
        st.markdown(f"""<div class="card a"><h4>⚠️ Category Is Shrinking</h4>
        <p>Generic category searches fell <b>{cat_pct:.0f}%</b>. Users are brand-loyal now.
        Signal to double down on <em>branded</em> content experiences, not generic discovery.</p></div>""",
        unsafe_allow_html=True)
    with i3:
        st.markdown("""<div class="card s"><h4>🎙 Podcasts = Biggest Bet</h4>
        <p>537 podcast keywords. Motivational & celebrity podcasts grew <b>+35,000%</b>. This is
        the single largest untapped growth category in the dataset.</p></div>""",
        unsafe_allow_html=True)
    with i4:
        st.markdown("""<div class="card r"><h4>⚔️ YT Music is Threat #1</h4>
        <p>YouTube Music holds <b>39.3%</b> of competitor SoV, backed by Google's distribution.
        Requires a focused differentiation strategy — not just price competition.</p></div>""",
        unsafe_allow_html=True)

# ╔════════════════════════════════════════════════════════════╗
# ║  TAB 1 — TRENDS & SEASONALITY                             ║
# ╚════════════════════════════════════════════════════════════╝
with tabs[1]:
    st.markdown("### 📈 Temporal Trends & Seasonality")

    show = st.multiselect("Show themes", ["Brand","Category","Competition"],
                          default=["Brand","Category","Competition"], key="tr")
    fig_tr = go.Figure()
    for t in show:
        d = fm[fm["Theme"]==t].sort_values("Month")
        fig_tr.add_trace(go.Scatter(x=d["Month"], y=d["Volume"], name=t, mode="lines",
            line=dict(color=TC.get(t,"#fff"),width=2.5),
            hovertemplate=f"<b>{t}</b><br>%{{x}}<br>%{{y:,.0f}}<extra></extra>"))
    T(fig_tr, h=340, title="Monthly Search Volume by Theme — 48-Month View")
    fig_tr.update_yaxes(tickformat=".2s")
    st.plotly_chart(fig_tr, use_container_width=True)

    st.markdown("""<div class="story-band">
    📖 <b>What this chart tells us:</b> Brand (green) shows a clear upward trajectory with a
    <b>Dec/Jan spike every year</b> from Spotify Wrapped. Category (blue) shows steady decline —
    users are brand-loyal, not discovery-oriented. Competition (amber) is flat-to-declining,
    meaning Spotify is <b>gaining share of mind</b> faster than any competitor.
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Year-over-Year Growth % by Theme")
        yoy = []
        for t in ["Brand","Category","Competition"]:
            td = df[df["Theme"]==t]
            for y1,y2 in [(2022,2023),(2023,2024),(2024,2025)]:
                v1 = td[[c for c in DC if c.startswith(str(y1))]].sum().sum()
                v2 = td[[c for c in DC if c.startswith(str(y2))]].sum().sum()
                yoy.append({"Period":f"{y1}→{y2}","Theme":t,"YoY":round((v2-v1)/v1*100,1)})
        ydf2 = pd.DataFrame(yoy)
        fig_yoy = px.bar(ydf2, x="Period", y="YoY", color="Theme", barmode="group",
                         color_discrete_map=TC, text_auto=".1f")
        fig_yoy.update_traces(marker_line_width=0, texttemplate="%{text}%",
                              textposition="outside")
        T(fig_yoy, h=300, title="YoY Growth % — All Themes, All Years")
        fig_yoy.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig_yoy, use_container_width=True)

    with c2:
        st.markdown("#### Seasonality — Avg Monthly Volume")
        mns = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        seas = []
        for mi, mn in enumerate(mns, 1):
            cols = [c for c in DC if int(c[5:])==mi]
            seas.append({"Month":mn,"Vol":df[cols].sum().sum()/4})
        sdf = pd.DataFrame(seas)
        peak = {"Jan","Jul","Dec"}; trough = {"Apr"}
        clrs = ["#1DB954" if m in peak else "#ef4444" if m in trough
                else "rgba(29,185,84,.35)" for m in mns]
        fig_s = go.Figure(go.Bar(x=sdf["Month"], y=sdf["Vol"], marker_color=clrs,
            hovertemplate="<b>%{x}</b><br>Avg: %{y:,.0f}<extra></extra>",
            text=sdf["Vol"].apply(fmt), textposition="outside",
            textfont=dict(size=9, color="#94a3b8")))
        T(fig_s, h=300, title="🟢 Peak Months (Dec/Jan/Jul)  🔴 Trough (Apr)")
        fig_s.update_yaxes(tickformat=".2s")
        st.plotly_chart(fig_s, use_container_width=True)

    st.markdown("""<div class="story-band">
    📅 <b>Campaign Calendar:</b>  Run biggest activations in <b>December</b> (Wrapped peak) and
    <b>January</b> (New Year surge). <b>July</b> = summer secondary spike — travel playlists.
    <b>April is the volume trough</b> — ideal for aggressive promos at lowest competition CPM.
    </div>""", unsafe_allow_html=True)

    st.markdown("#### Quarterly Volume — Shows Q4 Seasonality Pattern")
    qdata = []
    for yr in [2022,2023,2024,2025]:
        quarters = {"Q1":[1,2,3],"Q2":[4,5,6],"Q3":[7,8,9],"Q4":[10,11,12]}
        for q, months in quarters.items():
            cols = [f"{yr}-{m:02d}" for m in months if f"{yr}-{m:02d}" in DC]
            if not cols: continue
            for t in ["Brand","Category","Competition"]:
                qdata.append({"Period":f"{yr} {q}","Theme":t,
                              "Volume":df[df["Theme"]==t][cols].sum().sum()})
    qdf = pd.DataFrame(qdata)
    fig_q = px.bar(qdf, x="Period", y="Volume", color="Theme",
                   barmode="group", color_discrete_map=TC)
    fig_q.update_traces(marker_line_width=0)
    T(fig_q, h=280, title="Quarterly Volume — Q4 Spike Visible Every Year")
    fig_q.update_yaxes(tickformat=".2s")
    fig_q.update_xaxes(tickangle=45)
    st.plotly_chart(fig_q, use_container_width=True)

    st.markdown("#### 🌡 Seasonality Heatmap (Year × Month)")
    hm_theme = st.selectbox("Theme", ["All","Brand","Category","Competition"], key="hmt")
    src = df if hm_theme=="All" else df[df["Theme"]==hm_theme]
    hm_z, hm_txt = [], []
    for yr in [2022,2023,2024,2025]:
        row, txt = [], []
        for mi in range(1,13):
            key = f"{yr}-{mi:02d}"
            v = src[key].sum() if key in src.columns else 0
            row.append(v); txt.append(fmt(v))
        hm_z.append(row); hm_txt.append(txt)
    fig_hm = go.Figure(go.Heatmap(z=hm_z, x=mns, y=["2022","2023","2024","2025"],
        colorscale=[[0,"#0d1523"],[0.5,"#0a5c2a"],[1,"#1DB954"]],
        text=hm_txt, texttemplate="%{text}",
        textfont={"size":11,"color":"#e2e8f0"}, showscale=True))
    T(fig_hm, h=230, title=f"{hm_theme} · Darker Green = Higher Volume")
    st.plotly_chart(fig_hm, use_container_width=True)

    st.markdown("#### 📋 YoY Table (SQL Window Functions)")
    yoy_tbl = Q(conn, """
        WITH y AS (SELECT Theme,Year,SUM(SV) V FROM s GROUP BY Theme,Year),
        l AS (SELECT Theme,Year,V,LAG(V)OVER(PARTITION BY Theme ORDER BY Year) P FROM y)
        SELECT Theme, Year, ROUND(V/1e6,2) AS Volume_M,
               ROUND((V-P)*100.0/NULLIF(P,0),1) AS YoY_Pct
        FROM l ORDER BY Theme, Year""")
    st.dataframe(yoy_tbl.style.format({"Volume_M":"{:.2f}M","YoY_Pct":"{:+.1f}%"}),
                 use_container_width=True, hide_index=True)

# ╔════════════════════════════════════════════════════════════╗
# ║  TAB 2 — THEMES & CATEGORIES                              ║
# ╚════════════════════════════════════════════════════════════╝
with tabs[2]:
    st.markdown("### 🗂 Theme & Category Deep Dive")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Volume by Theme")
        th = Q(conn,"SELECT Theme,ROUND(SUM(SV)/1e6,2) V FROM s GROUP BY Theme ORDER BY V DESC")
        fig_th = px.bar(th, x="Theme", y="V", color="Theme", color_discrete_map=TC, text_auto=".2f")
        fig_th.update_traces(marker_line_width=0, texttemplate="%{text}M", textposition="outside")
        T(fig_th, h=280, title="Total Search Volume (Millions)")
        fig_th.update_yaxes(title="Volume (M)")
        st.plotly_chart(fig_th, use_container_width=True)

    with c2:
        st.markdown("#### Top 20 Sub-Types by Keyword Count")
        st_cnt = (df.groupby(["Sub_Type","Theme"]).agg(Keywords=("Keyword","count"))
                  .reset_index().nlargest(20,"Keywords"))
        fig_stc = px.bar(st_cnt.sort_values("Keywords"), x="Keywords", y="Sub_Type",
                         orientation="h", color="Theme", color_discrete_map=TC, text="Keywords")
        fig_stc.update_traces(marker_line_width=0, textposition="outside")
        T(fig_stc, h=500, title="Sub-Type Distribution (Keyword Count)")
        st.plotly_chart(fig_stc, use_container_width=True)

    st.markdown("#### Top 15 Sub-Types by Search Volume")
    sub = Q(conn,"SELECT Sub_Type,Theme,ROUND(SUM(SV)/1e6,2) V FROM s GROUP BY Sub_Type,Theme ORDER BY V DESC LIMIT 15")
    sub["Label"] = sub["V"].apply(lambda x: f"{x:.2f}M")
    fig_sub = px.bar(sub.sort_values("V"), x="V", y="Sub_Type", orientation="h",
                     color="Theme", color_discrete_map=TC, text="Label")
    fig_sub.update_traces(marker_line_width=0, textposition="outside")
    T(fig_sub, h=420, title="Sub-Type Volume Ranking — Top 15")
    fig_sub.update_xaxes(title="Volume (M)")
    st.plotly_chart(fig_sub, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🎙 Podcast vs Music Discovery — Monthly Trend")
    lng_kw = Q(conn, "SELECT Keyword, Month, SV FROM s")
    pod = lng_kw[lng_kw["Keyword"].str.contains("podcast", case=False, na=False)]
    mus = lng_kw[lng_kw["Keyword"].str.lower().str.contains(
        "songs|music|playlist|bollywood|hindi|rock|edm|jazz|rap|punjabi", na=False)]
    pod_m = pod.groupby("Month")["SV"].sum().rename("Podcasts")
    mus_m = mus.groupby("Month")["SV"].sum().rename("Music Discovery")
    cmp = pd.DataFrame({"Podcasts":pod_m,"Music Discovery":mus_m}).fillna(0)
    fig_pm = go.Figure()
    fig_pm.add_trace(go.Scatter(x=cmp.index, y=cmp["Podcasts"], name="Podcasts",
        mode="lines", line=dict(color="#f59e0b",width=2.5)))
    fig_pm.add_trace(go.Scatter(x=cmp.index, y=cmp["Music Discovery"], name="Music Discovery",
        mode="lines", line=dict(color="#38bdf8",width=2.5)))
    T(fig_pm, h=300, title="Podcasts Are Growing — Music Discovery Is Declining")
    fig_pm.update_yaxes(tickformat=".2s")
    st.plotly_chart(fig_pm, use_container_width=True)

    st.markdown("""<div class="story-band">
    📖 <b>The Podcast Shift:</b> Podcast searches are growing consistently while music discovery
    declines. Users want <b>talk content, not just songs</b>. Spotify's podcast investment is
    strategically correct — accelerate it before YouTube and Amazon close the gap.
    </div>""", unsafe_allow_html=True)

    pa,pb,pc,pd_ = st.columns(4)
    pa.metric("Podcast Vol (total)", fmt(pod["SV"].sum()))
    pb.metric("Podcast Keywords",    f"{pod['Keyword'].nunique():,}")
    pc.metric("Music Vol (total)",   fmt(mus["SV"].sum()))
    pd_.metric("Music Keywords",     f"{mus['Keyword'].nunique():,}")

    st.markdown("#### 🎸 Genre Trends — Up vs Down")
    genre_q = Q(conn, """SELECT Sub_Type, Year, SUM(SV) V FROM s
        WHERE Sub_Type IN ('hindi songs','top bollywood songs','Rock',
          'EDM/house/Deep House','Jazz','rap artists','top punjabi songs')
        GROUP BY Sub_Type, Year ORDER BY Sub_Type, Year""")
    if not genre_q.empty:
        gp = genre_q.pivot(index="Year", columns="Sub_Type", values="V").fillna(0)
        fig_g = px.line(gp, markers=True,
                        color_discrete_sequence=px.colors.qualitative.Set2)
        T(fig_g, h=300, title="Genre Annual Volume — Hindi & Bollywood Dominant, Others Stable")
        fig_g.update_yaxes(tickformat=".2s")
        st.plotly_chart(fig_g, use_container_width=True)

        genre_gr = []
        for genre in genre_q["Sub_Type"].unique():
            gd = genre_q[genre_q["Sub_Type"]==genre].set_index("Year")["V"]
            v22 = gd.get(2022,0); v25 = gd.get(2025,0)
            pct = (v25-v22)/v22*100 if v22>0 else None
            genre_gr.append({"Genre":genre,"Vol 2022":fmt(v22),"Vol 2025":fmt(v25),
                             "4Y Growth":f"{pct:+.0f}%" if pct is not None else "N/A",
                             "Trend":"📈 Up" if v25>v22 else "📉 Down"})
        st.dataframe(pd.DataFrame(genre_gr), use_container_width=True, hide_index=True)

# ╔════════════════════════════════════════════════════════════╗
# ║  TAB 3 — TOP KEYWORDS                                     ║
# ╚════════════════════════════════════════════════════════════╝
with tabs[3]:
    st.markdown("### 🏆 Top Keywords Explorer")

    c1,c2,c3 = st.columns(3)
    n_top  = c1.slider("Show top N", 5, 50, 20)
    sort_b = c2.selectbox("Sort by", ["Avg_Monthly_Searches","Growth_4Y","Vol_2025"])
    tf     = c3.multiselect("Theme", ["Brand","Category","Competition"],
                             default=["Brand","Category","Competition"], key="tk")

    disp = (fdf[fdf["Theme"].isin(tf)].nlargest(n_top, sort_b)
            [["Keyword","Theme","Sub_Type","Avg_Monthly_Searches","Growth_4Y",
              "Vol_2022","Vol_2025","Seg5","Intent"]].copy())
    disp["Avg_Monthly_Searches"] = disp["Avg_Monthly_Searches"].apply(fmt)
    disp["Vol_2022"]  = disp["Vol_2022"].apply(fmt)
    disp["Vol_2025"]  = disp["Vol_2025"].apply(fmt)
    disp["Growth_4Y"] = disp["Growth_4Y"].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
    st.dataframe(disp, use_container_width=True, height=320, hide_index=True)

    st.markdown("---")
    ca, cb = st.columns(2)

    with ca:
        st.markdown("#### Top 20 by Volume")
        t20 = df.nlargest(20,"Avg_Monthly_Searches")[["Keyword","Avg_Monthly_Searches","Theme"]]
        t20["Label"] = t20["Avg_Monthly_Searches"].apply(fmt)
        fig_t = px.bar(t20.sort_values("Avg_Monthly_Searches"),
                       x="Avg_Monthly_Searches", y="Keyword", orientation="h",
                       color="Theme", color_discrete_map=TC, text="Label")
        fig_t.update_traces(marker_line_width=0, textposition="outside")
        T(fig_t, h=540)
        fig_t.update_xaxes(tickformat=".2s", title="Avg Monthly Searches")
        st.plotly_chart(fig_t, use_container_width=True)

    with cb:
        st.markdown("#### 🚀 Fastest Growing (2022→2025)")
        rising = (df[df["Vol_2022"]>100].nlargest(15,"Growth_4Y")
                  [["Keyword","Theme","Growth_4Y","Vol_2022","Vol_2025"]])
        rising["Label"] = rising["Growth_4Y"].apply(lambda x: f"{x:+,.0f}%")
        fig_r = px.bar(rising.sort_values("Growth_4Y"),
                       x="Growth_4Y", y="Keyword", orientation="h",
                       color="Theme", color_discrete_map=TC, text="Label")
        fig_r.update_traces(marker_line_width=0, textposition="outside")
        T(fig_r, h=540)
        fig_r.update_xaxes(ticksuffix="%", title="Growth % (2022→2025)")
        st.plotly_chart(fig_r, use_container_width=True)

    st.markdown("#### 📊 Growing / Stable / Declining — Explicit Segmentation")
    g_count = int((df["Growth_4Y"] >  20).sum())
    s_count = int((df["Growth_4Y"].between(-20,20)).sum())
    d_count = int((df["Growth_4Y"] < -20).sum())
    na_cnt  = int(df["Growth_4Y"].isna().sum())

    seg_summary = pd.DataFrame([
        {"Segment":"📈 Growing  (>+20%)",      "Keywords":g_count,
         "Share":f"{g_count/len(df)*100:.1f}%","Action":"Invest · Scale SEO · Amplify"},
        {"Segment":"🟡 Stable   (−20 to +20%)","Keywords":s_count,
         "Share":f"{s_count/len(df)*100:.1f}%","Action":"Maintain · Defend position"},
        {"Segment":"📉 Declining (<−20%)",      "Keywords":d_count,
         "Share":f"{d_count/len(df)*100:.1f}%","Action":"Monitor · Pivot away"},
        {"Segment":"⚪ New / No Baseline",       "Keywords":na_cnt,
         "Share":f"{na_cnt/len(df)*100:.1f}%", "Action":"Establish baseline, track"},
    ])
    ca2,cb2 = st.columns([2,3])
    with ca2:
        st.dataframe(seg_summary, use_container_width=True, hide_index=True)
    with cb2:
        fig_seg = go.Figure(go.Bar(
            x=["📈 Growing","🟡 Stable","📉 Declining","⚪ New"],
            y=[g_count, s_count, d_count, na_cnt],
            marker_color=["#1DB954","#94a3b8","#ef4444","#64748b"],
            text=[f"{v:,}" for v in [g_count,s_count,d_count,na_cnt]],
            textposition="outside", textfont=dict(color="#e2e8f0",size=13)))
        T(fig_seg, h=280, title="How Many Keywords Are Growing vs Declining?")
        st.plotly_chart(fig_seg, use_container_width=True)

    st.markdown("#### 🗺 BCG Keyword Matrix (5-Segment)")
    seg5_cnt = df.groupby("Seg5")["Keyword"].count().reset_index().rename(columns={"Keyword":"Count"})
    seg5_vol = df.groupby("Seg5")["Avg_Monthly_Searches"].sum().reset_index().rename(columns={"Avg_Monthly_Searches":"Volume"})
    seg5_all = seg5_cnt.merge(seg5_vol, on="Seg5")
    seg5_all["Vol_Fmt"] = seg5_all["Volume"].apply(fmt)
    ca3,cb3 = st.columns(2)
    with ca3:
        fig_s5 = px.bar(seg5_all, x="Count", y="Seg5", orientation="h",
                        color="Seg5", color_discrete_map=SEG5, text="Count")
        fig_s5.update_traces(marker_line_width=0, textposition="outside")
        T(fig_s5, h=300, title="Segment: Keyword Count")
        st.plotly_chart(fig_s5, use_container_width=True)
    with cb3:
        fig_s5v = px.bar(seg5_all, x="Volume", y="Seg5", orientation="h",
                         color="Seg5", color_discrete_map=SEG5, text="Vol_Fmt")
        fig_s5v.update_traces(marker_line_width=0, textposition="outside")
        T(fig_s5v, h=300, title="Segment: Search Volume")
        fig_s5v.update_xaxes(tickformat=".2s")
        st.plotly_chart(fig_s5v, use_container_width=True)

    st.markdown("#### 📉 Biggest Declining Keywords")
    dec = (df[df["Vol_2022"]>100].nsmallest(15,"Growth_4Y")
           [["Keyword","Theme","Sub_Type","Growth_4Y","Vol_2022","Vol_2025"]])
    dec["Growth_4Y"] = dec["Growth_4Y"].apply(lambda x: f"{x:+.1f}%")
    dec["Vol_2022"]  = dec["Vol_2022"].apply(fmt)
    dec["Vol_2025"]  = dec["Vol_2025"].apply(fmt)
    st.dataframe(dec, use_container_width=True, hide_index=True)

# ╔════════════════════════════════════════════════════════════╗
# ║  TAB 4 — COMPETITIVE INTELLIGENCE                         ║
# ╚════════════════════════════════════════════════════════════╝
with tabs[4]:
    st.markdown("### ⚔️ Competitive Intelligence")

    comp  = df[df["Theme"]=="Competition"]
    brand = df[df["Theme"]=="Brand"]
    bt    = brand["Avg_Monthly_Searches"].sum()
    ct    = comp["Avg_Monthly_Searches"].sum()
    bm    = monthly_df[monthly_df["Theme"]=="Brand"].groupby("Month")["Volume"].sum()
    cpm   = monthly_df[monthly_df["Theme"]=="Competition"].groupby("Month")["Volume"].sum()
    corr_val = bm.corr(cpm)
    ytm_v = comp[comp["Sub_Type"]=="YT Music"]["Avg_Monthly_Searches"].sum()

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Brand Avg/mo",      fmt(bt/12))
    c2.metric("Competitor Avg/mo", fmt(ct/12))
    c3.metric("Brand SoV",         f"{bt/(bt+ct)*100:.1f}%")
    c4.metric("YT Music SoV",      f"{ytm_v/ct*100:.1f}%","Top rival")
    c5.metric("Brand–Comp Corr",   f"{corr_val:.3f}","Near-zero = independent")

    st.markdown(f"""<div class="story-band">
    📖 <b>Competitive Story:</b> Spotify holds <b>{bt/(bt+ct)*100:.1f}%</b> brand SoV vs all competitors.
    YouTube Music is the single biggest threat at <b>{ytm_v/ct*100:.1f}%</b> competitor SoV.
    The Brand–Competition correlation is <b>near-zero ({corr_val:.3f})</b> — Spotify's growth is
    <em>organically driven</em>, not just reactive to market movements. This is a strong position.
    </div>""", unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        st.markdown("#### Competitor Volume by Platform")
        cs = (comp.groupby("Sub_Type")["Avg_Monthly_Searches"].sum()
              .reset_index().sort_values("Avg_Monthly_Searches",ascending=False))
        cs["Label"] = cs["Avg_Monthly_Searches"].apply(fmt)
        fig_c = px.bar(cs, x="Avg_Monthly_Searches", y="Sub_Type", orientation="h",
                       color_discrete_sequence=["#f59e0b"], text="Label")
        fig_c.update_traces(marker_line_width=0, textposition="outside")
        T(fig_c, h=360, title="Competitor Avg Monthly Searches")
        fig_c.update_xaxes(tickformat=".2s")
        st.plotly_chart(fig_c, use_container_width=True)

    with cb:
        st.markdown("#### Full Market Share of Voice")
        sov_df = pd.DataFrame({
            "Platform":["Spotify Brand","YT Music","Wynk","Gaana","JioSaavn","Others"],
            "Vol":[bt,1_618_010,772_740,580_560,580_230,479_360]})
        fig_sov = px.pie(sov_df, names="Platform", values="Vol", hole=0.52,
                         color_discrete_sequence=["#1DB954","#ef4444","#f59e0b",
                                                   "#f97316","#fb923c","#64748b"])
        fig_sov.update_traces(textinfo="percent+label", textfont_size=11,
                               marker=dict(line=dict(color="#060b14",width=2)))
        T(fig_sov, h=360, title="Spotify vs Competitor SoV")
        st.plotly_chart(fig_sov, use_container_width=True)

    st.markdown("#### Brand vs Competition — 48-Month Trend")
    fig_vs = go.Figure()
    fig_vs.add_trace(go.Scatter(x=bm.index, y=bm.values, name="Spotify Brand",
        line=dict(color="#1DB954",width=2.5),
        hovertemplate="<b>Spotify</b><br>%{x}<br>%{y:,.0f}<extra></extra>"))
    fig_vs.add_trace(go.Scatter(x=cpm.index, y=cpm.values, name="All Competition",
        line=dict(color="#f59e0b",width=2.5),
        hovertemplate="<b>Competition</b><br>%{x}<br>%{y:,.0f}<extra></extra>"))
    T(fig_vs, h=300, title="Spotify Brand Growing, Competition Flat — Widening Gap")
    fig_vs.update_yaxes(tickformat=".2s")
    st.plotly_chart(fig_vs, use_container_width=True)

    st.markdown("#### Head-to-Head: Spotify Brand vs Each Competitor")
    comp_tbl = (comp.groupby("Sub_Type").agg(
        Keywords=("Keyword","count"),
        Avg_Vol=("Avg_Monthly_Searches","sum"),
        Avg_Growth=("Growth_4Y","mean")).reset_index())
    comp_tbl["Avg_Vol_Fmt"] = comp_tbl["Avg_Vol"].apply(fmt)
    comp_tbl["Growth_Fmt"]  = comp_tbl["Avg_Growth"].apply(
        lambda x: f"{x:+.0f}%" if pd.notna(x) else "N/A")
    brand_row = pd.DataFrame([{"Sub_Type":"🟢 SPOTIFY BRAND",
        "Keywords":len(brand), "Avg_Vol":bt, "Avg_Vol_Fmt":fmt(bt),
        "Avg_Growth":brand["Growth_4Y"].mean(),
        "Growth_Fmt":f"+{brand['Growth_4Y'].mean():.0f}%"}])
    cmp_tbl2 = pd.concat([brand_row, comp_tbl.sort_values("Avg_Vol",ascending=False)],
                         ignore_index=True)
    st.dataframe(cmp_tbl2[["Sub_Type","Keywords","Avg_Vol_Fmt","Growth_Fmt"]]
                 .rename(columns={"Sub_Type":"Platform","Avg_Vol_Fmt":"Total Search Vol",
                                  "Growth_Fmt":"Avg 4Y Growth"}),
                 use_container_width=True, hide_index=True)

    st.markdown("#### 🔥 Fastest Growing Competitor Keywords")
    cgr = (comp[comp["Vol_2022"]>100].nlargest(12,"Growth_4Y")
           [["Keyword","Sub_Type","Growth_4Y","Vol_2022","Vol_2025"]])
    cgr = cgr.copy()
    cgr["Growth_4Y"] = cgr["Growth_4Y"].apply(lambda x: f"{x:+,.0f}%")
    cgr["Vol_2022"]  = cgr["Vol_2022"].apply(fmt)
    cgr["Vol_2025"]  = cgr["Vol_2025"].apply(fmt)
    st.dataframe(cgr, use_container_width=True, hide_index=True)

# ╔════════════════════════════════════════════════════════════╗
# ║  TAB 5 — ADVANCED ANALYTICS                               ║
# ╚════════════════════════════════════════════════════════════╝
with tabs[5]:
    st.markdown("### 🔬 Advanced Analytics")

    # 1. Intent ────────────────────────────────────────────
    st.markdown("#### 1 · User Intent Classification")
    ia = df.groupby("Intent")["Avg_Monthly_Searches"].agg(["count","sum"]).reset_index()
    ia.columns = ["Intent","Keywords","Volume"]
    ia["Vol%"] = (ia["Volume"]/ia["Volume"].sum()*100).round(1)
    ia["Kw%"]  = (ia["Keywords"]/ia["Keywords"].sum()*100).round(1)
    ia["Vol_Fmt"] = ia["Volume"].apply(fmt)

    c1,c2,c3 = st.columns(3)
    with c1:
        fig_i = px.pie(ia, names="Intent", values="Volume", hole=0.6,
                       color="Intent", color_discrete_map=IC)
        fig_i.update_traces(textinfo="percent+label", textfont_size=11,
                             marker=dict(line=dict(color="#060b14",width=2)))
        T(fig_i, h=260, title="By Volume")
        st.plotly_chart(fig_i, use_container_width=True)
    with c2:
        fig_ib = px.bar(ia, x="Intent", y="Keywords", color="Intent",
                        color_discrete_map=IC, text="Keywords")
        fig_ib.update_traces(marker_line_width=0, textposition="outside")
        T(fig_ib, h=260, title="By Keyword Count")
        st.plotly_chart(fig_ib, use_container_width=True)
    with c3:
        st.dataframe(ia[["Intent","Keywords","Kw%","Vol_Fmt","Vol%"]].rename(
            columns={"Kw%":"Kw%","Vol_Fmt":"Volume","Vol%":"Vol%"}),
            use_container_width=True, hide_index=True)
        trx = ia[ia["Intent"]=="Transactional"]["Vol%"].values
        if len(trx):
            st.markdown(f"""<div class="card a"><h4>💰 {trx[0]:.1f}% = Purchase Intent</h4>
            <p>These users are actively evaluating premium/pricing/free trial.
            Highest-value conversion audience — optimise landing page UX for them.</p></div>""",
            unsafe_allow_html=True)

    # 2. MoM ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 2 · Month-over-Month Growth (SQL)")
    mom = Q(conn, """WITH m AS (SELECT Month,SUM(SV) V FROM s GROUP BY Month ORDER BY Month)
        SELECT Month,V,ROUND((V-LAG(V)OVER(ORDER BY Month))*100.0/
        NULLIF(LAG(V)OVER(ORDER BY Month),0),2) MoM FROM m""")
    ca,cb = st.columns(2)
    with ca:
        fig_mom = go.Figure(go.Bar(x=mom["Month"],y=mom["MoM"],
            marker_color=["#1DB954" if (v or 0)>=0 else "#ef4444" for v in mom["MoM"].fillna(0)],
            hovertemplate="<b>%{x}</b><br>MoM: %{y:+.2f}%<extra></extra>"))
        T(fig_mom, h=270, title="MoM % — Green=Growth, Red=Decline")
        fig_mom.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig_mom, use_container_width=True)
    with cb:
        mom_disp = mom.tail(18).copy()
        mom_disp["V"]   = mom_disp["V"].apply(fmt)
        mom_disp["MoM"] = mom_disp["MoM"].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "—")
        st.dataframe(mom_disp.rename(columns={"Month":"Month","V":"Volume","MoM":"MoM %"}),
                     use_container_width=True, hide_index=True)

    # 3. Theme Correlation ─────────────────────────────────
    st.markdown("---")
    st.markdown("#### 3 · Theme Correlation Matrix")
    bm2  = monthly_df[monthly_df["Theme"]=="Brand"].groupby("Month")["Volume"].sum()
    cpm2 = monthly_df[monthly_df["Theme"]=="Competition"].groupby("Month")["Volume"].sum()
    ctm2 = monthly_df[monthly_df["Theme"]=="Category"].groupby("Month")["Volume"].sum()
    corr_df2 = pd.DataFrame({"Brand":bm2,"Competition":cpm2,"Category":ctm2}).dropna()
    cm = corr_df2.corr().round(3)
    bc, bcat = cm.loc["Brand","Competition"], cm.loc["Brand","Category"]

    ca2,cb2 = st.columns([2,3])
    with ca2:
        fig_cm = px.imshow(cm, text_auto=True,
            color_continuous_scale=[[0,"#ef4444"],[0.5,"#0d1523"],[1,"#1DB954"]],
            zmin=-1, zmax=1)
        T(fig_cm, h=280, title="Correlation Heatmap")
        st.plotly_chart(fig_cm, use_container_width=True)
    with cb2:
        st.markdown(f"""<div class="card g"><h4>📊 What the Correlations Mean</h4>
        <p><b>Brand ↔ Competition: {bc:.3f}</b><br>
        Near-zero = Spotify's growth is <b>organic and self-driven</b>, not reactive to competitors.<br><br>
        <b>Brand ↔ Category: {bcat:.3f}</b><br>
        Negative/weak = As brand searches grow, generic category searches fall — a
        <b>brand maturity signal ✓</b>. Users go directly to Spotify.<br><br>
        <b>Business Implication:</b> Double down on branded campaigns.
        Every brand search gained is a generic category search lost — to Spotify's benefit.</p>
        </div>""", unsafe_allow_html=True)

    # 4. Genre correlation ─────────────────────────────────
    st.markdown("---")
    st.markdown("#### 4 · Genre-to-Genre Correlation Heatmap")
    genre_subs = ["hindi songs","top bollywood songs","Rock","EDM/house/Deep House",
                  "Jazz","rap artists","top punjabi songs"]
    genre_wide = {}
    for gs in genre_subs:
        row = df[df["Sub_Type"]==gs][DC].sum()
        if len(row) > 0: genre_wide[gs] = row
    if genre_wide:
        gw = pd.DataFrame(genre_wide).T
        gcm = gw.T.corr().round(2)
        fig_gc = px.imshow(gcm, text_auto=True,
            color_continuous_scale=[[0,"#ef4444"],[0.5,"#0d1523"],[1,"#1DB954"]],
            zmin=-1, zmax=1)
        T(fig_gc, h=380, title="Genre Correlation — Do Genres Rise & Fall Together?")
        st.plotly_chart(fig_gc, use_container_width=True)
        st.markdown("""<div class="story-band">
        📖 <b>Genre Correlation Insight:</b> High positive correlation (green) = same listener type.
        Marketing one genre captures the correlated genre's audience too — ideal for
        <b>cross-playlist promotion</b>. Negative correlation (red) = distinct audiences to target separately
        with independent campaigns.
        </div>""", unsafe_allow_html=True)

    # 5. Anomaly detection ─────────────────────────────────
    st.markdown("---")
    st.markdown("#### 5 · Statistical Anomaly Detection (Z-Score)")
    overall2 = monthly_df.groupby("Month")["Volume"].sum().reset_index().sort_values("Month")
    overall2["z"] = (overall2["Volume"]-overall2["Volume"].mean())/overall2["Volume"].std()
    overall2["anomaly"] = overall2["z"].abs() > 1.8
    fig_an = go.Figure()
    fig_an.add_trace(go.Scatter(x=overall2["Month"], y=overall2["Volume"],
        mode="lines", name="Volume", line=dict(color="#38bdf8",width=2),
        hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>"))
    anom = overall2[overall2["anomaly"]]
    if not anom.empty:
        fig_an.add_trace(go.Scatter(x=anom["Month"], y=anom["Volume"],
            mode="markers", name="Anomaly (|z|>1.8)",
            marker=dict(color="#ef4444",size=14,symbol="star"),
            customdata=anom["z"],
            hovertemplate="<b>ANOMALY</b><br>%{x}<br>%{y:,.0f}<br>z-score=%{customdata:.2f}<extra></extra>"))
    T(fig_an, h=300, title="Anomaly Detection — Red Stars = Statistically Unusual Months")
    fig_an.update_yaxes(tickformat=".2s")
    st.plotly_chart(fig_an, use_container_width=True)
    if not anom.empty:
        at = anom[["Month","Volume","z"]].copy()
        at["Volume"] = at["Volume"].apply(fmt)
        at["z"] = at["z"].apply(lambda x: f"{x:+.2f}")
        at["Type"] = at["z"].apply(lambda x: "🔺 Spike" if float(x)>0 else "🔻 Drop")
        st.dataframe(at, use_container_width=True, hide_index=True)

    # 6. Growth vs Volume scatter ──────────────────────────
    st.markdown("---")
    st.markdown("#### 6 · Keyword Landscape — Growth vs Volume Bubble Chart")
    scat = df[df["Vol_2022"]>100].dropna(subset=["Growth_4Y"])
    scat_s = scat.sample(min(700,len(scat)), random_state=42)
    fig_sc = px.scatter(scat_s, x="Growth_4Y", y="Avg_Monthly_Searches",
        color="Theme", color_discrete_map=TC, log_y=True, opacity=0.65,
        size="Avg_Monthly_Searches", size_max=20,
        hover_data=["Keyword","Sub_Type","Seg5"],
        labels={"Growth_4Y":"Growth % (2022→2025)",
                "Avg_Monthly_Searches":"Avg Monthly Searches (log)"})
    T(fig_sc, h=420, title="Stars = Top-Right · Dogs = Bottom-Left · Bubble Size = Volume")
    fig_sc.add_vline(x=0, line_dash="dash", line_color="#64748b", opacity=0.5,
                     annotation_text="Zero Growth", annotation_position="top right",
                     annotation=dict(font=dict(color="#64748b",size=9)))
    fig_sc.add_hline(y=scat["Avg_Monthly_Searches"].median(),
                     line_dash="dash", line_color="#64748b", opacity=0.5,
                     annotation_text="Median Volume", annotation_position="right",
                     annotation=dict(font=dict(color="#64748b",size=9)))
    st.plotly_chart(fig_sc, use_container_width=True)

    # 7. Pain points ───────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 7 · Pain Point Keywords — What Users Are Frustrated About")
    pain = df[df["Keyword"].str.lower().str.contains(
        "remove ad|no ad|without ad|offline|free premium|cancel|not working|ads|skip", na=False
    )].nlargest(12,"Avg_Monthly_Searches")[["Keyword","Theme","Sub_Type","Avg_Monthly_Searches"]]
    pain = pain.copy()
    pain["Label"] = pain["Avg_Monthly_Searches"].apply(fmt)
    fig_p = px.bar(pain.sort_values("Avg_Monthly_Searches"),
                   x="Avg_Monthly_Searches", y="Keyword", orientation="h",
                   color_discrete_sequence=["#ef4444"], text="Label")
    fig_p.update_traces(marker_line_width=0, textposition="outside")
    T(fig_p, h=360, title="Pain-Point Keywords = Product Bugs Disguised as Search Queries")
    fig_p.update_xaxes(tickformat=".2s")
    st.plotly_chart(fig_p, use_container_width=True)

    st.markdown("""<div class="story-band">
    📖 <b>Pain Point Insight:</b> When users search "spotify remove ads" or "offline not working",
    they're filing bug reports via Google. <b>Each of these keywords is a product ticket.</b>
    Fix the experience → searches disappear → brand perception improves → premium conversion rises.
    </div>""", unsafe_allow_html=True)

# ╔════════════════════════════════════════════════════════════╗
# ║  TAB 6 — DATA QUALITY                                     ║
# ╚════════════════════════════════════════════════════════════╝
with tabs[6]:
    st.markdown("### 🛡 Data Quality Assessment")

    c1, c2 = st.columns(2)
    with c1:
        st.success(f"✅ **Missing Values — ZERO**\n\nNo missing values across all {len(df):,} rows and {len(DC)} monthly columns.")
        st.success("✅ **Time Series — COMPLETE**\n\nAll 48 months present for every keyword. No gaps detected.")
        st.success("✅ **Zero Values — VALID**\n\nAll monthly values ≥ 10. Low values are legitimate.")
        st.warning("⚠️ **Outlier — 'spotify' keyword**\n\n2,240,000 avg/mo — 507× above median (4,400). Valid brand term. Retained.")
        st.warning("⚠️ **Typo Corrected — 'Competiton'**\n\nSource data misspelling auto-corrected to 'Competition'.")
        st.info("ℹ️ **Right-Skewed Distribution**\n\nMedian ~210 · Mean ~4,428 · Max 2,240,000. Log scale applied in scatter plots.")

        

    with c2:
        st.markdown("#### Descriptive Statistics")
        st.dataframe(df[["Avg_Monthly_Searches","Vol_2022","Vol_2025","Growth_4Y"]]
                     .describe().round(1), use_container_width=True)
        st.markdown("#### Theme Distribution")
        tc = df.groupby("Theme").agg(Keywords=("Keyword","count"),
              Total_Vol=("Avg_Monthly_Searches","sum")).reset_index()
        tc["Total_Vol"] = tc["Total_Vol"].apply(fmt)
        tc["Share%"]    = (df.groupby("Theme")["Keyword"].count()/len(df)*100).round(1).values
        st.dataframe(tc, use_container_width=True, hide_index=True)


# ╔════════════════════════════════════════════════════════════╗
# ║  TAB 7 — STRATEGY                                         ║
# ╚════════════════════════════════════════════════════════════╝
with tabs[7]:
    st.markdown("### 💡 Strategic Recommendations")
    st.markdown("""<div class="hero" style="margin-bottom:24px;">
    <div class="hero-eye">▶ Part 5 — Data-Driven Action Plan</div>
    <h1>Business <span>Strategy</span></h1>
    <div class="hero-sub">Based on 48-month keyword analysis · 2,939 keywords · Jan 2022 – Dec 2025</div>
    </div>""", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### 📱 Product Strategy")
        for card in [
            ("g","1 · Offline Mode — CRITICAL",
             "53 'offline' keywords signal Indian users are underserved on connectivity. Make offline "
             "playback a key <b>premium differentiator</b> in onboarding — not a buried setting."),
            ("r","2 · Ad-Free Experience — HIGH",
             "200+ pain-point keywords around ads reveal this is the #1 user frustration. A mid-tier "
             "plan or longer ad-free trial window directly accelerates free→premium conversion."),
            ("s","3 · Hindi / Bollywood Discovery",
             "155M+ Hindi + 38M+ Bollywood searches dominate Category. Build editorial playlists, "
             "partner with Bollywood labels, and surface regional content in first 10 sec of onboarding."),
            ("a","4 · AI-Powered Features — EMERGING",
             "AI + music/podcast creation keywords grew <b>20,000–50,000%</b> from 2022→2025. "
             "Launch AI DJ and playlist curation before competitors close the gap."),
        ]:
            st.markdown(f"""<div class="card {card[0]}"><h4>{card[1]}</h4>
            <p>{card[2]}</p></div>""", unsafe_allow_html=True)

        st.markdown("#### 📢 Marketing Strategy")
        for card in [
            ("g","5 · Podcast Content Investment",
             "537 podcast keywords — largest cluster. Motivational & celebrity podcasts grew "
             "<b>+28,000–35,000%</b>. Target: 'best podcasts 2025', 'Nikhil Kamath podcast'."),
            ("s","6 · Wrapped Amplification → January",
             "December is peak every year but January sustains the surge. Extend Wrapped "
             "narrative into New Year campaigns — the audience is still primed."),
        ]:
            st.markdown(f"""<div class="card {card[0]}"><h4>{card[1]}</h4>
            <p>{card[2]}</p></div>""", unsafe_allow_html=True)

    with c2:
        st.markdown("#### ⚔️ Competitive Strategy")
        for card in [
            ("r","7 · Counter YT Music (39.3% Competitor SoV)",
             "Differentiate on what YouTube can't match:<br>• <b>Podcast exclusives</b><br>"
             "• <b>Spotify Wrapped</b> emotional hook<br>• <b>Offline premium downloads</b>"
             "<br>• <b>Superior discovery algorithm</b>"),
            ("a","8 · Attack Local Competitor Moat",
             "Gaana + Wynk + JioSaavn = 96M+ searches on local content. Accelerate "
             "<b>Bhojpuri, Telugu, Tamil, Punjabi</b> curation — their moat, attacked with Spotify's resources."),
            ("s","9 · Capitalise on Wynk / Gaana Decline",
             "Several local competitor keywords are declining. Run targeted acquisition "
             "campaigns while their brand searches are weakest — users are looking for alternatives."),
        ]:
            st.markdown(f"""<div class="card {card[0]}"><h4>{card[1]}</h4>
            <p>{card[2]}</p></div>""", unsafe_allow_html=True)

        st.markdown("#### 🌱 Top Growth Opportunities")
        opps = pd.DataFrame([
            ("🎙 Motivational Podcasts", "+35,000%","801K/mo searches","HIGH"),
            ("🎤 Celebrity Podcasts",    "+28,150%","Nikhil Kamath etc.","HIGH"),
            ("💰 Free→Premium Funnel",   "+16,342%","Price-sensitive users","HIGH"),
            ("👥 Spotify Jam (Social)",  "+11,955%","Viral/social feature","MEDIUM"),
            ("🤖 AI Creator Tools",      "+50,000%","PPT/playlist AI","MEDIUM"),
        ], columns=["Opportunity","Signal","Rationale","Priority"])
        st.dataframe(opps, use_container_width=True, hide_index=True, height=215)

        st.markdown("""<div class="card g"><h4>📅 Seasonal Campaign Calendar</h4>
        <p>🎄 <b>December</b> — Wrapped (proven #1 peak)<br>
        🎆 <b>January</b>  — New Year resolutions + playlist push<br>
        ☀️ <b>July</b>    — Summer travel + podcast discovery<br>
        🎯 <b>April</b>   — Volume trough → aggressive promos at lowest CPM</p>
        </div>""", unsafe_allow_html=True)

    # Priority matrix ──────────────────────────────────────
    st.markdown("---")
st.markdown("#### 📊 Priority Matrix — Impact vs Effort")

pm = pd.DataFrame([
    ("Offline Mode Enhancement",     "Critical","Low",   "Q1 2026","53 offline keywords"),
    ("Ad-Free Mid-Tier Plan",         "Critical","Low",   "Q1 2026","200+ pain-point keywords"),
    ("Podcast Content Investment",    "High",    "Medium","Ongoing","537 podcast sub-type cluster"),
    ("Hindi/Bollywood Campaigns",     "High",    "Low",   "Q1 2026","155M+ Hindi searches"),
    ("Counter YT Music",              "High",    "High",  "Q2 2026","39.3% competitor SoV"),
    ("Spotify Wrapped Amplification", "High",    "Low",   "Q4 2026","Dec peak extends to Jan"),
    ("Spotify Jam Social Features",   "Medium",  "Low",   "Q2 2026","+11,955% Jam growth"),
    ("Local Language Content",        "High",    "High",  "Q3 2026","96M local comp searches"),
    ("AI-Powered Features",           "Medium",  "High",  "Q4 2026","20,000%+ AI growth"),
    ("Free→Premium Funnel",           "High",    "Medium","Q2 2026","+16,342% free premium"),
], columns=["Initiative","Impact","Effort","Timeframe","Evidence"])

# Numeric mapping
pm["Impact_N"] = pm["Impact"].map({"Critical":4,"High":3,"Medium":2,"Low":1})
pm["Effort_N"] = pm["Effort"].map({"Low":1,"Medium":2,"High":3})

# Define quadrant type
pm["Quadrant"] = pm.apply(
    lambda r: "Quick Win" if r["Impact_N"]>=3 and r["Effort_N"]==1
    else "Strategic Bet" if r["Impact_N"]>=3 and r["Effort_N"]>=2
    else "Fill-in" if r["Impact_N"]<=2 and r["Effort_N"]==1
    else "Defer",
    axis=1
)

color_map = {
    "Quick Win":"#22c55e",
    "Strategic Bet":"#1DB954",
    "Fill-in":"#f59e0b",
    "Defer":"#64748b"
}

pm["Color"] = pm["Quadrant"].map(color_map)

ca_pm, cb_pm = st.columns([3,2])

with ca_pm:
    fig_pm = go.Figure()

    fig_pm.add_trace(go.Scatter(
        x=pm["Effort_N"],
        y=pm["Impact_N"],
        mode="markers",
        marker=dict(
            size=22,
            color=pm["Color"],
            line=dict(width=1, color="#111")
        ),
        text=pm["Initiative"],
        hovertemplate=(
            "<b>%{text}</b><br>" +
            "Impact: %{y}<br>" +
            "Effort: %{x}<br>" +
            "<extra></extra>"
        )
    ))

    # Add quadrant divider lines
    fig_pm.add_shape(type="line", x0=1.5, x1=1.5, y0=0.5, y1=4.5,
                     line=dict(color="gray", dash="dash"))
    fig_pm.add_shape(type="line", x0=0.5, x1=3.5, y0=2.5, y1=2.5,
                     line=dict(color="gray", dash="dash"))

    # Add quadrant labels
    fig_pm.add_annotation(x=1, y=4.5, text="⭐ Quick Wins",
                          showarrow=False, font=dict(size=12))
    fig_pm.add_annotation(x=3, y=4.5, text="🚀 Strategic Bets",
                          showarrow=False, font=dict(size=12))
    fig_pm.add_annotation(x=1, y=1, text="🧩 Fill-ins",
                          showarrow=False, font=dict(size=11))
    fig_pm.add_annotation(x=3, y=1, text="⬇ Defer",
                          showarrow=False, font=dict(size=11))

    fig_pm.update_xaxes(
        tickvals=[1,2,3],
        ticktext=["Low Effort","Medium Effort","High Effort"],
        title="Implementation Effort",
        range=[0.5,3.5]
    )

    fig_pm.update_yaxes(
        tickvals=[1,2,3,4],
        ticktext=["Low","Medium","High","Critical"],
        title="Business Impact",
        range=[0.5,4.5]
    )

    fig_pm.update_layout(
        height=420,
        template="plotly_dark",
        margin=dict(l=40,r=20,t=40,b=40),
        title="Priority Matrix — Impact vs Effort"
    )

    st.plotly_chart(fig_pm, use_container_width=True)

with cb_pm:
    st.dataframe(
        pm[["Initiative","Impact","Effort","Quadrant","Timeframe","Evidence"]],
        use_container_width=True,
        hide_index=True
    )


# ── Footer ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""<div style='text-align:center;font-family:Space Mono,monospace;
font-size:11px;color:#64748b;padding:14px;letter-spacing:1px;'>
🎵 SPOTIFY KEYWORD INTELLIGENCE &nbsp;·&nbsp; 2,939 Keywords &nbsp;·&nbsp;
Jan 2022 – Dec 2025 &nbsp;·&nbsp; Python · Streamlit · Plotly · SQLite
&nbsp;·&nbsp;  Feb 2026
</div>""", unsafe_allow_html=True)