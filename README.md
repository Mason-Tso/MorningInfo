# MorningInfo

A daily markets briefing, written for someone new to markets who is recruiting for
Sales & Trading, crypto/digital assets, and growth equity/VC roles.

- Arrives by email every morning at 7:30 AM Eastern (a Claude Code cloud routine sends it, so no
  computer needs to be on).
- Every edition is also saved to `briefings/YYYY-MM-DD.md`. Run `git pull` to refresh the archive.
- Covers: what the trading floor is talking about, a market snapshot with plain-English
  "so what" lines, bank and S&T news, crypto and digital assets, private credit (brief),
  growth equity and VC, three people worth reaching out to today, one concept explained from
  zero, an opinion on where a sector is heading, and a jargon glossary.

See `CLAUDE.md` for the full format spec, sectors, and data sources.

## Local run

```
python scripts/fetch_briefing_data.py
```

No API keys required. Standard library only.
