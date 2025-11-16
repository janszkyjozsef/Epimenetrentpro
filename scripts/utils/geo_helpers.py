import csv

def load_settlements(path):
    settlements = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            s = {
                "id": int(row.get("telepules_id") or 0),
                "name": row["telepules_nev"],
                "lat": float(row["lat"]),
                "lon": float(row["lon"]),
            }
            settlements.append(s)
    return settlements

def to_geojson(settlements, stats_by_name):
    features = []
    for st in settlements:
        s_stats = stats_by_name.get(st["name"], {})
        props = {
            "name": st["name"],
            "reachable": s_stats.get("reachable", False),
            "best_trip": s_stats.get("best_trip"),
            "time_slots": s_stats.get("time_slots", []),
            "best_duration": s_stats.get("best_duration"),
            "best_transfer_count": s_stats.get("best_transfer_count"),
        }
        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [st["lon"], st["lat"]]},
            "properties": props
        }
        features.append(feature)
    return {"type": "FeatureCollection", "features": features}
