let geojson;
let highlightedLayer = null;

// Initialize map
var map = L.map('map', {
    minZoom: 9.5,
    maxZoom: 16
})

// Restrict panning/zooming tightly to NYC metro (boroughs + NJ waterfront)
var bounds = L.latLngBounds(
    L.latLng(40.40, -74.45),  // SW: southern Staten Island / central NJ
    L.latLng(40.95, -73.65)   // NE: northern Bronx / eastern Queens
);
map.setMaxBounds(bounds);
map.fitBounds(bounds);
map.on('drag', function() {
    map.panInsideBounds(bounds, { animate: false });
});

// Add tile layer
L.tileLayer('https://api.maptiler.com/maps/openstreetmap/{z}/{x}/{y}.jpg?key=PomQwQ81LXSQaSTsapyk', {
    attribution: '<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap contributors</a>'
}).addTo(map);


// ── Field definitions ──────────────────────────────────────────────────────────
// Each field has: label, color ramp (low→high), breakpoints, and a formatter

const fieldConfig = {
    median_gross_rent: {
        label: "Median Gross Rent",
        colors: ['#FDDDBB', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026'],
        breaks: [2000, 2500, 3000, 3500, 4000],
        format: v => v != null ? `$${Number(v).toLocaleString()}` : 'N/A'
    },
    median_household_income: {
        label: "Median Household Income",
        colors: ['#FDDDBB', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026'],
        breaks: [40000, 60000, 80000, 100000, 130000],
        format: v => v != null ? `$${Number(v).toLocaleString()}` : 'N/A'
    },
    total_population: {
        label: "Total Population",
        colors: ['#FDDDBB', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026'],
        breaks: [5000, 10000, 20000, 35000, 50000],
        format: v => v != null ? Number(v).toLocaleString() : 'N/A'
    },
    housing_units_total: {
        label: "Total Housing Units",
        colors: ['#FDDDBB', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026'],
        breaks: [2000, 4000, 7000, 11000, 16000],
        format: v => v != null ? Number(v).toLocaleString() : 'N/A'
    },
    renter_occupied_units: {
        label: "Renter Occupied Units",
        colors: ['#FDDDBB', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026'],
        breaks: [500, 1500, 3000, 5000, 8000],
        format: v => v != null ? Number(v).toLocaleString() : 'N/A'
    },
    owner_occupied_units: {
        label: "Owner Occupied Units",
        colors: ['#FDDDBB', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026'],
        breaks: [500, 1500, 3000, 5000, 8000],
        format: v => v != null ? Number(v).toLocaleString() : 'N/A'
    },
    rent_50pct_or_more_income: {
        label: "Rent ≥ 50% Income",
        colors: ['#FDDDBB', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026'],
        breaks: [100, 300, 600, 1000, 1500],
        format: v => v != null ? Number(v).toLocaleString() : 'N/A'
    }
};

// Active color field (default)
let activeColorField = 'median_gross_rent';

// ── Color helpers ──────────────────────────────────────────────────────────────
function getColor(value, field) {
    const cfg = fieldConfig[field];
    if (value == null) return '#ccc';
    for (let i = cfg.breaks.length - 1; i >= 0; i--) {
        if (value >= cfg.breaks[i]) return cfg.colors[i + 1];
    }
    return cfg.colors[0];
}

function style(feature) {
    return {
        fillColor: getColor(feature.properties[activeColorField], activeColorField),
        weight: 1,
        color: 'white',
        fillOpacity: 0.7
    };
}

function highlightFeature(e) {
    const layer = e.target;

    if (highlightedLayer && highlightedLayer !== layer) {
        geojson.resetStyle(highlightedLayer);
    }

    layer.setStyle({
        weight: 3,
        color: '#666',
        fillOpacity: 0.9
    });

    layer.bringToFront();
    highlightedLayer = layer;
}

function resetHighlight(e) {
    geojson.resetStyle(e.target);
    highlightedLayer = null;
}

// ── Tooltip ────────────────────────────────────────────────────────────────────
let selectedFields = new Set();

function buildTooltipContent(properties) {
    // Determine the "ID" dynamically
    let idLabel, idValue;
    if ("GEOID20" in properties) {
        idLabel = "ZIP";
        idValue = properties["GEOID20"];
    } else if ("BoroName" in properties) {
        idLabel = "Borough";
        idValue = properties["BoroName"];
    } else {
        idLabel = "ID";
        idValue = "N/A";
    }

    let content = `<strong>${idLabel}: ${idValue}</strong><br>`;

    selectedFields.forEach(field => {
        const cfg = fieldConfig[field];
        content += `${cfg.label}: ${cfg.format(properties[field])}<br>`;
    });

    return content;
}

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        mousemove: function() {
            layer.bindTooltip(buildTooltipContent(feature.properties), { sticky: true }).openTooltip();
        }
    });
}

// ── Legend (dynamic) ───────────────────────────────────────────────────────────
var legendControl = L.control({ position: 'bottomleft' });
var legendDiv;

function getNiceStep(min, max, steps = 6) {
    const range = max - min;
    const roughStep = range / steps;

    const magnitude = Math.pow(10, Math.floor(Math.log10(roughStep)));
    const residual = roughStep / magnitude;

    let niceResidual;
    if (residual >= 5) niceResidual = 10;
    else if (residual >= 2) niceResidual = 5;
    else if (residual >= 1) niceResidual = 2;
    else niceResidual = 1;

    return niceResidual * magnitude;
}

function computeDynamicBreaks(field) {
    if (!geojson) return;

    const values = [];
    geojson.eachLayer(layer => {
        const num = Number(layer.feature.properties[field]);
        if (!isNaN(num)) values.push(num);
    });

    if (values.length === 0) return;

    const min = Math.min(...values);
    const max = Math.max(...values);

    if (min === max) {
        fieldConfig[field].breaks = [min];
        return;
    }

    const step = getNiceStep(min, max, 6);
    const niceMin = Math.floor(min / step) * step;
    const niceMax = Math.ceil(max / step) * step;

    const breaks = [];
    for (let v = niceMin + step; v < niceMax; v += step) {
        breaks.push(v);
    }

    fieldConfig[field].breaks = breaks;
}

function updateLegend() {
    if (!legendDiv) return;

    const cfg = fieldConfig[activeColorField];
    const breaks = cfg.breaks;
    const colors = cfg.colors;

    let items = '';

    for (let i = 0; i <= breaks.length; i++) {
        let label;

        if (i === 0) {
            label = `&le; ${cfg.format(breaks[0])}`;
        } else if (i === breaks.length) {
            label = `&gt; ${cfg.format(breaks[breaks.length - 1])}`;
        } else {
            label = `${cfg.format(breaks[i - 1])} &ndash; ${cfg.format(breaks[i])}`;
        }

        const color = colors[i] || colors[colors.length - 1];

        items = `
            <div class="legend-item">
                <span class="legend-swatch" style="background:${color}"></span>
                <span class="legend-label">${label}</span>
            </div>
        ` + items;
    }

    legendDiv.innerHTML = `
        <div class="legend-title">${cfg.label}</div>
        <div class="legend-items">${items}</div>
    `;
}

legendControl.onAdd = function () {
    legendDiv = L.DomUtil.create('div', 'map-legend');
    updateLegend();
    return legendDiv;
};

legendControl.addTo(map);

// ── Re-color map ───────────────────────────────────────────────────────────────
function refreshMapColors() {
    if (!geojson) return;
    geojson.setStyle(style);
    updateLegend();
}

// ── Function to switch GeoJSON ──────────────────────────────────────────────
function loadGeoJSON(url) {
    console.log('Loading GeoJSON from:', url);
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (geojson) {
                map.removeLayer(geojson);
                highlightedLayer = null;
            }

            geojson = L.geoJson(data, {
                style: style,
                onEachFeature: onEachFeature
            }).addTo(map);

            computeDynamicBreaks(activeColorField);
            refreshMapColors();
        })
        .catch(err => console.error('Error loading GeoJSON:', err));
}

// ── Toolbar setup ─────────────────────────────────────────────────────────────
const toolbar = document.getElementById("toolbar");

// Divider
const divider4 = document.createElement("div");
divider4.className = "toolbar-divider";
toolbar.appendChild(divider4);

// ── Search Section ──
const searchSection = document.createElement("div");
searchSection.className = "toolbar-section";
searchSection.innerHTML = `<div class="toolbar-section-title">Search by ID</div>
<input type="text" id="searchInput" placeholder="Enter ID" style="width: 100%; padding: 4px;">`;
toolbar.appendChild(searchSection);

// Divider
const divider0 = document.createElement("div");
divider0.className = "toolbar-divider";
toolbar.appendChild(divider0);

// ── Region Selector Section ──
const geojsonSection = document.createElement("div");
geojsonSection.className = "toolbar-section";
geojsonSection.innerHTML = `<div class="toolbar-section-title">Select Region</div>`;

const geojsonFiles = {
    'Boroughs': '../datasets/final-usables/merged_nyc_county.geojson',
    'ZIP Codes': '../datasets/final-usables/merged_nyc_zcta.geojson'
};

Object.entries(geojsonFiles).forEach(([labelText, url], idx) => {
    const label = document.createElement("label");
    label.className = "radio-label";
    label.innerHTML = `
        <input type="radio" name="geojsonFile" value="${url}" ${idx === 0 ? 'checked' : ''}>
        ${labelText}
    `;
    geojsonSection.appendChild(label);
});

toolbar.appendChild(geojsonSection);

// Divider
const divider2 = document.createElement("div");
divider2.className = "toolbar-divider";
toolbar.appendChild(divider2);

// ── Color Map By Section ──
const colorBySection = document.createElement("div");
colorBySection.className = "toolbar-section";
colorBySection.innerHTML = `<div class="toolbar-section-title">Color Map By</div>`;

Object.entries(fieldConfig).forEach(([key, cfg]) => {
    const label = document.createElement("label");
    label.className = "radio-label";
    label.innerHTML = `
        <input type="radio" name="colorBy" value="${key}" ${key === activeColorField ? 'checked' : ''}>
        ${cfg.label}
    `;
    colorBySection.appendChild(label);
});

toolbar.appendChild(colorBySection);

// Divider
const divider1 = document.createElement("div");
divider1.className = "toolbar-divider";
toolbar.appendChild(divider1);

// ── Tooltip Fields Section ──
const tooltipSection = document.createElement("div");
tooltipSection.className = "toolbar-section";
tooltipSection.innerHTML = `<div class="toolbar-section-title">Show in Tooltip</div>`;

// Select All checkbox
const selectAllLabel = document.createElement("label");
selectAllLabel.className = "checkbox-label";
selectAllLabel.innerHTML = `<input type="checkbox" id="selectAll"> <strong>Select All</strong>`;
tooltipSection.appendChild(selectAllLabel);

// Individual field checkboxes
Object.entries(fieldConfig).forEach(([key, cfg]) => {
    const label = document.createElement("label");
    label.className = "checkbox-label";
    label.innerHTML = `<input type="checkbox" value="${key}"> ${cfg.label}`;
    tooltipSection.appendChild(label);
});

toolbar.appendChild(tooltipSection);

// Divider
const divider3 = document.createElement("div");
divider3.className = "toolbar-divider";
toolbar.appendChild(divider3);

// ── Export Section ──
const exportSection = document.createElement("div");
exportSection.className = "toolbar-section";
exportSection.innerHTML = `<div class="toolbar-section-title">Export Data</div>`;

// Export CSV button
const exportCSVBtn = document.createElement("button");
exportCSVBtn.textContent = "Export CSV";
exportCSVBtn.style.cursor = "pointer";
exportCSVBtn.style.marginBottom = "5px";
exportSection.appendChild(exportCSVBtn);

// Export GeoJSON button
const exportGeoJSONBtn = document.createElement("button");
exportGeoJSONBtn.textContent = "Export GeoJSON";
exportGeoJSONBtn.style.cursor = "pointer";
exportSection.appendChild(exportGeoJSONBtn);

toolbar.appendChild(exportSection);

// ── Wire up Color Map radios ──
document.querySelectorAll('input[name="colorBy"]').forEach(radio => {
    radio.addEventListener('change', () => {
        activeColorField = radio.value;
        computeDynamicBreaks(activeColorField);
        refreshMapColors();
    });
});

// ── Wire up Tooltip checkboxes ──
const checkboxes = document.querySelectorAll('#toolbar input[type="checkbox"]:not(#selectAll)');
const selectAll = document.getElementById("selectAll");

// Automatically check all boxes and populate selectedFields on load
checkboxes.forEach(cb => {
    cb.checked = true;           // check the box
    selectedFields.add(cb.value); // add to selectedFields
});
selectAll.checked = true;         // check "Select All"

checkboxes.forEach(cb => {
    cb.addEventListener('change', () => {
        if (cb.checked) selectedFields.add(cb.value);
        else selectedFields.delete(cb.value);
        selectAll.checked = [...checkboxes].every(c => c.checked);
    });
});

selectAll.addEventListener('change', () => {
    checkboxes.forEach(cb => {
        cb.checked = selectAll.checked;
        if (selectAll.checked) selectedFields.add(cb.value);
        else selectedFields.delete(cb.value);
    });
});

// ── Wire up GeoJSON radios ──
document.querySelectorAll('input[name="geojsonFile"]').forEach(radio => {
    radio.addEventListener('change', () => {
        loadGeoJSON(radio.value);
    });
});

// ── Wire up Export Buttons ──
exportCSVBtn.addEventListener("click", () => {
    if (!geojson) return;
    const selected = Array.from(selectedFields);
    if (selected.length === 0) { alert("No fields selected"); return; }

    const rows = geojson.toGeoJSON().features.map(f => {
        const row = { id: f.properties.GEOID20 || f.properties.BoroName || "" };
        selected.forEach(field => row[field] = f.properties[field]);
        return row;
    });

    const csvContent = [Object.keys(rows[0]).join(","), ...rows.map(r => Object.values(r).join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "export.csv";
    link.click();
});

exportGeoJSONBtn.addEventListener("click", () => {
    if (!geojson) return;
    const selected = Array.from(selectedFields);
    const features = geojson.toGeoJSON().features.map(f => {
        const props = { id: f.properties.GEOID20 || f.properties.BoroName || "" };
        selected.forEach(field => props[field] = f.properties[field]);
        return { type: "Feature", geometry: f.geometry, properties: props };
    });
    const geojsonData = JSON.stringify({ type: "FeatureCollection", features: features });
    const blob = new Blob([geojsonData], { type: "application/json;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "export.geojson";
    link.click();
});

// ── Search functionality ──
const searchInput = document.getElementById('searchInput');

if (searchInput) {
    searchInput.addEventListener('input', function(e) {
        const searchId = e.target.value.trim();

        if (highlightedLayer) {
            geojson.resetStyle(highlightedLayer);
            highlightedLayer = null;
        }

        if (!geojson || !searchId) return;

        geojson.eachLayer(layer => {
            const id = layer.feature.properties.GEOID20 
                || layer.feature.properties.BoroName 
                || "";

            if (id.toString().toLowerCase() === searchId.toLowerCase()) {
                layer.setStyle({
                    weight: 3,
                    color: '#ff7800',
                    fillOpacity: 0.9
                });
                highlightedLayer = layer;
                map.fitBounds(layer.getBounds());
            }
        });
    });
}

loadGeoJSON('../datasets/final-usables/merged_nyc_county.geojson');

let scrollTimeout;

toolbar.addEventListener('scroll', () => {
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
        toolbar.scrollTop = 0;  // scroll back to top
    }, 1000); // 1 second after user stops scrolling
});