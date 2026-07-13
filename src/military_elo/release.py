from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
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
                    "note": "Provisional HCED tactical coding; strategic war outcome is not inferred.",
                }
            )
    return output


def _strategic_participants(
    side_a: list[str],
    side_b: list[str],
    outcome: str,
    confidence: float,
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
                    "stakes": 0.72,
                    "national_scale": 0.72,
                    "termination": terminations[index],
                    "evidence_confidence": confidence,
                    "result_class": result_classes[index],
                    "outcome": side_values[index],
                    "note": (
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
            rejections["uncoded_side"] += 1
            continue

        winner = normalize_label(candidate.get("winner_raw"))
        loser = normalize_label(candidate.get("loser_raw"))
        side_a_label = normalize_label(candidate.get("side_1_raw"))
        side_b_label = normalize_label(candidate.get("side_2_raw"))
        draw = winner in {"draw", "inconclusive", "stalemate"}
        if not draw and (winner != side_a_label or loser != side_b_label):
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

    def resolve_iwd_label(
        label: str,
        low_year: int,
        high_year: int,
    ) -> tuple[str | None, dict[str, Any] | None]:
        normalized = normalize_label(label)
        seed_matches = {
            str(entity["id"])
            for entity in seed_entities
            if _entity_covers(entity, low_year, high_year)
            and normalized
            in {
                normalize_label(entity.get("name")),
                *[normalize_label(alias) for alias in entity.get("aliases", [])],
            }
        }
        if len(seed_matches) == 1:
            return next(iter(seed_matches)), None

        observed_matches = {
            entity_id
            for _, _, entity_id in label_observations.get(normalized, [])
            if entity_id in release_entities
            and _entity_covers(release_entities[entity_id], low_year, high_year)
        }
        if len(observed_matches) == 1:
            return next(iter(observed_matches)), None

        candidate_matches = [
            polity
            for polity in polity_alias_index.get(normalized, [])
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
                name_matches = seed_label_index.get(
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
                    return mapped_seed, None
                return None, None
            return _candidate_entity_id(polity), polity
        return None, None

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
    ):
        sources_by_id[source["id"]] = source

    all_events = [*seed_events, *source_events, *iwd_events]
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
        "provisional_iwd_wars": len(iwd_events),
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
            "The curated seed plus strict source-derived HCED tactical and IWD strategic tranches. "
            "The separate registry publishes time-bounded Cliopatria polity candidates, "
            "including unrated entries, without assigning them invented Elo results."
        ),
        "coverage_note": (
            "Registry coverage is much broader than rating coverage. Source-derived HCED "
            "engagements remain provisional; IWD component wars enter only as one aggregated "
            "coalition update per parent conflict, and unresolved records do not affect Elo. "
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
                "IWD component wars never enter individually: each parent conflict is rated at "
                "most once, as a coalition event aggregated from its component dyads, and only "
                "when the reconstructed sides are consistent, the component outcomes are "
                "unanimous, no curated seed war overlaps, and every belligerent resolves to a "
                "unique time-bounded identity. All other parent wars stay staged."
            ),
            "accepted_hced_events": len(source_events),
            "accepted_iwd_wars": len(iwd_events),
            "iwd_parent_wars_total": iwd_aggregation["parents_total"],
            "iwd_components_aggregated": iwd_aggregation["components_aggregated"],
            "iwd_components_attached_to_rated_parents": iwd_aggregation["components_attached"],
            "hced_rejections": dict(sorted(rejections.items())),
            "iwd_rejections": dict(sorted(iwd_rejections.items())),
            "source_queue_counts": review_counts,
        },
        "known_limitations": [
            "The release is not a complete census and must not be presented as a definitive all-history ranking.",
            "Strategic war outcomes remain much less complete than tactical engagement outcomes.",
            "HCED winner labels and the Seshat crosswalk are source assertions pending claim-level human review.",
            "Cliopatria intervals are split at temporal gaps; final historiographic continuity still requires explicit decisions.",
            "Some Cliopatria identity intervals span successive regimes (for example one Cambodia identity covering 1956-2024), so events resolved to them can share a rating line across regime changes until those identities receive explicit curated splits.",
            "Aggregated IWD coalition events use declared uniform defaults for contribution, role, scale, and stakes because the source carries no per-participant data.",
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
        "provisional_iwd_wars": len(iwd_events),
        "registry_polities": len(registry_rows),
        "staged_source_records": staged_source_records,
        "unresolved_event_candidates": unresolved_event_candidates,
        "hced_rejections": dict(sorted(rejections.items())),
        "iwd_rejections": dict(sorted(iwd_rejections.items())),
    }
