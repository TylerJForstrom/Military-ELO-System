"""Source-specific acquisition into an immutable, review-first staging area."""

from .provenance import RawSnapshot, write_snapshot

__all__ = ["RawSnapshot", "write_snapshot"]
