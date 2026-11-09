"""Regression coverage for reproducible, fail-closed Jev receipts."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "jev_evaluate.py"
SPEC = importlib.util.spec_from_file_location("jev_evaluate", SCRIPT)
jev_evaluate = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(jev_evaluate)


REQUEST = {
    "questionSetVersion": "watts.integration.receipt-contract.v1",
    "state": {"scenario": "synthetic protocol validation"},
    "questions": {"safe": {"type": "noul", "instructions": "Does this synthetic state describe a protocol test?"}},
    "model": "jev-latest",
}
RULES = {"safe": {"threshold": 0.8, "direction": "at_least"}}


class ReceiptContractTests(unittest.TestCase):
    def test_key_alone_never_authorizes_paid_call(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            request, output = root / "request.json", root / "receipt.json"
            request.write_text(json.dumps(REQUEST), encoding="utf-8")
            with patch.object(jev_evaluate, "call", side_effect=AssertionError("network called")) as call, \
                 patch.object(jev_evaluate.sys, "argv", ["jev_evaluate.py", "--request", str(request),
                                                        "--purpose", "synthetic test", "--out", str(output)]), \
                 patch.dict(jev_evaluate.os.environ, {"TYPESAFE_API_KEY": "synthetic"}, clear=True):
                self.assertEqual(jev_evaluate.main(), 0)
            call.assert_not_called()
            self.assertEqual(json.loads(output.read_text())["deterministicDecision"]["outcome"], "unavailable")

    def test_unavailable_receipt_keeps_reproducible_inputs(self):
        receipt = jev_evaluate.unavailable_receipt(REQUEST, RULES, "synthetic test", "no provider")
        self.assertEqual(receipt["request"], REQUEST)
        self.assertEqual(receipt["rules"], RULES)
        self.assertIsNone(receipt["response"])
        self.assertEqual(receipt["inputHash"], jev_evaluate.input_hash(REQUEST))
        self.assertEqual(receipt["deterministicDecision"]["outcome"], "unavailable")

    def test_malformed_json_writes_an_unavailable_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            request, rules, output = root / "request.json", root / "rules.json", root / "receipt.json"
            request.write_text(json.dumps(REQUEST), encoding="utf-8")
            rules.write_text(json.dumps(RULES), encoding="utf-8")
            with patch.object(jev_evaluate, "call", side_effect=json.JSONDecodeError("bad", "?", 0)), \
                 patch.object(jev_evaluate.sys, "argv", ["jev_evaluate.py", "--request", str(request), "--rules", str(rules), "--purpose", "synthetic test", "--out", str(output), "--live"]), \
                 patch.dict(jev_evaluate.os.environ, {"TYPESAFE_API_KEY": "synthetic", "CONFIRM": "send"}, clear=True):
                self.assertEqual(jev_evaluate.main(), 0)
            receipt = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(receipt["deterministicDecision"]["outcome"], "unavailable")
            self.assertEqual(receipt["request"], REQUEST)
            self.assertEqual(receipt["rules"], RULES)

    def test_protocol_shape_failure_writes_an_unavailable_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            request, output = root / "request.json", root / "receipt.json"
            request.write_text(json.dumps(REQUEST), encoding="utf-8")
            with patch.object(jev_evaluate, "call", side_effect=ValueError("missing answers")), \
                 patch.object(jev_evaluate.sys, "argv", ["jev_evaluate.py", "--request", str(request), "--purpose", "synthetic test", "--out", str(output), "--live"]), \
                 patch.dict(jev_evaluate.os.environ, {"TYPESAFE_API_KEY": "synthetic", "CONFIRM": "send"}, clear=True):
                self.assertEqual(jev_evaluate.main(), 0)
            receipt = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(receipt["deterministicDecision"]["outcome"], "unavailable")
            self.assertEqual(receipt["rules"], {})

    def test_private_request_is_refused_before_a_receipt_is_written(self):
        unsafe = {**REQUEST, "state": {"email": "person@example.com"}}
        with self.assertRaisesRegex(ValueError, "email address"):
            jev_evaluate.assert_public_safe(unsafe, "request")

    def test_private_provider_response_becomes_unavailable_not_persisted(self):
        with self.assertRaisesRegex(ValueError, "email address"):
            jev_evaluate.assert_public_safe({"answers": {}, "echo": "person@example.com"}, "response")
