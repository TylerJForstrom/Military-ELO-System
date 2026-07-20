"""Fail-closed contract for the Huang Chao label-policy tranche.

The three HCED rows already have complete, aligned tactical outcomes.  Their
only mechanical blocker was record precedence: resolving the coded counterpart
would materialize the raw Cliopatria Tang record before the Goguryeo lane
installed its curated payload for the same identity.  The curated Tang payload
is now pre-seeded byte-for-byte, so it wins that collision without opening a
generic Tang/China alias or changing any identity window.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

from .common import normalize_label
from .policy import HCED_LABEL_POLICIES
from .wave7_global import canonical_hced_row_sha256
from .wave8_goguryeo import WAVE8_GOGURYEO_ENTITIES


__all__ = (
    "HUANG_CHAO_CONTRACT_IDS",
    "HUANG_CHAO_FINAL_AUDIT_SIGNATURE",
    "HUANG_CHAO_FUNNEL_AUDIT",
    "HUANG_CHAO_ROW_HASHES",
    "HUANG_CHAO_TANG_PRECEDENCE_CONTRACT",
    "huang_chao_audit_signature",
    "huang_chao_metadata",
    "validate_huang_chao_queue_contracts",
    "validate_huang_chao_release",
    "validate_huang_chao_seed_precedence",
)


_LABEL = "huang chao"
_MOVEMENT = "huang_chao_rebel_movement"
_TANG = "clio_cn_tang_dyn_1_623_3e98c37b"
_TANG_CANDIDATE_ID = "cliopatria-1571"

HUANG_CHAO_ROW_HASHES: dict[str, str] = {
    "hced-Chenzhou883-1": (
        "1d91c26a31df6d36796f3cb46fcd8be51148dda0ab042082ab3a5568babfe578"
    ),
    "hced-Guangzhou879-1": (
        "710b88f41f09a976e27cb76b2f399c9c0e307350b34ae3dbab184267283361c6"
    ),
    "hced-Liangtian883-1": (
        "f3802e70ab73b78ffc8ac3ee6ede4bf80019d0d9762baa1e2fe62f710052372a"
    ),
}
HUANG_CHAO_CONTRACT_IDS = frozenset(HUANG_CHAO_ROW_HASHES)

_ROW_SEMANTICS: dict[str, dict[str, Any]] = {
    "hced-Chenzhou883-1": {
        "name": "Chenzhou",
        "year_low": 883,
        "year_high": 883,
        "side_1_raw": "China",
        "side_2_raw": "Huang Chao",
        "winner_raw": "China",
        "massacre_raw": "No",
    },
    "hced-Guangzhou879-1": {
        "name": "Guangzhou",
        "year_low": 879,
        "year_high": 879,
        "side_1_raw": "Huang Chao",
        "side_2_raw": "Tang China",
        "winner_raw": "Huang Chao",
        "massacre_raw": "Battle followed by massacre",
    },
    "hced-Liangtian883-1": {
        "name": "Liangtian",
        "year_low": 883,
        "year_high": 883,
        "side_1_raw": "Tang China",
        "side_2_raw": "Huang Chao",
        "winner_raw": "Tang China",
        "massacre_raw": "No",
    },
}

_RELEASE_OUTCOMES: dict[str, tuple[str, str]] = {
    "hced-Chenzhou883-1": (_TANG, _MOVEMENT),
    "hced-Guangzhou879-1": (_MOVEMENT, _TANG),
    "hced-Liangtian883-1": (_TANG, _MOVEMENT),
}

HUANG_CHAO_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "ce1b4ebc028cbd493d93121cf7de1d60acae8ec6050f60ad1c80b1ca5ee09d1f"
    ),
    "events_touched": 3,
    "label": _LABEL,
    "sole_blocker_events": 3,
    "zero_time_valid_candidates": 3,
}

_TANG_FIXTURE = next(
    dict(entity)
    for entity in WAVE8_GOGURYEO_ENTITIES
    if str(entity["id"]) == _TANG
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


HUANG_CHAO_TANG_PRECEDENCE_CONTRACT: dict[str, Any] = {
    "cliopatria_candidate_id": _TANG_CANDIDATE_ID,
    "entity_id": _TANG,
    "policy_entity_id": _MOVEMENT,
    "policy_window": [875, 884],
    "required_seshat_ids": ["cn_tang_dyn_1", "cn_tang_dyn_2"],
    "strategy": "curated_seed_payload_precedes_candidate_materialization",
    "tang_payload_sha256": _sha256(_TANG_FIXTURE),
    "unlocked_candidate_ids": sorted(HUANG_CHAO_CONTRACT_IDS),
}


def _signature_payload() -> dict[str, Any]:
    return {
        "funnel": HUANG_CHAO_FUNNEL_AUDIT,
        "precedence": HUANG_CHAO_TANG_PRECEDENCE_CONTRACT,
        "release_outcomes": _RELEASE_OUTCOMES,
        "row_hashes": HUANG_CHAO_ROW_HASHES,
        "row_semantics": _ROW_SEMANTICS,
    }


def huang_chao_audit_signature() -> str:
    return _sha256(_signature_payload())


HUANG_CHAO_FINAL_AUDIT_SIGNATURE = (
    "bab2a8fc764de56274f5581d1c883a791fe5954d199ff02d9d7fddd017ca98c9"
)


def _validate_static(*, check_signature: bool = True) -> None:
    if set(_ROW_SEMANTICS) != set(HUANG_CHAO_ROW_HASHES):
        raise ValueError("Huang Chao row contract inventory changed")
    if set(_RELEASE_OUTCOMES) != set(HUANG_CHAO_ROW_HASHES):
        raise ValueError("Huang Chao release outcome inventory changed")
    if HCED_LABEL_POLICIES.get(_LABEL) != ((875, 884, _MOVEMENT),):
        raise ValueError("Huang Chao label policy changed")
    if _TANG_FIXTURE.get("aliases"):
        raise ValueError("Huang Chao precedence contract opened a Tang alias")
    if check_signature and huang_chao_audit_signature() != HUANG_CHAO_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Huang Chao final audit signature changed")


def validate_huang_chao_queue_contracts(
    hced_rows: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    exact = [
        row
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == _LABEL
        or normalize_label(row.get("side_2_raw")) == _LABEL
    ]
    ids = [str(row.get("candidate_id")) for row in exact]
    if len(ids) != len(set(ids)) or set(ids) != set(HUANG_CHAO_CONTRACT_IDS):
        raise ValueError("Huang Chao exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in HUANG_CHAO_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(dict(row)) != expected_hash:
            raise ValueError(f"Huang Chao row fingerprint changed: {candidate_id}")
        if row.get("do_not_rate_automatically") is not True:
            raise ValueError(f"Huang Chao discovery safety flag changed: {candidate_id}")
        if row.get("winner_loser_complete") is not True:
            raise ValueError(f"Huang Chao outcome completeness changed: {candidate_id}")
        if any(row.get(key) != value for key, value in _ROW_SEMANTICS[candidate_id].items()):
            raise ValueError(f"Huang Chao row semantics changed: {candidate_id}")
        if row.get("winner_raw") not in {row.get("side_1_raw"), row.get("side_2_raw")}:
            raise ValueError(f"Huang Chao winner is not a named side: {candidate_id}")
    return {
        "exact_label_rows": len(exact),
        "policy_promotions": len(HUANG_CHAO_CONTRACT_IDS),
        "source_outcome_reversals": 0,
    }


def validate_huang_chao_seed_precedence(
    seed_entities: Iterable[Mapping[str, Any]],
    cliopatria_rows: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    seed = list(seed_entities)
    tang = [dict(entity) for entity in seed if str(entity.get("id")) == _TANG]
    movement = [entity for entity in seed if str(entity.get("id")) == _MOVEMENT]
    if len(tang) != 1 or tang[0] != _TANG_FIXTURE:
        raise ValueError("Huang Chao curated Tang seed precedence changed")
    if len(movement) != 1:
        raise ValueError("Huang Chao movement seed inventory changed")
    if (
        int(movement[0].get("start_year", 0)) != 875
        or int(movement[0].get("end_year", 0)) != 884
        or movement[0].get("aliases")
    ):
        raise ValueError("Huang Chao movement boundary or alias changed")

    candidates = [
        row
        for row in cliopatria_rows
        if str(row.get("candidate_id")) == _TANG_CANDIDATE_ID
    ]
    if len(candidates) != 1:
        raise ValueError("Huang Chao Tang source candidate inventory changed")
    candidate = candidates[0]
    if (
        candidate.get("canonical_name_candidate") != "Tang Dynasty"
        or int(candidate.get("start_year", 0)) != 623
        or int(candidate.get("end_year", 0)) != 910
        or sorted(map(str, candidate.get("seshat_ids", [])))
        != HUANG_CHAO_TANG_PRECEDENCE_CONTRACT["required_seshat_ids"]
        or candidate.get("do_not_rate_automatically") is not True
    ):
        raise ValueError("Huang Chao Tang source candidate semantics changed")
    return {
        "curated_seed_records": 2,
        "source_candidate_records": 1,
        "unlocked_policy_rows": len(HUANG_CHAO_CONTRACT_IDS),
    }


def validate_huang_chao_release(
    events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    matches = [
        event
        for event in events
        if str(event.get("hced_candidate_id")) in HUANG_CHAO_CONTRACT_IDS
    ]
    ids = [str(event.get("hced_candidate_id")) for event in matches]
    if len(ids) != len(set(ids)) or set(ids) != set(HUANG_CHAO_CONTRACT_IDS):
        raise ValueError("Huang Chao release ownership changed")
    for event in matches:
        candidate_id = str(event["hced_candidate_id"])
        outcomes = {
            str(participant.get("entity_id")): str(participant.get("termination"))
            for participant in event.get("participants", [])
        }
        winner, loser = _RELEASE_OUTCOMES[candidate_id]
        if outcomes != {
            winner: "engagement_victory",
            loser: "engagement_defeat",
        }:
            raise ValueError(f"Huang Chao release outcome changed: {candidate_id}")
        if (
            event.get("identity_resolution") != "label"
            or set(event.get("side_identity_resolution", {}).values())
            != {"label_policy", "seshat_crosswalk"}
            or float(event.get("confidence", -1)) != 0.64
            or event.get("event_type") != "engagement"
            or event.get("scale") != "battle"
            or event.get("date_precision") != "year"
        ):
            raise ValueError(f"Huang Chao release provenance changed: {candidate_id}")
        if any(value in {"draw", "unknown"} for value in outcomes.values()):
            raise ValueError(f"Huang Chao invented non-result: {candidate_id}")
    return {
        "label_policy_events": len(matches),
        "source_outcome_reversals": 0,
        "tactical_events": len(matches),
    }


def huang_chao_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "contract_ids": sorted(HUANG_CHAO_CONTRACT_IDS),
        "final_audit_signature": HUANG_CHAO_FINAL_AUDIT_SIGNATURE,
        "funnel_audit": HUANG_CHAO_FUNNEL_AUDIT,
        "precedence_contract": HUANG_CHAO_TANG_PRECEDENCE_CONTRACT,
    }
