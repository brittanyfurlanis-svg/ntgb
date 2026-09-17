# NTGB — NT Gas Flows

Public map of daily gas flows across the Northern Territory, built from AEMO's Gas Bulletin Board (GBB) files.
Live at https://www.ntgb.com.au once the steps in RUNBOOK.md are done.

```
site/                 the website (static — no server code)
  index.html          the map; reads site/data/latest.json
  data/latest.json    31 days of actuals + 7 days of forecasts for NT facilities, rebuilt twice a day
  CNAME               tells GitHub Pages the custom domain
scripts/fetch_gbb.py  pulls the three AEMO CSVs, keeps NT facilities, writes latest.json and the history folders
data/history/         NT-only: every actual day, every published forecast and every connection-point day we have ever fetched
data/raw/             the complete AEMO files (all states) as downloaded, gzipped, one folder per fetch date
.github/workflows/    refresh.yml (fetch on a schedule) and pages.yml (publish the site)
tests/                offline test of the fetcher using fixture CSVs
```

How it stays current: GitHub Actions runs `scripts/fetch_gbb.py` at 13:00 and 17:00 ACST every day
(AEMO publishes actuals around midday the day after the gas day), commits any change, and GitHub Pages
republishes the site. "Run workflow" on the Refresh AEMO data action refreshes on demand.

Data notes
- Facility ids and zones are AEMO's; the map's names, positions and layer rules live in the Facility Register workbook
  (`NT_Gas_Flows_Facility_Register_*.xlsx`) — change the map there, then in `site/index.html`.
- NGP's Mount Isa row is State = QLD (location 590001) — the fetcher filters by facility id, never by state.
- Zero flow is not missing data: a facility is "not reported" only when its row is absent for a gas day.
- Forecasts are stored per issue date (`data/history/forecast/issued-YYYY-MM-DD.json`) so forecast-vs-actual can be built later (backlog B-001).
- Connection-point flows are stored per gas day (`data/history/connection/`) for the trunk segment flows (backlog B-003); not drawn yet.

Attribution: data © AEMO, reproduced with acknowledgement. NTGB is independent and not affiliated with AEMO or the Northern Territory Government.
