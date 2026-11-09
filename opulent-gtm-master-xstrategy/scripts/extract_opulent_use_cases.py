from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
INDEX_URL = "https://opulent-cloud.vercel.app/use-cases/"
JSON_OUTPUT = ROOT / "research" / "evidence" / "opulent-use-cases.json"
MARKDOWN_OUTPUT = ROOT / "references" / "opulent-use-case-catalog.md"

CATEGORY_BUYER = {
    "GTM Engineering": "Revenue and growth",
    "Finance Operations": "Finance and operations",
    "Data & Analytics": "Data and analytics",
    "Automations": "Engineering and operations",
    "Incident Response": "Reliability and security",
    "Migrations": "Engineering leadership",
    "Feature Development": "Product and engineering",
    "Project Management": "Product operations",
    "Code Quality": "Engineering quality and security",
    "Opulent Optimization": "AI platform and engineering productivity",
}

CATEGORY_VALUE_MOTION = {
    "GTM Engineering": "Revenue growth",
    "Finance Operations": "Operating efficiency",
    "Data & Analytics": "Decision intelligence",
    "Automations": "Operating leverage",
    "Incident Response": "Risk reduction",
    "Migrations": "Delivery acceleration",
    "Feature Development": "Delivery acceleration",
    "Project Management": "Planning throughput",
    "Code Quality": "Quality and risk reduction",
    "Opulent Optimization": "Learning velocity",
}

LIFECYCLE_BY_SLUG = {
    "deal-sourcing-as-a-self-driving-crm": "Discover",
    "event-prospecting": "Discover",
    "background-account-triage": "Qualify",
    "self-evolving-pipeline-operations": "Optimize",
    "stand-up-a-crm-and-outreach-pipeline-in-one-run": "Convert",
    "relationship-intelligence-for-the-warm-intro": "Engage",
    "opulent-x-clodo-people-search-into-reviewed-pipelines": "Discover",
    "competitor-landscape-into-living-battlecards": "Enable",
    "procurement-as-a-governed-agent-run": "Operate",
    "order-and-invoice-work-as-one-reconciled-loop": "Operate",
    "live-sap-simulation-before-consultants-finish-discovery": "Deliver",
    "opulent-x-ramp-controllable-autonomous-finance": "Operate",
    "forecast-cash-flow-to-the-liquidity-low-point": "Plan",
    "data-analysis-as-an-agent-run-workflow": "Decide",
    "reason-over-entire-datasets-with-async-spawns": "Decide",
    "ad-hoc-data-queries-in-slack": "Decide",
    "customer-health-summaries-in-slack": "Retain",
    "anomaly-detection-across-connected-data": "Protect",
    "antifragile-deployments": "Protect",
    "autonomous-triage-for-knowledge-work-queues": "Operate",
    "daily-sentry-error-fixes": "Protect",
    "auto-fix-failing-ci-builds": "Protect",
    "run-nightly-e2e-tests-on-staging": "Protect",
    "fleet-wide-maintenance-across-thousands-of-repositories": "Scale",
    "daily-datadog-health-digest": "Protect",
    "auto-investigate-datadog-alerts": "Protect",
    "auto-generate-incident-postmortems": "Learn",
    "debug-a-bug-report-end-to-end": "Protect",
    "migrate-50-files-from-rest-to-graphql": "Deliver",
    "create-a-react-18-to-19-upgrade-playbook": "Plan",
    "refactor-a-multi-million-line-etl-monolith": "Deliver",
    "implement-bookings-api-from-openapi-spec": "Deliver",
    "click-test-real-product-flows-with-computer-use": "Validate",
    "figma-to-pixel-perfect-code": "Deliver",
    "catch-visual-regressions-before-every-pr": "Protect",
    "auto-triage-bugs-via-linear": "Qualify",
    "turn-prds-into-sprint-tickets": "Plan",
    "bulk-plan-your-ticket-backlog": "Plan",
    "add-unit-tests-to-your-payments-service": "Protect",
    "auto-fix-pr-bugs-before-merge": "Protect",
    "security-swarm-fix-vulnerabilities-at-scale": "Protect",
    "fix-checkout-latency-with-three-competing-strategies": "Optimize",
    "test-8-untested-modules-in-one-night": "Scale",
    "learn-from-past-runs-to-sharpen-the-next-prompt": "Learn",
}

PARTNER_WEDGES = {
    "opulent-x-clodo-people-search-into-reviewed-pipelines",
    "opulent-x-ramp-controllable-autonomous-finance",
}

PRIMARY_NONFEATURED = {
    "event-prospecting",
    "relationship-intelligence-for-the-warm-intro",
    "forecast-cash-flow-to-the-liquidity-low-point",
    "anomaly-detection-across-connected-data",
}

ENABLEMENT_ASSETS = {
    "competitor-landscape-into-living-battlecards",
    "create-a-react-18-to-19-upgrade-playbook",
    "bulk-plan-your-ticket-backlog",
    "learn-from-past-runs-to-sharpen-the-next-prompt",
}


class UseCaseIndexParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.current_href: str | None = None
        self.current_text: list[str] = []
        self.cards: list[tuple[str, list[str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a" or self.current_href is not None:
            return
        href = dict(attrs).get("href")
        if href and href.startswith("/use-cases/") and href != "/use-cases/":
            self.current_href = href
            self.current_text = []

    def handle_data(self, data: str) -> None:
        if self.current_href is None:
            return
        value = " ".join(data.split())
        if value:
            self.current_text.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.current_href is not None:
            self.cards.append((self.current_href, self.current_text))
            self.current_href = None
            self.current_text = []


def slug_from_href(href: str) -> str:
    return href.strip("/").split("/")[-1]


def portfolio_role(slug: str, featured: bool, capabilities: list[str]) -> str:
    if slug in PARTNER_WEDGES:
        return "Partner wedge"
    if slug in ENABLEMENT_ASSETS:
        return "Enablement asset"
    if featured or slug in PRIMARY_NONFEATURED:
        return "Primary wedge"
    if {"Integrations", "MCP", "Schedules"}.intersection(capabilities):
        return "Expansion module"
    return "Proof accelerator"


def parse_cards(raw_html: bytes) -> list[dict[str, object]]:
    parser = UseCaseIndexParser()
    parser.feed(raw_html.decode("utf-8"))
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for href, raw_tokens in parser.cards:
        slug = slug_from_href(href)
        if slug in seen:
            continue
        seen.add(slug)
        tokens = raw_tokens[:]
        featured = bool(tokens and tokens[0] == "★")
        if featured:
            tokens.pop(0)
        if len(tokens) < 3:
            raise ValueError(f"Could not parse use-case card {href}: {tokens!r}")
        category, title, summary, *capabilities = tokens
        if category not in CATEGORY_BUYER:
            raise ValueError(f"Unknown site category {category!r} for {slug}")
        if slug not in LIFECYCLE_BY_SLUG:
            raise ValueError(f"Missing editorial lifecycle label for {slug}")
        rows.append(
            {
                "ordinal": len(rows) + 1,
                "slug": slug,
                "url": urljoin(INDEX_URL, href),
                "title": title,
                "summary": summary,
                "observed": {
                    "site_category": category,
                    "featured": featured,
                    "capability_tags": capabilities,
                },
                "gtm_labels": {
                    "buyer_group": CATEGORY_BUYER[category],
                    "value_motion": CATEGORY_VALUE_MOTION[category],
                    "lifecycle_stage": LIFECYCLE_BY_SLUG[slug],
                    "portfolio_role": portfolio_role(slug, featured, capabilities),
                },
            }
        )
    missing = set(LIFECYCLE_BY_SLUG) - seen
    if missing:
        raise ValueError(f"Expected labeled use cases missing from live index: {sorted(missing)}")
    return rows


def render_markdown(payload: dict[str, object]) -> str:
    rows = payload["use_cases"]
    lines = [
        "# Opulent Use-Case Catalog",
        "",
        f"Source: [{INDEX_URL}]({INDEX_URL})",
        "",
        f"Captured: {payload['retrieved_at']}",
        "",
        f"Snapshot: {payload['count']} use cases; SHA-256 `{payload['source_sha256']}`",
        "",
        "## Label contract",
        "",
        "- **Observed labels** reproduce the live index card: site category, featured star, capability tags, title, and summary.",
        "- **GTM labels** are editorial classifications for commercial planning: buyer group, value motion, lifecycle stage, and portfolio role.",
        "- Portfolio roles mean: `Primary wedge` can lead a sales conversation; `Partner wedge` attaches to an ecosystem; `Expansion module` follows an initial foothold; `Proof accelerator` demonstrates capability; `Enablement asset` improves planning or positioning.",
        "- These labels organize the portfolio; they do not replace account evidence or authorize external claims.",
        "",
        "## Portfolio summary",
        "",
        f"- Site categories: {', '.join(f'{k} ({v})' for k, v in payload['counts']['site_categories'].items())}",
        f"- Portfolio roles: {', '.join(f'{k} ({v})' for k, v in payload['counts']['portfolio_roles'].items())}",
        f"- Featured on source index: {payload['counts']['featured']}",
        "",
        "## Complete labeled catalog",
        "",
    ]
    for row in rows:
        observed = row["observed"]
        labels = row["gtm_labels"]
        capabilities = ", ".join(observed["capability_tags"]) or "None shown"
        featured = "yes" if observed["featured"] else "no"
        lines.extend(
            [
                f"### {row['ordinal']:02d}. [{row['title']}]({row['url']})",
                "",
                f"- Observed: `{observed['site_category']}`; featured `{featured}`; capabilities `{capabilities}`",
                f"- GTM labels: buyer `{labels['buyer_group']}`; value `{labels['value_motion']}`; lifecycle `{labels['lifecycle_stage']}`; role `{labels['portfolio_role']}`",
                f"- Extracted summary: {row['summary']}",
                "",
            ]
        )
    lines.extend(
        [
            "## GTM use",
            "",
            "Choose one `Primary wedge` or `Partner wedge` only after matching it to a named buyer, observed workflow pain, proof availability, and a safe next action. Use expansion modules and proof accelerators to deepen or validate that wedge; do not present the entire catalog as one offer.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    request = Request(INDEX_URL, headers={"User-Agent": "Opulent-GTM-Catalog/1.0"})
    with urlopen(request, timeout=30) as response:
        raw_html = response.read()
        headers = {key.lower(): value for key, value in response.headers.items()}
    rows = parse_cards(raw_html)
    category_counts = Counter(row["observed"]["site_category"] for row in rows)
    role_counts = Counter(row["gtm_labels"]["portfolio_role"] for row in rows)
    payload = {
        "schema_version": 1,
        "source_url": INDEX_URL,
        "retrieved_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_last_modified": headers.get("last-modified"),
        "source_etag": headers.get("etag"),
        "source_sha256": hashlib.sha256(raw_html).hexdigest(),
        "count": len(rows),
        "classification_method": "Observed fields are extracted from the live index; GTM fields are deterministic editorial labels defined in this script.",
        "counts": {
            "site_categories": dict(category_counts),
            "portfolio_roles": dict(role_counts),
            "featured": sum(bool(row["observed"]["featured"]) for row in rows),
        },
        "use_cases": rows,
    }
    if len(rows) != 44:
        raise SystemExit(f"Expected 44 live use cases, found {len(rows)}")
    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    MARKDOWN_OUTPUT.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Wrote {len(rows)} labeled use cases to {JSON_OUTPUT}")
    print(f"Wrote readable catalog to {MARKDOWN_OUTPUT}")


if __name__ == "__main__":
    main()
