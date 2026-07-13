from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .http import get_bytes
from .provenance import write_review_candidates, write_snapshot


BASE_URL = "https://ucdpapi.pcr.uu.se/api"


def fetch_ucdp(
    resource: str = "dyadic",
    version: str = "26.1",
    raw_root: str | Path = "data/raw",
    review_path: str | Path = "data/review/ucdp-candidates.jsonl",
    page_size: int = 1000,
    max_pages: int | None = None,
    pause_seconds: float = 0.5,
    api_token: str | None = None,
) -> list[dict[str, Any]]:
    if not api_token:
        raise ValueError(
            "UCDP API access requires a token. Request one from the maintainer listed at "
            "https://ucdp.uu.se/apidocs/ or use the open versioned CSV downloads."
        )
    page = 1
    records: list[dict[str, Any]] = []
    while max_pages is None or page <= max_pages:
        url = f"{BASE_URL}/{resource}/{version}?pagesize={page_size}&page={page}"
        payload = get_bytes(url, headers={"x-ucdp-access-token": api_token})
        document = json.loads(payload)
        page_records = document.get("Result") or document.get("result") or []
        if not isinstance(page_records, list):
            raise ValueError(f"Unexpected UCDP API response for {url}")
        write_snapshot(
            payload,
            raw_root,
            source_id=f"ucdp-{resource}",
            source_url=url,
            license_name="CC-BY-4.0",
            extension="json",
            record_count=len(page_records),
            source_version=version,
            notes="UCDP records are staged for actor/entity and outcome adjudication",
        )
        records.extend(page_records)
        total_pages = int(document.get("TotalPages") or document.get("totalPages") or page)
        if page >= total_pages or not page_records:
            break
        page += 1
        time.sleep(max(0.0, pause_seconds))

    candidates = [
        {
            "candidate_id": f"ucdp-{resource}-{record.get('conflict_id', record.get('dyad_id', index))}-{record.get('year', '')}",
            "source": f"ucdp-{resource}-{version}",
            "review_status": "needs_review",
            "do_not_rate_automatically": True,
            "raw": record,
            "extraction_notes": [
                "Map UCDP actors to versioned historical entities.",
                "UCDP intensity/deaths are not themselves victory or defeat labels.",
                "Combine termination/outcome sources before producing a strategic result.",
            ],
        }
        for index, record in enumerate(records)
    ]
    write_review_candidates(candidates, review_path)
    return candidates
