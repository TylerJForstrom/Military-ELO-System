"""Military History Elo: auditable ratings for engagements and wars."""

from .config import ModelConfig
from .engine import EloEngine
from .models import Entity, Event, Participant

__all__ = ["EloEngine", "Entity", "Event", "ModelConfig", "Participant"]
__version__ = "0.1.0"
