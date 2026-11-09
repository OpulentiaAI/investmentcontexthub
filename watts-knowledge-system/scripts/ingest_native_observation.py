#!/usr/bin/env python3
"""Validate raw read-only native results from an owner-bound session.

This consumes saved native tool results and source references, never calls a host API.
The public installed integration catalog cannot prove authentication or full inventory.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import sys
from urllib.parse import urlparse

try:
    from scripts.refresh_runtime_observation import HUB, write_private
except ModuleNotFoundError:
    from refresh_runtime_observation import HUB, write_private


def normalize_native_catalog(catalog: object, mapping: dict, owner_id: str,
                             workspace_id: str, observed_at: str) -> dict:
    if (not isinstance(catalog, dict) or catalog.get("success") is not True
            or any(not isinstance(catalog.get(key), list)
                   for key in ("integrations", "mcp_servers", "connected_apps"))):
        raise ValueError("native integration catalog result is incomplete or malformed")
    if (mapping.get("ownerId") != owner_id or mapping.get("workspaceId") != workspace_id
            or not isinstance(mapping.get("connections"), dict)):
        raise ValueError("source mapping does not match owner and workspace")
    sources = []
    seen_connections = set()
    seen_sources = set()
    mapping_complete = True
    for category, rows in (("integrations", catalog["integrations"]),
                           ("mcp_servers", catalog["mcp_servers"]),
                           ("connected_apps", catalog["connected_apps"])):
        for index, row in enumerate(rows):
            if (not isinstance(row, dict) or not isinstance(row.get("slug"), str)
                    or not row["slug"] or row.get("installed") is not True):
                raise ValueError("installed native catalog row lacks a stable slug or installed metadata")
            refs = row.get("connection_ids") if category == "integrations" else None
            if refs is not None and (not isinstance(refs, list)
                                     or any(not isinstance(ref, str) or not ref for ref in refs)):
                raise ValueError("native integration connection IDs are malformed")
            if not refs:
                mapping_complete = False
                refs = [None]
            for ref in refs:
                if ref is not None:
                    if ref in seen_connections:
                        raise ValueError("native integration connection identity repeated")
                    seen_connections.add(ref)
                identity = ref if ref is not None else f"catalog:{category}:{index}:{row['slug']}"
                source_id = mapping["connections"].get(ref) if ref is not None else None
                mapped = (isinstance(source_id, str) and source_id not in seen_sources
                          and source_id and all(c.islower() or c.isdigit() or c == "-" for c in source_id))
                if not mapped:
                    mapping_complete = False
                    source_id = "unmapped-" + hashlib.sha256(identity.encode()).hexdigest()[:16]
                seen_sources.add(source_id)
                sources.append({"sourceId": source_id, "mapped": bool(mapped),
                                "connected": None, "reach": "unknown",
                                "connectionRefSha256": hashlib.sha256(identity.encode()).hexdigest()})
    if not sources:
        raise ValueError("native integration catalog is empty, not a verified zero")
    return {"ownerId": owner_id, "workspaceId": workspace_id, "observedAt": observed_at,
            "ownerScopeVerified": True, "workspaceTargetVerified": True,
            "inventoryComplete": False, "paginationComplete": False,
            "mappingComplete": mapping_complete, "sources": sources}


def ingest(workspace: object, mesa: object, capabilities: object, source_refs: dict,
           mapping: dict, owner_id: str, workspace_id: str, expected_repo: str,
           observed_at: str) -> dict:
    if (source_refs.get("workspace") != "workspace_manage:get"
            or source_refs.get("mesa") != "mesa_get_overview"
            or source_refs.get("capabilities") != "list_integrations:installed"):
        raise ValueError("native tool source references are missing or do not match verified read-only tools")
    if not isinstance(workspace, dict) or workspace.get("success") is not True:
        raise ValueError("native workspace get did not succeed")
    target = workspace.get("workspace")
    if (not isinstance(target, dict) or target.get("workspaceId") != workspace_id
            or target.get("userId") != owner_id):
        raise ValueError("native workspace result does not prove exact owner and target")
    if (not isinstance(mesa, dict) or mesa.get("success") is not True or mesa.get("truncated") is not False
            or not isinstance(mesa.get("repo_id"), str) or not mesa["repo_id"]
            or not isinstance(mesa.get("data"), dict)):
        raise ValueError("native Mesa result is incomplete or lacks a registered repository")
    repo = mesa["data"]
    if not isinstance(repo.get("id"), str) or repo["id"] != mesa["repo_id"]:
        raise ValueError("Mesa repository identity is inconsistent")
    upstream = repo.get("upstream")
    owner, separator, name = expected_repo.partition("/")
    if not separator or not owner or not name:
        raise ValueError("expected repository must be owner/repo")
    if isinstance(upstream, dict) and isinstance(upstream.get("url"), str):
        parsed_url = urlparse(upstream["url"])
        path = parsed_url.path.strip("/").removesuffix(".git")
        repo_matches = (parsed_url.scheme == "https" and parsed_url.hostname == "github.com"
                        and not parsed_url.username and not parsed_url.password
                        and path.lower() == expected_repo.lower())
    else:
        repo_matches = False
    if not repo_matches:
        raise ValueError("thread-scoped Mesa repository does not match expected owner/repo")
    snapshot = normalize_native_catalog(capabilities, mapping, owner_id, workspace_id, observed_at)
    return {"owner": {"ownerId": owner_id, "observedAt": observed_at, "unique": True, "readOnly": True},
            "workspace": {"ownerId": owner_id, "workspaceId": workspace_id,
                          "observedAt": observed_at, "unique": True},
            "sources": snapshot, "mesaRepoRefSha256": hashlib.sha256(mesa["repo_id"].encode()).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-result", type=pathlib.Path, required=True)
    parser.add_argument("--mesa-result", type=pathlib.Path, required=True)
    parser.add_argument("--capabilities-result", type=pathlib.Path, required=True)
    parser.add_argument("--source-refs", type=pathlib.Path, required=True)
    parser.add_argument("--source-map", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args()
    inputs = (args.workspace_result, args.mesa_result, args.capabilities_result,
              args.source_refs, args.source_map)
    owner_id = os.environ.get("OPERATOR_ACCOUNT_ID", "")
    workspace_id = os.environ.get("OPERATOR_WORKSPACE_ID", "")
    expected_repo = os.environ.get("OPERATOR_REPO", "")
    try:
        if (not owner_id or not workspace_id or not expected_repo
                or any(p.resolve().is_relative_to(HUB.resolve()) for p in (*inputs, args.out))):
            raise ValueError("private owner/workspace/repository bindings and private result paths required")
        raw = [path.read_bytes() for path in inputs]
        at = dt.datetime.now(dt.timezone.utc).isoformat()
        record = ingest(*(json.loads(blob) for blob in raw), owner_id, workspace_id, expected_repo, at)
        args.out.mkdir(parents=True, exist_ok=True, mode=0o700)
        hashes = {key: write_private(args.out / f"{key}.json", record[key])
                  for key in ("owner", "workspace", "sources")}
        write_private(args.out / "observation-receipt.json", {
            "mode": "read-only-capability-metadata", "observedAt": at,
            "sourceRefs": {name: {"tool": json.loads(raw[3])[name],
                                  "rawSha256": hashlib.sha256(blob).hexdigest()}
                           for name, blob in zip(("workspace", "mesa", "capabilities"), raw[:3])},
            "sourceMapSha256": hashlib.sha256(raw[4]).hexdigest(),
            "mesaRepoRefSha256": record["mesaRepoRefSha256"], "sha256": hashes,
        })
    except (OSError, ValueError, KeyError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"native ingestion: {exc}", file=sys.stderr)
        return 3
    print(json.dumps({"status": "partial",
                      "sha256": hashes}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
