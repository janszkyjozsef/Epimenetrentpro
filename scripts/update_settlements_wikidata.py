#!/usr/bin/env python3
"""Fetch every settlement that belongs to Baranya County from Wikidata.

The script queries the public Wikidata SPARQL endpoint, extracts the
settlement name (Hungarian label) and its centroid coordinates, then writes
`data_raw/baranya_telepulesek.csv` in the format expected by the processing
pipeline.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data_raw"
OUT_CSV = RAW_DIR / "baranya_telepulesek.csv"
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "Epimenetrentpro/1.0 (https://github.com/user/project)"

BARANYA_QID = "Q188521"  # Wikidata identifier for Baranya megye
SETTLEMENT_QID = "Q486972"  # human settlement

SPARQL_QUERY = f"""
SELECT ?item ?itemLabel ?coord WHERE {{
  ?item wdt:P31/wdt:P279* wd:{SETTLEMENT_QID};
        wdt:P131 wd:{BARANYA_QID}.
  OPTIONAL {{ ?item wdt:P625 ?coord. }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "hu,en". }}
}}
ORDER BY ?itemLabel
"""


def fetch_settlements() -> List[Dict[str, str]]:
    params = urlencode({"format": "json", "query": SPARQL_QUERY})
    req = Request(f"{SPARQL_ENDPOINT}?{params}")
    req.add_header("User-Agent", USER_AGENT)
    try:
        with urlopen(req) as resp:
            payload = json.loads(resp.read())
    except HTTPError as exc:
        raise RuntimeError(
            f"Wikidata request failed with HTTP {exc.code}: {exc.reason}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(
            "Could not reach Wikidata. Check your internet connection/proxy settings."
        ) from exc
    return payload["results"]["bindings"]


def parse_point(wkt: str) -> Tuple[float, float]:
    if not wkt.startswith("Point(") or not wkt.endswith(")"):
        raise ValueError(f"Unexpected WKT point: {wkt}")
    lon_str, lat_str = wkt[6:-1].split(" ", 1)
    return float(lat_str), float(lon_str)


def normalize_label(label: str) -> str:
    return label.strip()


def filter_valid_rows(rows: Iterable[Dict[str, str]]):
    for row in rows:
        label = normalize_label(row.get("itemLabel", {}).get("value", ""))
        coord = row.get("coord", {}).get("value")
        if not label or coord is None:
            continue
        lat, lon = parse_point(coord)
        if math.isfinite(lat) and math.isfinite(lon):
            yield {"name": label, "lat": lat, "lon": lon}


def write_csv(entries: List[Dict[str, float]]):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["telepules_id", "telepules_nev", "lat", "lon"])
        for idx, entry in enumerate(entries, start=1):
            writer.writerow([idx, entry["name"], f"{entry['lat']:.6f}", f"{entry['lon']:.6f}"])


def main():
    bindings = fetch_settlements()
    entries = sorted(filter_valid_rows(bindings), key=lambda r: r["name"])
    write_csv(entries)
    print(f"Wrote {len(entries)} settlements to {OUT_CSV.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
