# EQ Auction Tracker 💰

Tracks EC Tunnel auction prices on Frostreaver. Data stored in Supabase, dashboard hosted on Streamlit Cloud.

## How It Works

- **Parser runs on your PC** while you play EQ, reads the log file and sends auction data to Supabase
- **Dashboard is hosted publicly** on Streamlit Cloud — anyone can visit the URL to check prices

---

## Setup — Getting It Online (One Time)

### Step 1 — Put the code on GitHub
1. Go to https://github.com and create a free account if you don't have one
2. Click **New Repository**, name it `eq-tracker`, make it **Public**, click Create
3. Download GitHub Desktop from https://desktop.github.com
4. Open GitHub Desktop, sign in, clone your new repo to your PC
5. Copy all the files from your ECTUNNEL folder into the cloned repo folder
6. In GitHub Desktop click **Commit to main** then **Push origin**

### Step 2 — Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io and sign in with GitHub
2. Click **New app**
3. Pick your `eq-tracker` repo, branch `main`, file `dashboard.py`
4. Click **Advanced settings** and add this secret:
   ```
   DATABASE_URL = "postgresql://postgres.dbtghqkhjfhctxzqhvhu:dWbd6LL3ln1LawHf@aws-1-us-west-2.pooler.supabase.com:6543/postgres"
   ```
5. Click **Deploy** — you'll get a public URL like `https://yourname-eq-tracker.streamlit.app`

### Step 3 — Update db.py to use the secret
On Streamlit Cloud, secrets are read from environment. The db.py is already set up to handle this.

---

## Running the Parser (Every Time You Play)

Double-click `Start EQ Tracker.bat` in your ECTUNNEL folder. It opens:
- **Parser window** — watches Braece's log, sends auctions to Supabase
- **Local dashboard** — http://localhost:8501 (optional, same data as the public site)

Or just run the parser alone:
```
python run.py "C:\Users\Public\Daybreak Game Company\Installed Games\EverQuest\Logs\eqlog_Braece_frostreaver.txt"
```

---

## Files
```
eq_tracker/
├── db.py           — Supabase database connection + all queries
├── parser.py       — Log watcher + auction parser
├── dashboard.py    — Streamlit dashboard
├── run.py          — Starts the parser
├── requirements.txt
└── README.md
```
