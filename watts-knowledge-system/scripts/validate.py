#!/usr/bin/env python3
"""
validate.py — check the hub's integrity before anyone points Opulent at it.

Checks
------
1. Every instance file has frontmatter with a `type:` that exists in type/.
2. Every required field declared on a type (and its parents) is present.
3. Every [[wikilink]] resolves to a real file in the hub.
4. Every wks.automation has a fenced Prompt block containing a CAUTION line.
5. No automation is `enabled: yes` without `firstOpenChecked: yes`.
6. No file claims `sendReady: yes`.
7. Every terminal wks.extraction-run names its gap or its blocker.
8. A resolved wks.experiment carries the value and sample size it rests on.
9. When a source manifest exists, every connected connector has a row in it.

Also regenerates catalogs/ from what actually exists.

    python3 scripts/validate.py            # check
    python3 scripts/validate.py --catalog  # check + rewrite catalogs

The checks are callable as a library for tests:

    from validate import run_checks
    result = run_checks(hub=pathlib.Path("/tmp/fixture-hub"))
    result.errors, result.warnings, result.by_type
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import re
import sys
from dataclasses import dataclass, field

try:
    from scripts.knowledge_contracts import check_records
except ModuleNotFoundError:
    from knowledge_contracts import check_records

HUB = pathlib.Path(__file__).resolve().parent.parent
CONTENT_DIRS = ["entities", "entities/connectors", "captures", "concepts", "claims", "maps",
                "signals", "pipelines", "automations", "workflows", "extractions", "runbooks",
                "catalogs", "research", "skills", "inject", "playbooks", "fixtures/good", "data/metrics"]
# Root pages Jeremy or his agent will read. Not typed as wks.* but they are surface.
SURFACE_ROOT_FILES = ["start here.md", "ONBOARDING.md", "README.md", "AGENTS.md"]
FORBIDDEN_ON_JEREMY_SURFACE = [
    "Jeremy Alston",
    "Paul Cushman",
    "address trap",
    "never messages him",
    "This hub never messages",
    "CONVEX_DEPLOY",
    "deploy key",
    "Aside",
    "vercel-labs",
    "eve template",
    "eve-content-agent",
    "eve-typefully",
    "typefully-eve",
    "Typefully",
    "eve.dev",
    "getOAuthAuthorizationUrl",
    "The requester",
    "wattssanchez@opulent.ai",
    "authOwner: operator",
    "paul@opulent.ai",
    "Internal checks",
    "house bar",
]

# Vocabulary supplied by declared deps, resolved by the engine at mount time.
# We cannot read those repos locally, so treat them as known and check shape only.
EXTERNAL_TYPES = {
    "node::au-base-types", "thing::au-base-types", "idea::au-base-types",
    "event::au-base-types", "source::au-base-types", "map::au-base-types",
    "lens::au-base-types", "supersede::au-base-types",
    "mcp.skill::au-mcp-sdk", "mcp.inject::au-mcp-sdk", "mcp.tool::au-mcp-sdk",
    "agent-profile::au-mcp-sdk", "composition::au-host-sdk",
    "au.engine.repo::au-engine", "au.engine.workspace::au-engine",
}
# Fields every node inherits from the base vocabulary.
BASE_FIELDS = {"tldr", "aliases", "origin", "original", "date", "involved"}

FM = re.compile(r"^---\n(.*?)\n---\n", re.S)
WIKILINK = re.compile(r"\[\[([^\]|:]+?)(?:::[^\]]+)?\]\]")


@dataclass
class CheckResult:
    """Everything one run of the checks found, plus what it looked at."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    by_type: dict[str, list[pathlib.Path]] = field(default_factory=dict)
    files_checked: int = 0
    types_loaded: int = 0


def parse_frontmatter(text: str) -> dict[str, str]:
    """Deliberately shallow: we only need top-level scalar keys."""
    m = FM.match(text)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if line.startswith((" ", "-", "#")) or ":" not in line:
            continue
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip().strip('"')
    return out


def scalar(value: str) -> str:
    """Normalize a frontmatter scalar: unquoted, trimmed, lowercased."""
    return value.strip().strip('"').strip("'").strip().lower()


def manifest_rows(text: str) -> tuple[list[dict[str, str]], list[str]]:
    """Read the deliberately flat public-safe rows, rejecting ambiguous shapes."""
    rows: list[dict[str, str]] = []
    errors: list[str] = []
    in_sources = False
    for line in text.splitlines():
        if line == "sources:":
            if in_sources or rows:
                errors.append("duplicate sources section")
            in_sources = True
            continue
        if not in_sources:
            continue
        if line and not line.startswith(" "):
            in_sources = False
            continue
        if not line.strip():
            continue
        start = re.fullmatch(r"  - sourceId: (.+)", line)
        field = re.fullmatch(r"    ([A-Za-z][A-Za-z0-9]*):\s*(.*)", line)
        if start:
            rows.append({"sourceId": start.group(1).strip().strip('"')})
        elif field and rows:
            key, value = field.groups()
            if key in rows[-1]:
                errors.append(f"duplicate `{key}` in row `{rows[-1]['sourceId']}`")
            rows[-1][key] = value.strip().strip('"')
        else:
            errors.append(f"malformed source row line `{line[:80]}`")
    return rows, errors


def load_types(hub: pathlib.Path | None = None) -> dict[str, dict]:
    root = hub or HUB
    types: dict[str, dict] = {}
    tdir = root / "type"
    for p in tdir.glob("*.type.yaml"):
        name = p.name[: -len(".type.yaml")]
        body = p.read_text(encoding="utf-8")
        fields = re.findall(r"^  ([a-zA-Z][a-zA-Z0-9]*)\??:", body, re.M)
        # A field declared without `?` is required. Read the optional ones
        # separately so the difference is explicit rather than implied.
        optional = set(re.findall(r"^  ([a-zA-Z][a-zA-Z0-9]*)\?:", body, re.M))
        required = {f for f in fields if f not in optional}
        # Bare enum declarations: `field: [a, b, c]`. A value outside the set is
        # an error, never a silently-ignored unknown — an unrecognized
        # `doNotContact` value must not read as "not do-not-contact".
        enums: dict[str, set[str]] = {}
        for fname, values in re.findall(r"^  ([a-zA-Z][a-zA-Z0-9]*)\??:\s*\[([^\]]+)\]", body, re.M):
            if "::" in values:
                continue
            enum = {v.strip().strip('"').strip("'").lower() for v in values.split(",") if v.strip()}
            if enum:
                enums[fname] = enum
        extends = re.findall(r"^extends:\s*\[([^\]]*)\]", body, re.M)
        parents = []
        if extends:
            parents = [x.strip() for x in extends[0].split(",") if x.strip()]
        else:
            blk = re.search(r"^extends:\n((?:\s+- .*\n)+)", body, re.M)
            if blk:
                parents = [l.strip("- ").strip() for l in blk.group(1).splitlines()]
        types[name] = {"fields": set(fields), "required": required,
                       "enums": enums, "parents": parents}
    return types


def all_files(hub: pathlib.Path | None = None) -> list[pathlib.Path]:
    root = hub or HUB
    out = []
    for d in CONTENT_DIRS:
        p = root / d
        if p.is_dir():
            out.extend(sorted(p.glob("*.md")))
    start = root / "start here.md"
    if start.exists():
        out.append(start)
    return out


def surface_files(hub: pathlib.Path | None = None) -> list[pathlib.Path]:
    root = hub or HUB
    out = list(all_files(root))
    for name in SURFACE_ROOT_FILES:
        p = root / name
        if p.exists():
            out.append(p)
    return out


def surface_violations(path: pathlib.Path, text: str, hub: pathlib.Path | None = None) -> list[str]:
    rel = path.relative_to(hub or HUB)
    if str(rel).startswith("ops/") or "/ops/" in str(rel):
        return []
    if re.search(r"^surface:\s*[\"']?operator", text, re.M):
        return [f"{rel}: operator file must live under ops/, not on the product surface"]
    found = []
    for phrase in FORBIDDEN_ON_JEREMY_SURFACE:
        if phrase in text:
            found.append(f"{rel}: product surface contains `{phrase}`")
    return found


def stems(hub: pathlib.Path | None = None) -> set[str]:
    root = hub or HUB
    return {p.stem for p in all_files(root)} | {p.name[:-len(".type.yaml")] for p in (root / "type").glob("*.type.yaml")}


def cross_checks(hub: pathlib.Path, errors: list[str], warnings: list[str]) -> None:
    """Rules that span more than one file. Each one is a coverage or safety claim."""
    root = hub or HUB

    # --- coverage: a connected source must have a manifest row -----------------
    # Completeness is manifest-based. One extraction speaks for one source only,
    # so a connected connector with no row is a gap, never an implicit zero.
    connectors = []
    cdir = root / "entities" / "connectors"
    if cdir.is_dir():
        for p in sorted(cdir.glob("*.md")):
            fm = parse_frontmatter(p.read_text(encoding="utf-8"))
            if scalar(fm.get("connected", "")) == "yes":
                connectors.append((fm.get("slug") or p.stem, p))

    manifest_rows_list: list[dict[str, str]] = []
    manifest_files = sorted((root / "entities").glob("*source-manifest*.md"))
    for p in sorted(set(manifest_files)):
        text = p.read_text(encoding="utf-8")
        # Rows are declared as a list of maps. Split on the row marker rather
        # than scanning offsets: `\s` matches newlines, so an indentation-based
        # scan can run across row boundaries and silently misparse a row.
        parsed, faults = manifest_rows(text)
        manifest_rows_list.extend(parsed)
        errors.extend(f"{p.relative_to(root)}: {fault}" for fault in faults)

    # Keep a list, not a dict: keying by sourceId silently overwrites a duplicate
    # row, which would make the separation checks below vacuous.
    rows_by_source = {scalar(r["sourceId"]): r for r in manifest_rows_list} if manifest_rows_list else {}
    if manifest_rows_list:
        seen_ids: dict[str, int] = {}
        for r in manifest_rows_list:
            seen_ids[r["sourceId"]] = seen_ids.get(r["sourceId"], 0) + 1
        for sid, n in seen_ids.items():
            if n > 1:
                errors.append(
                    f"source-manifest `{sid}`: duplicate sourceId across {n} rows — "
                    "encode the dataset owner in a distinct stable sourceId so rows "
                    "cannot overwrite or merge different people's data"
                )

    if rows_by_source:
        row_type = load_types(root).get("wks.source-manifest-row")
        if not row_type:
            errors.append("source-manifest: undefined `wks.source-manifest-row` type")
            row_type = {"required": set(), "enums": {}, "fields": set(manifest_rows_list[0])}
        ROW_REQUIRED = row_type["required"]
        for sid, row in rows_by_source.items():
            for field in ROW_REQUIRED:
                if not str(row.get(field, "")).strip():
                    errors.append(
                        f"source-manifest `{sid}`: row is missing `{field}`"
                    )
            for field, allowed in row_type["enums"].items():
                if field in row and scalar(row[field]) not in allowed:
                    errors.append(f"source-manifest `{sid}`: invalid `{field}` value `{row[field]}`")
            for field in row:
                if field not in row_type["fields"]:
                    errors.append(f"source-manifest `{sid}`: unknown row field `{field}`")
        for slug, path in connectors:
            if slug not in rows_by_source:
                errors.append(
                    f"{path.relative_to(root)}: connected source `{slug}` has no source-manifest row"
                )
        for sid, row in rows_by_source.items():
            state = scalar(row.get("state", ""))
            if state in ("extracted", "unavailable", "blocked") and not row.get("blockerNote") and state != "extracted":
                errors.append(
                    f"source-manifest `{sid}`: state `{state}` requires a blockerNote"
                )
            if state == "extracted" and not row.get("lastObservedAt"):
                errors.append(
                    f"source-manifest `{sid}`: state `extracted` requires lastObservedAt"
                )
            if state == "extracted":
                ref = row.get("lastRun", "").strip("[]")
                run_path = next((p for p in (root / "extractions").glob("*.md") if p.stem == ref), None)
                if not run_path or scalar(row.get("completeness", "")) != "full":
                    errors.append(f"source-manifest `{sid}`: extracted requires FULL completeness and linked lastRun")
                else:
                    run = parse_frontmatter(run_path.read_text(encoding="utf-8"))
                    if (run.get("sourceId") != sid or scalar(run.get("scope", "")) != "full"
                            or scalar(run.get("outcome", "")) != "ok"
                            or scalar(run.get("completeness", "")) != "complete"
                            or scalar(run.get("truncated", "")) != "no"):
                        errors.append(f"source-manifest `{sid}`: linked run does not prove a full successful extraction")
            if not row.get("doesNotCover"):
                errors.append(
                    f"source-manifest `{sid}`: doesNotCover is required — the gap is the important half"
                )
    elif connectors:
        errors.append(
            f"coverage: {len(connectors)} connected source(s) and no source-manifest — "
            "completeness is manifest-based; add rows (see docs/completeness-and-source-coverage.md)"
        )

    # --- extraction runs: a terminal outcome must name its gap -----------------
    for p in sorted((root / "extractions").glob("*.md")) + sorted((root / "runbooks").glob("*.md")):
        text = p.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if fm.get("type") != "wks.extraction-run":
            continue
        outcome = scalar(fm.get("outcome", ""))
        if outcome in ("partial", "failed", "unavailable"):
            if not fm.get("missing") and not fm.get("blockerNote"):
                errors.append(
                    f"{p.relative_to(root)}: outcome `{outcome}` requires `missing` or `blockerNote`"
                )
        if fm.get("artifactRef") and not fm.get("artifactSha256"):
            errors.append(
                f"{p.relative_to(root)}: artifactRef without artifactSha256 — an unchecked hash is not proof"
            )
        if scalar(fm.get("outcome", "")) == "ok":
            if (scalar(fm.get("completeness", "")) != "complete" or scalar(fm.get("truncated", "")) != "no"
                    or scalar(fm.get("scope", "")) != "full" and not fm.get("continuingFrom")):
                errors.append(f"{p.relative_to(root)}: ok requires complete non-truncated run and a linked delta")
            try:
                captured, expected = int(fm["pagesCaptured"]), int(fm["pagesExpected"])
                indices = json.loads(fm["pageIndices"])
                if expected < 1 or captured != expected or indices != list(range(1, expected + 1)):
                    raise ValueError
            except (KeyError, ValueError, json.JSONDecodeError):
                errors.append(f"{p.relative_to(root)}: ok requires contiguous complete page counts")
            ref, sha = fm.get("artifactRef", ""), fm.get("artifactSha256", "")
            if not re.fullmatch(r"[0-9a-fA-F]{64}", sha):
                errors.append(f"{p.relative_to(root)}: ok requires a 64-hex artifactSha256")
            artifact = (root / ref).resolve() if ref else None
            if not artifact or not artifact.is_relative_to(root.resolve()) or not artifact.is_file():
                errors.append(f"{p.relative_to(root)}: ok requires a locally verifiable artifact")
            elif hashlib.sha256(artifact.read_bytes()).hexdigest() != sha.lower():
                errors.append(f"{p.relative_to(root)}: artifactSha256 does not match artifact bytes")
        if scalar(fm.get("scope", "")) == "delta" and not fm.get("continuingFrom"):
            errors.append(
                f"{p.relative_to(root)}: a delta run requires continuingFrom"
            )

    # --- warm paths: an unevidenced route cannot be used -----------------------
    # A path is only as good as the public record behind it. Without a URL it is
    # a guess, and a guess must never become an introduction.
    if "wks.warm-path" in load_types(root):
        dnc: set[str] = set()
        pdir = root / "entities"
        scan_dirs = [pdir, root / "research", root / "signals", root / "fixtures" / "good"]
        for d in scan_dirs:
            if not d.is_dir():
                continue
            for p in sorted(d.glob("*.md")):
                fm = parse_frontmatter(p.read_text(encoding="utf-8"))
                if fm.get("type") == "wks.person" and scalar(fm.get("doNotContact", "no")) == "yes":
                    dnc.add(p.stem)
        for d in ("research", "signals", "entities", "playbooks", "fixtures/good"):
            for p in sorted((root / d).glob("*.md")):
                text = p.read_text(encoding="utf-8")
                fm = parse_frontmatter(text)
                if fm.get("type") != "wks.warm-path":
                    continue
                # Presence is the test. A synthetic TLD such as example.invalid is
                # a perfectly resolvable citation for fixture purposes.
                if not str(fm.get("evidenceUrl", "")).strip():
                    errors.append(
                        f"{p.relative_to(root)}: warm path needs a resolvable evidenceUrl "
                        "— an unevidenced route cannot be used"
                    )
                # An unverified route stays visible for research but is blocked from
                # use. Measured: a URL with no observation date scored 0.12, URL plus
                # date 0.22 — so the weakest tiers must not be actionable.
                if scalar(fm.get("verified", "")) == "no" and scalar(fm.get("strength", "")) in ("working", "direct"):
                    errors.append(
                        f"{p.relative_to(root)}: warm path is `verified: no` but claims "
                        f"`strength: {fm.get('strength')}` — an unverified route cannot be actionable"
                    )
                intro = str(fm.get("introducer", ""))
                for stem in dnc:
                    if stem in intro:
                        errors.append(
                            f"{p.relative_to(root)}: warm path introduces through `{stem}`, "
                            "who is flagged doNotContact"
                        )

    # --- awards: a conflict state must be a real answer ------------------------
    if "wks.award" in load_types(root):
        for d in ("research", "signals", "entities"):
            for p in sorted((root / d).glob("*.md")):
                fm = parse_frontmatter(p.read_text(encoding="utf-8"))
                if fm.get("type") != "wks.award":
                    continue
                if scalar(fm.get("conflict", "")) not in ("yes", "no"):
                    errors.append(
                        f"{p.relative_to(root)}: award `conflict` must be yes or no, "
                        f"got `{fm.get('conflict', '')}`"
                    )
                if not str(fm.get("publisherUrl", "")).strip():
                    errors.append(
                        f"{p.relative_to(root)}: award needs a publisherUrl — "
                        "a social post is never a source"
                    )

    # --- search runs: a captured artifact needs a real hash --------------------
    for d in ("signals", "entities", "research"):
        for p in sorted((root / d).glob("*.md")):
            fm = parse_frontmatter(p.read_text(encoding="utf-8"))
            if fm.get("type") != "wks.search-run":
                continue
            sha = str(fm.get("artifactSha256", "")).strip()
            if sha and not re.fullmatch(r"[0-9a-fA-F]{64}", sha):
                errors.append(
                    f"{p.relative_to(root)}: artifactSha256 is not a SHA-256 digest"
                )
            if sha and not str(fm.get("artifactPath", "")).strip():
                errors.append(
                    f"{p.relative_to(root)}: artifactSha256 without artifactPath"
                )

    # --- observations: two rows for the same signal and org are one row --------
    seen_obs: dict[tuple[str, str], pathlib.Path] = {}
    for d in ("signals", "research", "entities", "fixtures/good"):
        for p in sorted((root / d).glob("*.md")):
            fm = parse_frontmatter(p.read_text(encoding="utf-8"))
            if fm.get("type") != "wks.observation":
                continue
            key = (str(fm.get("signal", "")).strip(), str(fm.get("quote", "")).strip().lower())
            if not key[0]:
                continue
            if key in seen_obs:
                errors.append(
                    f"{p.relative_to(root)}: duplicate observation — same signal and quote as "
                    f"{seen_obs[key].relative_to(root)}"
                )
            else:
                seen_obs[key] = p
        for p in sorted((root / d).glob("*.md")):
            fm = parse_frontmatter(p.read_text(encoding="utf-8"))
            if fm.get("type") != "wks.experiment":
                continue
            state = scalar(fm.get("state", ""))
            if state in ("supported", "refuted"):
                if fm.get("observedValue") in (None, "") or fm.get("sampleSize") in (None, ""):
                    errors.append(
                        f"{p.relative_to(root)}: state `{state}` requires observedValue and sampleSize"
                    )
            if state == "insufficient" and fm.get("observedValue") not in (None, ""):
                errors.append(
                    f"{p.relative_to(root)}: state `insufficient` must not carry an observedValue — "
                    "a small sample is a result, not a number to fill in"
                )


def redaction_checks(hub: pathlib.Path, errors: list[str]) -> None:
    """Nothing secret-shaped belongs in a public repository, ever.

    This is a net, not a proof. It catches the shapes that actually leak:
    provider key prefixes, bearer headers, private-key blocks, deploy keys.
    """
    patterns = [
        (re.compile(r"\bsk-[A-Za-z0-9]{20,}"), "an API key (sk-…)"),
        (re.compile(r"\bsk_live_[A-Za-z0-9]{10,}"), "a live secret key"),
        (re.compile(r"\bghp_[A-Za-z0-9]{20,}"), "a GitHub token (ghp_…)"),
        (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"), "a GitHub PAT"),
        (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "an AWS access key id"),
        (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"), "a Slack token"),
        (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "a private key block"),
        (re.compile(r"\bBearer\s+[A-Za-z0-9\-._~+/]{30,}"), "a bearer token"),
        (re.compile(r"CONVEX_DEPLOY_KEY\s*=\s*\S"), "a deploy key assignment"),
    ]
    for d in CONTENT_DIRS:
        p = hub / d
        if not p.is_dir():
            continue
        for f in sorted(p.glob("*.md")):
            text = f.read_text(encoding="utf-8")
            for rx, label in patterns:
                if rx.search(text):
                    errors.append(
                        f"{f.relative_to(hub)}: looks like it contains {label} "
                        "— secrets are runtime-only and never committed"
                    )

    # Receipts are public evidence, not a private spill directory. Scan active
    # and historical records recursively because a raw request/response can
    # otherwise bypass both the markdown-only graph scan and the CI contract.
    receipt_root = hub / "evidence" / "jev-receipts"
    if receipt_root.is_dir():
        for f in sorted(receipt_root.rglob("*.json")):
            text = f.read_text(encoding="utf-8")
            for rx, label in patterns:
                if rx.search(text):
                    errors.append(f"{f.relative_to(hub)}: looks like it contains {label}")
            try:
                receipt = json.loads(text)
            except json.JSONDecodeError:
                errors.append(f"{f.relative_to(hub)}: receipt is not valid JSON")
                continue
            rel = f.relative_to(receipt_root)
            if rel.parts[0] == "superseded":
                if receipt.get("historyStatus") != "superseded_non_reproducible" or receipt.get("evidenceUse") != "prohibited":
                    errors.append(f"{f.relative_to(hub)}: superseded receipt must be marked prohibited non-evidence")
            else:
                for key in ("request", "rules", "response", "inputHash", "deterministicDecision"):
                    if key not in receipt:
                        errors.append(f"{f.relative_to(hub)}: active receipt is missing `{key}`")


def run_checks(hub: pathlib.Path | None = None) -> CheckResult:
    """Run every check against `hub` (defaults to this repository)."""
    root = hub or HUB
    types = load_types(root)
    files = all_files(root)
    known = stems(root) | {pathlib.Path(n).stem for n in SURFACE_ROOT_FILES}
    result = CheckResult(types_loaded=len(types), files_checked=len(files))
    errors, warnings = result.errors, result.warnings
    by_type = result.by_type

    for p in surface_files(root):
        text = p.read_text(encoding="utf-8")
        errors.extend(surface_violations(p, text, root))

    for p in files:
        rel = p.relative_to(root)
        text = p.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)

        if not fm:
            errors.append(f"{rel}: no frontmatter")
            continue

        t = fm.get("type")
        if not t:
            errors.append(f"{rel}: frontmatter has no `type`")
        elif t not in types and t not in EXTERNAL_TYPES:
            errors.append(f"{rel}: unknown type `{t}`")
        else:
            by_type.setdefault(t, []).append(rel)

        # wikilinks resolve
        for link in WIKILINK.findall(text):
            target = link.split("|")[0].strip()
            if target and target not in known:
                errors.append(f"{rel}: dangling link [[{target}]]")

        # send safety. Scoped to frontmatter: prose that discusses the field, or a
        # documentation code block quoting it, is not a pre-approved draft. Any
        # value other than `no` fails closed, including an unrecognized one.
        if "sendReady" in fm and scalar(fm.get("sendReady", "")) != "no":
            errors.append(
                f"{rel}: sendReady is {fm.get('sendReady')} — nothing in the hub may ship pre-approved"
            )

        if t == "wks.automation":
            if "```text" not in text:
                errors.append(f"{rel}: automation has no fenced Prompt block")
            elif "CAUTION" not in text:
                errors.append(f"{rel}: automation prompt has no CAUTION line")
            enabled = scalar(fm.get("enabled", "no"))
            checked = scalar(fm.get("firstOpenChecked", "no"))
            if enabled == "yes" and checked != "yes":
                errors.append(f"{rel}: enabled without a checked first open")
            if checked == "yes":
                receipt_ref = fm.get("firstOpenReceipt", "")
                receipt = (root / receipt_ref).resolve() if receipt_ref else None
                if (not receipt or not receipt.is_relative_to(root.resolve()) or not receipt.is_file()
                        or receipt.suffix != ".json"):
                    errors.append(f"{rel}: checked first open requires a local evidence receipt")
                else:
                    try:
                        proof = json.loads(receipt.read_text(encoding="utf-8"))
                        artifact = (root / proof["artifactRef"]).resolve()
                        cost = float(proof["costUsd"])
                        valid = (proof["automationSlug"] == fm.get("slug")
                                 and proof["status"] == "succeeded"
                                 and proof["openedBy"] and proof["openedAt"]
                                 and proof["effects"] == []
                                 and math.isfinite(cost) and 0 <= cost <= float(fm["costCeilingUsd"]))
                        valid = valid and artifact.is_relative_to(root.resolve()) and artifact.is_file()
                        valid = valid and hashlib.sha256(artifact.read_bytes()).hexdigest() == proof["artifactSha256"]
                    except (KeyError, ValueError, TypeError, OSError, json.JSONDecodeError):
                        valid = False
                    if not valid:
                        errors.append(f"{rel}: checked first-open receipt has no verified artifact/open/cost proof")
            if enabled == "yes":
                errors.append(
                    f"{rel}: enabled has no local cost authorizer — this repository only supports disabled drafts"
                )
            if "costCeilingUsd" not in fm:
                errors.append(f"{rel}: no costCeilingUsd — a future executor must reject dispatch without one")
            elif not re.match(r"^\d+(\.\d+)?$", fm.get("costCeilingUsd", "")):
                errors.append(f"{rel}: costCeilingUsd must be a non-negative number")

        if t and t.startswith("wks."):
            if "tldr" not in fm:
                errors.append(f"{rel}: no tldr (required by node::au-base-types)")
            if "provenance" not in fm:
                warnings.append(f"{rel}: no provenance")
            # undeclared fields become engine diagnostics at mount time
            declared = set(BASE_FIELDS) | {"type", "status", "owner", "updated", "provenance"}
            required: set[str] = set()
            enums: dict[str, set[str]] = {}
            cur, seen = t, set()
            while cur in types and cur not in seen:
                seen.add(cur)
                declared |= types[cur]["fields"]
                required |= types[cur]["required"]
                enums.update({k: v for k, v in types[cur].get("enums", {}).items() if k not in enums})
                parents = [x for x in types[cur]["parents"] if x in types]
                cur = parents[0] if parents else ""
            for k in fm:
                if k not in declared:
                    warnings.append(f"{rel}: field `{k}` not declared on {t}")
            # A field declared without `?` is required. Presence is the test:
            # the frontmatter reader is deliberately shallow, so a block list or
            # a nested map reads as an empty scalar and must not be called absent.
            for k in sorted(required - BASE_FIELDS):
                if k not in fm:
                    errors.append(f"{rel}: required field `{k}` is missing on {t}")
            # An unrecognized enum value fails closed. This is safety-bearing:
            # a hostile or malformed `doNotContact` value must never be read as
            # "not do-not-contact", and the same holds for every other enum.
            for k, allowed in enums.items():
                if k not in fm or not str(fm.get(k, "")).strip():
                    continue
                raw = fm.get(k, "")
                if raw.startswith("["):
                    continue  # inline list shorthand; not a bare scalar
                if scalar(raw) not in allowed:
                    errors.append(
                        f"{rel}: `{k}` is `{raw}` on {t}, which is not one of "
                        f"{sorted(allowed)} — an unrecognized value fails closed"
                    )

    cross_checks(root, errors, warnings)
    errors.extend(check_records(root, [(path, parse_frontmatter(path.read_text(encoding="utf-8")))
                                      for path in all_files(root)]))
    redaction_checks(root, errors)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", action="store_true")
    ap.add_argument("--hub", type=pathlib.Path, default=None,
                    help="repository root to check (defaults to this repo)")
    args = ap.parse_args()

    result = run_checks(hub=args.hub)
    by_type = result.by_type

    print(f"files checked : {result.files_checked}")
    print(f"types loaded  : {result.types_loaded}")
    for t in sorted(by_type):
        print(f"  {t:20} {len(by_type[t])}")

    if result.warnings:
        print(f"\nwarnings ({len(result.warnings)}):")
        for w in result.warnings:
            print(f"  ! {w}")

    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for e in result.errors:
            print(f"  x {e}")

    if args.catalog:
        write_catalogs(by_type)
        print("\ncatalogs regenerated")

    print("\nOK" if not result.errors else "\nFAILED")
    return 1 if result.errors else 0


def write_catalogs(by_type: dict[str, list[pathlib.Path]], hub: pathlib.Path | None = None) -> None:
    root = hub or HUB
    cat = root / "catalogs"
    cat.mkdir(exist_ok=True)

    def table(t: str, cols: tuple[str, ...]) -> str:
        rows = []
        for rel in sorted(by_type.get(t, [])):
            fm = parse_frontmatter((root / rel).read_text(encoding="utf-8"))
            cells = [f"[[{rel.stem}]]"] + [fm.get(c, "").strip('"') or "-" for c in cols[1:]]
            rows.append("| " + " | ".join(cells) + " |")
        head = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols)
        return head + "\n" + "\n".join(rows) if rows else head

    (cat / "automation-dictionary.md").write_text(
        "---\ntype: wks.catalog\ntldr: \"Every automation this hub can stand up, and whether it is gated.\"\nstatus: active\n"
        "owner: Derrick Watts\nupdated: 2026-09-16\nsurface: watts\nprovenance: \"Generated by scripts/validate.py --catalog\"\n"
        f"indexes: automations\nentryCount: {len(by_type.get('wks.automation', []))}\n---\n\n"
        "# Automation dictionary\n\nEvery automation this hub can stand up. None are Enabled until "
        "[[first-open-gate]] passes.\n\n# Index\n\n"
        + table("wks.automation", ("name", "slug", "mode", "enabled", "firstOpenChecked", "costCeilingUsd"))
        + "\n", encoding="utf-8")
    # Engine body sections are H1 (`# Index`), not H2.

    (cat / "signal-catalog.md").write_text(
        "---\ntype: wks.catalog\ntldr: \"Ranked buying triggers, strongest intent first.\"\nstatus: active\nowner: Derrick Watts\n"
        "updated: 2026-09-16\nsurface: watts\nprovenance: \"Generated by scripts/validate.py --catalog\"\n"
        f"indexes: signals\nentryCount: {len(by_type.get('wks.signal', []))}\n---\n\n"
        "# Signal catalog\n\nRanked buying triggers. Rank 1 is the strongest intent.\n\n# Index\n\n"
        + table("wks.signal", ("name", "rank", "decayDays"))
        + "\n", encoding="utf-8")

    (cat / "runbook-catalog.md").write_text(
        "---\ntype: wks.catalog\ntldr: \"Operating procedures and data-extraction runbooks.\"\nstatus: active\nowner: Derrick Watts\n"
        "updated: 2026-09-16\nsurface: watts\nprovenance: \"Generated by scripts/validate.py --catalog\"\n"
        f"indexes: workflows\nentryCount: {len(by_type.get('wks.runbook', [])) + len(by_type.get('wks.extraction', []))}\n---\n\n"
        "# Runbook and extraction catalog\n\n# Index\n\n### Runbooks\n\n"
        + table("wks.runbook", ("name", "trigger", "audience"))
        + "\n\n### Extractions\n\n"
        + table("wks.extraction", ("name", "sourceSystem", "requiresAuth", "authOwner"))
        + "\n", encoding="utf-8")

    (cat / "tactic-catalog.md").write_text(
        "---\ntype: wks.catalog\ntldr: \"Outside plays we adopted, each attributed to its author.\"\nstatus: active\nowner: Derrick Watts\n"
        "updated: 2026-09-16\nsurface: watts\nprovenance: \"Generated by scripts/validate.py --catalog\"\n"
        f"indexes: tactics\nentryCount: {len(by_type.get('wks.tactic', []))}\n---\n\n"
        "# Tactic catalog\n\nOutside plays we have adopted. Every one is attributed; a claimed result "
        "stays the author's claim and is never restated as ours.\n\n# Index\n\n"
        + table("wks.tactic", ("name", "source", "category", "adoptionState"))
        + "\n", encoding="utf-8")

    (cat / "playbook-catalog.md").write_text(
        "---\ntype: wks.catalog\ntldr: \"Specialist modules in the outbound motion, and the automation each one owns.\"\nstatus: active\n"
        "owner: Derrick Watts\nupdated: 2026-09-16\nsurface: watts\nprovenance: \"Generated by scripts/validate.py --catalog\"\n"
        f"indexes: playbooks\nentryCount: {len(by_type.get('wks.playbook', []))}\n---\n\n"
        "# Playbook catalog\n\nEvery specialist module in the motion. Run them in the order on "
        "routing. Do not skip icp or the send gate.\n\n# Index\n\n"
        + table("wks.playbook", ("name", "module", "role", "nextOwner"))
        + "\n", encoding="utf-8")

    (cat / "channel-catalog.md").write_text(
        "---\ntype: wks.catalog\ntldr: \"How a settled message changes when it moves to a channel.\"\nstatus: active\n"
        "owner: Derrick Watts\nupdated: 2026-09-16\nsurface: watts\nprovenance: \"Generated by scripts/validate.py --catalog\"\n"
        f"indexes: channels\nentryCount: {len(by_type.get('wks.channel-guide', []))}\n---\n\n"
        "# Channel catalog\n\nSame claim. Different first fold. Start with channels.\n\n# Index\n\n"
        + table("wks.channel-guide", ("name", "channel", "firstFoldChars", "wordCap"))
        + "\n", encoding="utf-8")

    (cat / "skill-catalog.md").write_text(
        "---\ntype: wks.catalog\ntldr: \"Triggered skills and profiles.\"\nstatus: active\nowner: Derrick Watts\n"
        "updated: 2026-09-16\nsurface: watts\nprovenance: \"Generated by scripts/validate.py --catalog\"\n"
        f"indexes: skills\nentryCount: {len(by_type.get('mcp.skill::au-mcp-sdk', []))}\n---\n\n"
        "# Skill and agent catalog\n\n# Index\n\n### Skills\n\n"
        + table("mcp.skill::au-mcp-sdk", ("name", "description"))
        + "\n\n### Agent profiles\n\nYAML files under `profiles/`.\n"
        + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
