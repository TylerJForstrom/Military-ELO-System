import unittest

from military_elo.config import ModelConfig
from military_elo.engine import EloEngine
from military_elo.models import Entity, Event, Participant


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


if __name__ == "__main__":
    unittest.main()
