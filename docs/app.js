const MAP_CENTER = [46.05, 18.25]; // Baranya középvonal környéke
const SLOTS = [
  '07:00–07:30',
  '07:30–08:00',
  '08:00–08:30',
  '08:30–09:00',
  '09:00–09:30',
  '09:30–10:00',
];

let map, layer, data;
let metric = 'duration';
let slotIndex = 0;

function init() {
  map = L.map('map').setView(MAP_CENTER, 9);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  fetch('data/baranya_travel_times.geojson')
    .then(r => r.json())
    .then(geo => {
      data = geo;
      layer = L.geoJSON(geo, {
        pointToLayer: (feature, latlng) => L.circleMarker(latlng, styleFor(feature)),
        onEachFeature: (feature, lyr) => {
          lyr.bindPopup(popupHtml(feature));
        }
      }).addTo(map);
      updateLegend();
    });

  document.querySelectorAll('input[name="metric"]').forEach(el => {
    el.addEventListener('change', (e) => {
      metric = e.target.value;
      redraw();
      updateLegend();
    });
  });

  const slider = document.getElementById('slot-slider');
  slider.addEventListener('input', (e) => {
    slotIndex = parseInt(e.target.value, 10);
    document.getElementById('slot-label').textContent = SLOTS[slotIndex];
    redraw();
  });

  // init label
  document.getElementById('slot-label').textContent = SLOTS[slotIndex];
}

function redraw() {
  layer.eachLayer(l => {
    const f = l.feature;
    l.setStyle(styleFor(f));
    l.setPopupContent(popupHtml(f));
  });
}

function styleFor(feature) {
  const props = feature.properties || {};
  const slotTrip = (props.time_slots && props.time_slots[slotIndex]) || null;
  const best = props.best_trip || null;
  const reachable = !!props.reachable && (!!slotTrip || !!best);

  let color = '#888888'; // unreachable
  if (reachable) {
    if (metric === 'duration') {
      const dur = (slotTrip && slotTrip.duration_minutes) || (best && best.duration_minutes) || null;
      color = colorForDuration(dur);
    } else {
      const tr = (slotTrip && slotTrip.transfer_count) || (best && best.transfer_count) || null;
      color = colorForTransfers(tr);
    }
  }

  return {
    radius: 7,
    fillColor: color,
    color: '#333',
    weight: 1,
    opacity: 1,
    fillOpacity: 0.9,
  };
}

function colorForDuration(d) {
  if (d == null) return '#cccccc';
  if (d <= 30) return '#2ecc71';    // zöld
  if (d <= 60) return '#f1c40f';    // sárga
  if (d <= 90) return '#e67e22';    // narancs
  return '#e74c3c';                 // piros
}

function colorForTransfers(t) {
  if (t == null) return '#cccccc';
  if (t <= 0) return '#2ecc71';
  if (t === 1) return '#f1c40f';
  if (t === 2) return '#e67e22';
  return '#e74c3c';
}

function popupHtml(feature) {
  const p = feature.properties || {};
  const slotTrip = (p.time_slots && p.time_slots[slotIndex]) || null;
  const best = p.best_trip || null;

  const choice = slotTrip || best;
  if (!p.reachable || !choice) {
    return `<b>${p.name}</b><br/>Nincs elérhető út 7–10 közötti érkezéssel.`;
  }
  return `
    <b>${p.name}</b><br/>
    <div>Indulás: <b>${choice.departure_time}</b></div>
    <div>Érkezés Pécsre: <b>${choice.arrival_time}</b></div>
    <div>Menetidő: <b>${choice.duration_minutes} perc</b></div>
    <div>Átszállások: <b>${choice.transfer_count}</b></div>
  `;
}

function updateLegend() {
  const el = document.getElementById('legend');
  if (metric === 'duration') {
    el.innerHTML = `
      <div class="item"><span class="swatch" style="background:#2ecc71"></span> 0–30 perc</div>
      <div class="item"><span class="swatch" style="background:#f1c40f"></span> 31–60 perc</div>
      <div class="item"><span class="swatch" style="background:#e67e22"></span> 61–90 perc</div>
      <div class="item"><span class="swatch" style="background:#e74c3c"></span> 90+ perc</div>
      <div class="item"><span class="swatch" style="background:#888"></span> nincs adat / nem elérhető</div>
    `;
  } else {
    el.innerHTML = `
      <div class="item"><span class="swatch" style="background:#2ecc71"></span> 0 átszállás</div>
      <div class="item"><span class="swatch" style="background:#f1c40f"></span> 1 átszállás</div>
      <div class="item"><span class="swatch" style="background:#e67e22"></span> 2 átszállás</div>
      <div class="item"><span class="swatch" style="background:#e74c3c"></span> 3+ átszállás</div>
      <div class="item"><span class="swatch" style="background:#888"></span> nincs adat / nem elérhető</div>
    `;
  }
}

document.addEventListener('DOMContentLoaded', init);
