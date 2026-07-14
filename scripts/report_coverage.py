from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from military_elo.coverage import (  # noqa: E402
    CoverageInputError,
    build_coverage_report,
    render_coverage_json,
    render_coverage_markdown,
    write_coverage_report,
)


def _optional_input(path: str | None, default: Path) -> Path | None:
    """Resolve an optional input without hiding an explicitly missing path."""

    if path is not None:
        return Path(path)
    return default if default.exists() else None


def _allowed_output_directory(path: Path) -> bool:
    resolved = path.resolve()
    if any(part.casefold() == "build" for part in resolved.parts):
        return True
    temporary_root = Path(tempfile.gettempdir()).resolve()
    try:
        resolved.relative_to(temporary_root)
        return True
    except ValueError:
        return False


def _print_both(markdown: str, json_text: str) -> None:
    sys.stdout.write(markdown)
    if not markdown.endswith("\n"):
        sys.stdout.write("\n")
    sys.stdout.write("\n---\n\n## Deterministic JSON\n\n```json\n")
    sys.stdout.write(json_text)
    sys.stdout.write("```\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Report observed Military History Elo coverage without treating it as "
            "true historical completeness."
        )
    )
    parser.add_argument(
        "--data",
        "--release",
        dest="data",
        default=str(ROOT / "data" / "release"),
        help="Release directory containing events, entities, sources, and metadata JSON.",
    )
    parser.add_argument(
        "--review",
        help=(
            "Optional directory of machine-local review JSONL queues; when omitted, "
            "the repository data/review directory is used if present."
        ),
    )
    parser.add_argument(
        "--registry",
        help=(
            "Optional registry JSON path; when omitted, the repository registry is "
            "used if present."
        ),
    )
    parser.add_argument(
        "--results",
        help=(
            "Optional results JSON path for opponent-network coverage; when omitted, "
            "the repository results file is used if present."
        ),
    )
    parser.add_argument(
        "--as-of",
        help="Deterministic queue-aging reference date (YYYY-MM-DD); defaults to release metadata as_of.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown", "both"),
        default="both",
        help="Stdout format when --output-dir is omitted.",
    )
    parser.add_argument(
        "--output-dir",
        "--output",
        dest="output_dir",
        help="Explicit build/ or temporary directory for paired coverage.json and coverage.md files.",
    )
    parser.add_argument(
        "--basename",
        default="coverage",
        help="Base filename used with --output-dir (default: coverage).",
    )
    args = parser.parse_args(argv)

    review = _optional_input(args.review, ROOT / "data" / "review")
    registry = _optional_input(
        args.registry, ROOT / "data" / "catalog" / "registry.json"
    )
    results = _optional_input(args.results, ROOT / "web" / "data" / "results.json")
    try:
        report = build_coverage_report(
            args.data,
            review_dir=review,
            registry_path=registry,
            results_path=results,
            as_of=args.as_of,
        )
    except (CoverageInputError, OSError) as exc:
        parser.error(str(exc))

    if args.output_dir:
        output_dir = Path(args.output_dir)
        if not _allowed_output_directory(output_dir):
            parser.error("--output-dir must be inside build/ or the system temporary directory")
        try:
            json_path, markdown_path = write_coverage_report(
                report, output_dir, basename=args.basename
            )
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        print(f"Wrote {json_path} and {markdown_path}")
        return 0

    json_text = render_coverage_json(report)
    markdown = render_coverage_markdown(report)
    if args.format == "json":
        sys.stdout.write(json_text)
    elif args.format == "markdown":
        sys.stdout.write(markdown)
    else:
        _print_both(markdown, json_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
