from __future__ import annotations

import json
import time
import urllib.parse
from pathlib import Path
from typing import Any

from .http import get_bytes
from .provenance import write_review_candidates, write_snapshot


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


def fetch_wikidata(
    raw_root: str | Path = "data/raw",
    review_path: str | Path = "data/review/wikidata-candidates.jsonl",
    page_size: int = 1000,
    max_pages: int | None = None,
    pause_seconds: float = 1.0,
) -> list[dict[str, Any]]:
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
