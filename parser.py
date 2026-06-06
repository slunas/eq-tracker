"""
parser.py — Log watcher + auction parser.
Reads EQ log file and sends auctions to Supabase.
"""

import re
import time
from pathlib import Path

KRONO_ALIASES = ['krono', 'kronos', 'kron', 'kr']
NOISE_WORDS = {'pst', 'obo', 'or', 'and', 'wts', 'wtb', 'wtt', 'free', 'cheap', 'rare',
               'pm', 'msg', 'ea', 'each', 'per', 'stack', 'tell', 'me', 'offers', 'ls',
               'selling', 'buying', 'paying'}


def normalize_msg(text):
    def k_replace(m):
        return str(int(float(m.group(1)) * 1000)) + 'pp'
    text = re.sub(r'(\d+(?:\.\d+)?)\s*[kK]\s*pp', k_replace, text)
    def k_replace2(m):
        return str(int(float(m.group(1)) * 1000)) + 'pp '
    text = re.sub(r'(\d+(?:\.\d+)?)[kK](?=\s|$|[^a-zA-Z])', k_replace2, text)
    text = re.sub(r'(\d+)\s*p(?!p|st|er|s|l|a|y|o|i|u|e)', r'\1pp', text, flags=re.IGNORECASE)
    text = text.replace('/', ' ').replace('--', ' ')
    return text


def clean_item_name(name):
    name = name.strip(" -,:/'\"")
    words = name.split()
    while words and words[-1].lower() in NOISE_WORDS:
        words.pop()
    while words and words[0].lower() in NOISE_WORDS:
        words.pop(0)
    return " ".join(words).title()


def is_krono(word):
    return word.lower().rstrip('s') in [a.rstrip('s') for a in KRONO_ALIASES]


def parse_auction_line(line):
    results = []

    seller_match = re.search(r'\] (\w+) auction', line, re.IGNORECASE)
    seller = seller_match.group(1) if seller_match else None

    quote_match = re.search(r"'(.+?)'", line)
    msg = quote_match.group(1) if quote_match else line
    msg = normalize_msg(msg)

    segments = re.split(r'\b(WTS|WTB|WTT)\b', msg, flags=re.IGNORECASE)
    current_type = None

    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        if seg.upper() in ('WTS', 'WTB', 'WTT'):
            current_type = 'WTS' if seg.upper() in ('WTS', 'WTT') else 'WTB'
            continue
        if current_type is None:
            continue

        # Pass 1: Krono sold for pp
        # Handles: "Krono 8000pp", "2 Krono 16000pp" (divides by qty), "8000pp Krono"
        krono_alias_pattern = '|'.join(re.escape(a) for a in KRONO_ALIASES)
        m = re.search(
            rf'(?:(\d+)\s*pp\s+(?:{krono_alias_pattern})'
            rf'|(\d+)\s+(?:{krono_alias_pattern})\s+(\d[\d,]*)\s*pp'
            rf'|(?:{krono_alias_pattern})\s+(\d[\d,]*)\s*pp)',
            seg, re.IGNORECASE
        )
        if m:
            if m.group(2) and m.group(3):
                qty = int(m.group(2))
                total = int(m.group(3).replace(',', ''))
                price = total // qty
            else:
                price = int((m.group(1) or m.group(4)).replace(',', ''))
            results.append({'type': current_type, 'item': 'Krono', 'price_pp': price,
                           'price_krono': None, 'seller': seller, 'raw': msg})
            seg = seg[:m.start()] + ' ' + seg[m.end():]

        # Pass 2: items with pp prices
        item_pp = re.compile(
            r'([A-Za-z][A-Za-z\s\'\-\+\:]{1,60}?)(?:\s*x\s*\d+\s+|\s+)(\d[\d,]{0,8})\s*pp',
            re.IGNORECASE
        )
        for m in item_pp.finditer(seg):
            name = clean_item_name(m.group(1))
            price = int(m.group(2).replace(',', ''))
            if not name or len(name) < 2 or name.upper() in NOISE_WORDS or is_krono(name):
                continue
            results.append({'type': current_type, 'item': name, 'price_pp': price,
                           'price_krono': None, 'seller': seller, 'raw': msg})

        # Pass 3: items priced in Krono
        for alias in KRONO_ALIASES:
            kron_pat = re.compile(
                rf'([A-Za-z][A-Za-z\s\'\-\+\:]{{1,60}}?)\s+(\d+)\s+{re.escape(alias)}(?:s|no)?\b',
                re.IGNORECASE
            )
            for m in kron_pat.finditer(seg):
                name = clean_item_name(m.group(1))
                kron_count = int(m.group(2))
                if not name or len(name) < 2 or name.upper() in NOISE_WORDS or is_krono(name):
                    continue
                results.append({'type': current_type, 'item': name, 'price_pp': None,
                               'price_krono': kron_count, 'seller': seller, 'raw': msg})

        # Pass 4: "1kr" glued style
        kron_glued = re.compile(r'([A-Za-z][A-Za-z\s\'\-\+\:]{1,60}?)\s+(\d+)\s*[kK][rR]\b', re.IGNORECASE)
        for m in kron_glued.finditer(seg):
            name = clean_item_name(m.group(1))
            kron_count = int(m.group(2))
            if not name or len(name) < 2 or name.upper() in NOISE_WORDS or is_krono(name):
                continue
            results.append({'type': current_type, 'item': name, 'price_pp': None,
                           'price_krono': kron_count, 'seller': seller, 'raw': msg})

    return results


def watch_log(log_path, verbose=True):
    from db import init_db, save_auction

    init_db()

    path = Path(log_path)
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {log_path}")

    print(f"👀 Watching: {log_path}")
    print("Press Ctrl+C to stop.\n")

    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            line = line.strip()
            if not line or 'auction' not in line.lower():
                continue
            if not any(kw in line.upper() for kw in ('WTS', 'WTB', 'WTT')):
                continue

            entries = parse_auction_line(line)
            for entry in entries:
                try:
                    # Filter out bad Krono prices
                    if entry['item'] == 'Krono' and entry['price_pp']:
                        if not is_valid_krono_price(entry['price_pp']):
                            print(f"  ⚠️ Rejected Krono price {entry['price_pp']:,}pp (too far from avg)")
                            continue
                    save_auction(entry)
                    if verbose:
                        kron_str = f" ({entry['price_krono']} Krono)" if entry['price_krono'] else ""
                        pp_str = f"{entry['price_pp']:,}pp" if entry['price_pp'] else "?"
                        print(f"[{entry['type']}] {entry['item']} — {pp_str}{kron_str}  (seller: {entry['seller']})")
                except Exception as e:
                    print(f"  ⚠️ Failed to save: {e}")


def is_valid_krono_price(price_pp, con=None):
    """Return True if price is within 50% of the rolling average."""
    from db import get_krono_current, get_con, release_con
    owned = con is None
    if owned:
        con = get_con()
    try:
        avg = get_krono_current(con)
        if avg is None:
            return True  # no data yet, accept anything
        return avg * 0.5 <= price_pp <= avg * 1.5
    finally:
        if owned:
            release_con(con)
