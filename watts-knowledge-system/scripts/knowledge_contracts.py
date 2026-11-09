"""Offline evidence bindings for learning review and issue resolution records."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
import re

try:
    from scripts.learning_gate import assess, candidate_hash, validate_candidate
except ModuleNotFoundError:
    from learning_gate import assess, candidate_hash, validate_candidate


CANDIDATE_FIELDS = (
    "learningId", "kind", "scope", "content", "rationale", "sourceRef",
    "sourceSha256", "sourceKind",
)
MAX_PROOF_BYTES = 1024 * 1024


def _meaningful(value):
    return (isinstance(value, str) and bool(value.strip())
            and value.strip().upper() not in {"UNVERIFIED", "UNKNOWN", "NONE", "N/A"}
            and "[NEED:" not in value.upper())


def _time(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string")
    result = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("timestamp requires timezone")
    return result


def _proof(root, ref, digest):
    if not isinstance(ref, str) or not ref or Path(ref).is_absolute():
        raise ValueError("evidence must be a relative file")
    relative = Path(ref)
    if any(part in {"..", "ops"} or part.startswith(".") for part in relative.parts):
        raise ValueError("evidence must be public-safe and inside the hub")
    path = root / relative
    if any(part.is_symlink() for part in [path, *path.parents] if part != root.parent):
        raise ValueError("evidence cannot be a symlink")
    path = path.resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("evidence file is missing or outside the hub")
    if path.stat().st_size > MAX_PROOF_BYTES:
        raise ValueError("evidence exceeds size limit")
    raw = path.read_bytes()
    if not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ValueError("evidence requires a sha256 digest")
    if "sha256:" + hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError("evidence hash mismatch")
    return raw


def _json(raw):
    def reject_constant(value):
        raise ValueError("invalid JSON number")

    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    result = json.loads(raw, parse_constant=reject_constant, object_pairs_hook=unique_pairs)
    json.dumps(result, allow_nan=False)
    if not isinstance(result, dict):
        raise ValueError("receipt must be an object")
    return result


def check_records(root: Path, records: list[tuple[Path, dict]]) -> list[str]:
    errors = []
    learnings = [(path, fm) for path, fm in records if fm.get("type") == "wks.learning"]
    issues = [(path, fm) for path, fm in records if fm.get("type") == "wks.issue"]
    seen_ids = set()
    active_content = set()
    valid_learnings = set()
    for path, fm in learnings:
        label = str(path.relative_to(root))
        try:
            candidate = {key: fm.get(key, "") for key in CANDIDATE_FIELDS}
            validate_candidate(candidate)
            if candidate["learningId"] in seen_ids:
                raise ValueError("duplicate learningId")
            seen_ids.add(candidate["learningId"])
            _proof(root, fm.get("sourceRef"), fm.get("sourceSha256"))
            if fm.get("decision") not in {"candidate", "accepted", "rejected", "superseded"}:
                raise ValueError("invalid learning decision")
            if fm.get("decision") in {"accepted", "superseded"}:
                receipt = _json(_proof(root, fm.get("reviewReceipt"), fm.get("reviewReceiptSha256")))
                if type(receipt.get("schemaVersion")) is not int or receipt["schemaVersion"] != 1:
                    raise ValueError("review receipt has an unsupported version")
                replay = assess(receipt["candidates"], receipt["review"],
                                generator_id=receipt["generatorId"], existing=receipt["existing"])
                if (receipt.get("decisions") != replay["decisions"]
                        or receipt.get("candidateSetHash") != replay["candidateSetHash"]
                        or receipt.get("reviewerId") != replay["reviewerId"]):
                    raise ValueError("review receipt does not reproduce")
                matching = [item for item in replay["decisions"]
                            if item["learningId"] == candidate["learningId"]]
                if (len(matching) != 1 or matching[0]["decision"] != "accepted"
                        or matching[0]["candidateHash"] != candidate_hash(candidate)):
                    raise ValueError("learning lacks exact accepted review")
            if fm.get("decision") == "accepted":
                key = tuple(" ".join(fm[field].casefold().split()) for field in ("scope", "content"))
                if key in active_content:
                    raise ValueError("duplicate accepted learning in the same scope")
                active_content.add(key)
            if fm.get("decision") != "superseded" and fm.get("supersededBy"):
                raise ValueError("only superseded learning may name a replacement")
            valid_learnings.add(path)
        except (KeyError, ValueError, TypeError, OSError, RecursionError):
            errors.append(f"{label}: learning requires valid source and exact reproducible review; no duplicate IDs/content")

    for path, fm in learnings:
        if fm.get("decision") != "superseded":
            continue
        ref = fm.get("supersededBy", "")
        match = re.fullmatch(r"\[\[([^\]]+)\]\]", ref)
        targets = [(p, item) for p, item in learnings if match and p.stem == match[1]]
        if (len(targets) != 1 or targets[0][0] == path or targets[0][0] not in valid_learnings
                or targets[0][1].get("decision") != "accepted"
                or targets[0][1].get("scope") != fm.get("scope")):
            errors.append(f"{path.relative_to(root)}: superseded learning requires an accepted same-scope replacement")

    seen_issues = set()
    for path, fm in issues:
        label = str(path.relative_to(root))
        try:
            for field in ("issueId", "scope", "symptom"):
                if not _meaningful(fm.get(field)):
                    raise ValueError("missing issue identity")
            if fm["issueId"] in seen_issues:
                raise ValueError("duplicate issueId")
            seen_issues.add(fm["issueId"])
            start, end = _time(fm.get("windowStart")), _time(fm.get("windowEnd"))
            if start >= end:
                raise ValueError("reversed incident window")
            _proof(root, fm.get("evidenceRef"), fm.get("evidenceSha256"))
            baseline = fm.get("baselineStatus")
            if baseline == "available":
                comparison = _json(_proof(root, fm.get("baselineRef"), fm.get("baselineSha256")))
                if any(comparison.get(key) != fm.get(key) for key in ("scope", "symptom")):
                    raise ValueError("baseline must match the exact scope and symptom")
                before_start = _time(comparison.get("windowStart"))
                before_end = _time(comparison.get("windowEnd"))
                if before_end > start or before_end - before_start != end - start:
                    raise ValueError("baseline must precede the incident and have the same duration")
                observation = comparison.get("observed")
                if (not _meaningful(comparison.get("query")) or observation is None
                        or observation == "" or observation == {} or observation == []):
                    raise ValueError("baseline requires the exact query and observed result")
            elif baseline != "unavailable" or not _meaningful(fm.get("limitation")):
                raise ValueError("baseline or explicit limitation is required")
            if fm.get("conclusion") not in {"unverified", "inconclusive", "confirmed"}:
                raise ValueError("unknown conclusion")
            if fm.get("conclusion") == "confirmed":
                if baseline != "available" or any(not _meaningful(fm.get(key)) for key in
                                                  ("runtimeRevision", "mechanism", "alternatives")):
                    raise ValueError("confirmed cause requires runtime, baseline, mechanism and alternatives")
                if _time(fm.get("causeObservedAt")) > start:
                    raise ValueError("cause must precede the observed symptom")
            if fm.get("phase") not in {"detected", "investigating", "blocked", "mitigated", "resolved"}:
                raise ValueError("unknown issue phase")
            if fm.get("phase") == "blocked" and not _meaningful(fm.get("blockerNote")):
                raise ValueError("blocked issue requires a blocker")
            if fm.get("phase") == "resolved":
                if not _meaningful(fm.get("changeRef")):
                    raise ValueError("resolution requires a change reference")
                applied = _time(fm.get("changeAppliedAt"))
                proof = _json(_proof(root, fm.get("verificationRef"), fm.get("verificationSha256")))
                if type(proof.get("schemaVersion")) is not int or proof["schemaVersion"] != 1:
                    raise ValueError("unsupported verification schema")
                if any(proof.get(key) != fm.get(key) for key in ("issueId", "scope", "symptom", "changeRef")):
                    raise ValueError("resolution evidence belongs to another issue or change")
                checked = _time(proof.get("checkedAt"))
                if checked <= applied or checked <= end or checked > dt.datetime.now(dt.timezone.utc):
                    raise ValueError("verification must be post-change and post-incident")
                if not _meaningful(proof.get("check")) or not _meaningful(proof.get("runtimeRevision")):
                    raise ValueError("verification requires check and observed runtime revision")
                expected = proof["expected"]
                if expected is None or expected == "" or expected == {} or expected == []:
                    raise ValueError("verification requires an explicit expected result")
                if json.dumps(expected, sort_keys=True, allow_nan=False) != json.dumps(proof["observed"], sort_keys=True, allow_nan=False):
                    raise ValueError("post-change verification did not match expected result")
        except (KeyError, ValueError, TypeError, OSError, RecursionError):
            errors.append(f"{label}: issue requires scoped evidence, baseline/limitation, and post-change resolution proof")
    return errors
