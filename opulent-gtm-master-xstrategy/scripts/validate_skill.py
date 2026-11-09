from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
REQUIRED_REFERENCES = [
    "operating-sequence.md",
    "account-campaign-contracts.md",
    "evidence-and-metrics.md",
    "diego-workbook-evidence.md",
    "field-theory-findings.md",
    "reference-repo-patterns.md",
    "opulent-use-case-catalog.md",
]
REQUIRED_SECTIONS = [
    "## Overview",
    "## What's Needed From User",
    "## Before You Start",
    "## Procedure",
    "## Specifications",
    "## Advice and Pointers",
    "## Forbidden Actions",
    "## Performance Bar Checklist",
]


def fail(message: str):
    raise SystemExit(f"FAIL: {message}")


text = SKILL.read_text(encoding="utf-8")
if "name: opulent-gtm-master-xstrategy" not in text:
    fail("frontmatter name does not match directory")
for section in REQUIRED_SECTIONS:
    if section not in text:
        fail(f"missing required section: {section}")

procedure = text.split("## Procedure", 1)[1].split("## Specifications", 1)[0]
steps = re.findall(r"^\d+\. ", procedure, flags=re.MULTILINE)
if not 1 <= len(steps) <= 12:
    fail(f"procedure must have 1-12 steps, found {len(steps)}")

for name in REQUIRED_REFERENCES:
    path = ROOT / "references" / name
    if not path.is_file() or path.stat().st_size < 200:
        fail(f"missing or empty reference: {name}")

catalog_path = ROOT / "research" / "evidence" / "opulent-use-cases.json"
if not catalog_path.is_file():
    fail("missing machine-readable Opulent use-case catalog")
catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
rows = catalog.get("use_cases", [])
if catalog.get("source_url") != "https://opulent-cloud.vercel.app/use-cases/":
    fail("use-case catalog source URL is incorrect")
if catalog.get("count") != 44 or len(rows) != 44:
    fail(f"expected 44 use cases, found {len(rows)}")
if len({row.get("url") for row in rows}) != 44:
    fail("use-case URLs are missing or duplicated")
for row in rows:
    observed = row.get("observed", {})
    labels = row.get("gtm_labels", {})
    if not all(row.get(key) for key in ("title", "summary", "url")):
        fail("use-case record is missing title, summary, or URL")
    if not all(key in observed for key in ("site_category", "featured", "capability_tags")):
        fail(f"observed labels are incomplete for {row.get('slug')}")
    if not all(labels.get(key) for key in ("buyer_group", "value_motion", "lifecycle_stage", "portfolio_role")):
        fail(f"GTM labels are incomplete for {row.get('slug')}")

catalog_markdown = (ROOT / "references" / "opulent-use-case-catalog.md").read_text(encoding="utf-8")
for row in rows:
    if row["title"] not in catalog_markdown or row["url"] not in catalog_markdown:
        fail(f"readable catalog is missing {row['slug']}")

for forbidden in ("@gmail.com", "linkedin.com/in/", "Email Address:"):
    for path in [SKILL, *(ROOT / "references").glob("*.md")]:
        if forbidden.lower() in path.read_text(encoding="utf-8").lower():
            fail(f"possible direct identifier in reusable skill: {path.name}")

print("PASS: opulent-gtm-master-xstrategy structure, references, sequencing, and PII guard")
