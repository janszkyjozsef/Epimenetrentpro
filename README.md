# Baranya → Pécs bejutási idő térkép (7–10 érkezési ablak)

Interaktív, GitHub Pages-en futó térkép, amely településenként megmutatja a **leggyorsabb** közösségi közlekedéses eljutást Pécsre **7:00–10:00 közötti érkezéssel**.  
**Nincs fizetős API**, a frontenden csak a Leaflet + OSM csempék futnak. A menetrendi adatok **Menetrendek.hu** forrásból **kézi exporttal** vagy saját CSV-sablonnal adhatók meg.

## Gyorsindítás (demo adatokkal)

1. Python környezet:
   ```bash
   python -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```
   Windows:
   ```bash
   py -3 -m venv .venv
   .venv\Scripts\pip install -r requirements.txt
   ```

2. Feldolgozás (demo adatból GeoJSON generálás és másolás a `docs/data` alá):
   ```bash
   .venv/bin/python scripts/process_timetables.py
   ```
   Windows:
   ```bash
   .venv\Scripts\python scripts/process_timetables.py
   ```

3. Commit & push GitHubra, majd kapcsold be a **GitHub Pages**-t a repo `docs/` mappájára. A térkép azonnal működik a demó adatokkal.

## Saját adatok (Menetrendek.hu)

A projekt **nem végez automatikus scrapinget**. A Menetrendek.hu szolgáltatási feltételeit tartsd be. Két bevitt adatút támogatott:

### A) CSV-sablon (javasolt és stabil)

1. Nyisd meg a `data_raw/connections.csv` fájlt és kövesd ezt a fejlécet:
   ```csv
   origin_name,departure_time,arrival_time,transfer_count
   ```
   - `origin_name`: Település neve (pl. `Siklós`).
   - `departure_time`: HH:MM (pl. `06:30`).
   - `arrival_time`: HH:MM (pl. `07:15`).
   - `transfer_count`: egész szám (0 = átszállás nélkül).

   Több sor is lehet egy településre (különböző opciók). A feldolgozó kiválasztja **azt az utat**, amely **7:00–10:00 között érkezik** és **a leggyorsabb**.

2. Futtasd újra a feldolgozót (lásd fent).

### B) HTML-export importálása (kísérleti)

1. A Menetrendek.hu útvonal-keresési találati oldalát mentsd le HTML-ként a `data_raw/menetrendek_exports/` mappába (pl. `Abaliget_pecs_2025-03-12.html`).  
2. Futtasd:
   ```bash
   .venv/bin/python scripts/import_menetrendek_html.py
   ```
   Windows:
   ```bash
   .venv\Scripts\python scripts/import_menetrendek_html.py
   ```
   Ez megkísérli kinyerni a találatokból az indulási/érkezési időket és az átszállások számát, majd **hozzáfűzi** a `data_raw/connections.csv`-hez.  
   A HTML struktúra változhat; ha az import nem talál semmit, használd az **A) CSV-sablont**.

## Településlista

A `data_raw/baranya_telepulesek.csv` tartalmazza a települések nevét és koordinátáit. A demóban ~10 település szerepel – éles használathoz szükség van **Baranya összes településére** ugyanebben a formátumban (`telepules_id,telepules_nev,lat,lon`).

### Automatikus frissítés (Wikidata)

1. Futtasd az új segédszkriptet, amely a Wikidata SPARQL végpontról tölti le a teljes listát és felülírja a CSV-t:
   ```bash
   .venv/bin/python scripts/update_settlements_wikidata.py
   ```
   - Internetkapcsolat és a Wikidata elérése szükséges.
   - Ha vállalati proxy mögött futsz, gondoskodj róla, hogy a `https_proxy` / `HTTPS_PROXY` változók helyesen legyenek beállítva.
2. Ezek után futtasd a feldolgozót:
   ```bash
   .venv/bin/python scripts/process_timetables.py
   ```
   A feldolgozó már minden településhez létrehozza a GeoJSON pontot, akkor is, ha nincs hozzá menetrendi adat (ilyenkor `reachable = false`).

## Kimenet

- `data_processed/baranya_travel_times.json` – aggregált adatok
- `data_processed/baranya_travel_times.geojson` – térképi adatok
- Ezek **automatikusan** átmásolódnak a `docs/data/` alá, hogy a GitHub Pages frontenden betölthetők legyenek.

## Színezés és UI

- Váltó: **Menetidő (perc)** vs **Átszállások száma**
- Csúszka: érkezési **idősáv** 7:00–10:00 között (30 perces szeletek).
- Településre kattintva: legjobb opció adatai (indulás, érkezés, menetidő, átszállások).

## Licenc

MIT.
