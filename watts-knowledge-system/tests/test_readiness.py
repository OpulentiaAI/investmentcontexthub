import datetime as dt
import hashlib
import json
import pathlib
import tempfile
import unittest

from scripts.readiness import readiness


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.now = dt.datetime(2026, 9, 24, 12, tzinfo=dt.timezone.utc)
        self.expected = {"ownerId": "synthetic-owner", "workspaceId": "synthetic-workspace",
                         "repo": "example.invalid/synthetic"}
        base = {"ownerId": "synthetic-owner", "observedAt": "2026-09-24T11:00:00Z"}
        self.proofs = {
            "owner": {**base, "unique": True, "readOnly": True},
            "workspace": {**base, "workspaceId": "synthetic-workspace", "unique": True},
            "runtime": {**base, "workspaceId": "synthetic-workspace", "repo": "example.invalid/synthetic",
                        "workspaceBound": True, "contextMounted": True, "threadId": "synthetic-thread",
                        "nativeCreate": {"success": True, "workspaceId": "synthetic-workspace",
                                         "id": "synthetic-thread", "threadId": "synthetic-thread"}},
            "sources": {**base, "workspaceId": "synthetic-workspace",
                        "ownerScopeVerified": True, "workspaceTargetVerified": True,
                        "mappingComplete": True, "inventoryComplete": True,
                        "paginationComplete": True,
                        "sources": [{"sourceId": "synthetic", "mapped": True, "connected": True}]},
        }
        self.intake = self.root / "intake.json"
        self.save()

    def save(self):
        entries = {}
        for name, data in self.proofs.items():
            path = self.root / f"{name}.json"
            payload = json.dumps(data).encode()
            path.write_bytes(payload)
            entries[name] = {"path": str(path), "sha256": hashlib.sha256(payload).hexdigest()}
        self.intake.write_text(json.dumps({"starter": {"slug": "watts-source-manifest-review",
                                                    "paidToolsEnabled": False}, "observations": entries}))

    def test_valid_observed_prerequisites_reach_ready_without_running_services(self):
        self.assertEqual(readiness(self.intake, self.expected, self.now)["status"], "READY")

    def test_missing_unbound_or_stale_evidence_blocks(self):
        cases = [("runtime", "workspaceBound", False),
                 ("sources", "ownerScopeVerified", False),
                 ("sources", "mappingComplete", False),
                 ("owner", "observedAt", "2026-09-20T00:00:00Z")]
        for name, key, value in cases:
            with self.subTest(name=name, key=key):
                original = self.proofs[name][key]
                self.proofs[name][key] = value
                self.save()
                self.assertEqual(readiness(self.intake, self.expected, self.now)["status"], "BLOCKED")
                self.proofs[name][key] = original

    def test_tampered_hash_blocks(self):
        (self.root / "owner.json").write_text("{}")
        self.assertIn("owner: evidence hash mismatch", readiness(self.intake, self.expected, self.now)["reasons"])

    def test_same_owner_snapshot_from_another_workspace_blocks(self):
        self.proofs["sources"]["workspaceId"] = "other-client-workspace"
        self.save()
        result = readiness(self.intake, self.expected, self.now)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(any("sources:" in reason for reason in result["reasons"]))

    def test_nonobject_intake_and_evidence_block_without_traceback(self):
        for value in (None, [], ["synthetic"]):
            with self.subTest(intake=value):
                self.intake.write_text(json.dumps(value))
                self.assertEqual(readiness(self.intake, self.expected, self.now)["status"], "BLOCKED")
        for value in (None, [], {"observedAt": 123}):
            with self.subTest(proof=value):
                self.save()
                payload = json.dumps(value).encode()
                path = self.root / "sources.json"
                path.write_bytes(payload)
                intake = json.loads(self.intake.read_text())
                intake["observations"]["sources"]["sha256"] = hashlib.sha256(payload).hexdigest()
                self.intake.write_text(json.dumps(intake))
                self.assertEqual(readiness(self.intake, self.expected, self.now)["status"], "BLOCKED")

    def test_paid_role_is_not_ready_without_real_cost_enforcement(self):
        data = json.loads(self.intake.read_text())
        data["starter"]["slug"] = "watts-contact-enrichment"
        data["starter"]["paidToolsEnabled"] = True
        self.intake.write_text(json.dumps(data))
        self.assertEqual(readiness(self.intake, self.expected, self.now)["status"], "BLOCKED")

    def test_missing_or_empty_expected_binding_blocks(self):
        for key in self.expected:
            with self.subTest(key=key):
                expected = {**self.expected, key: ""}
                self.assertEqual(readiness(self.intake, expected, self.now)["status"], "BLOCKED")

    def test_runtime_requires_actual_matching_native_thread_identity(self):
        for key, value in (("threadId", None), ("threadId", ""), ("threadId", "other-thread")):
            with self.subTest(key=key, value=value):
                original = self.proofs["runtime"].get(key)
                if value is None:
                    self.proofs["runtime"].pop(key)
                else:
                    self.proofs["runtime"][key] = value
                self.save()
                self.assertEqual(readiness(self.intake, self.expected, self.now)["status"], "BLOCKED")
                self.proofs["runtime"][key] = original
        for value in (None, "", "other-thread"):
            with self.subTest(native_thread=value):
                original = self.proofs["runtime"]["nativeCreate"].pop("threadId")
                if value is not None:
                    self.proofs["runtime"]["nativeCreate"]["threadId"] = value
                self.save()
                self.assertEqual(readiness(self.intake, self.expected, self.now)["status"], "BLOCKED")
                self.proofs["runtime"]["nativeCreate"]["threadId"] = original

    def test_source_rows_require_unique_mapped_id_and_known_connection_state(self):
        invalid_rows = ([{}], [{"sourceId": "synthetic", "connected": True}],
                        [{"sourceId": "synthetic", "mapped": False, "connected": True}],
                        [{"sourceId": "synthetic", "mapped": True, "connected": None}],
                        [{"sourceId": "synthetic", "mapped": True, "connected": "yes"}],
                        [{"sourceId": "synthetic", "mapped": True, "connected": True}] * 2,
                        ["not-a-row"])
        original = self.proofs["sources"]["sources"]
        for rows in invalid_rows:
            with self.subTest(rows=rows):
                self.proofs["sources"]["sources"] = rows
                self.save()
                self.assertEqual(readiness(self.intake, self.expected, self.now)["status"], "BLOCKED")
        self.proofs["sources"]["sources"] = original
