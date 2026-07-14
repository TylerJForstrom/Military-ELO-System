from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from military_elo.review import build_gold_set_document, load_json_records


DEFAULT_STRATA = ("era", "region", "layer", "domain", "source_family")


def _safe_output_path(path: str | Path, input_paths: list[str | Path]) -> Path:
    destination = Path(path).resolve()
    if destination.suffix.lower() != ".json":
        raise ValueError("Gold-set documents must use a .json output path")
    if destination in {Path(item).resolve() for item in input_paths}:
        raise ValueError("Output path must not overwrite an input document")
    repository = ROOT.resolve()
    build_root = (ROOT / "build").resolve()
    try:
        destination.relative_to(repository)
    except ValueError:
        pass
    else:
        try:
            destination.relative_to(build_root)
        except ValueError as error:
            raise ValueError("In-repository review output is allowed only under build/") from error
    return destination


def _write_json(destination: Path, document: dict) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(
        document,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
        allow_nan=False,
    ) + "\n"
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(serialized)
            temporary_name = temporary.name
        os.replace(temporary_name, destination)
    finally:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)


def _source_family_mappings(
    specifications: list[str],
    inputs: list[str],
) -> dict[Path, str]:
    input_paths = {Path(item).resolve() for item in inputs}
    mappings: dict[Path, str] = {}
    for specification in specifications:
        if "=" not in specification:
            raise ValueError("--source-family must use INPUT=FAMILY")
        path_text, family = specification.rsplit("=", 1)
        path = Path(path_text).resolve()
        family = family.strip()
        if path not in input_paths:
            raise ValueError(f"Source-family mapping does not name an input: {path_text}")
        if not family:
            raise ValueError("Source-family mapping requires a non-blank family")
        if path in mappings:
            raise ValueError(f"Duplicate source-family mapping for {path_text}")
        mappings[path] = family
    return mappings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a seeded, stratified gold-set sample from JSON or JSONL records"
    )
    parser.add_argument("inputs", nargs="+", help="Input JSON arrays/documents or JSONL files")
    parser.add_argument("--output", default=str(ROOT / "build" / "gold-set.json"))
    parser.add_argument("--size", type=int, required=True, help="Number of records to sample")
    parser.add_argument("--seed", type=int, default=1900)
    parser.add_argument(
        "--stratify",
        nargs="+",
        default=list(DEFAULT_STRATA),
        metavar="FIELD",
        help="Categorical fields used as the joint stratum",
    )
    parser.add_argument(
        "--id-field",
        default=None,
        help="Explicit stable record-id field (defaults to common project id fields)",
    )
    parser.add_argument(
        "--source-family",
        action="append",
        default=[],
        metavar="INPUT=FAMILY",
        help="Explicitly assign a source family to records from one input",
    )
    args = parser.parse_args(argv)

    source_families = _source_family_mappings(args.source_family, args.inputs)
    records = []
    for input_path in args.inputs:
        family = source_families.get(Path(input_path).resolve())
        for loaded in load_json_records(input_path):
            record = dict(loaded)
            if family is not None:
                declared = record.get("source_family")
                if declared not in (None, "") and declared != family:
                    raise ValueError(
                        f"Record source_family {declared!r} conflicts with mapping {family!r}"
                    )
                record["source_family"] = family
            records.append(record)
    document = build_gold_set_document(
        records,
        args.size,
        seed=args.seed,
        stratify_by=args.stratify,
        id_field=args.id_field,
    )
    destination = _safe_output_path(args.output, args.inputs)
    _write_json(destination, document)
    print(
        f"Sampled {document['sample_size']} of {document['population_size']} records "
        f"with seed {document['seed']}; wrote {destination}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
