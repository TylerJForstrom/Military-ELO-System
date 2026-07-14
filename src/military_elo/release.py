from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any, Iterable


SEED_CODE_POLICIES: dict[str, tuple[tuple[int, int, str], ...]] = {
    "ir_achaemenid_emp": ((-550, -330, "achaemenid_empire"),),
    "ir_archaemenid_emp": ((-550, -330, "achaemenid_empire"),),
    "tn_carthage_emp": ((-650, -146, "carthage"),),
    "it_roman_rep_1": ((-509, -27, "roman_republic"),),
    "it_roman_rep_2": ((-509, -27, "roman_republic"),),
    "it_roman_rep_3": ((-509, -27, "roman_republic"),),
    "it_roman_principate": ((-27, 286, "roman_empire"),),
    "it_roman_dominate": ((287, 394, "roman_empire"),),
    "tr_roman_dominate": ((287, 394, "roman_empire"),),
    "tr_east_roman_emp": ((395, 625, "byzantine_empire"),),
    "tr_byzantine_emp_1": ((395, 1453, "byzantine_empire"),),
    "tr_byzantine_emp_2": ((395, 1453, "byzantine_empire"),),
    "tr_byzantine_emp_3": ((395, 1453, "byzantine_empire"),),
    "ir_sassanian_emp_1": ((224, 651, "sasanian_empire"),),
    "ir_sassanian_emp_2": ((224, 651, "sasanian_empire"),),
    "sy_umayyad_cal": ((661, 750, "umayyad_caliphate"),),
    "fr_carolingian_emp_1": ((481, 843, "frankish_kingdom"),),
    "fr_carolingian_emp_2": ((481, 843, "frankish_kingdom"),),
    "gr_macedonian_emp": ((-336, -323, "macedonian_empire"),),
    "mn_mongol_emp": ((1206, 1294, "mongol_empire"),),
    "eg_mamluk_sultanate_1": ((1250, 1517, "mamluk_sultanate"),),
    "eg_mamluk_sultanate_3": ((1250, 1517, "mamluk_sultanate"),),
    "tr_ottoman_emp_1": ((1299, 1922, "ottoman_empire"),),
    "tr_ottoman_emp_2": ((1299, 1922, "ottoman_empire"),),
    "tr_ottoman_emp_3": ((1299, 1922, "ottoman_empire"),),
    "tr_ottoman_emp_4": ((1299, 1922, "ottoman_empire"),),
    "ir_safavid_emp": ((1501, 1736, "safavid_empire"),),
    "in_mughal_emp": ((1526, 1857, "mughal_empire"),),
    "es_spanish_emp_1": ((1479, 1898, "spanish_empire"),),
    "es_spanish_emp_2": ((1479, 1898, "spanish_empire"),),
    "es_spanish_emp_3": ((1479, 1898, "spanish_empire"),),
    "fr_valois_k_1": ((987, 1792, "kingdom_france"),),
    "fr_valois_k_2": ((987, 1792, "kingdom_france"),),
    "fr_bourbon_k_1": ((987, 1792, "kingdom_france"),),
    "fr_bourbon_k_2": (
        (987, 1792, "kingdom_france"),
        (1804, 1815, "first_french_empire"),
    ),
    "gb_british_emp_1": ((1707, 2026, "united_kingdom"),),
    "gb_british_emp_2": ((1707, 2026, "united_kingdom"),),
    "ru_romanov_dyn_1": ((1721, 1917, "russian_empire"),),
    "ru_romanov_dyn_2": ((1721, 1917, "russian_empire"),),
    "de_german_reich_2": ((1871, 1918, "german_empire"),),
    "de_third_reich": ((1933, 1945, "nazi_germany"),),
    "jp_japanese_emp": ((1868, 1947, "empire_japan"),),
    "ru_soviet_union": ((1922, 1991, "soviet_union"),),
    "us_antebellum": ((1776, 2026, "united_states"),),
    "us_united_states_of_america_reconstruction": ((1776, 2026, "united_states"),),
    "us_united_states_contemporary": ((1776, 2026, "united_states"),),
    "us_united_states_of_america_contemporary": ((1776, 2026, "united_states"),),
    "vt_vietnam_democratic_rep": ((1945, 1976, "north_vietnam"),),
    "vt_vietnam_rep": ((1955, 1975, "south_vietnam"),),
    "cn_chinese_peoples_rep": ((1949, 2026, "peoples_republic_china"),),
}

# Explicit, time-bounded identity policy for IWD/COW country codes whose source
# label does not name the historical polity directly. COW code 365 labels both
# the Russian Empire and the Soviet Union as "Russia"; the 1918-1921
# revolutionary era is deliberately absent so wars from that period stay staged
# instead of being attached to either neighboring identity.
IWD_COW_CODE_POLICIES: dict[str, tuple[tuple[int, int, str], ...]] = {
    "365": (
        (1721, 1917, "russian_empire"),
        (1922, 1991, "soviet_union"),
    ),
}

# Explicit, time-bounded identity policies for bare HCED side labels that lack
# Seshat coding. A policy label is authoritative: outside its windows the side
# stays staged instead of falling through to alias matching. Deliberate gaps
# (France 1793-1803 and 1816-1957, Russia pre-1721 and 1918-1921, Persia
# -329..223 and post-1736) keep events from eras without a curated identity
# staged rather than attached to a neighboring regime.
HCED_LABEL_POLICIES: dict[str, tuple[tuple[int, int, str], ...]] = {
    "france": (
        (987, 1792, "kingdom_france"),
        (1804, 1815, "first_french_empire"),
        (1958, 2026, "french_fifth_republic"),
    ),
    "russia": (
        (1721, 1917, "russian_empire"),
        (1922, 1991, "soviet_union"),
    ),
    "spain": ((1479, 1898, "spanish_empire"),),
    "rome": ((-509, -27, "roman_republic"), (-27, 394, "roman_empire")),
    "romans": ((-509, -27, "roman_republic"), (-27, 394, "roman_empire")),
    "byzantium": ((395, 1453, "byzantine_empire"),),
    "byzantines": ((395, 1453, "byzantine_empire"),),
    "persia": (
        (-550, -330, "achaemenid_empire"),
        (224, 651, "sasanian_empire"),
        (1501, 1736, "safavid_empire"),
    ),
    "ottomans": ((1299, 1922, "ottoman_empire"),),
}

# Faction, party, movement, and collective-peoples labels are not time-bounded
# polities (the rating unit is a versioned polity or autonomous military actor,
# never a peoples name). The blocklist is checked before every alias tier so
# these labels cannot resolve even when a source record carries a colliding
# alias; promoting one later requires an explicit HCED_LABEL_POLICIES entry
# mapping it to a curated identity.
HCED_FACTION_LABELS: frozenset[str] = frozenset({
    # war-faction / party / movement labels
    "royalists", "parliamentarians", "carlists", "taiping", "indian rebels",
    "chinese communists", "chinese nationalists", "kuomintang", "guomindang",
    "spanish republicans", "spanish nationalists", "communists", "nationalists",
    "republicans", "loyalists", "rebels", "insurgents", "jacobites",
    "huguenots", "catholics", "protestants", "covenanters", "confederates",
    "unionists", "boxers", "whites", "reds", "bolsheviks", "mujahideen",
    # collective-peoples labels with no unique time-bounded polity referent
    "vikings", "norsemen", "danes", "tatars", "crusaders", "moors",
    "berbers", "cossacks", "palestinians", "barbary pirates", "pirates",
    "saxons", "huns", "white huns", "mongols", "ostrogoths", "visigoths",
    "goths", "vandals", "franks", "avars", "magyars", "gauls", "celts",
    "slavs", "picts", "normans", "bulgars", "pechenegs", "cumans", "khazars",
    "alans", "lombards", "angles", "jutes", "britons", "scythians",
    "sarmatians", "xiongnu", "arabs", "turks", "germans", "greeks",
    "zulus", "sikhs", "maori", "comanche", "sioux", "cherokee",
    "apache", "seminole",
})

# Genuine polity names whose only time-valid Cliopatria identity is a
# multi-regime envelope (for example one Sweden identity spanning 980-2024):
# full-interval containment is vacuous against such a span, so resolving the
# label would manufacture rating continuity across regime boundaries. These
# stay staged under their own counter until curated identity splits exist.
HCED_PENDING_SPLIT_LABELS: frozenset[str] = frozenset({
    "sweden",
    "georgia",
    "champa",
    "switzerland",
    "swiss confederation",
    "tibet",
})

# Coalition and composite battle-side labels are not rating units: coalition
# sides need curated per-participant composition, and slash/comma/parenthesis
# composites are ambiguous between alias and coalition — ambiguity always
# stays staged.
IWBD_COALITION_SIDE_LABELS: frozenset[str] = frozenset({
    "allies",
    "allied powers",
    "axis",
    "central powers",
    "balkan league",
    "coalition",
    "nato",
    "arab states",
})

# Declared identity deny windows for IWBD belligerent labels: within a window
# the label is never resolved, because it denotes an actor distinct from the
# identity the resolver would return. "Turkey" in 1920-1923 denotes the Ankara
# (Kemalist) government fighting in parallel with the Istanbul government, and
# must not attach to the ottoman_empire identity whose interval still covers
# those years.
IWBD_IDENTITY_DENY_WINDOWS: dict[str, tuple[tuple[int, int], ...]] = {
    "turkey": ((1920, 1923),),
}

_IWBD_CANDIDATE_ID = re.compile(r"^iwbd-(-?\d+)-(-?\d+)-(\d+)$")

# Every declared rejection counter per promotion path, including gates that
# measure zero on the current snapshot: a zero gate is a declared guard, and
# the published artifact must distinguish "declared and measured zero" from
# "not implemented".
HCED_LABEL_REJECTION_COUNTERS: tuple[str, ...] = (
    "label_outcome_not_aligned",
    "outside_continuity_policy",
    "no_unique_time_valid_polity",
    "blank_side_label",
    "faction_label_not_a_polity",
    "label_pending_identity_split",
    "label_outside_policy_window",
    "no_unique_time_valid_label_match",
    "same_or_empty_opposing_side",
    "duplicate_of_curated_seed",
    "duplicate_of_promoted_event",
)

IWBD_REJECTION_COUNTERS: tuple[str, ...] = (
    "missing_battle_name",
    "missing_or_invalid_date",
    "missing_belligerent_label",
    "duplicate_within_iwbd",
    "duplicate_of_curated_seed",
    "duplicate_of_hced_battle",
    "malformed_candidate_id",
    "contains_constituent_iwbd_rows",
    "outcome_not_aligned_to_battle_sides",
    "coalition_or_composite_side",
    "unresolved_time_bounded_belligerent",
    "same_or_empty_opposing_side",
)

UCDP_REJECTION_COUNTERS: tuple[str, ...] = (
    "malformed_source_row",
    "not_terminal_episode",
    "outcome_peace_agreement",
    "outcome_ceasefire",
    "outcome_low_activity",
    "outcome_actor_ceased",
    "outcome_missing_or_unknown",
    "missing_or_invalid_episode_years",
    "nonstate_primary_party",
    "unresolved_time_bounded_party",
    "same_or_empty_opposing_side",
    "documented_side_attribution_dispute",
    "duplicate_of_promoted_strategic_event",
    "dyad_conflict_outcome_contradiction",
    "contradictory_linked_episode_outcomes",
)


def _declared_rejections(
    rejections: Counter[str], declared: tuple[str, ...]
) -> dict[str, int]:
    return {key: rejections.get(key, 0) for key in sorted({*rejections, *declared})}

# Explicit, time-bounded identity policies for UCDP Gleditsch-Ward codes whose
# label does not name the historical polity directly. A policy code is
# authoritative: outside its windows the party stays unresolved instead of
# falling back to name matching. Deliberate gaps: GW 365 omits 1918-1921 and
# 1992+ (revolutionary era and the post-Soviet federation have no curated
# identity); GW 816 omits post-unification years; GW 700 omits 1979-1995 and
# 2002-2003 because the DRA and the transitional administrations have no
# curated identity — Cliopatria's blanket "Afghanistan 1979-2024" polity would
# bridge four regimes, which namesake continuity rules forbid.
UCDP_GW_CODE_POLICIES: dict[str, tuple[tuple[int, int, str], ...]] = {
    "365": (
        (1721, 1917, "russian_empire"),
        (1922, 1991, "soviet_union"),
    ),
    "816": ((1945, 1976, "north_vietnam"),),
    "817": ((1955, 1975, "south_vietnam"),),
    "700": (
        (1996, 2001, "taliban"),
        (2004, 2021, "islamic_republic_afghanistan"),
    ),
}

# Curated exclusions for UCDP termination episodes with a documented
# side-attribution dispute: promoting the source's coding would assign a rated
# outcome to a polity that may not have fought. Ambiguity between time-bounded
# identities always stays staged for human review.
UCDP_CURATED_EXCLUSIONS: dict[tuple[str, str], str] = {
    ("334", "1"): (
        "side_attribution_dispute: UCDP codes the 1974 episode (Battle of the "
        "Paracel Islands) against the DRV (gwno 816, 'Government of Vietnam "
        "(North Vietnam)'), but historical accounts attribute the engagement "
        "to the Republic of Vietnam Navy (GW 817). Which registry identity "
        "opposed China is ambiguous between two time-bounded identities; "
        "ambiguity always fails. Staged for human review."
    ),
}


def _cow_policy_seed_id(code: str, low_year: int, high_year: int) -> str | None:
    policies = IWD_COW_CODE_POLICIES.get(code)
    if not policies:
        return None
    matches = [
        entity_id
        for start_year, end_year, entity_id in policies
        if low_year >= start_year and high_year <= end_year
    ]
    return matches[0] if len(set(matches)) == 1 else None


def _label_policy_seed_id(label: str, low_year: int, high_year: int) -> str | None:
    matches = [
        entity_id
        for start_year, end_year, entity_id in HCED_LABEL_POLICIES.get(label, ())
        if low_year >= start_year and high_year <= end_year
    ]
    return matches[0] if len(set(matches)) == 1 else None


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def _write_json(path: str | Path, value: object) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def normalize_label(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(character for character in text if not unicodedata.combining(character))
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def _slug(value: str, maximum: int = 54) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", normalize_label(value)).strip("_")
    return (slug or "polity")[:maximum].rstrip("_")


def _event_key(name: str, year: int) -> tuple[str, int]:
    normalized = normalize_label(name)
    normalized = re.sub(r"^(battle|siege|campaign|war) (of |at )?", "", normalized)
    return normalized, year


def _candidate_entity_id(candidate: dict[str, Any]) -> str:
    identifiers = (
        list(candidate.get("seshat_ids", []))
        or list(candidate.get("wikidata_ids", []))
        or [str(candidate.get("canonical_name_candidate", "polity"))]
    )
    identity = "|".join(
        [
            *map(str, identifiers),
            str(candidate.get("canonical_name_candidate", "")),
            str(candidate.get("start_year", "")),
            str(candidate.get("end_year", "")),
        ]
    )
    digest = hashlib.sha1(identity.encode("utf-8")).hexdigest()[:8]
    year = int(candidate["start_year"])
    year_token = f"bce{abs(year)}" if year < 0 else str(year)
    return f"clio_{_slug(str(identifiers[0]))}_{year_token}_{digest}"


def _infer_kind(name: str) -> str:
    lowered = normalize_label(name)
    for token, kind in (
        ("city state", "city_state"),
        ("empire", "empire"),
        ("caliphate", "caliphate"),
        ("sultanate", "sultanate"),
        ("khanate", "khanate"),
        ("kingdom", "kingdom"),
        ("republic", "republic"),
        ("confeder", "confederation"),
        ("dynasty", "dynastic_state"),
    ):
        if token in lowered:
            return kind
    return "polity"


def _policy_seed_id(code: str, low_year: int, high_year: int) -> str | None:
    policies = SEED_CODE_POLICIES.get(code)
    if not policies:
        return None
    matches = [
        entity_id
        for start_year, end_year, entity_id in policies
        if low_year >= start_year and high_year <= end_year
    ]
    return matches[0] if len(set(matches)) == 1 else None


def _normalized_labels(labels: Iterable[Any]) -> set[str]:
    normalized = {normalize_label(label) for label in labels}
    normalized.discard("")
    return normalized


def _candidate_labels(candidate: dict[str, Any]) -> set[str]:
    return _normalized_labels(
        [
            candidate.get("canonical_name_candidate"),
            *candidate.get("aliases", []),
            *candidate.get("wikipedia_titles", []),
        ]
    )


def _seed_entity_labels(entity: dict[str, Any]) -> set[str]:
    return _normalized_labels([entity.get("name"), *entity.get("aliases", [])])


def _candidate_overlaps_entity(candidate: dict[str, Any], entity: dict[str, Any]) -> bool:
    entity_end = entity.get("end_year")
    return int(candidate["end_year"]) >= int(entity["start_year"]) and (
        entity_end is None or int(candidate["start_year"]) <= int(entity_end)
    )


def _candidate_policy_seed(
    candidate: dict[str, Any],
    seed_by_id: dict[str, dict[str, Any]],
) -> str | None:
    start = int(candidate["start_year"])
    end = int(candidate["end_year"])
    matches: set[str] = set()
    for code in candidate.get("seshat_ids", []):
        for policy_start, policy_end, entity_id in SEED_CODE_POLICIES.get(code, ()):
            overlap = max(0, min(end, policy_end) - max(start, policy_start) + 1)
            duration = max(1, end - start + 1)
            if overlap / duration >= 0.80:
                matches.add(entity_id)
    if len(matches) != 1:
        return None
    mapped_seed = next(iter(matches))
    seed_entity = seed_by_id.get(mapped_seed)
    # Vassal and client polities can carry the sovereign's crosswalk codes, so
    # a code-window match alone must not merge a distinct polity (for example
    # the Duchy of Burgundy) into the seed identity; the candidate also has to
    # share one of the seed's names.
    if not seed_entity or not (_candidate_labels(candidate) & _seed_entity_labels(seed_entity)):
        return None
    return mapped_seed


def _resolve_code(
    code: str,
    low_year: int,
    high_year: int,
    owners: dict[str, list[dict[str, Any]]],
) -> tuple[str | None, dict[str, Any] | None, str | None]:
    if code in SEED_CODE_POLICIES:
        seed_id = _policy_seed_id(code, low_year, high_year)
        return seed_id, None, None if seed_id else "outside_continuity_policy"

    active = [
        candidate
        for candidate in owners.get(code, [])
        if int(candidate["start_year"]) <= low_year
        and int(candidate["end_year"]) >= high_year
    ]
    if len(active) != 1:
        return None, None, "no_unique_time_valid_polity"
    return _candidate_entity_id(active[0]), active[0], None


def _scale(candidate: dict[str, Any]) -> tuple[str, int]:
    raw = candidate.get("scale_raw") or candidate.get("scale_inferred_raw")
    try:
        level = max(1, min(5, int(float(raw))))
    except (TypeError, ValueError):
        level = 2
    if level <= 1:
        return "skirmish", level
    if level <= 3:
        return "battle", level
    if level == 4:
        return "campaign", level
    return "theater", level


def _domain(value: Any) -> str:
    normalized = normalize_label(value)
    domains: set[str] = set()
    if any(token in normalized for token in ("sea", "naval", "maritime", "water")):
        domains.add("naval")
    if "air" in normalized:
        domains.add("air")
    if any(token in normalized for token in ("land", "ground")):
        domains.add("land")
    return next(iter(domains)) if len(domains) == 1 else "mixed"


def _participants(
    side_a: list[str],
    side_b: list[str],
    draw: bool,
    confidence: float,
    scale_level: int,
    note: str | None = None,
) -> list[dict[str, Any]]:
    if draw:
        winner_values = {
            "battlefield_control": 0.50,
            "mission_objective": 0.50,
            "force_preservation": 0.50,
            "positional_gain": 0.50,
        }
        loser_values = dict(winner_values)
        winner_class = loser_class = "stalemate_or_inconclusive"
        termination = "inconclusive_engagement"
    else:
        margin = min(0.40, 0.22 + 0.035 * scale_level)
        winner_values = {
            "battlefield_control": 0.50 + margin,
            "mission_objective": 0.48 + margin,
            "force_preservation": 0.50 + margin * 0.45,
            "positional_gain": 0.48 + margin * 0.75,
        }
        loser_values = {key: 1.0 - value for key, value in winner_values.items()}
        winner_class = "major_tactical_victory" if scale_level >= 4 else "limited_victory"
        loser_class = "major_tactical_defeat" if scale_level >= 4 else "limited_defeat"
        termination = "engagement_victory"

    output: list[dict[str, Any]] = []
    for side, entity_ids, outcome, result_class, side_termination in (
        ("side_a", side_a, winner_values, winner_class, termination),
        (
            "side_b",
            side_b,
            loser_values,
            loser_class,
            termination if draw else "engagement_defeat",
        ),
    ):
        contribution = round(1.0 / len(entity_ids), 4)
        for entity_id in entity_ids:
            output.append(
                {
                    "entity_id": entity_id,
                    "side": side,
                    "role": "primary" if len(entity_ids) == 1 else "major_ally",
                    "contribution": contribution,
                    "stakes": 0.50 if scale_level < 4 else 0.68,
                    "national_scale": min(0.75, 0.12 + 0.10 * scale_level),
                    "termination": side_termination,
                    "evidence_confidence": confidence,
                    "result_class": result_class,
                    "outcome": outcome,
                    "note": note
                    or "Provisional HCED tactical coding; strategic war outcome is not inferred.",
                }
            )
    return output


def _strategic_participants(
    side_a: list[str],
    side_b: list[str],
    outcome: str,
    confidence: float,
    *,
    stakes: float = 0.72,
    national_scale: float = 0.72,
    note: str | None = None,
) -> list[dict[str, Any]]:
    draw_values = {
        "battlefield_outcome": 0.50,
        "political_objectives": 0.50,
        "territorial_outcome": 0.50,
        "sovereignty_survival": 0.95,
        "settlement_durability": 0.50,
        "force_preservation": 0.50,
    }
    victor_values = {
        "battlefield_outcome": 0.80,
        "political_objectives": 0.76,
        "territorial_outcome": 0.66,
        "sovereignty_survival": 0.96,
        "settlement_durability": 0.70,
        "force_preservation": 0.62,
    }
    defeated_values = {
        "battlefield_outcome": 0.20,
        "political_objectives": 0.24,
        "territorial_outcome": 0.34,
        "sovereignty_survival": 0.78,
        "settlement_durability": 0.30,
        "force_preservation": 0.38,
    }
    if outcome == "draw":
        side_values = (draw_values, draw_values)
        result_classes = ("stalemate_or_inconclusive", "stalemate_or_inconclusive")
        terminations = ("draw", "draw")
    elif outcome == "side_a":
        side_values = (victor_values, defeated_values)
        result_classes = ("limited_victory", "limited_defeat")
        terminations = ("victory", "defeat")
    else:
        side_values = (defeated_values, victor_values)
        result_classes = ("limited_defeat", "limited_victory")
        terminations = ("defeat", "victory")

    output: list[dict[str, Any]] = []
    for index, (side, entity_ids) in enumerate((("side_a", side_a), ("side_b", side_b))):
        contribution = round(1.0 / len(entity_ids), 4)
        for entity_id in entity_ids:
            output.append(
                {
                    "entity_id": entity_id,
                    "side": side,
                    "role": "primary" if len(entity_ids) == 1 else "major_ally",
                    "contribution": contribution,
                    "stakes": stakes,
                    "national_scale": national_scale,
                    "termination": terminations[index],
                    "evidence_confidence": confidence,
                    "result_class": result_classes[index],
                    "outcome": side_values[index],
                    "note": note
                    or (
                        "Coalition-aggregated IWD parent-war outcome; existential or "
                        "regime-ending severity is never inferred from IWD outcome codes."
                    ),
                }
            )
    return output


_WAR_NUMERAL_TOKENS = {
    "first": "1",
    "second": "2",
    "third": "3",
    "fourth": "4",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "i": "1",
    "ii": "2",
    "iii": "3",
    "iv": "4",
}
_WAR_STOP_TOKENS = {"war", "wars", "the", "of", "in", "on", "and"}


def _war_tokens(value: Any) -> frozenset[str]:
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", str(value or ""))
    text = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", text)
    tokens: set[str] = set()
    for token in normalize_label(text).split():
        if token.isdigit() or token in _WAR_STOP_TOKENS:
            continue
        tokens.add(_WAR_NUMERAL_TOKENS.get(token, token))
    return frozenset(tokens)


def _war_tokens_match(left: frozenset[str], right: frozenset[str]) -> bool:
    if not left or not right:
        return False
    smaller, larger = (left, right) if len(left) <= len(right) else (right, left)
    if sum(len(token) for token in smaller) < 4:
        return False
    return smaller <= larger


def _seed_war_token_spans(
    seed_events: list[dict[str, Any]],
) -> list[tuple[int, int, tuple[frozenset[str], ...]]]:
    return [
        (
            int(event["year"]),
            int(event.get("end_year", event["year"])),
            tuple(
                {
                    key
                    for key in (
                        _war_tokens(event.get("name")),
                        _war_tokens(event.get("cluster_id")),
                    )
                    if key
                }
            ),
        )
        for event in seed_events
        if event.get("event_type") == "war"
    ]


def _overlaps_seed_war(
    seed_war_spans: list[tuple[int, int, tuple[frozenset[str], ...]]],
    keys: Iterable[frozenset[str]],
    low_year: int,
    high_year: int,
) -> bool:
    key_list = [key for key in keys if key]
    for seed_low, seed_high, seed_keys in seed_war_spans:
        if high_year < seed_low or low_year > seed_high:
            continue
        for key in key_list:
            for seed_key in seed_keys:
                if _war_tokens_match(key, seed_key):
                    return True
    return False


def _humanize_war_name(value: Any) -> str:
    text = str(value or "").replace("_", " ")
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    text = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", text)
    text = re.sub(r"(?<=\d)(?=[A-Za-z])", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def aggregate_iwd_parent_wars(
    candidates: list[dict[str, Any]],
    seed_war_spans: list[tuple[int, int, tuple[frozenset[str], ...]]],
    resolve_party: Any,
) -> dict[str, Any]:
    """Aggregate IWD component wars into at most one strategic event per parent.

    Component records repeat one umbrella conflict across many dyads, so they
    never enter the ledger individually. Each ``parent_war_id`` group is
    reconstructed as two coalitions from its initiator/target pairs and rated
    once, only when every check passes:

    - at least one component has a terminal outcome, years, and both principals;
    - the parent does not overlap a curated seed war (naming variants included);
    - the opposition graph is two-colorable and connected — an entity coded on
      both sides quarantines the parent because no explicit time-bounded
      side-switch policy is defined;
    - component outcomes are unanimous once oriented to the reconstructed
      sides, so draws and mixed dyad results are never forced into one binary
      umbrella outcome;
    - every belligerent resolves to a unique time-bounded identity.

    Confidence drops when some component rows could not contribute, and all
    component rows are attached to the emitted event as provenance.
    """
    grouped: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidates:
        parent_id = str(
            candidate.get("parent_war_id")
            or f"component_{candidate.get('source_component_id')}"
        )
        grouped.setdefault(parent_id, []).append(candidate)

    events: list[dict[str, Any]] = []
    rejections: Counter[str] = Counter()
    resolved_polities: dict[str, dict[str, Any]] = {}
    components_aggregated = 0
    components_attached = 0

    for parent_id in sorted(
        grouped, key=lambda value: (0, int(value)) if value.isdigit() else (1, value)
    ):
        components = sorted(grouped[parent_id], key=lambda row: str(row.get("candidate_id")))
        parent_name = next(
            (str(row["parent_war_name"]) for row in components if row.get("parent_war_name")),
            "",
        )
        usable: list[dict[str, Any]] = []
        provenance: list[dict[str, Any]] = []
        for component in components:
            outcome_code = str(component.get("terminal_outcome_code") or "")
            if outcome_code not in {"1", "2", "3"}:
                status = "not_aggregated_missing_terminal_outcome"
            elif component.get("start_year") is None or component.get("end_year") is None:
                status = "not_aggregated_missing_year"
            elif not component.get("initiators") or not component.get("targets"):
                status = "not_aggregated_missing_principal_side"
            else:
                status = "aggregated"
                usable.append(component)
            provenance.append(
                {
                    "candidate_id": str(component.get("candidate_id")),
                    "component_name": str(component.get("name") or ""),
                    "terminal_outcome_code": outcome_code or None,
                    "status": status,
                }
            )
        if not usable:
            rejections["no_usable_component"] += 1
            continue

        low_year = min(int(component["start_year"]) for component in usable)
        high_year = max(int(component["end_year"]) for component in usable)

        keys = {_war_tokens(parent_name)}
        keys.update(_war_tokens(component.get("name")) for component in components)
        if _overlaps_seed_war(seed_war_spans, keys, low_year, high_year):
            rejections["overlaps_curated_strategic_event"] += 1
            continue

        parties: dict[str, dict[str, Any]] = {}
        opposed: dict[str, set[str]] = {}
        allied: dict[str, set[str]] = {}
        for component in usable:
            component_sides = []
            for field in ("initiators", "targets"):
                side_keys = []
                for party in component[field]:
                    key = str(party.get("cow_code") or f"name:{normalize_label(party.get('name'))}")
                    info = parties.setdefault(
                        key,
                        {"name": str(party.get("name") or ""), "cow_code": party.get("cow_code"), "years": []},
                    )
                    info["years"] += [int(component["start_year"]), int(component["end_year"])]
                    side_keys.append(key)
                component_sides.append(side_keys)
            initiator_keys, target_keys = component_sides
            for left in initiator_keys:
                for right in target_keys:
                    opposed.setdefault(left, set()).add(right)
                    opposed.setdefault(right, set()).add(left)
            for side_keys in component_sides:
                for left in side_keys:
                    for right in side_keys:
                        if left != right:
                            allied.setdefault(left, set()).add(right)

        colors: dict[str, int] = {}
        conflict = False
        graph_components = 0
        for start in sorted(parties):
            if start in colors:
                continue
            graph_components += 1
            stack: list[tuple[str, int]] = [(start, 0)]
            while stack:
                node, color = stack.pop()
                known = colors.get(node)
                if known is not None:
                    if known != color:
                        conflict = True
                        break
                    continue
                colors[node] = color
                stack.extend((neighbor, 1 - color) for neighbor in opposed.get(node, ()))
                stack.extend((neighbor, color) for neighbor in allied.get(node, ()))
            if conflict:
                break
        if conflict:
            # No explicit time-bounded side-switch policies are defined, so an
            # entity coded on both sides always quarantines the parent war.
            rejections["inconsistent_coalition_sides"] += 1
            continue
        if graph_components > 1:
            rejections["disconnected_coalition_graph"] += 1
            continue

        anchor_color = colors[min(parties)]
        outcomes: set[str] = set()
        for component in usable:
            code = str(component["terminal_outcome_code"])
            initiator_key = str(
                component["initiators"][0].get("cow_code")
                or f"name:{normalize_label(component['initiators'][0].get('name'))}"
            )
            if code == "3":
                outcomes.add("draw")
            elif (code == "1") == (colors[initiator_key] == anchor_color):
                outcomes.add("side_a")
            else:
                outcomes.add("side_b")
        if len(outcomes) != 1:
            rejections["mixed_component_outcomes"] += 1
            continue
        outcome = outcomes.pop()

        resolution: dict[str, str] = {}
        pending_polities: dict[str, dict[str, Any]] = {}
        unresolved = False
        for key in sorted(parties):
            info = parties[key]
            entity_id, polity = resolve_party(
                info["name"], info["cow_code"], min(info["years"]), max(info["years"])
            )
            if not entity_id:
                unresolved = True
                break
            resolution[key] = entity_id
            if polity is not None:
                pending_polities[entity_id] = polity
        if unresolved:
            rejections["unresolved_time_bounded_party"] += 1
            continue

        side_a = _deduplicate(
            resolution[key] for key in parties if colors[key] == anchor_color
        )
        side_b = _deduplicate(
            resolution[key] for key in parties if colors[key] != anchor_color
        )
        if not side_a or not side_b or set(side_a) & set(side_b):
            rejections["same_or_empty_opposing_side"] += 1
            continue

        resolved_polities.update(pending_polities)
        completeness = len(usable) / len(components)
        confidence = round(0.76 - 0.12 * (1.0 - completeness), 2)
        display_name = _humanize_war_name(parent_name) or f"IWD parent war {parent_id}"
        components_aggregated += len(usable)
        components_attached += len(components)
        events.append(
            {
                "id": f"iwd_war_{_slug(parent_id, 16)}_{_slug(display_name, 44)}",
                "name": display_name,
                "year": low_year,
                "end_year": high_year,
                "event_type": "war",
                "war_type": "world_war" if "world" in _war_tokens(parent_name) else "interstate_limited",
                "scale": "major_war",
                "stakes": "major",
                "decisiveness": 0.44 if outcome == "draw" else 0.74,
                "confidence": confidence,
                "geographic_scope": 0.68,
                "domain": "mixed",
                "cluster_id": f"iwd_parent_{_slug(parent_id, 24)}",
                "date_precision": "year",
                "sequence": int(parent_id) if parent_id.isdigit() else 0,
                "summary": (
                    "Coalition-aggregated strategic outcome from IWD v1.21: this parent "
                    f"conflict receives exactly one strategic update, built from "
                    f"{len(usable)} of {len(components)} component dyads with a unanimous "
                    "side-oriented outcome. Component rows are retained as provenance, and "
                    "existential severity is never inferred from IWD outcome codes."
                ),
                "participants": _strategic_participants(side_a, side_b, outcome, confidence),
                "source_ids": ["iwd_dataset"],
                "status": "complete",
                "iwd_parent_war_id": parent_id,
                "iwd_parent_war_name": parent_name or None,
                "iwd_components": provenance,
            }
        )

    return {
        "events": events,
        "parent_rejections": rejections,
        "parents_total": len(grouped),
        "parents_promoted": len(events),
        "components_total": len(candidates),
        "components_aggregated": components_aggregated,
        "components_attached": components_attached,
        "resolved_polities": resolved_polities,
    }


def _entity_covers(entity: dict[str, Any], low_year: int, high_year: int) -> bool:
    end_year = entity.get("end_year")
    return int(entity["start_year"]) <= low_year and (
        end_year is None or int(end_year) >= high_year
    )


def _resolve_label_tiers(
    normalized: str,
    low_year: int,
    high_year: int,
    context: dict[str, Any],
    require_observation_coherence: bool,
) -> tuple[str | None, dict[str, Any] | None, str | None]:
    """Exact-normalized label resolution: seed alias, then crosswalk
    observations, then Cliopatria alias with the seed-mapping guards.

    Every tier requires exactly one match that covers the full
    ``[low_year, high_year]`` interval; ambiguity always fails. The
    observation-coherence flag additionally requires an observed entity's own
    labels to contain the queried label (guards against crosswalk
    mis-pairings); the IWD caller keeps it off so the committed IWD promotion
    stays pinned.
    """
    seed_matches = {
        str(entity["id"])
        for entity in context["seed_entities"]
        if _entity_covers(entity, low_year, high_year)
        and normalized
        in {
            normalize_label(entity.get("name")),
            *[normalize_label(alias) for alias in entity.get("aliases", [])],
        }
    }
    if len(seed_matches) == 1:
        return next(iter(seed_matches)), None, "seed_alias"

    release_entities = context["release_entities"]
    entity_labels = context["entity_labels"]
    observed_matches = {
        entity_id
        for _, _, entity_id in context["label_observations"].get(normalized, [])
        if entity_id in release_entities
        and _entity_covers(release_entities[entity_id], low_year, high_year)
        and (
            not require_observation_coherence
            or normalized in entity_labels.get(entity_id, set())
        )
    }
    if len(observed_matches) == 1:
        return next(iter(observed_matches)), None, "crosswalk_observation"

    seed_by_id = context["seed_by_id"]
    candidate_matches = [
        polity
        for polity in context["polity_alias_index"].get(normalized, [])
        if int(polity["start_year"]) <= low_year
        and int(polity["end_year"]) >= high_year
    ]
    candidate_ids = {_candidate_entity_id(polity) for polity in candidate_matches}
    if len(candidate_ids) == 1:
        polity = candidate_matches[0]
        # A candidate that maps onto a curated seed identity must resolve to
        # the seed entity; otherwise one polity would hold two parallel
        # rating identities.
        mapped_seed = _candidate_policy_seed(polity, seed_by_id)
        if not mapped_seed:
            name_matches = context["seed_label_index"].get(
                normalize_label(polity.get("canonical_name_candidate")), set()
            )
            if len(name_matches) == 1:
                named_seed = next(iter(name_matches))
                named_entity = seed_by_id.get(named_seed)
                # A name match alone must not bridge eras: a same-named
                # polity from a different century stays its own identity.
                if named_entity and _candidate_overlaps_entity(polity, named_entity):
                    mapped_seed = named_seed
        if mapped_seed:
            seed_entity = seed_by_id.get(mapped_seed)
            if seed_entity and _entity_covers(seed_entity, low_year, high_year):
                return mapped_seed, None, "cliopatria_alias_to_seed"
            return None, None, None
        return _candidate_entity_id(polity), polity, "cliopatria_alias"
    return None, None, None


def resolve_hced_side_label(
    label: Any,
    low_year: int,
    high_year: int,
    context: dict[str, Any],
) -> tuple[str | None, dict[str, Any] | None, str | None, str | None]:
    """Resolve a bare HCED side label to a unique time-bounded identity.

    Returns ``(entity_id, polity, rejection_reason, tier)``. The three front
    gates (faction blocklist, pending-split set, label-policy table) are
    authoritative: a gated label never falls through to alias matching.
    """
    normalized = normalize_label(label)
    if not normalized:
        return None, None, "blank_side_label", None
    if normalized in HCED_FACTION_LABELS:
        return None, None, "faction_label_not_a_polity", None
    if normalized in HCED_PENDING_SPLIT_LABELS:
        return None, None, "label_pending_identity_split", None
    if normalized in HCED_LABEL_POLICIES:
        seed_id = _label_policy_seed_id(normalized, low_year, high_year)
        if seed_id:
            return seed_id, None, None, "label_policy"
        return None, None, "label_outside_policy_window", None
    entity_id, polity, tier = _resolve_label_tiers(
        normalized, low_year, high_year, context, require_observation_coherence=True
    )
    if entity_id:
        return entity_id, polity, None, tier
    return None, None, "no_unique_time_valid_label_match", None


def promote_hced_label_rows(
    deferred_rows: list[dict[str, Any]],
    curated_seed_keys: set[tuple[str, int]],
    promoted_event_keys: set[tuple[str, int]],
    resolve_code: Any,
    resolve_side_label: Any,
) -> dict[str, Any]:
    """Second HCED promotion pass for rows lacking Seshat coding on a side.

    Deferred rows re-enter through a declared label-resolution ruleset: the
    coded side (if any) resolves through the unchanged Seshat-code path, the
    uncoded side only through explicit time-bounded label policies or exact
    time-valid alias matching with uniqueness. Label-resolved events carry
    reduced identity confidence and an ``identity_resolution`` provenance
    marker. Nothing here writes ``label_observations``: alias-derived
    resolutions must never launder themselves into the higher-trust
    observation tier, and results must not depend on row order.
    """
    events: list[dict[str, Any]] = []
    rejections: Counter[str] = Counter()
    resolved_polities: dict[str, dict[str, Any]] = {}
    observation_resolutions: Counter[tuple[str, str]] = Counter()
    cluster_spans: dict[str, list[Any]] = {}
    accepted_keys = set(promoted_event_keys)

    for candidate in deferred_rows:
        low_year = int(candidate["year_low"])
        best_year = int(candidate["year_best"])
        high_year = int(candidate["year_high"])
        winner = normalize_label(candidate.get("winner_raw"))
        loser = normalize_label(candidate.get("loser_raw"))
        side_a_label = normalize_label(candidate.get("side_1_raw"))
        side_b_label = normalize_label(candidate.get("side_2_raw"))
        draw = winner in {"draw", "inconclusive", "stalemate"}
        # A blank winner is unknown, never a draw and never a vacuous match
        # against a blank side label.
        if not draw and (
            not winner or not loser or winner != side_a_label or loser != side_b_label
        ):
            rejections["label_outcome_not_aligned"] += 1
            continue

        resolved_sides: list[list[str]] = []
        side_tiers: list[str] = []
        observation_hits: list[tuple[str, str]] = []
        pending_polities: dict[str, dict[str, Any]] = {}
        label_side_count = 0
        resolution_failed = False
        for codes, label in (
            (
                _deduplicate(map(str, candidate.get("seshat_side_1_candidates", []))),
                candidate.get("side_1_raw"),
            ),
            (
                _deduplicate(map(str, candidate.get("seshat_side_2_candidates", []))),
                candidate.get("side_2_raw"),
            ),
        ):
            resolved: list[str] = []
            if codes:
                for code in codes:
                    entity_id, polity, reason = resolve_code(code, low_year, high_year)
                    if not entity_id:
                        rejections[reason or "unresolved_entity"] += 1
                        resolution_failed = True
                        break
                    if polity:
                        pending_polities[entity_id] = polity
                    resolved.append(entity_id)
                side_tiers.append("seshat_crosswalk")
            else:
                entity_id, polity, reason, tier = resolve_side_label(
                    label, low_year, high_year
                )
                if not entity_id:
                    rejections[reason or "no_unique_time_valid_label_match"] += 1
                    resolution_failed = True
                else:
                    if polity:
                        pending_polities[entity_id] = polity
                    resolved.append(entity_id)
                    side_tiers.append(str(tier))
                    label_side_count += 1
                    if tier == "crosswalk_observation":
                        observation_hits.append((normalize_label(label), entity_id))
            if resolution_failed:
                break
            resolved_sides.append(_deduplicate(resolved))
        if resolution_failed:
            continue
        side_a, side_b = resolved_sides
        if not side_a or not side_b or set(side_a) & set(side_b):
            rejections["same_or_empty_opposing_side"] += 1
            continue

        event_name = str(
            candidate.get("name") or candidate.get("source_record_id") or "Unnamed engagement"
        )
        event_key = _event_key(event_name, best_year)
        if event_key in curated_seed_keys:
            rejections["duplicate_of_curated_seed"] += 1
            continue
        if event_key in accepted_keys:
            rejections["duplicate_of_promoted_event"] += 1
            continue
        accepted_keys.add(event_key)
        resolved_polities.update(pending_polities)
        observation_resolutions.update(observation_hits)

        scale, scale_level = _scale(candidate)
        confidence = 0.73 if candidate.get("consulted_source_raw") else 0.67
        confidence -= 0.03 * label_side_count
        if low_year != high_year:
            confidence -= 0.03
        confidence = round(confidence, 2)
        war_names = list(map(str, candidate.get("war_names", [])))
        cluster = _slug(war_names[0]) if war_names else None
        if cluster:
            span = cluster_spans.setdefault(
                f"hced_war_{cluster}", [_war_tokens(war_names[0]), low_year, high_year]
            )
            span[1] = min(span[1], low_year)
            span[2] = max(span[2], high_year)
        source_ids = ["hced_dataset", "hced_seshat_crosswalk"]
        if any(entity_id.startswith("clio_") for entity_id in (*side_a, *side_b)):
            source_ids.append("cliopatria_v020")
        events.append(
            {
                "id": f"hced_label_{_slug(str(candidate['candidate_id']), 74)}",
                "name": event_name,
                "year": low_year,
                "end_year": high_year,
                "event_type": "engagement",
                "war_type": "interstate_limited",
                "scale": scale,
                "stakes": "major" if scale_level >= 4 else "limited",
                "decisiveness": 0.32 if draw else round(min(0.90, 0.54 + 0.06 * scale_level), 2),
                "confidence": confidence,
                "geographic_scope": round(min(0.70, 0.08 + 0.09 * scale_level), 2),
                "domain": _domain(candidate.get("theatre_raw")),
                "cluster_id": f"hced_war_{cluster}" if cluster else None,
                "date_precision": "range" if low_year != high_year else "year",
                "sequence": int(candidate.get("source_row") or 0),
                "summary": (
                    "Provisional tactical result from HCED. At least one side lacked "
                    "Seshat crosswalk coding and was resolved by a declared, "
                    "time-bounded label policy or an exact time-valid alias match; "
                    "this carries lower identity confidence than crosswalk "
                    "resolution and does not infer the enclosing war's strategic "
                    "outcome."
                ),
                "identity_resolution": "label",
                "side_identity_resolution": {
                    "side_a": side_tiers[0],
                    "side_b": side_tiers[1],
                },
                "hced_candidate_id": str(candidate["candidate_id"]),
                "participants": _participants(
                    side_a,
                    side_b,
                    draw,
                    confidence,
                    scale_level,
                ),
                "source_ids": source_ids,
                "status": "complete",
            }
        )

    return {
        "events": events,
        "rejections": rejections,
        "rows_total": len(deferred_rows),
        "accepted": len(events),
        "resolved_polities": resolved_polities,
        "observation_resolutions": [
            {"label": label, "entity_id": entity_id, "resolved_sides": count}
            for (label, entity_id), count in sorted(observation_resolutions.items())
        ],
        "cluster_spans": cluster_spans,
    }


def _iwbd_id_parts(candidate_id: str) -> tuple[str, str, str] | None:
    match = _IWBD_CANDIDATE_ID.match(candidate_id)
    return (match.group(1), match.group(2), match.group(3)) if match else None


def _iwbd_dates(row: dict[str, Any]) -> tuple[date, date] | None:
    try:
        start = date.fromisoformat(str(row.get("start_date")))
        end = date.fromisoformat(str(row.get("end_date")))
    except (TypeError, ValueError):
        return None
    return (start, end) if end >= start else None


def _iwbd_base_war(row: dict[str, Any]) -> str:
    return re.sub(r"\s*\(.*\)$", "", str(row.get("war_name") or ""))


def promote_iwbd_battles(
    candidates: list[dict[str, Any]],
    curated_seed_keys: set[tuple[str, int]],
    hced_event_keys: set[tuple[str, int]],
    resolve_label: Any,
    hced_war_cluster_spans: dict[str, list[Any]],
    iwd_parent_ids: set[str],
) -> dict[str, Any]:
    """Promote non-duplicate IWBD battles as provisional tactical engagements.

    A battle enters only when it is not a duplicate of any curated seed event,
    any HCED candidate (promoted or staged), or an earlier IWBD row by
    normalized battle name and year within one year; its date span does not
    strictly contain a differently-named battle of the same war (campaign
    umbrellas stay staged); its coded victor matches a named side (the
    inconclusive pair is a coded tactical stalemate, never a guess); both
    sides are single polities resolving to unique time-bounded identities
    outside declared deny windows; and severity is capped at limited. The
    war-level victor code is ignored entirely: battles never update the
    strategic layer.
    """
    events: list[dict[str, Any]] = []
    rejections: Counter[str] = Counter()
    resolved_polities: dict[str, dict[str, Any]] = {}
    seen_keys: set[tuple[str, int]] = set()

    # Containment pre-pass over every row with a name and valid dates (not
    # just survivors), so the umbrella gate is order-independent: an IWBD
    # record whose span strictly contains a differently-named battle of the
    # same war is a presumptive campaign umbrella and stays staged.
    war_groups: dict[tuple[str, str], list[tuple[str, date, date]]] = {}
    for row in candidates:
        name = str(row.get("name") or "")
        parsed = _iwbd_dates(row)
        parts = _iwbd_id_parts(str(row.get("candidate_id") or ""))
        if not name or parsed is None or parts is None:
            continue
        war_groups.setdefault(
            (parts[0], str(row.get("war_name") or "")), []
        ).append((name, parsed[0], parsed[1]))

    accepted_rows: list[dict[str, Any]] = []
    for row in sorted(candidates, key=lambda r: int(r.get("source_row") or 0)):
        name = str(row.get("name") or "")
        if not name:
            rejections["missing_battle_name"] += 1
            continue
        parsed = _iwbd_dates(row)
        if parsed is None:
            rejections["missing_or_invalid_date"] += 1
            continue
        start, end = parsed
        year_low, year_high = start.year, end.year
        attacker = row.get("attacker_raw")
        defender = row.get("defender_raw")
        if not attacker or not defender:
            rejections["missing_belligerent_label"] += 1
            continue
        attacker, defender = str(attacker), str(defender)

        lookup_keys = {_event_key(name, year) for year in range(year_low - 1, year_high + 2)}
        exact_keys = {_event_key(name, year) for year in range(year_low, year_high + 1)}
        if lookup_keys & seen_keys:
            rejections["duplicate_within_iwbd"] += 1
            continue
        if lookup_keys & curated_seed_keys:
            rejections["duplicate_of_curated_seed"] += 1
            seen_keys |= exact_keys
            continue
        if lookup_keys & hced_event_keys:
            rejections["duplicate_of_hced_battle"] += 1
            seen_keys |= exact_keys
            continue
        seen_keys |= exact_keys

        parts = _iwbd_id_parts(str(row.get("candidate_id") or ""))
        if parts is None:
            rejections["malformed_candidate_id"] += 1
            continue
        cow_number = parts[0]
        normalized_name = normalize_label(name)
        span_days = (end - start).days
        contained = False
        for other_name, other_start, other_end in war_groups.get(
            (cow_number, str(row.get("war_name") or "")), []
        ):
            if normalize_label(other_name) == normalized_name:
                continue
            if (
                start <= other_start
                and end >= other_end
                and span_days > (other_end - other_start).days
            ):
                contained = True
                break
        if contained:
            rejections["contains_constituent_iwbd_rows"] += 1
            continue

        winner = normalize_label(row.get("winner_raw"))
        role = str(row.get("battle_level_victor_role") or "")
        normalized_attacker = normalize_label(attacker)
        normalized_defender = normalize_label(defender)
        draw = winner == "inconclusive" and normalize_label(role) == "inconclusive"
        if not draw and not (
            (role == "Attacker" and winner == normalized_attacker)
            or (role == "Defender" and winner == normalized_defender)
        ):
            rejections["outcome_not_aligned_to_battle_sides"] += 1
            continue

        if any(
            "/" in label or "," in label or "(" in label
            or normalize_label(label) in IWBD_COALITION_SIDE_LABELS
            for label in (attacker, defender)
        ):
            rejections["coalition_or_composite_side"] += 1
            continue

        denied = False
        for label in (attacker, defender):
            for deny_low, deny_high in IWBD_IDENTITY_DENY_WINDOWS.get(
                normalize_label(label), ()
            ):
                if not (year_high < deny_low or year_low > deny_high):
                    denied = True
                    break
            if denied:
                break
        if denied:
            rejections["unresolved_time_bounded_belligerent"] += 1
            continue
        attacker_id, attacker_polity = resolve_label(attacker, year_low, year_high)
        defender_id, defender_polity = resolve_label(defender, year_low, year_high)
        if not attacker_id or not defender_id:
            rejections["unresolved_time_bounded_belligerent"] += 1
            continue
        if attacker_id == defender_id:
            rejections["same_or_empty_opposing_side"] += 1
            continue
        for entity_id, polity in (
            (attacker_id, attacker_polity),
            (defender_id, defender_polity),
        ):
            if polity is not None:
                resolved_polities[entity_id] = polity

        accepted_rows.append(
            {
                "row": row,
                "name": name,
                "start": start,
                "end": end,
                "attacker_id": attacker_id,
                "defender_id": defender_id,
                "draw": draw,
                "victor_role": role,
                "cow_number": cow_number,
                "iwd_number": parts[1],
                "base_war": _iwbd_base_war(row),
            }
        )

    # Cluster assignment is per war, never per row: all accepted battles of
    # one (cowNum, theater-stripped war) group share exactly one tactical
    # down-weighting cluster — an existing HCED war cluster when the war-name
    # tokens match exactly one with year overlap, else the IWD parent-war
    # family for a joinable iwdNum (the parent war id itself, never a
    # component id), else a distinct iwbd_war_* fallback.
    group_rows: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for accepted in accepted_rows:
        group_rows.setdefault((accepted["cow_number"], accepted["base_war"]), []).append(accepted)
    group_clusters: dict[tuple[str, str], str] = {}
    for (cow_number, base_war), rows in group_rows.items():
        group_low = min(item["start"].year for item in rows)
        group_high = max(item["end"].year for item in rows)
        war_tokens = _war_tokens(base_war)
        matches = [
            cluster_id
            for cluster_id, (tokens, span_low, span_high) in hced_war_cluster_spans.items()
            if _war_tokens_match(war_tokens, tokens)
            and group_low <= span_high
            and group_high >= span_low
        ]
        if len(set(matches)) == 1:
            group_clusters[(cow_number, base_war)] = matches[0]
        elif rows[0]["iwd_number"] != "-9" and rows[0]["iwd_number"] in iwd_parent_ids:
            group_clusters[(cow_number, base_war)] = (
                f"iwd_parent_{_slug(rows[0]['iwd_number'], 24)}"
            )
        else:
            group_clusters[(cow_number, base_war)] = (
                f"iwbd_war_{cow_number}_{_slug(base_war, 40)}"
            )

    for accepted in accepted_rows:
        row = accepted["row"]
        name = accepted["name"]
        start, end = accepted["start"], accepted["end"]
        draw = accepted["draw"]
        if draw or accepted["victor_role"] == "Attacker":
            side_a, side_b = [accepted["attacker_id"]], [accepted["defender_id"]]
        else:
            side_a, side_b = [accepted["defender_id"]], [accepted["attacker_id"]]
        candidate_id = str(row.get("candidate_id"))
        events.append(
            {
                "id": f"iwbd_{_slug(candidate_id, 24)}_{_slug(name, 44)}",
                "name": name,
                "year": start.year,
                "end_year": end.year,
                "event_type": "engagement",
                "war_type": "interstate_limited",
                "scale": "battle",
                "stakes": "limited",
                "decisiveness": 0.32 if draw else 0.66,
                "confidence": 0.70,
                "geographic_scope": 0.26,
                "domain": _domain(row.get("war_name")),
                "cluster_id": group_clusters[(accepted["cow_number"], accepted["base_war"])],
                "date_precision": "day",
                "sequence": int(row.get("source_row") or 0),
                "summary": (
                    "Provisional tactical result from IWBD. The victor is coded by "
                    "tactical control of the attacker's objective; this does not "
                    "describe casualties, magnitude, or the enclosing war's "
                    "strategic outcome, which is never inferred from battle results."
                ),
                "participants": _participants(
                    side_a,
                    side_b,
                    draw,
                    0.70,
                    2,
                    note=(
                        "Provisional IWBD tactical coding; the enclosing war's "
                        "strategic outcome is not inferred from battle results."
                    ),
                ),
                "source_ids": ["iwbd_dataset", "cliopatria_v020"],
                "status": "complete",
                "iwbd_candidate_id": candidate_id,
                "iwbd_war_name": str(row.get("war_name") or ""),
                "iwbd_cow_war_number": accepted["cow_number"],
                "iwbd_iwd_war_number": (
                    accepted["iwd_number"] if accepted["iwd_number"] != "-9" else None
                ),
                "iwbd_battle_level_victor_role": str(row.get("battle_level_victor_role") or ""),
                "iwbd_duration_days": row.get("duration_days"),
            }
        )

    return {
        "events": events,
        "rejections": rejections,
        "battles_total": len(candidates),
        "battles_promoted": len(events),
        "resolved_polities": resolved_polities,
    }


def _gw_policy_seed_id(code: str, low_year: int, high_year: int) -> str | None:
    matches = [
        entity_id
        for start_year, end_year, entity_id in UCDP_GW_CODE_POLICIES.get(code, ())
        if low_year >= start_year and high_year <= end_year
    ]
    return matches[0] if len(set(matches)) == 1 else None


_UCDP_PARENTHETICAL = re.compile(r"^(.*?)\s*\((.*)\)\s*$")


def _ucdp_label_variants(name: Any) -> list[str]:
    label = str(name or "").strip()
    if label.lower().startswith("government of "):
        label = label[len("government of "):]
    match = _UCDP_PARENTHETICAL.match(label)
    variants = [label] if not match else [match.group(1), match.group(2)]
    return [variant for variant in (v.strip() for v in variants) if variant]


def resolve_ucdp_party(
    name: Any,
    gwno: Any,
    low_year: int,
    high_year: int,
    context: dict[str, Any],
) -> tuple[str | None, dict[str, Any] | None, str | None]:
    """Resolve a UCDP party to a unique time-bounded identity.

    A Gleditsch-Ward code with an explicit policy is authoritative: outside
    its windows the party stays unresolved, never falling back to name
    matching. Otherwise the label (stripped of "Government of ", with
    parenthetical variants derived) resolves through the shared exact-alias
    tiers; every derived variant must resolve, and to the same entity —
    ambiguity always fails. Returns ``(entity_id, polity, method)``.
    """
    code = str(gwno or "").strip()
    if code in UCDP_GW_CODE_POLICIES:
        seed_id = _gw_policy_seed_id(code, low_year, high_year)
        return seed_id, None, ("gw_code_policy" if seed_id else None)
    variants = _ucdp_label_variants(name)
    if not variants:
        return None, None, None
    entity_ids: set[str] = set()
    polity: dict[str, Any] | None = None
    tiers: list[str] = []
    for variant in variants:
        entity_id, variant_polity, tier = _resolve_label_tiers(
            normalize_label(variant),
            low_year,
            high_year,
            context,
            require_observation_coherence=False,
        )
        if not entity_id:
            return None, None, None
        entity_ids.add(entity_id)
        if variant_polity is not None:
            polity = variant_polity
        tiers.append(str(tier))
    if len(entity_ids) != 1:
        return None, None, None
    method = {
        "seed_alias": "seed_label",
        "cliopatria_alias": "cliopatria_label",
        "cliopatria_alias_to_seed": "cliopatria_label",
    }.get(tiers[0], tiers[0])
    return next(iter(entity_ids)), polity, method


def _ucdp_split(value: Any) -> list[str]:
    return [part.strip() for part in str(value or "").split(",") if part.strip()]


def _ucdp_int(value: Any) -> int | None:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def promote_ucdp_termination_episodes(
    conflict_rows: list[dict[str, Any]],
    dyad_rows: list[dict[str, Any]],
    promoted_war_index: list[tuple[str, str | None, int, int, frozenset[str], dict[str, str]]],
    resolver: Any,
    curated_exclusions: dict[tuple[str, str], str] | None = None,
) -> dict[str, Any]:
    """Promote UCDP conflict-termination victory episodes as strategic events.

    The promotion unit is the conflict-level terminal episode; the dyad file
    is a consistency reference only and is never promoted. Only outcome codes
    3 and 4 (victories) can produce events — peace agreements, ceasefires,
    low activity, and actor cessation stay staged, because peace is not a
    loss and unknown stays unknown. Both sides must consist entirely of
    state primaries resolving to unique time-bounded identities; episodes
    duplicating an already-promoted strategic event (shared entity on each
    side with year overlap), contradicted by a terminal dyad row, or linked
    by end date to an oppositely-oriented victory assertion (the Six-Day
    rule) stay staged. Severity is capped at limited; secondary supporters
    are recorded as provenance and never receive an outcome.
    """
    if curated_exclusions is None:
        curated_exclusions = UCDP_CURATED_EXCLUSIONS
    events: list[dict[str, Any]] = []
    rejections: Counter[str] = Counter()
    duplicate_details: list[dict[str, Any]] = []
    resolved_polities: dict[str, dict[str, Any]] = {}

    def parse_primaries(raw: dict[str, Any], side: str) -> list[tuple[str, str]] | None:
        names = _ucdp_split(raw.get(f"side_{side}"))
        codes = _ucdp_split(raw.get(f"gwno_{side}"))
        if not names or len(names) != len(codes):
            return None
        if not all(name.lower().startswith("government of ") for name in names):
            return None
        return list(zip(names, codes))

    def parse_secondaries(raw: dict[str, Any], side: str) -> list[tuple[str, str | None]]:
        names = _ucdp_split(raw.get(f"side_{side}_2nd"))
        codes = _ucdp_split(raw.get(f"gwno_{side}_2nd"))
        if len(names) == len(codes):
            return list(zip(names, codes))
        return [(name, None) for name in names]

    def best_effort_ids(
        parties: list[tuple[str, str | None]], low_year: int, high_year: int
    ) -> set[str]:
        resolved: set[str] = set()
        for name, code in parties:
            entity_id, _, _ = resolver(name, code, low_year, high_year)
            if entity_id:
                resolved.add(entity_id)
        return resolved

    # Pre-pass over every terminal victory assertion in the file, independent
    # of its own gate outcomes, resolved best-effort. Feeds the ledger-cluster
    # map (an accepted episode of a conflict whose sibling deduplicates
    # against ledger war W inherits W's cluster) and the linked-episode index
    # (assertions sharing an exact end date and a resolved entity).
    assertions: list[dict[str, Any]] = []
    for candidate in conflict_rows:
        raw = candidate.get("raw", {})
        if str(raw.get("c_epterm", "")).strip() != "1":
            continue
        outcome_code = str(raw.get("c_outcome", "")).strip()
        if outcome_code not in {"3", "4"}:
            continue
        start = _ucdp_int(raw.get("c_ep_startyear"))
        end = _ucdp_int(raw.get("c_ep_endyear"))
        if start is None or end is None:
            continue
        side_a = parse_primaries(raw, "a") or []
        side_b = parse_primaries(raw, "b") or []
        primary_a = best_effort_ids(side_a, start, end)
        primary_b = best_effort_ids(side_b, start, end)
        dedup_a = primary_a | best_effort_ids(parse_secondaries(raw, "a"), start, end)
        dedup_b = primary_b | best_effort_ids(parse_secondaries(raw, "b"), start, end)
        winners, losers = (
            (primary_a, primary_b) if outcome_code == "3" else (primary_b, primary_a)
        )
        assertions.append(
            {
                "conflict_id": str(raw.get("conflict_id", "")).strip(),
                "epno": str(raw.get("c_epno", "")).strip(),
                "start": start,
                "end": end,
                "end_date": str(raw.get("c_ependdate", "")).strip(),
                "winners": winners,
                "losers": losers,
                "dedup_a": dedup_a,
                "dedup_b": dedup_b,
            }
        )

    ledger_clusters: dict[str, dict[str, str]] = {}
    for assertion in assertions:
        for event_id, cluster_id, war_low, war_high, entities, _ in promoted_war_index:
            if war_low > assertion["end"] or war_high < assertion["start"]:
                continue
            if assertion["dedup_a"] & entities and assertion["dedup_b"] & entities:
                if cluster_id:
                    ledger_clusters.setdefault(assertion["conflict_id"], {})[
                        cluster_id
                    ] = event_id
    linked_by_date: dict[str, list[dict[str, Any]]] = {}
    for assertion in assertions:
        if assertion["end_date"]:
            linked_by_date.setdefault(assertion["end_date"], []).append(assertion)

    # Dyad reference file: quarantine rows failing year sanity (never silently
    # repaired), count the blank-outcome terminal row, index the sane
    # terminal remainder for the consistency scan.
    dyad_rows_quarantined_corrupt = 0
    dyad_terminal_blank_outcome = 0
    dyads_by_conflict: dict[str, list[dict[str, Any]]] = {}
    for candidate in dyad_rows:
        raw = candidate.get("raw", {})
        year = _ucdp_int(raw.get("year"))
        if year is None or not 1900 <= year <= 2035:
            dyad_rows_quarantined_corrupt += 1
            continue
        if str(raw.get("d_epterm", "")).strip() != "1":
            # Non-terminal annual rows never gate a promotion; a blank
            # episode-end year here just means the episode is ongoing.
            continue
        if not str(raw.get("d_outcome", "")).strip():
            dyad_terminal_blank_outcome += 1
            continue
        start = _ucdp_int(raw.get("d_ep_startyear"))
        end = _ucdp_int(raw.get("d_ep_endyear"))
        if start is None or end is None:
            # A terminal row without sane episode years cannot be scanned;
            # quarantine it explicitly rather than silently repairing it.
            dyad_rows_quarantined_corrupt += 1
            continue
        dyads_by_conflict.setdefault(str(raw.get("conflict_id", "")).strip(), []).append(raw)

    def sort_key(candidate: dict[str, Any]) -> tuple[int, int, int]:
        raw = candidate.get("raw", {})
        return (
            _ucdp_int(raw.get("c_ep_endyear")) or 0,
            _ucdp_int(raw.get("conflict_id")) or 0,
            _ucdp_int(raw.get("c_epno")) or 0,
        )

    accepted_index: list[tuple[str, str | None, int, int, frozenset[str], dict[str, str]]] = []

    for candidate in sorted(conflict_rows, key=sort_key):
        raw = candidate.get("raw", {})
        conflict_id = str(raw.get("conflict_id", "")).strip()
        year = _ucdp_int(raw.get("year"))
        if not conflict_id or year is None or not 1900 <= year <= 2035:
            rejections["malformed_source_row"] += 1
            continue
        if str(raw.get("c_epterm", "")).strip() != "1":
            rejections["not_terminal_episode"] += 1
            continue
        outcome_code = str(raw.get("c_outcome", "")).strip()
        if outcome_code == "1":
            rejections["outcome_peace_agreement"] += 1
            continue
        if outcome_code == "2":
            rejections["outcome_ceasefire"] += 1
            continue
        if outcome_code == "5":
            rejections["outcome_low_activity"] += 1
            continue
        if outcome_code == "6":
            rejections["outcome_actor_ceased"] += 1
            continue
        if outcome_code not in {"3", "4"}:
            rejections["outcome_missing_or_unknown"] += 1
            continue
        low_year = _ucdp_int(raw.get("c_ep_startyear"))
        high_year = _ucdp_int(raw.get("c_ep_endyear"))
        if low_year is None or high_year is None:
            rejections["missing_or_invalid_episode_years"] += 1
            continue
        side_a_parties = parse_primaries(raw, "a")
        side_b_parties = parse_primaries(raw, "b")
        if side_a_parties is None or side_b_parties is None:
            rejections["nonstate_primary_party"] += 1
            continue

        party_resolutions: list[dict[str, Any]] = []
        pending_polities: dict[str, dict[str, Any]] = {}
        side_ids: list[list[str]] = []
        side_codes: list[set[str]] = []
        unresolved = False
        for side_name, parties in (("side_a", side_a_parties), ("side_b", side_b_parties)):
            resolved: list[str] = []
            for name, code in parties:
                entity_id, polity, method = resolver(name, code, low_year, high_year)
                if not entity_id:
                    unresolved = True
                    break
                if polity is not None:
                    pending_polities[entity_id] = polity
                resolved.append(entity_id)
                party_resolutions.append(
                    {
                        "name": name,
                        "gwno": code,
                        "side": side_name,
                        "entity_id": entity_id,
                        "method": method,
                    }
                )
            if unresolved:
                break
            side_ids.append(_deduplicate(resolved))
            side_codes.append({code for _, code in parties})
        if unresolved:
            rejections["unresolved_time_bounded_party"] += 1
            continue
        side_a_ids, side_b_ids = side_ids
        if not side_a_ids or not side_b_ids or set(side_a_ids) & set(side_b_ids):
            rejections["same_or_empty_opposing_side"] += 1
            continue

        epno = str(raw.get("c_epno", "")).strip()
        exclusion_reason = curated_exclusions.get((conflict_id, epno))
        if exclusion_reason:
            rejections["documented_side_attribution_dispute"] += 1
            continue

        winners_ids, losers_ids = (
            (set(side_a_ids), set(side_b_ids))
            if outcome_code == "3"
            else (set(side_b_ids), set(side_a_ids))
        )
        winner_codes, loser_codes = (
            (side_codes[0], side_codes[1])
            if outcome_code == "3"
            else (side_codes[1], side_codes[0])
        )
        primary_pair_codes = winner_codes | loser_codes

        secondaries_a = parse_secondaries(raw, "a")
        secondaries_b = parse_secondaries(raw, "b")
        dedup_a = set(side_a_ids) | best_effort_ids(secondaries_a, low_year, high_year)
        dedup_b = set(side_b_ids) | best_effort_ids(secondaries_b, low_year, high_year)
        duplicate_event = None
        for event_id, cluster_id, war_low, war_high, entities, terminations in (
            *promoted_war_index,
            *accepted_index,
        ):
            if war_low > high_year or war_high < low_year:
                continue
            if dedup_a & entities and dedup_b & entities:
                duplicate_event = (event_id, terminations)
                break
        if duplicate_event is not None:
            event_id, terminations = duplicate_event
            agrees = contradicts = False
            for entity_id in winners_ids:
                termination = str(terminations.get(entity_id, ""))
                if "victory" in termination:
                    agrees = True
                elif "defeat" in termination:
                    contradicts = True
            for entity_id in losers_ids:
                termination = str(terminations.get(entity_id, ""))
                if "defeat" in termination:
                    agrees = True
                elif "victory" in termination:
                    contradicts = True
            orientation = (
                "contradicts" if contradicts else "agrees" if agrees else "undetermined"
            )
            duplicate_details.append(
                {
                    "conflict_id": conflict_id,
                    "c_epno": epno,
                    "matched_event_id": event_id,
                    "orientation": orientation,
                }
            )
            rejections["duplicate_of_promoted_strategic_event"] += 1
            continue

        dyad_checks: list[dict[str, Any]] = []
        dyad_contradiction = False
        for dyad_raw in dyads_by_conflict.get(conflict_id, []):
            dyad_start = _ucdp_int(dyad_raw.get("d_ep_startyear"))
            dyad_end = _ucdp_int(dyad_raw.get("d_ep_endyear"))
            if dyad_start is None or dyad_end is None:
                continue
            if dyad_start > high_year or dyad_end < low_year:
                continue
            dyad_outcome = str(dyad_raw.get("d_outcome", "")).strip()
            status = "nonvictory_terminal_ignored"
            if dyad_outcome in {"3", "4"}:
                dyad_a = set(_ucdp_split(dyad_raw.get("gwno_a")))
                dyad_b = set(_ucdp_split(dyad_raw.get("gwno_b")))
                dyad_winners, dyad_losers = (
                    (dyad_a, dyad_b) if dyad_outcome == "3" else (dyad_b, dyad_a)
                )
                if dyad_winners & loser_codes or dyad_losers & winner_codes:
                    dyad_contradiction = True
                else:
                    status = "consistent_victory"
            elif dyad_outcome in {"1", "2"}:
                dyad_pair = set(_ucdp_split(dyad_raw.get("gwno_a"))) | set(
                    _ucdp_split(dyad_raw.get("gwno_b"))
                )
                # The same state pair the conflict level calls a victory is
                # called a negotiated ending at the dyad level: mixed evidence
                # quarantines the episode; nothing is rated.
                if dyad_pair and dyad_pair <= primary_pair_codes:
                    dyad_contradiction = True
            dyad_checks.append(
                {
                    "dyad_id": str(dyad_raw.get("dyad_id", "")).strip(),
                    "d_epid": str(dyad_raw.get("d_epid", "")).strip(),
                    "d_ep_startyear": dyad_start,
                    "d_ep_endyear": dyad_end,
                    "d_outcome": dyad_outcome,
                    "status": status,
                }
            )
            if dyad_contradiction:
                break
        if dyad_contradiction:
            rejections["dyad_conflict_outcome_contradiction"] += 1
            continue

        end_date = str(raw.get("c_ependdate", "")).strip()
        linked_contradiction = False
        linked_group = False
        for assertion in linked_by_date.get(end_date, []) if end_date else []:
            if assertion["conflict_id"] == conflict_id and assertion["epno"] == epno:
                continue
            assertion_entities = assertion["winners"] | assertion["losers"]
            if not ((winners_ids | losers_ids) & assertion_entities):
                continue
            linked_group = True
            if winners_ids & assertion["losers"] or losers_ids & assertion["winners"]:
                linked_contradiction = True
                break
        if linked_contradiction:
            rejections["contradictory_linked_episode_outcomes"] += 1
            continue

        intensity = str(raw.get("intensity_level", "")).strip()
        incompatibility = str(raw.get("incompatibility", "")).strip()
        scale = "major_war" if intensity == "2" else "campaign"
        stakes = "major" if incompatibility in {"2", "3"} else "limited"
        end_precision = str(raw.get("c_ependprec", "")).strip()
        has_secondaries = bool(secondaries_a or secondaries_b)
        confidence = 0.74
        if has_secondaries:
            confidence -= 0.05
        if end_precision not in {"1", "2", "3"}:
            confidence -= 0.03
        confidence = round(confidence, 2)
        participant_uniform = 0.72 if scale == "major_war" else 0.52

        display_a = " & ".join(
            name[len("Government of "):] if name.lower().startswith("government of ") else name
            for name, _ in side_a_parties
        )
        display_b = " & ".join(
            name[len("Government of "):] if name.lower().startswith("government of ") else name
            for name, _ in side_b_parties
        )
        territory = str(raw.get("territory_name", "")).strip()
        display_name = f"{display_a}–{display_b} conflict termination {low_year}"
        if high_year != low_year:
            display_name += f"–{high_year}"
        if territory:
            display_name += f" ({territory})"

        conflict_ledger = ledger_clusters.get(conflict_id, {})
        inherited_from = None
        if len(conflict_ledger) == 1:
            cluster_id, inherited_from = next(iter(conflict_ledger.items()))
        elif linked_group and end_date:
            cluster_id = f"ucdp_linked_{_slug(end_date, 24)}"
        else:
            cluster_id = f"ucdp_conflict_{_slug(conflict_id, 24)}"

        resolved_polities.update(pending_polities)
        epid = str(raw.get("c_epid", "")).strip()
        event = {
            "id": f"ucdp_term_{conflict_id}_ep{epno}_{_slug(display_name, 40)}",
            "name": display_name,
            "year": low_year,
            "end_year": high_year,
            "event_type": "war",
            "war_type": "interstate_limited",
            "scale": scale,
            "stakes": stakes,
            "decisiveness": 0.74,
            "confidence": confidence,
            "geographic_scope": 0.68 if scale == "major_war" else 0.44,
            "domain": "mixed",
            "cluster_id": cluster_id,
            "date_precision": "year",
            "sequence": int(epid) if epid.isdigit() else 0,
            "summary": (
                "Provisional strategic outcome promoted mechanically from UCDP "
                "conflict-termination episode codes. Episode-level victory (code "
                "3/4) only; severity capped at limited; secondary supporters "
                "carry no outcome. Pending claim-level human review."
            ),
            "participants": _strategic_participants(
                side_a_ids,
                side_b_ids,
                "side_a" if outcome_code == "3" else "side_b",
                confidence,
                stakes=participant_uniform,
                national_scale=participant_uniform,
                note=(
                    "Episode-level UCDP conflict-termination outcome; existential "
                    "or regime-ending severity is never inferred from UCDP "
                    "termination codes."
                ),
            ),
            "source_ids": ["ucdp_termination_conflict", "ucdp_termination_dyad"],
            "status": "complete",
            "ucdp_conflict_id": conflict_id,
            "ucdp_episode_id": epid,
            "ucdp_episode_number": epno,
            "ucdp_outcome_code": outcome_code,
            "ucdp_episode_end_date": end_date or None,
            "ucdp_end_date_precision": end_precision or None,
            "ucdp_incompatibility": incompatibility or None,
            "ucdp_intensity_level_terminal_year": intensity or None,
            "ucdp_territory_name": territory or None,
            "candidate_id": str(candidate.get("candidate_id")),
            "ucdp_party_resolutions": party_resolutions,
            "ucdp_secondary_parties": {
                "side_a": [
                    {
                        "name": name,
                        "gwno": code,
                        "resolved_entity_id": resolver(name, code, low_year, high_year)[0],
                    }
                    for name, code in secondaries_a
                ],
                "side_b": [
                    {
                        "name": name,
                        "gwno": code,
                        "resolved_entity_id": resolver(name, code, low_year, high_year)[0],
                    }
                    for name, code in secondaries_b
                ],
            },
            "ucdp_dyad_checks": dyad_checks,
        }
        if inherited_from:
            event["ucdp_cluster_inherited_from"] = inherited_from
        events.append(event)
        accepted_index.append(
            (
                event["id"],
                cluster_id,
                low_year,
                high_year,
                frozenset([*side_a_ids, *side_b_ids]),
                {
                    str(participant["entity_id"]): str(participant["termination"])
                    for participant in event["participants"]
                },
            )
        )

    return {
        "events": events,
        "rejections": rejections,
        "rows_total": len(conflict_rows),
        "episodes_promoted": len(events),
        "dyad_rows_total": len(dyad_rows),
        "dyad_rows_quarantined_corrupt": dyad_rows_quarantined_corrupt,
        "dyad_terminal_blank_outcome": dyad_terminal_blank_outcome,
        "duplicate_details": duplicate_details,
        "resolved_polities": resolved_polities,
    }


def _count_review_records(review_root: str | Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in sorted(Path(review_root).glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as handle:
            counts[path.name] = sum(1 for line in handle if line.strip())
    return counts


def _deduplicate(values: Iterable[str]) -> list[str]:
    return sorted({value for value in values if value})


def build_expanded_release(
    seed_dir: str | Path,
    review_root: str | Path,
    release_dir: str | Path,
    registry_path: str | Path,
) -> dict[str, Any]:
    seed_root = Path(seed_dir)
    review = Path(review_root)
    release = Path(release_dir)
    seed_entities: list[dict[str, Any]] = json.loads(
        (seed_root / "entities.json").read_text(encoding="utf-8")
    )
    seed_events: list[dict[str, Any]] = json.loads(
        (seed_root / "events.json").read_text(encoding="utf-8")
    )
    sources: list[dict[str, Any]] = json.loads(
        (seed_root / "sources.json").read_text(encoding="utf-8")
    )
    seed_metadata: dict[str, Any] = json.loads(
        (seed_root / "metadata.json").read_text(encoding="utf-8")
    )
    seed_by_id = {str(entity["id"]): entity for entity in seed_entities}
    seed_label_index: dict[str, set[str]] = {}
    for entity in seed_entities:
        for label in [entity.get("name"), *entity.get("aliases", [])]:
            normalized = normalize_label(label)
            if normalized:
                seed_label_index.setdefault(normalized, set()).add(str(entity["id"]))

    cliopatria = read_jsonl(review / "cliopatria-entity-candidates.jsonl")
    polities = [row for row in cliopatria if row.get("record_type") == "POLITY"]
    hced = read_jsonl(review / "hced-candidates.jsonl")
    owners: dict[str, list[dict[str, Any]]] = {}
    for candidate in polities:
        for code in candidate.get("seshat_ids", []):
            owners.setdefault(str(code), []).append(candidate)

    release_entities = {str(entity["id"]): dict(entity) for entity in seed_entities}
    candidate_by_release_id: dict[str, dict[str, Any]] = {}
    source_events: list[dict[str, Any]] = []
    iwd_events: list[dict[str, Any]] = []
    label_observations: dict[str, list[tuple[int, int, str]]] = {}
    rejections: Counter[str] = Counter()
    iwd_rejections: Counter[str] = Counter()
    curated_seed_keys = {
        _event_key(str(event["name"]), int(event["year"])) for event in seed_events
    }
    deferred_label_rows: list[dict[str, Any]] = []
    promoted_hced_keys: set[tuple[str, int]] = set()
    hced_cluster_spans: dict[str, list[Any]] = {}

    def ensure_candidate_entity(polity: dict[str, Any]) -> str:
        entity_id = _candidate_entity_id(polity)
        candidate_by_release_id[entity_id] = polity
        if entity_id in release_entities:
            return entity_id
        canonical_name = str(polity["canonical_name_candidate"])
        release_entities[entity_id] = {
            "id": entity_id,
            "name": canonical_name,
            "kind": _infer_kind(canonical_name),
            "start_year": int(polity["start_year"]),
            "end_year": int(polity["end_year"]),
            "region": "Unclassified",
            "aliases": _deduplicate(
                [
                    *map(str, polity.get("aliases", [])),
                    *map(str, polity.get("wikipedia_titles", [])),
                ]
            ),
            "predecessors": [],
            "continuity_note": (
                "Time-bounded Cliopatria interval. Namesakes, predecessors, and successors "
                "receive no inherited rating without an explicit continuity decision."
            ),
            "source_ids": ["cliopatria_v020"],
        }
        return entity_id

    for candidate in hced:
        if candidate.get("duplicate_source_id"):
            rejections["duplicate_source_id"] += 1
            continue
        if candidate.get("year_low") is None or candidate.get("year_high") is None:
            rejections["missing_or_invalid_year"] += 1
            continue
        low_year = int(candidate["year_low"])
        best_year = int(candidate["year_best"])
        high_year = int(candidate["year_high"])
        side_a_codes = _deduplicate(map(str, candidate.get("seshat_side_1_candidates", [])))
        side_b_codes = _deduplicate(map(str, candidate.get("seshat_side_2_candidates", [])))
        if not side_a_codes or not side_b_codes:
            # Rows lacking Seshat coding on a side are deferred to the second,
            # label-resolution promotion pass instead of being rejected here.
            deferred_label_rows.append(candidate)
            continue

        winner = normalize_label(candidate.get("winner_raw"))
        loser = normalize_label(candidate.get("loser_raw"))
        side_a_label = normalize_label(candidate.get("side_1_raw"))
        side_b_label = normalize_label(candidate.get("side_2_raw"))
        draw = winner in {"draw", "inconclusive", "stalemate"}
        # A blank winner is unknown, never a draw and never a vacuous match
        # against a blank side label.
        if not draw and (
            not winner or not loser or winner != side_a_label or loser != side_b_label
        ):
            rejections["outcome_not_aligned_to_crosswalk_sides"] += 1
            continue

        resolved_sides: list[list[str]] = []
        resolved_polities: dict[str, dict[str, Any]] = {}
        resolution_failed = False
        for codes in (side_a_codes, side_b_codes):
            resolved: list[str] = []
            for code in codes:
                entity_id, polity, reason = _resolve_code(code, low_year, high_year, owners)
                if not entity_id:
                    rejections[reason or "unresolved_entity"] += 1
                    resolution_failed = True
                    break
                if polity:
                    resolved_polities[entity_id] = polity
                resolved.append(entity_id)
            if resolution_failed:
                break
            resolved_sides.append(_deduplicate(resolved))
        if resolution_failed:
            continue
        side_a, side_b = resolved_sides
        if not side_a or not side_b or set(side_a) & set(side_b):
            rejections["same_or_empty_opposing_side"] += 1
            continue

        event_name = str(candidate.get("name") or candidate.get("source_record_id") or "Unnamed engagement")
        event_key = _event_key(event_name, best_year)
        if event_key in curated_seed_keys:
            rejections["duplicate_of_curated_seed"] += 1
            continue
        promoted_hced_keys.add(event_key)

        for polity in resolved_polities.values():
            ensure_candidate_entity(polity)

        for label, entity_ids in (
            (side_a_label, side_a),
            (side_b_label, side_b),
        ):
            if label and len(entity_ids) == 1:
                label_observations.setdefault(label, []).append(
                    (low_year, high_year, entity_ids[0])
                )

        scale, scale_level = _scale(candidate)
        confidence = 0.73 if candidate.get("consulted_source_raw") else 0.67
        if low_year != high_year:
            confidence -= 0.03
        confidence = round(confidence, 2)
        war_names = list(map(str, candidate.get("war_names", [])))
        cluster = _slug(war_names[0]) if war_names else None
        if cluster:
            span = hced_cluster_spans.setdefault(
                f"hced_war_{cluster}", [_war_tokens(war_names[0]), low_year, high_year]
            )
            span[1] = min(span[1], low_year)
            span[2] = max(span[2], high_year)
        source_events.append(
            {
                "id": f"hced_{_slug(str(candidate['candidate_id']), 80)}",
                "name": event_name,
                "year": low_year,
                "end_year": high_year,
                "event_type": "engagement",
                "war_type": "interstate_limited",
                "scale": scale,
                "stakes": "major" if scale_level >= 4 else "limited",
                "decisiveness": 0.32 if draw else round(min(0.90, 0.54 + 0.06 * scale_level), 2),
                "confidence": confidence,
                "geographic_scope": round(min(0.70, 0.08 + 0.09 * scale_level), 2),
                "domain": _domain(candidate.get("theatre_raw")),
                "cluster_id": f"hced_war_{cluster}" if cluster else None,
                "date_precision": "range" if low_year != high_year else "year",
                "sequence": int(candidate.get("source_row") or 0),
                "summary": (
                    "Provisional tactical result from HCED. Both opposing sides were resolved "
                    "through its Seshat crosswalk and a time-valid polity interval; this does "
                    "not infer the enclosing war's strategic outcome."
                ),
                "participants": _participants(
                    side_a,
                    side_b,
                    draw,
                    confidence,
                    scale_level,
                ),
                "source_ids": ["hced_dataset", "hced_seshat_crosswalk", "cliopatria_v020"],
                "status": "complete",
            }
        )

    polity_alias_index: dict[str, list[dict[str, Any]]] = {}
    for polity in polities:
        labels = _deduplicate(
            [
                str(polity.get("canonical_name_candidate") or ""),
                *map(str, polity.get("aliases", [])),
                *map(str, polity.get("wikipedia_titles", [])),
            ]
        )
        for label in labels:
            normalized = normalize_label(label)
            if normalized:
                polity_alias_index.setdefault(normalized, []).append(polity)

    # Own-label sets per entity, used by the observation-coherence guard in the
    # HCED label pass (the IWD path keeps the tier unguarded so the committed
    # IWD promotion stays pinned).
    entity_labels: dict[str, set[str]] = {
        str(entity["id"]): _seed_entity_labels(entity) for entity in seed_entities
    }
    for polity in polities:
        entity_labels.setdefault(_candidate_entity_id(polity), set()).update(
            _candidate_labels(polity)
        )

    label_context: dict[str, Any] = {
        "seed_entities": seed_entities,
        "seed_by_id": seed_by_id,
        "seed_label_index": seed_label_index,
        "label_observations": label_observations,
        "release_entities": release_entities,
        "entity_labels": entity_labels,
        "polity_alias_index": polity_alias_index,
    }

    def resolve_iwd_label(
        label: str,
        low_year: int,
        high_year: int,
    ) -> tuple[str | None, dict[str, Any] | None]:
        entity_id, polity, _ = _resolve_label_tiers(
            normalize_label(label),
            low_year,
            high_year,
            label_context,
            require_observation_coherence=False,
        )
        return entity_id, polity

    def resolve_iwd_party(
        name: str,
        cow_code: Any,
        low_year: int,
        high_year: int,
    ) -> tuple[str | None, dict[str, Any] | None]:
        code = str(cow_code) if cow_code else ""
        if code in IWD_COW_CODE_POLICIES:
            # An explicit COW-code policy is authoritative: outside its
            # intervals the party stays unresolved instead of falling back to
            # name matching.
            return _cow_policy_seed_id(code, low_year, high_year), None
        return resolve_iwd_label(name, low_year, high_year)

    iwd_path = review / "iwd-1.21-candidates.jsonl"
    iwd_candidates = read_jsonl(iwd_path) if iwd_path.exists() else []
    # IWD component records repeat one umbrella war across many dyads, so they
    # are rated only through parent-war coalition aggregation: at most one
    # strategic update per largerwarid, with every component row retained as
    # provenance. Parents whose sides, outcomes, or identities cannot be
    # reconstructed defensibly stay staged.
    iwd_aggregation = aggregate_iwd_parent_wars(
        iwd_candidates,
        _seed_war_token_spans(seed_events),
        resolve_iwd_party,
    )
    iwd_events.extend(iwd_aggregation["events"])
    iwd_rejections.update(iwd_aggregation["parent_rejections"])
    for polity in iwd_aggregation["resolved_polities"].values():
        ensure_candidate_entity(polity)

    # Second HCED pass: rows deferred for missing Seshat coding re-enter
    # through the declared label-resolution ruleset. It runs after IWD
    # aggregation so the IWD inputs are identical with or without the label
    # pass, and entities materialize only after every gate has passed.
    hced_label_pass = promote_hced_label_rows(
        deferred_label_rows,
        curated_seed_keys,
        promoted_hced_keys,
        lambda code, low_year, high_year: _resolve_code(code, low_year, high_year, owners),
        lambda label, low_year, high_year: resolve_hced_side_label(
            label, low_year, high_year, label_context
        ),
    )
    label_events: list[dict[str, Any]] = hced_label_pass["events"]
    hced_label_rejections: Counter[str] = hced_label_pass["rejections"]
    for polity in hced_label_pass["resolved_polities"].values():
        ensure_candidate_entity(polity)
    for cluster_id, (tokens, low_year, high_year) in hced_label_pass["cluster_spans"].items():
        span = hced_cluster_spans.setdefault(cluster_id, [tokens, low_year, high_year])
        span[1] = min(span[1], low_year)
        span[2] = max(span[2], high_year)

    # IWBD battles are deduplicated against curated seed events and every
    # HCED candidate — promoted or staged, over the candidate's full year
    # range — because an HCED row rejected today may promote later and no
    # event may ever enter the tactical stream twice.
    hced_event_keys: set[tuple[str, int]] = set()
    for candidate in hced:
        name = str(candidate.get("name") or "")
        if not name:
            continue
        year_low = candidate.get("year_low")
        year_high = candidate.get("year_high")
        if year_low is None or year_high is None:
            for year in {
                candidate.get("year_low"),
                candidate.get("year_best"),
                candidate.get("year_high"),
            }:
                if year is not None:
                    hced_event_keys.add(_event_key(name, int(year)))
            continue
        for year in range(int(year_low), int(year_high) + 1):
            hced_event_keys.add(_event_key(name, year))

    iwbd_path = review / "iwbd-candidates.jsonl"
    iwbd_candidates = read_jsonl(iwbd_path) if iwbd_path.exists() else []
    iwd_parent_ids = {
        str(candidate.get("parent_war_id"))
        for candidate in iwd_candidates
        if candidate.get("parent_war_id") is not None
    }
    iwbd_promotion = promote_iwbd_battles(
        iwbd_candidates,
        curated_seed_keys,
        hced_event_keys,
        resolve_iwd_label,
        hced_cluster_spans,
        iwd_parent_ids,
    )
    iwbd_events: list[dict[str, Any]] = iwbd_promotion["events"]
    iwbd_rejections: Counter[str] = iwbd_promotion["rejections"]
    for polity in iwbd_promotion["resolved_polities"].values():
        ensure_candidate_entity(polity)

    # UCDP conflict-termination episodes: the strategic-layer promotion path.
    # The promoted-war index (curated seed wars plus IWD parents) drives the
    # entity-and-year duplicate gate so an episode already represented in the
    # ledger is never rated twice.
    ucdp_conflict_path = review / "ucdp-termination-conflict-candidates.jsonl"
    ucdp_dyad_path = review / "ucdp-termination-dyad-candidates.jsonl"
    ucdp_conflict_rows = read_jsonl(ucdp_conflict_path) if ucdp_conflict_path.exists() else []
    ucdp_dyad_rows = read_jsonl(ucdp_dyad_path) if ucdp_dyad_path.exists() else []
    promoted_war_index = [
        (
            str(event["id"]),
            event.get("cluster_id"),
            int(event["year"]),
            int(event.get("end_year", event["year"])),
            frozenset(
                str(participant["entity_id"]) for participant in event["participants"]
            ),
            {
                str(participant["entity_id"]): str(participant.get("termination", ""))
                for participant in event["participants"]
            },
        )
        for event in (*seed_events, *iwd_events)
        if event.get("event_type") == "war"
    ]
    ucdp_promotion = promote_ucdp_termination_episodes(
        ucdp_conflict_rows,
        ucdp_dyad_rows,
        promoted_war_index,
        lambda name, gwno, low_year, high_year: resolve_ucdp_party(
            name, gwno, low_year, high_year, label_context
        ),
    )
    ucdp_events: list[dict[str, Any]] = ucdp_promotion["events"]
    ucdp_rejections: Counter[str] = ucdp_promotion["rejections"]
    for polity in ucdp_promotion["resolved_polities"].values():
        ensure_candidate_entity(polity)

    sources_by_id = {str(source["id"]): source for source in sources}
    for source in (
        {
            "id": "hced_dataset",
            "title": "Historical Conflict Event Dataset (HCED), version 5.0 / data v3",
            "url": "https://doi.org/10.7910/DVN/6ZFC0V",
            "publisher": "Harvard Dataverse",
            "license": "CC0-1.0",
            "source_type": "structured_dataset",
            "accessed": "2026-07-13",
        },
        {
            "id": "hced_seshat_crosswalk",
            "title": "HCED-to-Seshat polity crosswalk",
            "url": "https://dataverse.harvard.edu/api/access/datafile/11018172?format=original",
            "publisher": "Harvard Dataverse",
            "license": "CC0-1.0",
            "source_type": "identity_crosswalk",
            "accessed": "2026-07-13",
        },
        {
            "id": "cliopatria_v020",
            "title": "Cliopatria historical polity registry v0.2.0",
            "url": "https://doi.org/10.5281/zenodo.20274630",
            "publisher": "Seshat Global History Databank / Zenodo",
            "license": "CC-BY-4.0",
            "source_type": "historical_polity_registry",
            "accessed": "2026-07-13",
        },
        {
            "id": "iwd_dataset",
            "title": "Interstate War Data v1.21",
            "url": "https://doi.org/10.7910/DVN/WGS1YX",
            "publisher": "Harvard Dataverse",
            "license": "CC0-1.0",
            "source_type": "structured_dataset",
            "accessed": "2026-07-13",
        },
        {
            "id": "iwbd_dataset",
            "title": "Interstate War Battle dataset (IWBD)",
            "url": "https://dataverse.harvard.edu/api/access/datafile/4435240?format=original",
            "publisher": "Harvard Dataverse",
            "license": "CC0-1.0",
            "source_type": "structured_dataset",
            "accessed": "2026-07-13",
        },
        {
            "id": "ucdp_termination_conflict",
            "title": "UCDP Conflict Termination Dataset v4-2024, conflict level",
            "url": "https://ucdp.uu.se/downloads/monadterm/UCDPConflictTerminationDataset_v4_2024_Conflict.csv",
            "publisher": "Uppsala Conflict Data Program",
            "license": "CC-BY-4.0",
            "source_type": "structured_dataset",
            "accessed": "2026-07-13",
        },
        {
            "id": "ucdp_termination_dyad",
            "title": "UCDP Conflict Termination Dataset v4-2024, dyad level",
            "url": "https://ucdp.uu.se/downloads/monadterm/UCDPConflictTerminationDataset_v4_2024_Dyad.csv",
            "publisher": "Uppsala Conflict Data Program",
            "license": "CC-BY-4.0",
            "source_type": "structured_dataset",
            "accessed": "2026-07-13",
        },
    ):
        sources_by_id[source["id"]] = source

    all_events = [
        *seed_events,
        *source_events,
        *iwd_events,
        *label_events,
        *iwbd_events,
        *ucdp_events,
    ]
    used_entity_ids = {
        str(participant["entity_id"])
        for event in all_events
        for participant in event["participants"]
    }
    release_entity_rows = sorted(
        release_entities.values(),
        key=lambda entity: (int(entity["start_year"]), str(entity["name"]), str(entity["id"])),
    )
    review_counts = _count_review_records(review)

    registry_entities: dict[str, dict[str, Any]] = {
        str(entity["id"]): {
            "id": str(entity["id"]),
            "name": str(entity["name"]),
            "kind": str(entity.get("kind") or "polity"),
            "start_year": int(entity["start_year"]),
            "end_year": int(entity["end_year"]) if entity.get("end_year") is not None else None,
            "status": "rated" if str(entity["id"]) in used_entity_ids else "unrated",
            "identity_status": "curated",
            "region": str(entity.get("region") or "Unclassified"),
        }
        for entity in seed_entities
    }
    used_candidate_ids = {
        str(candidate["candidate_id"]) for candidate in candidate_by_release_id.values()
    }
    for candidate in polities:
        mapped_seed = _candidate_policy_seed(candidate, seed_by_id)
        if not mapped_seed:
            name_matches = seed_label_index.get(
                normalize_label(candidate.get("canonical_name_candidate")), set()
            )
            if len(name_matches) == 1:
                named_seed = next(iter(name_matches))
                named_entity = seed_by_id.get(named_seed)
                # A name match alone must not bridge eras: a same-named polity
                # from a different century keeps its own registry row.
                if named_entity and _candidate_overlaps_entity(candidate, named_entity):
                    mapped_seed = named_seed
        if mapped_seed and mapped_seed in registry_entities:
            continue
        entity_id = _candidate_entity_id(candidate)
        registry_entities[entity_id] = {
            "id": entity_id,
            "name": str(candidate["canonical_name_candidate"]),
            "kind": _infer_kind(str(candidate["canonical_name_candidate"])),
            "start_year": int(candidate["start_year"]),
            "end_year": int(candidate["end_year"]),
            "status": (
                "provisional"
                if str(candidate["candidate_id"]) in used_candidate_ids
                else "unrated"
            ),
            "identity_status": "source_candidate",
            "coverage_discontinuous": len(
                candidate.get("temporal_coverage_groups", [])
            ) > 1,
            "region": "Unclassified",
        }

    registry_rows = sorted(
        registry_entities.values(),
        key=lambda entity: (str(entity["name"]), int(entity["start_year"]), str(entity["id"])),
    )
    staged_source_records = sum(review_counts.values())
    identity_queue_names = {
        "cliopatria-entity-candidates.jsonl",
        "ucdp-actor-26.1-candidates.jsonl",
    }
    unresolved_event_candidates = max(
        0,
        sum(
            count
            for name, count in review_counts.items()
            if name not in identity_queue_names
        )
        - len(source_events)
        - len(label_events)
        - len(iwbd_events)
        - len(ucdp_events)
        - iwd_aggregation["components_attached"],
    )
    latest_rated_event_year = max(int(event["end_year"]) for event in all_events)
    coverage = {
        "registry_polities": len(registry_rows),
        "rated_entities": len(used_entity_ids),
        "rated_events": len(all_events),
        "staged_source_records": staged_source_records,
        "unresolved_event_candidates": unresolved_event_candidates,
        "latest_rated_event_year": latest_rated_event_year,
        "curated_seed_events": len(seed_events),
        "provisional_hced_events": len(source_events),
        "provisional_hced_label_events": len(label_events),
        "provisional_iwd_wars": len(iwd_events),
        "provisional_iwbd_battles": len(iwbd_events),
        "iwbd_battles_total": iwbd_promotion["battles_total"],
        "provisional_ucdp_events": len(ucdp_events),
        "ucdp_termination_rows_total": ucdp_promotion["rows_total"],
        "iwd_parent_wars_total": iwd_aggregation["parents_total"],
        "iwd_component_records": iwd_aggregation["components_total"],
        "iwd_components_aggregated": iwd_aggregation["components_aggregated"],
        "source_queue_counts": review_counts,
    }
    registry = {"entities": registry_rows, "coverage": coverage}

    metadata = {
        **seed_metadata,
        "dataset_id": "military-elo-expanded-provisional-v0.2",
        "title": "Expanded provisional Military History Elo evidence release",
        "version": "0.2.0",
        "coverage_status": "expanded_provisional",
        "comprehensive": False,
        "description": (
            "The curated seed plus source-derived tactical tranches (crosswalk-resolved and "
            "label-resolved HCED engagements, deduplicated IWBD battles) and strategic "
            "tranches (aggregated IWD coalition wars, UCDP terminal-victory episodes). "
            "The separate registry publishes time-bounded Cliopatria polity candidates, "
            "including unrated entries, without assigning them invented Elo results."
        ),
        "coverage_note": (
            "Registry coverage is much broader than rating coverage. Source-derived HCED "
            "and IWBD engagements remain provisional; IWD component wars enter only as one "
            "aggregated coalition update per parent conflict, UCDP termination records only "
            "as conflict-level terminal victory episodes, and unresolved records do not affect Elo. "
            f"The latest rated event ends in {latest_rated_event_year}; later timeline years carry ratings forward."
        ),
        "footer_note": (
            "Known polities, entities with Elo, and staged source records are reported separately. "
            "Absence from the rating ledger is not evidence of military failure."
        ),
        "record_counts_expected": {
            "entities": len(release_entity_rows),
            "events": len(all_events),
            "sources": len(sources_by_id),
            "registry_polities": len(registry_rows),
        },
        "year_range": {
            "start": min(int(event["year"]) for event in all_events),
            "end": max(int(event["end_year"]) for event in all_events),
            "calendar_note": seed_metadata.get("year_range", {}).get("calendar_note", ""),
        },
        "promotion": {
            "policy": (
                "Only nonduplicate HCED rows with aligned outcomes, both Seshat-coded sides, "
                "and unique time-valid polity identities enter the provisional tactical ledger. "
                "Rows lacking Seshat coding on one or both sides are retried in a second, "
                "declared label-resolution pass: sides resolve only through explicit "
                "time-bounded label policies or exact-normalized alias matching with "
                "uniqueness, full event-interval validity, and name-coherence for "
                "observation-derived pairings; faction and collective-peoples labels never "
                "resolve; polity labels pending identity splits never resolve; ambiguity "
                "always stays staged. Label-resolved events carry reduced identity confidence "
                "and an identity_resolution provenance marker. "
                "IWD component wars never enter individually: each parent conflict is rated at "
                "most once, as a coalition event aggregated from its component dyads, and only "
                "when the reconstructed sides are consistent, the component outcomes are "
                "unanimous, no curated seed war overlaps, and every belligerent resolves to a "
                "unique time-bounded identity. All other parent wars stay staged. "
                "IWBD battles enter only when they are not a duplicate of any curated seed "
                "event, any HCED candidate (promoted or staged), or an earlier IWBD row by "
                "normalized battle name and year within one year; their date span does not "
                "contain a differently-named battle of the same war (campaign umbrellas stay "
                "staged); the coded victor matches a named side; both sides are single "
                "polities resolving to unique time-bounded identities outside declared deny "
                "windows; and severity is capped at limited. Duplicate matches are excluded, "
                "never merged. "
                "UCDP conflict-termination episodes promote only as conflict-level terminal "
                "victory episodes (outcome codes 3/4): peace agreements, ceasefires, low "
                "activity, and actor cessation stay staged; every primary party must be a "
                "state resolving to a unique time-bounded identity through explicit "
                "Gleditsch-Ward code policies or exact time-valid alias matching; episodes "
                "duplicating an already-promoted strategic event, contradicted by a terminal "
                "dyad row, linked by end date to an oppositely-oriented victory assertion, or "
                "carrying a documented side-attribution dispute stay staged; severity is "
                "capped at limited and secondary supporters carry no outcome."
            ),
            "accepted_hced_events": len(source_events),
            "accepted_hced_label_events": len(label_events),
            "hced_label_pass_input_rows": hced_label_pass["rows_total"],
            "accepted_iwd_wars": len(iwd_events),
            "iwd_parent_wars_total": iwd_aggregation["parents_total"],
            "iwd_components_aggregated": iwd_aggregation["components_aggregated"],
            "iwd_components_attached_to_rated_parents": iwd_aggregation["components_attached"],
            "hced_rejections": dict(sorted(rejections.items())),
            "hced_label_rejections": _declared_rejections(
                hced_label_rejections, HCED_LABEL_REJECTION_COUNTERS
            ),
            "hced_label_policy_labels": sorted(HCED_LABEL_POLICIES),
            "hced_faction_labels_staged": sorted(HCED_FACTION_LABELS),
            "hced_pending_split_labels": sorted(HCED_PENDING_SPLIT_LABELS),
            "hced_label_observation_resolutions": hced_label_pass["observation_resolutions"],
            "iwd_rejections": dict(sorted(iwd_rejections.items())),
            "accepted_iwbd_battles": len(iwbd_events),
            "iwbd_battles_total": iwbd_promotion["battles_total"],
            "iwbd_rejections": _declared_rejections(iwbd_rejections, IWBD_REJECTION_COUNTERS),
            "accepted_ucdp_events": len(ucdp_events),
            "ucdp_termination_rows_total": ucdp_promotion["rows_total"],
            "ucdp_rejections": _declared_rejections(ucdp_rejections, UCDP_REJECTION_COUNTERS),
            "ucdp_curated_exclusions": [
                {"conflict_id": key[0], "episode_number": key[1], "reason": reason}
                for key, reason in sorted(UCDP_CURATED_EXCLUSIONS.items())
            ],
            "ucdp_duplicate_details": ucdp_promotion["duplicate_details"],
            "ucdp_dyad_rows_total": ucdp_promotion["dyad_rows_total"],
            "ucdp_dyad_rows_quarantined_corrupt": ucdp_promotion[
                "dyad_rows_quarantined_corrupt"
            ],
            "ucdp_dyad_terminal_blank_outcome": ucdp_promotion["dyad_terminal_blank_outcome"],
            "source_queue_counts": review_counts,
        },
        "known_limitations": [
            "The release is not a complete census and must not be presented as a definitive all-history ranking.",
            "Strategic war outcomes remain much less complete than tactical engagement outcomes.",
            "HCED winner labels and the Seshat crosswalk are source assertions pending claim-level human review.",
            "Label-resolved HCED events rest on side-name identity policies and exact alias matches rather than the Seshat crosswalk; they carry lower confidence and remain source assertions pending claim-level human review, and the label-policy entries are entity-boundary decisions pending second-reviewer sign-off.",
            "Cliopatria intervals are split at temporal gaps; final historiographic continuity still requires explicit decisions.",
            "Some Cliopatria identity intervals span successive regimes (for example one Cambodia identity covering 1956-2024), so events resolved to them can share a rating line across regime changes until those identities receive explicit curated splits.",
            "Aggregated IWD coalition events use declared uniform defaults for contribution, role, scale, and stakes because the source carries no per-participant data.",
            "IWBD events use declared uniform defaults for scale, stakes, contribution, and role because the source carries no per-battle magnitude data, and IWBD war-level victor codes are ignored: battle records never update strategic outcomes.",
            "Coalition-labelled IWBD battles (notably both world wars) remain staged pending curated coalition composition, and IWBD rows whose date span contains a sibling battle are staged as presumptive campaign umbrellas, which also quarantines some genuinely distinct long engagements.",
            "IWBD-HCED name and date matches are counted as exclusions only; they are not treated as independent corroboration and no HCED record is modified.",
            "UCDP episode-level termination outcomes may not describe every supporter: secondary parties are recorded without outcomes, and uniform strategic vectors with scale-linked participant uniforms are declared defaults, as with IWD.",
            "The 1967 Arab-Israeli fronts and the 1974 Paracel episode stay staged: the source carries mutually contradictory orientations for the former and a documented side-attribution dispute for the latter.",
            "Ancient, non-literate, small, defeated, and non-European polities remain systematically under-recorded.",
        ],
        "prohibited_interpretation": (
            "Do not treat provisional ratings or unrated registry entries as a definitive ranking "
            "of every country and empire in history."
        ),
    }

    _write_json(release / "entities.json", release_entity_rows)
    _write_json(release / "events.json", all_events)
    _write_json(release / "sources.json", sorted(sources_by_id.values(), key=lambda row: row["id"]))
    _write_json(release / "metadata.json", metadata)
    _write_json(registry_path, registry)
    return {
        "entities": len(release_entity_rows),
        "rated_entities": len(used_entity_ids),
        "events": len(all_events),
        "provisional_hced_events": len(source_events),
        "provisional_hced_label_events": len(label_events),
        "provisional_iwd_wars": len(iwd_events),
        "provisional_iwbd_battles": len(iwbd_events),
        "provisional_ucdp_events": len(ucdp_events),
        "registry_polities": len(registry_rows),
        "staged_source_records": staged_source_records,
        "unresolved_event_candidates": unresolved_event_candidates,
        "hced_rejections": dict(sorted(rejections.items())),
        "hced_label_rejections": _declared_rejections(
            hced_label_rejections, HCED_LABEL_REJECTION_COUNTERS
        ),
        "iwd_rejections": dict(sorted(iwd_rejections.items())),
        "iwbd_rejections": _declared_rejections(iwbd_rejections, IWBD_REJECTION_COUNTERS),
        "ucdp_rejections": _declared_rejections(ucdp_rejections, UCDP_REJECTION_COUNTERS),
    }
