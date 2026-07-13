from __future__ import annotations

import time
import urllib.error
import urllib.request


USER_AGENT = "MilitaryHistoryElo/0.1 (research ingestion; contact: local project owner)"


def get_bytes(
    url: str,
    accept: str = "application/json",
    attempts: int = 4,
    headers: dict[str, str] | None = None,
) -> bytes:
    request_headers = {"Accept": accept, "User-Agent": USER_AGENT, **(headers or {})}
    request = urllib.request.Request(url, headers=request_headers)
    delay = 1.0
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError):
            if attempt + 1 == attempts:
                raise
            time.sleep(delay)
            delay *= 2
    raise RuntimeError("unreachable")
