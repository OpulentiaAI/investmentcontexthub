"""Contract tests for the graph checks.

Two halves:
  - negative tests: a deliberately broken hub MUST produce the named error
  - positive tests: a correct hub MUST stay clean

The negative half is the point. A validator nobody has watched fail is a
validator nobody should trust.
"""
from __future__ import annotations

import unittest
import hashlib

from tests.support import HubCase


class FrontmatterRules(HubCase):
    def test_missing_frontmatter_is_an_error(self):
        self.declare_type("wks.thing")
        self.write("signals/bare.md", "# no frontmatter at all\n")
        self.assert_error_contains("no frontmatter")

    def test_unknown_type_is_an_error(self):
        self.instance("signals/mystery.md", "wks.does_not_exist")
        self.assert_error_contains("unknown type")

    def test_frontmatter_without_type_is_an_error(self):
        self.write("signals/typeless.md", "---\ntldr: x\n---\n\n# Body\n")
        self.assert_error_contains("frontmatter has no `type`")

    def test_missing_tldr_is_an_error(self):
        self.declare_type("wks.thing")
        self.write("signals/notldr.md", (
            "---\ntype: wks.thing\nstatus: active\nowner: x\nupdated: 2026-09-18\n"
            "surface: watts\nprovenance: p\n---\n\n# Body\n"
        ))
        self.assert_error_contains("no tldr")

    def test_a_clean_instance_passes(self):
        self.declare_type("wks.thing")
        self.instance("signals/good.md", "wks.thing")
        self.assertEqual(self.errors(), [])


class LinkRules(HubCase):
    def test_dangling_wikilink_is_an_error(self):
        self.declare_type("wks.thing")
        self.instance("signals/linky.md", "wks.thing", body="\n# Body\n\nSee [[nowhere]].\n")
        self.assert_error_contains("dangling link [[nowhere]]")

    def test_resolvable_wikilink_is_fine(self):
        self.declare_type("wks.thing")
        self.instance("signals/target.md", "wks.thing")
        self.instance("signals/source.md", "wks.thing", body="\n# Body\n\nSee [[target]].\n")
        self.assertEqual(self.errors(), [])


class SendSafetyRules(HubCase):
    def test_send_ready_yes_is_an_error(self):
        self.declare_type("wks.message")
        self.instance("signals/draft.md", "wks.message", extra="sendReady: yes\n")
        self.assert_error_contains("sendReady is")

    def test_send_ready_no_is_clean(self):
        self.declare_type("wks.message")
        self.instance("signals/draft.md", "wks.message", extra="sendReady: no\n")
        self.assertEqual(self.errors(), [])


class AutomationRules(HubCase):
    def prompt(self, extra: str = "enabled: no\nfirstOpenChecked: no\ncostCeilingUsd: 1\n",
               caution: bool = True) -> str:
        tail = "CAUTION: never send.\n" if caution else "do the thing.\n"
        return (
            "---\n"
            "type: wks.automation\n"
            "tldr: t\nstatus: active\nowner: x\nupdated: 2026-09-18\n"
            "surface: watts\nprovenance: p\n"
            "slug: t\n"
            f"{extra}"
            "---\n\n# Overview\n\n# Prompt\n\n```text\n"
            f"{tail}"
            "```\n\n# Forbidden Actions\n"
        )

    def setUp(self):
        super().setUp()
        self.declare_type("wks.automation")

    def test_enabled_without_first_open_is_an_error(self):
        self.write("automations/a.md", self.prompt("enabled: yes\nfirstOpenChecked: no\ncostCeilingUsd: 1\n"))
        self.assert_error_contains("enabled without a checked first open")

    def test_enabled_with_first_open_checked_still_fails_without_a_cost_authorizer(self):
        self.write("automations/a.md", self.prompt("enabled: yes\nfirstOpenChecked: yes\ncostCeilingUsd: 1\n"))
        self.assert_error_contains("no local cost authorizer")

    def test_prompt_without_caution_is_an_error(self):
        self.write("automations/a.md", self.prompt(caution=False))
        self.assert_error_contains("no CAUTION line")

    def test_missing_prompt_block_is_an_error(self):
        self.write("automations/a.md", (
            "---\ntype: wks.automation\ntldr: t\nstatus: active\nowner: x\n"
            "updated: 2026-09-18\nsurface: watts\nprovenance: p\nslug: t\n"
            "enabled: no\nfirstOpenChecked: no\ncostCeilingUsd: 1\n---\n\n# Overview\n"
        ))
        self.assert_error_contains("no fenced Prompt block")

    def test_negative_cost_ceiling_is_an_error(self):
        self.write("automations/a.md", self.prompt("enabled: no\nfirstOpenChecked: no\ncostCeilingUsd: -1\n"))
        self.assert_error_contains("costCeilingUsd must be a non-negative number")

    def test_missing_cost_ceiling_is_an_error(self):
        self.write("automations/a.md", self.prompt("enabled: no\nfirstOpenChecked: no\n"))
        self.assert_error_contains("no costCeilingUsd")


class SurfaceRules(HubCase):
    def test_operator_marker_on_product_surface_is_an_error(self):
        self.declare_type("wks.thing")
        self.instance("signals/leak.md", "wks.thing", extra="surface: operator\n")
        self.assert_error_contains("operator file must live under ops/")

    def test_forbidden_phrase_on_product_surface_is_an_error(self):
        self.declare_type("wks.thing")
        self.instance("signals/leak.md", "wks.thing", body="\n# Body\n\nCONVEX_DEPLOY here.\n")
        self.assert_error_contains("product surface contains")


class CoverageRules(HubCase):
    """One extraction is not coverage — the guardrail is enforced, not just documented."""

    def test_connected_source_without_manifest_row_is_an_error(self):
        self.declare_type("wks.source-manifest", parents="thing::au-base-types",
                          fields="  sourceId: String\n  state: String\n"
                                 "  doesNotCover: String[+]\n  lastObservedAt: Date\n  blockerNote: String")
        self.connector("spear")
        self.write("entities/source-manifest.md", (
            "---\ntype: wks.source-manifest\ntldr: t\nstatus: active\nowner: x\n"
            "updated: 2026-09-18\nsurface: watts\nprovenance: p\n---\n\n"
            "# Manifest\n\nsources:\n"
            "  - sourceId: notion\n"
            "    state: pending\n"
            "    doesNotCover: mailbox\n"
        ))
        self.assert_error_contains("has no source-manifest row")

    def test_connected_sources_without_any_manifest_is_an_error(self):
        self.connector("spear")
        self.connector("notion")
        self.assert_error_contains("no source-manifest")

    def test_manifest_row_missing_does_not_cover_is_an_error(self):
        self.connector("spear")
        self.write("entities/source-manifest.md", (
            "---\ntype: wks.source-manifest\ntldr: t\nstatus: active\nowner: x\n"
            "updated: 2026-09-18\nsurface: watts\nprovenance: p\n---\n\n"
            "sources:\n  - sourceId: spear\n    state: pending\n"
        ))
        self.assert_error_contains("doesNotCover is required")

    def test_extracted_row_requires_last_observed_at(self):
        self.connector("spear")
        self.write("entities/source-manifest.md", (
            "---\ntype: wks.source-manifest\ntldr: t\nstatus: active\nowner: x\n"
            "updated: 2026-09-18\nsurface: watts\nprovenance: p\n---\n\n"
            "sources:\n  - sourceId: spear\n    state: extracted\n    doesNotCover: mailbox\n"
        ))
        self.assert_error_contains("extracted` requires lastObservedAt")

    def test_extracted_row_needs_matching_full_run(self):
        self.connector("spear")
        self.write("entities/source-manifest.md", (
            "---\ntype: wks.source-manifest\ntldr: t\nstatus: active\nowner: x\n"
            "updated: 2026-09-18\nsurface: watts\nprovenance: p\n---\n\n"
            "sources:\n  - sourceId: spear\n    state: extracted\n"
            "    lastObservedAt: 2026-09-18\n    lastRun: [[missing-run]]\n"
            "    completeness: FULL\n    doesNotCover: mailbox\n"
        ))
        self.assert_error_contains("requires FULL completeness and linked lastRun")

    def test_undefined_nested_row_type_is_an_error(self):
        (self.root / "type" / "wks.source-manifest-row.type.yaml").unlink()
        self.connector("spear")
        self.write("entities/source-manifest.md", (
            "---\ntype: wks.source-manifest\ntldr: t\nstatus: active\nowner: x\n"
            "updated: 2026-09-18\nsurface: watts\nprovenance: p\n---\n\n"
            "sources:\n  - sourceId: spear\n    state: pending\n"
        ))
        self.assert_error_contains("undefined `wks.source-manifest-row` type")

    def test_unavailable_row_requires_a_blocker_note(self):
        self.connector("gmail")
        self.write("entities/source-manifest.md", (
            "---\ntype: wks.source-manifest\ntldr: t\nstatus: active\nowner: x\n"
            "updated: 2026-09-18\nsurface: watts\nprovenance: p\n---\n\n"
            "sources:\n  - sourceId: gmail\n    state: unavailable\n    doesNotCover: mail\n"
        ))
        self.assert_error_contains("requires a blockerNote")


class ExtractionRunRules(HubCase):
    """Exercised against the real wks.extraction-run declaration."""

    def run_doc(self, extra: str) -> None:
        base = ("sourceId: s\nscope: full\nobservedAt: 2026-09-18\nproduced: [rows]\n"
                "recordCount: 1\nfileCount: 1\ncompleteness: COMPLETE\ntruncated: no\n"
                "outcome: ok\nprivacy: private\n")
        self.instance("extractions/r.md", "wks.extraction-run", extra=base + extra)

    def test_partial_without_gap_or_blocker_is_an_error(self):
        self.run_doc("outcome: partial\n")
        self.assert_error_contains("requires `missing` or `blockerNote`")

    def test_partial_with_missing_is_clean(self):
        self.run_doc("outcome: partial\nmissing: [dms]\n")
        self.assert_no_error_containing("requires `missing`")

    def test_artifact_ref_without_hash_is_an_error(self):
        self.run_doc("artifactRef: a.zip\n")
        self.assert_error_contains("artifactRef without artifactSha256")

    def test_delta_without_continuing_from_is_an_error(self):
        self.run_doc("scope: delta\n")
        self.assert_error_contains("delta run requires continuingFrom")

    def test_ok_run_is_clean(self):
        self.write("artifact.txt", "synthetic artifact")
        sha = hashlib.sha256(b"synthetic artifact").hexdigest()
        self.run_doc(f"artifactRef: artifact.txt\nartifactSha256: {sha}\n"
                     "pagesCaptured: 1\npagesExpected: 1\npageIndices: [1]\n")
        self.assertEqual(self.errors(), [])

    def test_truncated_read_is_representable(self):
        self.run_doc("outcome: partial\ntruncated: yes\n"
                     "errors: [large-output truncation lost rows]\nmissing: [remaining pages]\n")
        self.assertEqual(self.errors(), [])

    def test_truncated_run_cannot_claim_ok(self):
        self.run_doc("truncated: yes\n")
        self.assert_error_contains("ok requires complete non-truncated")

    def test_wrong_digest_does_not_prove_artifact(self):
        self.write("artifact.txt", "synthetic artifact")
        self.run_doc(f"artifactRef: artifact.txt\nartifactSha256: {'0' * 64}\n"
                     "pagesCaptured: 1\npagesExpected: 1\npageIndices: [1]\n")
        self.assert_error_contains("does not match artifact bytes")

    def test_ok_run_with_repeated_page_is_not_complete(self):
        self.write("artifact.txt", "synthetic artifact")
        sha = hashlib.sha256(b"synthetic artifact").hexdigest()
        self.run_doc(f"artifactRef: artifact.txt\nartifactSha256: {sha}\n"
                     "pagesCaptured: 2\npagesExpected: 2\npageIndices: [1, 1]\n")
        self.assert_error_contains("contiguous complete page counts")


class ExperimentRules(HubCase):
    """Exercised against the real wks.experiment declaration."""

    BASE = ("unit: replies\nhypothesis: h\nmeasure: rate\nthreshold: 3\ndirection: at_least\n"
            "preconditions: [approval]\n")

    def experiment(self, extra: str) -> None:
        self.instance("research/e.md", "wks.experiment", extra=self.BASE + extra)

    def test_supported_without_value_is_an_error(self):
        self.experiment("state: supported\n")
        self.assert_error_contains("requires observedValue and sampleSize")

    def test_insufficient_must_not_carry_a_value(self):
        self.experiment("state: insufficient\nobservedValue: 0\n")
        self.assert_error_contains("must not carry an observedValue")

    def test_supported_with_value_and_sample_is_clean(self):
        self.experiment("state: supported\nobservedValue: 3\nsampleSize: 20\n")
        self.assertEqual(self.errors(), [])

    def test_insufficient_alone_is_clean(self):
        self.experiment("state: insufficient\n")
        self.assertEqual(self.errors(), [])

    def test_run_experiment_carries_no_promotion(self):
        # Promotion is a human decision. An automation must never set it.
        self.experiment("state: running\n")
        self.assert_no_error_containing("promotedBy")


class EnumFailClosed(HubCase):
    """An unrecognized enum value must fail closed, never read as a benign one.

    Adversarial review reproduced a suppression bypass: a warm path through a
    person whose `doNotContact` was `"yes # hostile-value"` passed validation,
    because the DNC scan compared the normalized scalar to `yes` and found no
    match. Enum validation closes the whole class, not just this instance.
    """

    def setUp(self):
        super().setUp()
        self.instance("signals/protected.md", "wks.person", extra="doNotContact: yes\n")
        self.instance("signals/intro.md", "wks.person", extra="doNotContact: no\n")
        self.write("signals/route.md", (
            "---\ntype: wks.warm-path\ntldr: t\nstatus: active\nowner: x\n"
            "updated: 2026-09-18\nsurface: watts\nprovenance: p\n"
            'target: "[[intro]]"\nintroducer: "[[protected]]"\n'
            'pathKind: former-colleagues\nevidenceUrl: "https://example.invalid/x"\n'
            "strength: working\nverified: yes\n---\n\n# Route\n"
        ))

    def test_baseline_bypass_route_is_rejected(self):
        self.assert_error_contains("doNotContact")

    def test_noncanonical_dnc_value_fails_closed(self):
        # The exact bypass: quoted value with a trailing comment.
        self.write("signals/protected.md", (
            "---\ntype: wks.person\ntldr: t\nstatus: active\nowner: x\n"
            "updated: 2026-09-18\nsurface: watts\nprovenance: p\n"
            'doNotContact: "yes # hostile-value"\n---\n\n# P\n'
        ))
        errors = self.errors()
        self.assertTrue(
            any("not one of" in e and "doNotContact" in e for e in errors),
            f"an unrecognized doNotContact value must fail closed; got {errors}",
        )
        self.assertTrue(
            any("doNotContact" in e for e in errors),
            "the suppression bypass must not pass validation",
        )

    def test_garbage_dnc_value_also_fails_closed(self):
        self.write("signals/protected.md", (
            "---\ntype: wks.person\ntldr: t\nstatus: active\nowner: x\n"
            "updated: 2026-09-18\nsurface: watts\nprovenance: p\n"
            "doNotContact: maybe\n---\n\n# P\n"
        ))
        self.assertTrue(any("doNotContact" in e for e in self.errors()))

    def test_canonical_no_still_allows_a_route(self):
        self.write("signals/route.md", (
            "---\ntype: wks.warm-path\ntldr: t\nstatus: active\nowner: x\n"
            "updated: 2026-09-18\nsurface: watts\nprovenance: p\n"
            'target: "[[protected]]"\nintroducer: "[[intro]]"\n'
            'pathKind: former-colleagues\nevidenceUrl: "https://example.invalid/x"\n'
            "strength: working\nverified: yes\n---\n\n# Route\n"
        ))
        self.assert_no_error_containing("doNotContact")


class SendReadyScope(HubCase):
    def setUp(self):
        super().setUp()
        self.declare_type("wks.message")

    def test_send_ready_yes_in_frontmatter_is_an_error(self):
        self.instance("signals/m.md", "wks.message", extra="sendReady: yes\n")
        self.assert_error_contains("sendReady")

    def test_noncanonical_send_ready_value_fails_closed(self):
        self.instance("signals/m.md", "wks.message", extra="sendReady: approved\n")
        self.assert_error_contains("sendReady")

    def test_send_ready_yes_in_prose_is_not_an_error(self):
        # A document that QUOTES the field in a body code block is not a draft.
        self.instance("signals/m.md", "wks.message", extra="sendReady: no\n",
                      body='\n# Body\n\nExample frontmatter:\n\n```yaml\nsendReady: yes\n```\n')
        self.assert_no_error_containing("sendReady")

    def test_send_ready_no_is_clean(self):
        self.instance("signals/m.md", "wks.message", extra="sendReady: no\n")
        self.assert_no_error_containing("sendReady")


class DuplicateManifestRows(HubCase):
    """Two rows for one source with the same owner would merge two datasets."""

    def setUp(self):
        super().setUp()
        self.connector("apollo")

    def write_manifest(self, rows: str) -> None:
        self.write("entities/source-manifest.md", (
            "---\ntype: wks.source-manifest\ntldr: t\nstatus: active\nowner: x\n"
            "updated: 2026-09-18\nsurface: watts\nprovenance: p\n---\n\n"
            f"sources:\n{rows}"
        ))

    def test_duplicate_source_with_same_owner_is_an_error(self):
        self.write_manifest(
            "  - sourceId: apollo\n    kind: mcp\n    reach: readable\n    authorization: live\n"
            "    state: pending\n    lastObservedAt: 2026-09-18\n    suppressionSurface: no\n"
            "    covers: c\n    doesNotCover: d\n    privacy: private\n    datasetOwner: same-owner\n"
            "  - sourceId: apollo\n    kind: mcp\n    reach: readable\n    authorization: live\n"
            "    state: pending\n    lastObservedAt: 2026-09-18\n    suppressionSurface: no\n"
            "    covers: c\n    doesNotCover: d\n    privacy: private\n    datasetOwner: same-owner\n"
        )
        errors = self.errors()
        self.assertTrue(
            any("duplicate sourceId" in e for e in errors),
            f"duplicate source ids must be an error; got {errors}",
        )

    def test_duplicate_source_with_distinct_owners_is_an_error(self):
        self.write_manifest(
            "  - sourceId: apollo\n    kind: mcp\n    reach: readable\n    authorization: live\n"
            "    state: pending\n    lastObservedAt: 2026-09-18\n    suppressionSurface: no\n"
            "    covers: c\n    doesNotCover: d\n    privacy: private\n    datasetOwner: owner-one\n"
            "  - sourceId: apollo\n    kind: mcp\n    reach: readable\n    authorization: live\n"
            "    state: pending\n    lastObservedAt: 2026-09-18\n    suppressionSurface: no\n"
            "    covers: c\n    doesNotCover: d\n    privacy: private\n    datasetOwner: owner-two\n"
        )
        self.assert_error_contains("duplicate sourceId")


if __name__ == "__main__":
    unittest.main()
