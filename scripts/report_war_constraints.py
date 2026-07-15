from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from military_elo.war_constraints import (  # noqa: E402
    build_current_war_constraint_report,
    render_war_constraint_json,
    render_war_constraint_markdown,
    write_war_constraint_report,
)


def _allowed_output_directory(path: Path) -> bool:
    resolved = path.resolve()
    if any(part.casefold() == "build" for part in resolved.parts):
        return True
    try:
        resolved.relative_to(Path(tempfile.gettempdir()).resolve())
        return True
    except ValueError:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build a deterministic, read-only report of unresolved HCED labels "
            "linked by normalized war names. Suggestions never modify the release."
        )
    )
    parser.add_argument(
        "--review",
        default=str(ROOT / "data" / "review"),
        help="Review directory containing HCED and Cliopatria candidate JSONL files.",
    )
    parser.add_argument(
        "--seed",
        default=str(ROOT / "data" / "seed"),
        help="Curated seed directory containing entities.json and events.json.",
    )
    parser.add_argument(
        "--release",
        default=str(ROOT / "data" / "release"),
        help="Release directory used only to measure existing event redundancy.",
    )
    parser.add_argument(
        "--results",
        default=str(ROOT / "web" / "data" / "results.json"),
        help="Dashboard results JSON used only for opponent-network components.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown", "both"),
        default="markdown",
        help="Stdout format when --output-dir is omitted.",
    )
    parser.add_argument(
        "--output-dir",
        help="Write paired JSON and Markdown artifacts inside build/ or a temporary directory.",
    )
    parser.add_argument("--basename", default="war-constraints")
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of ranked wars included in Markdown (JSON always contains all wars).",
    )
    args = parser.parse_args(argv)

    try:
        report = build_current_war_constraint_report(
            args.review,
            args.seed,
            args.release,
            results_path=args.results,
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    if args.output_dir:
        output_dir = Path(args.output_dir)
        if not _allowed_output_directory(output_dir):
            parser.error("--output-dir must be inside build/ or the system temporary directory")
        json_path, markdown_path = write_war_constraint_report(
            report,
            output_dir,
            basename=args.basename,
            top=max(0, args.top),
        )
        print(f"Wrote {json_path} and {markdown_path}")
        return 0

    json_text = render_war_constraint_json(report)
    markdown = render_war_constraint_markdown(report, top=max(0, args.top))
    if args.format == "json":
        sys.stdout.write(json_text)
    elif args.format == "markdown":
        sys.stdout.write(markdown)
    else:
        sys.stdout.write(markdown)
        if not markdown.endswith("\n"):
            sys.stdout.write("\n")
        sys.stdout.write("\n---\n\n## Deterministic JSON\n\n```json\n")
        sys.stdout.write(json_text)
        sys.stdout.write("```\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
