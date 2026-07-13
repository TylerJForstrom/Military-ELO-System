from __future__ import annotations

import argparse
import http.server
import socketserver
from functools import partial
from pathlib import Path


class _NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    # The deployed site revalidates on every request (see netlify.toml); the
    # local server must match so reviews never look at a stale artifact.
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve the local dashboard")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--directory", default="web")
    args = parser.parse_args()
    directory = Path(args.directory).resolve()
    handler = partial(_NoCacheHandler, directory=str(directory))
    with socketserver.TCPServer(("127.0.0.1", args.port), handler) as server:
        print(f"Military History Elo: http://127.0.0.1:{args.port}")
        server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
