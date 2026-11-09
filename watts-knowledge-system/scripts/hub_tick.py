#!/usr/bin/env python3
"""
hub_tick.py — static offline automation-policy inspection, not an executor.

It scans declared automation metadata and prompt verbs, recording *possible*
effects as blocked intents. It never mounts source data, starts a provider
session, checks actual cost authority, or proves a scheduled cycle ran.
An enabled tick is rejected because this repository has no general dispatcher.

    python3 scripts/hub_tick.py --automation watts-source-manifest-review
    python3 scripts/hub_tick.py --all --out /tmp/ticks
    python3 scripts/hub_tick.py --all --json        # machine-readable

Exit codes:
    0  every policy inspection completed with possible effects blocked
    1  an automation is enabled without a checked first open
    2  a side effect would have fired
    3  an automation could not run (missing precondition)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys

HUB = pathlib.Path(__file__).resolve().parent.parent
AUTOMATIONS = HUB / "automations"

SIDE_EFFECT_KINDS = ("send", "spend", "publish", "contact", "enable", "merge", "deploy")

# Actions the loop will never perform, keyed by the verb that would imply them.
EFFECT_VERBS = {
    "send": ["send outbound", "auto-send", "send the", "email the prospect", "inmail", "enable send"],
    "spend": ["purchase", "buy the", "spend", "pay for"],
    "publish": ["publish", "post publicly", "merge", "deploy"],
    "contact": ["contact them", "reach out to", "call the prospect"],
    "enable": ["enable the clock", "enable this", "turn on the automation"],
}


def parse_frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if line.startswith((" ", "-", "#")) or ":" not in line:
            continue
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip().strip('"')
    return out


def load_automations(hub: pathlib.Path) -> list[dict]:
    out = []
    for p in sorted((hub / "automations").glob("*.md")):
        text = p.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if fm.get("type") != "wks.automation":
            continue
        out.append({
            "path": p,
            "slug": fm.get("slug") or p.stem,
            "mode": fm.get("mode", ""),
            "enabled": (fm.get("enabled", "no") or "no").strip().lower(),
            "firstOpenChecked": (fm.get("firstOpenChecked", "no") or "no").strip().lower(),
            "confirmWord": fm.get("confirmWord", ""),
            "costCeilingUsd": fm.get("costCeilingUsd", ""),
            "producesArtifact": fm.get("producesArtifact", ""),
            "loopGuard": fm.get("loopGuard", ""),
            "text": text,
        })
    return out


def scan_effects(text: str) -> list[dict]:
    """Find prose that would imply a real-world effect, in the prompt block."""
    block = text
    m = re.search(r"```text\n(.*?)```", text, re.S)
    if m:
        block = m.group(1)
    found = []
    low = block.lower()
    for kind, verbs in EFFECT_VERBS.items():
        for verb in verbs:
            if verb in low:
                # A CAUTION line that forbids the verb is a guard, not an intent.
                for line in block.splitlines():
                    if verb in line.lower():
                        if line.strip().startswith("CAUTION") or "never" in line.lower():
                            continue
                        found.append({"kind": kind, "match": verb,
                                      "line": line.strip()[:120]})
                        break
    return found


def tick(automation: dict, hub: pathlib.Path) -> dict:
    """Run one automation's loop in dry-run. Returns a tick record."""
    slug = automation["slug"]
    record = {
        "slug": slug,
        "mode": automation["mode"],
        "enabled": automation["enabled"],
        "firstOpenChecked": automation["firstOpenChecked"],
        "dryRun": True,
        "preconditions": [],
        "artifact": None,
        "intents": [],
        "status": "ok",
    }

    # --- precondition: the loop guard must be satisfiable ---------------------
    if automation["loopGuard"]:
        today = dt.date.today().isoformat()
        artifact = (automation["producesArtifact"] or "").replace("<date>", today)
        record["artifact"] = artifact
        already = artifact and list(hub.glob(f"**/{artifact}"))
        if already:
            record["preconditions"].append({"check": "loopGuard", "ok": False,
                                            "note": f"{artifact} already exists; a tick would no-op"})
            record["status"] = "no-op"
            return record
        record["preconditions"].append({"check": "loopGuard", "ok": True,
                                        "note": f"no {artifact} present"})

    # --- precondition: coverage ledger ----------------------------------------
    manifests = list((hub / "entities").glob("*source-manifest*.md"))
    record["preconditions"].append({
        "check": "source-manifest",
        "ok": bool(manifests),
        "note": "present" if manifests else "absent — coverage claims are unbacked",
    })

    # --- precondition: nothing is enabled without a checked first open ---------
    if automation["enabled"] == "yes" and automation["firstOpenChecked"] != "yes":
        record["intents"].append({"kind": "enable", "disposition": "blocked",
                                  "reason": "enabled without a checked first open"})
        record["status"] = "violation"
        return record

    # --- side effects found in the prompt are recorded, never performed --------
    for effect in scan_effects(automation["text"]):
        record["intents"].append({
            "kind": effect["kind"],
            "disposition": "blocked",
            "reason": "dry-run: recorded as intent, not performed",
            "match": effect["match"],
        })

    if not record["intents"]:
        record["intents"].append({"kind": "none", "disposition": "blocked",
                                  "reason": "no side effect in this automation; reads only"})
    return record


def violations(automation: dict) -> str | None:
    if automation["enabled"] == "yes" and automation["firstOpenChecked"] != "yes":
        return (f"{automation['path'].name}: enabled without a checked first open")
    if automation["enabled"] == "yes":
        return (f"{automation['path'].name}: enabled without a local cost authorizer; "
                "this runner supports disabled drafts only")
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--automation", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--hub", type=pathlib.Path, default=None)
    ap.add_argument("--out", default=None, help="write tick receipts here")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    hub = args.hub or HUB
    automations = load_automations(hub)
    if args.automation:
        automations = [a for a in automations if a["slug"] == args.automation]
        if not automations:
            print(f"no automation with slug {args.automation!r}", file=sys.stderr)
            return 3
    elif not args.all:
        print("pass --automation <slug> or --all", file=sys.stderr)
        return 3

    # A violation is fatal before any tick runs.
    for a in automations:
        v = violations(a)
        if v:
            print(f"VIOLATION: {v}", file=sys.stderr)
            return 1

    ticks = [tick(a, hub) for a in automations]

    if args.out:
        out = pathlib.Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        for t in ticks:
            (out / f"{t['slug']}.tick.json").write_text(
                json.dumps(t, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps({"ticks": ticks}, indent=2))
    else:
        for t in ticks:
            blocked = [i for i in t["intents"] if i["disposition"] == "blocked"]
            print(f"{t['slug']:42} mode={t['mode']:16} status={t['status']:10} "
                  f"intents_blocked={len(blocked)} artifact={t['artifact'] or '-'}")
        total = sum(len(t["intents"]) for t in ticks)
        print(f"\n{len(ticks)} automation(s) ticked dry-run, {total} intent(s) recorded, "
              f"0 performed")

    # Fail closed: if any intent is not blocked, the loop did something real.
    unblocked = [i for t in ticks for i in t["intents"] if i["disposition"] != "blocked"]
    if unblocked:
        print(f"\nFAIL-CLOSED VIOLATION: {len(unblocked)} unblocked intent(s)", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
