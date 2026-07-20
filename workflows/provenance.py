"""Provenance & AI-labeling for composition outputs (Phase 5, T5.2).

Implements the role-spec provenance promise: every output is tagged as
human-made, AI-assisted, or fully AI-generated, with traceable source refs and
a content hash for integrity. Writes `<artifact>.provenance.json` beside the
artifact.
"""
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import List, Optional

# Provenance classification (mirrors platform monetization / impersonation rules).
HUMAN = "human-made"
AI_ASSISTED = "ai-assisted"
AI_GENERATED = "ai-generated"
VALID_CLASSES = {HUMAN, AI_ASSISTED, AI_GENERATED}


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_provenance(artifact_path: str,
                     classification: str,
                     generator: str,
                     sources: Optional[List[str]] = None,
                     parameters: Optional[dict] = None,
                     notes: str = "") -> dict:
    """Build a provenance record for an artifact.

    Args:
        artifact_path: path to the output file (must exist).
        classification: one of human-made / ai-assisted / ai-generated.
        generator: name of the tool/algorithm that produced it.
        sources: list of source references (files, prompts, seeds).
        parameters: generation parameters for reproducibility.
        notes: free-text note.
    """
    if classification not in VALID_CLASSES:
        raise ValueError(f"classification must be one of {sorted(VALID_CLASSES)}")
    if not os.path.exists(artifact_path):
        raise FileNotFoundError(artifact_path)

    record = {
        "artifact": os.path.basename(artifact_path),
        "classification": classification,
        "generator": generator,
        "sources": sources or [],
        "parameters": parameters or {},
        "notes": notes,
        "sha256": _sha256_file(artifact_path),
        "bytes": os.path.getsize(artifact_path),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "provenance_version": "1.0",
    }
    return record


def write_provenance(artifact_path: str, classification: str, generator: str,
                     **kwargs) -> str:
    """Write `<artifact>.provenance.json` next to the artifact. Returns its path."""
    record = build_provenance(artifact_path, classification, generator, **kwargs)
    prov_path = artifact_path + ".provenance.json"
    with open(prov_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    return prov_path


def policy_warnings(record: dict) -> List[str]:
    """Surface likely distribution / rights issues before publish."""
    warns = []
    if record["classification"] == AI_GENERATED and not record["sources"]:
        warns.append("Fully AI-generated with no source refs — some platforms "
                     "restrict monetization of unattributed AI output.")
    if record["classification"] == AI_ASSISTED and not record["sources"]:
        warns.append("AI-assisted but no human source traced — add attribution "
                     "to preserve credit.")
    if not record.get("generator"):
        warns.append("Missing generator name — provenance is not reproducible.")
    return warns
