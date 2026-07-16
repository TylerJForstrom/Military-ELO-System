"""Exact Wave 8 dispositions for HCED rows labelled ``Manchus``.

The source label crosses an ethnic name, the Jin state conventionally called
Later Jin, the Qing state, and particular field forces.  This lane therefore
resolves only six candidate-keyed assertions.  It opens no generic Manchu or
Jurchen identity and transfers no rating across the 1636 Jin--Qing boundary.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_MANCHUS_CONTRACT_IDS",
    "WAVE8_MANCHUS_CONTRACTS",
    "WAVE8_MANCHUS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_MANCHUS_CROSS_LANE_DISPOSITIONS",
    "WAVE8_MANCHUS_ENTITIES",
    "WAVE8_MANCHUS_EXCLUSION_IDS",
    "WAVE8_MANCHUS_EXCLUSIONS",
    "WAVE8_MANCHUS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_MANCHUS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_MANCHUS_HOLD_IDS",
    "WAVE8_MANCHUS_HOLDS",
    "WAVE8_MANCHUS_INTEGRATION_DISPOSITIONS",
    "WAVE8_MANCHUS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_MANCHUS_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_MANCHUS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_MANCHUS_OUTCOME_OVERRIDES",
    "WAVE8_MANCHUS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_MANCHUS_RESERVED_IDS",
    "WAVE8_MANCHUS_SOURCES",
    "install_wave8_manchus_entities",
    "install_wave8_manchus_sources",
    "promote_wave8_manchus_contracts",
    "validate_wave8_manchus_integration_dispositions",
    "validate_wave8_manchus_queue_contracts",
    "wave8_manchus_audit_signature",
    "wave8_manchus_cohort_counts",
    "wave8_manchus_counts",
    "wave8_manchus_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Manchus regime audit"
_EVENT_ID_PREFIX = "hced_wave8_manchus_"

_JIN_STATE_ID = "nurhaci_hong_taiji_jin_state_1616_1636"
_HONGGUANG_ID = "southern_ming_hongguang_regime_1644_1645"
_MING_ID = "clio_cn_ming_dyn_1375_80721637"
_JOSEON_ID = "joseon"
_QING_ID = "clio_cn_qing_dyn_1_1645_8a50480c"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = False,
    crosscheck: bool = False,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    if crosscheck:
        roles.append("outcome_consistency_crosscheck")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(roles),
    }


WAVE8_MANCHUS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_manchus_cambridge_qing_inner_asia",
        "The Qing and Inner Asia: 1636-1800",
        (
            "https://www.cambridge.org/core/books/abs/cambridge-history-of-"
            "inner-asia/qing-and-inner-asia-16361800/"
            "F843687E97193ED212B2CF1BDEBA3357"
        ),
        "Cambridge University Press",
        "scholarly_history_chapter",
        "cambridge_di_cosmo_qing_inner_asia",
    ),
    _source(
        "wave8_manchus_lu_huang_preqing_title",
        "A New Study of the Title of the Reigning Dynasty during the Pre-Qing Period",
        "https://doi.org/10.1163/23521341-12340146",
        "Brill, Journal of Chinese Humanities",
        "peer_reviewed_open_access_article",
        "lu_huang_preqing_dynastic_title",
    ),
    _source(
        "wave8_manchus_swope_military_collapse",
        "The Military Collapse of China's Ming Dynasty, 1618-44",
        (
            "https://www.routledge.com/The-Military-Collapse-of-Chinas-Ming-"
            "Dynasty-1618-44-1st-Edition/Swope/p/book/9780203795439"
        ),
        "Routledge",
        "scholarly_military_history_monograph",
        "swope_military_collapse_ming",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_manchus_huang_liaotung_1619",
        "The Liao-tung Campaign of 1619",
        "https://d-nb.info/1142298841/34",
        "Oriens Extremus 28.1; German National Library digital copy",
        "peer_reviewed_historical_article",
        "huang_liaotung_campaign_1619",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_manchus_ihp_saerhu_artillery",
        (
            "The Defeat in the Battle of Saerhu (1619) and the Introduction of "
            "European-style Muzzle Loading Artillery into Late-Ming China"
        ),
        "https://www1.ihp.sinica.edu.tw/en/Publications/Bulletin/62/Article/217",
        "Institute of History and Philology, Academia Sinica",
        "peer_reviewed_historical_article",
        "ihp_huang_saerhu_artillery_2008",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_manchus_kci_first_invasion_1627",
        (
            "Analysis on Combat and Negotiation Phases during the First Manchu "
            "Invasion of Choson in 1627"
        ),
        (
            "https://www.kci.go.kr/kciportal/ci/sereArticleSearch/"
            "ciSereArtiView.kci?sereArticleSearchBean.artiId=ART002839932"
        ),
        "Korea Citation Index; Institute of Korean Local History",
        "peer_reviewed_historical_article",
        "jang_first_manchu_invasion_1627",
    ),
    _source(
        "wave8_manchus_ming_history_yuan_chonghuan",
        "History of Ming: Biography of Yuan Chonghuan",
        "https://ctext.org/wiki.pl?chapter=88096&if=en",
        "Chinese Text Project digitization of the Ming Shi",
        "digitized_dynastic_history",
        "ming_shi_yuan_chonghuan",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_manchus_ncu_dalinghe",
        "Reexamining the Battle of Dalinghe: A Military Perspective",
        (
            "https://etd.lib.ncu.edu.tw/thesis/detail/"
            "90aaf0ec2c0519a411ca2f7492d37c4b/"
        ),
        "National Central University",
        "institutional_scholarly_thesis",
        "tang_dalinghe_military_thesis_2016",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_manchus_cambridge_southern_ming",
        "The Southern Ming, 1644-1662",
        (
            "https://www.cambridge.org/core/books/abs/cambridge-history-of-china/"
            "southern-ming-16441662/97FA570559404A627906FBF78D0C3A09"
        ),
        "Cambridge University Press",
        "scholarly_history_chapter",
        "cambridge_struve_southern_ming",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_manchus_wakeman_great_enterprise",
        "The Great Enterprise, Volume 1",
        "https://www.ucpress.edu/books/the-great-enterprise-volume-1/hardcover",
        "University of California Press",
        "scholarly_history_monograph",
        "wakeman_great_enterprise_volume_1",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_manchus_taiwan_waiji_yangzhou",
        "Taiwan Waiji, Volume 4 (Yangzhou and the Hongguang court)",
        "https://ctext.org/wiki.pl?chapter=907884&if=en",
        "Chinese Text Project digitization",
        "digitized_near_contemporary_chronicle",
        "taiwan_waiji_volume_4",
        outcome=True,
        crosscheck=True,
    ),
)


WAVE8_MANCHUS_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _JIN_STATE_ID,
        "name": "Jin state of Nurhaci and Hong Taiji (1616-1636)",
        "kind": "dynastic_state",
        "start_year": 1616,
        "end_year": 1636,
        "region": "Manchuria and the Liaodong frontier",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "State bounded from Nurhaci's 1616 proclamation through Hong Taiji's "
            "1636 proclamation of Great Qing. Later Jin is a historiographical "
            "convention; the reviewed official usage calls the state Jin. No rating "
            "is inherited by Jurchen or Manchu peoples, the Eight Banners, the Qing "
            "state, any earlier Jin dynasty, a field force, or a modern state."
        ),
        "source_ids": [
            "wave8_manchus_cambridge_qing_inner_asia",
            "wave8_manchus_lu_huang_preqing_title",
        ],
    },
    {
        "id": _HONGGUANG_ID,
        "name": "Southern Ming Hongguang regime (1644-1645)",
        "kind": "rump_dynastic_regime",
        "start_year": 1644,
        "end_year": 1645,
        "region": "Lower Yangzi and southern China",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "The first Southern Ming court, established at Nanjing in 1644 and "
            "collapsed in 1645. No rating is inherited by the pre-1644 Ming state, "
            "later Southern Ming courts, loyalist field armies, the Qing state, or "
            "a modern state."
        ),
        "source_ids": [
            "wave8_manchus_cambridge_southern_ming",
            "wave8_manchus_wakeman_great_enterprise",
        ],
    },
)


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str = "day",
    granularity: str = "engagement",
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": year,
        "year_high": year,
    }


_ROW_HASHES = {
    "hced-Ningyuan1626-1": (
        "6f5a9f4c5701b9256a8273c1a801efecdb49acea8ad11b17db2dfe0bb93066cf"
    ),
    "hced-Niumaozhai1619-1": (
        "8f41afd7042ed1f917d0bc7b41a7124f698b886db53d03172da5a75336df5e41"
    ),
    "hced-Pyongyang1627-1": (
        "5ced47d9c4208fa36db6496c57533c0384b56b7aa1326c4a8a2bf708e360af87"
    ),
    "hced-Shenyang1621-1": (
        "79dbfc3b6cd8f783eb166173a0fa068fa9c8346f1706335738962df7e8e10892"
    ),
    "hced-Xiaoling1631-1": (
        "b52f266740cb195d8b2a3b59235c2ab76e724f0f4e57eca9e481d2e4e870c598"
    ),
    "hced-Yangzhou1645-1": (
        "e09c803e360333bad25b07a28b39a620b20865aafe4e43cf9049c9863ce51bc7"
    ),
}


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    source_by_id = {str(source["id"]): source for source in WAVE8_MANCHUS_SOURCES}
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "result_type": "win",
        "winner_side": 1,
        "war_type": "interstate_limited",
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {str(source_by_id[source_id]["source_family_id"]) for source_id in outcomes}
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": True,
        "audit_note": audit_note,
    }


WAVE8_MANCHUS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Niumaozhai1619-1": _contract(
        "hced-Niumaozhai1619-1",
        _canonical(
            "Battle of Niumaozhai",
            1619,
            "17-20 April 1619 (Korean and Manchu records differ)",
            date_precision="day_range",
        ),
        "jin_ming_joseon_saerhu_campaign_1619",
        [_JIN_STATE_ID],
        [_MING_ID, _JOSEON_ID],
        [
            "wave8_manchus_huang_liaotung_1619",
            "wave8_manchus_ihp_saerhu_artillery",
            "wave8_manchus_swope_military_collapse",
        ],
        [
            "wave8_manchus_huang_liaotung_1619",
            "wave8_manchus_swope_military_collapse",
        ],
        (
            "Ray Huang reconstructs the destruction of Liu Ting's Chinese-Korean "
            "column at Niu-mao-chai and records the unresolved 17/20 April source "
            "difference. The opposing Korean contingent is retained as Joseon; it "
            "is not absorbed into Ming. The winner is the bounded Jin state, not a "
            "generic ethnic label. The uncertain stockade point is withheld."
        ),
        confidence=0.92,
    ),
    "hced-Shenyang1621-1": _contract(
        "hced-Shenyang1621-1",
        _canonical(
            "Battle of Shenyang",
            1621,
            "10th day of the third lunar month, 1621",
        ),
        "jin_ming_liaodong_war_1621_1631",
        [_JIN_STATE_ID],
        [_MING_ID],
        [
            "wave8_manchus_ihp_saerhu_artillery",
            "wave8_manchus_swope_military_collapse",
        ],
        [
            "wave8_manchus_ihp_saerhu_artillery",
            "wave8_manchus_swope_military_collapse",
        ],
        (
            "The reviewed histories describe a fought assault in which Nurhaci's "
            "Jin army defeated the Ming defenders and took Shenyang. The HCED city "
            "point agrees with Shenyang and is retained."
        ),
        confidence=0.91,
    ),
    "hced-Ningyuan1626-1": _contract(
        "hced-Ningyuan1626-1",
        _canonical(
            "Battle of Ningyuan",
            1626,
            "2-10 February 1626",
            date_precision="day_range",
        ),
        "jin_ming_liaodong_war_1621_1631",
        [_MING_ID],
        [_JIN_STATE_ID],
        [
            "wave8_manchus_ming_history_yuan_chonghuan",
            "wave8_manchus_swope_military_collapse",
        ],
        [
            "wave8_manchus_ming_history_yuan_chonghuan",
            "wave8_manchus_swope_military_collapse",
        ],
        (
            "The Ming garrison under Yuan Chonghuan repelled Nurhaci's Jin army; "
            "the raw Ming win therefore stands. The staged coordinate is far west "
            "of the Ningyuan/Xingcheng fortress and is withheld."
        ),
        confidence=0.94,
    ),
    "hced-Xiaoling1631-1": _contract(
        "hced-Xiaoling1631-1",
        _canonical(
            "Battle of Xiaolinghe",
            1631,
            "early October 1631",
            date_precision="month",
        ),
        "jin_ming_liaodong_war_1621_1631",
        [_JIN_STATE_ID],
        [_MING_ID],
        [
            "wave8_manchus_ncu_dalinghe",
            "wave8_manchus_swope_military_collapse",
        ],
        [
            "wave8_manchus_ncu_dalinghe",
            "wave8_manchus_swope_military_collapse",
        ],
        (
            "This is the Xiaolinghe field defeat of a Ming relief force during the "
            "Dalinghe campaign, not the whole siege. Jin forces won the competitive "
            "engagement. Because the raw point identifies only a river/campaign "
            "area rather than a reviewed battlefield, it is withheld."
        ),
        confidence=0.89,
    ),
    "hced-Yangzhou1645-1": _contract(
        "hced-Yangzhou1645-1",
        _canonical(
            "Siege of Yangzhou",
            1645,
            "city fell 20 May 1645 after a one-week siege",
        ),
        "qing_southern_ming_jiangnan_campaign_1645",
        [_QING_ID],
        [_HONGGUANG_ID],
        [
            "wave8_manchus_cambridge_southern_ming",
            "wave8_manchus_taiwan_waiji_yangzhou",
            "wave8_manchus_wakeman_great_enterprise",
        ],
        [
            "wave8_manchus_cambridge_southern_ming",
            "wave8_manchus_taiwan_waiji_yangzhou",
            "wave8_manchus_wakeman_great_enterprise",
        ],
        (
            "Qing forces breached the defended city and defeated Shi Kefa's "
            "Hongguang-regime defenders. The subsequent massacre is not treated as "
            "a second result, but it does not erase the competitive siege outcome. "
            "HCED's Qing Seshat code was attached to the losing side; the exact "
            "actor contract corrects that identity without reversing the raw winner."
        ),
        confidence=0.95,
    ),
}


WAVE8_MANCHUS_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Pyongyang1627-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Pyongyang1627-1"],
        "canonical_event": _canonical(
            "Occupation of Pyongyang",
            1627,
            "early 1627 (occupied without a fight)",
            date_precision="year",
            granularity="noncompetitive_occupation",
        ),
        "hold_category": "noncompetitive_occupation_without_battle",
        "hold_reason": (
            "Swope reports that Jin forces took Pyongyang without a fight during "
            "the 1627 invasion. A noncompetitive occupation cannot produce an Elo "
            "result, and HCED's raw Joseon loser is not converted into a battlefield "
            "opponent. No winner or loser is emitted; unknown is never made a draw."
        ),
        "evidence_refs": [
            "wave8_manchus_kci_first_invasion_1627",
            "wave8_manchus_swope_military_collapse",
        ],
    }
}

# The sole hold is a terminal exclusion from tactical Elo, not a deferred draw.
WAVE8_MANCHUS_EXCLUSIONS = WAVE8_MANCHUS_HOLDS
WAVE8_MANCHUS_CONTRACT_IDS = frozenset(WAVE8_MANCHUS_CONTRACTS)
WAVE8_MANCHUS_HOLD_IDS = frozenset(WAVE8_MANCHUS_HOLDS)
WAVE8_MANCHUS_EXCLUSION_IDS = WAVE8_MANCHUS_HOLD_IDS
WAVE8_MANCHUS_RESERVED_IDS = WAVE8_MANCHUS_CONTRACT_IDS | WAVE8_MANCHUS_HOLD_IDS
WAVE8_MANCHUS_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


# Niumaozhai is not securely geocoded, Ningyuan's point is far west of the
# fortress, and Xiaolinghe is a river/campaign-area assertion. Country fields
# remain valid. Shenyang and Yangzhou are retained as reviewed city points.
WAVE8_MANCHUS_POINT_QUARANTINE_ADDITIONS = frozenset(
    {
        "hced-Ningyuan1626-1",
        "hced-Niumaozhai1619-1",
        "hced-Xiaoling1631-1",
    }
)
WAVE8_MANCHUS_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_MANCHUS_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_MANCHUS_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_MANCHUS_COUNTRY_QUARANTINE_ADDITIONS,
}


# All five promoted outcomes agree with the raw side ordering. The work is
# identity correction, not result reversal.
WAVE8_MANCHUS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


# The locked IWBD snapshot begins in 1823 and has no same-name/same-year twin.
# These aliases make a future probable twin fail closed until it is adjudicated.
WAVE8_MANCHUS_IWBD_ZERO_OVERLAP_AUDIT: dict[str, tuple[str, ...]] = {
    "1619": ("battle of niu mao chai", "battle of niumaozhai", "niumaozhai"),
    "1621": ("battle of shenyang", "capture of shenyang", "shenyang"),
    "1626": ("battle of ningyuan", "ningyuan"),
    "1627": ("occupation of pyongyang", "pyongyang"),
    "1631": (
        "battle of xiaoling",
        "battle of xiaolinghe",
        "xiaoling",
        "xiaolinghe",
    ),
    "1645": ("siege of yangzhou", "yangzhou"),
}
WAVE8_MANCHUS_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_MANCHUS_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_MANCHUS_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_MANCHUS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_MANCHUS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_MANCHUS_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_MANCHUS_ENTITIES,
        "expected_candidate_ids": sorted(WAVE8_MANCHUS_EXPECTED_CANDIDATE_IDS),
        "holds": WAVE8_MANCHUS_HOLDS,
        "integration_dispositions": WAVE8_MANCHUS_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_MANCHUS_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_MANCHUS_IWBD_ZERO_OVERLAP_AUDIT,
        "outcome_overrides": WAVE8_MANCHUS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_MANCHUS_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_MANCHUS_SOURCES,
    }


def wave8_manchus_audit_signature() -> str:
    """Return the SHA-256 pin over the complete audited lane state."""

    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_MANCHUS_FINAL_AUDIT_SIGNATURE = (
    "4657b9676c73dbb94075a460b6c01a240efee05128c2bf6e5c13a5a1cd0944cc"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (len(WAVE8_MANCHUS_CONTRACTS), len(WAVE8_MANCHUS_HOLDS)) != (5, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_MANCHUS_ENTITIES), len(WAVE8_MANCHUS_SOURCES)) != (2, 11):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_MANCHUS_RESERVED_IDS != WAVE8_MANCHUS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if WAVE8_MANCHUS_CONTRACT_IDS & WAVE8_MANCHUS_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotions and holds overlap")
    if WAVE8_MANCHUS_EXCLUSIONS is not WAVE8_MANCHUS_HOLDS:
        raise ValueError(f"{_LANE_NAME} exclusion inventory diverged")
    if wave8_manchus_audit_signature() != WAVE8_MANCHUS_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_MANCHUS_SOURCES}
    if len(source_by_id) != len(WAVE8_MANCHUS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    families = [str(source["source_family_id"]) for source in WAVE8_MANCHUS_SOURCES]
    if len(families) != len(set(families)):
        raise ValueError(f"{_LANE_NAME} source families are not independent")
    for source in WAVE8_MANCHUS_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_MANCHUS_ENTITIES}
    expected_windows = {
        _JIN_STATE_ID: (1616, 1636),
        _HONGGUANG_ID: (1644, 1645),
    }
    if set(entity_by_id) != set(expected_windows):
        raise ValueError(f"{_LANE_NAME} identity inventory changed")
    for entity_id, entity in entity_by_id.items():
        if (entity["start_year"], entity["end_year"]) != expected_windows[entity_id]:
            raise ValueError(f"{_LANE_NAME} identity window changed")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        note = str(entity["continuity_note"]).casefold()
        if "no rating is inherited" not in note or "modern state" not in note:
            raise ValueError(f"{_LANE_NAME} identity permits rating inheritance")
        if normalize_label(entity["name"]) in {"jurchen", "manchu", "manchus"}:
            raise ValueError(f"{_LANE_NAME} installed a timeless ethnic identity")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    allowed_entities = {_MING_ID, _JOSEON_ID, _QING_ID, *entity_by_id}
    used_new_entities: set[str] = set()
    used_sources: set[str] = set()
    expected_precisions = {
        "hced-Ningyuan1626-1": "day_range",
        "hced-Niumaozhai1619-1": "day_range",
        "hced-Shenyang1621-1": "day",
        "hced-Xiaoling1631-1": "month",
        "hced-Yangzhou1645-1": "day",
    }
    for candidate_id, contract in WAVE8_MANCHUS_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} queue hash table drifted")
        row_hash = str(contract["raw_row_sha256"])
        if len(row_hash) != 64 or any(c not in "0123456789abcdef" for c in row_hash):
            raise ValueError(f"{_LANE_NAME} has an invalid queue hash")

        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        if canonical["granularity"] != "engagement":
            raise ValueError(f"{_LANE_NAME} promoted a non-engagement")
        if canonical["date_precision"] != expected_precisions[candidate_id]:
            raise ValueError(f"{_LANE_NAME} canonical date precision drifted")

        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} side inventory is not canonical")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (set(side_1) | set(side_2)) <= allowed_entities:
            raise ValueError(f"{_LANE_NAME} uses an unknown identity")
        if any(
            normalize_label(entity_id) in {"jurchen", "manchu", "manchus"}
            for entity_id in (*side_1, *side_2)
        ):
            raise ValueError(f"{_LANE_NAME} rates a generic ethnic label")
        used_new_entities.update((set(side_1) | set(side_2)) & set(entity_by_id))
        year = int(canonical["year_low"])
        for entity_id in (set(side_1) | set(side_2)) & set(entity_by_id):
            start, end = expected_windows[entity_id]
            if not start <= year <= end:
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")

        if contract["result_type"] != "win" or contract["winner_side"] != 1:
            raise ValueError(f"{_LANE_NAME} invented a draw or unknown result")
        if contract["war_type"] != "interstate_limited":
            raise ValueError(f"{_LANE_NAME} war-type contract drifted")
        if contract["actor_override"] is not True:
            raise ValueError(f"{_LANE_NAME} actor correction is not explicit")
        if contract["source_outcome_override"] is not False:
            raise ValueError(f"{_LANE_NAME} contains an outcome override")
        if contract["outcome_reversal"] is not False:
            raise ValueError(f"{_LANE_NAME} contains an outcome reversal")

        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} evidence provenance drifted")
        if not outcomes or not _is_sorted_unique(outcomes) or not set(outcomes) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source for a result")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome family provenance drifted")
        used_sources.update(evidence)

    if used_new_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new entities are not exactly consumed")

    forbidden_hold_keys = {
        "losers",
        "outcome_source_family_ids",
        "outcome_source_ids",
        "result_type",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "winner_side",
        "winners",
    }
    for candidate_id, hold in WAVE8_MANCHUS_HOLDS.items():
        if hold["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} hold hash table drifted")
        if forbidden_hold_keys & set(hold):
            raise ValueError(f"{_LANE_NAME} hold contains a rateable result")
        canonical = hold["canonical_event"]
        if canonical["granularity"] != "noncompetitive_occupation":
            raise ValueError(f"{_LANE_NAME} hold granularity drifted")
        reason = str(hold["hold_reason"]).casefold()
        for phrase in ("without a fight", "cannot produce an elo", "never made a draw"):
            if phrase not in reason:
                raise ValueError(f"{_LANE_NAME} hold rationale is incomplete")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} hold evidence drifted")
        used_sources.update(evidence)

    used_sources.update(
        source_id
        for entity in WAVE8_MANCHUS_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    expected_points = {
        "hced-Ningyuan1626-1",
        "hced-Niumaozhai1619-1",
        "hced-Xiaoling1631-1",
    }
    if WAVE8_MANCHUS_POINT_QUARANTINE_ADDITIONS != expected_points:
        raise ValueError(f"{_LANE_NAME} point quarantine contract changed")
    if WAVE8_MANCHUS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country quarantine contract changed")
    if not expected_points <= WAVE8_MANCHUS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} quarantine references an unpromoted row")
    if (
        WAVE8_MANCHUS_OUTCOME_OVERRIDES
        or WAVE8_MANCHUS_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_MANCHUS_CROSS_LANE_DISPOSITIONS
        or WAVE8_MANCHUS_INTEGRATION_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty disposition inventory changed")

    if set(WAVE8_MANCHUS_IWBD_ZERO_OVERLAP_AUDIT) != {
        "1619",
        "1621",
        "1626",
        "1627",
        "1631",
        "1645",
    }:
        raise ValueError(f"{_LANE_NAME} IWBD zero-overlap years changed")
    for aliases in WAVE8_MANCHUS_IWBD_ZERO_OVERLAP_AUDIT.values():
        if not _is_sorted_unique(aliases):
            raise ValueError(f"{_LANE_NAME} IWBD zero-overlap aliases drifted")


def _is_exact_manchus_label(value: Any) -> bool:
    return normalize_label(value) == "manchus"


def validate_wave8_manchus_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate the six-row exact-label inventory and every row fingerprint."""

    _validate_static()
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_MANCHUS_CONTRACTS,
        WAVE8_MANCHUS_HOLDS,
        lane_name=_LANE_NAME,
    )
    exact_label_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_manchus_label(row.get("side_1_raw"))
        or _is_exact_manchus_label(row.get("side_2_raw"))
    }
    if exact_label_ids != WAVE8_MANCHUS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Manchus inventory changed: "
            f"{sorted(exact_label_ids)}"
        )
    return counts


def _iwbd_year(row: Mapping[str, Any]) -> int | None:
    for field in ("start_date", "end_date"):
        value = row.get(field)
        if isinstance(value, str) and len(value) >= 4 and value[:4].isdigit():
            return int(value[:4])
    value = row.get("year")
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def validate_wave8_manchus_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Fail closed if a future IWBD snapshot adds a probable reviewed-event twin."""

    validate_wave8_manchus_queue_contracts(hced_rows)
    audited = {
        (int(year), normalize_label(name))
        for year, names in WAVE8_MANCHUS_IWBD_ZERO_OVERLAP_AUDIT.items()
        for name in names
    }
    collisions = []
    for row in iwbd_rows:
        year = _iwbd_year(row)
        name = normalize_label(row.get("name"))
        if year is not None and (year, name) in audited:
            collisions.append(str(row.get("candidate_id") or "<missing-id>"))
    if collisions:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD duplicate(s): "
            f"{sorted(collisions)}"
        )
    return {
        "cross_lane_hced_dispositions": 0,
        "integration_dispositions": 0,
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
    }


def install_wave8_manchus_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_MANCHUS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_manchus_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_MANCHUS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_MANCHUS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_MANCHUS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_manchus_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_manchus_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_MANCHUS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_manchus_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_MANCHUS_CONTRACTS.values()
            ).items()
        )
    )


def wave8_manchus_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_MANCHUS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_MANCHUS_CROSS_LANE_DISPOSITIONS
        ),
        "holds": len(WAVE8_MANCHUS_HOLDS),
        "integration_dispositions": len(WAVE8_MANCHUS_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_MANCHUS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_MANCHUS_ENTITIES),
        "new_sources": len(WAVE8_MANCHUS_SOURCES),
        "newly_rated_events": len(WAVE8_MANCHUS_CONTRACTS),
        "outcome_overrides": len(WAVE8_MANCHUS_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_MANCHUS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_MANCHUS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_MANCHUS_RESERVED_IDS),
    }


def wave8_manchus_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_MANCHUS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_MANCHUS_POINT_QUARANTINE_ADDITIONS,
    }
