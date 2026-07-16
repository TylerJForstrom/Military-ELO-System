from __future__ import annotations

import json
import unittest
from pathlib import Path

from military_elo.promotion.wave6_pre1500 import (
    WAVE6_PRE1500_REGISTRY_SUPERSESSIONS,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class Wave6RegistryConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.entities = {
            row["id"]: row for row in _json(ROOT / "data" / "release" / "entities.json")
        }
        registry = _json(ROOT / "data" / "catalog" / "registry.json")
        cls.registry = {row["id"]: row for row in registry["entities"]}
        cls.events = _json(ROOT / "data" / "release" / "events.json")

    def test_every_release_entity_has_an_exact_registry_identity(self) -> None:
        self.assertLessEqual(set(self.entities), set(self.registry))
        for entity_id, entity in self.entities.items():
            with self.subTest(entity_id=entity_id):
                registry = self.registry[entity_id]
                for field in ("name", "kind", "start_year", "end_year", "region"):
                    self.assertEqual(registry.get(field), entity.get(field), field)

    def test_superseded_registry_ids_are_preserved_and_never_rated(self) -> None:
        participant_ids = {
            participant["entity_id"]
            for event in self.events
            for participant in event["participants"]
        }
        for old_id, replacement_id in WAVE6_PRE1500_REGISTRY_SUPERSESSIONS.items():
            with self.subTest(old_id=old_id):
                old = self.registry[old_id]
                self.assertEqual(old["identity_status"], "superseded")
                self.assertEqual(old["status"], "unrated")
                self.assertEqual(old["superseded_by"], replacement_id)
                self.assertIn(replacement_id, self.entities)
                self.assertNotIn(old_id, participant_ids)

    def test_reused_pre1500_entities_preserve_cliopatria_provenance(self) -> None:
        bulgaria = self.entities["clio_bg_bulgaria_early_682_95daf02a"]
        seljuk = self.entities["clio_ir_seljuk_sultanate_1040_577da931"]
        self.assertIn("cliopatria_v020", bulgaria["source_ids"])
        self.assertIn("cliopatria_v020", seljuk["source_ids"])
        self.assertIn("Seljuk Empire", seljuk["aliases"])

    def test_reviewed_modern_boundaries_are_explicit(self) -> None:
        egypt = self.entities["egypt_muhammad_ali"]
        syria = self.entities["clio_q41137_1973_b05dea50"]
        self.assertEqual((egypt["start_year"], egypt["end_year"]), (1805, 1882))
        self.assertEqual((syria["start_year"], syria["end_year"]), (1962, None))


if __name__ == "__main__":
    unittest.main()
