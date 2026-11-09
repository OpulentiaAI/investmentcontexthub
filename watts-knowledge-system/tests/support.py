"""Shared helpers for the validator contract tests.

Each test builds a throwaway hub on disk, writes only the files it needs, and
runs the real checks against it. That keeps every assertion tied to the same
code path CI uses, instead of to a reimplementation of it.
"""
from __future__ import annotations

import importlib.util
import pathlib
import shutil
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
VALIDATE_PATH = REPO / "scripts" / "validate.py"


def load_validator():
    """Import scripts/validate.py as a module without installing anything."""
    spec = importlib.util.spec_from_file_location("hub_validate", VALIDATE_PATH)
    module = importlib.util.module_from_spec(spec)
    # Register before exec: @dataclass resolves its own module through sys.modules.
    sys.modules["hub_validate"] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop("hub_validate", None)
        raise
    return module


VALIDATE = load_validator()

CONNECTOR_TEMPLATE = """---
type: wks.connector
tldr: {name}
status: active
owner: Derrick Watts
updated: 2026-09-18
surface: watts
provenance: "test fixture"
slug: {slug}
kind: mcp
connected: {connected}
authOwner: user
---

# {name}
"""

TYPE_TEMPLATE = """#: Test type.
extends: [{parents}]
fields:
{fields}
"""


class HubCase(unittest.TestCase):
    """A temp hub with the minimum a check needs to run."""

    def setUp(self) -> None:
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="hub-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        for d in ("type", "entities", "entities/connectors", "automations",
                  "runbooks", "extractions", "research", "signals", "fixtures/good"):
            (self.root / d).mkdir(parents=True, exist_ok=True)
        # Run against the REAL ontology. Re-declaring types in tests lets them
        # drift from the files the repo actually ships.
        for t in sorted((REPO / "type").glob("*.type.yaml")):
            shutil.copy(t, self.root / "type" / t.name)

    def write(self, rel: str, text: str) -> pathlib.Path:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def declare_type(self, name: str, parents: str = "idea::au-base-types",
                     fields: str = "  kind?: String") -> None:
        self.write(f"type/{name}.type.yaml",
                   TYPE_TEMPLATE.format(parents=parents, fields=fields))

    def connector(self, slug: str, connected: str = "yes") -> None:
        self.write(f"entities/connectors/{slug}.md",
                   CONNECTOR_TEMPLATE.format(name=slug.title(), slug=slug, connected=connected))

    def instance(self, rel: str, type_name: str, extra: str = "", body: str = "\n# Body\n") -> None:
        self.write(rel, (
            "---\n"
            f"type: {type_name}\n"
            f"tldr: test instance\n"
            "status: active\n"
            "owner: Derrick Watts\n"
            "updated: 2026-09-18\n"
            "surface: watts\n"
            'provenance: "test fixture"\n'
            f"{extra}"
            "---\n"
            f"{body}"
        ))

    def check(self):
        return VALIDATE.run_checks(hub=self.root)

    def errors(self) -> list[str]:
        return self.check().errors

    def warnings(self) -> list[str]:
        return self.check().warnings

    def assert_error_contains(self, needle: str) -> None:
        found = self.errors()
        self.assertTrue(
            any(needle in e for e in found),
            f"expected an error containing {needle!r}; got {found}",
        )

    def assert_no_error_containing(self, needle: str) -> None:
        found = [e for e in self.errors() if needle in e]
        self.assertEqual(found, [], f"did not expect an error containing {needle!r}")
