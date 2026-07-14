import json
import unittest

from military_elo.config import ModelConfig
from military_elo.engine import EloEngine
from military_elo.models import Entity, Event, Participant, Source


def entities():
    return [
        Entity("old_empire", "Old Empire", "empire", 0, 100),
        Entity("successor", "Successor", "empire", 101, 300, predecessors=("old_empire",)),
        Entity("rival", "Rival", "state", 0, 300),
        Entity("ally", "Ally", "state", 0, 300),
    ]


def outcome(value):
    return {
        "battlefield_outcome": value,
        "political_objectives": value,
        "territorial_outcome": value,
        "sovereignty_survival": value,
        "settlement_durability": value,
        "force_preservation": value,
    }


def war(event_id, year, participants, **overrides):
    values = {
        "id": event_id,
        "name": event_id,
        "year": year,
        "end_year": year,
        "event_type": "war",
        "war_type": "interstate_limited",
        "scale": "major_war",
        "stakes": "major",
        "decisiveness": 0.8,
        "confidence": 1.0,
        "participants": tuple(participants),
        "source_ids": ("source",),
    }
    values.update(overrides)
    return Event(**values)


class EloEngineTests(unittest.TestCase):
    def test_new_entity_never_inherits_predecessor_rating(self):
        first = war(
            "old_wins",
            50,
            [
                Participant("old_empire", "a", outcome=outcome(1.0)),
                Participant("rival", "b", outcome=outcome(0.0)),
            ],
        )
        engine = EloEngine().run(entities(), [first])
        self.assertGreater(engine.states["old_empire"].strategic.rating, 1500)
        self.assertEqual(engine.states["successor"].strategic.rating, 1500)

    def test_event_updates_are_zero_sum(self):
        event = war(
            "coalition_war",
            50,
            [
                Participant("old_empire", "a", role="coalition_lead", contribution=1, outcome=outcome(0.95)),
                Participant("ally", "a", role="supporting_ally", contribution=0.4, outcome=outcome(0.9)),
                Participant("rival", "b", contribution=1, outcome=outcome(0.1)),
            ],
        )
        update = EloEngine().run(entities(), [event]).event_updates[0]
        self.assertLess(abs(sum(item.delta for item in update.participants)), 1e-9)
        self.assertGreater(next(item for item in update.participants if item.entity_id == "old_empire").delta, 0)
        self.assertLess(next(item for item in update.participants if item.entity_id == "rival").delta, 0)

    def test_existential_loss_moves_more_than_limited_loss(self):
        limited = war(
            "limited",
            50,
            [Participant("old_empire", "a", outcome=outcome(0)), Participant("rival", "b", outcome=outcome(1))],
            stakes="limited",
            scale="campaign",
        )
        existential = war(
            "existential",
            50,
            [Participant("old_empire", "a", outcome=outcome(0)), Participant("rival", "b", outcome=outcome(1))],
            stakes="existential",
            scale="total_war",
        )
        limited_delta = EloEngine().run(entities(), [limited]).event_updates[0].participants[0].delta
        existential_delta = EloEngine().run(entities(), [existential]).event_updates[0].participants[0].delta
        self.assertGreater(abs(existential_delta), abs(limited_delta))

    def test_context_makes_expected_favorite_gain_less_for_same_result(self):
        equal_event = war(
            "equal",
            50,
            [Participant("old_empire", "a", outcome=outcome(1)), Participant("rival", "b", outcome=outcome(0))],
        )
        favorite_event = war(
            "favorite",
            50,
            [
                Participant("old_empire", "a", force_size=400_000, outcome=outcome(1)),
                Participant("rival", "b", force_size=50_000, outcome=outcome(0)),
            ],
        )
        equal_gain = EloEngine().run(entities(), [equal_event]).event_updates[0].participants[0].delta
        favorite_gain = EloEngine().run(entities(), [favorite_event]).event_updates[0].participants[0].delta
        self.assertLess(favorite_gain, equal_gain)

    def test_low_confidence_pulls_outcome_toward_draw(self):
        high = war(
            "high",
            50,
            [Participant("old_empire", "a", outcome=outcome(1)), Participant("rival", "b", outcome=outcome(0))],
            confidence=1.0,
        )
        low = war(
            "low",
            50,
            [Participant("old_empire", "a", outcome=outcome(1)), Participant("rival", "b", outcome=outcome(0))],
            confidence=0.25,
        )
        high_gain = EloEngine().run(entities(), [high]).event_updates[0].participants[0].delta
        low_gain = EloEngine().run(entities(), [low]).event_updates[0].participants[0].delta
        self.assertLess(low_gain, high_gain)

    def test_explicit_zero_participant_confidence_is_preserved(self):
        event = war(
            "uncertain",
            50,
            [
                Participant("old_empire", "a", outcome=outcome(1), evidence_confidence=0),
                Participant("rival", "b", outcome=outcome(0), evidence_confidence=0),
            ],
            confidence=1.0,
        )
        update = EloEngine().run(entities(), [event]).event_updates[0]
        self.assertAlmostEqual(update.participants[0].actual, 0.5)
        self.assertAlmostEqual(update.participants[1].actual, 0.5)
        self.assertAlmostEqual(update.participants[0].delta, 0)
        self.assertAlmostEqual(update.participants[1].delta, 0)

    def test_events_in_one_war_cluster_receive_diminishing_weight(self):
        clustered = [
            war(
                f"clustered_{index}",
                50 + index,
                [
                    Participant("old_empire", "a", outcome=outcome(1)),
                    Participant("rival", "b", outcome=outcome(0)),
                ],
                cluster_id="same_war",
            )
            for index in range(3)
        ]
        independent = [
            war(
                f"independent_{index}",
                50 + index,
                [
                    Participant("old_empire", "a", outcome=outcome(1)),
                    Participant("rival", "b", outcome=outcome(0)),
                ],
                cluster_id=f"war_{index}",
            )
            for index in range(3)
        ]

        clustered_engine = EloEngine().run(entities(), clustered)
        independent_engine = EloEngine().run(entities(), independent)
        self.assertLess(
            clustered_engine.states["old_empire"].strategic.rating,
            independent_engine.states["old_empire"].strategic.rating,
        )
        clustered_weights = {
            update.evidence_weight for update in clustered_engine.event_updates
        }
        self.assertEqual(len(clustered_weights), 1)
        self.assertLess(next(iter(clustered_weights)), 1.0)
        self.assertLess(
            clustered_engine.states["old_empire"].strategic.evidence,
            independent_engine.states["old_empire"].strategic.evidence,
        )

    def test_same_year_sequence_does_not_control_processing_order(self):
        def same_year_events(first_sequence, second_sequence):
            return [
                war(
                    "alpha",
                    50,
                    [
                        Participant("old_empire", "a", outcome=outcome(1)),
                        Participant("rival", "b", outcome=outcome(0)),
                    ],
                    sequence=first_sequence,
                ),
                war(
                    "beta",
                    50,
                    [
                        Participant("old_empire", "a", outcome=outcome(0)),
                        Participant("rival", "b", outcome=outcome(1)),
                    ],
                    sequence=second_sequence,
                ),
            ]

        forward = EloEngine().run(entities(), same_year_events(1, 2))
        reversed_sequence = EloEngine().run(entities(), same_year_events(2, 1))
        self.assertAlmostEqual(
            forward.states["old_empire"].strategic.rating,
            reversed_sequence.states["old_empire"].strategic.rating,
        )
        self.assertEqual(
            [update.event.id for update in forward.event_updates],
            ["alpha", "beta"],
        )

    def test_vietnam_style_defeat_is_not_existential_by_dimensions(self):
        config = ModelConfig()
        event = war(
            "intervention",
            200,
            [
                Participant(
                    "successor",
                    "a",
                    outcome={
                        "battlefield_outcome": 0.55,
                        "political_objectives": 0.10,
                        "territorial_outcome": 0.25,
                        "sovereignty_survival": 0.98,
                        "settlement_durability": 0.10,
                        "force_preservation": 0.75,
                    },
                ),
                Participant("rival", "b", outcome=outcome(0.95)),
            ],
            war_type="insurgency_intervention",
        )
        update = EloEngine(config).run(entities(), [event]).event_updates[0]
        intervention = next(item for item in update.participants if item.entity_id == "successor")
        self.assertGreater(intervention.actual, 0.05)
        self.assertNotEqual(intervention.result_class, "existential_defeat")

    def test_terminal_total_war_defeat_costs_more_than_failed_intervention(self):
        intervention = war(
            "intervention",
            200,
            [
                Participant(
                    "successor",
                    "a",
                    stakes=0.25,
                    national_scale=0.50,
                    termination="withdrawal",
                    outcome={
                        "battlefield_outcome": 0.55,
                        "political_objectives": 0.10,
                        "territorial_outcome": 0.25,
                        "sovereignty_survival": 0.98,
                        "settlement_durability": 0.10,
                        "force_preservation": 0.75,
                    },
                ),
                Participant("rival", "b", stakes=1, national_scale=1, outcome=outcome(0.95)),
            ],
            war_type="insurgency_intervention",
            geographic_scope=0.5,
        )
        terminal = war(
            "terminal",
            200,
            [
                Participant(
                    "successor",
                    "a",
                    stakes=1,
                    national_scale=1,
                    termination="capitulation",
                    outcome=outcome(0),
                ),
                Participant("rival", "b", stakes=1, national_scale=1, outcome=outcome(1)),
            ],
            war_type="world_war",
            stakes="existential",
            scale="total_war",
            geographic_scope=1,
        )
        intervention_loss = EloEngine().run(entities(), [intervention]).event_updates[0].participants[0].delta
        terminal_loss = EloEngine().run(entities(), [terminal]).event_updates[0].participants[0].delta
        self.assertGreater(abs(terminal_loss), abs(intervention_loss) * 1.5)

    def test_dashboard_source_export_round_trips_family_and_role_metadata(self):
        event = war(
            "sourced_event",
            50,
            [
                Participant("old_empire", "a", outcome=outcome(1)),
                Participant("rival", "b", outcome=outcome(0)),
            ],
            outcome_source_ids=("source",),
            outcome_source_family_ids=("iwbd",),
        )
        source = Source(
            "source",
            "Outcome dataset",
            "https://example.test/outcomes",
            source_family_id="iwbd",
            evidence_roles=("outcome",),
        )
        engine = EloEngine().run(entities(), [event])
        ratings_before = {
            entity_id: state.strategic.rating
            for entity_id, state in engine.states.items()
        }

        dashboard = json.loads(json.dumps(engine.export({source.id: source})))
        exported_event = dashboard["events"][0]
        exported_source = exported_event["sources"][0]

        self.assertEqual(exported_event["source_ids"], ["source"])
        self.assertEqual(exported_event["outcome_source_ids"], ["source"])
        self.assertEqual(exported_event["outcome_source_family_ids"], ["iwbd"])
        self.assertEqual(
            exported_source,
            {
                "id": "source",
                "title": "Outcome dataset",
                "url": "https://example.test/outcomes",
                "source_family_id": "iwbd",
                "evidence_roles": ["outcome"],
            },
        )
        self.assertEqual(Source.from_dict(exported_source), source)
        self.assertEqual(
            {
                entity_id: state.strategic.rating
                for entity_id, state in engine.states.items()
            },
            ratings_before,
        )

        legacy_event = war(
            "legacy_source_event",
            51,
            [
                Participant("old_empire", "a", outcome=outcome(1)),
                Participant("rival", "b", outcome=outcome(0)),
            ],
        )
        legacy_source = Source(
            "source", "Legacy source", "https://example.test/legacy"
        )
        legacy_export = EloEngine().run(entities(), [legacy_event]).export(
            {legacy_source.id: legacy_source}
        )["events"][0]
        self.assertNotIn("outcome_source_ids", legacy_export)
        self.assertNotIn("outcome_source_family_ids", legacy_export)
        self.assertNotIn("source_family_id", legacy_export["sources"][0])
        self.assertNotIn("evidence_roles", legacy_export["sources"][0])


if __name__ == "__main__":
    unittest.main()
