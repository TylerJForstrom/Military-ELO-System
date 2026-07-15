import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DashboardLocationContractTests(unittest.TestCase):
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
            f"node contract test failed:\n{completed.stdout}\n{completed.stderr}",
        )

    def test_strict_normalizer_preserves_exact_contract_and_one_axis_zero(self) -> None:
        self._run_node(
            r"""
const assert = require('node:assert/strict');
const location = require('./web/location.js');
const provenance = {
  source_id: 'hced_dataset',
  source_record_id: 'ExactRecord',
  assertion_status: 'unreviewed_source_assertion',
  coordinate_precision: 'unknown',
};
const normalized = location.normalizeEventLocation({
  hced_candidate_id: 'hced-ExactRecord-1',
  source_ids: ['hced_dataset'],
  modern_location_country: 'Unchanged source label',
  geometry: {type: 'Point', coordinates: [0, 45]},
  location_provenance: provenance,
});
assert.deepEqual(normalized, {
  hced_candidate_id: 'hced-ExactRecord-1',
  modern_location_country: 'Unchanged source label',
  geometry: {type: 'Point', coordinates: [0, 45]},
  location_provenance: provenance,
});
assert.equal(location.formatPoint(normalized.geometry), '[0, 45]');
assert.equal(
  location.LOCATION_WARNING,
  'HCED location fields are unreviewed source assertions. Quarantined values are withheld, not corrected. Coordinate precision is unknown.',
);
"""
        )

    def test_normalizer_rejects_bool_coercion_ranges_and_open_provenance(self) -> None:
        self._run_node(
            r"""
const assert = require('node:assert/strict');
const location = require('./web/location.js');
const valid = {source_id: 'hced_dataset', source_record_id: 'r', assertion_status: 'unreviewed_source_assertion', coordinate_precision: 'unknown'};
for (const geometry of [
  {type: 'Point', coordinates: [true, 2]},
  {type: 'Point', coordinates: ['1', 2]},
  {type: 'Point', coordinates: [181, 2]},
  {type: 'Point', coordinates: [1, 91]},
  {type: 'Point', coordinates: [1, 2, 3]},
  {type: 'Point', coordinates: [1, 2], quarantine_reason: 'must-not-publish'},
  {type: 'Point', coordinates: [1, 2], bbox: [1, 2, 1, 2]},
  {type: 'LineString', coordinates: [[1, 2], [3, 4]]},
]) assert.equal(location.normalizeGeoJsonPoint(geometry), null);
assert.equal(location.normalizeProvenance({...valid, reason: 'must not leak'}), null);
assert.equal(location.normalizeProvenance({...valid, assertion_status: 'verified'}), null);
const withheld = location.normalizeEventLocation({
  hced_candidate_id: 'hced-r-1',
  source_ids: ['hced_dataset'],
  modern_location_country: 'Country',
  geometry: {type: 'Point', coordinates: [1, 2]},
  location_provenance: {...valid, reason: 'must not leak'},
});
assert.deepEqual(withheld, {hced_candidate_id: 'hced-r-1'});
assert.deepEqual(location.normalizeEventLocation({}), {});
assert.deepEqual(location.normalizeEventLocation({
  hced_candidate_id: 'hced-r-1',
  source_ids: ['hced_dataset'],
  geometry: {type: 'Point', coordinates: [1, 2]},
  location_provenance: valid,
}), {
  hced_candidate_id: 'hced-r-1',
  geometry: {type: 'Point', coordinates: [1, 2]},
  location_provenance: valid,
});
for (const source_ids of [undefined, [], ['other_source']]) {
  assert.deepEqual(location.normalizeEventLocation({
    hced_candidate_id: 'hced-r-1',
    source_ids,
    modern_location_country: 'Country',
    geometry: {type: 'Point', coordinates: [1, 2]},
    location_provenance: valid,
  }), {hced_candidate_id: 'hced-r-1'});
}
for (const coordinates of [[0, 0], [-0, 0], [0, -0], [-0, -0]]) {
  assert.deepEqual(location.normalizeEventLocation({
    hced_candidate_id: 'hced-r-1',
    source_ids: ['hced_dataset'],
    geometry: {type: 'Point', coordinates},
    location_provenance: valid,
  }), {hced_candidate_id: 'hced-r-1'});
}
for (const coordinates of [[0, 12], [12, 0], [-180, -90], [180, 90]]) {
  assert.deepEqual(location.normalizeEventLocation({
    hced_candidate_id: 'hced-r-1',
    source_ids: ['hced_dataset'],
    geometry: {type: 'Point', coordinates},
    location_provenance: valid,
  }).geometry.coordinates, coordinates);
}
"""
        )

    def test_dashboard_loads_contract_before_the_fail_closed_map(self) -> None:
        index = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        map_source = (ROOT / "web" / "map.js").read_text(encoding="utf-8")
        location = (ROOT / "web" / "location.js").read_text(encoding="utf-8")
        self.assertLess(index.index("./location.js"), index.index("./map.js"))
        self.assertLess(index.index("./map.js"), index.index("./horizon.js"))
        self.assertLess(index.index("./horizon.js"), index.index("./app.js"))
        self.assertIn("locationContract.normalizeEventLocation(event)", app)
        self.assertIn("locationContract.normalizeEventLocation(event)", map_source)
        self.assertIn("if (!location.geometry || !location.location_provenance) return null", map_source)
        self.assertIn("Source-transcribed location", app)
        self.assertIn("Source geographic-jurisdiction label", app)
        self.assertIn("Point [longitude, latitude]", app)
        self.assertIn("locationContract.LOCATION_WARNING", app)
        self.assertIn("Modern HCED location notice", app)
        self.assertIn(
            "HCED location fields are unreviewed source assertions. "
            "Quarantined values are withheld, not corrected. "
            "Coordinate precision is unknown.",
            location,
        )
        self.assertNotIn("location_name", app)
        self.assertNotIn("location_name", map_source)
        self.assertNotIn("L.map", app + map_source)


if __name__ == "__main__":
    unittest.main()
