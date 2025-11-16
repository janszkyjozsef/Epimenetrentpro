import os, csv, glob
from utils.parsing import parse_menetrend_html_file

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = os.path.join(BASE, 'data_raw')
EXPORTS = os.path.join(RAW, 'menetrendek_exports')
CONN = os.path.join(RAW, 'connections.csv')

def main():
    files = glob.glob(os.path.join(EXPORTS, '*.html'))
    if not files:
        print('Nincs HTML export a data_raw/menetrendek_exports mappában.')
        return

    rows = []
    for fp in files:
        rows.extend(parse_menetrend_html_file(fp))

    if not rows:
        print('Nem sikerült adatsort kinyerni. Ellenőrizd a HTML fájlokat vagy használd a CSV-sablont.')
        return

    # Append to connections.csv, creating file if needed
    header = ['origin_name','departure_time','arrival_time','transfer_count']
    exists = os.path.exists(CONN)
    with open(CONN, 'a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=header)
        if not exists:
            w.writeheader()
        for r in rows:
            w.writerow({
                'origin_name': r['origin_name'],
                'departure_time': r['departure_time'],
                'arrival_time': r['arrival_time'],
                'transfer_count': r['transfer_count'],
            })
    print(f'OK: {len(rows)} sor hozzáadva a connections.csv-hez.')

if __name__ == '__main__':
    main()
