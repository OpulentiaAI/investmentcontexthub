import datetime as dt
import hashlib
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

import scripts.source_review_cycle as worker
from scripts.source_review_cycle import cycle


class SourceReviewCycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.spec = self.root / "spec.md"
        self.spec.write_text("---\nslug: watts-source-manifest-review\n---\n")
        self.manifest = self.root / "manifest.md"
        self.manifest.write_text("# Manifest\n\nsources:\n  - sourceId: spear\n"
                                 "    state: pending\n    doesNotCover: mailbox\n")
        self.snapshot = self.root / "snapshot.json"
        self.now = dt.datetime(2026, 9, 24, 12, tzinfo=dt.timezone.utc)
        self.data = {"ownerScopeVerified": True, "workspaceTargetVerified": True,
                     "inventoryComplete": True, "paginationComplete": True, "mappingComplete": True,
                     "observedAt": "2026-09-24T11:00:00Z",
                     "sources": [{"sourceId": "spear", "connected": True}]}
        self.save()

    def save(self):
        payload = json.dumps(self.data).encode()
        self.snapshot.write_bytes(payload)
        (self.root / "observation-receipt.json").write_text(json.dumps({
            "mode": "read-only-capability-metadata",
            "sha256": {"sources": hashlib.sha256(payload).hexdigest()},
        }))

    def run_cycle(self, run_id="cycle-one"):
        return cycle(run_id, self.snapshot, self.root / "runs", self.spec, self.manifest, self.now)

    def test_valid_snapshot_produces_proven_artifact_and_is_idempotent(self):
        first = self.run_cycle()
        self.assertEqual(first["status"], "succeeded")
        self.assertEqual(first["attempt"], 1)
        self.assertEqual(self.run_cycle(), first)
        self.assertIn("coverage UNVERIFIED", (self.root / "runs/cycle-one/source-manifest-review.md").read_text())

    def test_missing_snapshot_blocks_then_retries_same_run(self):
        self.snapshot.unlink()
        blocked = self.run_cycle()
        self.assertEqual(blocked["status"], "blocked")
        self.assertFalse((self.root / "runs/cycle-one/source-manifest-review.md").exists())
        self.save()
        recovered = self.run_cycle()
        self.assertEqual(recovered["status"], "succeeded")
        self.assertEqual(recovered["attempt"], 2)

    def test_unreceipted_or_tampered_snapshot_does_not_complete(self):
        (self.root / "observation-receipt.json").unlink()
        self.assertEqual(self.run_cycle()["status"], "blocked")
        self.save()
        self.snapshot.write_text('{"changed":true}')
        self.assertEqual(self.run_cycle()["status"], "blocked")

    def test_stale_unknown_or_duplicate_snapshot_fails_closed(self):
        for change in ({"observedAt": "2026-09-22T00:00:00Z"},
                       {"ownerScopeVerified": False},
                       {"sources": self.data["sources"] * 2}):
            with self.subTest(change=change):
                self.data.update(change)
                self.save()
                self.assertEqual(self.run_cycle()["status"], "blocked")
                self.data = {"ownerScopeVerified": True, "workspaceTargetVerified": True,
                             "inventoryComplete": True, "paginationComplete": True, "mappingComplete": True,
                             "observedAt": "2026-09-24T11:00:00Z",
                             "sources": [{"sourceId": "spear", "connected": True}]}

    def test_successful_run_rejects_changed_input_and_repairs_missing_artifact(self):
        self.run_cycle()
        artifact = self.root / "runs/cycle-one/source-manifest-review.md"
        artifact.unlink()
        self.assertEqual(self.run_cycle()["attempt"], 2)
        self.data["sources"].append({"sourceId": "notion", "connected": True})
        self.save()
        with self.assertRaisesRegex(ValueError, "different inputs"):
            self.run_cycle()

    def test_partial_artifact_without_receipt_restarts_cleanly(self):
        run_dir = self.root / "runs/cycle-one"
        run_dir.mkdir(parents=True)
        (run_dir / "source-manifest-review.md").write_text("partial")
        self.assertEqual(self.run_cycle()["status"], "succeeded")
        self.assertNotEqual((run_dir / "source-manifest-review.md").read_text(), "partial")

    def test_incomplete_inventory_is_partial_and_retries_after_completion(self):
        self.data["paginationComplete"] = False
        self.save()
        result = self.run_cycle()
        self.assertEqual(result["status"], "partial")
        self.assertIn("PARTIAL", (self.root / "runs/cycle-one/source-manifest-review.md").read_text())
        self.data["paginationComplete"] = True
        self.save()
        self.assertEqual(self.run_cycle()["attempt"], 2)

    def test_unmapped_source_emits_partial_artifact_without_full_coverage_claim(self):
        self.data["mappingComplete"] = False
        self.data["sources"].append({"sourceId": "unmapped-1234567890abcdef", "connected": True,
                                      "mapped": False})
        self.save()
        receipt = self.run_cycle()
        self.assertEqual(receipt["status"], "partial")
        artifact = (self.root / "runs/cycle-one/source-manifest-review.md").read_text()
        self.assertIn("Unmapped connection", artifact)
        self.assertIn("No FULL coverage claim", artifact)

    def test_native_catalog_unknown_auth_produces_hashed_partial_receipt(self):
        self.data["inventoryComplete"] = False
        self.data["paginationComplete"] = False
        self.data["mappingComplete"] = False
        self.data["sources"] = [{"sourceId": "unmapped-1234567890abcdef", "connected": None,
                                 "reach": "unknown", "mapped": False}]
        self.save()
        receipt = self.run_cycle()
        self.assertEqual(receipt["status"], "partial")
        artifact_bytes = (self.root / "runs/cycle-one/source-manifest-review.md").read_bytes()
        self.assertEqual(receipt["artifactSha256"], hashlib.sha256(artifact_bytes).hexdigest())
        self.assertIn("unknown authentication: 1", artifact_bytes.decode())
        self.assertIn("No FULL coverage claim", artifact_bytes.decode())

    def test_artifact_write_failure_records_failed_and_retry_succeeds(self):
        actual = worker.write_atomic

        def fail_artifact(path, data):
            if path.name.endswith(".md"):
                raise OSError(28, "synthetic disk full")
            return actual(path, data)

        with patch.object(worker, "write_atomic", side_effect=fail_artifact):
            self.assertEqual(self.run_cycle()["status"], "failed")
        self.assertEqual(self.run_cycle()["status"], "succeeded")
        self.assertEqual(self.run_cycle()["attempt"], 2)

    def test_next_day_refreshed_snapshot_runs_without_owner_intake_edit(self):
        self.assertEqual(self.run_cycle()["status"], "succeeded")
        self.data["observedAt"] = "2026-09-25T11:00:00Z"
        self.save()
        self.now += dt.timedelta(days=1)
        second = self.run_cycle("cycle-two")
        self.assertEqual(second["status"], "succeeded")
        self.assertEqual(second["attempt"], 1)

    def test_cached_success_rechecks_freshness_before_skipping(self):
        self.assertEqual(self.run_cycle()["status"], "succeeded")
        self.now += dt.timedelta(days=2)
        result = self.run_cycle()
        self.assertEqual(result["status"], "blocked")
        self.assertIn("older than 24 hours", result["reason"])
        self.assertIsNone(result["artifactSha256"])

    def test_corrupt_or_wrong_run_receipt_is_not_reused_as_success(self):
        self.run_cycle()
        receipt = self.root / "runs/cycle-one/receipt.json"
        for body in ("not JSON", "[]", '{"runId":"different","status":"succeeded"}'):
            with self.subTest(body=body):
                receipt.write_text(body)
                result = self.run_cycle()
                self.assertEqual(result["runId"], "cycle-one")
                self.assertEqual(result["status"], "succeeded")
                self.assertEqual(result["attempt"], 1)

    def test_artifacts_and_run_directory_are_owner_only(self):
        self.run_cycle()
        run_dir = self.root / "runs/cycle-one"
        self.assertEqual(run_dir.stat().st_mode & 0o777, 0o700)
        for path in run_dir.iterdir():
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_symlinked_run_directory_is_refused(self):
        out = self.root / "runs"
        out.mkdir()
        (out / "cycle-one").symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.run_cycle()

    def test_report_preserves_blocker_and_flags_missing_notes(self):
        self.run_cycle()
        artifact = self.root / "runs/cycle-one/source-manifest-review.md"
        self.assertIn("MISSING: manifest row has no blocker note", artifact.read_text())
        self.manifest.write_text(self.manifest.read_text() + '    blockerNote: "Need auth | owner approval"\n')
        self.run_cycle("cycle-with-note")
        text = (self.root / "runs/cycle-with-note/source-manifest-review.md").read_text()
        self.assertIn("Need auth \\| owner approval", text)

    def test_nonobject_snapshot_and_receipt_block_without_traceback(self):
        for value in (None, [], {"observedAt": 123}):
            with self.subTest(snapshot=value):
                self.data = value
                self.save()
                self.assertEqual(self.run_cycle()["status"], "blocked")
        for value in (None, [], {"mode": "read-only-capability-metadata", "sha256": None}):
            with self.subTest(receipt=value):
                (self.root / "observation-receipt.json").write_text(json.dumps(value))
                self.assertEqual(self.run_cycle()["status"], "blocked")

    def test_missing_or_contradictory_mapping_proof_is_partial(self):
        self.data.pop("mappingComplete")
        self.save()
        self.assertEqual(self.run_cycle()["status"], "partial")
        self.data["mappingComplete"] = True
        self.data["sources"][0]["mapped"] = False
        self.save()
        self.assertEqual(self.run_cycle()["status"], "partial")
