#!/usr/bin/env python3
"""Offline operator intake gate; verifies private evidence bytes, never a service."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re

HUB = pathlib.Path(__file__).resolve().parent.parent
REQUIRED = ("owner", "workspace", "runtime", "sources")


def readiness(intake_path: pathlib.Path, expected: dict[str, str], now: dt.datetime | None = None) -> dict:
    reasons: list[str] = []
    now = now or dt.datetime.now(dt.timezone.utc)
    if any(not isinstance(expected.get(key), str) or not expected[key].strip()
           for key in ("ownerId", "workspaceId", "repo")):
        return {"status": "BLOCKED", "reasons": ["private owner/workspace/repo bindings missing"]}
    try:
        intake = json.loads(intake_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "BLOCKED", "reasons": ["private intake missing or malformed"]}
    if not isinstance(intake, dict):
        return {"status": "BLOCKED", "reasons": ["private intake must be a JSON object"]}
    observations = intake.get("observations", {})
    if not isinstance(observations, dict):
        observations = {}
    starter = intake.get("starter", {})
    if (not isinstance(starter, dict)
            or starter.get("slug") != "watts-source-manifest-review"
            or starter.get("paidToolsEnabled") is not False):
        reasons.append("starter: only the no-paid source review is ready; paid roles need verified pre-dispatch cost enforcement")
    for name in REQUIRED:
        entry = observations.get(name)
        if not isinstance(entry, dict):
            reasons.append(f"{name}: missing evidence")
            continue
        try:
            path = pathlib.Path(entry["path"]).resolve()
            if path.is_relative_to(HUB.resolve()) or not path.is_file():
                raise ValueError("evidence must be a private existing file")
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
                raise ValueError("evidence hash mismatch")
            proof = json.loads(raw)
            if not isinstance(proof, dict) or not isinstance(proof.get("observedAt"), str):
                raise ValueError("evidence must be an object with an observation time")
            observed = dt.datetime.fromisoformat(proof["observedAt"].replace("Z", "+00:00"))
            if observed.tzinfo is None or not dt.timedelta(0) <= now - observed <= dt.timedelta(hours=24):
                raise ValueError("evidence is stale or future-dated")
            if proof.get("ownerId") != expected["ownerId"]:
                raise ValueError("owner does not match private binding")
            if name == "owner" and not (proof.get("unique") is True and proof.get("readOnly") is True):
                raise ValueError("unique owner not verified read-only")
            if name == "workspace" and not (proof.get("workspaceId") == expected["workspaceId"]
                                                 and proof.get("unique") is True):
                raise ValueError("workspace not uniquely bound to owner")
            if name == "runtime" and not (proof.get("workspaceId") == expected["workspaceId"]
                                               and proof.get("repo") == expected["repo"]
                                               and proof.get("workspaceBound") is True
                                               and isinstance(proof.get("nativeCreate"), dict)
                                               and proof["nativeCreate"].get("success") is True
                                               and proof["nativeCreate"].get("workspaceId") == expected["workspaceId"]
                                               and isinstance(proof.get("threadId"), str)
                                               and bool(proof["threadId"].strip())
                                               and proof["nativeCreate"].get("threadId") == proof.get("threadId")
                                               and isinstance(proof["nativeCreate"].get("id"), str)
                                               and bool(proof["nativeCreate"]["id"].strip())
                                               and proof.get("contextMounted") is True):
                raise ValueError("runtime did not prove owner/workspace/repo context")
            sources = proof.get("sources")
            valid_sources = isinstance(sources, list) and bool(sources)
            seen_sources: set[str] = set()
            if valid_sources:
                for source in sources:
                    if not isinstance(source, dict):
                        valid_sources = False
                        break
                    source_id = source.get("sourceId")
                    if (not isinstance(source_id, str)
                            or not re.fullmatch(r"[a-z0-9-]+", source_id)
                            or source_id in seen_sources or source.get("mapped") is not True
                            or type(source.get("connected")) is not bool):
                        valid_sources = False
                        break
                    seen_sources.add(source_id)
            if name == "sources" and not (proof.get("ownerScopeVerified") is True
                                               and proof.get("workspaceId") == expected["workspaceId"]
                                               and proof.get("workspaceTargetVerified") is True
                                               and proof.get("mappingComplete") is True
                                               and proof.get("inventoryComplete") is True
                                               and proof.get("paginationComplete") is True
                                               and valid_sources):
                raise ValueError("source snapshot is unavailable, unscoped, or partially mapped")
        except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
            reasons.append(f"{name}: {exc}")
    return {"status": "READY" if not reasons else "BLOCKED", "reasons": reasons,
            "meaning": "no-paid source-review starter eligible for a disabled first-open test; no job enabled or dispatched"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intake", type=pathlib.Path, required=True)
    args = parser.parse_args()
    expected = {"ownerId": os.environ.get("OPERATOR_ACCOUNT_ID", ""),
                "workspaceId": os.environ.get("OPERATOR_WORKSPACE_ID", ""),
                "repo": os.environ.get("OPERATOR_REPO", "")}
    if not all(expected.values()):
        result = {"status": "BLOCKED", "reasons": ["private owner/workspace/repo bindings missing"]}
    else:
        result = readiness(args.intake, expected)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "READY" else 3


if __name__ == "__main__":
    raise SystemExit(main())
