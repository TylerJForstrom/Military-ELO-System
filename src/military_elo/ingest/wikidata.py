from __future__ import annotations

import json
import time
import urllib.parse
from pathlib import Path
from typing import Any

from .http import get_bytes
from .provenance import validate_review_destination, write_review_candidates, write_snapshot


ENDPOINT = "https://query.wikidata.org/sparql"

QUERY_TEMPLATE = """
SELECT ?event ?eventLabel ?kind ?date ?endDate ?participant ?participantLabel
       ?winner ?winnerLabel ?partOf ?partOfLabel ?location ?locationLabel WHERE {
  VALUES ?class { wd:Q178561 wd:Q645883 wd:Q198 }
  ?event wdt:P31 ?class .
  BIND(IF(?class = wd:Q178561, "engagement",
       IF(?class = wd:Q645883, "campaign", "war")) AS ?kind)
  OPTIONAL { ?event wdt:P585 ?pointInTime . }
  OPTIONAL { ?event wdt:P580 ?startTime . }
  BIND(COALESCE(?pointInTime, ?startTime) AS ?date)
  FILTER(BOUND(?date))
  OPTIONAL { ?event wdt:P582 ?endDate . }
  OPTIONAL { ?event wdt:P710 ?participant . }
  OPTIONAL { ?event wdt:P1346 ?winner . }
  OPTIONAL { ?event wdt:P361 ?partOf . }
  OPTIONAL { ?event wdt:P276 ?location . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT {limit}
OFFSET {offset}
"""


def _value(row: dict[str, Any], key: str) -> str | None:
    item = row.get(key)
    return str(item.get("value")) if isinstance(item, dict) and item.get("value") is not None else None


# Era-bucketed hydration query for the broadened battle-tree pull. One row per
# event (GROUP_CONCAT collapses the multi-valued properties), full P279*
# subclass closure, and coordinate/country capture the bounded discovery query
# lacked. Wikidata encodes winners for only a few dozen battles in the whole
# graph, so the winners column is retained as evidence of that scarcity, not
# as an outcome source; every candidate stays needs_review and
# do_not_rate_automatically.
BATTLE_QUERY_TEMPLATE = """
SELECT ?event
       (SAMPLE(?eventLabelR) AS ?eventLabel)
       (SAMPLE(?d) AS ?date)
       (SAMPLE(?ed) AS ?endDate)
       (SAMPLE(?co) AS ?coord)
       (GROUP_CONCAT(DISTINCT ?kQid; separator="|") AS ?classes)
       (GROUP_CONCAT(DISTINCT ?pPair; separator="|") AS ?participants)
       (GROUP_CONCAT(DISTINCT ?wPair; separator="|") AS ?winners)
       (GROUP_CONCAT(DISTINCT ?oPair; separator="|") AS ?partOf)
       (GROUP_CONCAT(DISTINCT ?ctryQid; separator="|") AS ?countries)
WHERE {
  ?event wdt:P31 ?class .
  ?class wdt:P279* {root} .
  {extra}
  BIND(STRAFTER(STR(?class), "/entity/") AS ?kQid)
  { ?event wdt:P585 ?d } UNION { ?event wdt:P580 ?d }
  FILTER(YEAR(?d) >= {low} && YEAR(?d) < {high})
  OPTIONAL { ?event wdt:P582 ?ed }
  OPTIONAL { ?event wdt:P625 ?co }
  OPTIONAL { ?event rdfs:label ?eventLabelR . FILTER(LANG(?eventLabelR) = "en") }
  OPTIONAL { ?event wdt:P17 ?ctry . BIND(STRAFTER(STR(?ctry), "/entity/") AS ?ctryQid) }
  OPTIONAL {
    ?event wdt:P710 ?p .
    OPTIONAL { ?p rdfs:label ?pLabel . FILTER(LANG(?pLabel) = "en") }
    BIND(CONCAT(STRAFTER(STR(?p), "/entity/"), "~", COALESCE(?pLabel, "")) AS ?pPair)
  }
  OPTIONAL {
    { ?event wdt:P1346 ?w }
    UNION
    { ?event p:P710 ?ws . ?ws ps:P710 ?w ; pq:P3831 wd:Q18560095 . }
    OPTIONAL { ?w rdfs:label ?wLabel . FILTER(LANG(?wLabel) = "en") }
    BIND(CONCAT(STRAFTER(STR(?w), "/entity/"), "~", COALESCE(?wLabel, "")) AS ?wPair)
  }
  OPTIONAL {
    ?event wdt:P361 ?o .
    OPTIONAL { ?o rdfs:label ?oLabel . FILTER(LANG(?oLabel) = "en") }
    BIND(CONCAT(STRAFTER(STR(?o), "/entity/"), "~", COALESCE(?oLabel, "")) AS ?oPair)
  }
}
GROUP BY ?event
"""

# Bucket boundaries sized from the measured per-century event histogram so no
# request exceeds roughly 2,500 rows or the endpoint's 60-second budget.
BATTLE_ERA_BUCKETS: tuple[tuple[int, int], ...] = (
    (-4000, 500),
    (500, 1000),
    (1000, 1300),
    (1300, 1500),
    (1500, 1600),
    (1600, 1700),
    (1700, 1800),
    (1800, 1850),
    (1850, 1900),
    (1900, 1920),
    (1920, 1946),
    (1946, 2027),
)

# The battle series walks the Q178561 subclass tree; the siege series adds
# Q188055-tree items while excluding anything already in the battle tree.
BATTLE_SERIES: tuple[tuple[str, str, str], ...] = (
    ("battle", "wd:Q178561", ""),
    ("siege", "wd:Q188055", "MINUS { ?event wdt:P31/wdt:P279* wd:Q178561 . }"),
)


def fetch_wikidata_battles(
    raw_root: str | Path = "build/acquisition/wikidata-battles/raw",
    review_path: str | Path = "build/acquisition/wikidata-battles/wikidata-battles-live.jsonl",
    pause_seconds: float = 2.0,
) -> list[dict[str, Any]]:
    """Fetch the era-bucketed battle and siege trees as immutable snapshots."""

    validate_review_destination(review_path)
    all_rows: list[dict[str, Any]] = []
    for series_name, root, extra in BATTLE_SERIES:
        for low, high in BATTLE_ERA_BUCKETS:
            query = (
                BATTLE_QUERY_TEMPLATE.replace("{root}", root)
                .replace("{extra}", extra)
                .replace("{low}", str(low))
                .replace("{high}", str(high))
            )
            url = ENDPOINT + "?" + urllib.parse.urlencode(
                {"query": query, "format": "json"}
            )
            payload = get_bytes(url)
            document = json.loads(payload)
            rows = document.get("results", {}).get("bindings", [])
            write_snapshot(
                payload,
                raw_root,
                source_id="wikidata-battles",
                source_url=url,
                license_name="CC0-1.0",
                extension="json",
                record_count=len(rows),
                notes=(
                    f"SPARQL {series_name} tree bucket [{low}, {high}); grouped one "
                    "row per event; automated extraction is not approved rating data"
                ),
            )
            all_rows.extend(rows)
            time.sleep(max(0.0, pause_seconds))

    candidates = parse_wikidata_battle_rows(all_rows)
    write_review_candidates(candidates, review_path)
    return candidates


def _split_pairs(raw: str | None) -> list[dict[str, str]]:
    pairs = []
    for chunk in (raw or "").split("|"):
        chunk = chunk.strip()
        if not chunk:
            continue
        qid, _, label = chunk.partition("~")
        if qid:
            pairs.append({"uri": f"http://www.wikidata.org/entity/{qid}", "label": label or qid})
    return pairs


def _parse_point(raw: str | None) -> tuple[str | None, str | None]:
    if not raw or not raw.startswith("Point("):
        return None, None
    body = raw[len("Point(") : raw.rfind(")")]
    parts = body.split()
    if len(parts) != 2:
        return None, None
    longitude, latitude = parts
    return latitude, longitude


def parse_wikidata_battle_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse grouped SPARQL rows to review candidates, first bucket wins."""

    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        event_uri = _value(row, "event")
        if not event_uri or event_uri in grouped:
            continue
        classes = [c for c in (_value(row, "classes") or "").split("|") if c]
        if "Q188055" in classes and "Q178561" not in classes:
            kind = "siege"
        elif classes == ["Q1261499"]:
            kind = "naval_engagement"
        else:
            kind = "engagement"
        latitude, longitude = _parse_point(_value(row, "coord"))
        grouped[event_uri] = {
            "candidate_id": event_uri.rsplit("/", 1)[-1],
            "source": "wikidata-battles",
            "source_url": event_uri,
            "review_status": "needs_review",
            "do_not_rate_automatically": True,
            "name": _value(row, "eventLabel"),
            "kind": kind,
            "classes": classes,
            "date": _value(row, "date"),
            "end_date": _value(row, "endDate"),
            "latitude": latitude,
            "longitude": longitude,
            "countries": [c for c in (_value(row, "countries") or "").split("|") if c],
            "participants": _split_pairs(_value(row, "participants")),
            "winners": _split_pairs(_value(row, "winners")),
            "part_of": _split_pairs(_value(row, "partOf")),
            "extraction_notes": [
                "Participants mix polities, commanders, and units; outcome is "
                "absent from the source (Wikidata encodes winners for only a "
                "few dozen battles); opposing sides, outcomes, severity, and "
                "entity continuity all require review before any rating."
            ],
        }
    return list(grouped.values())


def fetch_wikidata(
    raw_root: str | Path = "build/acquisition/wikidata/raw",
    review_path: str | Path = "build/acquisition/wikidata/wikidata-live.jsonl",
    page_size: int = 1000,
    max_pages: int | None = None,
    pause_seconds: float = 1.0,
) -> list[dict[str, Any]]:
    # The live endpoint is acquisition-only. Refuse a locked queue basename
    # before the first request so a failed refresh has no raw/review side effects.
    validate_review_destination(review_path)
    all_rows: list[dict[str, Any]] = []
    page = 0
    while max_pages is None or page < max_pages:
        query = QUERY_TEMPLATE.replace("{limit}", str(page_size)).replace(
            "{offset}", str(page * page_size)
        )
        url = ENDPOINT + "?" + urllib.parse.urlencode({"query": query, "format": "json"})
        payload = get_bytes(url)
        document = json.loads(payload)
        rows = document.get("results", {}).get("bindings", [])
        write_snapshot(
            payload,
            raw_root,
            source_id="wikidata",
            source_url=url,
            license_name="CC0-1.0",
            extension="json",
            record_count=len(rows),
            notes=f"SPARQL page {page + 1}; automated extraction is not approved rating data",
        )
        all_rows.extend(rows)
        page += 1
        if len(rows) < page_size:
            break
        time.sleep(max(0.0, pause_seconds))

    grouped: dict[str, dict[str, Any]] = {}
    for row in all_rows:
        event_uri = _value(row, "event")
        if not event_uri:
            continue
        candidate = grouped.setdefault(
            event_uri,
            {
                "candidate_id": event_uri.rsplit("/", 1)[-1],
                "source": "wikidata",
                "source_url": event_uri,
                "review_status": "needs_review",
                "do_not_rate_automatically": True,
                "name": _value(row, "eventLabel"),
                "kind": _value(row, "kind"),
                "date": _value(row, "date"),
                "end_date": _value(row, "endDate"),
                "participants": {},
                "winners": {},
                "part_of": {},
                "locations": {},
                "extraction_notes": [
                    "Identity aliases, opposing sides, objectives, outcome severity and entity continuity require review."
                ],
            },
        )
        for field, label_field, output_key in (
            ("participant", "participantLabel", "participants"),
            ("winner", "winnerLabel", "winners"),
            ("partOf", "partOfLabel", "part_of"),
            ("location", "locationLabel", "locations"),
        ):
            uri = _value(row, field)
            if uri:
                candidate[output_key][uri] = _value(row, label_field) or uri.rsplit("/", 1)[-1]
    candidates = []
    for candidate in grouped.values():
        for key in ("participants", "winners", "part_of", "locations"):
            candidate[key] = [{"uri": uri, "label": label} for uri, label in candidate[key].items()]
        candidates.append(candidate)
    write_review_candidates(candidates, review_path)
    return candidates
