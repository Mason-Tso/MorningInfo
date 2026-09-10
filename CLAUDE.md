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

## Briefing format (plain-text email, ~900-1,300 words, 5-7 minute read)

Plain text only: no markdown headers, no tables, no bold. Use CAPS section labels, short
paragraphs, and "-" bullets. Explain every piece of jargon the first time it appears, in
parentheses, in one short clause. Tone: a friendly senior analyst mentoring a smart beginner.
Dates and numbers must come from the data file or a verified source; never invent numbers.
If something is unavailable, say so in one line and move on.

Subject line: `MorningInfo — Thu Sep 10: <5-8 word headline of the day>`

Sections, in this order:

1. **THE ONE THING** (3-4 sentences). The single story a trader at Citi/JPM/Goldman is talking
   about this morning, explained simply, and why it matters.
2. **MARKET SNAPSHOT.** One line each: S&P 500, Nasdaq, Dow, VIX, 10-year yield, 2-year yield,
   dollar index, oil, gold, Bitcoin, Ethereum. Format: `- S&P 500: 7,602 (-0.9%) — <so-what in
   under 10 words>`. Then two sentences on what the pattern across them says (for example:
   yields up, stocks down, oil up = inflation scare).
3. **BANKS & SALES/TRADING** (4-6 bullets, the priority section). For each item: what happened,
   why a trader cares, and which desk it touches (rates, FX, equities, credit, commodities,
   equity derivatives, etc.). Explain the desk in a few words when first mentioned.
4. **CRYPTO & DIGITAL ASSETS** (4-6 bullets). Bank moves first, then the named companies, then
   policy. Say what each company does in plain terms when first mentioned.
5. **PRIVATE CREDIT** (2-3 bullets, brief). One clause each on why it matters to banks.
6. **GROWTH EQUITY & VC** (3-5 bullets). Amount, lead investor, what the company does, why the
   round is interesting. Include Insight Partners / General Atlantic whenever they appear.
7. **THREE PEOPLE TO REACH OUT TO TODAY.** Exactly three. Each entry:
   `- WHO: <type of person: role + desk/team + firm, e.g. "a rates trader at Citi">`
   `  WHY TODAY: <the news hook that makes today a natural reason to reach out>`
   `  OPENER: <one natural sentence or question Mason could send or ask, showing he read the news; not sycophantic>`
   At least one must be bank S&T. Spread the other two across crypto/digital assets and
   growth equity/VC when the news allows.
8. **CONCEPT OF THE DAY** (~120 words). One concept that appeared in today's news, explained
   from zero with a concrete example. Do not repeat a concept used in the last 10 briefings
   (check `briefings/`).
9. **MY TAKE** (one paragraph). A clear opinion on where one sector is heading, with reasoning
   tied to today's news. Label it as opinion.
10. **JARGON DECODED.** Every technical term used above, one line each, max 12 terms.
11. **SOURCES.** 6-10 URLs actually used.

Do not pad. If a sector had a quiet day, say "Quiet day; nothing you need to know" and move on.

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
