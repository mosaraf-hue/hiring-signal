# Amazon Hiring Signal Tracker

Tracks Amazon.jobs postings over time so you can spot which orgs/categories
are actively hiring (budget signal) and where (location signal) — fully
automated once deployed.

## How it works

```
scraper.py  --(runs daily via GitHub Actions)-->  data/jobs.json  -->  dashboard/index.html
```

- `scraper.py` calls amazon.jobs' internal search endpoint, paginates through
  every live listing, and merges results into `data/jobs.json`. Each job
  tracks `first_seen`, `last_seen`, and `status` (open/closed) so you can see
  new postings and how long roles stay open.
- `.github/workflows/scrape.yml` runs that script once a day for free on
  GitHub's infrastructure and commits the updated data — no server for you
  to maintain or pay for.
- `dashboard/index.html` is a static page (no backend needed) that reads
  `data/jobs.json` and renders KPIs, a hiring-trend chart by category, an
  open-roles-by-location chart, and a filterable job table.

## One-time setup (~10 minutes)

1. **Create a GitHub repo** (private is fine) and push these files to it.
2. **Turn on Actions**: repo → Settings → Actions → General → allow workflows
   to run and to have read/write permissions (needed so the workflow can
   commit `data/jobs.json` back to the repo).
3. **Kick off the first run manually**: repo → Actions tab → "Scrape Amazon
   Jobs" → Run workflow. This populates real data instead of the sample data
   included here.
4. **Turn on GitHub Pages**: repo → Settings → Pages → Deploy from a branch →
   pick `main` and `/ (root)`. Your dashboard will be live at
   `https://<you>.github.io/<repo>/dashboard/`.
5. Done. It now updates itself daily and your dashboard always shows current
   data when you open the link.

## Adjusting it

- **Change frequency**: edit the `cron` line in `.github/workflows/scrape.yml`
  (currently once a day at 13:00 UTC). Keep it infrequent — this hits a
  non-public endpoint and being a light, polite requester keeps it working.
- **Add a "watchlist" view**: the dashboard filters by category/location/status
  already; if you want a saved shortlist of teams you personally care about,
  that's a small addition to `dashboard/index.html` — ask and I'll add it.
- **Field drift**: amazon.jobs isn't a documented API, so if `scraper.py`
  starts returning 0 jobs, open amazon.jobs/en/search in a browser, check
  the Network tab in dev tools for the `search.json` call, and compare its
  response fields against `normalize()` in `scraper.py`.

## A note on scope

`data/jobs.json` currently has **sample/synthetic data** so you can see what
the dashboard looks like immediately. Once you run the real scraper (step 3
above), it overwrites this with live Amazon postings.

This scrapes a non-public (though unauthenticated) endpoint, which sits
outside amazon.jobs' terms of service even though the underlying data is
publicly visible on the site. That's a call worth making deliberately —
keeping request volume low (as configured) reduces the odds of being
noticed or blocked, but doesn't change the ToS question.
