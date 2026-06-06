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

st.set_page_config(page_title="EQ Auction Tracker", page_icon="💰", layout="wide")

# Init tables on first load
try:
    init_db()
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("💰 EQ Auction Tracker")
st.sidebar.caption("Frostreaver Server")
page = st.sidebar.radio("Navigate", ["📊 Krono Prices", "🔍 Item Lookup", "📜 Recent Auctions"])
days = st.sidebar.slider("History (days)", 7, 90, 30)
st.sidebar.markdown("---")
st.sidebar.caption("Data updates live as the parser runs.")


# ════════════════════════════════════════════
# PAGE 1 — KRONO
# ════════════════════════════════════════════

if page == "📊 Krono Prices":
    st.title("📊 Krono Price Tracker")

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

        rows = get_krono_history(days=days)
        if rows:
            df = pd.DataFrame(rows, columns=['Date', 'Avg', 'Low', 'High', 'Sales'])
            df['Date'] = pd.to_datetime(df['Date'])
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Date'], y=df['High'], fill=None, mode='lines', line_color='rgba(255,100,100,0.3)', name='High'))
            fig.add_trace(go.Scatter(x=df['Date'], y=df['Low'], fill='tonexty', mode='lines', line_color='rgba(100,200,100,0.3)', fillcolor='rgba(150,200,150,0.15)', name='Low'))
            fig.add_trace(go.Scatter(x=df['Date'], y=df['Avg'], mode='lines+markers', line=dict(color='gold', width=2), name='Avg'))
            fig.update_layout(title=f"Krono — Last {days} Days", xaxis_title="Date", yaxis_title="pp", hovermode='x unified', template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
            fig2 = px.bar(df, x='Date', y='Sales', title='Daily Sale Count', template='plotly_dark', color_discrete_sequence=['gold'])
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
            df['Avg Price (pp)'] = df['Avg Price (pp)'].apply(lambda x: f"{int(x):,}" if x else "—")
            df['Low (pp)'] = df['Low (pp)'].apply(lambda x: f"{int(x):,}" if x else "—")
            df['High (pp)'] = df['High (pp)'].apply(lambda x: f"{int(x):,}" if x else "—")
            st.dataframe(df, use_container_width=True, hide_index=True)

            selected = st.selectbox("View details for:", [r[0] for r in rows])
            if selected:
                tab1, tab2 = st.tabs(["📋 All Listings", "📈 Price History"])

                with tab1:
                    listings = get_item_listings(selected)
                    if listings:
                        ldf = pd.DataFrame(listings, columns=['Seller', 'Price (pp)', 'Price (Krono)', 'Type', 'Time', 'Raw Line'])
                        ldf['Time'] = pd.to_datetime(ldf['Time']).dt.strftime('%Y-%m-%d %H:%M')
                        ldf['Price (pp)'] = ldf['Price (pp)'].apply(lambda x: f"{int(x):,}pp" if pd.notna(x) else "—")
                        ldf['Price (Krono)'] = ldf['Price (Krono)'].apply(lambda x: f"{int(x)} 🪙" if pd.notna(x) else "—")
                        st.dataframe(ldf[['Seller', 'Price (pp)', 'Price (Krono)', 'Type', 'Time']], use_container_width=True, hide_index=True)
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
        df['Price (Krono)'] = df['Price (Krono)'].apply(lambda x: f"{int(x)} 🪙" if pd.notna(x) else "—")
        type_filter = st.radio("Show", ["All", "WTS only", "WTB only"], horizontal=True)
        if type_filter == "WTS only":
            df = df[df['Type'] == 'WTS']
        elif type_filter == "WTB only":
            df = df[df['Type'] == 'WTB']
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No auctions yet. Run the parser while playing!")
