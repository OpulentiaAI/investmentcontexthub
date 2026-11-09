import datetime as dt
import json
import pathlib
import os
import stat
import tempfile
import unittest
from unittest.mock import patch

from scripts.export_native_automation import HUB, export, main


class NativeExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.spec = HUB / "automations/source-manifest-review.md"
        self.binding = self.root / "binding.json"
        self.recurrence = self.root / "recurrence.json"
        self.expected = {"ownerId": "synthetic-owner", "workspaceId": "synthetic-workspace",
                         "repo": "example.invalid/synthetic"}
        self.now = dt.datetime(2026, 9, 24, 12, tzinfo=dt.timezone.utc)
        self.target = {**self.expected, "threadId": "synthetic-thread", "ownerVerified": True,
                       "workspaceBound": True, "contextMounted": True,
                       "observedAt": "2026-09-24T11:00:00Z",
                       "nativeCreate": {"success": True, "workspaceId": "synthetic-workspace",
                                        "id": "synthetic-thread", "threadId": "synthetic-thread"}}
        self.schedule = {"slug": "watts-source-manifest-review", "cron": "0 8 * * 1",
                         "timezone": "America/Chicago", "approved": True, "hostParsedEquivalent": True,
                         "rrule": "DTSTART;TZID=America/Chicago:20260928T080000\nRRULE:FREQ=WEEKLY;BYDAY=MO;BYHOUR=8;BYMINUTE=0"}
        self.save()

    def save(self):
        self.binding.write_text(json.dumps(self.target))
        self.recurrence.write_text(json.dumps(self.schedule))

    def run_export(self):
        return export(self.spec, self.binding, self.recurrence, self.expected, self.now)

    def test_disabled_single_action_targets_same_workspace_thread_on_repeat(self):
        payload = self.run_export()
        self.assertEqual(payload, self.run_export())
        self.assertEqual(payload["action"], "create")
        self.assertIs(payload["enabled"], False)
        self.assertEqual(payload["triggers"][0]["event_type"], "schedule:recurring")
        self.assertEqual(payload["triggers"][0]["conditions"]["any"][0]["all"][0]["field"], "rrule")
        self.assertEqual(len(payload["actions"]), 1)
        action = payload["actions"][0]
        self.assertEqual((action["type"], action["target_session_id"]), ("message_session", "synthetic-thread"))
        self.assertNotIn("Create an Opulent automation", action["prompt"])
        self.assertIn("At EVERY firing", action["prompt"])
        self.assertIn("NATIVE READ-ONLY", action["prompt"])
        self.assertIn("scripts/ingest_native_observation.py", action["prompt"])
        self.assertNotIn("CONVEX_DEPLOY_KEY", action["prompt"])
        self.assertNotIn("OPULENT_FRONTEND", action["prompt"])
        self.assertNotIn("auto_create", json.dumps(payload))
        self.assertNotIn("replies", action)

    def test_wrong_owner_or_workspace_and_unverified_recurrence_fail(self):
        for key, value in (("ownerId", "wrong"), ("workspaceId", "wrong"),
                           ("ownerVerified", False), ("workspaceBound", False),
                           ("contextMounted", False)):
            with self.subTest(key=key):
                self.target[key] = value
                self.save()
                with self.assertRaisesRegex(ValueError, "binding is unverified"):
                    self.run_export()
                self.target[key] = self.expected.get(key, True)
        self.schedule["hostParsedEquivalent"] = False
        self.save()
        with self.assertRaisesRegex(ValueError, "host-parsed"):
            self.run_export()

    def test_stale_binding_and_schedule_mismatch_fail_closed(self):
        self.target["observedAt"] = "2026-09-20T11:00:00Z"
        self.save()
        with self.assertRaisesRegex(ValueError, "stale"):
            self.run_export()
        self.target["observedAt"] = "2026-09-24T11:00:00Z"
        self.schedule["cron"] = "0 9 * * 1"
        self.save()
        with self.assertRaisesRegex(ValueError, "recurrence"):
            self.run_export()

    def test_fixed_utc_recurrence_is_not_local_canonical_time(self):
        self.schedule["rrule"] = "DTSTART:20260928T130000Z\nRRULE:FREQ=WEEKLY;BYDAY=MO;BYHOUR=13;BYMINUTE=0"
        self.save()
        with self.assertRaisesRegex(ValueError, "recurrence"):
            self.run_export()

    def test_cli_writes_owner_only_payload_without_following_existing_symlink(self):
        self.target["observedAt"] = dt.datetime.now(dt.timezone.utc).isoformat()
        self.save()
        out = self.root / "output.json"
        target = self.root / "unrelated.json"
        target.write_text("unchanged")
        out.symlink_to(target)
        env = {"OPERATOR_ACCOUNT_ID": self.expected["ownerId"],
               "OPERATOR_WORKSPACE_ID": self.expected["workspaceId"],
               "OPERATOR_REPO": self.expected["repo"]}
        argv = ["export_native_automation.py", "--spec", str(self.spec),
                "--binding", str(self.binding), "--recurrence", str(self.recurrence),
                "--out", str(out)]
        old_umask = os.umask(0o022)
        try:
            with patch.dict(os.environ, env), patch("sys.argv", argv):
                self.assertEqual(main(), 0)
        finally:
            os.umask(old_umask)
        self.assertFalse(out.is_symlink())
        self.assertEqual(target.read_text(), "unchanged")
        self.assertEqual(stat.S_IMODE(out.stat().st_mode), 0o600)
        self.assertIs(json.loads(out.read_text())["enabled"], False)

    def test_nonobject_binding_and_recurrence_fail_cleanly(self):
        for path in (self.binding, self.recurrence):
            original = path.read_text()
            with self.subTest(path=path):
                path.write_text("[]")
                with self.assertRaisesRegex(ValueError, "JSON objects"):
                    self.run_export()
                path.write_text(original)

    def test_malformed_timestamp_and_missing_native_id_fail_cleanly(self):
        original = self.target["observedAt"]
        for value in (None, 123, []):
            with self.subTest(timestamp=value):
                self.target["observedAt"] = value
                self.save()
                with self.assertRaisesRegex(ValueError, "timestamp"):
                    self.run_export()
        self.target["observedAt"] = original
        self.target["nativeCreate"].pop("id")
        self.save()
        with self.assertRaisesRegex(ValueError, "binding is unverified"):
            self.run_export()

    def test_empty_expected_owner_cannot_authorize_export(self):
        self.expected["ownerId"] = ""
        with self.assertRaisesRegex(ValueError, "bindings required"):
            self.run_export()
