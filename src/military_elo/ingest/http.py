from __future__ import annotations

import hashlib
import time
import urllib.error
import urllib.request


USER_AGENT = "MilitaryHistoryElo/0.1 (research ingestion; contact: local project owner)"


class HTTPContentMismatchError(ValueError):
    """Raised when downloaded bytes do not match a caller-pinned artifact."""


def get_bytes(
    url: str,
    accept: str = "application/json",
    attempts: int = 4,
    headers: dict[str, str] | None = None,
    *,
    expected_sha256: str | None = None,
    expected_size: int | None = None,
) -> bytes:
    request_headers = {"Accept": accept, "User-Agent": USER_AGENT, **(headers or {})}
    request = urllib.request.Request(url, headers=request_headers)
    delay = 1.0
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                payload = response.read()
            actual_sha256 = hashlib.sha256(payload).hexdigest()
            if expected_size is not None and len(payload) != expected_size:
                raise HTTPContentMismatchError(
                    f"Downloaded size mismatch for {url}: expected {expected_size}, "
                    f"found {len(payload)}"
                )
            if expected_sha256 is not None and actual_sha256 != expected_sha256:
                raise HTTPContentMismatchError(
                    f"Downloaded SHA-256 mismatch for {url}: expected {expected_sha256}, "
                    f"found {actual_sha256}"
                )
            return payload
        except (urllib.error.URLError, TimeoutError):
            if attempt + 1 == attempts:
                raise
            time.sleep(delay)
            delay *= 2
    raise RuntimeError("unreachable")
