#!/usr/bin/env python3
"""Export a disabled native message_session job; never call the provider."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys

try:
    from scripts.validate import parse_frontmatter
    from scripts.refresh_runtime_observation import write_private
except ModuleNotFoundError:
    from validate import parse_frontmatter
    from refresh_runtime_observation import write_private

HUB = pathlib.Path(__file__).resolve().parent.parent


def export(spec_path: pathlib.Path, binding_path: pathlib.Path, recurrence_path: pathlib.Path,
           expected: dict[str, str], now: dt.datetime | None = None) -> dict:
    if any(not isinstance(expected.get(key), str) or not expected[key].strip()
           for key in ("ownerId", "workspaceId", "repo")):
        raise ValueError("private owner/workspace/repo bindings required")
    if spec_path.resolve().parent != (HUB / "automations").resolve():
        raise ValueError("spec must be a canonical automation in this hub")
    if binding_path.resolve().is_relative_to(HUB.resolve()) or recurrence_path.resolve().is_relative_to(HUB.resolve()):
        raise ValueError("owner/thread and recurrence evidence must stay private")
    text = spec_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    slug = fm.get("slug", "")
    if fm.get("enabled") != "no" or not slug:
        raise ValueError("only disabled declared automations may be exported")
    if slug != "watts-source-manifest-review":
        raise ValueError("paid or unproven roles remain blocked until host pre-dispatch cost enforcement exists")
    schedule = re.search(r'^schedule:\n(?:  .*\n)*?  kind: (\w+)\n  expression: "([^"]+)"\n  timezone: ([^\n]+)', text, re.M)
    if not schedule or schedule.group(1) != "cron":
        raise ValueError("event triggers or malformed schedules require separate host validation")
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    recurrence = json.loads(recurrence_path.read_text(encoding="utf-8"))
    if not isinstance(binding, dict) or not isinstance(recurrence, dict):
        raise ValueError("binding and recurrence must be JSON objects")
    if not isinstance(binding.get("observedAt"), str):
        raise ValueError("binding must have an observation timestamp")
    observed = dt.datetime.fromisoformat(binding["observedAt"].replace("Z", "+00:00"))
    now = now or dt.datetime.now(dt.timezone.utc)
    if observed.tzinfo is None or not dt.timedelta(0) <= now - observed <= dt.timedelta(hours=24):
        raise ValueError("thread binding is stale or future-dated")
    if (binding.get("ownerId") != expected["ownerId"]
            or binding.get("workspaceId") != expected["workspaceId"]
            or binding.get("repo") != expected["repo"]
            or not isinstance(binding.get("threadId"), str) or not binding["threadId"]
            or binding.get("ownerVerified") is not True
            or binding.get("workspaceBound") is not True
            or binding.get("contextMounted") is not True
            or not isinstance(binding.get("nativeCreate"), dict)
            or binding["nativeCreate"].get("success") is not True
            or not isinstance(binding["nativeCreate"].get("id"), str)
            or not binding["nativeCreate"]["id"].strip()
            or binding["nativeCreate"].get("workspaceId") != expected["workspaceId"]
            or binding["nativeCreate"].get("threadId") != binding["threadId"]):
        raise ValueError("target thread owner/workspace/repository binding is unverified")
    if (recurrence.get("slug") != slug or recurrence.get("cron") != schedule.group(2)
            or recurrence.get("timezone") != schedule.group(3)
            or recurrence.get("hostParsedEquivalent") is not True
            or recurrence.get("approved") is not True
            or not isinstance(recurrence.get("rrule"), str)
            or not re.match(rf"^DTSTART;TZID={re.escape(schedule.group(3))}:\d{{8}}T\d{{6}}\nRRULE:",
                            recurrence["rrule"])
            or recurrence["rrule"].split("\n", 1)[0].endswith("Z")
            or "\nRRULE:" not in recurrence["rrule"]):
        raise ValueError("recurrence has not been host-parsed and approved against canonical schedule")
    block = re.search(r"```text\n(.*?)\n```", text, re.S)
    if not block or "CAUTION:" not in block.group(1):
        raise ValueError("canonical prompt is absent or unsafe")
    lines = [line for line in block.group(1).splitlines()
             if not line.startswith(("Create an Opulent automation", "Trigger:", "When the automation runs,"))]
    job = "\n".join(lines).strip()
    if "Create an Opulent automation" in job or "Trigger:" in job:
        raise ValueError("prompt still contains recursive automation instructions")
    prompt = (f"Role: {slug}. This is one no-paid metadata review, not a request to create, "
              "enable, or alter an automation. Paid external tools are disabled for this role.\n"
              f"At EVERY firing, before work or spend, read the host's current thread/workspace "
              f"identity and verify owner {expected['ownerId']}, workspace {expected['workspaceId']}, "
              f"and authorized source spec {expected['repo']} at current main or an approved revision. "
              "Use NATIVE READ-ONLY `workspace_manage(get)` for the exact target, "
              "`mesa_get_overview` for this thread's registered repository, and the host's "
              "read-only `list_integrations(filter=installed)` catalog projection. "
              "Save their unmodified results as private workspace.json, mesa.json and capabilities.json; "
              "save exact tool source refs as private source-refs.json and an owner-scoped "
              "connectionId-to-sourceId mapping as private source-map.json. Run "
              "`python3 scripts/ingest_native_observation.py --workspace-result <workspace.json> "
              "--mesa-result <mesa.json> --capabilities-result <capabilities.json> "
              "--source-refs <source-refs.json> --source-map <source-map.json> "
              "--out <private-observation-dir>` from an authorized copy of this hub. "
              "Set expected owner/workspace/repo privately. Use source ref "
              "`list_integrations:installed`; never invent an auth flag. The adapter "
              "validates those bytes and persists owner.json, "
              "workspace.json, sources.json and observation-receipt.json with SHA-256 digests. "
              "Do not request a deployment key, frontend checkout or operator CLI in this client job. "
              "Installed means configured OR connected; missing connection IDs, MCP catalog "
              "projection, and connected-app status cannot prove auth or full inventory. "
              "The review artifact and receipt remain PARTIAL, never FULL from this projection. "
              "If native owner/workspace or Mesa upstream cannot be verified, block. "
              "Refresh these observations automatically "
              "on the next firing; do not ask the owner to edit a date or reuse a stale intake. "
              "This is NOT authority to re-extract source data, run a paid preflight, or change any "
              "provider state. This source-review role cannot use paid external tools. "
              "Repository filters and saved attachments do not provision "
              "context. If identity/auth is expired, ambiguous, or an observation cannot be "
              "persisted, emit a blocked receipt in the bound thread and stop; never treat an "
              "empty response as zero. Unchanged healthy access continues. Only a validated "
              "artifact and successful run receipt close this role/input/cycle. Never send, "
              "publish, or enable.\n\n" + job)
    name_match = re.search(r'Create an Opulent automation named "([^"]+)"', block.group(1))
    if not name_match:
        raise ValueError("canonical automation name missing")
    return {"action": "create", "name": name_match.group(1), "enabled": False,
            "triggers": [{"event_type": "schedule:recurring", "conditions": {"any": [{"all": [
                {"field": "rrule", "operator": "recurrence", "value": recurrence["rrule"]}
            ]}]}, "replies": []}],
            "actions": [{"type": "message_session", "target_session_id": binding["threadId"],
                         "prompt": prompt}]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=pathlib.Path, required=True)
    parser.add_argument("--binding", type=pathlib.Path, required=True)
    parser.add_argument("--recurrence", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args()
    expected = {"ownerId": os.environ.get("OPERATOR_ACCOUNT_ID", ""),
                "workspaceId": os.environ.get("OPERATOR_WORKSPACE_ID", ""),
                "repo": os.environ.get("OPERATOR_REPO", "")}
    try:
        if not all(expected.values()) or args.out.resolve().is_relative_to(HUB.resolve()):
            raise ValueError("private owner/workspace/repo bindings and private output path required")
        body = export(args.spec, args.binding, args.recurrence, expected)
        args.out.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        write_private(args.out, body)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(f"native export: {exc}", file=sys.stderr)
        return 1
    print("disabled native payload exported privately; no provider operation performed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
