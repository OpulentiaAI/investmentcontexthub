"""Tests for the dry-run automation loop.

"Disabled" is only a real property if a tick proves it. These tests assert the
loop runs, records effects instead of performing them, and fails closed when it
should.
"""
from __future__ import annotations

import importlib.util
import pathlib
import shutil
import sys
import tempfile
import unittest

from tests.support import REPO

TICK_PATH = REPO / "scripts" / "hub_tick.py"


def load_tick():
    spec = importlib.util.spec_from_file_location("hub_tick", TICK_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["hub_tick"] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop("hub_tick", None)
        raise
    return module


TICK = load_tick()

AUTOMATION = """---
type: wks.automation
tldr: t
status: draft
owner: Derrick Watts
updated: 2026-09-18
surface: watts
provenance: p
slug: {slug}
uses: []
schedule:
  tldr: weekday cron
  kind: cron
  expression: "0 7 * * 1-5"
  timezone: America/Chicago
  source: opulent-native
mode: {mode}
confirmWord: send
firstOpenChecked: "{checked}"
enabled: "{enabled}"
costCeilingUsd: 1
producesArtifact: "{artifact}"
loopGuard: "If today's artifact exists, stop."
---

# {slug}

# Overview
Test automation.

# Prompt
```text
Create an Opulent automation named "test".

Never send outbound mail. Never contact them directly.

1. Read the hub.
2. If the artifact for today already exists, stop.
3. Write "{artifact}".
4. Draft one opener per row with send_ready: false.
5. Then send the digest to the operator's own address, which is delivery to him.

CAUTION: Never send. Never enable a clock. Never invent a value.
```

# Forbidden Actions
- Do not send
"""


class TickCase(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="hub-tick-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        (self.root / "automations").mkdir(parents=True)
        (self.root / "entities").mkdir(parents=True)
        for t in sorted((REPO / "type").glob("*.type.yaml")):
            (self.root / "type").mkdir(exist_ok=True)
            shutil.copy(t, self.root / "type" / t.name)

    def add(self, slug: str, enabled="no", checked="no", mode="draft-then-wait",
            artifact="out-2026-01-01.md", extra_step=""):
        text = AUTOMATION.format(slug=slug, mode=mode, enabled=enabled,
                                 checked=checked, artifact=artifact)
        if extra_step:
            text = text.replace("\nCAUTION:", f"\n{extra_step}\n\nCAUTION:")
        (self.root / "automations" / f"{slug}.md").write_text(text, encoding="utf-8")

    def ticks(self):
        return [TICK.tick(a, self.root) for a in TICK.load_automations(self.root)]


class DryRunContract(TickCase):
    def test_a_disabled_automation_ticks_without_performing_anything(self):
        self.add("solo")
        ticks = self.ticks()
        self.assertEqual(len(ticks), 1)
        self.assertEqual(ticks[0]["status"], "ok")
        self.assertTrue(all(i["disposition"] == "blocked" for i in ticks[0]["intents"]))

    def test_effect_language_outside_caution_is_recorded_as_blocked_intent(self):
        self.add("solo")
        kinds = {i["kind"] for i in self.ticks()[0]["intents"]}
        self.assertIn("send", kinds,
                      "a non-CAUTION send phrase is a real intent and must be recorded")

    def test_contact_language_outside_caution_is_also_recorded(self):
        self.add("solo", extra_step="6. Reach out to the hiring manager once the list is approved.")
        kinds = {i["kind"] for i in self.ticks()[0]["intents"]}
        self.assertIn("contact", kinds)

    def test_caution_line_is_not_read_as_an_intent(self):
        # "Never send" is a guard. Reading it as an intent would be a false positive.
        self.add("solo")
        matches = {i.get("match") for i in self.ticks()[0]["intents"]}
        self.assertNotIn("enable send", matches)

    def test_enabled_without_first_open_is_a_violation(self):
        self.add("risky", enabled="yes", checked="no")
        self.assertIsNotNone(TICK.violations(TICK.load_automations(self.root)[0]))
        self.assertEqual(self.ticks()[0]["status"], "violation")

    def test_enabled_with_first_open_checked_is_blocked_without_cost_authorizer(self):
        self.add("fine", enabled="yes", checked="yes")
        self.assertIn("without a local cost authorizer", TICK.violations(TICK.load_automations(self.root)[0]))

    def test_existing_artifact_makes_the_tick_a_noop(self):
        self.add("solo", artifact="done-2026-01-01.md")
        (self.root / "done-2026-01-01.md").write_text("already ran", encoding="utf-8")
        self.assertEqual(self.ticks()[0]["status"], "no-op")

    def test_missing_manifest_is_reported_as_a_failed_precondition(self):
        self.add("solo")
        checks = {c["check"]: c["ok"] for c in self.ticks()[0]["preconditions"]}
        self.assertFalse(checks["source-manifest"],
                         "an absent coverage ledger must be visible, not assumed")

    def test_manifest_present_satisfies_the_precondition(self):
        self.add("solo")
        (self.root / "entities" / "source-manifest.md").write_text(
            "---\ntype: wks.source-manifest\ntldr: t\n---\n\n# M\n", encoding="utf-8")
        checks = {c["check"]: c["ok"] for c in self.ticks()[0]["preconditions"]}
        self.assertTrue(checks["source-manifest"])


class RepoLoop(unittest.TestCase):
    """The real repository must tick clean with nothing enabled."""

    def test_every_automation_ticks_and_nothing_is_enabled(self):
        automations = TICK.load_automations(REPO)
        self.assertGreaterEqual(len(automations), 6)
        for a in automations:
            self.assertEqual(a["enabled"], "no", f"{a['slug']} must not be enabled")
            self.assertIsNone(TICK.violations(a), f"{a['slug']} violates the first-open gate")

    def test_repo_tick_records_zero_performed_effects(self):
        ticks = [TICK.tick(a, REPO) for a in TICK.load_automations(REPO)]
        performed = [i for t in ticks for i in t["intents"] if i["disposition"] != "blocked"]
        self.assertEqual(performed, [], "no effect may be performed in dry-run")


if __name__ == "__main__":
    unittest.main()
