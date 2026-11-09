#!/usr/bin/env python3
"""Capture a confirmed workspace_manage(create_thread) result as private evidence."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import sys

try:
    from scripts import materialize, pilot
except ModuleNotFoundError:
    import materialize
    import pilot

HUB = pathlib.Path(__file__).resolve().parent.parent


def mounted_context(binding: dict) -> None:
    materialize.USER_ID = binding["OPERATOR_ACCOUNT_ID"]
    materialize.WORKSPACE_ID = binding["OPERATOR_WORKSPACE_ID"]
    installed = materialize.inventory(verify_content=True)
    knowledge, runbooks = materialize.workspace_attached_ids()
    for path, kind, folder in materialize.collect():
        collection = "runbooks" if kind == "runbook" else "notes"
        identity = (collection, f"watts/{folder}/{path.stem}")
        if identity not in installed or installed[identity] not in (runbooks if kind == "runbook" else knowledge):
            raise RuntimeError("hub context is not fully attached to the verified target workspace")


def capture(response: dict, binding: dict, repo: str, now: dt.datetime | None = None,
            mounted: bool = False) -> dict:
    if mounted is not True:
        raise ValueError("target workspace context has not been verified read-only")
    if (response.get("success") is not True
            or response.get("workspaceId") != binding["OPERATOR_WORKSPACE_ID"]
            or not isinstance(response.get("threadId"), str) or not response["threadId"]
            or not isinstance(response.get("id"), str) or not response["id"]):
        raise ValueError("native thread create response did not bind the target workspace")
    if not repo:
        raise ValueError("expected repository binding is missing")
    return {"ownerId": binding["OPERATOR_ACCOUNT_ID"],
            "workspaceId": binding["OPERATOR_WORKSPACE_ID"], "repo": repo,
            "threadId": response["threadId"], "ownerVerified": True,
            "workspaceBound": True, "contextMounted": True,
            "observedAt": (now or dt.datetime.now(dt.timezone.utc)).isoformat(),
            "nativeCreate": {key: response[key] for key in ("success", "workspaceId", "id", "threadId")}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host-response", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args()
    try:
        if (args.host_response.resolve().is_relative_to(HUB.resolve())
                or args.out.resolve().is_relative_to(HUB.resolve())):
            raise ValueError("native response and binding must stay private")
        response = json.loads(args.host_response.read_text(encoding="utf-8"))
        verified = pilot.identity()
        mounted_context(verified)
        binding = capture(response, verified, pilot.required("OPERATOR_REPO"), mounted=True)
        payload = (json.dumps(binding, indent=2, sort_keys=True) + "\n").encode()
        args.out.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        temporary = args.out.with_name(f".{args.out.name}.{os.getpid()}.tmp")
        with os.fdopen(os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), "wb") as stream:
            stream.write(payload)
        os.replace(temporary, args.out)
    except (OSError, ValueError, KeyError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"native binding: {exc}", file=sys.stderr)
        return 3
    print(json.dumps({"status": "captured", "sha256": hashlib.sha256(payload).hexdigest()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
