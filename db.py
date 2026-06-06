"""
db.py — Database connection and setup.
Connects to Supabase (Postgres) instead of local SQLite.
"""

import psycopg2
import psycopg2.extras
from psycopg2 import pool

import os
try:
    import streamlit as st
    DB_URL = st.secrets["DATABASE_URL"]
except Exception:
    DB_URL = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres.dbtghqkhjfhctxzqhvhu:dWbd6LL3ln1LawHf@aws-1-us-west-2.pooler.supabase.com:6543/postgres"
    )

# Connection pool so we don't open a new connection every query
_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = psycopg2.pool.SimpleConnectionPool(1, 10, DB_URL)
    return _pool

def get_con():
    return get_pool().getconn()

def release_con(con):
    get_pool().putconn(con)

def init_db():
    con = get_con()
    try:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS auctions (
                id          SERIAL PRIMARY KEY,
                item        TEXT NOT NULL,
                price_pp    INTEGER,
                price_krono INTEGER,
                type        TEXT NOT NULL,
                seller      TEXT,
                server      TEXT DEFAULT 'frostreaver',
                raw_line    TEXT,
                timestamp   TIMESTAMPTZ DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS krono_prices (
                id        SERIAL PRIMARY KEY,
                price_pp  INTEGER NOT NULL,
                seller    TEXT,
                server    TEXT DEFAULT 'frostreaver',
                timestamp TIMESTAMPTZ DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_auctions_item      ON auctions(item);
            CREATE INDEX IF NOT EXISTS idx_auctions_timestamp ON auctions(timestamp);
            CREATE INDEX IF NOT EXISTS idx_krono_timestamp    ON krono_prices(timestamp);
        """)
        con.commit()
        print("✅ Database tables ready.")
    finally:
        release_con(con)


def save_auction(entry: dict):
    con = get_con()
    try:
        cur = con.cursor()

        if entry['item'] == 'Krono' and entry['price_pp']:
            cur.execute(
                "INSERT INTO krono_prices (price_pp, seller) VALUES (%s, %s)",
                (entry['price_pp'], entry['seller'])
            )

        # Convert krono price to pp if possible
        price_pp = entry['price_pp']
        if entry['price_krono'] and price_pp is None:
            krono_val = get_krono_current(con)
            if krono_val:
                price_pp = entry['price_krono'] * krono_val

        cur.execute("""
            INSERT INTO auctions (item, price_pp, price_krono, type, seller, raw_line)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            entry['item'], price_pp, entry['price_krono'],
            entry['type'], entry['seller'], entry['raw']
        ))
        con.commit()
    finally:
        release_con(con)


def get_krono_current(con=None):
    """Rolling average of last 20 krono sales."""
    owned = con is None
    if owned:
        con = get_con()
    try:
        cur = con.cursor()
        cur.execute("""
            SELECT AVG(price_pp) FROM (
                SELECT price_pp FROM krono_prices
                ORDER BY timestamp DESC LIMIT 20
            ) sub
        """)
        row = cur.fetchone()
        return int(row[0]) if row and row[0] else None
    finally:
        if owned:
            release_con(con)


def get_krono_stats():
    con = get_con()
    try:
        cur = con.cursor()
        cur.execute("""
            SELECT
                ROUND(AVG(price_pp)) as avg_all,
                MAX(price_pp) as high,
                MIN(price_pp) as low,
                COUNT(*) as total
            FROM krono_prices
        """)
        row = cur.fetchone()
        cur.execute("""
            SELECT ROUND(AVG(price_pp)) FROM (
                SELECT price_pp FROM krono_prices
                ORDER BY timestamp DESC LIMIT 20
            ) sub
        """)
        recent = cur.fetchone()
        if row:
            return {
                'avg_all_time': row[0],
                'avg_recent_20': recent[0] if recent else None,
                'all_time_high': row[1],
                'all_time_low': row[2],
                'total_sales': row[3]
            }
        return {}
    finally:
        release_con(con)


def get_krono_history(days=30):
    con = get_con()
    try:
        cur = con.cursor()
        cur.execute("""
            SELECT DATE(timestamp) as day,
                   AVG(price_pp) as avg,
                   MIN(price_pp) as low,
                   MAX(price_pp) as high,
                   COUNT(*) as sales
            FROM krono_prices
            WHERE timestamp > NOW() - INTERVAL '%s days'
            GROUP BY DATE(timestamp)
            ORDER BY day
        """, (days,))
        return cur.fetchall()
    finally:
        release_con(con)


def search_items(query, limit=20):
    con = get_con()
    try:
        cur = con.cursor()
        cur.execute("""
            SELECT item,
                   COUNT(*) as sales,
                   ROUND(AVG(price_pp)) as avg_price,
                   MIN(price_pp) as low,
                   MAX(price_pp) as high,
                   MAX(timestamp) as last_seen
            FROM auctions
            WHERE LOWER(item) LIKE LOWER(%s)
              AND type = 'WTS'
              AND price_pp IS NOT NULL
            GROUP BY item
            ORDER BY sales DESC
            LIMIT %s
        """, (f"%{query}%", limit))
        return cur.fetchall()
    finally:
        release_con(con)


def get_item_history(item_name, days=30):
    con = get_con()
    try:
        cur = con.cursor()
        cur.execute("""
            SELECT DATE(timestamp) as day,
                   AVG(price_pp) as avg,
                   MIN(price_pp) as low,
                   MAX(price_pp) as high,
                   COUNT(*) as sales
            FROM auctions
            WHERE LOWER(item) LIKE LOWER(%s)
              AND type = 'WTS'
              AND price_pp IS NOT NULL
              AND timestamp > NOW() - INTERVAL '%s days'
            GROUP BY DATE(timestamp)
            ORDER BY day
        """, (f"%{item_name}%", days))
        return cur.fetchall()
    finally:
        release_con(con)


def get_item_listings(item_name, limit=200):
    con = get_con()
    try:
        cur = con.cursor()
        cur.execute("""
            SELECT seller, price_pp, price_krono, type, timestamp, raw_line
            FROM auctions
            WHERE LOWER(item) LIKE LOWER(%s)
            ORDER BY timestamp DESC
            LIMIT %s
        """, (f"%{item_name}%", limit))
        return cur.fetchall()
    finally:
        release_con(con)


def get_recent_auctions(limit=100):
    con = get_con()
    try:
        cur = con.cursor()
        cur.execute("""
            SELECT item, price_pp, price_krono, type, seller, timestamp
            FROM auctions
            ORDER BY timestamp DESC
            LIMIT %s
        """, (limit,))
        return cur.fetchall()
    finally:
        release_con(con)
