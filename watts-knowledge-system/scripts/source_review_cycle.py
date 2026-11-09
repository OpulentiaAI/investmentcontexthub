#!/usr/bin/env python3
"""Deterministic source-review cycle on an owner-scoped, pre-mounted safe snapshot.

This is one useful offline worker, not a scheduler or a provider executor.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
import pathlib
import re
import sys
import tempfile

try:
    from scripts.validate import manifest_rows
except ModuleNotFoundError:
    from validate import manifest_rows

HUB = pathlib.Path(__file__).resolve().parent.parent
SPEC = HUB / "automations" / "source-manifest-review.md"
MANIFEST = HUB / "entities" / "source-manifest.md"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_atomic(path: pathlib.Path, data: bytes) -> None:
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = pathlib.Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def review(snapshot: dict, manifest: list[dict[str, str]], now: dt.datetime) -> str:
    if snapshot.get("ownerScopeVerified") is not True or snapshot.get("workspaceTargetVerified") is not True:
        raise ValueError("owner scope and target workspace not verified")
    observed = dt.datetime.fromisoformat(snapshot["observedAt"].replace("Z", "+00:00"))
    if observed.tzinfo is None or not dt.timedelta(0) <= now - observed <= dt.timedelta(hours=24):
        raise ValueError("source snapshot missing, future-dated, or older than 24 hours")
    sources = snapshot.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("source snapshot is empty or unavailable, not a verified zero")
    incomplete = snapshot.get("inventoryComplete") is not True or snapshot.get("paginationComplete") is not True
    ids = [s.get("sourceId") for s in sources if isinstance(s, dict)]
    if (len(ids) != len(sources) or len(set(ids)) != len(ids)
            or any(not isinstance(x, str) or not re.fullmatch(r"[a-z0-9-]+", x) for x in ids)):
        raise ValueError("source snapshot has missing or duplicate source identifiers")
    for source in sources:
        if (type(source.get("connected")) is not bool
                and not (source.get("connected") is None and source.get("reach") == "unknown"
                         and incomplete)):
            raise ValueError("source snapshot has unverified connector state outside a partial observation")
    by_id = {s["sourceId"]: s for s in sources}
    manifest_ids = {row["sourceId"] for row in manifest}
    lines = ["# Source coverage review", "", f"Observed: {snapshot['observedAt']}", "",
             "| Source | Manifest | Observed | Finding | Blocker note |", "|---|---|---|---|---|"]
    covered = 0
    for sid in sorted(manifest_ids | set(by_id)):
        row = next((r for r in manifest if r["sourceId"] == sid), None)
        actual = by_id.get(sid)
        if not actual:
            finding = "No observed source; coverage UNVERIFIED"
        elif actual["connected"] is None:
            finding = ("Catalog projection only; authentication and reach UNVERIFIED"
                       if row else "Unmapped catalog/connection identity; authentication and reach UNVERIFIED")
        elif not row:
            finding = "Unmapped connection; source identity UNVERIFIED" if actual.get("mapped") is False else "Missing manifest row"
        elif actual["connected"] and row["state"] == "extracted":
            finding = "Extracted claim requires separately validated run proof"
        elif not actual["connected"] and row.get("reach") == "readable":
            finding = "Declared readable but capability is disconnected"
        elif row["state"] in ("pending", "unavailable", "blocked"):
            finding = "Not extracted; coverage UNVERIFIED"
        else:
            finding = "Agrees on declared state only; no live payload proof"
        if actual and actual["connected"] and row:
            covered += 1
        observed_state = ("UNVERIFIED" if actual["connected"] is None else
                          "connected" if actual["connected"] else "disconnected") if actual else "UNVERIFIED"
        blocker = row.get("blockerNote", "") if row else ""
        if row and row["state"] in ("pending", "unavailable", "blocked") and not blocker:
            blocker = "MISSING: manifest row has no blocker note"
        blocker = blocker.replace("\\", "\\\\").replace("|", "\\|").replace("\n", "\\n").replace("\r", "\\r")
        lines.append(f"| {sid} | {row['state'] if row else 'MISSING'} | {observed_state} | {finding} | {blocker} |")
    connected = sum(s["connected"] is True for s in sources)
    unknown = sum(s["connected"] is None for s in sources)
    lines.extend(["", f"Connected sources with a manifest row: {covered}/{connected}.",
                  f"Catalog/connection identities with unknown authentication: {unknown}.",
                  "This compares metadata only; it does not establish source reach or extraction completeness.", ""])
    if (incomplete or snapshot.get("mappingComplete") is not True or unknown
            or any(s.get("mapped") is False for s in sources)):
        lines.append("PARTIAL: capability inventory, pagination or explicit source mapping is incomplete. No FULL coverage claim.")
    return "\n".join(lines)


def cycle(run_id: str, snapshot_path: pathlib.Path, out: pathlib.Path,
          spec: pathlib.Path = SPEC, manifest_path: pathlib.Path = MANIFEST,
          now: dt.datetime | None = None) -> dict:
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", run_id):
        raise ValueError("run ID must be an opaque path-safe identifier")
    if out.resolve().is_relative_to(HUB.resolve()):
        raise ValueError("run receipts belong in a private output directory, not the repository")
    run_dir = out / run_id
    if run_dir.is_symlink():
        raise ValueError("run directory must not be a symlink")
    run_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    run_dir.chmod(0o700)
    lock_fd = os.open(run_dir / ".lock", os.O_CREAT | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(lock_fd, "w") as lock:
        os.fchmod(lock.fileno(), 0o600)
        fcntl.flock(lock, fcntl.LOCK_EX)
        spec_bytes = spec.read_bytes()
        manifest_bytes = manifest_path.read_bytes()
        input_bytes = snapshot_path.read_bytes() if snapshot_path.is_file() else b""
        source_receipt = snapshot_path.with_name("observation-receipt.json")
        receipt_bytes = source_receipt.read_bytes() if source_receipt.is_file() else b""
        fingerprint = digest(json.dumps({"spec": digest(spec_bytes), "manifest": digest(manifest_bytes),
                                         "snapshot": digest(input_bytes), "observation": digest(receipt_bytes)},
                                        sort_keys=True, separators=(",", ":")).encode())
        receipt_path = run_dir / "receipt.json"
        artifact_path = run_dir / "source-manifest-review.md"
        old = None
        if receipt_path.is_file() and not receipt_path.is_symlink():
            try:
                old = json.loads(receipt_path.read_text(encoding="utf-8"))
                if (not isinstance(old, dict) or old.get("runId") != run_id
                        or type(old.get("attempt")) is not int or old["attempt"] < 1):
                    old = None
            except (ValueError, OSError):
                old = None
        if old and old.get("status") == "succeeded" and old.get("inputHash") != fingerprint:
            raise ValueError("run ID already succeeded with different inputs")
        result = {"runId": run_id, "status": "blocked", "inputHash": fingerprint,
                  "specSha256": digest(spec_bytes), "attempt": 1, "artifactSha256": None,
                  "reason": None, "at": (now or dt.datetime.now(dt.timezone.utc)).isoformat()}
        if old:
            result["attempt"] = old.get("attempt", 0) + 1
        try:
            observed_receipt = json.loads(receipt_bytes)
            if (not isinstance(observed_receipt, dict)
                    or observed_receipt.get("mode") != "read-only-capability-metadata"
                    or not isinstance(observed_receipt.get("sha256"), dict)
                    or observed_receipt.get("sha256", {}).get("sources") != digest(input_bytes)):
                raise ValueError("source observation receipt is absent or hash-mismatched")
            snapshot = json.loads(input_bytes)
            if not isinstance(snapshot, dict) or not isinstance(snapshot.get("observedAt"), str):
                raise ValueError("source snapshot must be an object with an observation timestamp")
            rows, errors = manifest_rows(manifest_bytes.decode("utf-8"))
            if errors or not rows or len({r["sourceId"] for r in rows}) != len(rows):
                raise ValueError("source manifest is malformed or ambiguous")
            artifact = review(snapshot, rows, now or dt.datetime.now(dt.timezone.utc))
            if (old and old.get("status") == "succeeded" and old.get("specSha256") == digest(spec_bytes)
                    and artifact_path.is_file() and not artifact_path.is_symlink()
                    and digest(artifact_path.read_bytes()) == old.get("artifactSha256")
                    and digest(artifact.encode("utf-8")) == old.get("artifactSha256")):
                return old
            write_atomic(artifact_path, artifact.encode("utf-8"))
            partial = (snapshot.get("inventoryComplete") is not True
                       or snapshot.get("paginationComplete") is not True
                       or snapshot.get("mappingComplete") is not True
                       or any(s.get("connected") is None or s.get("mapped") is False
                              for s in snapshot["sources"]))
            result.update(status="partial" if partial else "succeeded",
                          reason="source inventory or mapping is incomplete" if partial else None,
                          artifactSha256=digest(artifact_path.read_bytes()))
        except OSError as exc:
            result.update(status="failed", reason=f"artifact write failed: {exc.strerror or type(exc).__name__}")
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            result["reason"] = str(exc)
        write_atomic(receipt_path, (json.dumps(result, sort_keys=True, indent=2) + "\n").encode())
        return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--snapshot", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args()
    try:
        result = cycle(args.run_id, args.snapshot, args.out)
    except (OSError, ValueError) as exc:
        print(f"cycle: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "succeeded" else 3


if __name__ == "__main__":
    raise SystemExit(main())
