from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_STRATEGIC_WEIGHTS: dict[str, dict[str, float]] = {
    "interstate_limited": {
        "battlefield_outcome": 0.15,
        "political_objectives": 0.30,
        "territorial_outcome": 0.20,
        "sovereignty_survival": 0.10,
        "settlement_durability": 0.15,
        "force_preservation": 0.10,
    },
    "conquest": {
        "battlefield_outcome": 0.15,
        "political_objectives": 0.15,
        "territorial_outcome": 0.25,
        "sovereignty_survival": 0.30,
        "settlement_durability": 0.10,
        "force_preservation": 0.05,
    },
    "colonial_anti_colonial": {
        "battlefield_outcome": 0.10,
        "political_objectives": 0.35,
        "territorial_outcome": 0.15,
        "sovereignty_survival": 0.20,
        "settlement_durability": 0.15,
        "force_preservation": 0.05,
    },
    "insurgency_intervention": {
        "battlefield_outcome": 0.08,
        "political_objectives": 0.40,
        "territorial_outcome": 0.12,
        "sovereignty_survival": 0.20,
        "settlement_durability": 0.15,
        "force_preservation": 0.05,
    },
    "civil_war": {
        "battlefield_outcome": 0.12,
        "political_objectives": 0.30,
        "territorial_outcome": 0.15,
        "sovereignty_survival": 0.25,
        "settlement_durability": 0.12,
        "force_preservation": 0.06,
    },
    "world_war": {
        "battlefield_outcome": 0.18,
        "political_objectives": 0.20,
        "territorial_outcome": 0.17,
        "sovereignty_survival": 0.25,
        "settlement_durability": 0.10,
        "force_preservation": 0.10,
    },
    "punitive_expedition": {
        "battlefield_outcome": 0.25,
        "political_objectives": 0.30,
        "territorial_outcome": 0.10,
        "sovereignty_survival": 0.10,
        "settlement_durability": 0.10,
        "force_preservation": 0.15,
    },
    "peace_enforcement": {
        "battlefield_outcome": 0.08,
        "political_objectives": 0.32,
        "territorial_outcome": 0.05,
        "sovereignty_survival": 0.15,
        "settlement_durability": 0.30,
        "force_preservation": 0.10,
    },
}

DEFAULT_TACTICAL_WEIGHTS = {
    "battlefield_control": 0.45,
    "mission_objective": 0.25,
    "force_preservation": 0.20,
    "positional_gain": 0.10,
}

DEFAULT_OPERATIONAL_WEIGHTS = {
    "campaign_objective": 0.35,
    "theater_control": 0.25,
    "force_preservation": 0.15,
    "tempo_initiative": 0.15,
    "logistics_sustainment": 0.10,
}


@dataclass
class ModelConfig:
    baseline: float = 1500.0
    elo_scale: float = 400.0
    tactical_k: float = 28.0
    operational_k: float = 34.0
    strategic_k: float = 42.0
    min_k: float = 4.0
    max_k: float = 96.0
    min_uncertainty: float = 60.0
    max_uncertainty: float = 350.0
    uncertainty_drift_per_year: float = 2.5
    uncertainty_information_gain: float = 0.16
    home_advantage_points: float = 35.0
    force_advantage_points_per_doubling: float = 45.0
    max_context_adjustment: float = 180.0
    tactical_composite_weight: float = 0.20
    operational_composite_weight: float = 0.25
    strategic_composite_weight: float = 0.55
    tactical_full_evidence: int = 5
    operational_full_evidence: int = 4
    strategic_full_evidence: int = 3
    scale_multipliers: dict[str, float] = field(
        default_factory=lambda: {
            "skirmish": 0.45,
            "battle": 0.80,
            "campaign": 1.05,
            "theater": 1.25,
            "major_war": 1.40,
            "total_war": 1.65,
        }
    )
    stakes_multipliers: dict[str, float] = field(
        default_factory=lambda: {
            "low": 0.65,
            "limited": 0.90,
            "major": 1.20,
            "existential": 1.55,
        }
    )
    role_multipliers: dict[str, float] = field(
        default_factory=lambda: {
            "primary": 1.0,
            "coalition_lead": 1.0,
            "major_ally": 0.78,
            "supporting_ally": 0.48,
            "expeditionary": 0.38,
            "proxy_sponsor": 0.25,
        }
    )
    tactical_weights: dict[str, float] = field(
        default_factory=lambda: dict(DEFAULT_TACTICAL_WEIGHTS)
    )
    operational_weights: dict[str, float] = field(
        default_factory=lambda: dict(DEFAULT_OPERATIONAL_WEIGHTS)
    )
    strategic_weights: dict[str, dict[str, float]] = field(
        default_factory=lambda: {k: dict(v) for k, v in DEFAULT_STRATEGIC_WEIGHTS.items()}
    )

    @classmethod
    def from_file(cls, path: str | Path) -> "ModelConfig":
        raw: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
        config = cls()
        for key, value in raw.items():
            if not hasattr(config, key):
                raise ValueError(f"Unknown model configuration key: {key}")
            setattr(config, key, value)
        config.validate()
        return config

    def validate(self) -> None:
        if self.baseline <= 0 or self.elo_scale <= 0:
            raise ValueError("baseline and elo_scale must be positive")
        if not 0 < self.tactical_composite_weight <= 1:
            raise ValueError("tactical_composite_weight must be in (0, 1]")
        if not 0 < self.operational_composite_weight <= 1:
            raise ValueError("operational_composite_weight must be in (0, 1]")
        if not 0 < self.strategic_composite_weight <= 1:
            raise ValueError("strategic_composite_weight must be in (0, 1]")
        total_composite = (
            self.tactical_composite_weight
            + self.operational_composite_weight
            + self.strategic_composite_weight
        )
        if abs(total_composite - 1.0) > 1e-6:
            raise ValueError(f"composite weights must sum to 1.0, got {total_composite}")
        for label, weights in [
            ("tactical", self.tactical_weights),
            ("operational", self.operational_weights),
            *self.strategic_weights.items(),
        ]:
            total = sum(weights.values())
            if abs(total - 1.0) > 1e-6:
                raise ValueError(f"{label} outcome weights must sum to 1.0, got {total}")
