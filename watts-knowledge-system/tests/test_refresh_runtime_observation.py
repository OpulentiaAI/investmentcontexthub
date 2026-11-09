import datetime as dt
import hashlib
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from scripts import refresh_runtime_observation as observation


class RuntimeObservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = pathlib.Path(self.temp.name) / "private"
        self.binding = {"OPERATOR_ACCOUNT_ID": "synthetic-owner",
                        "OPERATOR_WORKSPACE_ID": "synthetic-workspace",
                        "OPERATOR_DEPLOYMENT": "test:synthetic"}
        self.rows = [{"providerId": "mcp:connector-opaque", "kind": "mcp",
                      "connected": True, "connectionId": "private-id"},
                     {"providerId": "native:integration", "kind": "native",
                      "connected": False, "connectionId": "private-id-2"},
                     {"providerId": "native:integration", "kind": "connected_account",
                      "connected": True, "connectionId": "private-id-3"}]
        self.mapping = {"ownerId": "synthetic-owner", "workspaceId": "synthetic-workspace",
                        "connections": {"private-id": "spear", "private-id-2": "parallel",
                                        "private-id-3": "mesa"}}
        self.map_file = pathlib.Path(self.temp.name) / "mapping.json"
        self.map_file.write_text(json.dumps(self.mapping))

    def test_read_only_host_calls_write_hashed_safe_metadata_each_day(self):
        with patch.object(observation.pilot, "identity", return_value=self.binding) as identity, \
                patch.object(observation.pilot, "convex_read", return_value=self.rows) as read, \
                patch.object(observation.pilot, "required", side_effect=lambda name:
                             str(self.map_file) if name == "OPERATOR_SOURCE_MAP" else self.temp.name):
            first = observation.refresh(self.out, dt.datetime(2026, 9, 24, 12, tzinfo=dt.timezone.utc))
            second = observation.refresh(self.out, dt.datetime(2026, 9, 25, 12, tzinfo=dt.timezone.utc))
        self.assertEqual(identity.call_count, 2)
        self.assertEqual(read.call_count, 2)
        self.assertEqual(read.call_args.args[:2],
                         ("mcpConnectors:listInstalledCapabilitiesInternal", {"userId": "synthetic-owner"}))
        self.assertNotEqual(first["sha256"]["sources"], second["sha256"]["sources"])
        saved = (self.out / "sources.json").read_bytes()
        self.assertEqual(hashlib.sha256(saved).hexdigest(), second["sha256"]["sources"])
        self.assertNotIn("private-id", saved.decode())
        self.assertEqual([row["sourceId"] for row in json.loads(saved)["sources"]],
                         ["spear", "parallel", "mesa"])
        receipt = json.loads((self.out / "observation-receipt.json").read_text())
        self.assertEqual(receipt["sha256"]["sources"], second["sha256"]["sources"])

    def test_empty_duplicate_or_malformed_capabilities_block(self):
        for rows in ([], [{"providerId": "mcp:opaque", "connectionId": "private-id", "connected": "yes"}],
                     [self.rows[0], self.rows[0]]):
            with self.subTest(rows=rows), self.assertRaises(RuntimeError):
                observation.normalize_capabilities(rows, "synthetic-owner", "synthetic-workspace",
                                                   self.mapping, "2026-09-24T12:00:00Z")

    def test_unmapped_mcp_connection_is_partial_not_inferred_from_provider_name(self):
        mapping = {**self.mapping, "connections": {"private-id-2": "parallel", "private-id-3": "mesa"}}
        snapshot = observation.normalize_capabilities(self.rows, "synthetic-owner", "synthetic-workspace",
                                                      mapping, "2026-09-24T12:00:00Z")
        self.assertIs(snapshot["mappingComplete"], False)
        self.assertTrue(snapshot["sources"][0]["sourceId"].startswith("unmapped-"))
        self.assertIs(snapshot["sources"][0]["mapped"], False)
        self.assertNotEqual(snapshot["sources"][1]["sourceId"], snapshot["sources"][2]["sourceId"])

    def test_plain_list_does_not_prove_complete_inventory_or_project_arbitrary_fields(self):
        self.rows[0]["kind"] = {"private": "must-not-project"}
        snapshot = observation.normalize_capabilities(self.rows, "synthetic-owner", "synthetic-workspace",
                                                      self.mapping, "2026-09-24T12:00:00Z")
        self.assertIs(snapshot["mappingComplete"], True)
        self.assertIs(snapshot["inventoryComplete"], False)
        self.assertIs(snapshot["paginationComplete"], False)
        self.assertNotIn("must-not-project", json.dumps(snapshot))
