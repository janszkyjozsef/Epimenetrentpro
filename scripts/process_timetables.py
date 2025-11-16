import os, json, csv, shutil, datetime
from utils.geo_helpers import load_settlements, to_geojson
from utils.parsing import read_connections_csv
from utils.routing import compute_best_per_origin

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = os.path.join(BASE, 'data_raw')
PROC = os.path.join(BASE, 'data_processed')
DOCS_DATA = os.path.join(BASE, 'docs', 'data')

SETTLEMENTS_CSV = os.path.join(RAW, 'baranya_telepulesek.csv')
CONNECTIONS_CSV = os.path.join(RAW, 'connections.csv')

def main():
    settlements = load_settlements(SETTLEMENTS_CSV)
    connections = read_connections_csv(CONNECTIONS_CSV)

    stats_by_origin = compute_best_per_origin(connections)

    # Build full stats list aligned to settlements
    stats_by_name = {}
    for st in settlements:
        s = stats_by_origin.get(st['name'])
        if s is None:
            stats_by_name[st['name']] = {
                'origin_name': st['name'],
                'reachable': False,
                'best_trip': None,
                'best_duration': None,
                'best_transfer_count': None,
                'time_slots': []
            }
        else:
            stats_by_name[st['name']] = s

    # JSON
    out_json = {
        'date': datetime.date.today().isoformat(),
        'arrival_window': {'start': '07:00', 'end': '10:00'},
        'settlements': []
    }
    for st in settlements:
        s = stats_by_name[st['name']]
        out_json['settlements'].append({
            'id': st['id'],
            'name': st['name'],
            'lat': st['lat'],
            'lon': st['lon'],
            'reachable': s['reachable'],
            'best_trip': s['best_trip'],
            'best_duration': s['best_duration'],
            'best_transfer_count': s['best_transfer_count'],
            'time_slots': s['time_slots']
        })

    os.makedirs(PROC, exist_ok=True)
    with open(os.path.join(PROC, 'baranya_travel_times.json'), 'w', encoding='utf-8') as f:
        json.dump(out_json, f, ensure_ascii=False, indent=2)

    # GeoJSON
    geojson = to_geojson(settlements, stats_by_name)
    with open(os.path.join(PROC, 'baranya_travel_times.geojson'), 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False)

    # Copy to docs/data
    os.makedirs(DOCS_DATA, exist_ok=True)
    shutil.copy(os.path.join(PROC, 'baranya_travel_times.json'), os.path.join(DOCS_DATA, 'baranya_travel_times.json'))
    shutil.copy(os.path.join(PROC, 'baranya_travel_times.geojson'), os.path.join(DOCS_DATA, 'baranya_travel_times.geojson'))

    print('OK: data_processed/* generated and copied to docs/data/.')

if __name__ == '__main__':
    main()
