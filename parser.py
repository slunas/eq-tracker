"""
parser.py — EQ Auction Log Parser
Strict, safe parsing. Better to miss edge cases than corrupt data.
"""

import re
import time
from pathlib import Path

KRONO_ALIASES = ['krono', 'kronos', 'kron']
NOISE_WORDS = {'pst', 'obo', 'or', 'and', 'wts', 'wtb', 'wtt', 'free', 'cheap', 'rare',
               'pm', 'msg', 'ea', 'each', 'per', 'stack', 'tell', 'me', 'offers',
               'selling', 'buying', 'paying', 'buying', 'cheap', 'cheap'}

KRONO_MIN = 1000
KRONO_MAX = 20000


# ─────────────────────────────────────────────
# PRICE NORMALIZATION
# ─────────────────────────────────────────────

def to_pp(price_str):
    """
    Convert a price string to integer pp.
    Handles: 8000, 8000pp, 8000p, 8k, 8.5k, 8kpp
    Returns None if it can't parse cleanly.
    """
    s = price_str.strip().lower().rstrip('p')  # strip trailing p/pp
    try:
        if s.endswith('k'):
            return int(float(s[:-1]) * 1000)
        return int(s.replace(',', ''))
    except (ValueError, TypeError):
        return None


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def clean_item_name(name):
    name = name.strip(" -,:/'\"\\|[](){}#@!?")
    # Remove weird unicode/special chars
    name = re.sub(r'[^\x20-\x7E]', '', name)
    words = name.split()
    while words and words[-1].lower() in NOISE_WORDS:
        words.pop()
    while words and words[0].lower() in NOISE_WORDS:
        words.pop(0)
    result = " ".join(words).title()
    # Must be at least 3 chars and start with a letter
    if len(result) < 3 or not result[0].isalpha():
        return None
    return result


def is_krono(word):
    return word.lower().rstrip('s') in [a.rstrip('s') for a in KRONO_ALIASES]


def get_seller(line):
    """Extract seller name from EQ log line."""
    m = re.search(r'\] ([A-Za-z][A-Za-z0-9]{1,20}) auctions,', line, re.IGNORECASE)
    name = m.group(1) if m else None
    if name and name.lower() == "you":
        name = "Braece"
    return name


def get_message(line):
    """Extract auction message from quotes."""
    m = re.search(r"'(.+?)'", line)
    name = m.group(1) if m else None
    if name and name.lower() == "you":
        name = "Braece"
    return name


# ─────────────────────────────────────────────
# KRONO PRICE EXTRACTION
# ─────────────────────────────────────────────

def extract_krono_price(seg):
    """
    Strictly extract Krono price from a segment.
    Handles:
      Krono 8000pp / Krono 8000p / Krono 8000 / Krono 8k / Krono 8.5k
      2 Krono 16000pp / krono x2 12000
    Returns (price_pp, match_span) or (None, None)
    """
    alias_pat = '|'.join(re.escape(a) for a in KRONO_ALIASES)

    # Pattern: [qty] krono [xqty] <price>[pp/p/k]
    m = re.search(
        rf'(?:(\d+)\s+)?(?:{alias_pat})s?\s*(?:x\s*(\d+)\s+)?(\d[\d.,]*(?:[kK](?:pp?)?|pp?)?)(?=\s|$|[,|/])',
        seg, re.IGNORECASE
    )
    if m:
        qty1 = int(m.group(1)) if m.group(1) else 1
        qty2 = int(m.group(2)) if m.group(2) else 1
        qty = max(qty1, qty2)
        price = to_pp(m.group(3))
        if price and KRONO_MIN <= price // qty <= KRONO_MAX:
            return price // qty, m.span()

    # Pattern: <price>pp krono
    m = re.search(
        rf'(\d[\d.,]*(?:[kK](?:pp?)?|pp?))\s+(?:{alias_pat})s?(?=\s|$|[,\|/])',
        seg, re.IGNORECASE
    )
    if m:
        price = to_pp(m.group(1))
        if price and KRONO_MIN <= price <= KRONO_MAX:
            return price, m.span()

    return None, None


# ─────────────────────────────────────────────
# ITEM PRICE EXTRACTION
# ─────────────────────────────────────────────

def extract_items(seg, seller, msg_type):
    """
    Extract item+price pairs from a WTS/WTB segment.
    Only accepts items with explicit pp/p/k prices.
    Skips anything that looks weird.
    """
    results = []

    # Separators: // | □ — normalize to comma
    seg = re.sub(r'[/|\\□\-]{2,}', ',', seg)
    seg = re.sub(r'\s{2,}', ' ', seg)

    # Pattern A: item priced in pp/k  e.g. "Staff 500pp" "Fungi 2kpp"
    pp_pat = re.compile(
        r"([A-Za-z][A-Za-z0-9\s'\-\+\:,]{2,60}?)"
        r"\s+"
        r"(\d[\d,]*(?:\.\d+)?[kK]?(?:pp?))"
        r"(?=\s*(?:each|ea|obo|pst|$|,|\|)|\s+[A-Z])",
        re.IGNORECASE
    )
    for m in pp_pat.finditer(seg):
        name = clean_item_name(m.group(1))
        if not name or len(name) < 3 or name.lower() in NOISE_WORDS or is_krono(name):
            continue
        price = to_pp(m.group(2))
        if not price or price <= 0 or price > 10_000_000:
            continue
        results.append({'type': msg_type, 'item': name, 'price_pp': price,
                        'price_krono': None, 'seller': seller, 'raw': seg})

    # Pattern B: item priced in kr/krono  e.g. "Staff 9kr" "Fungi 2 krono"
    kr_pat = re.compile(
        r"([A-Za-z][A-Za-z0-9\s'\-\+\:,]{2,60}?)"
        r"\s+(\d+)\s*(?:krono|kronos|kron|kr)s?"
        r"(?=\s*(?:each|ea|obo|pst|,|$)|\s+[A-Z]|$)",
        re.IGNORECASE
    )
    for m in kr_pat.finditer(seg):
        name = clean_item_name(m.group(1))
        if not name or len(name) < 3 or name.lower() in NOISE_WORDS or is_krono(name):
            continue
        kr_count = int(m.group(2))
        if kr_count < 1 or kr_count > 100:
            continue
        results.append({'type': msg_type, 'item': name, 'price_pp': None,
                        'price_krono': kr_count, 'seller': seller, 'raw': seg})

    return results


# ─────────────────────────────────────────────
# MAIN PARSER
# ─────────────────────────────────────────────

def parse_auction_line(line):
    results = []

    seller = get_seller(line)
    msg = get_message(line)
    if not msg:
        return results

    # Split on WTS/WTB/WTT boundaries
    segments = re.split(r'\b(WTS|WTB|WTT|BUYING|SELLING)\b', msg, flags=re.IGNORECASE)

    current_type = None
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        if seg.upper() in ('WTS', 'WTT', 'SELLING'):
            current_type = 'WTS'
            continue
        if seg.upper() in ('WTB', 'BUYING'):
            current_type = 'WTB'
            continue
        if current_type is None:
            continue

        # Try Krono first (only on WTS lines for price tracking)
        krono_price, span = extract_krono_price(seg) if current_type == "WTS" else (None, None)
        if krono_price:
            # Sanity check: if a pp price appears AFTER the kr match, this is likely
            # a trade offer like "fungus tunic 1kr 2000p" not a Krono sale
            after_match = seg[span[1]:] if span else ''
            has_pp_after = bool(re.search(r'\d+\s*(?:pp?|[kK]pp?)', after_match, re.IGNORECASE))
            if not has_pp_after:
                results.append({
                    'type': current_type,
                    'item': 'Krono',
                    'price_pp': krono_price,
                    'price_krono': None,
                    'seller': seller,
                    'raw': msg
                })
            # Remove matched krono from seg so it doesn't confuse item parser
            seg = seg[:span[0]] + ' ' + seg[span[1]:]

        # Then items
        results.extend(extract_items(seg, seller, current_type))

    return results


# ─────────────────────────────────────────────
# LOG WATCHER
# ─────────────────────────────────────────────

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
            if not any(kw in line.upper() for kw in ('WTS', 'WTB', 'WTT', 'BUYING', 'SELLING')):
                continue

            entries = parse_auction_line(line)
            for entry in entries:
                try:
                    # Hard cap on Krono prices
                    if entry['item'] == 'Krono' and entry['price_pp']:
                        if not (KRONO_MIN <= entry['price_pp'] <= KRONO_MAX):
                            print(f"  ⚠️ Rejected Krono {entry['price_pp']:,}pp (out of range)")
                            continue
                    save_auction(entry)
                    if verbose:
                        kron_str = f" ({entry['price_krono']} Krono)" if entry['price_krono'] else ""
                        pp_str = f"{entry['price_pp']:,}pp" if entry['price_pp'] else "?"
                        print(f"[{entry['type']}] {entry['item']} — {pp_str}{kron_str}  (seller: {entry['seller']})")
                except Exception as e:
                    print(f"  ⚠️ Failed to save: {e}")


def is_valid_krono_price(price_pp):
    """Return True if price is within 50% of the rolling average."""
    from db import get_krono_current, get_con, release_con
    con = get_con()
    try:
        avg = get_krono_current(con)
        if avg is None:
            return True
        return avg * 0.5 <= price_pp <= avg * 1.5
    finally:
        release_con(con)
