# MorningInfo — daily markets briefing for coffee chats

## What this repo does

Every morning at 7:30 AM Eastern a cloud routine (Claude Code, running in Anthropic's cloud,
so Mason's computer can be off) does the following:

1. Runs `scripts/fetch_briefing_data.py` to pull live market numbers and the last ~36 hours of
   news across the sectors below.
2. Verifies and deepens the important stories with web search.
3. Writes a plain-English briefing to `briefings/YYYY-MM-DD.md` and pushes it to `main`.
4. Emails the same text to masontso74@gmail.com through the Gmail connector.

To get the archive on a laptop: `git pull`.

## Who this is for

Mason: Duke sophomore (Class of 2029), CS + Economics, recruiting right now for
Sales & Trading summer analyst roles (top priority: Citi, JPMorgan, Goldman Sachs, and the other
big banks), also interested in crypto / digital assets firms and growth equity / VC.
**New to markets.** The briefing exists so he can walk into a coffee chat sounding informed and
learn something every day. It must never assume knowledge; every term gets explained.

## Sectors and names to watch

- **Banks & Sales/Trading (priority):** Citi, JPMorgan, Goldman Sachs, Morgan Stanley,
  Bank of America, Barclays, Deutsche Bank, UBS. Trading revenue, desk performance, hires/exits,
  strategy calls from their research desks, regulation, tech/AI on the trading floor.
- **Private credit (keep brief):** Apollo, Blackstone, Ares, Blue Owl, KKR, bank partnerships,
  fund raises, defaults/stress, how it competes with bank lending.
- **Crypto & digital assets:** bank moves first (Citi, JPMorgan, Goldman, Morgan Stanley, BofA:
  tokenized deposits, stablecoins, custody, trading), then Ripple, Galaxy Digital, Pantera
  Capital, Coinbase, Robinhood, Securitize, Centrifuge, Plaid, Stripe, Hyperliquid, Circle,
  Kraken/Payward, and other fintech/crypto startups. Policy: GENIUS Act, SEC, CFTC, Treasury.
- **Growth equity & VC:** Insight Partners, General Atlantic, plus a16z, Sequoia, Thrive, TCV,
  Vista, Blackstone Growth, Tiger, Coatue. Fintech funding rounds, fund closes, exits, IPOs.

## Briefing format (plain-text email, wire-style news digest)

Style model: a trading-desk morning note. Dense, factual, news-first. Each item is a short
paragraph of 1-3 sentences that states what happened, the key numbers, and why it matters,
and ENDS with a source tag in caps (WSJ, BBG, FT, Reuters, CNBC, NYT, Axios, CoinDesk, The Block,
TechCrunch, PitchBook, company press release, etc.). No headline-only bullets, no filler, no
"in today's briefing" intros. Plain text only: no markdown headers, tables or bold; CAPS section
labels; items separated by a blank line. Target 1,200-1,800 words, 25-40 items.

Example of the item style to match:

  Within weeks of Iran's closure of the Strait of Hormuz, once Saudi Arabia's primary export
  route for oil, the kingdom turned to Plan B: bypassing the strait by ramping up exports through
  pipelines to the Red Sea. NYT

  BofA total card spending (w/e Sept 5) +7.8% y/y (prev. +3.7%). BofA said the surge was likely
  due to base effects from the shift in Labor Day timing and a rebound in gas prices. BofA

Tailoring for Mason (new to markets): when an item uses a term a beginner would not know, add a
short bracketed gloss the first time, e.g. "FICC [the fixed income, currencies and commodities
trading division]" or "the 2s10s curve [gap between 2-year and 10-year yields]". Keep glosses
to one short clause; do not turn items into lectures. Numbers must come from fetched data or a
named source; never invent them.

Subject line: `MorningInfo — Thu Sep 10: <5-8 word headline of the day>`

Sections, in this order:

1. **TAPE** (one or two lines). S&P, Nasdaq, 10-year yield, 2-year yield, DXY, Brent or WTI,
   gold, BTC, ETH with the latest level and move, and the as-of time. Example:
   `TAPE (7:15am ET): S&P 7,604 -0.4% | Nasdaq 26,150 -0.4% | 10y 4.91% +6bp | 2y 4.53% | DXY 98.4 | Brent $105 | Gold $4,400 | BTC $77.9k | ETH $2,465`
2. **MACRO & MARKETS** (8-12 items). What is moving markets: geopolitics, Fed/ECB/BoJ, data
   prints (PPI, CPI, jobs), Treasury yields, oil, big earnings, sell-side calls (name the bank:
   "GS FICC", "JPM's Kolanovic", "MS's Wilson"), notable stock moves.
3. **BANKS & SALES/TRADING** (5-8 items, priority). Citi, JPMorgan, Goldman, Morgan Stanley,
   BofA, Barclays, Deutsche, UBS: trading revenue and desk performance, hires/exits, strategy
   notes from their research, regulation, AI on the floor, layoffs, comp, anything a desk is
   talking about. Say which desk it touches when relevant.
4. **CRYPTO & DIGITAL ASSETS** (6-10 items). Bank moves first (tokenized deposits, stablecoins,
   custody), then Ripple, Galaxy, Pantera, Coinbase, Robinhood, Securitize, Centrifuge, Plaid,
   Stripe, Hyperliquid, Circle, Kraken/Payward and other fintech/crypto startups; then policy
   (GENIUS Act, SEC, CFTC, Treasury). Prices and flows count as news.
5. **PRIVATE CREDIT** (2-4 items, brief). Apollo, Blackstone, Ares, Blue Owl, KKR, fund
   raises, redemptions, downgrades, bank partnerships.
6. **GROWTH EQUITY, VC & FINTECH FUNDING** (5-8 items). Insight Partners and General Atlantic
   whenever they appear; other big rounds, fund closes, exits, IPOs; fintech rounds with amount,
   lead investor, valuation, what the company does.
7. **REACH OUT TODAY** (exactly three, compact). One per line:
   `- <type of person: role + desk/team + firm> — <the news hook> — Ask: "<one natural question>"`
   At least one in bank S&T; spread the others across crypto/digital assets and growth/VC.
8. **DECODER** (5-8 terms used above, one line each, plain English).
9. **TAKE** (3-4 sentences, labelled opinion). Where one sector is heading and why, tied to
   today's items.

Do not pad. If a sector is quiet, write one item saying so and move on. Prefer items dated
today or yesterday (Eastern time). Older items only if they are still driving the story and the
item says so.

## Project structure

```
scripts/fetch_briefing_data.py   # stdlib-only data pull: Yahoo Finance, FRED, CoinGecko, Google News RSS, direct feeds
briefings/YYYY-MM-DD.md          # archive, one file per day, written by the routine
CLAUDE.md                        # this file: audience, sectors, format
README.md                        # short human-facing overview
```

## Data sources (no keys required)

| Source | What it pulls |
|---|---|
| Yahoo Finance chart API | Indices, VIX, 10-year (live), DXY, FX, gold, oil, bank/fintech/alt-manager stocks |
| FRED (fredgraph.csv) | 2-year and 10-year Treasury yields, fed funds, SOFR (lag 1-2 days) |
| CoinGecko | BTC, ETH, SOL, XRP, HYPE prices and 24h change |
| Google News RSS searches | Per-company and per-topic headlines, last 36 hours |
| CNBC, MarketWatch, American Banker, CoinDesk, The Block, Finextra, TechCrunch Venture | Direct feeds |

Optional keys (read from environment variables, never committed): `FINNHUB_API_KEY` adds
per-ticker company news and quotes; `FMP_API_KEY` and `TIINGO_API_KEY` are reserved for
future use. To use them in the cloud routine, prefix the fetch command in the routine prompt
with `FINNHUB_API_KEY=... python3 scripts/fetch_briefing_data.py`.

## Network access in the cloud sandbox (important)

The routine runs in the "Default" claude.ai/code environment. Unless that environment's network
access is set to allow outbound traffic, the egress proxy blocks BOTH the fetch script (Bash) AND
WebFetch. Only WebSearch works, and it returns snippets rather than pages, so the briefing
quality drops. The fix is a one-time account setting: open the environment at
https://claude.ai/code (Settings > Environments > Default) and set network access to allow
outbound traffic (or allowlist at least: query1.finance.yahoo.com, fred.stlouisfed.org,
api.coingecko.com, news.google.com, feeds.content.dowjones.io, www.cnbc.com,
www.americanbanker.com, www.coindesk.com, www.theblock.co, www.finextra.com, techcrunch.com).

Symptoms of the block: every snapshot line reads "unavailable" and every news section
"nothing fetched"; WebFetch returns EGRESS_BLOCKED. When that happens the routine should not
debug the proxy. It should run

```
python3 scripts/fetch_briefing_data.py --urls
```

(needs no network; prints every URL the script would fetch, grouped) and try WebFetch on a few of
them once. If WebFetch is blocked too, fall back to WebSearch with targeted queries (index closes,
yields, oil, bank names, company names, "fintech raises") and write the best briefing possible,
noting in the MARKET SNAPSHOT which numbers are from search snippets.

## Running locally

```
python scripts/fetch_briefing_data.py          # human-readable raw data
python scripts/fetch_briefing_data.py --json   # JSON
```

Takes about 25 seconds. Then write the briefing following the format above.
