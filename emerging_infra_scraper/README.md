
# Emerging Infra Scraper (Starter Kit)

A minimal, configurable pipeline to **collect project pages and articles** about development, infrastructure, and technology for **Ghana, Kenya, and Nigeria**, then **generate YouTube-friendly title ideas** for your channel.

> Expand to any country by adding seeds and site-specific parsers.

## What's Inside
- `seeds.yaml` — curated list of official portals + news/search pages per country
- `scraper.py` — polite scraper using `requests`, `BeautifulSoup`, and optional `feedparser`
- `out/` — output folder where CSV + title ideas will be saved

## Install (local machine)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install requests beautifulsoup4 pyyaml feedparser
```

## Run

```bash
python scraper.py --config seeds.yaml --out out
```

Outputs:
- `out/scraped_YYYYMMDD_HHMMSS.csv` — table of (country, title, url, date_text, summary, source_portal/source_feed)
- `out/titles_YYYYMMDD_HHMMSS.txt` — auto-suggested video titles

## Customize

1. **Add more sources** to `seeds.yaml` (ministries, PPP units, road/rail/port/energy agencies, AfDB/World Bank).
2. **Write site-specific parsers** by replacing `parse_generic_article` or branching on domain.
3. **Schedule** via cron/GitHub Actions and push outputs to a repo or Google Sheets.
4. **Enrich** with currency normalization, km/MW extraction, and geocoding for maps.

## Ethics & Legality
- Respect `robots.txt` and each site's ToS.
- Rate-limit requests; attribute sources in your videos.
- Prefer open data / APIs whenever possible.

— Generated 2025-10-16T18:58:31.205101 UTC
