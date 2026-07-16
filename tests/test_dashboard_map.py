import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DashboardMapContractTests(unittest.TestCase):
    def _run_node(self, source: str) -> None:
        completed = subprocess.run(
            ["node", "-e", source],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            completed.returncode,
            0,
            f"node map contract test failed:\n{completed.stdout}\n{completed.stderr}",
        )

    def test_map_scripts_markup_and_offline_contract_are_present(self) -> None:
        index = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        map_source = (ROOT / "web" / "map.js").read_text(encoding="utf-8")

        self.assertLess(index.index("./location.js"), index.index("./map.js"))
        self.assertLess(index.index("./map.js"), index.index("./horizon.js"))
        self.assertLess(index.index("./horizon.js"), index.index("./app.js"))
        for element_id in (
            "battle-map",
            "map-marker-layer",
            "map-window-select",
            "map-domain-select",
            "map-layer-select",
            "map-confidence-select",
            "map-location-status-select",
            "map-summary",
            "map-cluster-panel",
        ):
            self.assertIn(f'id="{element_id}"', index)
        self.assertIn("mapContract.createBattleMap", app)
        self.assertIn("state.battleMap.update", app)
        self.assertIn(
            "horizonContract.eventAvailabilityYear(selectedEvent) === state.selectedYear",
            app,
        )
        self.assertIn("Past 25 years", index)
        self.assertIn("All through selected year", index)
        self.assertNotIn("Selected year &plusmn;", index)
        self.assertIn("elements.eventDetail.focus({ preventScroll: true })", app)
        self.assertIn("participantText", map_source)
        self.assertIn("Elo Δ", map_source)
        self.assertIn("map-cluster-event-outcome", map_source)
        self.assertIn("pendingFocusEventId = cluster.events[0].id", map_source)
        self.assertIn("buttons[focusIndex].focus()", map_source)
        self.assertIn('const button = element("button"', map_source)
        self.assertIn('addEventListener("focus"', map_source)
        self.assertNotIn("L.map", app + map_source)
        self.assertNotIn("mapbox", (app + map_source).lower())
        self.assertNotIn("openstreetmap", (app + map_source).lower())
        self.assertNotIn("fetch(", map_source)

    def test_projection_time_layer_and_confidence_boundaries(self) -> None:
        self._run_node(
            r"""
const assert = require('node:assert/strict');
const map = require('./web/map.js');

assert.equal(map.eventLayer('engagement'), 'tactical');
assert.equal(map.eventLayer({type: 'campaign'}), 'operational');
assert.equal(map.eventLayer({event_type: 'war'}), 'strategic');
assert.equal(map.confidenceBand(0.549999), 'low');
assert.equal(map.confidenceBand(0.55), 'medium');
assert.equal(map.confidenceBand(0.799999), 'medium');
assert.equal(map.confidenceBand(0.8), 'high');
assert.equal(map.confidenceBand(null), 'unknown');

assert.deepEqual(map.timeWindow(-500, 'year'), {start: -500, end: -500});
assert.deepEqual(map.timeWindow(-500, '25'), {start: -525, end: -500});
assert.deepEqual(map.timeWindow(1900, 'all'), {start: -Infinity, end: 1900});
assert.equal(map.eventOverlapsWindow({year: -510, end_year: -490}, map.timeWindow(-500, 'year')), false);
assert.equal(map.eventOverlapsWindow({year: -510, end_year: -500}, map.timeWindow(-500, 'year')), true);
assert.equal(map.eventOverlapsWindow({year: -530, end_year: -520}, map.timeWindow(-500, '5')), false);
assert.equal(map.eventOverlapsWindow({year: 1949, end_year: 1955}, map.timeWindow(1950, 'all')), false);

assert.deepEqual(
  map.projectEquirectangular([0, 0], 1000, 500, {zoom: 1, centerX: 0.5, centerY: 0.5}),
  {x: 500, y: 250},
);
assert.deepEqual(
  map.projectEquirectangular([-180, 90], 1000, 500, {zoom: 1, centerX: 0.5, centerY: 0.5}),
  {x: 0, y: 0},
);
assert.deepEqual(
  map.projectEquirectangular([180, -90], 1000, 500, {zoom: 1, centerX: 0.5, centerY: 0.5}),
  {x: 1000, y: 500},
);
assert.equal(map.projectEquirectangular([181, 0], 1000, 500, {}), null);
"""
        )

    def test_map_index_fails_closed_and_never_geocodes_labels(self) -> None:
        self._run_node(
            r"""
const assert = require('node:assert/strict');
const map = require('./web/map.js');

const provenance = {
  source_id: 'hced_dataset',
  source_record_id: 'ExactRecord',
  assertion_status: 'unreviewed_source_assertion',
  coordinate_precision: 'unknown',
};
const base = {
  id: 'event-1',
  name: 'Safe battle',
  year: 1900,
  end_year: 1900,
  type: 'engagement',
  domain: 'land',
  confidence: 0.61,
  participants: [],
  hced_candidate_id: 'hced-ExactRecord-1',
  source_ids: ['hced_dataset'],
  modern_location_country: 'Source jurisdiction label',
  geometry: {type: 'Point', coordinates: [10, 20]},
  location_provenance: provenance,
};
assert.equal(map.createMapIndex([base]).length, 1);

const invalidCountry = map.safeMapEvent({...base, id: 'invalid-country', modern_location_country: ' private '});
assert.ok(invalidCountry);
assert.equal(Object.hasOwn(invalidCountry, 'modern_location_country'), false);

const rejected = [
  {...base, id: 'no-point', geometry: undefined},
  {...base, id: 'country-only', geometry: undefined, modern_location_country: 'France'},
  {...base, id: 'sentinel', geometry: {type: 'Point', coordinates: [0, 0]}},
  {...base, id: 'open-geometry', geometry: {type: 'Point', coordinates: [10, 20], quarantine_reason: 'private'}},
  {...base, id: 'wrong-source', source_ids: ['other_source']},
  {...base, id: 'missing-candidate', hced_candidate_id: undefined},
  {...base, id: 'open-provenance', location_provenance: {...provenance, reason: 'private'}},
  {...base, id: 'invented-verified-status', location_provenance: {...provenance, assertion_status: 'verified'}},
  {id: 'new-unmapped-promotion', name: 'New promotion', year: 2001, end_year: 2001, type: 'war', modern_location_country: 'Somewhere'},
];
for (const event of rejected) assert.equal(map.safeMapEvent(event), null, event.id);
assert.deepEqual(map.createMapIndex(rejected), []);
"""
        )

    def test_filters_and_clustering_are_deterministic(self) -> None:
        self._run_node(
            r"""
const assert = require('node:assert/strict');
const map = require('./web/map.js');
const provenance = (id) => ({
  source_id: 'hced_dataset', source_record_id: id,
  assertion_status: 'unreviewed_source_assertion', coordinate_precision: 'unknown',
});
const event = (id, year, coordinates, domain = 'land', confidence = 0.61) => ({
  id, name: id, year, end_year: year, type: 'engagement', domain, confidence,
  participants: [], hced_candidate_id: `hced-${id}-1`, source_ids: ['hced_dataset'],
  geometry: {type: 'Point', coordinates}, location_provenance: provenance(id),
});
const raw = [
  event('a', 1900, [10, 20]),
  event('b', 1901, [10, 20]),
  event('c', 1940, [120, -20], 'naval', 0.81),
];
const index = map.createMapIndex(raw);
assert.deepEqual(index.map((row) => row.id), ['a', 'b', 'c']);
assert.deepEqual(
  map.filterMapEvents(index, {selectedYear: 1900, window: '5', domain: 'all', layer: 'all', confidence: 'all', locationStatus: 'all'}).map((row) => row.id),
  ['a'],
);
assert.deepEqual(
  map.filterMapEvents(index, {selectedYear: 1900, window: 'all', domain: 'naval', layer: 'tactical', confidence: 'high', locationStatus: 'unreviewed_source_assertion'}).map((row) => row.id),
  [],
);
assert.deepEqual(
  map.filterMapEvents(index, {selectedYear: 1950, window: 'all', domain: 'naval', layer: 'tactical', confidence: 'high', locationStatus: 'unreviewed_source_assertion'}).map((row) => row.id),
  ['c'],
);
assert.deepEqual(
  map.filterMapEvents(index, {selectedYear: 1900, window: 'all', domain: 'all', layer: 'operational', confidence: 'all', locationStatus: 'all'}),
  [],
);

const options = {width: 1000, height: 500, cellSize: 44, view: {zoom: 1, centerX: 0.5, centerY: 0.5}};
const forward = map.clusterEvents(index, options).map((cluster) => ({key: cluster.key, ids: cluster.events.map((row) => row.id)}));
const reverse = map.clusterEvents([...index].reverse(), options).map((cluster) => ({key: cluster.key, ids: cluster.events.map((row) => row.id)}));
assert.deepEqual(forward, reverse);
assert.equal(forward.length, 2);
assert.deepEqual(forward.find((cluster) => cluster.ids.includes('a')).ids, ['a', 'b']);
"""
        )

    def test_real_dashboard_exposes_only_the_published_point_projection(self) -> None:
        self._run_node(
            r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const map = require('./web/map.js');
const results = JSON.parse(fs.readFileSync('./web/data/results.json', 'utf8'));
const index = map.createMapIndex(results.events);
assert.equal(index.length, results.registry.coverage.hced_location_assertions.geojson_points);
assert.equal(index.every((event) => event.geometry && event.location_provenance), true);
assert.equal(index.every((event) => event.location_status === 'unreviewed_source_assertion'), true);
assert.equal(index.every((event) => event.layer === 'tactical'), true);
assert.equal(index.every((event) => event.participants.every((participant) => typeof participant.delta === 'number')), true);

const ids = new Set(index.map((event) => event.id));
assert.equal(ids.has('hced_label_hced_focchies1649_1'), false);
assert.equal(ids.has('hced_label_hced_amadiye1973_1'), true);
assert.equal(ids.has('hced_hced_atlantic1915_1917_1'), true);
assert.equal(index.find((event) => event.id === 'hced_label_hced_amadiye1973_1').modern_location_country, undefined);
assert.equal(index.find((event) => event.id === 'hced_hced_atlantic1915_1917_1').modern_location_country, undefined);
"""
        )


if __name__ == "__main__":
    unittest.main()
