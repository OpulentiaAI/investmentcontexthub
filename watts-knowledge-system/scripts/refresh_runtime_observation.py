#!/usr/bin/env python3
"""Refresh read-only host capability metadata, never source payloads."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import sys

try:
    from scripts import pilot
except ModuleNotFoundError:
    import pilot

HUB = pathlib.Path(__file__).resolve().parent.parent


def write_private(path: pathlib.Path, data: dict) -> str:
    payload = (json.dumps(data, sort_keys=True, indent=2) + "\n").encode()
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with os.fdopen(os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), "wb") as stream:
        stream.write(payload)
    os.replace(temporary, path)
    return hashlib.sha256(payload).hexdigest()


def normalize_capabilities(rows: object, owner_id: str, workspace_id: str,
                           mapping: dict, observed_at: str) -> dict:
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("capability response is empty or malformed, not a verified zero")
    if (mapping.get("ownerId") != owner_id or mapping.get("workspaceId") != workspace_id
            or not isinstance(mapping.get("connections"), dict)):
        raise RuntimeError("source map is not scoped to the verified owner and workspace")
    sources = []
    seen_connections = set()
    seen_sources = set()
    mapping_complete = True
    for row in rows:
        if (not isinstance(row, dict) or not isinstance(row.get("providerId"), str)
                or not isinstance(row.get("connectionId"), str) or not row["connectionId"]
                or type(row.get("connected")) is not bool):
            raise RuntimeError("capability row lacks source identity or connection state")
        connection_id = row["connectionId"]
        if connection_id in seen_connections:
            raise RuntimeError("duplicate capability connection identity")
        seen_connections.add(connection_id)
        source_id = mapping["connections"].get(connection_id)
        mapped = (isinstance(source_id, str) and re.fullmatch(r"[a-z0-9-]+", source_id)
                  and source_id not in seen_sources)
        if not mapped:
            mapping_complete = False
            source_id = "unmapped-" + hashlib.sha256(connection_id.encode()).hexdigest()[:16]
        seen_sources.add(source_id)
        sources.append({"sourceId": source_id, "connected": row["connected"],
                        "mapped": bool(mapped), "connectionRefSha256": hashlib.sha256(connection_id.encode()).hexdigest()})
    return {"ownerId": owner_id, "workspaceId": workspace_id, "observedAt": observed_at,
            "ownerScopeVerified": True, "workspaceTargetVerified": True,
            "inventoryComplete": False, "paginationComplete": False,
            "mappingComplete": mapping_complete, "sources": sources}


def refresh(out: pathlib.Path, now: dt.datetime | None = None) -> dict:
    if out.resolve().is_relative_to(HUB.resolve()):
        raise RuntimeError("observation output must be private, outside this repository")
    binding = pilot.identity()
    rows = pilot.convex_read("mcpConnectors:listInstalledCapabilitiesInternal",
                             {"userId": binding["OPERATOR_ACCOUNT_ID"]},
                             pathlib.Path(pilot.required("OPULENT_FRONTEND")))
    at = (now or dt.datetime.now(dt.timezone.utc)).isoformat()
    map_path = pathlib.Path(pilot.required("OPERATOR_SOURCE_MAP")).resolve()
    if map_path.is_relative_to(HUB.resolve()):
        raise RuntimeError("source map must stay private")
    source_map = json.loads(map_path.read_text(encoding="utf-8"))
    source = normalize_capabilities(rows, binding["OPERATOR_ACCOUNT_ID"],
                                    binding["OPERATOR_WORKSPACE_ID"], source_map, at)
    out.mkdir(parents=True, exist_ok=True, mode=0o700)
    files = {
        "owner": {"ownerId": binding["OPERATOR_ACCOUNT_ID"], "observedAt": at,
                  "unique": True, "readOnly": True},
        "workspace": {"ownerId": binding["OPERATOR_ACCOUNT_ID"],
                      "workspaceId": binding["OPERATOR_WORKSPACE_ID"],
                      "observedAt": at, "unique": True},
        "sources": source,
    }
    hashes = {name: write_private(out / f"{name}.json", body) for name, body in files.items()}
    write_private(out / "observation-receipt.json", {
        "observedAt": at, "mode": "read-only-capability-metadata",
        "functions": ["userIdentityLinks:resolveOwnershipCandidatesInternal",
                      "workspaceEntities:listForAgentInternal",
                      "mcpConnectors:listInstalledCapabilitiesInternal"],
        "sha256": hashes, "sourceCount": len(source["sources"]),
    })
    return {"status": "partial",
            "sourceCount": len(source["sources"]), "sha256": hashes}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args()
    try:
        result = refresh(args.out)
    except (RuntimeError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"read-only observation: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
