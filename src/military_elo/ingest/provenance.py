from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import unicodedata
import urllib.parse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


CORPUS_LOCK_SCHEMA_VERSION = 1
CORPUS_TRANSFORMATION_VERSION = "open-data-review-v1"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CORPUS_LOCK = PROJECT_ROOT / "data/corpus.lock.json"
LICENSE_CLASSIFICATIONS = frozenset(
    {"open_core", "separate_secondary", "permission_gated"}
)
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
_CREDENTIAL_QUERY_TERMS = (
    "api_key",
    "apikey",
    "access_token",
    "auth_token",
    "credential",
    "password",
    "secret",
    "signature",
)
_CREDENTIAL_QUERY_KEYS = frozenset(
    {"auth", "authorization", "bearer", "jwt", "key", "sas", "sig", "signature", "token"}
)


class CorpusLockError(ValueError):
    """Raised when a corpus lock or a locked artifact fails closed."""


@dataclass(frozen=True)
class RawSnapshot:
    source_id: str
    source_url: str
    retrieved_at: str
    license: str
    sha256: str
    path: str
    record_count: int | None = None
    source_version: str = ""
    notes: str = ""


@dataclass(frozen=True)
class LockedFile:
    filename: str
    sha256: str
    size_bytes: int


@dataclass(frozen=True)
class LockedDataset:
    id: str
    title: str
    source_url: str
    dataset_version: str
    license_id: str
    license_classification: str
    retrieved_at: str
    retrieval_method: str
    files: tuple[LockedFile, ...]


@dataclass(frozen=True)
class LockedInput:
    dataset_id: str
    filename: str


@dataclass(frozen=True)
class LockedOutput:
    kind: str
    filename: str
    sha256: str
    size_bytes: int
    record_count: int


@dataclass(frozen=True)
class LockedTransformation:
    id: str
    transformer: str
    version: str
    inputs: Mapping[str, LockedInput]
    output: LockedOutput


@dataclass(frozen=True)
class CorpusLock:
    schema_version: int
    corpus_id: str
    created_at: str
    transformation_version: str
    datasets: Mapping[str, LockedDataset]
    transformations: Mapping[str, LockedTransformation]

    def dataset(self, dataset_id: str) -> LockedDataset:
        try:
            return self.datasets[dataset_id]
        except KeyError as exc:
            raise CorpusLockError(f"Dataset is not in the corpus lock: {dataset_id}") from exc

    def transformation(self, transformation_id: str) -> LockedTransformation:
        try:
            return self.transformations[transformation_id]
        except KeyError as exc:
            raise CorpusLockError(
                f"Transformation is not in the corpus lock: {transformation_id}"
            ) from exc


def utc_stamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CorpusLockError(f"Duplicate JSON key in corpus lock: {key}")
        result[key] = value
    return result


def _object(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CorpusLockError(f"{context} must be a JSON object")
    return value


def _keys(
    value: dict[str, Any],
    context: str,
    required: set[str],
    optional: set[str] | None = None,
) -> None:
    optional = optional or set()
    missing = required - value.keys()
    unknown = value.keys() - required - optional
    if missing:
        raise CorpusLockError(f"{context} is missing keys: {', '.join(sorted(missing))}")
    if unknown:
        raise CorpusLockError(f"{context} has unknown keys: {', '.join(sorted(unknown))}")


def _text(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise CorpusLockError(f"{context} must be a non-empty, trimmed string")
    if any(ord(character) < 32 for character in value):
        raise CorpusLockError(f"{context} contains control characters")
    return value


def _nonnegative_integer(value: Any, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CorpusLockError(f"{context} must be a non-negative integer")
    return value


def _timestamp(value: Any, context: str) -> str:
    text = _text(value, context)
    if not text.endswith("Z"):
        raise CorpusLockError(f"{context} must be a UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise CorpusLockError(f"{context} is not a valid timestamp") from exc
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise CorpusLockError(f"{context} must be UTC")
    return text


def _safe_component(value: Any, context: str) -> str:
    text = _text(value, context)
    normalized = unicodedata.normalize("NFC", text)
    if normalized != text:
        raise CorpusLockError(f"{context} must use NFC Unicode normalization")
    if (
        text in {".", ".."}
        or "/" in text
        or "\\" in text
        or ":" in text
        or any(character in text for character in '*?"<>|')
        or any(ord(character) < 32 for character in text)
        or text.endswith((".", " "))
        or Path(text).is_absolute()
    ):
        raise CorpusLockError(f"{context} must be a portable basename")
    windows_stem = text.split(".", 1)[0].casefold()
    if windows_stem in {
        "con",
        "prn",
        "aux",
        "nul",
        "clock$",
        "conin$",
        "conout$",
        *(f"com{number}" for number in range(1, 10)),
        *(f"lpt{number}" for number in range(1, 10)),
    }:
        raise CorpusLockError(f"{context} is a reserved Windows filename")
    return text


def _sha256(value: Any, context: str) -> str:
    text = _text(value, context)
    if not _SHA256_PATTERN.fullmatch(text):
        raise CorpusLockError(f"{context} must be a lowercase full SHA-256 digest")
    return text


def _safe_url(value: Any, context: str) -> str:
    text = _text(value, context)
    parsed = urllib.parse.urlsplit(text)
    if parsed.scheme != "https" or not parsed.netloc:
        raise CorpusLockError(f"{context} must be an absolute HTTPS URL")
    if parsed.username is not None or parsed.password is not None:
        raise CorpusLockError(f"{context} must not contain URL credentials")
    if parsed.fragment:
        raise CorpusLockError(f"{context} must not contain a URL fragment")
    for key, _ in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True):
        normalized = re.sub(r"[^a-z0-9]+", "_", key.casefold()).strip("_")
        if (
            normalized in _CREDENTIAL_QUERY_KEYS
            or normalized.endswith(
                ("_auth", "_authorization", "_jwt", "_key", "_sas", "_token", "_signature")
            )
            or any(term in normalized for term in _CREDENTIAL_QUERY_TERMS)
        ):
            raise CorpusLockError(f"{context} must not contain credential query parameters")
    return text


def _parse_locked_file(value: Any, context: str) -> LockedFile:
    item = _object(value, context)
    _keys(item, context, {"filename", "sha256", "size_bytes"})
    return LockedFile(
        filename=_safe_component(item["filename"], f"{context}.filename"),
        sha256=_sha256(item["sha256"], f"{context}.sha256"),
        size_bytes=_nonnegative_integer(item["size_bytes"], f"{context}.size_bytes"),
    )


def load_corpus_lock(path: str | Path = DEFAULT_CORPUS_LOCK) -> CorpusLock:
    lock_path = Path(path)
    try:
        with lock_path.open("r", encoding="utf-8") as handle:
            document = json.load(handle, object_pairs_hook=_strict_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CorpusLockError(f"Cannot read corpus lock {lock_path}: {exc}") from exc

    root = _object(document, "corpus lock")
    _keys(
        root,
        "corpus lock",
        {
            "schema_version",
            "corpus_id",
            "created_at",
            "transformation_version",
            "datasets",
            "transformations",
        },
    )
    if root["schema_version"] != CORPUS_LOCK_SCHEMA_VERSION:
        raise CorpusLockError(
            f"Unsupported corpus lock schema_version: {root['schema_version']!r}"
        )
    transformation_version = _text(
        root["transformation_version"], "corpus lock.transformation_version"
    )
    if transformation_version != CORPUS_TRANSFORMATION_VERSION:
        raise CorpusLockError(
            "Corpus transformation version mismatch: "
            f"lock has {transformation_version!r}, code requires "
            f"{CORPUS_TRANSFORMATION_VERSION!r}"
        )

    raw_datasets = _object(root["datasets"], "corpus lock.datasets")
    datasets: dict[str, LockedDataset] = {}
    dataset_ids_casefold: set[str] = set()
    for dataset_id, raw_dataset in raw_datasets.items():
        safe_id = _safe_component(dataset_id, f"dataset id {dataset_id!r}")
        if safe_id.casefold() in dataset_ids_casefold:
            raise CorpusLockError(f"Duplicate case-insensitive dataset id: {safe_id}")
        dataset_ids_casefold.add(safe_id.casefold())
        item = _object(raw_dataset, f"dataset {safe_id}")
        _keys(
            item,
            f"dataset {safe_id}",
            {"title", "source_url", "dataset_version", "license", "retrieval", "files"},
        )
        license_item = _object(item["license"], f"dataset {safe_id}.license")
        _keys(license_item, f"dataset {safe_id}.license", {"id", "classification"})
        classification = _text(
            license_item["classification"], f"dataset {safe_id}.license.classification"
        )
        if classification not in LICENSE_CLASSIFICATIONS:
            raise CorpusLockError(
                f"Unknown license classification for {safe_id}: {classification}"
            )
        retrieval = _object(item["retrieval"], f"dataset {safe_id}.retrieval")
        _keys(retrieval, f"dataset {safe_id}.retrieval", {"retrieved_at", "method"})
        retrieval_method = _text(
            retrieval["method"], f"dataset {safe_id}.retrieval.method"
        )
        if retrieval_method not in {"https", "authorized_copy"}:
            raise CorpusLockError(
                f"Unsupported retrieval method for {safe_id}: {retrieval_method}"
            )
        raw_files = item["files"]
        if not isinstance(raw_files, list) or not raw_files:
            raise CorpusLockError(f"dataset {safe_id}.files must be a non-empty array")
        files = tuple(
            _parse_locked_file(raw_file, f"dataset {safe_id}.files[{index}]")
            for index, raw_file in enumerate(raw_files)
        )
        filenames_casefold: set[str] = set()
        for locked_file in files:
            if locked_file.filename.casefold() in filenames_casefold:
                raise CorpusLockError(
                    f"Duplicate case-insensitive filename in {safe_id}: {locked_file.filename}"
                )
            filenames_casefold.add(locked_file.filename.casefold())
        datasets[safe_id] = LockedDataset(
            id=safe_id,
            title=_text(item["title"], f"dataset {safe_id}.title"),
            source_url=_safe_url(item["source_url"], f"dataset {safe_id}.source_url"),
            dataset_version=_text(
                item["dataset_version"], f"dataset {safe_id}.dataset_version"
            ),
            license_id=_text(license_item["id"], f"dataset {safe_id}.license.id"),
            license_classification=classification,
            retrieved_at=_timestamp(
                retrieval["retrieved_at"], f"dataset {safe_id}.retrieval.retrieved_at"
            ),
            retrieval_method=retrieval_method,
            files=files,
        )

    raw_transformations = _object(
        root["transformations"], "corpus lock.transformations"
    )
    transformations: dict[str, LockedTransformation] = {}
    transformation_ids_casefold: set[str] = set()
    output_names_casefold: set[str] = set()
    for transformation_id, raw_transformation in raw_transformations.items():
        safe_id = _safe_component(
            transformation_id, f"transformation id {transformation_id!r}"
        )
        if safe_id.casefold() in transformation_ids_casefold:
            raise CorpusLockError(f"Duplicate transformation id: {safe_id}")
        transformation_ids_casefold.add(safe_id.casefold())
        item = _object(raw_transformation, f"transformation {safe_id}")
        _keys(item, f"transformation {safe_id}", {"transformer", "version", "inputs", "output"})
        inputs_item = _object(item["inputs"], f"transformation {safe_id}.inputs")
        if not inputs_item:
            raise CorpusLockError(f"transformation {safe_id}.inputs must not be empty")
        inputs: dict[str, LockedInput] = {}
        roles_casefold: set[str] = set()
        for role, raw_input in inputs_item.items():
            safe_role = _safe_component(role, f"transformation {safe_id} input role")
            if safe_role.casefold() in roles_casefold:
                raise CorpusLockError(f"Duplicate input role in {safe_id}: {safe_role}")
            roles_casefold.add(safe_role.casefold())
            input_item = _object(
                raw_input, f"transformation {safe_id}.inputs.{safe_role}"
            )
            _keys(
                input_item,
                f"transformation {safe_id}.inputs.{safe_role}",
                {"dataset", "filename"},
            )
            input_dataset_id = _text(
                input_item["dataset"],
                f"transformation {safe_id}.inputs.{safe_role}.dataset",
            )
            filename = _safe_component(
                input_item["filename"],
                f"transformation {safe_id}.inputs.{safe_role}.filename",
            )
            if input_dataset_id not in datasets:
                raise CorpusLockError(
                    f"Transformation {safe_id} references unknown dataset {input_dataset_id}"
                )
            if filename not in {locked.filename for locked in datasets[input_dataset_id].files}:
                raise CorpusLockError(
                    f"Transformation {safe_id} references unlocked file "
                    f"{input_dataset_id}/{filename}"
                )
            inputs[safe_role] = LockedInput(input_dataset_id, filename)
        output_item = _object(item["output"], f"transformation {safe_id}.output")
        _keys(
            output_item,
            f"transformation {safe_id}.output",
            {"kind", "filename", "sha256", "size_bytes", "record_count"},
        )
        output_kind = _text(output_item["kind"], f"transformation {safe_id}.output.kind")
        if output_kind != "generated_review_queue":
            raise CorpusLockError(
                f"Unsupported output kind for transformation {safe_id}: {output_kind}"
            )
        output_filename = _safe_component(
            output_item["filename"], f"transformation {safe_id}.output.filename"
        )
        if not output_filename.endswith("-candidates.jsonl"):
            raise CorpusLockError(
                f"Generated review queue must end in -candidates.jsonl: {output_filename}"
            )
        if output_filename.casefold() in output_names_casefold:
            raise CorpusLockError(f"Multiple transformations claim {output_filename}")
        output_names_casefold.add(output_filename.casefold())
        transformations[safe_id] = LockedTransformation(
            id=safe_id,
            transformer=_text(item["transformer"], f"transformation {safe_id}.transformer"),
            version=_text(item["version"], f"transformation {safe_id}.version"),
            inputs=inputs,
            output=LockedOutput(
                kind=output_kind,
                filename=output_filename,
                sha256=_sha256(
                    output_item["sha256"], f"transformation {safe_id}.output.sha256"
                ),
                size_bytes=_nonnegative_integer(
                    output_item["size_bytes"],
                    f"transformation {safe_id}.output.size_bytes",
                ),
                record_count=_nonnegative_integer(
                    output_item["record_count"],
                    f"transformation {safe_id}.output.record_count",
                ),
            ),
        )

    return CorpusLock(
        schema_version=CORPUS_LOCK_SCHEMA_VERSION,
        corpus_id=_safe_component(root["corpus_id"], "corpus lock.corpus_id"),
        created_at=_timestamp(root["created_at"], "corpus lock.created_at"),
        transformation_version=transformation_version,
        datasets=datasets,
        transformations=transformations,
    )


def locked_file(dataset: LockedDataset, filename: str | None = None) -> LockedFile:
    if filename is None:
        if len(dataset.files) != 1:
            raise CorpusLockError(
                f"Dataset {dataset.id} contains {len(dataset.files)} files; filename is required"
            )
        return dataset.files[0]
    for item in dataset.files:
        if item.filename == filename:
            return item
    raise CorpusLockError(f"File is not locked for {dataset.id}: {filename}")


def locked_snapshot_reference(dataset_id: str, filename: str) -> str:
    return f"data/raw/{dataset_id}/{filename}"


def _contained_path(root: Path, *parts: str) -> Path:
    resolved_root = root.resolve()
    candidate = root.joinpath(*parts)
    resolved_candidate = candidate.resolve(strict=False)
    if not resolved_candidate.is_relative_to(resolved_root):
        raise CorpusLockError(f"Locked path escapes configured root: {candidate}")
    if candidate.is_symlink():
        raise CorpusLockError(f"Locked path must not be a symbolic link: {candidate}")
    return candidate


def verify_locked_file(path: str | Path, expected: LockedFile | LockedOutput) -> Path:
    candidate = Path(path)
    if not candidate.exists():
        raise CorpusLockError(f"Locked file is missing: {candidate}")
    if not candidate.is_file() or candidate.is_symlink():
        raise CorpusLockError(f"Locked path is not a regular file: {candidate}")
    actual_size = candidate.stat().st_size
    if actual_size != expected.size_bytes:
        raise CorpusLockError(
            f"Locked file size mismatch for {candidate}: expected {expected.size_bytes}, "
            f"found {actual_size}"
        )
    actual_sha256 = sha256_file(candidate)
    if actual_sha256 != expected.sha256:
        raise CorpusLockError(
            f"Locked file SHA-256 mismatch for {candidate}: expected {expected.sha256}, "
            f"found {actual_sha256}"
        )
    return candidate


def resolve_locked_snapshot(
    corpus_lock: CorpusLock,
    raw_root: str | Path,
    dataset_id: str,
    filename: str | None = None,
) -> Path:
    dataset = corpus_lock.dataset(dataset_id)
    expected = locked_file(dataset, filename)
    candidate = _contained_path(Path(raw_root), dataset.id, expected.filename)
    return verify_locked_file(candidate, expected)


def verify_transformation_output(
    corpus_lock: CorpusLock,
    review_root: str | Path,
    transformation_id: str,
) -> Path:
    transformation = corpus_lock.transformation(transformation_id)
    candidate = _contained_path(Path(review_root), transformation.output.filename)
    verified = verify_locked_file(candidate, transformation.output)
    with verified.open("rb") as handle:
        record_count = sum(1 for line in handle if line.strip())
    if record_count != transformation.output.record_count:
        raise CorpusLockError(
            f"Locked review record count mismatch for {verified}: expected "
            f"{transformation.output.record_count}, found {record_count}"
        )
    return verified


def install_locked_snapshot(
    payload: bytes,
    raw_root: str | Path,
    dataset: LockedDataset,
    expected: LockedFile,
) -> Path:
    actual_sha256 = sha256_bytes(payload)
    if len(payload) != expected.size_bytes or actual_sha256 != expected.sha256:
        raise CorpusLockError(
            f"Downloaded bytes do not match lock for {dataset.id}/{expected.filename}: "
            f"expected {expected.size_bytes} bytes and {expected.sha256}, found "
            f"{len(payload)} bytes and {actual_sha256}"
        )
    root = Path(raw_root)
    destination = _contained_path(root, dataset.id, expected.filename)
    if destination.exists():
        return verify_locked_file(destination, expected)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=destination.parent, prefix=f".{destination.name}.", delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        verify_locked_file(temporary, expected)
        os.replace(temporary, destination)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return destination


def write_snapshot(
    payload: bytes,
    raw_root: str | Path,
    source_id: str,
    source_url: str,
    license_name: str,
    extension: str,
    record_count: int | None = None,
    source_version: str = "",
    notes: str = "",
) -> RawSnapshot:
    root = Path(raw_root)
    source_dir = root / source_id
    source_dir.mkdir(parents=True, exist_ok=True)
    retrieved_at = utc_stamp()
    digest = sha256_bytes(payload)
    safe_time = retrieved_at.replace(":", "").replace("-", "")
    path = source_dir / f"{safe_time}-{digest[:12]}.{extension.lstrip('.')}"
    path.write_bytes(payload)
    snapshot = RawSnapshot(
        source_id=source_id,
        source_url=source_url,
        retrieved_at=retrieved_at,
        license=license_name,
        sha256=digest,
        path=path.as_posix(),
        record_count=record_count,
        source_version=source_version,
        notes=notes,
    )
    append_snapshot_manifest(snapshot, root / "manifest.jsonl")
    return snapshot


def append_snapshot_manifest(snapshot: RawSnapshot, manifest_path: str | Path) -> None:
    path = Path(manifest_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(asdict(snapshot), ensure_ascii=False, sort_keys=True) + "\n")


def review_candidates_bytes(records: list[dict[str, Any]]) -> bytes:
    return b"".join(
        (json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
        for record in records
    )


def validate_review_destination(
    destination: str | Path,
    *,
    expected: LockedOutput | None = None,
    corpus_lock: CorpusLock | str | Path | None = None,
) -> None:
    """Preflight a generated queue destination against a concrete lock contract."""

    path = Path(destination)
    lexical_name = _safe_component(path.name, "review destination filename")
    resolved_name = _safe_component(
        path.resolve(strict=False).name, "resolved review destination filename"
    )
    if expected is not None and path.name.casefold() != expected.filename.casefold():
        raise CorpusLockError(
            f"Review destination {path.name} does not match expected locked output "
            f"{expected.filename}"
        )

    supplied_lock: CorpusLock | None = None
    if isinstance(corpus_lock, CorpusLock):
        supplied_lock = corpus_lock
    elif corpus_lock is not None:
        supplied_lock = load_corpus_lock(corpus_lock)
    default_lock = (
        load_corpus_lock(DEFAULT_CORPUS_LOCK) if DEFAULT_CORPUS_LOCK.is_file() else None
    )

    destination_names = {lexical_name.casefold(), resolved_name.casefold()}

    def matching_output(lock: CorpusLock | None) -> LockedOutput | None:
        if lock is None:
            return None
        return next(
            (
                transformation.output
                for transformation in lock.transformations.values()
                if transformation.output.filename.casefold() in destination_names
            ),
            None,
        )

    default_output = matching_output(default_lock)
    supplied_output = matching_output(supplied_lock)

    if expected is None:
        if default_output is not None or supplied_output is not None:
            raise CorpusLockError(
                f"Refusing unlocked overwrite of corpus review queue {path.name}; "
                "restage it through the locked transformation contract"
            )
        return

    if corpus_lock is not None and supplied_output is None:
        raise CorpusLockError(
            f"Review destination is not declared by the supplied corpus lock: {path.name}"
        )
    authoritative_output = supplied_output if corpus_lock is not None else default_output
    if authoritative_output is not None and expected != authoritative_output:
        raise CorpusLockError(
            f"Supplied output contract does not match the corpus lock for {path.name}"
        )


def write_review_candidates(
    records: list[dict[str, Any]],
    destination: str | Path,
    *,
    expected: LockedOutput | None = None,
    corpus_lock: CorpusLock | str | Path | None = None,
) -> None:
    path = Path(destination)
    validate_review_destination(
        path,
        expected=expected,
        corpus_lock=corpus_lock,
    )
    payload = review_candidates_bytes(records)
    if expected is not None:
        actual_sha256 = sha256_bytes(payload)
        if (
            len(records) != expected.record_count
            or len(payload) != expected.size_bytes
            or actual_sha256 != expected.sha256
        ):
            raise CorpusLockError(
                f"Generated review queue does not match lock for {expected.filename}: "
                f"expected {expected.record_count} records, {expected.size_bytes} bytes, "
                f"and {expected.sha256}; found {len(records)} records, {len(payload)} bytes, "
                f"and {actual_sha256}"
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def append_review_decision(record: dict[str, Any], destination: str | Path) -> None:
    """Append one local human decision without ever rewriting generated queues."""

    path = Path(destination)
    if path.parent.name != "decisions" or path.suffix != ".jsonl":
        raise ValueError("Human decisions must be written under a decisions/*.jsonl path")
    decision_id = record.get("decision_id")
    candidate_id = record.get("candidate_id")
    if not isinstance(decision_id, str) or not decision_id.strip():
        raise ValueError("A human decision requires a stable decision_id")
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("A human decision requires a candidate_id")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                existing = json.loads(line)
                if existing.get("decision_id") == decision_id:
                    raise ValueError(f"Decision id already exists: {decision_id}")
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
