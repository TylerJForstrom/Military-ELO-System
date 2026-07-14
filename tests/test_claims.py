import json
import unittest
from pathlib import Path

from military_elo.claims import Claim, EvidenceLink, SourceLocator, canonical_json
from military_elo.models import Entity, Event, Participant, Source


ROOT = Path(__file__).resolve().parents[1]
CHECKSUM = "a" * 64


def locator(**overrides):
    values = {
        "source_id": "source-1",
        "edition": "2nd ed.",
        "page": 42,
        "checksum": CHECKSUM,
        "language": "en",
        "source_family": "monograph-family-1",
        "creator": "Historian Example",
        "citation": "Historian Example, Example History, 2nd ed., p. 42.",
    }
    values.update(overrides)
    return SourceLocator(**values)


class ClaimModelTests(unittest.TestCase):
    def test_source_locator_round_trip_retains_exact_locator_and_authorship(self):
        original = locator(row="table-7", url="https://example.test/book#page=42")
        restored = SourceLocator.from_dict(original.to_dict())
        self.assertEqual(restored, original)
        self.assertTrue(restored.has_exact_anchor)
        self.assertEqual(restored.creator, "Historian Example")

    def test_claim_round_trip_is_deterministic_and_status_is_lifecycle_only(self):
        claim = Claim(
            id="claim-1",
            subject="event-1",
            predicate="winner",
            value={"side": "a", "details": {"control": True, "score": 1}},
            precision={"kind": "categorical", "confidence": 0.7},
            provenance=(locator(),),
            contradicts=("claim-2",),
            claim_group_id="winner:event-1",
            exclusive=True,
            impact="high",
            evidence_ids=("evidence-1",),
        )
        encoded = claim.to_dict()
        self.assertEqual(encoded["status"], "active")
        self.assertNotIn("decision", encoded)
        self.assertEqual(Claim.from_dict(encoded), claim)
        self.assertEqual(canonical_json(encoded), canonical_json(Claim.from_dict(encoded).to_dict()))

    def test_evidence_link_is_typed_but_does_not_resolve_claim(self):
        link = EvidenceLink(
            id="evidence-1",
            claim_id="claim-1",
            locator=locator(),
            relationship="contradicts",
            source_family="monograph-family-1",
            note="Independent source reports the opposing side.",
        )
        self.assertEqual(EvidenceLink.from_dict(link.to_dict()), link)
        self.assertNotIn("accepted", link.to_dict())

    def test_differently_ordered_json_values_have_one_canonical_form(self):
        left = {"b": [2, {"z": 1, "a": 0}], "a": True}
        right = {"a": True, "b": [2, {"a": 0, "z": 1}]}
        self.assertEqual(canonical_json(left), canonical_json(right))

    def test_claim_payload_is_deeply_immutable_and_detached(self):
        payload = {"side": "a", "details": {"sources": ["one"]}}
        precision = {"range": [0.6, 0.8]}
        immutable = Claim(
            id="claim-immutable",
            subject="event-1",
            predicate="winner",
            value=payload,
            precision=precision,
            provenance=(locator(),),
        )
        payload["side"] = "b"
        precision["range"].append(1.0)
        self.assertEqual(immutable.to_dict()["value"]["side"], "a")
        self.assertEqual(immutable.to_dict()["precision"]["range"], [0.6, 0.8])
        with self.assertRaises(TypeError):
            immutable.value["side"] = "b"
        with self.assertRaises(TypeError):
            immutable.value["details"]["sources"] += ("two",)
        with self.assertRaises(TypeError):
            Claim(
                "claim-set",
                "event-1",
                "winner",
                "a",
                provenance={locator()},
            )

    def test_claim_requires_explicit_value_and_real_boolean_exclusive(self):
        base = {
            "id": "claim-1",
            "subject": "event-1",
            "predicate": "winner",
            "precision": None,
            "provenance": [locator().to_dict()],
        }
        with self.assertRaises(ValueError):
            Claim.from_dict(base)
        explicit_null = Claim.from_dict({**base, "value": None})
        self.assertIsNone(explicit_null.to_dict()["value"])
        with self.assertRaises(TypeError):
            Claim.from_dict({**base, "value": "side-a", "exclusive": "false"})
        for invalid_ids in ("evidence-1", False, {}):
            with self.subTest(invalid_ids=invalid_ids), self.assertRaises(TypeError):
                Claim.from_dict(
                    {**base, "value": "side-a", "evidence_ids": invalid_ids}
                )

    def test_claim_schema_is_draft_2020_12_and_lifecycle_constrained(self):
        schema = json.loads((ROOT / "schemas" / "claim.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(
            schema["properties"]["status"]["enum"],
            ["active", "withdrawn", "superseded"],
        )
        self.assertIn("evidenceLink", schema["$defs"])


class LegacyModelCompatibilityTests(unittest.TestCase):
    def test_legacy_entity_source_participant_and_event_load_without_new_fields(self):
        entity_raw = {
            "id": "a",
            "name": "A",
            "kind": "state",
            "start_year": 1,
            "end_year": 10,
            "source_ids": ["source-1"],
        }
        source_raw = {
            "id": "source-1",
            "title": "Source",
            "url": "https://example.test/source",
        }
        participant_raw = {
            "entity_id": "a",
            "side": "one",
            "outcome": {"battlefield_control": 1},
        }
        event_raw = {
            "id": "event-1",
            "name": "Event",
            "year": 5,
            "end_year": 5,
            "event_type": "engagement",
            "participants": [participant_raw, {"entity_id": "b", "side": "two"}],
            "source_ids": ["source-1"],
        }

        entity = Entity.from_dict(entity_raw)
        source = Source.from_dict(source_raw)
        participant = Participant.from_dict(participant_raw)
        event = Event.from_dict(event_raw)
        self.assertEqual(entity.id, "a")
        self.assertEqual(source.id, "source-1")
        self.assertEqual(participant.entry, None)
        self.assertEqual(event.aliases, ())

        entity_output = entity.to_dict()
        participant_output = participant.to_dict()
        event_output = event.to_dict()
        for key in ("claim_ids", "adjudication_ids"):
            self.assertNotIn(key, entity_output)
            self.assertNotIn(key, event_output)
        for key in ("entry", "exit", "objectives", "claim_ids", "adjudication_ids"):
            self.assertNotIn(key, participant_output)
        for key in (
            "aliases",
            "parent_event_ids",
            "child_event_ids",
            "date_interval",
            "geometry",
            "participation_episodes",
        ):
            self.assertNotIn(key, event_output)

        self.assertEqual(Entity.from_dict(entity_output), entity)
        self.assertEqual(Source.from_dict(source.to_dict()), source)
        self.assertEqual(Participant.from_dict(participant_output), participant)
        self.assertEqual(Event.from_dict(event_output), event)

    def test_optional_model_fields_round_trip_when_supplied(self):
        entity = Entity.from_dict(
            {
                "id": "a",
                "name": "A",
                "kind": "state",
                "start_year": 1,
                "claim_ids": ["claim-entity"],
                "adjudication_ids": ["decision-entity"],
            }
        )
        raw = {
            "id": "event-1",
            "name": "Event",
            "year": 5,
            "event_type": "engagement",
            "participants": [
                {
                    "entity_id": "a",
                    "side": "one",
                    "entry": {"low": 4, "best": 5, "high": 5, "precision": "year"},
                    "exit": {"low": 5, "best": 5, "high": 6, "precision": "year"},
                    "objectives": ["hold ground"],
                    "claim_ids": ["claim-p"],
                    "adjudication_ids": ["decision-p"],
                },
                {"entity_id": "b", "side": "two"},
            ],
            "source_ids": ["source-1"],
            "aliases": ["Alias"],
            "parent_event_ids": ["event-parent"],
            "child_event_ids": ["event-child"],
            "date_interval": {
                "start": {"low": 4, "best": 5, "high": 5, "precision": "year"},
                "end": {"low": 5, "best": 5, "high": 6, "precision": "year"},
            },
            "geometry": {"coordinates": [10.0, 20.0], "type": "Point"},
            "claim_ids": ["claim-1"],
            "adjudication_ids": ["decision-1"],
            "participation_episodes": [
                {
                    "id": "episode-1",
                    "entity_id": "a",
                    "side": "one",
                    "role": "primary",
                    "claim_ids": ["claim-episode"],
                }
            ],
        }
        event = Event.from_dict(raw)
        output = event.to_dict()
        self.assertEqual(entity.to_dict()["adjudication_ids"], ["decision-entity"])
        self.assertEqual(Entity.from_dict(entity.to_dict()), entity)
        self.assertEqual(output["claim_ids"], ["claim-1"])
        self.assertEqual(output["participants"][0]["objectives"], ["hold ground"])
        self.assertEqual(output["participants"][0]["adjudication_ids"], ["decision-p"])
        self.assertEqual(output["participation_episodes"][0]["claim_ids"], ["claim-episode"])
        self.assertEqual(Event.from_dict(output), event)


if __name__ == "__main__":
    unittest.main()
