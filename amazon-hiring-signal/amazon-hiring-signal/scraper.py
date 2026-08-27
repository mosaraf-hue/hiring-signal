#!/usr/bin/env python3
"""
Amazon Jobs signal scraper.

Pulls every live listing from amazon.jobs' internal search endpoint,
normalizes it, and merges it into data/jobs.json — a running dataset
that tracks when each job was first seen and last seen (still live).

Run on a schedule (see .github/workflows/scrape.yml). Each run:
  1. Fetches all pages of current listings.
  2. Marks jobs no longer returned as "closed" (last_seen stays frozen).
  3. Adds new jobs with first_seen = today.
  4. Writes data/jobs.json for the dashboard to read.

NOTE: amazon.jobs has no official public API. This uses the same
internal JSON endpoint the site's own search page calls. Amazon can
change field names or block automated traffic without notice — if
this starts returning empty results, open amazon.jobs/en/search in a
browser, check dev tools > Network for the search.json call, and
diff the params/fields against this script.
"""

import json
import time
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://www.amazon.jobs/en/search.json"
PAGE_SIZE = 100          # amazon.jobs typically caps this around 100
MAX_PAGES = 500          # hard safety ceiling (50k jobs) so a bug can't loop forever
SLEEP_BETWEEN_REQUESTS = 1.5   # seconds — keep this polite, don't hammer the endpoint
DATA_PATH = Path(__file__).parent / "data" / "jobs.json"

HEADERS = {
    # A normal browser-like UA. amazon.jobs will often 403 requests with
    # no user-agent at all.
    "User-Agent": "Mozilla/5.0 (compatible; job-signal-tracker/1.0; +personal use)",
    "Accept": "application/json",
}


def fetch_page(offset: int) -> dict:
    params = {
        "offset": offset,
        "result_limit": PAGE_SIZE,
        "sort": "recent",
    }
    url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def normalize(raw_job: dict) -> dict:
    """
    Map amazon.jobs' raw fields to a stable schema. Uses .get() with
    fallbacks everywhere because upstream field names have drifted
    before (e.g. normalized_location vs location vs city/state/country).
    """
    job_id = raw_job.get("id_icims") or raw_job.get("id") or raw_job.get("job_id")

    city = raw_job.get("city") or ""
    state = raw_job.get("state") or ""
    country = raw_job.get("country_code") or raw_job.get("country") or ""
    location = raw_job.get("normalized_location") or ", ".join(
        [p for p in [city, state, country] if p]
    )

    category = (
        raw_job.get("job_category")
        or raw_job.get("category")
        or raw_job.get("business_category")
        or "Uncategorized"
    )

    team = ""
    if isinstance(raw_job.get("team"), dict):
        team = raw_job["team"].get("team_name", "")
    else:
        team = raw_job.get("team_name", "")

    return {
        "job_id": job_id,
        "title": raw_job.get("title", "").strip(),
        "category": category,
        "team": team,
        "location": location,
        "city": city,
        "state": state,
        "country": country,
        "posted_date": raw_job.get("posted_date", ""),
        "url": "https://www.amazon.jobs" + raw_job.get("job_path", "")
        if raw_job.get("job_path")
        else raw_job.get("url_next_step", ""),
        "raw": raw_job,  # keep the original in case the dashboard needs a field we didn't map
    }


def scrape_all() -> list[dict]:
    all_jobs = []
    offset = 0
    total_hits = None

    for page in range(MAX_PAGES):
        try:
            data = fetch_page(offset)
        except Exception as e:
            print(f"[error] request failed at offset {offset}: {e}", file=sys.stderr)
            break

        jobs = data.get("jobs", [])
        if total_hits is None:
            total_hits = data.get("hits", data.get("total_hits", 0))
            print(f"[info] reported total hits: {total_hits}")

        if not jobs:
            break

        all_jobs.extend(normalize(j) for j in jobs)
        offset += PAGE_SIZE
        print(f"[info] fetched {len(all_jobs)} / {total_hits or '?'}")

        if total_hits and offset >= total_hits:
            break

        time.sleep(SLEEP_BETWEEN_REQUESTS)

    return all_jobs


def merge_with_history(current_jobs: list[dict]) -> dict:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if DATA_PATH.exists():
        history = json.loads(DATA_PATH.read_text())
    else:
        history = {"jobs": {}, "last_run": None}

    seen_ids = set()
    for job in current_jobs:
        jid = str(job["job_id"])
        seen_ids.add(jid)
        if jid in history["jobs"]:
            history["jobs"][jid].update(job)
            history["jobs"][jid]["last_seen"] = today
            history["jobs"][jid]["status"] = "open"
        else:
            job["first_seen"] = today
            job["last_seen"] = today
            job["status"] = "open"
            history["jobs"][jid] = job

    # anything not seen this run is no longer posted -> mark closed
    for jid, job in history["jobs"].items():
        if jid not in seen_ids and job.get("status") != "closed":
            job["status"] = "closed"
            job["closed_date"] = today

    history["last_run"] = today
    return history


def main():
    print("[info] starting scrape of amazon.jobs")
    current_jobs = scrape_all()
    print(f"[info] scrape complete: {len(current_jobs)} live jobs found")

    if not current_jobs:
        print("[warn] zero jobs returned — endpoint may have changed or blocked the request. "
              "Not overwriting existing data.", file=sys.stderr)
        sys.exit(1)

    history = merge_with_history(current_jobs)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(history, indent=2))
    print(f"[info] wrote {DATA_PATH} ({len(history['jobs'])} total jobs tracked)")


if __name__ == "__main__":
    main()
