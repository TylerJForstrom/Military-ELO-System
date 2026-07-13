from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RawSnapshot:
    source_id: str
    source_url: str
    retrieved_at: str
    license: str
    sha256: str
    path: str
    record_count: int | None = None
    source_version: str = ""
    notes: str = ""


def utc_stamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_snapshot(
    payload: bytes,
    raw_root: str | Path,
    source_id: str,
    source_url: str,
    license_name: str,
    extension: str,
    record_count: int | None = None,
    source_version: str = "",
    notes: str = "",
) -> RawSnapshot:
    root = Path(raw_root)
    source_dir = root / source_id
    source_dir.mkdir(parents=True, exist_ok=True)
    retrieved_at = utc_stamp()
    digest = hashlib.sha256(payload).hexdigest()
    safe_time = retrieved_at.replace(":", "").replace("-", "")
    path = source_dir / f"{safe_time}-{digest[:12]}.{extension.lstrip('.')}"
    path.write_bytes(payload)
    snapshot = RawSnapshot(
        source_id=source_id,
        source_url=source_url,
        retrieved_at=retrieved_at,
        license=license_name,
        sha256=digest,
        path=path.as_posix(),
        record_count=record_count,
        source_version=source_version,
        notes=notes,
    )
    manifest_path = root / "manifest.jsonl"
    with manifest_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(asdict(snapshot), ensure_ascii=False, sort_keys=True) + "\n")
    return snapshot


def write_review_candidates(records: list[dict[str, Any]], destination: str | Path) -> None:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
