"""Portable, canonical evaluator lookup catalogs.

The evaluator consumes the normalized ``KnowledgeObject`` dictionaries directly
for Gold selector matching.  A catalog therefore stores the complete object
dictionary, rather than a second, hand-maintained subset of fields.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


CATALOG_SCHEMA_VERSION = "panda-evaluator-catalog/v1"
LOOKUP_CONTRACT = "panda.evaluator.lookup/normalized-knowledge-object/v1"
CATALOG_FILENAME = "evaluator_lookup_catalog.json"


class EvaluatorCatalogError(RuntimeError):
    """The portable evaluator lookup catalog is not trustworthy."""


@dataclass(frozen=True)
class EvaluatorCatalogReceipt:
    """Identity of one canonical catalog artifact."""

    schema_version: str
    lookup_contract: str
    sha256: str
    count: int


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _catalog_payload(lookup: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    objects: list[dict[str, Any]] = []
    for object_id in sorted(lookup):
        item = lookup[object_id]
        if not isinstance(item, Mapping):
            raise EvaluatorCatalogError(f"lookup item is not an object: {object_id}")
        if item.get("object_id") != object_id:
            raise EvaluatorCatalogError(f"lookup key/object_id mismatch: {object_id}")
        # Copy the whole normalized dictionary.  This is the evaluator's formal
        # contract, including locator, lineage, metadata, chunks, and derived
        # workflow/data/product/version objects.
        objects.append(dict(item))
    return {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "lookup_contract": LOOKUP_CONTRACT,
        "objects": objects,
    }


def _catalog_bytes(lookup: Mapping[str, Mapping[str, Any]]) -> bytes:
    return (_canonical_json(_catalog_payload(lookup)) + "\n").encode("utf-8")


def catalog_fingerprint(lookup: Mapping[str, Mapping[str, Any]]) -> str:
    """Return the deterministic full-projection fingerprint for a lookup."""
    return hashlib.sha256(_catalog_bytes(lookup)).hexdigest()


def load_normalized_lookup(path: Path) -> dict[str, dict[str, Any]]:
    """Load the canonical normalized source without changing its projection."""
    try:
        stream = path.open(encoding="utf-8")
    except FileNotFoundError as exc:
        raise EvaluatorCatalogError(f"normalized evaluator source is missing: {path}") from exc
    lookup: dict[str, dict[str, Any]] = {}
    with stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                raise EvaluatorCatalogError(f"normalized evaluator source has blank line: {path}:{line_number}")
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise EvaluatorCatalogError(
                    f"normalized evaluator source has invalid JSON: {path}:{line_number}"
                ) from exc
            if not isinstance(item, dict) or not isinstance(item.get("object_id"), str) or not item["object_id"]:
                raise EvaluatorCatalogError(
                    f"normalized evaluator source has invalid object_id: {path}:{line_number}"
                )
            object_id = item["object_id"]
            if object_id in lookup:
                raise EvaluatorCatalogError(f"normalized evaluator source has duplicate object_id: {object_id}")
            lookup[object_id] = item
    if not lookup:
        raise EvaluatorCatalogError(f"normalized evaluator source is empty: {path}")
    return lookup


def write_evaluator_catalog(
    source_objects: Path, destination: Path,
) -> EvaluatorCatalogReceipt:
    """Export a deterministic full-object evaluator catalog and prove parity."""
    source_lookup = load_normalized_lookup(source_objects)
    payload = _catalog_bytes(source_lookup)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    catalog_lookup = load_evaluator_catalog(destination)
    if source_lookup != catalog_lookup:
        raise EvaluatorCatalogError("catalog round-trip does not match normalized lookup")
    return EvaluatorCatalogReceipt(
        schema_version=CATALOG_SCHEMA_VERSION,
        lookup_contract=LOOKUP_CONTRACT,
        sha256=hashlib.sha256(payload).hexdigest(),
        count=len(catalog_lookup),
    )


def load_evaluator_catalog(path: Path) -> dict[str, dict[str, Any]]:
    """Load only a canonical full-projection catalog; reject approximations."""
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise EvaluatorCatalogError(f"evaluator catalog is missing: {path}") from exc
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvaluatorCatalogError(f"evaluator catalog is invalid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise EvaluatorCatalogError(f"evaluator catalog is not an object: {path}")
    if payload.get("schema_version") != CATALOG_SCHEMA_VERSION:
        raise EvaluatorCatalogError("evaluator catalog schema is unsupported")
    if payload.get("lookup_contract") != LOOKUP_CONTRACT:
        raise EvaluatorCatalogError("evaluator catalog lookup contract is unsupported")
    values = payload.get("objects")
    if not isinstance(values, list) or not values:
        raise EvaluatorCatalogError("evaluator catalog objects must be a non-empty list")
    lookup: dict[str, dict[str, Any]] = {}
    for item in values:
        if not isinstance(item, dict) or not isinstance(item.get("object_id"), str) or not item["object_id"]:
            raise EvaluatorCatalogError("evaluator catalog has an invalid object_id")
        object_id = item["object_id"]
        if object_id in lookup:
            raise EvaluatorCatalogError(f"evaluator catalog has duplicate object_id: {object_id}")
        lookup[object_id] = item
    expected = _catalog_bytes(lookup)
    if raw != expected:
        raise EvaluatorCatalogError("evaluator catalog is not canonical full-object serialization")
    return lookup


def catalog_receipt(path: Path) -> EvaluatorCatalogReceipt:
    """Load and fingerprint a catalog after enforcing its canonical format."""
    lookup = load_evaluator_catalog(path)
    return EvaluatorCatalogReceipt(
        schema_version=CATALOG_SCHEMA_VERSION,
        lookup_contract=LOOKUP_CONTRACT,
        sha256=catalog_fingerprint(lookup),
        count=len(lookup),
    )
