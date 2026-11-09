#!/usr/bin/env python3
"""Read-only audit of the configured owner's installed hub inventory."""
from __future__ import annotations

import json
import sys

import materialize
import pilot


def main() -> int:
    try:
        binding = pilot.identity()
        materialize.USER_ID = binding["OPERATOR_ACCOUNT_ID"]
        materialize.WORKSPACE_ID = binding["OPERATOR_WORKSPACE_ID"]
        inventory = materialize.inventory()
        knowledge, runbooks = materialize.workspace_attached_ids()
        expected = materialize.collect()
        missing = [f"watts/{folder}/{path.stem}" for path, kind, folder in expected
                   if (("runbooks" if kind == "runbook" else "notes"),
                       f"watts/{folder}/{path.stem}") not in inventory]
        unattached = [f"watts/{folder}/{path.stem}" for path, kind, folder in expected
                      if (identifier := inventory.get((("runbooks" if kind == "runbook" else "notes"),
                                                       f"watts/{folder}/{path.stem}")))
                      and identifier not in (runbooks if kind == "runbook" else knowledge)]
        known = set(inventory.values())
        other_attached = len((knowledge | runbooks) - known)
        print(json.dumps({"expected": len(expected), "installed": len(expected) - len(missing),
                          "missing": missing, "unattached": unattached,
                          "unknownAttachedIdCount": other_attached}, indent=2))
        return 1 if missing or unattached else 0
    except (RuntimeError, OSError) as exc:
        print(f"audit: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
