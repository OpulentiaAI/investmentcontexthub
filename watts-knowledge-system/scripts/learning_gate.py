#!/usr/bin/env python3
"""Offline, fail-closed assessment of proposed hub learnings.

This gate checks supplied review metadata; it cannot authenticate a reviewer or
establish that a review actually occurred. Call assess again when consuming a
receipt rather than trusting its stored decisions. It never writes knowledge.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


CANDIDATE_FIELDS = {
    "learningId", "kind", "scope", "content", "rationale", "sourceRef",
    "sourceSha256", "sourceKind",
}
SOURCE_KINDS = {"human", "artifact", "telemetry", "code", "documentation"}
KINDS = {"system-fact", "operating-practice"}
SHA256 = re.compile(r"sha256:[0-9a-fA-F]{64}\Z")
MAX_INPUT_BYTES = 1024 * 1024


def _canonical(value: object) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ValueError("input must contain finite JSON values") from exc


def candidate_hash(candidate: object) -> str:
    """Hash a candidate's entire canonical JSON representation."""
    return "sha256:" + hashlib.sha256(_canonical(candidate)).hexdigest()


def candidate_set_hash(candidates: list) -> str:
    """Hash sorted candidate hashes, independent of candidate order."""
    if not isinstance(candidates, list):
        raise ValueError("candidates must be an array")
    return "sha256:" + hashlib.sha256(
        _canonical(sorted(candidate_hash(candidate) for candidate in candidates))
    ).hexdigest()


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _normalize(value: str) -> str:
    return " ".join(value.split()).casefold()


def _candidate_problem(candidate: object) -> str | None:
    if not isinstance(candidate, dict) or set(candidate) != CANDIDATE_FIELDS:
        return "Invalid candidate fields"
    if any(not _nonblank(candidate[key]) for key in CANDIDATE_FIELDS):
        return "Candidate fields must be nonblank strings"
    if candidate["learningId"] != candidate["learningId"].strip():
        return "Invalid learning ID"
    if candidate["kind"] not in KINDS or candidate["sourceKind"] not in SOURCE_KINDS:
        return "Unknown candidate kind or source kind"
    if len(candidate["content"]) > 300:
        return "Candidate content exceeds 300 characters"
    if not SHA256.fullmatch(candidate["sourceSha256"]):
        return "Invalid source SHA-256"
    if any(token in candidate[key].upper() for key in ("sourceRef", "sourceSha256", "sourceKind")
           for token in ("UNVERIFIED", "[NEED:")):
        return "Unverified source"
    return None


def validate_candidate(candidate: object) -> None:
    """Raise ValueError if a candidate fails the exact field and scalar contract."""
    problem = _candidate_problem(candidate)
    if problem:
        raise ValueError(problem)


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON key")
        obj[key] = value
    return obj


def _reject_nonfinite(_value: str) -> None:
    raise ValueError("non-finite JSON value")


def _decode(text: str) -> object:
    return json.loads(text, object_pairs_hook=_unique_object, parse_constant=_reject_nonfinite)


def assess(candidates: list, review: str | dict | None, *, generator_id: str,
           existing: list | None = None) -> dict:
    """Return a reproducible receipt; only exact reviewed candidates can pass."""
    if existing is None:
        existing = []
    if (not isinstance(candidates, list) or not isinstance(existing, list)
            or not _nonblank(generator_id) or generator_id != generator_id.strip()):
        raise ValueError("invalid assessment input")
    candidates = _decode(_canonical(candidates).decode("utf-8"))
    existing = _decode(_canonical(existing).decode("utf-8"))
    set_hash = candidate_set_hash(candidates)
    existing_keys = set()
    existing_ids = set()
    for item in existing:
        if (not isinstance(item, dict) or not all(_nonblank(item.get(key)) for key in
                                               ("learningId", "scope", "content"))
                or item["learningId"] != item["learningId"].strip()):
            raise ValueError("invalid existing learning")
        existing_ids.add(item["learningId"])
        existing_keys.add((_normalize(item["scope"]), _normalize(item["content"])))

    decoded = None
    valid_review = False
    reviewer_id = None
    verdicts = []
    if candidates:
        if isinstance(review, str):
            try:
                decoded = _decode(review)
            except (ValueError, TypeError, RecursionError):
                pass
        elif isinstance(review, dict):
            try:
                decoded = _decode(_canonical(review).decode("utf-8"))
            except (ValueError, TypeError, RecursionError):
                pass
        if (isinstance(decoded, dict)
                and set(decoded) == {"reviewerId", "candidateSetHash", "verdicts"}
                and _nonblank(decoded["reviewerId"])
                and decoded["reviewerId"] == decoded["reviewerId"].strip()
                and decoded["reviewerId"].casefold() != generator_id.casefold()
                and decoded["candidateSetHash"] == set_hash
                and isinstance(decoded["verdicts"], list)):
            valid_review = True
            reviewer_id = decoded["reviewerId"]
            verdicts = decoded["verdicts"]
        elif isinstance(decoded, dict) and _nonblank(decoded.get("reviewerId")):
            reviewer_id = decoded["reviewerId"]

    ids = [candidate.get("learningId") if isinstance(candidate, dict) else None
           for candidate in candidates]
    keys = [(_normalize(candidate["scope"]), _normalize(candidate["content"]))
            if isinstance(candidate, dict) and all(_nonblank(candidate.get(key)) for key in ("scope", "content"))
            else None for candidate in candidates]
    decisions = []
    for candidate, learning_id, key in zip(candidates, ids, keys):
        digest = candidate_hash(candidate)
        try:
            validate_candidate(candidate)
            problem = None
        except ValueError as exc:
            problem = str(exc)
        if not valid_review:
            problem = "Invalid review envelope"
        elif problem:
            pass
        elif ids.count(learning_id) != 1 or learning_id in existing_ids:
            problem = "Duplicate learning ID"
        elif key in existing_keys or keys.count(key) != 1:
            problem = "Duplicate existing learning"
        else:
            matches = [item for item in verdicts if isinstance(item, dict)
                       and item.get("learningId") == learning_id]
            if len(matches) != 1:
                problem = "Missing or ambiguous verdict"
            elif (set(matches[0]) != {"learningId", "candidateHash", "decision", "reason"}
                  or matches[0]["candidateHash"] != digest
                  or matches[0]["decision"] not in ("ACCEPT", "REJECT")
                  or not _nonblank(matches[0]["reason"])):
                problem = "Invalid or mismatched verdict"
            elif matches[0]["decision"] == "REJECT":
                problem = matches[0]["reason"]
        decisions.append({"learningId": learning_id, "candidateHash": digest,
                          "decision": "rejected" if problem else "accepted",
                          "reason": problem or matches[0]["reason"]})

    return {"schemaVersion": 1, "generatorId": generator_id, "reviewerId": reviewer_id,
            "candidateSetHash": set_hash, "candidates": candidates,
            "existing": existing, "review": decoded, "decisions": decisions}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assess supplied learning review metadata offline")
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        with args.input.open("rb") as source:
            data = source.read(MAX_INPUT_BYTES + 1)
        if len(data) > MAX_INPUT_BYTES:
            raise ValueError("input too large")
        payload = _decode(data.decode("utf-8"))
        if not isinstance(payload, dict) or not {"candidates", "review", "generatorId"} <= set(payload) \
                or set(payload) - {"candidates", "review", "generatorId", "existing"}:
            raise ValueError("invalid input envelope")
        receipt = assess(payload["candidates"], payload["review"],
                         generator_id=payload["generatorId"], existing=payload.get("existing", []))
        output = json.dumps(receipt, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    except (OSError, ValueError, TypeError, UnicodeError, RecursionError):
        print("Invalid learning gate input", file=sys.stderr)
        return 2
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
