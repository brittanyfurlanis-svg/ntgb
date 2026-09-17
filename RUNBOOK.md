# NTGB — www.ntgb.com.au runbook

Status (17 Sept 2026): LIVE. Repo `brittanyfurlanis-svg/ntgb` on GitHub, hosted on GitHub Pages, domain at GoDaddy,
AEMO data refreshing itself at 13:00 and 17:00 ACST daily. Everything below is clicking in a browser — nothing to install.

## What is set up (done)
1. **Repo** github.com/brittanyfurlanis-svg/ntgb (public). Folders: `site` (the map), `scripts` (AEMO fetcher), `data` (history + raw AEMO files, all states), `tests`, `.github/workflows`.
2. **Pages** Settings → Pages → Source = GitHub Actions, custom domain = `www.ntgb.com.au`.
3. **DNS at GoDaddy** (ntgb.com.au): A `@` → 185.199.108.153 / .109.153 / .110.153 / .111.153; CNAME `www` → `brittanyfurlanis-svg.github.io`.
4. **Refresh** Actions → "Refresh AEMO data": two jobs — `refresh` (fetch AEMO, commit data) then `publish` (redeploy the site).
   The publish job lives inside this workflow on purpose: a commit made by the bot does not trigger the separate "Publish site" workflow.

## Still to do
- **Enforce HTTPS**: Settings → Pages → once the "DNS check in progress" notice clears, tick **Enforce HTTPS**. Until then the site is served at http://www.ntgb.com.au (https will error). GitHub can take from an hour to a day after the DNS records go live.
- ntgb.com and ntgasboard.com: at GoDaddy use **Forwarding** → `https://www.ntgb.com.au` (permanent, 301). Do this after HTTPS is enforced.

## Day to day
- **Refresh on demand**: Actions → Refresh AEMO data → Run workflow → Run workflow. About 30 seconds; the site shows the new data a minute later.
- **A failed run** (nemweb down, file missing) leaves the site on the last good data — a failed fetch never blanks the page. Re-run it later.
- **Change the map**: edit `site/index.html` (upload the new file over the old one at github.com/brittanyfurlanis-svg/ntgb/upload/main/site) — the "Publish site" workflow redeploys in about a minute.
- **Check it ran**: Actions tab — green tick on today's "Refresh AEMO data". The footer of the site shows the last AEMO update and refresh time.

## Later (phase two)
- Private layer, sign-in, stored history beyond 31 days: `scripts/fetch_gbb.py` is plain Python and runs anywhere (Azure Australia East or Supabase Sydney); the public site stays static on Pages. The `data/raw` folder already holds every AEMO file as downloaded, all states, so nothing is lost in the meantime.
