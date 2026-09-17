#!/usr/bin/env python3
"""Fetch AEMO Gas Bulletin Board files and build the NTGB public data set.

Runs on a schedule (GitHub Actions) or by hand:  python scripts/fetch_gbb.py
Outputs:
  site/data/latest.json                       what the map reads: {actual, forecast, lastUpdated, fetchedAt}
  data/history/actual/<gasday>.json           every NT actual row ever seen, one file per gas day (overwritten on revision)
  data/history/forecast/issued-<date>.json    the full 7-day forecast as published on each fetch day (B-001: forecast history)
  data/history/connection/<gasday>.json       NT connection-point flows per gas day (B-003: segment flows, stored now, drawn later)
  data/raw/<fetchdate>/<file>.csv.gz          the complete AEMO files as downloaded — every state, every facility — for later use

Only NT facilities (ids in FACILITY_IDS) are kept. NGP's Mount Isa row is State = QLD, so filter by facility id, never by state.
No third-party packages: standard library only.
"""
import csv, gzip, io, json, os, sys, urllib.request
from datetime import datetime, timezone, timedelta

BASE = "https://nemweb.com.au/Reports/Current/GBB/"
FILES = {
    "actual": "GasBBActualFlowStorageLast31.CSV",
    "forecast": "GasBBNominationAndForecastNext7.CSV",
    "connection": "GasBBPipelineConnectionFlowLast31.CSV",
}
# NT facility ids as published by AEMO (see the Facility Register workbook — Facilities sheet)
FACILITY_IDS = {580010, 580020, 580030, 580040, 580050, 580060, 580070, 580100, 580180,
                580210, 580220, 580231, 580232, 580233, 580234, 580235, 580236, 580237}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DATA = os.path.join(ROOT, "site", "data")
HIST = os.path.join(ROOT, "data", "history")
RAW = os.path.join(ROOT, "data", "raw")


def fetch(name):
    url = BASE + FILES[name]
    req = urllib.request.Request(url, headers={"User-Agent": "NTGB/1.0 (ntgb.com.au)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read().decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(raw)))
    if not rows:
        raise RuntimeError(f"{name}: empty file")
    RAW_TEXT[name] = raw
    return rows


RAW_TEXT = {}


def save_raw(fetch_date):
    """Keep the complete files (all states) so nothing published today is lost when AEMO's window rolls on."""
    d = os.path.join(RAW, fetch_date)
    os.makedirs(d, exist_ok=True)
    for name, text in RAW_TEXT.items():
        with gzip.open(os.path.join(d, FILES[name] + ".gz"), "wt", encoding="utf-8") as g:
            g.write(text)


def num(x):
    try:
        return round(float(x), 3)
    except (TypeError, ValueError):
        return 0.0


def iso_day(s):
    # AEMO writes 2026/09/08 ; be tolerant of 2026-09-08 too
    return s.strip().replace("/", "-")[:10]


def key(row):
    return f"{int(row['FacilityId'])}-{int(row['LocationId'])}"


def shape(rows, date_col):
    """{gasday: {facilityId-locationId: [Demand, Supply, TransferIn, TransferOut]}} for NT facilities."""
    out = {}
    last_updated = ""
    for r in rows:
        try:
            fid = int(r["FacilityId"])
        except (KeyError, ValueError):
            continue
        if fid not in FACILITY_IDS:
            continue
        d = iso_day(r[date_col])
        out.setdefault(d, {})[key(r)] = [num(r["Demand"]), num(r["Supply"]), num(r["TransferIn"]), num(r["TransferOut"])]
        lu = r.get("LastUpdated", "")
        if lu > last_updated:
            last_updated = lu
    return out, last_updated


def shape_connection(rows):
    out = {}
    for r in rows:
        try:
            fid = int(r["FacilityId"])
        except (KeyError, ValueError):
            continue
        if fid not in FACILITY_IDS:
            continue
        d = iso_day(r["GasDate"])
        out.setdefault(d, []).append({
            "facilityId": fid,
            "pointId": int(r["ConnectionPointId"]),
            "point": r["ConnectionPointName"],
            "direction": r["FlowDirection"],
            "locationId": int(r["LocationId"]),
            "qty": num(r["ActualQuantity"]),
            "quality": r.get("Quality", ""),
        })
    return out


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, separators=(",", ":"), sort_keys=True)


def main():
    actual_rows = fetch("actual")
    forecast_rows = fetch("forecast")
    connection_rows = fetch("connection")

    actual, lu_a = shape(actual_rows, "GasDate")
    forecast, lu_f = shape(forecast_rows, "Gasdate" if "Gasdate" in forecast_rows[0] else "GasDate")
    connection = shape_connection(connection_rows)

    if not actual:
        raise RuntimeError("no NT rows in the actuals file — not writing anything")

    now = datetime.now(timezone(timedelta(hours=9, minutes=30)))  # ACST
    latest = {
        "actual": actual,
        "forecast": forecast,
        "lastUpdated": (max(lu_a, lu_f) or "")[:16].replace("/", "-"),
        "fetchedAt": now.strftime("%Y-%m-%d %H:%M ACST"),
    }
    write_json(os.path.join(SITE_DATA, "latest.json"), latest)
    save_raw(now.strftime("%Y-%m-%d"))

    for d, rows in actual.items():
        write_json(os.path.join(HIST, "actual", f"{d}.json"), rows)
    write_json(os.path.join(HIST, "forecast", f"issued-{now.strftime('%Y-%m-%d')}.json"), forecast)
    for d, rows in connection.items():
        write_json(os.path.join(HIST, "connection", f"{d}.json"), rows)

    print(f"ok: raw files saved for every state; {len(actual)} NT actual days, {len(forecast)} forecast days, {len(connection)} connection days; last AEMO update {latest['lastUpdated']}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # a failed fetch must not blank the site: latest.json is only rewritten on success
        print(f"FAILED: {e}", file=sys.stderr)
        sys.exit(1)
