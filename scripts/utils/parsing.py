import os
import csv
import re
from bs4 import BeautifulSoup

# Canonical CSV reader for connections
def read_connections_csv(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "origin_name": r["origin_name"].strip(),
                "departure_time": r["departure_time"].strip(),
                "arrival_time": r["arrival_time"].strip(),
                "transfer_count": int(r["transfer_count"]),
            })
    return rows

# Experimental HTML parser for Menetrendek.hu exports.
# Tries to find HH:MM times and infer pairs (departure -> arrival) per result block.
# If page structure differs, returns empty list.
TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):[0-5]\d\b")

def parse_menetrend_html_file(html_path, origin_hint=None):
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
    except Exception:
        return []

    soup = BeautifulSoup(html, 'lxml')
    text = soup.get_text(" ", strip=True)
    times = TIME_RE.findall(text)
    # We need pairs like (dep, arr). We'll collect consecutive pairs as a naive fallback.
    # This is intentionally conservative and may over/under-capture.
    results = []
    for i in range(0, len(times) - 1, 2):
        dep = times[i]
        arr = times[i+1]
        # Basic sanity: arrival after departure in minutes, allowing midnight wrap by +24h
        if _minutes(arr) - _minutes(dep) <= -1:
            continue
        results.append({
            "origin_name": origin_hint or _infer_origin_from_filename(os.path.basename(html_path)),
            "departure_time": dep,
            "arrival_time": arr,
            "transfer_count": _infer_transfers_from_text(text),
        })
    return results

def _infer_origin_from_filename(fname):
    # Try "Abaliget_pecs_2025-03-12.html" -> "Abaliget"
    base = fname.lower().replace('.html','')
    parts = re.split(r'[_\-]', base)
    if parts:
        return parts[0].capitalize()
    return "Ismeretlen"

def _infer_transfers_from_text(text):
    # Very naive heuristic: count occurrences of strings that might indicate changes.
    # Better to edit manually in connections.csv if inaccurate.
    hints = ["átszállás", "csatlakozás", "átszáll", "change"]
    count = 0
    for h in hints:
        count += text.lower().count(h)
    # Cap to a reasonable number; if text is long, this could be high.
    if count == 0:
        return 0
    return min(count, 3)

def _minutes(hhmm):
    h, m = hhmm.split(':')
    return int(h) * 60 + int(m)
