import datetime as dt
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

from scripts.readiness import readiness
from scripts.source_review_cycle import cycle


HUB = pathlib.Path(__file__).resolve().parent.parent


class LaunchRehearsalTests(unittest.TestCase):
    def test_native_catalog_to_report_stays_partial_and_cannot_enable_a_job(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            expected = {"ownerId": "synthetic-owner", "workspaceId": "synthetic-workspace",
                        "repo": "example/synthetic"}
            inputs = {
                "workspace-result": {"success": True, "workspace": {
                    "workspaceId": expected["workspaceId"], "userId": expected["ownerId"]}},
                "mesa-result": {"success": True, "truncated": False, "repo_id": "synthetic-mesa",
                                "data": {"id": "synthetic-mesa", "upstream": {
                                    "url": "https://github.com/example/synthetic"}}},
                "capabilities-result": {"success": True, "integrations": [
                    {"slug": "synthetic", "installed": True, "connection_ids": ["private-connection"]}],
                    "mcp_servers": [], "connected_apps": []},
                "source-refs": {"workspace": "workspace_manage:get", "mesa": "mesa_get_overview",
                                "capabilities": "list_integrations:installed"},
                "source-map": {"ownerId": expected["ownerId"], "workspaceId": expected["workspaceId"],
                               "connections": {"private-connection": "spear"}},
            }
            args = [sys.executable, str(HUB / "scripts/ingest_native_observation.py")]
            for name, value in inputs.items():
                path = root / f"{name}.json"
                path.write_text(json.dumps(value))
                args.extend([f"--{name}", str(path)])
            observations = root / "observations"
            args.extend(["--out", str(observations)])
            process = subprocess.run(args, capture_output=True, text=True, check=False, timeout=30,
                                     env={"PATH": os.defpath, "OPERATOR_ACCOUNT_ID": expected["ownerId"],
                                          "OPERATOR_WORKSPACE_ID": expected["workspaceId"],
                                          "OPERATOR_REPO": expected["repo"]})
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(json.loads(process.stdout)["status"], "partial")
            snapshot = observations / "sources.json"
            self.assertNotIn("private-connection", snapshot.read_text())
            now = dt.datetime.now(dt.timezone.utc)
            first = cycle("rehearsal-one", snapshot, root / "runs", now=now)
            self.assertEqual(first["status"], "partial")
            artifact = root / "runs/rehearsal-one/source-manifest-review.md"
            self.assertEqual(hashlib.sha256(artifact.read_bytes()).hexdigest(), first["artifactSha256"])
            self.assertIn("No FULL coverage claim", artifact.read_text())
            self.assertNotIn("private-connection", artifact.read_text())

            runtime = {"ownerId": expected["ownerId"], "workspaceId": expected["workspaceId"],
                       "repo": expected["repo"], "observedAt": now.isoformat(),
                       "workspaceBound": True, "contextMounted": True, "threadId": "synthetic-thread",
                       "nativeCreate": {"success": True, "workspaceId": expected["workspaceId"],
                                        "id": "synthetic-thread", "threadId": "synthetic-thread"}}
            (observations / "runtime.json").write_text(json.dumps(runtime))
            entries = {}
            for name in ("owner", "workspace", "runtime", "sources"):
                path = observations / f"{name}.json"
                entries[name] = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            intake = root / "intake.json"
            intake.write_text(json.dumps({"starter": {"slug": "watts-source-manifest-review",
                                                      "paidToolsEnabled": False}, "observations": entries}))
            result = readiness(intake, expected, now)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(len(result["reasons"]), 1)
            self.assertTrue(result["reasons"][0].startswith("sources:"))

            second = cycle("rehearsal-two", snapshot, root / "runs", now=now + dt.timedelta(days=2))
            self.assertEqual(second["status"], "blocked")
            self.assertIsNone(second["artifactSha256"])
            snapshot.write_text("{}")
            third = cycle("rehearsal-three", snapshot, root / "runs", now=now)
            self.assertEqual(third["status"], "blocked")
            self.assertIn("hash-mismatched", third["reason"])
