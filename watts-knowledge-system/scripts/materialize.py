#!/usr/bin/env python3
"""
materialize.py — install this hub into Derrick Watts's Opulent account.

What it does
------------
1. Reads every markdown file in the hub's content directories.
2. Creates one Opulent *knowledge* row per file (folder = the hub directory).
   Files under runbooks/ are additionally created as *runbook* rows.
3. Attaches the created ids to the account's workspace so every Opulent session
   on this account sees the hub as context.

It is idempotent: a file whose `name` already exists is skipped, not duplicated.

Dry run (default):
    python3 scripts/materialize.py

Real install:
    CONFIRM=send python3 scripts/materialize.py --apply
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys

HUB = pathlib.Path(__file__).resolve().parent.parent
PILOT = HUB / "scripts" / "pilot.sh"
USER_ID = os.environ.get("OPERATOR_ACCOUNT_ID", "")
WORKSPACE_ID = os.environ.get("OPERATOR_WORKSPACE_ID", "")

# Directory -> how it should land in Opulent.
#   knowledge : always-available reference the agent can search
#   runbook   : an operating procedure the agent can execute
CONTENT_DIRS = {
    "entities": "knowledge",
    "entities/connectors": "knowledge",
    "signals": "knowledge",
    "pipelines": "knowledge",
    "automations": "knowledge",
    "workflows": "knowledge",
    "extractions": "runbook",
    "runbooks": "runbook",
    "catalogs": "knowledge",
    "research": "knowledge",
    "skills": "knowledge",
    "inject": "knowledge",
    "playbooks": "knowledge",
}


def is_watts_surface(path: pathlib.Path) -> bool:
    """ops/ never installs. Product files with surface: operator never install."""
    rel = path.relative_to(HUB).as_posix()
    if rel.startswith("ops/") or "/ops/" in rel:
        return False
    text = path.read_text(encoding="utf-8")
    if re.search(r"^surface:\s*[\"']?operator", text, re.M):
        return False
    return True


def pilot(mode: str, fn: str, args: dict) -> object:
    """Call production through the governed seam."""
    proc = subprocess.run(
        [str(PILOT), mode, fn, json.dumps(args)],
        capture_output=True,
        text=True,
        env={**os.environ},
    )
    if proc.returncode != 0:
        raise RuntimeError(f"{fn} failed (exit {proc.returncode})")
    body = proc.stdout.strip()
    if not body:
        if fn == "workspaceEntities:attachContextForAgentInternal":
            return None
        raise RuntimeError(f"{fn} returned an empty response")
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        if fn in ("knowledgeRunbooks:createKnowledge", "knowledgeRunbooks:createRunbook"):
            return body
        raise RuntimeError(f"{fn} returned a malformed response") from None


def inventory(verify_content: bool = False) -> dict[tuple[str, str], str]:
    rows_by_name: dict[tuple[str, str], str] = {}
    expected_content = {
        ("runbooks" if kind == "runbook" else "notes", f"watts/{folder}/{path.stem}"):
            path.read_text(encoding="utf-8") for path, kind, folder in collect()
    } if verify_content else {}
    for fn, collection, key in (
        ("knowledgeRunbooks:listKnowledge", "notes", "name"),
        ("knowledgeRunbooks:listRunbooks", "runbooks", "title"),
    ):
        res = pilot("read", fn, {"userId": USER_ID, "limit": 500})
        if not isinstance(res, dict) or not isinstance(res.get(collection), list):
            raise RuntimeError(f"{fn} returned an unexpected inventory shape")
        rows = res[collection]
        if (type(res.get("total")) is not int or type(res.get("truncated")) is not bool
                or res["truncated"] or res["total"] != len(rows) or len(rows) > 500):
            raise RuntimeError(f"{fn} inventory is incomplete or ambiguous")
        for r in rows:
            if (not isinstance(r, dict) or not isinstance(r.get(key), str)
                    or not r[key] or not isinstance(r.get("id"), str) or not r["id"]):
                raise RuntimeError(f"{fn} returned a malformed inventory row")
            identity = (collection, r[key])
            if identity in rows_by_name:
                raise RuntimeError(f"{fn} returned duplicate name {r[key]}")
            if identity in expected_content and r.get("content") != expected_content[identity]:
                raise RuntimeError("installed hub content is unavailable or differs from the current checkout")
            rows_by_name[identity] = r["id"]
    return rows_by_name


def workspace_attached_ids() -> tuple[set[str], set[str]]:
    fn = "workspaceEntities:listForAgentInternal"
    res = pilot("read", fn, {"userId": USER_ID})
    if not isinstance(res, dict) or not isinstance(res.get("workspaces"), list):
        raise RuntimeError(f"{fn} returned an unexpected workspace shape")
    if type(res.get("total")) is not int or res["total"] != len(res["workspaces"]):
        raise RuntimeError(f"{fn} returned an incomplete workspace inventory")
    matches = [w for w in res["workspaces"] if isinstance(w, dict) and w.get("workspaceId") == WORKSPACE_ID]
    if len(matches) != 1:
        raise RuntimeError(f"{fn} did not identify exactly one target workspace")
    workspace = matches[0]
    ids = []
    for field in ("attachedKnowledgeIds", "attachedRunbookIds"):
        values = workspace.get(field)
        if not isinstance(values, list) or any(not isinstance(v, str) or not v for v in values):
            raise RuntimeError(f"{fn} returned malformed {field}")
        ids.append(set(values))
    return ids[0], ids[1]


def created_id(fn: str, res: object) -> str:
    if isinstance(res, dict):
        if set(res) != {"id"}:
            raise RuntimeError(f"{fn} returned an ambiguous creation response")
        res = res.get("id")
    if not isinstance(res, str) or not res.strip():
        raise RuntimeError(f"{fn} did not return an unambiguous created id")
    return res.strip()


def collect() -> list[tuple[pathlib.Path, str, str]]:
    """Return (path, kind, folder) for every content file."""
    out = []
    for rel, kind in CONTENT_DIRS.items():
        d = HUB / rel
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            if not is_watts_surface(p):
                continue
            out.append((p, kind, rel.replace("/", "-")))
    start = HUB / "start here.md"
    if start.exists() and is_watts_surface(start):
        out.append((start, "knowledge", "root"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually write to production")
    args = ap.parse_args()

    apply = args.apply
    if apply and os.environ.get("CONFIRM") != "send":
        sys.stderr.write("refusing to install: re-run with CONFIRM=send\n")
        return 2
    if apply and (not USER_ID or not WORKSPACE_ID):
        sys.stderr.write("refusing to install: configure owner and workspace privately\n")
        return 2

    files = collect()
    print(f"hub files found : {len(files)}")

    if not apply:
        for path, kind, folder in files:
            content = path.read_text(encoding="utf-8")
            print(f"  [dry] {kind:8} watts/{folder}/{path.stem}  ({len(content)} bytes)")
        print("\ndry run only. Re-run with: CONFIRM=send python3 scripts/materialize.py --apply")
        return 0

    try:
        have = inventory()
        attached_knowledge, attached_runbooks = workspace_attached_ids()
        print(f"already installed: {len(have)}")
        missing = {"notes": 0, "runbooks": 0}
        for path, kind, folder in files:
            collection = "runbooks" if kind == "runbook" else "notes"
            if (collection, f"watts/{folder}/{path.stem}") not in have:
                missing[collection] += 1
        for collection, count in missing.items():
            if sum(kind == collection for kind, _ in have) + count > 500:
                raise RuntimeError(f"{collection} inventory would exceed the verified 500-row limit")
        desired_knowledge: set[str] = set()
        desired_runbooks: set[str] = set()
        created = False
        for path, kind, folder in files:
            title = f"watts/{folder}/{path.stem}"
            collection = "runbooks" if kind == "runbook" else "notes"
            identity = (collection, title)
            if identity not in have:
                content = path.read_text(encoding="utf-8")
                if kind == "runbook":
                    fn = "knowledgeRunbooks:createRunbook"
                    res = pilot("write", fn, {"userId": USER_ID, "title": title,
                                              "content": content, "source": "watts-context-hub"})
                else:
                    fn = "knowledgeRunbooks:createKnowledge"
                    res = pilot("write", fn, {"userId": USER_ID, "name": title,
                                              "content": content, "folder": f"watts/{folder}",
                                              "source": "watts-context-hub", "status": "active"})
                have[identity] = created_id(fn, res)
                created = True
                print(f"  [ok]  {kind:8} {title}")
            if kind == "runbook":
                desired_runbooks.add(have[identity])
            else:
                desired_knowledge.add(have[identity])

        if created:
            confirmed = inventory()
            if any(confirmed.get(identity) != ident for identity, ident in have.items()):
                raise RuntimeError("created rows could not be verified in inventory")

        if not desired_knowledge <= attached_knowledge or not desired_runbooks <= attached_runbooks:
            fn = "workspaceEntities:attachContextForAgentInternal"
            print("\nattaching to workspace", WORKSPACE_ID)
            response = pilot("write", fn, {
                "userId": USER_ID,
                "workspaceId": WORKSPACE_ID,
                "attachedKnowledgeIds": sorted(attached_knowledge | desired_knowledge),
                "attachedRunbookIds": sorted(attached_runbooks | desired_runbooks),
            })
            if response is not None:
                raise RuntimeError(f"{fn} returned an unexpected response")
            current_knowledge, current_runbooks = workspace_attached_ids()
            if not (desired_knowledge | attached_knowledge) <= current_knowledge or not (
                    desired_runbooks | attached_runbooks) <= current_runbooks:
                raise RuntimeError(f"{fn} did not attach all intended ids")
            print("attached. Re-run scripts/audit.sh to verify the expected hub rows and attachments.")
    except RuntimeError as exc:
        print(f"materialization incomplete: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
