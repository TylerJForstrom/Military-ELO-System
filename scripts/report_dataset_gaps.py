from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from military_elo.promotion.common import (  # noqa: E402
    _normalized_event_name,
    normalize_label,
)


EARTH_RADIUS_KM = 6371.0088
MATCH_DISTANCE_KM = 25.0
SIGNED_YEAR = re.compile(r"^([+-]?\d+)-")

# P17 is a source-asserted country/jurisdiction claim, not battlefield
# geography. These deliberately conservative lanes cover the high-frequency
# claims needed for the gap comparison; everything else remains explicit as
# unmapped instead of being inferred from a combatant name or coordinate.
REGION_QIDS: dict[str, frozenset[str]] = {
    "Japan": frozenset({"Q17", "Q188712"}),
    "China": frozenset(
        {
            "Q148",
            "Q13426199",
            "Q8733",
            "Q7313",
            "Q1147037",
            "Q1147043",
            "Q391189",
            "Q30623",
        }
    ),
    "Korea and Mongolia": frozenset(
        {"Q884", "Q423", "Q28179", "Q28208", "Q711", "Q212056"}
    ),
    "Indian subcontinent": frozenset(
        {"Q668", "Q843", "Q902", "Q854", "Q837"}
    ),
    "Southeast Asia": frozenset(
        {
            "Q881",
            "Q252",
            "Q833",
            "Q836",
            "Q869",
            "Q424",
            "Q928",
            "Q334",
            "Q819",
            "Q574",
            "Q887803",
        }
    ),
    "West Asia and North Africa": frozenset(
        {
            "Q43",
            "Q858",
            "Q796",
            "Q794",
            "Q262",
            "Q79",
            "Q948",
            "Q889",
            "Q822",
            "Q851",
            "Q805",
            "Q810",
            "Q1028",
            "Q1016",
            "Q1049",
            "Q801",
            "Q219060",
            "Q23792",
            "Q12560",
            "Q83891",
            "Q12536",
            "Q63134381",
            "Q18234383",
            "Q160307",
            "Q55502",
            "Q75613",
            "Q8575586",
            "Q63135869",
            "Q975405",
            "Q6159007",
            "Q199688",
            "Q282428",
            "Q12490507",
            "Q171740",
            "Q1337854",
            "Q622855",
            "Q3708094",
            "Q582861",
            "Q3934817",
            "Q12183875",
            "Q3045696",
        }
    ),
    "Central Asia and Caucasus": frozenset(
        {"Q265", "Q232", "Q874", "Q863", "Q227", "Q399", "Q230"}
    ),
    "Mediterranean Europe": frozenset(
        {
            "Q29",
            "Q38",
            "Q41",
            "Q45",
            "Q229",
            "Q233",
            "Q222",
            "Q219",
            "Q224",
            "Q3399982",
            "Q766543",
            "Q217196",
            "Q45670",
            "Q12544",
            "Q17167",
            "Q1747689",
            "Q42834",
            "Q838931",
            "Q204920",
            "Q2429397",
            "Q170174",
            "Q173065",
            "Q4948",
            "Q200464",
            "Q604593",
            "Q238445",
            "Q188586",
            "Q199442",
            "Q153529",
            "Q170174",
            "Q174306",
            "Q106312111",
        }
    ),
    "Western and Northern Europe": frozenset(
        {
            "Q142",
            "Q145",
            "Q183",
            "Q31",
            "Q55",
            "Q34",
            "Q20",
            "Q35",
            "Q27",
            "Q25",
            "Q39",
            "Q40",
            "Q179876",
            "Q230791",
            "Q70972",
            "Q215530",
            "Q161885",
            "Q105313",
            "Q146246",
            "Q583038",
            "Q38872",
            "Q27306",
            "Q8680",
            "Q153136",
            "Q1031430",
            "Q186320",
            "Q174193",
            "Q215443",
            "Q330362",
            "Q642314",
        }
    ),
    "Eastern Europe": frozenset(
        {
            "Q36",
            "Q212",
            "Q159",
            "Q213",
            "Q28",
            "Q218",
            "Q403",
            "Q184",
            "Q191",
            "Q211",
            "Q221",
            "Q225",
            "Q37",
            "Q214",
            "Q236",
            "Q172107",
            "Q34266",
            "Q207272",
            "Q186096",
            "Q217",
            "Q42585",
            "Q171150",
            "Q1108445",
            "Q10957559",
            "Q154667",
            "Q389004",
            "Q156020",
            "Q170770",
            "Q16056854",
        }
    ),
    "Sub-Saharan Africa": frozenset(
        {
            "Q258",
            "Q1045",
            "Q912",
            "Q115",
            "Q1033",
            "Q117",
            "Q986",
            "Q974",
            "Q1032",
            "Q1029",
            "Q1036",
            "Q657",
            "Q1009",
            "Q916",
            "Q207521",
            "Q1041",
            "Q114",
            "Q924",
            "Q1030",
            "Q958",
            "Q729768",
        }
    ),
    "Americas": frozenset(
        {
            "Q30",
            "Q96",
            "Q16",
            "Q414",
            "Q419",
            "Q298",
            "Q717",
            "Q241",
            "Q790",
            "Q739",
            "Q77",
            "Q733",
            "Q28573",
            "Q179997",
            "Q861551",
            "Q736",
            "Q750",
            "Q155",
            "Q811",
            "Q804",
            "Q783",
            "Q792",
            "Q211435",
            "Q170603",
            "Q8965",
            "Q2919465",
            "Q2039931",
            "Q2608489",
            "Q170604",
            "Q242",
        }
    ),
    "Oceania": frozenset({"Q691", "Q664", "Q408"}),
}

FUNNEL_REGION_HINTS = {
    "algeria": "West Asia and North Africa",
    "cheyenne": "Americas",
    "commanche": "Americas",
    "germanic tribes": "Western and Northern Europe",
    "huang chao": "China",
    "libya": "West Asia and North Africa",
    "sassanid empire": "West Asia and North Africa",
    "sioux indians cheyenne indians": "Americas",
    "tidikelt tribes": "West Asia and North Africa",
    "tripoli": "West Asia and North Africa",
    "wurtemburg": "Western and Northern Europe",
}


def _qid_region_index() -> dict[str, str]:
    index: dict[str, str] = {}
    for region, qids in REGION_QIDS.items():
        for qid in qids:
            existing = index.get(qid)
            if existing is not None and existing != region:
                raise RuntimeError(f"Region mapping repeats {qid}: {existing}, {region}")
            index[qid] = region
    return index


QID_REGION = _qid_region_index()


def file_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        Path(path).read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} is not a JSON object")
        rows.append(value)
    return rows


def parse_signed_year(value: Any) -> int | None:
    match = SIGNED_YEAR.match(str(value or ""))
    return int(match.group(1)) if match else None


def normalized_event_name(value: Any) -> str:
    return _normalized_event_name(str(value or ""))


def valid_coordinates(row: Mapping[str, Any]) -> tuple[float, float] | None:
    try:
        latitude = float(row.get("latitude"))
        longitude = float(row.get("longitude"))
    except (TypeError, ValueError):
        return None
    if (
        not math.isfinite(latitude)
        or not math.isfinite(longitude)
        or not -90.0 <= latitude <= 90.0
        or not -180.0 <= longitude <= 180.0
        or (latitude == 0.0 and longitude == 0.0)
    ):
        return None
    return latitude, longitude


def haversine_km(first: tuple[float, float], second: tuple[float, float]) -> float:
    latitude_1, longitude_1 = map(math.radians, first)
    latitude_2, longitude_2 = map(math.radians, second)
    delta_latitude = latitude_2 - latitude_1
    delta_longitude = longitude_2 - longitude_1
    haversine = (
        math.sin(delta_latitude / 2.0) ** 2
        + math.cos(latitude_1)
        * math.cos(latitude_2)
        * math.sin(delta_longitude / 2.0) ** 2
    )
    return EARTH_RADIUS_KM * 2.0 * math.asin(min(1.0, math.sqrt(haversine)))


def century_bucket(year: int | None) -> tuple[int, str]:
    if year is None:
        return 10**9, "Unknown year"
    if year == 0:
        return 0, "Year 0"
    if year < 0:
        century = ((-year - 1) // 100) + 1
        return -century * 100, f"{century}{_ordinal_suffix(century)} century BCE"
    century = ((year - 1) // 100) + 1
    return (century - 1) * 100 + 1, f"{century}{_ordinal_suffix(century)} century CE"


def _ordinal_suffix(number: int) -> str:
    if 10 <= number % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")


def candidate_regions(row: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    country_qids = sorted({str(qid) for qid in row.get("countries", []) if qid})
    regions = sorted({QID_REGION[qid] for qid in country_qids if qid in QID_REGION})
    unmapped = sorted(qid for qid in country_qids if qid not in QID_REGION)
    if regions:
        return regions, unmapped
    if country_qids:
        return ["Unmapped P17 jurisdiction"], unmapped
    return ["No P17 jurisdiction claim"], []


def distinct_participant_count(row: Mapping[str, Any]) -> int:
    return len(
        {
            str(participant.get("uri"))
            for participant in row.get("participants", [])
            if isinstance(participant, Mapping) and participant.get("uri")
        }
    )


def _hced_year_interval(row: Mapping[str, Any]) -> tuple[int, int] | None:
    low = row.get("year_low", row.get("year_best"))
    high = row.get("year_high", row.get("year_best"))
    if isinstance(low, bool) or isinstance(high, bool):
        return None
    if not isinstance(low, int) or not isinstance(high, int):
        return None
    return min(low, high), max(low, high)


def deduplicate_wikidata_candidates(
    wikidata_rows: Iterable[dict[str, Any]], hced_rows: Iterable[dict[str, Any]]
) -> list[dict[str, Any]]:
    hced_by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in hced_rows:
        normalized_name = normalized_event_name(row.get("name"))
        if normalized_name:
            hced_by_name[normalized_name].append(row)

    annotations: list[dict[str, Any]] = []
    seen_candidate_ids: set[str] = set()
    for row in wikidata_rows:
        candidate_id = str(row.get("candidate_id") or "")
        if not candidate_id or candidate_id in seen_candidate_ids:
            raise ValueError(f"Missing or duplicate Wikidata candidate_id: {candidate_id!r}")
        seen_candidate_ids.add(candidate_id)
        year = parse_signed_year(row.get("date"))
        point = valid_coordinates(row)
        same_name_year: list[dict[str, Any]] = []
        matches: list[dict[str, Any]] = []
        normalized_name = normalized_event_name(row.get("name"))
        for hced in hced_by_name.get(normalized_name, []) if normalized_name else []:
            interval = _hced_year_interval(hced)
            if year is None or interval is None:
                continue
            low, high = interval
            if not low - 1 <= year <= high + 1:
                continue
            hced_id = str(hced.get("candidate_id") or "")
            same_name_year.append(
                {
                    "candidate_id": hced_id,
                    "name": hced.get("name"),
                    "year_best": hced.get("year_best"),
                }
            )
            hced_point = valid_coordinates(hced)
            if point is None or hced_point is None:
                continue
            distance = haversine_km(point, hced_point)
            if distance < MATCH_DISTANCE_KM:
                matches.append(
                    {
                        "candidate_id": hced_id,
                        "distance_km": round(distance, 3),
                        "name": hced.get("name"),
                        "year_best": hced.get("year_best"),
                    }
                )
        same_name_year.sort(key=lambda item: item["candidate_id"])
        matches.sort(key=lambda item: (item["distance_km"], item["candidate_id"]))
        regions, unmapped_qids = candidate_regions(row)
        _, century = century_bucket(year)
        participant_count = distinct_participant_count(row)
        annotations.append(
            {
                "candidate_id": candidate_id,
                "century": century,
                "countries": sorted(set(map(str, row.get("countries", [])))),
                "date": row.get("date"),
                "genuinely_new_under_contract": not matches,
                "has_coordinates": point is not None,
                "hced_match_candidates": matches,
                "hced_same_name_year_candidates": same_name_year,
                "kind": row.get("kind"),
                "name": row.get("name"),
                "participant_count": participant_count,
                "regions": regions,
                "unmapped_country_qids": unmapped_qids,
                "year": year,
            }
        )
    return annotations


def brecke_coverage(
    brecke_rows: Iterable[dict[str, Any]], hced_rows: Iterable[dict[str, Any]]
) -> dict[str, Any]:
    hced_by_war_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in hced_rows:
        for war_name in row.get("war_names", []):
            normalized = normalize_label(war_name)
            if normalized:
                hced_by_war_name[normalized].append(row)

    annotated: list[dict[str, Any]] = []
    for war in brecke_rows:
        aliases = {
            normalize_label(alias)
            for alias in war.get("aliases", [])
            if normalize_label(alias)
        }
        name_matches: dict[str, dict[str, Any]] = {}
        for alias in aliases:
            for hced in hced_by_war_name.get(alias, []):
                candidate_id = str(hced.get("candidate_id") or "")
                name_matches[candidate_id] = hced

        verified: list[str] = []
        status = str(war.get("interval_status") or "")
        start_year = war.get("start_year")
        end_year = war.get("end_year")
        if status == "closed" and isinstance(start_year, int) and isinstance(end_year, int):
            for candidate_id, hced in name_matches.items():
                interval = _hced_year_interval(hced)
                if interval is None:
                    continue
                hced_low, hced_high = interval
                if hced_low <= end_year and hced_high >= start_year:
                    verified.append(candidate_id)
        annotated.append(
            {
                "brecke_id": war.get("brecke_id"),
                "end_year": end_year,
                "hced_match_candidates": sorted(verified),
                "interval_status": status,
                "name_only_match_candidates": sorted(name_matches),
                "region_code": war.get("region_code"),
                "region_label": war.get("region_label"),
                "start_year": start_year,
                "war_name": war.get("war_name"),
            }
        )

    zero = [row for row in annotated if not row["hced_match_candidates"]]
    zero_by_region: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in zero:
        zero_by_region[str(row.get("region_label") or "Unclassified")].append(row)
    for rows in zero_by_region.values():
        rows.sort(
            key=lambda row: (
                row["start_year"] if isinstance(row["start_year"], int) else 10**9,
                str(row["war_name"]),
                str(row["brecke_id"]),
            )
        )
    return {
        "records": annotated,
        "summary": {
            "total_wars": len(annotated),
            "verified_hced_match": len(annotated) - len(zero),
            "zero_matching_hced_battles": len(zero),
            "zero_match_by_region": {
                region: len(rows) for region, rows in sorted(zero_by_region.items())
            },
        },
        "zero_match_wars_by_region": dict(sorted(zero_by_region.items())),
    }


def _counter_rows(counter: Counter[str], key_name: str) -> list[dict[str, Any]]:
    return [
        {key_name: key, "count": count}
        for key, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def build_report(
    wikidata_path: str | Path,
    hced_path: str | Path,
    brecke_path: str | Path,
    funnel_path: str | Path,
) -> dict[str, Any]:
    wikidata_rows = load_jsonl(wikidata_path)
    hced_rows = load_jsonl(hced_path)
    brecke_rows = load_jsonl(brecke_path)
    funnel = json.loads(Path(funnel_path).read_text(encoding="utf-8"))
    annotations = deduplicate_wikidata_candidates(wikidata_rows, hced_rows)

    genuinely_new = [row for row in annotations if row["genuinely_new_under_contract"]]
    pre_1500 = [row for row in genuinely_new if row["year"] is not None and row["year"] < 1500]
    actionable_pre_1500 = [row for row in pre_1500 if row["participant_count"] >= 2]
    century_counts: Counter[str] = Counter(row["century"] for row in genuinely_new)
    century_sort = {
        label: sort
        for row in genuinely_new
        for sort, label in [century_bucket(row["year"])]
    }
    century_rows = [
        {"century": label, "count": century_counts[label]}
        for label in sorted(century_counts, key=lambda label: (century_sort[label], label))
    ]

    region_all: Counter[str] = Counter()
    region_pre_1500: Counter[str] = Counter()
    region_actionable: Counter[str] = Counter()
    unmapped_qids: Counter[str] = Counter()
    for row in genuinely_new:
        for region in row["regions"]:
            region_all[region] += 1
        for qid in row["unmapped_country_qids"]:
            unmapped_qids[qid] += 1
    for row in pre_1500:
        for region in row["regions"]:
            region_pre_1500[region] += 1
    for row in actionable_pre_1500:
        for region in row["regions"]:
            region_actionable[region] += 1

    all_regions = sorted(set(region_all) | set(region_pre_1500) | set(region_actionable))
    revised_ranking = sorted(
        (
            {
                "region": region,
                "actionable_new_pre_1500": region_actionable[region],
                "all_new_pre_1500": region_pre_1500[region],
                "all_new_candidates": region_all[region],
            }
            for region in all_regions
        ),
        key=lambda row: (
            -row["actionable_new_pre_1500"],
            -row["all_new_pre_1500"],
            row["region"],
        ),
    )
    current_funnel = list(funnel.get("greedy_batch", {}).get("ranking", []))
    top_ten_funnel_regions = {
        FUNNEL_REGION_HINTS.get(str(row.get("label") or ""))
        for row in current_funnel[:10]
    } - {None}
    classified_ranking = [
        row
        for row in revised_ranking
        if row["region"]
        not in {"No P17 jurisdiction claim", "Unmapped P17 jurisdiction"}
    ]
    leading_region = classified_ranking[0] if classified_ranking else None
    top_twenty_funnel_yield = (
        int(current_funnel[19].get("cumulative_events", 0))
        if len(current_funnel) >= 20
        else sum(int(row.get("marginal_events", 0)) for row in current_funnel[:20])
    )
    material_disagreement = bool(
        leading_region
        and leading_region["region"] not in top_ten_funnel_regions
        and leading_region["actionable_new_pre_1500"] > 2 * top_twenty_funnel_yield
    )
    rank_by_region = {
        row["region"]: rank for rank, row in enumerate(revised_ranking, start=1)
    }
    scouting_expectation_ranks = {
        region: rank_by_region.get(region)
        for region in (
            "Japan",
            "China",
            "West Asia and North Africa",
            "Indian subcontinent",
        )
    }
    scouting_expectation_supported = all(
        isinstance(rank, int) and rank <= 4
        for rank in scouting_expectation_ranks.values()
    )

    brecke = brecke_coverage(brecke_rows, hced_rows)
    matched = [row for row in annotations if row["hced_match_candidates"]]
    return {
        "schema_version": 1,
        "analysis_scope": "staged discovery and coverage analysis only",
        "input_fingerprints": {
            "brecke_wars_sha256": file_sha256(brecke_path),
            "hced_candidates_sha256": file_sha256(hced_path),
            "hced_funnel_sha256": file_sha256(funnel_path),
            "wikidata_battle_candidates_sha256": file_sha256(wikidata_path),
        },
        "method": {
            "brecke_hced_match": (
                "Exact normalize_label match on Brecke aliases and HCED war_names, "
                "plus interval overlap for closed Brecke intervals; no fuzzy merge."
            ),
            "genuinely_new_definition": (
                "No HCED candidate satisfies normalized event name, Wikidata year "
                "within the HCED interval ±1, and coordinate distance strictly under 25 km."
            ),
            "priority_definition": (
                "Unmatched pre-1500 Wikidata candidates with at least two distinct P710 "
                "participants, ranked by conservative P17 analysis-region membership."
            ),
            "region_definition": (
                "Non-exclusive curated lanes from source-asserted P17 jurisdiction QIDs; "
                "not inferred battlefield geography. Unmapped QIDs stay unmapped."
            ),
        },
        "release_mutation": "none",
        "summary": {
            "wikidata_candidates": len(annotations),
            "hced_contract_matches": len(matched),
            "genuinely_new_under_contract": len(genuinely_new),
            "genuinely_new_without_coordinates": sum(
                not row["has_coordinates"] for row in genuinely_new
            ),
            "genuinely_new_pre_1500": len(pre_1500),
            "actionable_genuinely_new_pre_1500": len(actionable_pre_1500),
            "actionable_definition": "pre-1500 and at least two distinct P710 participants",
        },
        "wikidata_dedup": {
            "candidates": annotations,
            "genuinely_new_by_century": century_rows,
            "genuinely_new_by_region": [
                {
                    "region": region,
                    "all_new_candidates": region_all[region],
                    "all_new_pre_1500": region_pre_1500[region],
                    "actionable_new_pre_1500": region_actionable[region],
                }
                for region in sorted(region_all)
            ],
            "top_unmapped_country_qids": _counter_rows(
                Counter(dict(unmapped_qids.most_common(100))), "qid"
            ),
        },
        "brecke_coverage": brecke,
        "priority_comparison": {
            "material_disagreement": material_disagreement,
            "criterion": (
                "The leading classified discovery lane is absent from the regions represented "
                "by the current funnel top 10 and contains more than twice the cumulative "
                "event yield of the funnel top 20."
            ),
            "leading_discovery_region": leading_region,
            "current_funnel_top_20_cumulative_events": top_twenty_funnel_yield,
            "scouting_expectation_ranks": scouting_expectation_ranks,
            "scouting_expectation_supported": scouting_expectation_supported,
            "current_funnel_ranking": current_funnel[:20],
            "revised_promotion_priority": revised_ranking,
        },
    }


def _markdown_table(headers: list[str], rows: Iterable[Iterable[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return lines


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = report["summary"]
    comparison = report["priority_comparison"]
    brecke = report["brecke_coverage"]
    disagreement = bool(comparison["material_disagreement"])
    status = "MATERIAL DISAGREEMENT" if disagreement else "NO MATERIAL DISAGREEMENT"
    leading = comparison.get("leading_discovery_region") or {}
    lines = [
        "# Dataset gaps after the Wikidata + Brecke expansion",
        "",
        f"**Priority comparison: {status}.** "
        + (
            f"The revised discovery ranking is led by **{leading.get('region')}** "
            f"({leading.get('actionable_new_pre_1500', 0):,} actionable unmatched pre-1500 "
            "candidates), while the current funnel ranks individual identity labels. "
            "The new corpus therefore changes where the next review wave should look first."
            if disagreement
            else "The revised discovery lanes do not cross the declared materiality threshold."
        ),
        "",
        (
            "**The scouting expectation is not supported by the strict actionable ranking.** "
            f"West Asia/North Africa ranks "
            f"{comparison['scouting_expectation_ranks']['West Asia and North Africa']}, "
            f"Japan {comparison['scouting_expectation_ranks']['Japan']}, Indian subcontinent "
            f"{comparison['scouting_expectation_ranks']['Indian subcontinent']}, and China "
            f"{comparison['scouting_expectation_ranks']['China']}; Mediterranean Europe is "
            "the measured leader. This is why the report re-ranks the next review wave."
            if not comparison["scouting_expectation_supported"]
            else "The scouting expectation is supported by the strict actionable ranking."
        ),
        "",
        "This report is staged discovery analysis only. It does not approve an outcome, "
        "create a draw from an unknown result, or add any event to the rating ledger.",
        "",
        "## Headline",
        "",
        f"The expanded queue contains **{summary['wikidata_candidates']:,}** candidates. "
        f"The strict three-factor comparison finds **{summary['hced_contract_matches']:,}** "
        f"HCED matches and **{summary['genuinely_new_under_contract']:,}** unmatched rows. "
        f"Before 1500, **{summary['genuinely_new_pre_1500']:,}** are unmatched and "
        f"**{summary['actionable_genuinely_new_pre_1500']:,}** also carry at least two "
        "distinct P710 participants—the actionable headline expected by the contract.",
        "",
        f"A crucial limitation: **{summary['genuinely_new_without_coordinates']:,}** unmatched "
        "rows lack usable coordinates. They fail the strict match contract but are not proof "
        "that HCED lacks the same historical event; they remain review candidates.",
        "",
        "## Deduplication rule",
        "",
        "A Wikidata row matches HCED only when all three conditions hold: normalized event "
        "name equality, Wikidata year inside the HCED interval plus or minus one year, and "
        "haversine distance strictly below 25 km. `hced_match_candidates` is written only "
        "to `build/dataset-gaps.json`; the content-locked queue is never rewritten.",
        "",
        "## Revised discovery priority",
        "",
        "Region memberships are non-exclusive and derive only from a conservative mapping "
        "of source-asserted P17 QIDs. They are analysis lanes, not battlefield geography.",
        "",
    ]
    lines.extend(
        _markdown_table(
            ["Rank", "Discovery lane", "Actionable new pre-1500", "All new pre-1500", "All new"],
            (
                (
                    index,
                    row["region"],
                    f"{row['actionable_new_pre_1500']:,}",
                    f"{row['all_new_pre_1500']:,}",
                    f"{row['all_new_candidates']:,}",
                )
                for index, row in enumerate(
                    comparison["revised_promotion_priority"], start=1
                )
            ),
        )
    )
    lines.extend(["", "### Current HCED resolver funnel", ""])
    lines.extend(
        _markdown_table(
            ["Rank", "Unresolved label", "Marginal events", "Cumulative events"],
            (
                (
                    row.get("rank"),
                    row.get("label"),
                    row.get("marginal_events"),
                    row.get("cumulative_events"),
                )
                for row in comparison["current_funnel_ranking"]
            ),
        )
    )
    lines.extend(
        [
            "",
            f"Materiality rule: {comparison['criterion']} The current funnel top 20 "
            f"unlocks {comparison['current_funnel_top_20_cumulative_events']:,} events.",
            "",
            "## Genuinely-new candidates by century",
            "",
        ]
    )
    lines.extend(
        _markdown_table(
            ["Century", "Strict-contract unmatched candidates"],
            (
                (row["century"], f"{row['count']:,}")
                for row in report["wikidata_dedup"]["genuinely_new_by_century"]
            ),
        )
    )
    lines.extend(
        [
            "",
            "## Brecke war-name coverage",
            "",
            f"Of **{brecke['summary']['total_wars']:,}** Brecke war records, "
            f"**{brecke['summary']['verified_hced_match']:,}** have at least one exact-name, "
            "time-overlapping HCED battle and "
            f"**{brecke['summary']['zero_matching_hced_battles']:,}** have none. Brecke has "
            "no winner field and no reusable license grant; the sidecar is a war-name "
            "coverage registry only.",
            "",
        ]
    )
    lines.extend(
        _markdown_table(
            ["Brecke region", "Wars with zero matching HCED battles"],
            (
                (region, f"{count:,}")
                for region, count in brecke["summary"]["zero_match_by_region"].items()
            ),
        )
    )
    lines.extend(["", "### Zero-match Brecke wars, enumerated by region", ""])
    for region, wars in brecke["zero_match_wars_by_region"].items():
        lines.extend([f"#### {region}", ""])
        for war in wars:
            start = war.get("start_year")
            end = war.get("end_year")
            if start is None:
                interval = "unknown dates"
            elif end is None:
                interval = f"{start}–open"
            else:
                interval = f"{start}–{end}"
            lines.append(
                f"- `{war.get('brecke_id')}` — {interval}: {war.get('war_name')}"
            )
        lines.append("")
    lines.extend(
        [
            "## Interpretation limits",
            "",
            "- Wikidata P17 is a source-asserted jurisdiction claim, not modern sovereign "
            "truth or guaranteed battlefield geography.",
            "- Region counts are non-exclusive when a candidate has claims in more than one "
            "mapped lane; unmapped QIDs are preserved rather than guessed.",
            "- Missing coordinates make strict deduplication indeterminate, not evidence that "
            "two same-name events are distinct.",
            "- Brecke aliases use exact normalized matching only; plural, spelling, and fuzzy "
            "variants are intentionally not merged.",
            "- Automated extraction never approves rating data. Unknown is not a draw.",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(
    report: Mapping[str, Any], output_json: str | Path, output_markdown: str | Path
) -> None:
    json_path = Path(output_json)
    markdown_path = Path(output_markdown)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Report discovery gaps across Wikidata battles, HCED, and Brecke"
    )
    parser.add_argument(
        "--wikidata",
        default=str(PROJECT_ROOT / "data/review/wikidata-battle-candidates.jsonl"),
    )
    parser.add_argument(
        "--hced", default=str(PROJECT_ROOT / "data/review/hced-candidates.jsonl")
    )
    parser.add_argument(
        "--brecke", default=str(PROJECT_ROOT / "data/reference/brecke-wars.jsonl")
    )
    parser.add_argument(
        "--funnel",
        default=str(PROJECT_ROOT / "build/hced-unresolved-label-funnel.json"),
    )
    parser.add_argument(
        "--output-json", default=str(PROJECT_ROOT / "build/dataset-gaps.json")
    )
    parser.add_argument(
        "--output-markdown", default=str(PROJECT_ROOT / "docs/DATASET_GAPS.md")
    )
    args = parser.parse_args()
    review_sha_before = file_sha256(args.wikidata)
    report = build_report(args.wikidata, args.hced, args.brecke, args.funnel)
    write_report(report, args.output_json, args.output_markdown)
    review_sha_after = file_sha256(args.wikidata)
    if review_sha_after != review_sha_before:
        raise RuntimeError("Gap report mutated the content-locked Wikidata queue")
    print(
        f"wrote gap report: {report['summary']['actionable_genuinely_new_pre_1500']} "
        "actionable genuinely-new pre-1500 candidates"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
