import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DashboardInformationHorizonTests(unittest.TestCase):
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
            f"node horizon contract test failed:\n{completed.stdout}\n{completed.stderr}",
        )

    def test_1950_cutoff_excludes_later_events_entities_and_points(self) -> None:
        self._run_node(
            r"""
const assert = require('node:assert/strict');
const horizon = require('./web/horizon.js');

const entities = [
  {id: 'known', name: 'Known in 1950', start_year: 1900, end_year: null},
  {id: 'future', name: 'Future polity', start_year: 1960, end_year: null},
];
const series = {
  known: [
    {year: 1900, event_id: 'origin', composite: 1500, strategic: 1500, uncertainty: 300, delta: 0},
    {year: 1945, event_id: 'known-war', composite: 1612.5, strategic: 1620, uncertainty: 180, delta: 112.5},
    // Adversarial mismatch: the point is dated before the event's 1955 availability year.
    {year: 1949, event_id: 'unfinished-war', composite: 1999, strategic: 1999, uncertainty: 170, delta: 386.5},
    {year: 1975, event_id: 'later-war', composite: 1800, strategic: 1810, uncertainty: 100, delta: 250},
  ],
  future: [
    {year: 1960, event_id: 'origin', composite: 1500, strategic: 1500, uncertainty: 300, delta: 0},
    {year: 1975, event_id: 'future-war', composite: 1900, strategic: 1920, uncertainty: 120, delta: 400},
  ],
};
const events = [
  {id: 'known-war', year: 1939, end_year: 1945, participants: [{entity_id: 'known'}]},
  {id: 'unfinished-war', year: 1949, end_year: 1955, participants: [{entity_id: 'known'}]},
  {id: 'later-war', year: 1970, end_year: 1975, participants: [{entity_id: 'known'}]},
  {id: 'future-war', year: 1970, end_year: 1975, participants: [{entity_id: 'future'}]},
];

assert.equal(horizon.eventAvailabilityYear(events[1]), 1955);
assert.equal(horizon.eventIsAvailable(events[1], 1950), false);
assert.deepEqual(horizon.eventsAtOrBefore(events, 1950).map((event) => event.id), ['known-war']);
assert.deepEqual(
  horizon.authorizedSeriesThrough(series.known, events, 'known', 1950).map((point) => point.year),
  [1900, 1945],
);

const ranking = horizon.rankAtYear({entities, series, events, year: 1950, metric: 'strategic'});
assert.equal(ranking.length, 1);
assert.equal(ranking[0].entity.id, 'known');
assert.equal(ranking[0].value, 1620);
assert.equal(ranking[0].point.year, 1945);
assert.equal(ranking[0].events, 1);
assert.equal(ranking.some((row) => row.entity.id === 'future'), false);
"""
        )

    def test_markup_accessibility_and_fail_safe_integration(self) -> None:
        index = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        styles = (ROOT / "web" / "styles.css").read_text(encoding="utf-8")

        self.assertLess(index.index("./map.js"), index.index("./horizon.js"))
        self.assertLess(index.index("./horizon.js"), index.index("./app.js"))
        self.assertIn('class="timeline-workspace"', index)
        self.assertIn('aria-labelledby="timeline-ranking-title"', index)
        self.assertIn('<ol id="timeline-ranking-list"', index)
        self.assertIn('id="timeline-ranking-empty"', index)
        self.assertIn(".rankAtYear({", app)
        self.assertIn(".authorizedSeriesThrough", app)
        self.assertIn("horizonContract.eventIsAvailable(event, state.selectedYear)", app)
        self.assertIn("updatePerspectiveAvailability", app)
        self.assertIn("hideChartTooltip();", app)
        self.assertIn("pin-hidden-count", app)
        self.assertNotIn("fills the remaining slots with the all-time leaders", app)
        self.assertIn(".timeline-workspace", styles)
        self.assertIn(".timeline-ranking-list", styles)


if __name__ == "__main__":
    unittest.main()
