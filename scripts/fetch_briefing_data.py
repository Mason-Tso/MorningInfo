#!/usr/bin/env python3
"""
fetch_briefing_data.py

Pulls the raw material for the daily MorningInfo briefing and prints it to stdout.
Standard library only. No API key is required; keys are optional extras read from
environment variables (FINNHUB_API_KEY, FMP_API_KEY, TIINGO_API_KEY).

Sections printed:
  1. Market snapshot   (Yahoo Finance + FRED + CoinGecko, no keys)
  2. Bank stocks       (Finnhub if key present, else Yahoo Finance)
  3. News by topic     (Google News RSS searches + a few direct feeds, last ~36h)

Usage:
  python scripts/fetch_briefing_data.py            # full run
  python scripts/fetch_briefing_data.py --json     # machine-readable dump
"""

import csv
import email.utils
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

UA = {"User-Agent": "Mozilla/5.0 (MorningInfo briefing bot; stdlib urllib)"}
NEWS_WINDOW_HOURS = 36
NOW = datetime.now(timezone.utc)

FINNHUB_KEY = os.environ.get("FINNHUB_API_KEY", "").strip()
FMP_KEY = os.environ.get("FMP_API_KEY", "").strip()
TIINGO_KEY = os.environ.get("TIINGO_API_KEY", "").strip()


# --------------------------------------------------------------------------- #
# HTTP helpers
# --------------------------------------------------------------------------- #
def http_get(url, timeout=12, headers=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def get_text(url, **kw):
    try:
        return http_get(url, **kw).decode("utf-8", errors="replace")
    except Exception as e:  # noqa: BLE001
        return None


def get_json(url, **kw):
    try:
        return json.loads(http_get(url, **kw).decode("utf-8", errors="replace"))
    except Exception:  # noqa: BLE001
        return None


# --------------------------------------------------------------------------- #
# 1. Market snapshot
# --------------------------------------------------------------------------- #
# Yahoo Finance chart endpoint (no key needed; needs a browser-like User-Agent)
YAHOO_SYMBOLS = [
    # (label, yahoo symbol, unit, plain-English meaning)
    ("S&P 500", "^GSPC", "pts", "the broad US stock market (500 big companies)"),
    ("Nasdaq Composite", "^IXIC", "pts", "tech-heavy US stock index"),
    ("Dow Jones", "^DJI", "pts", "30 large US blue-chip companies"),
    ("VIX", "^VIX", "", "the 'fear gauge': expected stock-market volatility over the next 30 days"),
    ("10-year Treasury yield (live)", "^TNX", "%", "benchmark long-term US rate; Yahoo quotes it in percent"),
    ("US Dollar Index (DXY)", "DX-Y.NYB", "", "the dollar vs a basket of major currencies; up = stronger dollar"),
    ("EUR/USD", "EURUSD=X", "", "how many dollars one euro buys"),
    ("USD/JPY", "JPY=X", "", "how many yen one dollar buys"),
    ("Gold", "GC=F", "$/oz", "gold futures price in dollars per ounce"),
    ("WTI Crude", "CL=F", "$/bbl", "US benchmark oil futures price per barrel"),
]

# FRED series via fredgraph.csv (no key needed)
FRED_SERIES = [
    ("2-year Treasury yield", "DGS2", "reflects where markets think the Fed's rate is going over ~2 years"),
    ("10-year Treasury yield", "DGS10", "the benchmark long-term US interest rate; drives mortgage rates"),
    ("Fed funds effective rate", "DFF", "the Fed's overnight policy rate, i.e. the base cost of money"),
    ("SOFR", "SOFR", "overnight secured borrowing rate; the modern replacement for LIBOR"),
]

COINGECKO_IDS = [
    ("Bitcoin", "bitcoin"),
    ("Ethereum", "ethereum"),
    ("Solana", "solana"),
    ("XRP (Ripple)", "ripple"),
    ("Hyperliquid (HYPE)", "hyperliquid"),
]


def yahoo_quote(symbol):
    """Return (as_of_date, last, prev_close) from Yahoo's chart endpoint, or None."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?range=5d&interval=1d"
    data = get_json(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"})
    try:
        meta = data["chart"]["result"][0]["meta"]
        last = meta.get("regularMarketPrice")
        prev = meta.get("chartPreviousClose") or meta.get("previousClose")
        ts = meta.get("regularMarketTime")
        d = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC") if ts else "n/a"
        if last is None or prev is None:
            return None
        return d, float(last), float(prev)
    except (KeyError, IndexError, TypeError, ValueError):
        return None


def fred_last_two(series):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
    txt = get_text(url)
    if not txt:
        return None
    vals = []
    for row in csv.DictReader(io.StringIO(txt)):
        v = row.get(series) or row.get("VALUE") or ""
        d = row.get("DATE") or row.get("observation_date") or ""
        if v not in ("", "."):
            try:
                vals.append((d, float(v)))
            except ValueError:
                pass
    if len(vals) < 2:
        return None
    (d1, v1), (d0, v0) = vals[-1], vals[-2]
    return d1, v1, v0


def coingecko_prices():
    ids = ",".join(i for _, i in COINGECKO_IDS)
    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        f"?ids={ids}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"
    )
    return get_json(url) or {}


def pct(cur, prev):
    if prev in (None, 0):
        return None
    return (cur - prev) / prev * 100.0


def fmt_num(x, unit=""):
    if x is None:
        return "n/a"
    if abs(x) >= 1000:
        s = f"{x:,.0f}"
    elif abs(x) >= 10:
        s = f"{x:,.2f}"
    else:
        s = f"{x:,.4f}".rstrip("0").rstrip(".")
    return f"{s} {unit}".strip()


def fmt_pct(p):
    if p is None:
        return "n/a"
    return f"{p:+.2f}%"


def market_snapshot():
    out = {"indices": [], "rates": [], "crypto": []}
    for label, sym, unit, meaning in YAHOO_SYMBOLS:
        r = yahoo_quote(sym)
        if r:
            d, last, prev = r
            out["indices"].append(
                {"label": label, "date": d, "last": last, "prev": prev,
                 "chg_pct": pct(last, prev), "unit": unit, "meaning": meaning}
            )
        else:
            out["indices"].append({"label": label, "error": "unavailable", "meaning": meaning})
    for label, series, meaning in FRED_SERIES:
        r = fred_last_two(series)
        if r:
            d, v1, v0 = r
            out["rates"].append(
                {"label": label, "date": d, "last": v1, "prev": v0,
                 "chg_bp": round((v1 - v0) * 100, 1), "meaning": meaning}
            )
        else:
            out["rates"].append({"label": label, "error": "unavailable", "meaning": meaning})
    cg = coingecko_prices()
    for label, cid in COINGECKO_IDS:
        q = cg.get(cid) if isinstance(cg, dict) else None
        if q and "usd" in q:
            out["crypto"].append(
                {"label": label, "last": q["usd"], "chg_24h_pct": q.get("usd_24h_change"),
                 "mcap": q.get("usd_market_cap")}
            )
        else:
            out["crypto"].append({"label": label, "error": "unavailable"})
    return out


# --------------------------------------------------------------------------- #
# 2. Bank & fintech stocks
# --------------------------------------------------------------------------- #
STOCKS = [
    ("Citigroup", "C"), ("JPMorgan", "JPM"), ("Goldman Sachs", "GS"), ("Morgan Stanley", "MS"),
    ("Bank of America", "BAC"), ("Wells Fargo", "WFC"), ("Barclays (ADR)", "BCS"),
    ("Coinbase", "COIN"), ("Robinhood", "HOOD"), ("Galaxy Digital", "GLXY"),
    ("Circle", "CRCL"), ("Blackstone", "BX"), ("Apollo", "APO"), ("Ares", "ARES"),
    ("Regional banks ETF", "KRE"), ("Financials ETF", "XLF"),
]


def finnhub_quote(ticker):
    url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_KEY}"
    q = get_json(url)
    if q and q.get("c"):
        return {"last": q["c"], "prev": q.get("pc"), "chg_pct": q.get("dp")}
    return None


def yahoo_stock(ticker):
    r = yahoo_quote(ticker)
    if r:
        d, last, prev = r
        return {"last": last, "prev": prev, "chg_pct": pct(last, prev), "date": d}
    return None


def bank_stocks():
    rows = []
    for name, t in STOCKS:
        q = finnhub_quote(t) if FINNHUB_KEY else None
        if not q:
            q = yahoo_stock(t)
        rows.append({"name": name, "ticker": t, **(q or {"error": "unavailable"})})
    return rows


def finnhub_company_news(ticker, days=2, limit=5):
    if not FINNHUB_KEY:
        return []
    frm = (NOW - timedelta(days=days)).strftime("%Y-%m-%d")
    to = NOW.strftime("%Y-%m-%d")
    url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={frm}&to={to}&token={FINNHUB_KEY}"
    data = get_json(url) or []
    items = []
    for n in data[:limit]:
        items.append({"source": n.get("source", ""), "title": n.get("headline", ""),
                      "url": n.get("url", ""), "published": n.get("datetime")})
    return items


# --------------------------------------------------------------------------- #
# 3. News
# --------------------------------------------------------------------------- #
def gnews(query, when="2d"):
    q = urllib.parse.quote(f"{query} when:{when}")
    return f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"


# (section, label, feed url, max items)
FEEDS = [
    # --- Markets / macro -----------------------------------------------------
    ("MARKETS & MACRO", "CNBC Markets", "https://www.cnbc.com/id/15839069/device/rss/rss.html", 6),
    ("MARKETS & MACRO", "MarketWatch", "https://feeds.content.dowjones.io/public/rss/mw_topstories", 5),
    ("MARKETS & MACRO", "Google: Fed / rates / Treasury", gnews("Federal Reserve OR Treasury yields OR inflation markets"), 5),
    ("MARKETS & MACRO", "Google: Wall Street trading desks", gnews('"trading" AND ("Wall Street" OR "sales and trading" OR "markets revenue")'), 5),
    # --- Banks ---------------------------------------------------------------
    ("BANKS & S&T", "Google: Citi", gnews("Citigroup OR Citi bank markets"), 5),
    ("BANKS & S&T", "Google: JPMorgan", gnews("JPMorgan"), 5),
    ("BANKS & S&T", "Google: Goldman Sachs", gnews('"Goldman Sachs"'), 5),
    ("BANKS & S&T", "Google: Morgan Stanley / BofA / Barclays", gnews('"Morgan Stanley" OR "Bank of America" OR Barclays OR "Deutsche Bank" OR UBS trading'), 5),
    ("BANKS & S&T", "American Banker", "https://www.americanbanker.com/feed", 4),
    # --- Private credit ------------------------------------------------------
    ("PRIVATE CREDIT", "Google: private credit", gnews('"private credit"'), 6),
    ("PRIVATE CREDIT", "Google: Apollo / Blackstone / Ares credit", gnews('(Apollo OR Blackstone OR Ares OR "Blue Owl" OR KKR) AND (credit OR lending OR "direct lending")'), 4),
    # --- Crypto & digital assets --------------------------------------------
    ("CRYPTO & DIGITAL ASSETS", "CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/", 6),
    ("CRYPTO & DIGITAL ASSETS", "The Block", "https://www.theblock.co/rss.xml", 5),
    ("CRYPTO & DIGITAL ASSETS", "Google: banks + crypto", gnews('(Citi OR JPMorgan OR "Goldman Sachs" OR "Morgan Stanley" OR "Bank of America") AND (crypto OR stablecoin OR tokenization OR blockchain OR "digital assets")'), 5),
    ("CRYPTO & DIGITAL ASSETS", "Google: Ripple / Galaxy / Pantera", gnews("Ripple XRP OR \"Galaxy Digital\" OR \"Pantera Capital\""), 5),
    ("CRYPTO & DIGITAL ASSETS", "Google: Coinbase / Robinhood / Circle", gnews("Coinbase OR Robinhood OR \"Circle\" USDC"), 5),
    ("CRYPTO & DIGITAL ASSETS", "Google: Securitize / Centrifuge / tokenization", gnews("Securitize OR Centrifuge OR \"tokenized\" treasuries OR \"real-world assets\""), 5),
    ("CRYPTO & DIGITAL ASSETS", "Google: Hyperliquid / DeFi", gnews("Hyperliquid OR DeFi perpetuals"), 4),
    ("CRYPTO & DIGITAL ASSETS", "Google: stablecoin policy", gnews("stablecoin regulation OR GENIUS Act OR SEC crypto"), 4),
    # --- Fintech -------------------------------------------------------------
    ("FINTECH", "Google: Stripe / Plaid", gnews("Stripe OR Plaid fintech"), 5),
    ("FINTECH", "Finextra", "https://www.finextra.com/rss/headlines.aspx", 5),
    # --- Growth equity & VC --------------------------------------------------
    ("GROWTH EQUITY & VC", "Google: Insight Partners", gnews('"Insight Partners"'), 4),
    ("GROWTH EQUITY & VC", "Google: General Atlantic", gnews('"General Atlantic"'), 4),
    ("GROWTH EQUITY & VC", "Google: fintech funding rounds", gnews('fintech ("raises" OR "Series A" OR "Series B" OR "Series C" OR "funding round" OR valuation)'), 6),
    ("GROWTH EQUITY & VC", "Google: growth equity / VC mega-rounds", gnews('("growth equity" OR "venture capital") AND ("raises" OR "closes fund" OR "led by")'), 5),
    ("GROWTH EQUITY & VC", "TechCrunch Venture", "https://techcrunch.com/category/venture/feed/", 5),
]


def parse_date(s):
    if not s:
        return None
    try:
        d = email.utils.parsedate_to_datetime(s)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d
    except Exception:  # noqa: BLE001
        return None


def clean(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def fetch_rss(url, limit):
    raw = None
    try:
        raw = http_get(url)
        root = ET.fromstring(raw)
    except Exception:  # noqa: BLE001
        return []
    items = []
    cutoff = NOW - timedelta(hours=NEWS_WINDOW_HOURS)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = list(root.iter("item")) or root.findall(".//atom:entry", ns)
    for it in entries:
        title = clean(it.findtext("title") or it.findtext("atom:title", default="", namespaces=ns))
        link = (it.findtext("link") or "").strip()
        if not link:
            l = it.find("atom:link", ns)
            link = l.get("href", "") if l is not None else ""
        pub = it.findtext("pubDate") or it.findtext("atom:updated", default="", namespaces=ns) \
            or it.findtext("atom:published", default="", namespaces=ns)
        d = parse_date(pub)
        if d and d < cutoff:
            continue
        src = it.findtext("source") or ""
        desc = clean(it.findtext("description") or "")[:160]
        if title:
            # Google News titles end with " - Publisher"
            if src and title.endswith(f" - {src}"):
                title = title[: -len(src) - 3]
            items.append({"title": title, "link": link, "published": d.isoformat() if d else None,
                          "publisher": clean(src), "desc": desc})
        if len(items) >= limit:
            break
    return items


def news_by_section():
    seen = set()
    sections = {}
    for section, label, url, limit in FEEDS:
        items = fetch_rss(url, limit)
        kept = []
        for it in items:
            key = re.sub(r"[^a-z0-9]", "", it["title"].lower())[:70]
            if key in seen:
                continue
            seen.add(key)
            kept.append(it)
        if kept:
            sections.setdefault(section, []).append({"feed": label, "items": kept})
    return sections


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #
def render(snapshot, stocks, company_news, sections):
    L = []
    L.append(f"=== MORNINGINFO RAW DATA — {NOW.strftime('%A, %B %d, %Y %H:%M UTC')} ===")
    L.append("(Index/stock numbers are Yahoo's latest print vs the prior close; FRED yields lag 1-2 days; news window = last "
             f"{NEWS_WINDOW_HOURS}h. Anything marked n/a or unavailable was not reachable.)\n")

    L.append("--- MARKET SNAPSHOT ---")
    for r in snapshot["indices"]:
        if "error" in r:
            L.append(f"  {r['label']}: unavailable   # {r['meaning']}")
        else:
            L.append(f"  {r['label']}: {fmt_num(r['last'], r['unit'])} ({fmt_pct(r['chg_pct'])} vs prior close, as of {r['date']})   # {r['meaning']}")
    for r in snapshot["rates"]:
        if "error" in r:
            L.append(f"  {r['label']}: unavailable   # {r['meaning']}")
        else:
            L.append(f"  {r['label']}: {r['last']:.2f}% ({r['chg_bp']:+.0f} bp vs prior day, as of {r['date']})   # {r['meaning']}")
    for r in snapshot["crypto"]:
        if "error" in r:
            L.append(f"  {r['label']}: unavailable")
        else:
            mc = f", mkt cap ${r['mcap']/1e9:,.0f}B" if r.get("mcap") else ""
            L.append(f"  {r['label']}: ${r['last']:,.2f} ({fmt_pct(r.get('chg_24h_pct'))} 24h{mc})")
    L.append("")

    L.append("--- BANK / FINTECH / ALT-MANAGER STOCKS (last close vs prior) ---")
    for s in stocks:
        if "error" in s:
            L.append(f"  {s['name']} ({s['ticker']}): unavailable")
        else:
            L.append(f"  {s['name']} ({s['ticker']}): ${s['last']:,.2f} ({fmt_pct(s.get('chg_pct'))})")
    L.append("")

    if company_news:
        L.append("--- COMPANY NEWS (Finnhub) ---")
        for t, items in company_news.items():
            if not items:
                continue
            L.append(f"  [{t}]")
            for n in items:
                L.append(f"    - {n['title']} ({n['source']}) {n['url']}")
        L.append("")

    for section in ["MARKETS & MACRO", "BANKS & S&T", "PRIVATE CREDIT",
                    "CRYPTO & DIGITAL ASSETS", "FINTECH", "GROWTH EQUITY & VC"]:
        feeds = sections.get(section)
        L.append(f"--- NEWS: {section} ---")
        if not feeds:
            L.append("  (nothing fetched)")
        for f in feeds or []:
            L.append(f"  [{f['feed']}]")
            for it in f["items"]:
                pub = f" ({it['publisher']})" if it["publisher"] else ""
                when = it["published"][:16].replace("T", " ") if it["published"] else ""
                L.append(f"    - {it['title']}{pub} {when}")
                if it["link"]:
                    L.append(f"      {it['link']}")
        L.append("")

    L.append("=== END RAW DATA ===")
    return "\n".join(L)


def main():
    snapshot = market_snapshot()
    stocks = bank_stocks()
    company_news = {}
    if FINNHUB_KEY:
        for t in ["C", "JPM", "GS", "MS", "BAC", "COIN", "HOOD", "GLXY"]:
            company_news[t] = finnhub_company_news(t)
    sections = news_by_section()

    if "--json" in sys.argv:
        payload = {"generated_utc": NOW.isoformat(), "snapshot": snapshot, "stocks": stocks,
                   "company_news": company_news, "news": sections}
        sys.stdout.buffer.write(json.dumps(payload, indent=1).encode("utf-8"))
        return

    sys.stdout.buffer.write(render(snapshot, stocks, company_news, sections).encode("utf-8", errors="replace"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
