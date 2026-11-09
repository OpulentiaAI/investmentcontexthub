"""Watts automation spec contract: disabled, scheduled, guarded prompts."""
from pathlib import Path
import re
import unittest

SPECS = Path(__file__).resolve().parents[1] / "automations"

class AutomationSpecContract(unittest.TestCase):
    def test_every_spec_is_disabled_guarded_and_scheduled(self):
        specs = sorted(SPECS.glob("*.md"))
        self.assertGreaterEqual(len(specs), 6)
        for path in specs:
            with self.subTest(spec=path.name):
                text = path.read_text()
                self.assertIn('enabled: "no"', text)
                self.assertIn('firstOpenChecked: "no"', text)
                self.assertIn("costCeilingUsd:", text)
                self.assertIn("```text", text)
                self.assertIn("CAUTION:", text)
                self.assertRegex(text, r"(?m)^Trigger: .+America/Chicago")
                self.assertIn("same automation role", text)
                self.assertIn("validated successful artifact and run receipt", text)
                self.assertIn("# Forbidden Actions", text)

if __name__ == "__main__":
    unittest.main()
