import json
import unittest
from pathlib import Path

from military_elo.audit import audit_dataset, audit_evidence, has_errors
from military_elo.canonical import (
    CanonicalEvent,
    ParticipationEpisode,
    UncertainDate,
    UncertainDateInterval,
)
from military_elo.claims import Claim, EvidenceLink, SourceLocator
from military_elo.config import ModelConfig
from military_elo.models import Entity, Event, Participant, Source
from military_elo.review import (
    Adjudication,
    active_adjudications,
    append_adjudication,
    resolve_claims,
)


ROOT = Path(__file__).resolve().parents[1]
CHECKSUM = "b" * 64


def source_locator(family="family-a"):
    return SourceLocator(
        source_id="source-a",
        edition="v1",
        row=7,
        checksum=CHECKSUM,
        language="en",
        source_family=family,
    )


def claim(claim_id, value, **overrides):
    values = {
        "id": claim_id,
        "subject": "event-1",
        "predicate": "winner",
        "value": value,
        "precision": "categorical",
        "provenance": (source_locator(),),
    }
    values.update(overrides)
    return Claim(**values)


def decision(decision_id, claim_id, result="accepted", **overrides):
    values = {
        "id": decision_id,
        "claim_id": claim_id,
        "reviewer": f"reviewer-{decision_id}",
        "decision": result,
        "rationale": "Reasoned against the cited evidence.",
        "codebook_version": "1.0",
        "blind_review": True,
        "confidence": 0.8,
    }
    values.update(overrides)
    return Adjudication(**values)


class EvidenceAuditTests(unittest.TestCase):
    def test_contradictory_claims_are_preserved_and_warned_not_rejected(self):
        claims = [
            claim("claim-a", "side-a", contradicts=("claim-b",)),
            claim("claim-b", "side-b", contradicts=("claim-a",)),
        ]
        issues = audit_evidence(claims=claims)
        self.assertIn("claim_disagreement", {item.code for item in issues})
        self.assertFalse(has_errors(issues))

    def test_claim_status_cannot_encode_acceptance(self):
        invalid = claim("claim-a", "side-a", status="accepted")
        issues = audit_evidence(claims=[invalid])
        self.assertIn("invalid_claim_status", {item.code for item in issues})

    def test_typed_evidence_link_is_valid_and_source_family_mismatch_fails(self):
        linked_claim = claim("claim-a", "side-a", provenance=(), evidence_ids=("evidence-a",))
        valid = EvidenceLink(
            id="evidence-a",
            claim_id="claim-a",
            locator=source_locator(),
            relationship="supports",
            source_family="family-a",
        )
        self.assertFalse(has_errors(audit_evidence([linked_claim], [valid])))
        invalid = EvidenceLink(
            id="evidence-a",
            claim_id="claim-a",
            locator=source_locator(),
            relationship="supports",
            source_family="family-b",
        )
        self.assertIn(
            "evidence_source_family_mismatch",
            {item.code for item in audit_evidence([linked_claim], [invalid])},
        )

    def test_inexact_locator_is_an_error(self):
        bad_locator = SourceLocator(
            source_id="source-a",
            edition="v1",
            checksum=CHECKSUM,
            language="en",
            source_family="family-a",
        )
        issues = audit_evidence([claim("claim-a", "side-a", provenance=(bad_locator,))])
        self.assertIn("inexact_source_locator", {item.code for item in issues})

    def test_locator_types_urls_and_registry_references_are_errors(self):
        bad_locator = SourceLocator(
            source_id="missing-source",
            edition="v1",
            page=[],
            url="not-an-absolute-url",
            checksum=CHECKSUM,
            language="en",
            source_family="family-a",
        )
        issues = audit_evidence(
            [claim("claim-a", "side-a", provenance=(bad_locator,))],
            sources={"source-a": Source("source-a", "Source", "https://example.test")},
        )
        codes = {item.code for item in issues}
        self.assertIn("invalid_locator_anchor", codes)
        self.assertIn("invalid_locator_url", codes)
        unknown = next(item for item in issues if item.code == "unknown_locator_source")
        self.assertEqual(unknown.severity, "error")


class AdjudicationResolutionTests(unittest.TestCase):
    def test_append_only_supersession_preserves_prior_decisions(self):
        first = decision("decision-1", "claim-a", "needs_more_evidence")
        second = decision(
            "decision-2",
            "claim-a",
            "accepted",
            supersedes=("decision-1",),
        )
        history = append_adjudication((first,), second)
        self.assertEqual([item.id for item in history], ["decision-1", "decision-2"])
        self.assertEqual([item.id for item in active_adjudications(history)], ["decision-2"])

    def test_append_rejects_unknown_or_cross_claim_supersession(self):
        first = decision("decision-1", "claim-a")
        with self.assertRaises(ValueError):
            append_adjudication((first,), decision("decision-2", "claim-a", supersedes=("missing",)))
        with self.assertRaises(ValueError):
            append_adjudication((first,), decision("decision-2", "claim-b", supersedes=("decision-1",)))

    def test_append_and_resolution_reject_blank_workflow_fields_and_fake_reviewers(self):
        high = claim("claim-high", "side-a", impact="high")
        blank = decision("blank", high.id, reviewer=" ", rationale=" ")
        with self.assertRaises(ValueError):
            append_adjudication((), blank)
        with self.assertRaises(ValueError):
            resolve_claims([high], [blank])

        primary = decision(
            "primary",
            high.id,
            reviewer="reviewer-a",
            review_stage="primary",
        )
        padded_same = decision(
            "secondary",
            high.id,
            reviewer=" reviewer-a ",
            review_stage="secondary",
        )
        self.assertEqual(
            resolve_claims([high], [primary, padded_same])[high.id].state,
            "unresolved",
        )
        with self.assertRaises(TypeError):
            Adjudication.from_dict(
                {
                    **decision("typed", high.id).to_dict(),
                    "blind_review": "false",
                }
            )
        with self.assertRaises(TypeError):
            Adjudication.from_dict(
                {**decision("typed", high.id).to_dict(), "confidence": "0.8"}
            )
        with self.assertRaises(TypeError):
            Adjudication.from_dict(
                {**decision("typed", high.id).to_dict(), "review_stage": 2}
            )

    def test_high_impact_acceptance_requires_distinct_active_secondary_review(self):
        high = claim("claim-high", "side-a", impact="high")
        primary = decision(
            "primary",
            high.id,
            reviewer="reviewer-a",
            review_stage="primary",
        )
        one_review = resolve_claims([high], [primary])[high.id]
        self.assertEqual(one_review.state, "unresolved")

        secondary = decision(
            "secondary",
            high.id,
            reviewer="reviewer-b",
            review_stage="secondary",
        )
        resolved = resolve_claims([high], [primary, secondary])[high.id]
        self.assertEqual(resolved.state, "accepted")

        same_reviewer = decision(
            "secondary-same",
            high.id,
            reviewer="reviewer-a",
            review_stage="secondary",
        )
        self.assertEqual(
            resolve_claims([high], [primary, same_reviewer])[high.id].state,
            "unresolved",
        )

    def test_resolution_fails_closed_on_malformed_claim_gate_metadata(self):
        malformed_impact = claim("claim-impact", "side-a", impact="High")
        with self.assertRaises(ValueError):
            resolve_claims(
                [malformed_impact],
                [decision("decision-impact", malformed_impact.id)],
            )
        blank_group = claim(
            "claim-exclusive",
            "side-a",
            claim_group_id="",
            exclusive=True,
        )
        with self.assertRaises(ValueError):
            resolve_claims([blank_group], [decision("decision-exclusive", blank_group.id)])

    def test_superseded_secondary_acceptance_cannot_authorize_high_impact_claim(self):
        high = claim("claim-high", "side-a", impact="high")
        primary = decision(
            "primary",
            high.id,
            reviewer="reviewer-a",
            review_stage="primary",
        )
        secondary = decision(
            "secondary",
            high.id,
            reviewer="reviewer-b",
            review_stage="secondary",
        )
        rejection = decision(
            "secondary-rejected",
            high.id,
            "rejected",
            reviewer="reviewer-b",
            review_stage="secondary",
            supersedes=("secondary",),
        )
        resolution = resolve_claims([high], [primary, secondary, rejection])[high.id]
        self.assertEqual(resolution.state, "unresolved")
        self.assertNotEqual(resolution.state, "accepted")

    def test_mutually_exclusive_claims_cannot_both_resolve_accepted(self):
        claims = [
            claim("claim-a", "side-a", claim_group_id="winner", exclusive=True),
            claim("claim-b", "side-b", claim_group_id="winner", exclusive=True),
        ]
        decisions = [decision("decision-a", "claim-a"), decision("decision-b", "claim-b")]
        resolutions = resolve_claims(claims, decisions)
        self.assertEqual({item.state for item in resolutions.values()}, {"unresolved"})
        issues = audit_evidence(claims=claims, adjudications=decisions)
        self.assertIn("mutually_exclusive_acceptance", {item.code for item in issues})

    def test_exclusive_group_applies_when_another_member_omits_flag(self):
        claims = [
            claim("claim-a", "side-a", claim_group_id="winner", exclusive=True),
            claim("claim-b", "side-b", claim_group_id="winner"),
        ]
        decisions = [decision("decision-a", "claim-a"), decision("decision-b", "claim-b")]
        resolutions = resolve_claims(claims, decisions)
        self.assertEqual({item.state for item in resolutions.values()}, {"unresolved"})
        codes = {item.code for item in audit_evidence(claims=claims, adjudications=decisions)}
        self.assertIn("inconsistent_claim_group_exclusivity", codes)
        self.assertIn("mutually_exclusive_acceptance", codes)

    def test_exclusive_group_applies_when_another_member_explicitly_sets_false(self):
        claims = [
            claim("claim-a", "side-a", claim_group_id="winner", exclusive=True),
            claim("claim-b", "side-b", claim_group_id="winner", exclusive=False),
        ]
        decisions = [decision("decision-a", "claim-a"), decision("decision-b", "claim-b")]
        resolutions = resolve_claims(claims, decisions)
        self.assertEqual({item.state for item in resolutions.values()}, {"unresolved"})
        codes = {item.code for item in audit_evidence(claims=claims, adjudications=decisions)}
        self.assertIn("inconsistent_claim_group_exclusivity", codes)
        self.assertIn("mutually_exclusive_acceptance", codes)

    def test_adjudication_cannot_consider_evidence_from_another_claim(self):
        claims = [
            claim("claim-a", "side-a", provenance=(), evidence_ids=("evidence-a",)),
            claim("claim-b", "side-b"),
        ]
        link = EvidenceLink(
            id="evidence-a",
            claim_id="claim-a",
            locator=source_locator(),
            relationship="supports",
            source_family="family-a",
        )
        wrong = decision(
            "decision-b",
            "claim-b",
            evidence_ids_considered=("evidence-a",),
        )
        codes = {
            item.code
            for item in audit_evidence(
                claims=claims,
                evidence_links=[link],
                adjudications=[wrong],
            )
        }
        self.assertIn("cross_claim_adjudication_evidence", codes)

    def test_adjudication_schema_carries_review_workflow_fields(self):
        schema = json.loads(
            (ROOT / "schemas" / "adjudication.schema.json").read_text(encoding="utf-8")
        )
        for name in ("review_stage", "evidence_ids_considered", "blind_review", "confidence"):
            self.assertIn(name, schema["properties"])


class CanonicalEvidenceAuditTests(unittest.TestCase):
    def test_invalid_event_dates_geometry_and_episode_are_reported(self):
        event = CanonicalEvent(
            id="event-1",
            name="Event",
            date_interval=UncertainDateInterval(
                start=UncertainDate.exact("1914-02-30", "day"),
                end=UncertainDate.exact("1914-03-01", "day"),
            ),
            geometry={"type": "Point", "coordinates": ["east", 5]},
            participation_episodes=(
                ParticipationEpisode(
                    id="episode-1",
                    entity_id="entity-a",
                    side="a",
                    role="primary",
                    entry=UncertainDate.exact(1915, "year"),
                    exit=UncertainDate.exact(1914, "year"),
                    contribution=-0.1,
                ),
            ),
        )
        codes = {item.code for item in audit_evidence(canonical_events=[event])}
        self.assertIn("invalid_uncertain_date", codes)
        self.assertIn("invalid_event_geometry", codes)
        self.assertIn("invalid_participation_episode", codes)

    def test_event_hierarchy_cycle_is_an_error(self):
        first = CanonicalEvent("event-a", "A", child_event_ids=("event-b",))
        second = CanonicalEvent("event-b", "B", child_event_ids=("event-a",))
        codes = {item.code for item in audit_evidence(canonical_events=[first, second])}
        self.assertIn("event_hierarchy_cycle", codes)

    def test_episode_context_uses_uncertainty_overlap_and_precision_bounds(self):
        event = CanonicalEvent(
            "event-1",
            "Event",
            date_interval=UncertainDateInterval(
                UncertainDate.exact(1914, "year"),
                UncertainDate.exact(1914, "year"),
            ),
            participation_episodes=(
                ParticipationEpisode(
                    "overlap",
                    "entity-a",
                    "a",
                    "primary",
                    entry=UncertainDate(1913, None, 1915, "range"),
                    exit=UncertainDate.exact("1914-12-31", "day"),
                ),
                ParticipationEpisode(
                    "outside",
                    "entity-a",
                    "a",
                    "primary",
                    entry=UncertainDate.exact(1920, "year"),
                ),
            ),
        )
        issues = audit_evidence(
            canonical_events=[event],
            entity_ids={"entity-a"},
            entity_lifespans={"entity-a": (1900, 1918)},
        )
        outside = [item for item in issues if item.code == "episode_outside_event_interval"]
        self.assertEqual(len(outside), 1)
        self.assertIn("outside", outside[0].message)
        self.assertIn("episode_outside_entity_lifespan", {item.code for item in issues})

    def test_legacy_years_must_overlap_optional_date_interval(self):
        entities = [
            Entity("entity-a", "A", "state", 1900, 2000, source_ids=("source-a",)),
            Entity("entity-b", "B", "state", 1900, 2000, source_ids=("source-a",)),
        ]
        tactical = {
            "battlefield_control": 1.0,
            "mission_objective": 1.0,
            "force_preservation": 1.0,
            "positional_gain": 1.0,
        }
        event = Event(
            "event-1",
            "Event",
            1914,
            1914,
            "engagement",
            "interstate_limited",
            "battle",
            "limited",
            0.5,
            0.8,
            (
                Participant(
                    "entity-a",
                    "a",
                    outcome=tactical,
                    entry=UncertainDate.exact("1914-06-01", "day"),
                    exit=UncertainDate.exact("1914-12-31", "day"),
                ),
                Participant("entity-b", "b", outcome={key: 0.0 for key in tactical}),
            ),
            ("source-a",),
            date_interval=UncertainDateInterval(
                UncertainDate.exact(1920, "year"),
                UncertainDate.exact(1921, "year"),
            ),
        )
        sources = {"source-a": Source("source-a", "Source", "https://example.test")}
        codes = {item.code for item in audit_dataset(entities, [event], sources, ModelConfig())}
        self.assertIn("event_date_interval_mismatch", codes)

        same_year = Event.from_dict(
            {
                **event.to_dict(),
                "date_interval": {
                    "start": UncertainDate.exact(1914, "year").to_dict(),
                    "end": UncertainDate.exact(1914, "year").to_dict(),
                },
            }
        )
        same_year_codes = {
            item.code for item in audit_dataset(entities, [same_year], sources, ModelConfig())
        }
        self.assertNotIn("episode_outside_event_interval", same_year_codes)
        self.assertNotIn("event_date_interval_mismatch", same_year_codes)

    def test_same_id_legacy_overlays_receive_full_hierarchy_and_episode_audit(self):
        entities = [
            Entity("entity-a", "A", "state", 1900, 2000, source_ids=("source-a",)),
            Entity("entity-b", "B", "state", 1900, 2000, source_ids=("source-a",)),
        ]
        participants = (Participant("entity-a", "a"), Participant("entity-b", "b"))
        legacy = [
            Event(
                "event-a", "A", 1914, 1914, "war", "interstate_limited", "war",
                "limited", 0.5, 0.8, participants, ("source-a",),
                parent_event_ids=("event-b",),
                participation_episodes=(ParticipationEpisode("", "", "", ""),),
            ),
            Event(
                "event-b", "B", 1914, 1914, "war", "interstate_limited", "war",
                "limited", 0.5, 0.8, participants, ("source-a",),
                parent_event_ids=("event-a",),
            ),
        ]
        canonical = [
            CanonicalEvent(
                "event-a",
                "A",
                date_interval=UncertainDateInterval(
                    UncertainDate.exact(1920, "year"),
                    UncertainDate.exact(1920, "year"),
                ),
            ),
            CanonicalEvent("event-b", "B"),
        ]
        sources = {"source-a": Source("source-a", "Source", "https://example.test")}
        codes = {
            item.code
            for item in audit_dataset(
                entities,
                legacy,
                sources,
                ModelConfig(),
                canonical_events=canonical,
            )
        }
        self.assertIn("event_hierarchy_cycle", codes)
        self.assertIn("event_date_interval_mismatch", codes)
        self.assertIn("missing_participation_episode_id", codes)
        self.assertIn("missing_episode_entity", codes)

    def test_dataset_audit_validates_optional_legacy_model_evidence_fields(self):
        entities = [
            Entity("entity-a", "A", "state", 1900, 2000, source_ids=("source-a",)),
            Entity("entity-b", "B", "state", 1900, 2000, source_ids=("source-a",)),
        ]
        tactical = {
            "battlefield_control": 1.0,
            "mission_objective": 1.0,
            "force_preservation": 1.0,
            "positional_gain": 1.0,
        }
        event = Event(
            id="event-legacy-overlay",
            name="Event",
            year=1914,
            end_year=1914,
            event_type="engagement",
            war_type="interstate_limited",
            scale="battle",
            stakes="limited",
            decisiveness=0.5,
            confidence=0.8,
            participants=(
                Participant(
                    "entity-a",
                    "a",
                    outcome=tactical,
                    entry=UncertainDate.exact("1914-02-30", "day"),
                ),
                Participant("entity-b", "b", outcome={key: 0.0 for key in tactical}),
            ),
            source_ids=("source-a",),
            date_interval=UncertainDateInterval(
                start=UncertainDate.exact(1915, "year"),
                end=UncertainDate.exact(1914, "year"),
            ),
            participation_episodes=(
                ParticipationEpisode(
                    "episode-invalid",
                    "entity-a",
                    "a",
                    "primary",
                    contribution=1.5,
                ),
            ),
        )
        sources = {"source-a": Source("source-a", "Source", "https://example.test")}
        codes = {
            item.code
            for item in audit_dataset(entities, [event], sources, ModelConfig())
        }
        self.assertIn("invalid_participant_interval", codes)
        self.assertIn("invalid_uncertain_date", codes)
        self.assertIn("invalid_participation_episode", codes)

    def test_dataset_audits_all_new_entity_event_and_participant_references(self):
        entities = [
            Entity(
                "entity-a",
                "A",
                "state",
                1900,
                2000,
                source_ids=("source-a",),
                claim_ids=("missing-entity-claim",),
                adjudication_ids=("missing-entity-decision",),
            ),
            Entity("entity-b", "B", "state", 1900, 2000, source_ids=("source-a",)),
        ]
        tactical = {
            "battlefield_control": 1.0,
            "mission_objective": 1.0,
            "force_preservation": 1.0,
            "positional_gain": 1.0,
        }
        event = Event(
            "event-refs",
            "Event",
            1914,
            1914,
            "engagement",
            "interstate_limited",
            "battle",
            "limited",
            0.5,
            0.8,
            (
                Participant(
                    "entity-a",
                    "a",
                    outcome=tactical,
                    claim_ids=("missing-participant-claim",),
                    adjudication_ids=("missing-participant-decision",),
                ),
                Participant("entity-b", "b", outcome={key: 0.0 for key in tactical}),
            ),
            ("source-a",),
            claim_ids=("missing-event-claim",),
            adjudication_ids=("missing-event-decision",),
        )
        sources = {"source-a": Source("source-a", "Source", "https://example.test")}
        codes = {item.code for item in audit_dataset(entities, [event], sources, ModelConfig())}
        for expected in (
            "unknown_entity_claim",
            "unknown_entity_adjudication",
            "unknown_event_claim",
            "unknown_event_adjudication",
            "unknown_participant_claim",
            "unknown_participant_adjudication",
        ):
            self.assertIn(expected, codes)


if __name__ == "__main__":
    unittest.main()
