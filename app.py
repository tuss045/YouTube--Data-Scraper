import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import re
from io import BytesIO
from datetime import date, timedelta

st.set_page_config(
    page_title="VidIQ Nova — YouTube Analytics",
    page_icon="🤖",
    layout="wide"
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Page background */
.stApp {
    background: linear-gradient(135deg, #0a081a, #161233, #111124);
    min-height: 100vh;
}

/* Hide default streamlit header */
header[data-testid="stHeader"] { background: transparent; }

/* Hero banner */
.hero {
    background: linear-gradient(120deg, #121026 0%, #171b3a 50%, #0d2347 100%);
    border: 1px solid rgba(229, 57, 53, 0.25);
    border-radius: 20px;
    padding: 2.2rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(229,57,53,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 0.3rem;
    letter-spacing: -0.5px;
}
.hero-title span {
    color: #e53935;
}
.hero-sub {
    font-size: 1rem;
    color: rgba(255,255,255,0.6);
    margin: 0;
}

/* Section headers */
.section-head {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.45);
    margin-bottom: 0.6rem;
    margin-top: 1rem;
}

/* Metric cards */
.metric-row {
    display: flex;
    gap: 14px;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.metric-card {
    flex: 1;
    min-width: 180px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.2rem;
    transition: transform 0.2s, border-color 0.2s;
}
.metric-card:hover {
    border-color: rgba(255,255,255,0.15);
}
.metric-card .m-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.4);
    margin-bottom: 6px;
}
.metric-card .m-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.1;
}
.metric-card .m-sub {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.3);
    margin-top: 6px;
}
.metric-card.red { border-color: rgba(229, 57, 53, 0.3); background: rgba(229, 57, 53, 0.02); }
.metric-card.red .m-value { color: #ff7373; }
.metric-card.blue { border-color: rgba(66, 165, 245, 0.3); background: rgba(66, 165, 245, 0.02); }
.metric-card.blue .m-value { color: #64b5f6; }
.metric-card.green { border-color: rgba(102, 187, 106, 0.3); background: rgba(102, 187, 106, 0.02); }
.metric-card.green .m-value { color: #81c784; }
.metric-card.amber { border-color: rgba(255, 183, 77, 0.3); background: rgba(255, 183, 77, 0.02); }
.metric-card.amber .m-value { color: #ffb74d; }

/* Channel tag chips */
.ch-chip {
    display: inline-block;
    background: rgba(229,57,53,0.12);
    border: 1px solid rgba(229,57,53,0.3);
    color: #ef9a9a;
    font-size: 0.75rem;
    padding: 4px 12px;
    border-radius: 20px;
    margin: 4px 6px 4px 0;
    font-weight: 500;
}

/* Streamlit component stylings */
div[data-testid="stTextInput"] > label,
div[data-testid="stDateInput"] > label,
div[data-testid="stRadio"] > label,
div[data-testid="stTextArea"] > label {
    color: rgba(255,255,255,0.65) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
div[data-testid="stTextInput"] input,
div[data-testid="stDateInput"] input,
div[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #fff !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stDateInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #e53935 !important;
}

/* Primary button styling */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #e53935, #b71c1c) !important;
    border: none !important;
    color: white !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.7rem 2rem !important;
    border-radius: 12px !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s ease !important;
    width: 100%;
    box-shadow: 0 4px 12px rgba(229,57,53,0.2);
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(229,57,53,0.3);
    opacity: 0.95 !important;
}

/* Download button */
div[data-testid="stDownloadButton"] > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 500 !important;
    width: 100% !important;
    transition: background 0.2s;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.25) !important;
}

hr { border-color: rgba(255,255,255,0.06) !important; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">VidIQ <span>Nova</span></div>
  <p class="hero-sub">Multi-channel intelligence · Performance over time trends · Content isolation matrix</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar — API Key ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-head">🔑 API Configuration</div>', unsafe_allow_html=True)
    api_key = st.secrets.get("YOUTUBE_API_KEY", None)
    if not api_key:
        api_key = st.text_input("YouTube API Key", type="password", placeholder="AIzaSy...")
    else:
        st.success("API Key verified via background ecosystem ✓")

    st.markdown("---")
    st.markdown('<div class="section-head">ℹ️ About System</div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='color:rgba(255,255,255,0.45);font-size:0.8rem;line-height:1.6;'>"
        "VidIQ Nova performs structural multi-channel audits directly across production instances. "
        "Filter assets by time arrays, parse platform content segments, and extract reporting ledgers."
        "</p>",
        unsafe_allow_html=True
    )

# ── Input Panel ───────────────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    channel_ids_raw = st.text_area(
        "Target Channel IDs (One per line line array)",
        placeholder="UCxxxxxxxxxxxxxxxxxxxxxx\nUCyyyyyyyyyyyyyyyyyyyyyy",
        height=125
    )

    st.markdown('<div class="section-head">📂 Content Strategy Filter</div>', unsafe_allow_html=True)
    content_type = st.radio(
        "Content type Selection Matrix",
        options=["🎬 Long Videos", "⚡ Short Videos (Shorts)", "📢 Community Posts"],
        horizontal=True,
        label_visibility="collapsed"
    )

with col_right:
    st.markdown('<div class="section-head">📅 Temporal Window</div>', unsafe_allow_html=True)
    today = date.today()
    default_start = today - timedelta(days=90)

    date_start = st.date_input("Start Boundary (From)", value=default_start, max_value=today)
    date_end   = st.date_input("Terminal Boundary (To)", value=today, max_value=today)

st.markdown("---")

# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt(n):
    try:
        n = int(n)
        if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
        if n >= 1_000:     return f"{n/1_000:.1f}K"
        return str(n)
    except:
        return "—"

def duration_to_seconds(duration):
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if not m: return 0
    return (int(m.group(1) or 0) * 3600 +
            int(m.group(2) or 0) * 60  +
            int(m.group(3) or 0))

def in_date_range(pub_str, start, end):
    try:
        pub = pd.to_datetime(pub_str).date()
        return start <= pub <= end
    except:
        return False

def get_channel_info(yt, cid):
    try:
        resp = yt.channels().list(part='snippet,contentDetails,statistics', id=cid).execute()
        if not resp.get('items'): return None
        item = resp['items'][0]
        return {
            'name': item['snippet']['title'],
            'playlist': item['contentDetails']['relatedPlaylists']['uploads'],
            'subscribers': item['statistics'].get('subscriberCount', 0),
            'channel_id': item['id'],
        }
    except:
        return None

def get_all_video_ids(yt, playlist_id):
    ids = []
    try:
        req = yt.playlistItems().list(part='contentDetails', playlistId=playlist_id, maxResults=50)
        while req:
            resp = req.execute()
            for item in resp.get('items', []):
                ids.append(item['contentDetails']['videoId'])
            req = yt.playlistItems().list_next(req, resp)
    except:
        pass
    return ids

def get_video_details(yt, video_ids, filter_type, channel_name, start, end):
    rows = []
    for i in range(0, len(video_ids), 50):
        try:
            resp = yt.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_ids[i:i+50])
            ).execute()
            for v in resp.get('items', []):
                pub = v['snippet']['publishedAt']
                if not in_date_range(pub, start, end): continue
                
                raw_dur = v['contentDetails']['duration']
                secs = duration_to_seconds(raw_dur)
                if filter_type == 'short' and secs > 60: continue
                if filter_type == 'long'  and secs <= 60: continue
                
                vid_id = v['id']
                link = f"https://www.youtube.com/shorts/{vid_id}" if filter_type == 'short' else f"https://www.youtube.com/watch?v={vid_id}"
                
                rows.append({
                    'Date': pd.to_datetime(pub).date(),
                    'Channel Name': channel_name,
                    'Title': v['snippet']['title'],
                    'Link': link,
                    'Views': int(v['statistics'].get('viewCount', 0)),
                    'Likes': int(v['statistics'].get('likeCount', 0)),
                    'Comments': int(v['statistics'].get('commentCount', 0)),
                })
        except:
            pass
    return rows

def get_community_posts(yt, channel_id, channel_name, start, end):
    posts = []
    try:
        req = yt.activities().list(part='snippet,contentDetails', channelId=channel_id, maxResults=50)
        while req:
            resp = req.execute()
            for item in resp.get('items', []):
                if item['snippet']['type'] != 'bulletin': continue
                pub = item['snippet']['publishedAt']
                if not in_date_range(pub, start, end): continue
                desc = item['snippet'].get('description', '')
                posts.append({
                    'Date': pd.to_datetime(pub).date(),
                    'Channel Name': channel_name,
                    'Title': desc[:120] + ('…' if len(desc) > 120 else ''),
                    'Link': f"https://www.youtube.com/channel/{channel_id}/community",
                    'Views': 0,
                    'Likes': 0,
                    'Comments': 0,
                })
            npt = resp.get('nextPageToken')
            req = yt.activities().list(part='snippet,contentDetails', channelId=channel_id, maxResults=50, pageToken=npt) if npt else None
    except Exception as e:
        st.warning(f"Ecosystem logging anomaly parsing community nodes: {e}")
    return posts

def convert_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Ecosystem Analytics')
    return output.getvalue()

# ── Processing Execution ──────────────────────────────────────────────────────
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    fetch = st.button("⚡ Fetch Analytics Engines", type="primary")

if fetch:
    channel_ids = [c.strip() for c in channel_ids_raw.strip().splitlines() if c.strip()]

    if not api_key:
        st.error("🔑 API Key configuration invalid. Please update parameter paths.")
    elif not channel_ids:
        st.error("📺 Destination channel identifier array required.")
    elif date_start > date_end:
        st.error("📅 Operational validation failure: Terminal boundary exceeds start index.")
    else:
        yt = build("youtube", "v3", developerKey=api_key)
        all_rows = []
        channel_names = []

        progress = st.progress(0, text="Initializing processing sequences...")

        for idx, cid in enumerate(channel_ids):
            progress.progress((idx) / len(channel_ids), text=f"Querying channel array element {idx+1} of {len(channel_ids)}...")
            info = get_channel_info(yt, cid)
            if not info:
                st.warning(f"Target vector dropped: `{cid}` — context unresolvable.")
                continue

            channel_names.append(info['name'])
            filter_key = 'short' if content_type == "⚡ Short Videos (Shorts)" else 'long' if content_type == "🎬 Long Videos" else 'community'

            if filter_key == 'community':
                rows = get_community_posts(yt, info['channel_id'], info['name'], date_start, date_end)
            else:
                vids = get_all_video_ids(yt, info['playlist'])
                rows = get_video_details(yt, vids, filter_key, info['name'], date_start, date_end)

            all_rows.extend(rows)

        progress.progress(1.0, text="Complete.")
        progress.empty()

        if not all_rows:
            st.info("Execution complete: No elements map to specified context options.")
        else:
            df = pd.DataFrame(all_rows)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date', ascending=False).reset_index(drop=True)

            # ── Summary Metrics ────────────────────────────────────────────
            total_videos = len(df)
            total_views = df['Views'].sum()
            total_likes = df['Likes'].sum()
            total_comments = df['Comments'].sum()

            st.markdown(f"""
            <div style="margin:1rem 0 0.5rem;">
              <div class="section-head">📊 Global Ledger Aggregation Window</div>
              <div style="margin-bottom:12px;">
                {''.join(f'<span class="ch-chip">🌍 {n}</span>' for n in channel_names)}
              </div>
              <div class="metric-row">
                <div class="metric-card amber">
                  <div class="m-label">Assets Discovered</div>
                  <div class="m-value">{total_videos:,}</div>
                  <div class="m-sub">Active nodes parsed</div>
                </div>
                <div class="metric-card blue">
                  <div class="m-label">Gross Impression Views</div>
                  <div class="m-value">{fmt(total_views)}</div>
                  <div class="m-sub">Cumulative footprint</div>
                </div>
                <div class="metric-card red">
                  <div class="m-label">Gross Interaction Likes</div>
                  <div class="m-value">{fmt(total_likes)}</div>
                  <div class="m-sub">Positive user signals</div>
                </div>
                <div class="metric-card green">
                  <div class="m-label">Discussion Threads</div>
                  <div class="m-value">{fmt(total_comments)}</div>
                  <div class="m-sub">Community engagement</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Side-By-Side Advanced Channel Performance Matrix ─────────────
            if len(channel_names) > 1 and filter_key != 'community':
                st.markdown('<div class="section-head">📈 Channel Cross-Comparison Intelligence</div>', unsafe_allow_html=True)
                comparison_df = df.groupby('Channel Name').agg({
                    'Title': 'count',
                    'Views': 'sum',
                    'Likes': 'sum'
                }).rename(columns={'Title': 'Content Count', 'Views': 'Total Views', 'Likes': 'Total Likes'})
                st.dataframe(comparison_df, use_container_width=True)

            # ── Visual Time Series Trends ──────────────────────────────────
            if filter_key != 'community':
                st.markdown('<div class="section-head">📈 Chronological Impression Volume Trend</div>', unsafe_allow_html=True)
                trend_df = df.groupby('Date')[['Views']].sum()
                st.area_chart(trend_df, color="#e53935")

            # ── Interactive Unified Data Table ──────────────────────────────
            st.markdown('<div class="section-head">📋 Granular Content Matrix Ledgers</div>', unsafe_allow_html=True)
            
            # Format display dates back cleanly for presentation
            presentation_df = df.copy()
            presentation_df['Date'] = presentation_df['Date'].dt.date

            st.dataframe(
                presentation_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Link": st.column_config.LinkColumn("Source Link", display_text="▶ Inspect Node"),
                    "Views": st.column_config.NumberColumn("Views Metrics", format="%d"),
                    "Likes": st.column_config.NumberColumn("Likes Metrics", format="%d"),
                    "Comments": st.column_config.NumberColumn("Comments Matrix", format="%d"),
                    "Date": st.column_config.DateColumn("Publish Date"),
                }
            )

            # ── Structured Production Exports ────────────────────────────────
            st.markdown('<div class="section-head">📥 Export Pipeline Registry</div>', unsafe_allow_html=True)
            suffix_str = "shorts" if filter_key == 'short' else "longform" if filter_key == 'long' else "community"
            fname = f"NovaReport_{date_start}_to_{date_end}_{suffix_str}"

            dl1, dl2 = st.columns(2)
            with dl1:
                st.download_button(
                    "💾 Stream Production Excel Engine Ledger",
                    data=convert_to_excel(presentation_df),
                    file_name=f"{fname}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            with dl2:
                st.download_button(
                    "📄 Stream Standard Flattened Flatfile Data (.CSV)",
                    data=presentation_df.to_csv(index=False),
                    file_name=f"{fname}.csv",
                    mime="text/csv"
                )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:4rem;padding:1.5rem 0;border-top:1px solid rgba(255,255,255,0.05);">
  <span style="font-size:0.75rem;color:rgba(255,255,255,0.25);letter-spacing:0.1em;text-transform:uppercase;">
    Enterprise Sandbox Environment · Platform Intelligence Pipeline Version 2.4 Stable
  </span>
</div>
""", unsafe_allow_html=True)
