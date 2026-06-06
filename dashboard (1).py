
BANNER = """
<svg width="100%" viewBox="0 0 680 160" role="img" xmlns="http://www.w3.org/2000/svg">
<title>Frostreaver EC Tunnel Tracker banner</title>
<defs>
  <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#070c18" stop-opacity="0"/>
    <stop offset="100%" stop-color="#070c18" stop-opacity="0.6"/>
  </linearGradient>
  <linearGradient id="textbg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#040e22" stop-opacity="0.96"/>
    <stop offset="100%" stop-color="#071428" stop-opacity="0.96"/>
  </linearGradient>
</defs>
<style>
  .ban-bg{fill:#070c18}.mtn-dark{fill:#0b1220}.mtn-mid{fill:#0e1a2e}.mtn-light{fill:#12223d}
  .snow{fill:#d0e8ff;opacity:0.9}.star{fill:#6090c0}
  .title{font-family:Georgia,serif;fill:#f0d060;font-size:28px;font-weight:bold;letter-spacing:1px}
  .sub{font-family:Georgia,serif;fill:#80aece;font-size:11px;letter-spacing:3px}
  .gold-border{fill:none;stroke:#c8a84b;stroke-width:1.5}
  .blue-border{fill:none;stroke:#1e3a5a;stroke-width:0.8}
  .icicle{fill:#7ab0d8;opacity:0.85}
</style>
<rect class="ban-bg" width="680" height="160" rx="6"/>
<polygon class="mtn-dark" points="0,160 70,45 140,160"/>
<polygon class="mtn-mid" points="30,160 110,30 190,160"/>
<polygon class="mtn-light" points="90,160 170,50 250,160"/>
<polygon class="mtn-dark" points="150,160 210,65 270,160"/>
<polygon class="mtn-mid" points="410,160 470,65 530,160"/>
<polygon class="mtn-light" points="430,160 510,45 590,160"/>
<polygon class="mtn-dark" points="490,160 570,30 650,160"/>
<polygon class="mtn-mid" points="560,160 640,50 680,160"/>
<polygon class="mtn-dark" points="620,160 680,40 680,160"/>
<polygon class="snow" points="110,32 98,58 122,58"/>
<polygon class="snow" points="70,47 60,68 80,68"/>
<polygon class="snow" points="170,52 160,72 180,72"/>
<polygon class="snow" points="210,67 202,84 218,84"/>
<polygon class="snow" points="510,47 500,68 520,68"/>
<polygon class="snow" points="570,32 558,58 582,58"/>
<polygon class="snow" points="640,52 630,72 650,72"/>
<circle class="star" cx="20" cy="15" r="1"/><circle class="star" cx="55" cy="8" r="1.3"/>
<circle class="star" cx="130" cy="14" r="0.9"/><circle class="star" cx="195" cy="7" r="1.1"/>
<circle class="star" cx="310" cy="11" r="1"/><circle class="star" cx="370" cy="7" r="1.3"/>
<circle class="star" cx="485" cy="10" r="1.1"/><circle class="star" cx="545" cy="6" r="0.8"/>
<circle class="star" cx="655" cy="9" r="1.2"/>
<rect x="0" y="0" width="680" height="160" rx="6" fill="url(#fade)"/>
<rect x="100" y="38" width="480" height="88" rx="4" fill="url(#textbg)" stroke="#1e3a6a" stroke-width="0.8"/>
<rect x="104" y="42" width="472" height="80" rx="3" fill="none" stroke="#c8a84b44" stroke-width="0.6"/>
<polygon class="icicle" points="115,38 112,52 118,52"/><polygon class="icicle" points="127,38 124,46 130,46"/>
<polygon class="icicle" points="139,38 136,56 142,56"/><polygon class="icicle" points="151,38 148,44 154,44"/>
<polygon class="icicle" points="529,38 526,50 532,50"/><polygon class="icicle" points="541,38 538,54 544,54"/>
<polygon class="icicle" points="553,38 550,44 556,44"/><polygon class="icicle" points="565,38 562,52 568,52"/>
<text font-family="Georgia,serif" font-size="28" font-weight="bold" fill="#000d24" x="342" y="88" text-anchor="middle" letter-spacing="1">Frostreaver EC Tunnel Tracker</text>
<text class="title" x="340" y="86" text-anchor="middle">Frostreaver EC Tunnel Tracker</text>
<line x1="160" y1="96" x2="220" y2="96" stroke="#c8a84b55" stroke-width="0.6"/>
<line x1="460" y1="96" x2="520" y2="96" stroke="#c8a84b55" stroke-width="0.6"/>
<text font-family="Georgia,serif" font-size="11" fill="#000d24" x="342" y="110" text-anchor="middle" letter-spacing="3">REAL-TIME AUCTION PRICES · FROSTREAVER SERVER</text>
<text class="sub" x="340" y="108" text-anchor="middle">REAL-TIME AUCTION PRICES · FROSTREAVER SERVER</text>
<rect class="gold-border" x="4" y="4" width="672" height="152" rx="5"/>
<rect class="blue-border" x="9" y="9" width="662" height="142" rx="4"/>
<text font-family="Georgia,serif" font-size="14" fill="#c8a84b" x="18" y="88" opacity="0.6">❄</text>
<text font-family="Georgia,serif" font-size="14" fill="#c8a84b" x="652" y="88" opacity="0.6">❄</text>
</svg>
"""
"""
EQ Auction Tracker — Streamlit Dashboard
Reads from Supabase. Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from db import (
    init_db, get_krono_stats, get_krono_history,
    search_items, get_item_history, get_item_listings, get_recent_auctions
)


st.set_page_config(page_title="Frostreaver Tunnel", page_icon="⚔️", layout="wide")

st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0e0e12; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #16161e;
        border-right: 1px solid #c8a84b33;
    }

    /* Sidebar title */
    [data-testid="stSidebar"] h1 {
        color: #c8a84b !important;
        font-family: serif;
        font-size: 1.4rem;
    }

    /* All text */
    html, body, [class*="css"] { color: #e0d5b0; }

    /* Headers */
    h1, h2, h3 { color: #c8a84b !important; font-family: serif; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #1c1c26;
        border: 1px solid #c8a84b44;
        border-radius: 8px;
        padding: 12px;
    }
    [data-testid="metric-container"] label { color: #a09060 !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #c8a84b !important;
        font-size: 1.6rem !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #c8a84b33;
        border-radius: 6px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background: #1c1c26; border-radius: 6px; }
    .stTabs [data-baseweb="tab"] { color: #a09060; }
    .stTabs [aria-selected="true"] { color: #c8a84b !important; border-bottom: 2px solid #c8a84b; }

    /* Input boxes */
    .stTextInput input {
        background: #1c1c26;
        border: 1px solid #c8a84b55;
        color: #e0d5b0;
        border-radius: 6px;
    }

    /* Buttons */
    .stButton button {
        background: #1c1c26;
        border: 1px solid #c8a84b;
        color: #c8a84b;
        border-radius: 6px;
    }
    .stButton button:hover { background: #c8a84b22; }

    /* Radio buttons */
    .stRadio label { color: #a09060 !important; }

    /* Slider */
    .stSlider [data-baseweb="slider"] div[role="slider"] { background: #c8a84b; }

    /* Divider */
    hr { border-color: #c8a84b33; }

    /* Caption */
    .stCaption { color: #706040 !important; }

    /* Info boxes */
    .stAlert { background: #1c1c26; border-left: 3px solid #c8a84b; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(BANNER, unsafe_allow_html=True)
st.markdown("<div style='margin-bottom:1.5rem'></div>", unsafe_allow_html=True)


# Init tables on first load
try:
    init_db()
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown('<h1 style="color:#c8a84b;font-family:serif;">⚔️ Frostreaver<br>Tunnel</h1>', unsafe_allow_html=True)
page = st.sidebar.radio("Navigate", ["📊 Krono Prices", "🔍 Item Lookup", "📜 Recent Auctions"])
days = st.sidebar.slider("History (days)", 7, 90, 30)
st.sidebar.markdown("---")
st.sidebar.caption("Data updates live as the parser runs.")



def make_html_table(rows, columns):
    css = (
        "<style>"
        ".eq-table{width:100%;border-collapse:collapse;font-family:Georgia,serif;font-size:13px;}"
        ".eq-table th{background:#1a1a2a;color:#c8a84b;padding:8px 12px;text-align:left;border-bottom:1px solid #c8a84b44;}"
        ".eq-table td{padding:7px 12px;border-bottom:1px solid #1e1e2e;color:#d0c8a8;}"
        ".eq-table tr:hover td{background:#1c1c2c;}"
        ".wts{background:#1a3a1a;color:#4caf50;padding:2px 8px;border-radius:4px;font-weight:bold;font-size:12px;}"
        ".wtb{background:#3a1a1a;color:#ef5350;padding:2px 8px;border-radius:4px;font-weight:bold;font-size:12px;}"
        "</style>"
    )
    header = "".join(f"<th>{c}</th>" for c in columns)
    html = css + f'<table class="eq-table"><thead><tr>{header}</tr></thead><tbody>'
    for row in rows:
        cells = ""
        for i, val in enumerate(row):
            if columns[i] == "Type":
                cls = "wts" if str(val) == "WTS" else "wtb"
                cells += f'<td><span class="{cls}">{val}</span></td>'
            else:
                cells += f"<td>{val}</td>"
        html += f"<tr>{cells}</tr>"
    html += "</tbody></table>"
    return html


def item_link(name):
    slug = name.replace(' ', '+')
    url = f'https://everquest.allakhazam.com/search.html?q={slug}'
    return f'<a href="{url}" target="_blank" style="color:#7ab8d8;text-decoration:none;">{name}</a>'

# ════════════════════════════════════════════
# PAGE 1 — KRONO
# ════════════════════════════════════════════

if page == "📊 Krono Prices":
    col1, col2 = st.columns([0.08, 0.92])
    with col1:
        st.image("https://raw.githubusercontent.com/slunas/eq-tracker/main/krono.png", width=40)
    with col2:
        st.markdown("<h1 style='color:#c8a84b;font-family:serif;margin:0;padding-top:4px;'>Krono Price Tracker</h1>", unsafe_allow_html=True)

    try:
        stats = get_krono_stats()
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

    if not stats or not stats.get('total_sales'):
        st.info("No Krono data yet. Run the parser while people auction in EC Tunnel.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current (rolling avg)", f"{int(stats['avg_recent_20']):,}pp" if stats['avg_recent_20'] else "—")
        c2.metric("All-Time Average", f"{int(stats['avg_all_time']):,}pp" if stats['avg_all_time'] else "—")
        c3.metric("All-Time High", f"{int(stats['all_time_high']):,}pp" if stats['all_time_high'] else "—")
        c4.metric("All-Time Low", f"{int(stats['all_time_low']):,}pp" if stats['all_time_low'] else "—")
        st.caption(f"Based on {stats['total_sales']:,} Krono sales recorded")
        st.divider()

        # ── Two column layout: chat left, chart right ──
        col_chat, col_chart = st.columns([0.38, 0.62])

        with col_chat:
            st.markdown("<h3 style='color:#c8a84b;font-family:serif;margin-top:0;'>📜 Live Krono Sales</h3>", unsafe_allow_html=True)
            st.caption('Most recent 30 sales')
            _fcon = get_con()
            _fcur = _fcon.cursor()
            _fcur.execute("""
                SELECT seller, price_pp, type, timestamp
                FROM auctions
                WHERE LOWER(item) = 'krono'
                AND price_pp IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 30
            """)
            feed_rows = _fcur.fetchall()
            release_con(_fcon)

            if feed_rows:
                chat_lines = []
                for seller, price, typ, ts in feed_rows:
                    time_str = pd.to_datetime(ts).strftime('%H:%M')
                    action = 'WTS' if typ == 'WTS' else 'WTB'
                    action_color = '#4caf50' if typ == 'WTS' else '#ef5350'
                    price_str = f"{int(price):,}pp"
                    line = (
                        f"<div style='font-family:monospace;font-size:12px;padding:2px 0;border-bottom:1px solid #1a1a2a;'>"
                        f"<span style='color:#666;'>[{time_str}]</span> "
                        f"<span style='color:#ff9f43;font-weight:bold;'>{seller}</span>"
                        f"<span style='color:#888;'> auctions, '</span>"
                        f"<span style='color:{action_color};font-weight:bold;'>{action}</span>"
                        f" <span style='color:#c8a84b;'>Krono</span>"
                        f" <span style='color:#7ab8d8;font-weight:bold;'>{price_str}</span>"
                        f"<span style='color:#888;'> PST'</span>"
                        f"</div>"
                    )
                    chat_lines.append(line)
                chat_html = (
                    "<div style='background:#080c18;border:1px solid #c8a84b33;border-radius:6px;"
                    "padding:10px;height:420px;overflow-y:auto;'>"
                    + "".join(chat_lines) + "</div>"
                )
                st.markdown(chat_html, unsafe_allow_html=True)
            else:
                st.info("No Krono sales yet.")

        with col_chart:
            rows = get_krono_history(days=days)
            if rows:
                df = pd.DataFrame(rows, columns=['Date', 'Avg', 'Low', 'High', 'Sales'])
                df['Date'] = pd.to_datetime(df['Date'])
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df['Date'], y=df['High'], fill=None, mode='lines', line_color='rgba(255,100,100,0.3)', name='High'))
                fig.add_trace(go.Scatter(x=df['Date'], y=df['Low'], fill='tonexty', mode='lines', line_color='rgba(100,200,100,0.3)', fillcolor='rgba(150,200,150,0.15)', name='Low'))
                fig.add_trace(go.Scatter(x=df['Date'], y=df['Avg'], mode='lines+markers', line=dict(color='gold', width=2), name='Avg'))
                fig.update_layout(title=f"Krono — Last {days} Days", xaxis_title="Date", yaxis_title="pp", hovermode='x unified', template='plotly_dark', margin=dict(t=40))
                st.plotly_chart(fig, use_container_width=True)
                fig2 = px.bar(df, x='Date', y='Sales', title='Daily Sale Count', template='plotly_dark', color_discrete_sequence=['gold'])
                fig2.update_layout(margin=dict(t=40))
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info(f"No Krono data in the last {days} days.")


# ════════════════════════════════════════════
# PAGE 2 — ITEM LOOKUP
# ════════════════════════════════════════════

elif page == "🔍 Item Lookup":
    st.title("🔍 Item Price Lookup")
    query = st.text_input("Search item name", placeholder="e.g. Fungi Tunic, Rubicite, Banded...")

    if query and len(query) >= 2:
        rows = search_items(query)
        if rows:
            df = pd.DataFrame(rows, columns=['Item', 'Sales', 'Avg Price (pp)', 'Low (pp)', 'High (pp)', 'Last Seen'])
            df['Last Seen'] = pd.to_datetime(df['Last Seen']).dt.strftime('%Y-%m-%d %H:%M')
            df['Item'] = df['Item'].apply(item_link)
            df['Avg Price (pp)'] = df['Avg Price (pp)'].apply(lambda x: f"{int(x):,}" if x else "—")
            df['Low (pp)'] = df['Low (pp)'].apply(lambda x: f"{int(x):,}" if x else "—")
            df['High (pp)'] = df['High (pp)'].apply(lambda x: f"{int(x):,}" if x else "—")
            st.markdown(make_html_table(df.values.tolist(), df.columns.tolist()), unsafe_allow_html=True)

            selected = st.selectbox("View details for:", [r[0] for r in rows])
            if selected:
                tab1, tab2 = st.tabs(["📋 All Listings", "📈 Price History"])

                with tab1:
                    listings = get_item_listings(selected)
                    if listings:
                        st.caption('💡 pp for Krono listings = Krono avg at time of sale')
                        trows = []
                        for r in listings:
                            seller, price_pp, price_kr, typ, ts, raw = r
                            time_str = pd.to_datetime(ts).strftime('%Y-%m-%d %H:%M')
                            pp_str = f"{int(price_pp):,}pp" if price_pp is not None else "—"
                            kr_str = f'<img src="https://raw.githubusercontent.com/slunas/eq-tracker/main/krono.png" style="width:18px;height:18px;vertical-align:middle;"> {int(price_kr)}' if price_kr is not None else '—'
                            trows.append([typ, f'<a href="https://everquest.allakhazam.com/search.html?q={selected.replace(" ", "+")}" target="_blank" style="color:#7ab8d8;text-decoration:none;">{selected}</a>', pp_str, kr_str, time_str])
                        st.markdown(make_html_table(trows, ['Type','Seller','Price (pp)','Price (Krono)','Time']), unsafe_allow_html=True)
                        with st.expander("Show raw auction lines"):
                            for raw in set(r[5] for r in listings[:20]):
                                st.caption(raw)
                    else:
                        st.info("No listings found.")

                with tab2:
                    hist = get_item_history(selected, days=days)
                    if hist:
                        hdf = pd.DataFrame(hist, columns=['Date', 'Avg', 'Low', 'High', 'Sales'])
                        hdf['Date'] = pd.to_datetime(hdf['Date'])
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=hdf['Date'], y=hdf['High'], fill=None, mode='lines', line_color='rgba(255,100,100,0.4)', name='High'))
                        fig.add_trace(go.Scatter(x=hdf['Date'], y=hdf['Low'], fill='tonexty', mode='lines', line_color='rgba(100,200,100,0.4)', fillcolor='rgba(150,200,150,0.15)', name='Low'))
                        fig.add_trace(go.Scatter(x=hdf['Date'], y=hdf['Avg'], mode='lines+markers', line=dict(color='#00bfff', width=2), name='Avg'))
                        fig.update_layout(title=f"{selected} — Price History", xaxis_title="Date", yaxis_title="pp", hovermode='x unified', template='plotly_dark')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"No price history in the last {days} days.")
        else:
            st.warning(f"No items found matching '{query}'")
    elif query:
        st.caption("Type at least 2 characters.")


# ════════════════════════════════════════════
# PAGE 3 — RECENT AUCTIONS
# ════════════════════════════════════════════

elif page == "📜 Recent Auctions":
    st.title("📜 Recent Auctions")
    if st.button("🔄 Refresh"):
        st.rerun()

    rows = get_recent_auctions(limit=100)
    if rows:
        df = pd.DataFrame(rows, columns=['Item', 'Price (pp)', 'Price (Krono)', 'Type', 'Seller', 'Time'])
        df['Time'] = pd.to_datetime(df['Time']).dt.strftime('%Y-%m-%d %H:%M')
        df['Price (pp)'] = df['Price (pp)'].apply(lambda x: f"{int(x):,}pp" if pd.notna(x) else "—")
        df['Price (Krono)'] = df['Price (Krono)'].apply(lambda x: f'<img src="https://raw.githubusercontent.com/slunas/eq-tracker/main/krono.png" style="width:18px;height:18px;vertical-align:middle;"> {int(x)}' if pd.notna(x) else '—')
        type_filter = st.radio("Show", ["All", "WTS only", "WTB only"], horizontal=True)
        if type_filter == "WTS only":
            df = df[df['Type'] == 'WTS']
        elif type_filter == "WTB only":
            df = df[df['Type'] == 'WTB']
        df['Item'] = df['Item'].apply(lambda n: item_link(str(n)))
        trows = df[['Type','Item','Price (pp)','Price (Krono)','Seller','Time']].values.tolist()
        st.markdown(make_html_table(trows, ['Type','Item','Price (pp)','Price (Krono)','Seller','Time']), unsafe_allow_html=True)
    else:
        st.info("No auctions yet. Run the parser while playing!")
