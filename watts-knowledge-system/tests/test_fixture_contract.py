"""Fixture-driven tests.

Worker A's fixtures declare, in their own frontmatter, the error each bad case
must produce:

    expectError: "<substring of the validator error>"

These tests honour that contract. Every `fixtures/bad/*.md` is dropped into a
scanned directory of a temp hub — alongside the good fixtures so its wikilinks
resolve — and the validator must produce the named error. A bad fixture that
passes validation is a fixture that is not testing anything.

Good fixtures get the mirror treatment: each must validate cleanly.
"""
from __future__ import annotations

import pathlib
import shutil
import tempfile
import unittest

from tests.support import REPO, VALIDATE

GOOD_DIR = REPO / "fixtures" / "good"
BAD_DIR = REPO / "fixtures" / "bad"
EXPECT_ERROR = "expectError:"


def bad_cases() -> list[pathlib.Path]:
    if not BAD_DIR.is_dir():
        return []
    return sorted(BAD_DIR.glob("*.md"))


def good_cases() -> list[pathlib.Path]:
    if not GOOD_DIR.is_dir():
        return []
    return sorted(GOOD_DIR.glob("*.md"))


class FixtureContract(unittest.TestCase):
    """Consume worker A's fixture contract directly, rather than restating it."""

    def build_hub(self) -> pathlib.Path:
        root = pathlib.Path(tempfile.mkdtemp(prefix="hub-fixtures-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        # The real type declarations: these fixtures must be checked against the
        # actual ontology, not a copy that can drift.
        shutil.copytree(REPO / "type", root / "type")
        for d in ("signals", "research", "entities"):
            (root / d).mkdir(parents=True, exist_ok=True)
        # Good fixtures live in a scanned directory so bad-case wikilinks resolve.
        shutil.copytree(GOOD_DIR, root / "fixtures" / "good")
        return root

    @unittest.skipIf(not good_cases(), "no good fixtures yet")
    def test_good_fixtures_validate_cleanly(self):
        root = self.build_hub()
        result = VALIDATE.run_checks(hub=root)
        rel_errors = [e for e in result.errors if "fixtures/good" in e]
        self.assertEqual(rel_errors, [], f"good fixtures must be clean; got {rel_errors}")

    @unittest.skipIf(not bad_cases(), "no bad fixtures yet")
    def test_every_bad_fixture_declares_an_expectation(self):
        for path in bad_cases():
            text = path.read_text(encoding="utf-8")
            self.assertIn(
                EXPECT_ERROR, text,
                f"{path.name} is in fixtures/bad but declares no expectError",
            )

    @unittest.skipIf(not bad_cases(), "no bad fixtures yet")
    def test_bad_fixtures_produce_their_expected_error(self):
        # All bad fixtures go in together: cross-fixture rules such as duplicate
        # detection only fire when both halves of the duplicate are present.
        root = self.build_hub()
        for path in bad_cases():
            shutil.copy(path, root / "signals" / path.name)
        result = VALIDATE.run_checks(hub=root)
        failures = []
        for path in bad_cases():
            text = path.read_text(encoding="utf-8")
            expected = ""
            for line in text.splitlines():
                if line.startswith(EXPECT_ERROR):
                    expected = line.split(":", 1)[1].strip().strip('"').strip("'")
                    break
            if not expected:
                continue
            if not any(expected in e for e in result.errors):
                failures.append(f"{path.name}: expected an error containing {expected!r}")
        self.assertEqual(failures, [], "\n".join(failures) + "\n\nAll errors:\n" + "\n".join(result.errors))


class CoverageGuardrail(unittest.TestCase):
    """Connected sources without a manifest are an error, not a reminder."""

    def test_repo_has_a_manifest_for_every_connected_source(self):
        result = VALIDATE.run_checks(hub=REPO)
        connectors = list((REPO / "entities" / "connectors").glob("*.md"))
        connected = [
            p for p in connectors
            if VALIDATE.scalar(VALIDATE.parse_frontmatter(p.read_text(encoding="utf-8")).get("connected", "")) == "yes"
        ]
        manifests = list((REPO / "entities").glob("*source-manifest*.md"))
        self.assertTrue(manifests, "connected sources require a source manifest")
        self.assertFalse(
            any("no source-manifest" in e for e in result.errors),
            f"every connected source must have a manifest row; got {result.errors}",
        )

    def test_repo_build_is_clean(self):
        result = VALIDATE.run_checks(hub=REPO)
        self.assertEqual(result.errors, [], f"repository must validate clean; got {result.errors}")


class Baseline(unittest.TestCase):
    """The regression floor: the checks pass on the real tree."""

    def test_expected_types_present(self):
        types = VALIDATE.load_types(REPO)
        for name in ("wks.source-manifest", "wks.extraction-run", "wks.experiment",
                     "wks.warm-path", "wks.search-run", "wks.award"):
            self.assertIn(name, types, f"{name} must be declared")

    def test_manifest_type_separates_authorization_from_reach(self):
        body = (REPO / "type" / "wks.source-manifest.type.yaml").read_text(encoding="utf-8")
        self.assertRegex(body, r"authorization\??:")
        self.assertRegex(body, r"reach\??:")
        self.assertIn("past-use", body,
                      "registry state is not permission; past use must be representable")
        self.assertRegex(body, r"datasetOwner\??:",
                         "different people's datasets must stay separable")


if __name__ == "__main__":
    unittest.main()
