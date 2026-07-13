from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from .audit import audit_dataset, has_errors
from .config import ModelConfig
from .engine import EloEngine
from .models import Entity, Event, Source
from .sensitivity import run_sensitivity


def load_records(data_dir: str | Path) -> tuple[list[Entity], list[Event], dict[str, Source], dict[str, Any]]:
    root = Path(data_dir)
    entity_raw = json.loads((root / "entities.json").read_text(encoding="utf-8"))
    event_raw = json.loads((root / "events.json").read_text(encoding="utf-8"))
    source_raw = json.loads((root / "sources.json").read_text(encoding="utf-8"))
    metadata_path = root / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    entities = [Entity.from_dict(item) for item in entity_raw]
    events = [Event.from_dict(item) for item in event_raw]
    sources = {item.id: item for item in (Source.from_dict(row) for row in source_raw)}
    return entities, events, sources, metadata


def build_results(
    data_dir: str | Path,
    output_path: str | Path,
    config_path: str | Path | None = None,
    audit_path: str | Path | None = None,
    simulations: int = 0,
) -> dict[str, object]:
    entities, events, sources, metadata = load_records(data_dir)
    config = ModelConfig.from_file(config_path) if config_path else ModelConfig()
    issues = audit_dataset(entities, events, sources, config)
    if audit_path:
        destination = Path(audit_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps([issue.as_dict() for issue in issues], indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if has_errors(issues):
        messages = "\n".join(f"{issue.code}: {issue.record_id}: {issue.message}" for issue in issues if issue.severity == "error")
        raise ValueError(f"Dataset audit failed:\n{messages}")

    engine = EloEngine(config).run(entities, events)
    metadata = {
        **metadata,
        "generated": date.today().isoformat(),
        "model_version": "0.1.0",
        "baseline": config.baseline,
        "rated_events": len(engine.event_updates),
        "entities": len(entities),
        "audit_warnings": sum(issue.severity == "warning" for issue in issues),
        "simulations": simulations,
        "coverage": {
            "event_types": dict(Counter(event.event_type for event in events if event.status == "complete")),
            "war_types": dict(Counter(event.war_type for event in events if event.status == "complete")),
            "domains": dict(Counter(event.domain for event in events if event.status == "complete")),
            "confidence": {
                "high_0.80_to_1.00": sum(event.confidence >= 0.80 for event in events if event.status == "complete"),
                "medium_0.55_to_0.79": sum(0.55 <= event.confidence < 0.80 for event in events if event.status == "complete"),
                "low_below_0.55": sum(event.confidence < 0.55 for event in events if event.status == "complete"),
            },
            "by_century": dict(
                sorted(
                    Counter(
                        (event.end_year // 100) * 100
                        for event in events
                        if event.status == "complete"
                    ).items()
                )
            ),
        },
    }
    results = engine.export(sources, metadata)
    sensitivity = run_sensitivity(entities, events, config, simulations=simulations)
    if sensitivity:
        results["sensitivity"] = sensitivity
        for row in results["leaderboard"]:  # type: ignore[index]
            row["sensitivity"] = sensitivity.get(row["entity_id"], {})
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return results
