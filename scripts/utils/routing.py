from datetime import datetime

ARRIVAL_START = (7, 0)   # 07:00
ARRIVAL_END   = (10, 0)  # 10:00

def minutes(hhmm):
    h, m = hhmm.split(':')
    return int(h) * 60 + int(m)

def duration_minutes(dep, arr):
    d = minutes(arr) - minutes(dep)
    if d < 0:
        d += 24 * 60
    return d

def in_arrival_window(arrival_hhmm, start=ARRIVAL_START, end=ARRIVAL_END):
    a = minutes(arrival_hhmm)
    s = start[0]*60 + start[1]
    e = end[0]*60 + end[1]
    return s <= a <= e

def slot_index_for_arrival(arrival_hhmm):
    # 30 perces szeletek: [07:00-07:30), [07:30-08:00), ..., [09:30-10:00]
    a = minutes(arrival_hhmm)
    edges = [7*60, 7*60+30, 8*60, 8*60+30, 9*60, 9*60+30, 10*60]
    for i in range(len(edges)-1):
        if edges[i] <= a <= edges[i+1]:
            return i
    return None

def compute_best_per_origin(connections):
    # connections: list of dict {origin_name, departure_time, arrival_time, transfer_count}
    by_origin = {}
    for c in connections:
        by_origin.setdefault(c['origin_name'], []).append(c)

    results = {}
    for origin, trips in by_origin.items():
        # Filter only trips arriving in window
        valid = [t for t in trips if in_arrival_window(t['arrival_time'])]
        if not valid:
            results[origin] = {
                'origin_name': origin,
                'reachable': False,
                'best_trip': None,
                'best_duration': None,
                'best_transfer_count': None,
                'time_slots': []
            }
            continue

        # Compute durations
        for t in valid:
            t['duration'] = duration_minutes(t['departure_time'], t['arrival_time'])

        # Best (min duration)
        best = min(valid, key=lambda x: (x['duration'], x['transfer_count']))
        time_slots = [None]*6  # 6 half-hour slots between 07:00 and 10:00
        for t in valid:
            idx = slot_index_for_arrival(t['arrival_time'])
            if idx is None:
                continue
            cur = time_slots[idx]
            if cur is None or (t['duration'], t['transfer_count']) < (cur['duration'], cur['transfer_count']):
                time_slots[idx] = t

        results[origin] = {
            'origin_name': origin,
            'reachable': True,
            'best_trip': {
                'departure_time': best['departure_time'],
                'arrival_time': best['arrival_time'],
                'duration_minutes': best['duration'],
                'transfer_count': int(best['transfer_count']),
            },
            'best_duration': best['duration'],
            'best_transfer_count': int(best['transfer_count']),
            'time_slots': [
                ({
                    'departure_time': t['departure_time'],
                    'arrival_time': t['arrival_time'],
                    'duration_minutes': t['duration'],
                    'transfer_count': int(t['transfer_count'])
                } if t else None) for t in time_slots
            ]
        }
    return results
