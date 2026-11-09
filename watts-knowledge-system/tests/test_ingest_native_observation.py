import copy
import json
import pathlib
import tempfile
import unittest

from scripts import ingest_native_observation as native
from scripts.source_review_cycle import review
import datetime as dt


class NativeIngestionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.workspace = {"success": True, "workspace": {
            "workspaceId": "synthetic-workspace", "userId": "synthetic-owner"}, "threadCount": 1}
        self.mesa = {"success": True, "repo_id": "synthetic-thread-repo", "truncated": False,
                     "data": {"id": "synthetic-thread-repo", "org": "synthetic", "name": "repo",
                              "upstream": {"url": "https://github.com/example.invalid/synthetic.git",
                                           "auth_kind": None, "latest_sync": None}}}
        self.capabilities = {"success": True, "integrations": [
            {"slug": "shared-provider", "name": "Shared", "installed": True,
             "connection_ids": ["private-native-id", "private-account-id"],
             "runs": "native", "settings_path": "/settings"},
            {"slug": "no-id", "name": "No ID", "installed": True,
             "runs": "native", "settings_path": "/settings"}],
            "mcp_servers": [{"slug": "opaque-connector", "name": "MCP", "installed": True,
                             "server": "opaque", "settings_path": "/settings"}],
            "connected_apps": [{"slug": "app", "name": "App", "installed": True,
                                "server": "opaque-app", "status": "ready", "settings_path": "/settings"}]}
        self.refs = {"workspace": "workspace_manage:get", "mesa": "mesa_get_overview",
                     "capabilities": "list_integrations:installed"}
        self.mapping = {"ownerId": "synthetic-owner", "workspaceId": "synthetic-workspace",
                        "connections": {"private-native-id": "parallel", "private-account-id": "mesa"}}

    def ingest(self):
        return native.ingest(self.workspace, self.mesa, self.capabilities, self.refs,
                             self.mapping, "synthetic-owner", "synthetic-workspace",
                             "example.invalid/synthetic", "2026-09-24T12:00:00Z")

    def test_public_projections_are_partial_and_do_not_prove_authentication(self):
        record = self.ingest()
        sources = record["sources"]
        self.assertEqual([s["sourceId"] for s in sources["sources"][:2]], ["parallel", "mesa"])
        self.assertTrue(all(s["connected"] is None and s["reach"] == "unknown"
                            for s in sources["sources"]))
        self.assertFalse(sources["inventoryComplete"])
        self.assertFalse(sources["mappingComplete"])
        self.assertEqual(len(sources["sources"]), 5)
        self.assertNotIn("private-native-id", json.dumps(record))
        self.assertNotIn("opaque-app", json.dumps(record))
        artifact = review(sources, [{"sourceId": "parallel", "state": "pending", "reach": "unknown"}],
                          dt.datetime(2026, 9, 24, 12, tzinfo=dt.timezone.utc))
        self.assertIn("Catalog projection only; authentication and reach UNVERIFIED", artifact)
        self.assertIn("No FULL coverage claim", artifact)
        self.assertIn("unknown authentication: 5", artifact)

    def test_missing_identity_and_duplicate_provider_are_not_collapsed(self):
        self.mapping["connections"].pop("private-native-id")
        sources = self.ingest()["sources"]["sources"]
        self.assertTrue(sources[0]["sourceId"].startswith("unmapped-"))
        self.assertNotEqual(sources[0]["sourceId"], sources[1]["sourceId"])
        self.assertNotEqual(sources[2]["sourceId"], sources[3]["sourceId"])

    def test_missing_connection_ids_cannot_be_mapped_by_provider_slug(self):
        self.capabilities["integrations"][0].pop("connection_ids")
        self.mapping["connections"]["shared-provider"] = "parallel"
        sources = self.ingest()["sources"]["sources"]
        self.assertTrue(sources[0]["sourceId"].startswith("unmapped-"))
        self.assertTrue(all(s["mapped"] is False for s in sources))

    def test_all_visible_connection_ids_mapped_still_does_not_prove_full_inventory(self):
        self.capabilities["integrations"].pop()
        self.capabilities["mcp_servers"] = []
        self.capabilities["connected_apps"] = []
        observed = self.ingest()["sources"]
        self.assertTrue(observed["mappingComplete"])
        self.assertFalse(observed["inventoryComplete"])
        self.assertFalse(observed["paginationComplete"])
        self.assertTrue(all(s["connected"] is None for s in observed["sources"]))

    def test_wrong_owner_workspace_mesa_upstream_or_envelope_blocks(self):
        mutations = (
            lambda: self.workspace["workspace"].update(workspaceId="other"),
            lambda: self.workspace["workspace"].update(userId="other"),
            lambda: self.mesa["data"].update(upstream=None),
            lambda: self.mesa["data"]["upstream"].update(url="https://other.example/example.invalid/synthetic"),
            lambda: self.mesa.update(truncated=True),
            lambda: self.capabilities.pop("mcp_servers"),
            lambda: self.refs.update(capabilities="mcpConnectors:listInstalledCapabilitiesInternal"),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                originals = copy.deepcopy((self.workspace, self.mesa, self.capabilities, self.refs))
                mutate()
                with self.assertRaises(ValueError):
                    self.ingest()
                self.workspace, self.mesa, self.capabilities, self.refs = originals

    def test_duplicate_connection_identity_or_non_installed_row_blocks(self):
        self.capabilities["integrations"].append({"slug": "other", "installed": True,
                                                    "connection_ids": ["private-native-id"]})
        with self.assertRaises(ValueError):
            self.ingest()
        self.capabilities["integrations"].pop()
        self.capabilities["integrations"][0]["installed"] = False
        with self.assertRaises(ValueError):
            self.ingest()
