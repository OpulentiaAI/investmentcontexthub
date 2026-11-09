#!/usr/bin/env python3
"""Operator-configured Convex command seam; no account or deployment defaults."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import pathlib
import subprocess
import sys

READ_ONLY_FUNCTIONS = frozenset({
    "userIdentityLinks:resolveOwnershipCandidatesInternal",
    "workspaceEntities:listForAgentInternal",
    "mcpConnectors:listInstalledCapabilitiesInternal",
    "triggers:listAutomationsInternal",
    "knowledgeRunbooks:listKnowledge",
    "knowledgeRunbooks:listRunbooks",
})
WRITE_FUNCTIONS = frozenset({
    "knowledgeRunbooks:createKnowledge",
    "knowledgeRunbooks:createRunbook",
    "workspaceEntities:attachContextForAgentInternal",
})


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} must be configured privately")
    return value


def convex_read(function: str, args: dict, frontend: pathlib.Path) -> object:
    if function not in READ_ONLY_FUNCTIONS:
        raise RuntimeError("preflight function is not known read-only")
    result = subprocess.run(["npx", "--no-install", "convex", "run", function,
                             json.dumps(args, separators=(",", ":")), "--prod"],
                            cwd=frontend, capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise RuntimeError(f"read-only {function} probe failed")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"read-only {function} probe returned malformed JSON") from exc


def identity() -> dict:
    configured = {key: required(key) for key in (
        "OPERATOR_ACCOUNT_ID", "OPERATOR_EMAIL", "OPERATOR_WORKSPACE_ID", "OPERATOR_DEPLOYMENT"
    )}
    frontend = pathlib.Path(required("OPULENT_FRONTEND"))
    if not frontend.is_dir():
        raise RuntimeError("configured frontend is unavailable")
    if os.environ.get("CONVEX_DEPLOYMENT") != configured["OPERATOR_DEPLOYMENT"]:
        raise RuntimeError("active deployment differs from configured deployment")
    if not os.environ.get("CONVEX_DEPLOY_KEY"):
        raise RuntimeError("private Convex deployment credential is unavailable")
    deploy_file = frontend / ".env.deploy"
    if not deploy_file.is_file():
        raise RuntimeError("configured frontend has no private deployment file")
    deployment_lines = [line.partition("=")[2].strip().strip('"').strip("'")
                        for line in deploy_file.read_text(encoding="utf-8").splitlines()
                        if line.startswith("CONVEX_DEPLOYMENT=")]
    if deployment_lines != [configured["OPERATOR_DEPLOYMENT"]]:
        raise RuntimeError("frontend deployment differs from configured target")
    owner = convex_read("userIdentityLinks:resolveOwnershipCandidatesInternal",
                        {"email": configured["OPERATOR_EMAIL"]}, frontend)
    if (not isinstance(owner, dict) or owner.get("canonicalUserId") != configured["OPERATOR_ACCOUNT_ID"]
            or not isinstance(owner.get("emails"), list)
            or configured["OPERATOR_EMAIL"].lower() not in [str(e).lower() for e in owner["emails"]]):
        raise RuntimeError("owner resolution did not uniquely match configured owner and email")
    workspaces = convex_read("workspaceEntities:listForAgentInternal",
                             {"userId": configured["OPERATOR_ACCOUNT_ID"]}, frontend)
    if (not isinstance(workspaces, dict) or type(workspaces.get("total")) is not int
            or not isinstance(workspaces.get("workspaces"), list)
            or workspaces["total"] != len(workspaces["workspaces"])):
        raise RuntimeError("target workspace inventory is incomplete or malformed")
    matches = [w for w in workspaces["workspaces"] if isinstance(w, dict)
               and w.get("workspaceId") == configured["OPERATOR_WORKSPACE_ID"]
               and w.get("userId") == configured["OPERATOR_ACCOUNT_ID"]]
    if len(matches) != 1:
        raise RuntimeError("target workspace was not uniquely bound to configured owner")
    return configured


def run(mode: str, function: str, payload: str) -> str:
    if mode not in ("read", "write"):
        raise RuntimeError("usage: pilot.sh read|write <function> '<json>'")
    try:
        args = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError("arguments must be valid JSON") from exc
    if not isinstance(args, dict):
        raise RuntimeError("arguments must be a JSON object")
    read_functions = {value.strip() for value in required("OPERATOR_READ_FUNCTIONS").split(",") if value.strip()}
    write_functions = {value.strip() for value in required("OPERATOR_WRITE_FUNCTIONS").split(",") if value.strip()}
    if read_functions & write_functions:
        raise RuntimeError("read/write function allowlists overlap")
    allowed = read_functions if mode == "read" else write_functions
    if not read_functions <= READ_ONLY_FUNCTIONS or not write_functions <= WRITE_FUNCTIONS:
        raise RuntimeError("private function allowlist contains a function with the wrong access mode")
    if function not in allowed or not function or function.strip() != function:
        raise RuntimeError("function is not explicitly allowlisted for this mode")
    if mode == "write" and os.environ.get("CONFIRM") != "send":
        raise RuntimeError("refusing write without CONFIRM=send")
    ledger = pathlib.Path(required("OPERATOR_LEDGER"))
    repo = pathlib.Path(__file__).resolve().parent.parent
    if (repo / ".git").exists() and ledger.resolve().is_relative_to(repo):
        raise RuntimeError("private operator ledger cannot be in this repository")
    binding = identity()
    if args.get("userId") != binding["OPERATOR_ACCOUNT_ID"]:
        raise RuntimeError("operation is not scoped to the verified owner")
    if "workspaceId" in args and args["workspaceId"] != binding["OPERATOR_WORKSPACE_ID"]:
        raise RuntimeError("operation targets another workspace")
    command = ["npx", "--no-install", "convex", "run", function, json.dumps(args, separators=(",", ":")), "--prod"]
    ledger.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with os.fdopen(os.open(ledger, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600), "a", encoding="utf-8") as stream:
        result = subprocess.run(command, cwd=required("OPULENT_FRONTEND"), capture_output=True, text=True, timeout=120)
        stream.write(json.dumps({
            "at": dt.datetime.now(dt.timezone.utc).isoformat(), "mode": mode, "function": function,
            "argsSha256": hashlib.sha256(payload.encode()).hexdigest(), "argsBytes": len(payload.encode()),
            "fn": function,
            "deployment": binding["OPERATOR_DEPLOYMENT"], "exit": result.returncode,
        }) + "\n")
    if result.returncode:
        raise RuntimeError(f"{function} failed (exit {result.returncode}); inspect private ledger")
    return "\n".join(line for line in result.stdout.splitlines() if not line.startswith(
        ("ExperimentalWarning", "Ignoring `--prod`")))


def main() -> int:
    try:
        if len(sys.argv) not in (3, 4):
            raise RuntimeError("usage: pilot.sh read|write <function> '<json>'")
        print(run(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "{}"), end="")
        return 0
    except (RuntimeError, subprocess.TimeoutExpired, OSError) as exc:
        print(f"pilot: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
