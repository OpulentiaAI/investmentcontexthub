import datetime as dt
import unittest
from unittest.mock import patch

from scripts import capture_native_binding as native


class NativeBindingTests(unittest.TestCase):
    def setUp(self):
        self.binding = {"OPERATOR_ACCOUNT_ID": "synthetic-owner",
                        "OPERATOR_WORKSPACE_ID": "synthetic-workspace"}
        self.response = {"success": True, "workspaceId": "synthetic-workspace",
                         "id": "synthetic-thread", "threadId": "synthetic-thread"}

    def test_host_create_result_yields_workspace_bound_receipt(self):
        receipt = native.capture(self.response, self.binding, "example.invalid/repo",
                                 dt.datetime(2026, 9, 24, tzinfo=dt.timezone.utc), mounted=True)
        self.assertEqual(receipt["threadId"], "synthetic-thread")
        self.assertEqual(receipt["nativeCreate"], self.response)
        self.assertIs(receipt["contextMounted"], True)

    def test_wrong_or_ambiguous_create_result_is_rejected(self):
        for response in ({**self.response, "success": False},
                         {**self.response, "workspaceId": "another-workspace"},
                         {**self.response, "threadId": ""}):
            with self.subTest(response=response), self.assertRaises(ValueError):
                native.capture(response, self.binding, "example.invalid/repo", mounted=True)

    def test_missing_hub_attachment_blocks_binding_capture(self):
        with patch.object(native.materialize, "collect", return_value=[
                (native.HUB / "entities" / "missing.md", "knowledge", "entities")]), \
             patch.object(native.materialize, "inventory", return_value={}), \
             patch.object(native.materialize, "workspace_attached_ids", return_value=(set(), set())):
            with self.assertRaisesRegex(RuntimeError, "not fully attached"):
                native.mounted_context(self.binding)
