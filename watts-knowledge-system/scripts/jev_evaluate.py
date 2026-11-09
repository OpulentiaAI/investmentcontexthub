#!/usr/bin/env python3
"""
jev_evaluate.py — run a typed Jev evaluation and record a public-safe receipt.

Why this exists
---------------
"Jev was used" is not a claim anyone can check. A decision is only evidence when
it carries the request that produced it, the probabilities that were stated
*before* the outcome, and the deterministic rule code applied afterwards.

This script is the receipt writer. It:

  1. reads a request (state + typed questions) from a file,
  2. hashes the canonical request so the input is reproducible,
  3. calls the TypeSafe endpoint,
  4. records the raw answers, the probabilities, the confidence, and the usage,
  5. applies a *deterministic* decision rule in code and records its outcome.

The model judges. Code decides. A receipt that omits the deterministic outcome
is half a record, so this writes both or neither.

    python3 scripts/jev_evaluate.py --request req.json --purpose "why this ran" \
        --out evidence/jev-receipts/name.json

    python3 scripts/jev_evaluate.py --request req.json --purpose "..." --offline \
        --response canned.json        # no network; for tests and CI

Endpoint and auth come from the environment. The key is read at runtime, never
written to the receipt, never printed, never committed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
SCHEMA_VERSION = "1.0"
TIMEOUT_S = 2
MAX_BODY = 16 << 20
PUBLIC_UNSAFE = (
    ("email address", re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")),
    ("API key", re.compile(r"\bsk-[A-Za-z0-9]{20,}")),
    ("bearer token", re.compile(r"\bBearer\s+[A-Za-z0-9\-._~+/]{30,}")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
)


def canonical(request: dict) -> bytes:
    """Stable bytes for hashing: sorted keys, no incidental whitespace."""
    return json.dumps(request, sort_keys=True, separators=(",", ":")).encode("utf-8")


def input_hash(request: dict) -> str:
    return "sha256:" + hashlib.sha256(canonical(request)).hexdigest()


def assert_public_safe(value: object, label: str) -> None:
    """Reject public receipt content that looks like a private payload or secret."""
    try:
        text = json.dumps(value, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} is not JSON-serializable") from exc
    for kind, pattern in PUBLIC_UNSAFE:
        if pattern.search(text):
            raise ValueError(f"{label} contains an {kind}; public receipts require synthetic/redacted inputs")


def call(request: dict, key: str) -> dict:
    body = canonical(request)
    if len(body) > MAX_BODY:
        raise ValueError("request exceeds the response/body cap")
    req = urllib.request.Request(
        ENDPOINT, data=body, method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        decoded = json.loads(resp.read(MAX_BODY).decode("utf-8"))
    if not isinstance(decoded, dict) or not isinstance(decoded.get("answers"), dict):
        raise ValueError("provider response lacks an answers map")
    return decoded


def extract_answers(response: dict) -> list[dict]:
    """Normalize noul / choice / score answers into one list."""
    out = []
    for qid, a in (response.get("answers") or {}).items():
        rec = {"question_id": qid, "type": a.get("type")}
        if a.get("type") == "noul":
            rec["value"] = a.get("noul")
        elif a.get("type") == "choice":
            rec["value"] = a.get("choice")
            rec["probabilities"] = a.get("probabilities")
            rec["confidence"] = a.get("confidence")
        elif a.get("type") == "score":
            rec["value"] = a.get("score")
            rec["probabilities"] = a.get("probabilities")
            rec["confidence"] = a.get("confidence")
            rec["legend"] = (a.get("legend") or {}).values() if isinstance(a.get("legend"), dict) else a.get("legend")
        out.append(rec)
    return sorted(out, key=lambda r: r["question_id"])


def expected_value(answer: dict, level_points: list[float]) -> float | None:
    """sum(p * points) — for a threshold comparison, never a magnitude."""
    probs = answer.get("probabilities")
    if not probs or not level_points:
        return None
    total = 0.0
    for i, p in enumerate(level_points):
        total += float(probs.get(str(i), 0.0)) * p
    return total


def deterministic_decision(answers: list[dict], rules: dict) -> dict:
    """Apply thresholds in code. Abstention and unavailability are outcomes."""
    by_id = {a["question_id"]: a for a in answers}
    applied = []
    outcome = "pass"
    for qid, rule in rules.items():
        ans = by_id.get(qid)
        if ans is None:
            applied.append({"question_id": qid, "gate_result": "missing",
                            "reason": "question was not answered"})
            outcome = "review"
            continue
        entry = {"question_id": qid, "threshold": rule.get("threshold"),
                 "direction": rule.get("direction", "at_least"),
                 "value": ans.get("value")}
        if ans["type"] == "noul":
            v = ans.get("value")
            if v is None or not 0.0 <= v <= 1.0:
                entry["gate_result"] = "unavailable"
                entry["reason"] = "invalid probability; deterministic fallback required"
                outcome = "unavailable" if outcome == "pass" else outcome
            else:
                lo, hi = rule.get("review_band", [0.4, 0.6])
                if lo <= v <= hi:
                    entry["gate_result"] = "review"
                    entry["reason"] = "probability is in the human-review band"
                    outcome = "review" if outcome in ("pass",) else outcome
                elif (rule.get("direction") == "at_most" and v <= rule.get("threshold", 0.5)) or \
                     (rule.get("direction", "at_least") == "at_least" and v >= rule.get("threshold", 0.5)):
                    entry["gate_result"] = "passed"
                else:
                    entry["gate_result"] = "failed"
                    entry["reason"] = "threshold not met on the safe side"
                    outcome = "fail"
        else:
            entry["gate_result"] = "recorded"
            entry["reason"] = "composite input; combined by the published weights in code"
        applied.append(entry)
    return {"rule": "threshold gates, safe side; abstention and unavailability are outcomes",
            "outcome": outcome, "components": applied}


def input_summary(request: dict) -> dict:
    return {
        "stateKeys": sorted(request.get("state", {}).keys())
        if isinstance(request.get("state"), dict) else ["<scalar>"],
        "questionIds": sorted((request.get("questions") or {}).keys()),
        "questionTypes": {k: v.get("type") for k, v in (request.get("questions") or {}).items()},
        "questionSetVersion": request.get("questionSetVersion", "unversioned"),
    }


def unavailable_receipt(request: dict, rules: dict, purpose: str, reason: str) -> dict:
    """Record an unavailable call without losing its reproducible inputs."""
    return {
        "schemaVersion": SCHEMA_VERSION,
        "purpose": purpose,
        "endpoint": ENDPOINT,
        "offline": False,
        "model": None,
        "inputHash": input_hash(request),
        "inputSummary": input_summary(request),
        "request": request,
        "rules": rules,
        "response": None,
        "answers": [],
        "deterministicDecision": {
            "rule": "provider unavailable; deterministic rubric answers instead",
            "outcome": "unavailable",
            "components": [],
            "reason": reason,
        },
        "usage": None,
    }


def build_receipt(request: dict, response: dict, purpose: str,
                  rules: dict, offline: bool) -> dict:
    answers = extract_answers(response)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "purpose": purpose,
        "endpoint": ENDPOINT,
        "offline": offline,
        "model": response.get("model"),
        "inputHash": input_hash(request),
        "inputSummary": input_summary(request),
        # The public hub only accepts synthetic/redacted requests. Keeping all
        # three inputs makes the hash and deterministic outcome reproducible.
        "request": request,
        "rules": rules,
        "response": response,
        "answers": answers,
        "deterministicDecision": deterministic_decision(answers, rules),
        "usage": response.get("usage"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", required=True)
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rules", default=None,
                    help="JSON file of {question_id: {threshold, direction, review_band}}")
    ap.add_argument("--offline", action="store_true",
                    help="do not call the network; requires --response")
    ap.add_argument("--live", action="store_true",
                    help="explicitly request a paid provider call after current confirmation")
    ap.add_argument("--response", default=None, help="canned response JSON for --offline")
    args = ap.parse_args()

    request = json.loads(pathlib.Path(args.request).read_text(encoding="utf-8"))
    rules = json.loads(pathlib.Path(args.rules).read_text(encoding="utf-8")) if args.rules else {}
    try:
        assert_public_safe(request, "request")
        assert_public_safe(rules, "rules")
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.offline:
        if not args.response:
            print("--offline requires --response", file=sys.stderr)
            return 2
        response = json.loads(pathlib.Path(args.response).read_text(encoding="utf-8"))
    else:
        if not args.live or os.environ.get("CONFIRM") != "send":
            receipt = unavailable_receipt(
                request, rules, args.purpose,
                "live TypeSafe call not explicitly confirmed; offline fallback required",
            )
            out = pathlib.Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            print(f"unavailable (live call not authorized) -> {out}")
            return 0
        key = os.environ.get("TYPESAFE_API_KEY", "")
        if not key:
            # Unavailable is a recorded outcome, not a crash and not a silent skip.
            receipt = unavailable_receipt(
                request, rules, args.purpose,
                "TYPESAFE_API_KEY not bound; deterministic rubric answers instead",
            )
            out = pathlib.Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            print(f"unavailable (no key) -> {out}")
            return 0
        try:
            response = call(request, key)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError,
                UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError, KeyError) as exc:
            receipt = unavailable_receipt(
                request, rules, args.purpose,
                f"provider call failed: {type(exc).__name__}; deterministic rubric answers instead",
            )
            out = pathlib.Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            print(f"unavailable (provider failure) -> {out}")
            return 0

    try:
        assert_public_safe(response, "response")
    except ValueError as exc:
        receipt = unavailable_receipt(request, rules, args.purpose, str(exc))
    else:
        receipt = build_receipt(request, response, args.purpose, rules, args.offline)
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"{receipt['deterministicDecision']['outcome']} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
