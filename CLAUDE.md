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

## Briefing format (plain-text email, 5-minute news brief)

Style model: a morning news brief written for a smart beginner. Read time about 5 minutes
(900-1,200 words, 15-22 items). Each item is one short paragraph of 2-3 plain-English sentences:
what happened, why it matters, and, only when it truly matters, ONE number. Every item ENDS with
a source tag in caps (WSJ, BBG, FT, Reuters, CNBC, NYT, Axios, CoinDesk, The Block, TechCrunch,
PitchBook, or the company). Plain text only: no markdown headers, tables or bold; CAPS section
labels; items separated by a blank line.

Easy to understand is the top rule:
- Write like a news anchor explaining to a friend, not like a Bloomberg terminal. Full sentences,
  no ticker soup, no abbreviations without a gloss.
- Numbers are seasoning, not the meal. At most one or two figures per item, rounded ("oil is
  above $100 a barrel", "the 10-year yield is near 5%", "a $100 million round"). Never a string
  of levels and percentage moves. Skip basis points, intraday ticks and decimals unless the story
  is literally about that number.
- Always say why it matters in one clause a beginner can follow ("which makes borrowing more
  expensive for everyone", "which is bad for bank trading desks because...").
- When a term a beginner would not know appears, gloss it in a short bracket the first time,
  e.g. "FICC [the desk that trades bonds, currencies and commodities]".
- No stock prices to the cent ("shares closed at $138.14"). Say "shares rose" or "shares are
  near a record" instead, unless the price itself is the story.
- Freshness: the brief is about the last 24-48 hours. If an item is older than about three days
  (for example last quarter's earnings or a deal announced weeks ago), either drop it or say
  plainly when it happened ("back in July, JPMorgan reported..."). Never present old news as
  "just" happened, because Mason may repeat it in a coffee chat.
- No intros, no filler, no lectures. Numbers and facts must come from fetched data or a named
  source; never invent them.

Example of the item style to match:

  Oil is above $100 a barrel again after new US and Iranian strikes near the Strait of Hormuz,
  the shipping lane a fifth of the world's oil passes through. Higher oil feeds inflation fears,
  which is why bond yields jumped and stocks fell for a fourth day. CNBC

  A group of 21 big banks including Citi, Goldman and UBS said they will launch a shared dollar
  stablecoin [a digital token always worth $1] by early 2027 for cross-border payments. It is the
  banks' answer to Circle and other crypto firms taking payment business from them. Reuters

Subject line: `MorningInfo — Thu Sep 10: <5-8 word headline of the day>`

Sections, in this order:

1. **THE MOOD** (2-3 sentences, no list). What markets did and the one reason why, in plain
   words. Example: "Stocks fell for a fourth day and bond yields hit their highest since 2023,
   all because oil spiked on the Iran conflict and an inflation report ran hot. The dollar
   weakened and gold stayed near records. Bitcoin drifted lower with everything else."
2. **BIG PICTURE** (4-6 items). Geopolitics, the Fed and other central banks, inflation and
   jobs data, oil, major earnings, big sell-side calls (name the bank and person when known).
3. **BANKS & SALES/TRADING** (3-5 items, priority). Citi, JPMorgan, Goldman, Morgan Stanley,
   BofA, Barclays, Deutsche, UBS: trading revenue, desk news, hires and exits, strategy calls,
   regulation, AI on the floor, layoffs. Name the desk it touches and gloss it.
4. **CRYPTO & DIGITAL ASSETS** (3-5 items). Bank moves first (tokenized deposits, stablecoins,
   custody), then Ripple, Galaxy, Pantera, Coinbase, Robinhood, Securitize, Centrifuge, Plaid,
   Stripe, Hyperliquid, Circle, Kraken and other fintech/crypto startups; then policy.
5. **PRIVATE CREDIT** (1-2 items). Brief.
6. **GROWTH EQUITY, VC & FINTECH FUNDING** (3-4 items). Insight Partners and General Atlantic
   whenever they appear; big rounds and fund closes; say what the company does in plain words.
7. **REACH OUT TODAY** (exactly three, one line each):
   `- <type of person: role + desk/team + firm> — <the news hook> — Ask: "<one natural question>"`
   At least one in bank S&T; spread the others across crypto/digital assets and growth/VC.
8. **LEARN ONE THING** (3-4 sentences). One concept from today's news explained from zero
   with a concrete example. Do not repeat a concept from the last 10 briefings.
9. **TAKE** (2-3 sentences, labelled opinion). Where one sector is heading and why.

Do not pad. If a sector is quiet, write one line saying so and move on. Prefer items dated
today or yesterday (Eastern time).

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
