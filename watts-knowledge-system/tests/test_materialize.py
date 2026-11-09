import contextlib
import hashlib
import importlib.util
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("materialize", ROOT / "scripts/materialize.py")
materialize = importlib.util.module_from_spec(SPEC)
with patch.dict(os.environ, {"OPERATOR_ACCOUNT_ID": "synthetic-test-user"}):
    SPEC.loader.exec_module(materialize)


class MaterializeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        (self.root / "entities").mkdir()
        (self.root / "runbooks").mkdir()
        (self.root / "ops").mkdir()
        (self.root / "entities" / "visible.md").write_text("---\nsurface: watts\n---\nvisible")
        (self.root / "entities" / "operator.md").write_text("---\nsurface: operator\n---\nprivate")
        (self.root / "runbooks" / "procedure.md").write_text("---\nsurface: watts\n---\nprocedure")
        (self.root / "ops" / "private.md").write_text("---\nsurface: watts\n---\nprivate")
        self.addCleanup(patch.stopall)
        patch.object(materialize, "HUB", self.root).start()
        patch.object(materialize, "USER_ID", "synthetic-test-user").start()
        patch.object(materialize, "WORKSPACE_ID", "synthetic-test-workspace").start()
        patch.object(materialize, "CONTENT_DIRS", {"entities": "knowledge", "runbooks": "runbook"}).start()
        self.calls = []
        self.names = {"notes": {}, "runbooks": {}}
        self.attached = {"attachedKnowledgeIds": [], "attachedRunbookIds": []}
        self.truncated = False
        self.fail_create = False
        self.fail_attach = False
        patch.object(materialize, "pilot", self.pilot).start()

    def pilot(self, mode, fn, args):
        self.calls.append((mode, fn, args))
        if fn in ("knowledgeRunbooks:listKnowledge", "knowledgeRunbooks:listRunbooks"):
            collection, field = (("notes", "name") if fn.endswith("listKnowledge")
                                 else ("runbooks", "title"))
            rows = [{field: name, "id": ident} for name, ident in self.names[collection].items()]
            return {collection: rows, "total": len(rows), "truncated": self.truncated}
        if fn == "workspaceEntities:listForAgentInternal":
            return {"workspaces": [{"workspaceId": materialize.WORKSPACE_ID, **self.attached}], "total": 1}
        if fn.startswith("knowledgeRunbooks:create"):
            if self.fail_create:
                return None
            collection, field = (("notes", "name") if fn.endswith("createKnowledge")
                                 else ("runbooks", "title"))
            ident = f"id-{len(self.names[collection]) + 1}-{collection}"
            self.names[collection][args[field]] = ident
            return {"id": ident}
        if fn == "workspaceEntities:attachContextForAgentInternal":
            if not self.fail_attach:
                self.attached = {key: args[key] for key in self.attached}
            return None
        self.fail(f"unexpected service call {fn}")

    def run_main(self, apply=True, confirmed=True):
        out, err = io.StringIO(), io.StringIO()
        argv = ["materialize.py"] + (["--apply"] if apply else [])
        with patch.object(sys, "argv", argv), patch.dict(os.environ, {"CONFIRM": "send"} if confirmed else {}, clear=True):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                result = materialize.main()
        return result, out.getvalue(), err.getvalue()

    def test_dry_run_requires_no_service_access_and_excludes_operator_files(self):
        code, output, _ = self.run_main(apply=False, confirmed=False)
        self.assertEqual(code, 0)
        self.assertEqual(self.calls, [])
        self.assertIn("watts/entities/visible", output)
        self.assertIn("watts/runbooks/procedure", output)
        self.assertNotIn("operator", output)
        self.assertNotIn("private", output)

    def test_apply_requires_confirmation_before_any_service_access(self):
        code, _, err = self.run_main(confirmed=False)
        self.assertEqual(code, 2)
        self.assertEqual(self.calls, [])
        self.assertIn("refusing", err)

    def test_binding_inventory_requires_current_content_not_just_matching_names(self):
        content = (self.root / "entities/visible.md").read_text()
        for observed in (None, "stale hub content", content):
            with self.subTest(observed=observed):
                def read(mode, fn, args):
                    if fn.endswith("listKnowledge"):
                        return {"notes": [{"id": "note", "name": "watts/entities/visible",
                                           "content": observed}], "total": 1, "truncated": False}
                    return {"runbooks": [], "total": 0, "truncated": False}
                with patch.object(materialize, "pilot", side_effect=read):
                    if observed == content:
                        self.assertEqual(materialize.inventory(verify_content=True),
                                         {("notes", "watts/entities/visible"): "note"})
                    else:
                        with self.assertRaisesRegex(RuntimeError, "content is unavailable or differs"):
                            materialize.inventory(verify_content=True)

    def test_failed_or_incomplete_inventory_never_writes(self):
        for response in (None, {"notes": [], "total": 1, "truncated": False},
                         {"notes": [], "total": 0, "truncated": True},
                         {"notes": [{"name": "missing-id"}], "total": 1, "truncated": False}):
            with self.subTest(response=response):
                self.calls.clear()
                actual_pilot = self.pilot

                def faulty(mode, fn, args):
                    if fn == "knowledgeRunbooks:listKnowledge":
                        self.calls.append((mode, fn, args))
                        return response
                    return actual_pilot(mode, fn, args)

                with patch.object(materialize, "pilot", faulty):
                    code, _, err = self.run_main()
                self.assertEqual(code, 1)
                self.assertIn("inventory", err)
                self.assertFalse(any(mode == "write" for mode, _, _ in self.calls))

    def test_workspace_inventory_failure_never_writes(self):
        with patch.object(materialize, "workspace_attached_ids", side_effect=RuntimeError("unavailable")):
            code, _, _ = self.run_main()
        self.assertEqual(code, 1)
        self.assertFalse(any(mode == "write" for mode, _, _ in self.calls))

    def test_create_failure_returns_nonzero_without_claiming_attachment(self):
        self.fail_create = True
        code, output, err = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("created id", err)
        self.assertNotIn("attached.", output)
        self.assertFalse(any(fn.endswith("attachContextForAgentInternal") for _, fn, _ in self.calls))

    def test_unverified_or_error_creation_never_attaches(self):
        actual_pilot = self.pilot
        for result in ({"id": "synthetic-id", "error": "synthetic"}, {"id": "not-in-inventory"}):
            with self.subTest(result=result):
                self.calls.clear()

                def bad_create(mode, fn, args):
                    if fn.startswith("knowledgeRunbooks:create"):
                        self.calls.append((mode, fn, args))
                        return result
                    return actual_pilot(mode, fn, args)

                with patch.object(materialize, "pilot", bad_create):
                    code, output, _ = self.run_main()
                self.assertEqual(code, 1)
                self.assertNotIn("attached.", output)
                self.assertFalse(any(fn.endswith("attachContextForAgentInternal") for _, fn, _ in self.calls))

    def test_failed_attachment_is_recoverable_on_retry(self):
        self.fail_attach = True
        code, output, err = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("did not attach", err)
        self.assertNotIn("attached.", output)
        self.assertEqual(len(self.names["notes"]), 1)
        self.assertEqual(len(self.names["runbooks"]), 1)
        self.calls.clear()
        self.fail_attach = False
        code, output, _ = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn("attached.", output)
        self.assertFalse(any(fn.startswith("knowledgeRunbooks:create") for _, fn, _ in self.calls))
        self.assertEqual(set(self.attached["attachedKnowledgeIds"]), set(self.names["notes"].values()))
        self.assertEqual(set(self.attached["attachedRunbookIds"]), set(self.names["runbooks"].values()))

    def test_explicit_attachment_error_does_not_report_success(self):
        actual_pilot = self.pilot

        def failed_response(mode, fn, args):
            if fn == "workspaceEntities:attachContextForAgentInternal":
                self.calls.append((mode, fn, args))
                return {"error": "synthetic"}
            return actual_pilot(mode, fn, args)

        with patch.object(materialize, "pilot", failed_response):
            code, output, err = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("unexpected response", err)
        self.assertNotIn("attached.", output)

    def test_preflight_rejects_unsupported_inventory_size_before_writing(self):
        self.names["notes"] = {f"old-{n}": f"id-{n}" for n in range(500)}
        code, _, err = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("500-row limit", err)
        self.assertFalse(any(mode == "write" for mode, _, _ in self.calls))

    def test_existing_attachment_ids_are_preserved(self):
        self.names["notes"]["watts/entities/visible"] = "existing-hub"
        self.attached["attachedKnowledgeIds"] = ["already-attached"]
        code, _, _ = self.run_main()
        self.assertEqual(code, 0)
        self.assertEqual(set(self.attached["attachedKnowledgeIds"]), {"existing-hub", "already-attached"})


class PilotLogTests(unittest.TestCase):
    def private_fixture(self, root):
        (root / "scripts").mkdir()
        for name in ("pilot.sh", "pilot.py"):
            target = root / "scripts" / name
            target.write_bytes((ROOT / "scripts" / name).read_bytes())
            target.chmod(0o755)
        frontend = root / "frontend"
        frontend.mkdir()
        (frontend / ".env.deploy").write_text("CONVEX_DEPLOYMENT=test:synthetic\n")
        bin_dir = root / "bin"
        bin_dir.mkdir()
        self.probe_prefix = (
            '#!/bin/sh\ncase "$4" in\n'
            '  userIdentityLinks:resolveOwnershipCandidatesInternal) '
            'printf \'%s\\n\' \'{"canonicalUserId":"synthetic-test-user",'
            '"emails":["synthetic@example.invalid"]}\'; exit 0 ;;\n'
            '  workspaceEntities:listForAgentInternal) '
            'printf \'%s\\n\' \'{"total":1,"workspaces":[{"workspaceId":'
            '"synthetic-workspace","userId":"synthetic-test-user"}]}\'; exit 0 ;;\n'
            'esac\n')
        env = {**os.environ, "OPULENT_FRONTEND": str(frontend),
               "PATH": f"{bin_dir}:{os.environ['PATH']}", "CONFIRM": "send",
               "OPERATOR_ACCOUNT_ID": "synthetic-test-user", "OPERATOR_EMAIL": "synthetic@example.invalid",
               "OPERATOR_WORKSPACE_ID": "synthetic-workspace", "OPERATOR_DEPLOYMENT": "test:synthetic",
               "CONVEX_DEPLOYMENT": "test:synthetic", "CONVEX_DEPLOY_KEY": "synthetic-only",
               "OPERATOR_LEDGER": str(root / "private" / "audit.jsonl"),
               "OPERATOR_READ_FUNCTIONS": "knowledgeRunbooks:listKnowledge",
               "OPERATOR_WRITE_FUNCTIONS": "workspaceEntities:attachContextForAgentInternal,knowledgeRunbooks:createKnowledge"}
        return bin_dir, env

    def test_real_adapter_and_shell_stub_accept_empty_attachment_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            pilot_script = root / "scripts" / "pilot.sh"
            bin_dir, env = self.private_fixture(root)
            stub = bin_dir / "npx"
            stub.write_text(self.probe_prefix + "exit 0\n")
            stub.chmod(0o755)
            with patch.object(materialize, "PILOT", pilot_script), patch.dict(os.environ, env):
                self.assertIsNone(materialize.pilot("write", "workspaceEntities:attachContextForAgentInternal",
                                                    {"userId": "synthetic-test-user", "workspaceId": "synthetic-workspace"}))
                for mode, fn in (("read", "knowledgeRunbooks:listKnowledge"),
                                 ("write", "knowledgeRunbooks:createKnowledge")):
                    with self.subTest(fn=fn), self.assertRaisesRegex(RuntimeError, "empty response"):
                        materialize.pilot(mode, fn, {"userId": "synthetic-test-user"})
            logs = [root / "private" / "audit.jsonl"]
            self.assertEqual(len(logs), 1)
            self.assertEqual(len(logs[0].read_text().splitlines()), 3)

    def test_empty_and_noise_only_outputs_are_logged_with_cli_exit(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            bin_dir, env = self.private_fixture(root)
            stub = bin_dir / "npx"
            payload = '{"userId":"synthetic-test-user","secret":"synthetic-only"}'
            cases = (
                ("", 0),
                ("printf 'ExperimentalWarning: synthetic noise\\n'\n", 0),
                ("printf 'synthetic CLI failure\\n'\nexit 17\n", 17),
            )
            for body, cli_exit in cases:
                stub.write_text(self.probe_prefix + body)
                stub.chmod(0o755)
                result = subprocess.run(["bash", str(root / "scripts/pilot.sh"), "read", "knowledgeRunbooks:listKnowledge", payload],
                                        env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0 if cli_exit == 0 else 1, result.stderr)
                if cli_exit == 0:
                    self.assertEqual(result.stdout.strip(), "")
            logs = [root / "private" / "audit.jsonl"]
            self.assertEqual(len(logs), 1)
            raw = logs[0].read_text()
            self.assertNotIn("synthetic-only", raw)
            records = [json.loads(line) for line in raw.splitlines()]
            self.assertEqual([record["exit"] for record in records], [0, 0, 17])
            for record in records:
                self.assertEqual(record["fn"], "knowledgeRunbooks:listKnowledge")
                self.assertEqual(record["argsBytes"], len(payload))
                self.assertEqual(record["argsSha256"], hashlib.sha256(payload.encode()).hexdigest())
                self.assertNotIn("args", record)

    def test_owner_mismatch_or_missing_confirmation_never_reaches_cli(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            bin_dir, env = self.private_fixture(root)
            marker = root / "cli-called"
            stub = bin_dir / "npx"
            stub.write_text(self.probe_prefix + f"touch '{marker}'\n")
            stub.chmod(0o755)
            script = root / "scripts/pilot.sh"
            for mode, fn, args, changes in (
                ("read", "knowledgeRunbooks:listKnowledge", '{"userId":"another-owner"}', {}),
                ("write", "workspaceEntities:attachContextForAgentInternal",
                 '{"userId":"synthetic-test-user","workspaceId":"synthetic-workspace"}', {"CONFIRM": ""}),
                ("write", "workspaceEntities:attachContextForAgentInternal",
                 '{"userId":"synthetic-test-user","workspaceId":"other-workspace"}', {}),
                ("read", "knowledgeRunbooks:createKnowledge",
                 '{"userId":"synthetic-test-user"}',
                 {"OPERATOR_READ_FUNCTIONS": "knowledgeRunbooks:createKnowledge",
                  "OPERATOR_WRITE_FUNCTIONS": "workspaceEntities:attachContextForAgentInternal"}),
            ):
                with self.subTest(mode=mode, args=args):
                    result = subprocess.run(["bash", str(script), mode, fn, args],
                                            env={**env, **changes}, capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse(marker.exists())

    def test_ambiguous_owner_or_workspace_probe_blocks_before_action(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            bin_dir, env = self.private_fixture(root)
            marker = root / "action-called"
            stub = bin_dir / "npx"
            script = root / "scripts/pilot.sh"
            for bad_probe in (
                self.probe_prefix.replace('"canonicalUserId":"synthetic-test-user"',
                                          '"canonicalUserId":"another-owner"'),
                self.probe_prefix.replace('"total":1,"workspaces":',
                                          '"total":2,"workspaces":'),
            ):
                with self.subTest(probe=bad_probe):
                    stub.write_text(bad_probe + f"touch '{marker}'\n")
                    stub.chmod(0o755)
                    result = subprocess.run(["bash", str(script), "read", "knowledgeRunbooks:listKnowledge",
                                             '{"userId":"synthetic-test-user"}'], env=env,
                                            capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse(marker.exists())


class PilotAdapterTests(unittest.TestCase):
    def test_empty_stdout_only_allowed_for_attachment(self):
        with patch.object(materialize.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")) as run:
            self.assertIsNone(materialize.pilot("write", "workspaceEntities:attachContextForAgentInternal", {}))
            for mode, fn in (("read", "knowledgeRunbooks:listKnowledge"),
                             ("read", "knowledgeRunbooks:listRunbooks"),
                             ("read", "workspaceEntities:listForAgentInternal"),
                             ("write", "knowledgeRunbooks:createKnowledge"),
                             ("write", "knowledgeRunbooks:createRunbook")):
                with self.subTest(fn=fn), self.assertRaisesRegex(RuntimeError, "empty response"):
                    materialize.pilot(mode, fn, {})
            self.assertEqual(run.call_count, 6)

    def test_nonzero_adapter_exit_is_never_treated_as_void_success(self):
        with patch.object(materialize.subprocess, "run", return_value=subprocess.CompletedProcess([], 17, "", "synthetic")):
            with self.assertRaisesRegex(RuntimeError, "exit 17"):
                materialize.pilot("write", "workspaceEntities:attachContextForAgentInternal", {})


if __name__ == "__main__":
    unittest.main()
