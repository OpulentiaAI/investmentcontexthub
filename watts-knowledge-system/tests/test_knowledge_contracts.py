"""Synthetic evidence proves the typed lifecycle rejects unsupported claims."""

import hashlib
import json

from scripts.learning_gate import assess, candidate_hash, candidate_set_hash
from tests.support import HubCase


class KnowledgeContracts(HubCase):
    def artifact(self, name, value):
        raw = json.dumps(value, sort_keys=True) if not isinstance(value, str) else value
        self.write(name, raw)
        return "sha256:" + hashlib.sha256(raw.encode()).hexdigest()

    def record(self, path, type_name, fields):
        self.instance(path, type_name, extra="".join(f'{key}: "{value}"\n' for key, value in fields.items()))

    def candidate(self, learning_id="adapter-timeout"):
        source = "evidence/synthetic-source.txt"
        digest = self.artifact(source, "Synthetic test evidence: this adapter has a bounded call timeout.")
        return {"learningId": learning_id, "kind": "system-fact", "scope": "adapter:synthetic",
                "content": "The synthetic adapter bounds each call timeout.",
                "rationale": "Inspect the timeout before diagnosing a stalled call.",
                "sourceRef": source, "sourceSha256": digest, "sourceKind": "code"}

    def accepted(self, candidate=None, receipt_edit=None):
        candidate = candidate or self.candidate()
        review = {"reviewerId": "synthetic-reviewer", "candidateSetHash": candidate_set_hash([candidate]),
                  "verdicts": [{"learningId": candidate["learningId"], "candidateHash": candidate_hash(candidate),
                                "decision": "ACCEPT", "reason": "Synthetic test judgment, not a real review."}]}
        receipt = assess([candidate], review, generator_id="synthetic-generator")
        if receipt_edit:
            receipt_edit(receipt)
        ref = f'evidence/{candidate["learningId"]}-review.json'
        digest = self.artifact(ref, receipt)
        return {**candidate, "decision": "accepted", "reviewReceipt": ref, "reviewReceiptSha256": digest}

    def issue(self, phase="investigating"):
        evidence = "evidence/synthetic-incident.txt"
        return {"issueId": "synthetic-timeout", "scope": "adapter:synthetic", "symptom": "lookup timed out",
                "phase": phase, "windowStart": "2026-09-20T10:00:00Z", "windowEnd": "2026-09-20T10:05:00Z",
                "runtimeRevision": "UNVERIFIED", "evidenceRef": evidence,
                "evidenceSha256": self.artifact(evidence, "Synthetic timeout evidence, no live incident."),
                "baselineStatus": "unavailable", "limitation": "Synthetic fixture has no telemetry retention.",
                "conclusion": "inconclusive"}

    def baseline(self, issue):
        ref = "evidence/synthetic-baseline.json"
        proof = {"scope": issue["scope"], "symptom": issue["symptom"],
                 "windowStart": "2026-09-20T09:00:00Z", "windowEnd": "2026-09-20T09:05:00Z",
                 "query": "synthetic adapter AND lookup timed out", "observed": 0}
        return {"baselineStatus": "available", "baselineRef": ref,
                "baselineSha256": self.artifact(ref, proof)}, proof

    def resolution(self, issue, **overrides):
        proof = {"schemaVersion": 1, "issueId": issue["issueId"], "scope": issue["scope"],
                 "symptom": issue["symptom"], "changeRef": "synthetic-change-2", "runtimeRevision": "synthetic-revision-2",
                 "checkedAt": "2026-09-20T11:05:00Z", "check": "Replay the same lookup input after the fix.",
                 "expected": {"timeouts": 0}, "observed": {"timeouts": 0}, **overrides}
        ref = "evidence/synthetic-verification.json"
        return {"changeRef": "synthetic-change-2", "changeAppliedAt": "2026-09-20T11:00:00Z",
                "verificationRef": ref, "verificationSha256": self.artifact(ref, proof)}

    def test_valid_candidate_and_accepted_learning(self):
        candidate = self.candidate()
        self.record("research/candidate.md", "wks.learning", {**candidate, "decision": "candidate"})
        self.assertEqual(self.errors(), [])
        self.record("research/candidate.md", "wks.learning", self.accepted(candidate))
        self.assertEqual(self.errors(), [])

    def test_accepted_learning_needs_exact_reproducible_review(self):
        fields = self.accepted()
        for changes in ({"content": "Unreviewed replacement"}, {"reviewReceiptSha256": "sha256:" + "0" * 64},
                        {"reviewReceipt": "evidence/missing.json"}, {"sourceSha256": "sha256:" + "0" * 64},
                        {"sourceRef": "../outside"}):
            with self.subTest(changes=changes):
                self.record("research/learning.md", "wks.learning", {**fields, **changes})
                self.assert_error_contains("learning requires valid source and exact reproducible review")

    def test_forged_decision_and_self_review_do_not_validate(self):
        def forge(receipt):
            receipt["review"]["reviewerId"] = receipt["generatorId"]
            receipt["reviewerId"] = receipt["generatorId"]

        self.record("research/learning.md", "wks.learning", self.accepted(receipt_edit=forge))
        self.assert_error_contains("learning requires valid source and exact reproducible review")

    def test_candidate_rejects_invalid_fields_even_without_review(self):
        fields = {**self.candidate(), "decision": "candidate"}
        for changes in ({"content": "x" * 301}, {"scope": ""}, {"sourceKind": "agent-analysis"}, {"learningId": ""}):
            with self.subTest(changes=changes):
                self.record("research/learning.md", "wks.learning", {**fields, **changes})
                self.assert_error_contains("learning requires valid source")

    def test_duplicate_ids_and_scoped_content_fail(self):
        fields = self.accepted()
        self.record("research/a.md", "wks.learning", fields)
        self.record("research/b.md", "wks.learning", fields)
        self.assert_error_contains("no duplicate IDs/content")
        other = self.candidate("another-learning")
        self.record("research/b.md", "wks.learning", self.accepted(other))
        self.assert_error_contains("no duplicate IDs/content")
        other["scope"] = "adapter:different"
        self.record("research/b.md", "wks.learning", self.accepted(other))
        self.assertEqual(self.errors(), [])

    def test_supersession_requires_reviewed_same_scope_replacement(self):
        old = self.accepted()
        self.record("research/old.md", "wks.learning", {**old, "decision": "superseded", "supersededBy": "[[new]]"})
        candidate = {**self.candidate("replacement"), "content": "The synthetic timeout is now configurable."}
        self.record("research/new.md", "wks.learning", {**candidate, "decision": "candidate"})
        self.assert_error_contains("accepted same-scope replacement")
        self.record("research/new.md", "wks.learning", self.accepted(candidate))
        self.assertEqual(self.errors(), [])

    def test_missing_baseline_is_explicit_not_a_confirmed_cause(self):
        fields = self.issue()
        self.record("research/issue.md", "wks.issue", fields)
        self.assertEqual(self.errors(), [])
        for changes in ({"limitation": ""}, {"conclusion": "confirmed"}, {"phase": "blocked"},
                        {"windowStart": "2026-09-20T10:00:00"}):
            with self.subTest(changes=changes):
                self.record("research/issue.md", "wks.issue", {**fields, **changes})
                self.assert_error_contains("issue requires scoped evidence")

    def test_confirmed_cause_requires_matched_baseline_and_precedence(self):
        fields = self.issue()
        baseline, proof = self.baseline(fields)
        fields.update(baseline)
        fields.update(conclusion="confirmed", runtimeRevision="synthetic-revision-1", mechanism="Synthetic dependency timeout exhausted the lookup budget.",
                      alternatives="Synthetic traffic baseline rules out a request volume increase.", causeObservedAt="2026-09-20T09:59:00Z")
        self.record("research/issue.md", "wks.issue", fields)
        self.assertEqual(self.errors(), [])
        for update in ({"causeObservedAt": "2026-09-20T10:01:00Z"}, {"runtimeRevision": "UNVERIFIED"},
                       {"mechanism": ""}, {"alternatives": "[NEED: alternatives]"}):
            with self.subTest(cause=update):
                self.record("research/issue.md", "wks.issue", {**fields, **update})
                self.assert_error_contains("issue requires scoped evidence")
        for update in ({"scope": "different"}, {"symptom": "generic error"}, {"windowEnd": "2026-09-20T09:06:00Z"}, {"observed": None}):
            with self.subTest(update=update):
                fields["baselineSha256"] = self.artifact(fields["baselineRef"], {**proof, **update})
                self.record("research/issue.md", "wks.issue", fields)
                self.assert_error_contains("issue requires scoped evidence")

    def test_mitigation_is_not_resolution(self):
        fields = self.issue("mitigated")
        self.record("research/issue.md", "wks.issue", fields)
        self.assertEqual(self.errors(), [])
        fields["phase"] = "resolved"
        self.record("research/issue.md", "wks.issue", fields)
        self.assert_error_contains("post-change resolution proof")
        fields.update(self.resolution(fields))
        self.record("research/issue.md", "wks.issue", fields)
        self.assertEqual(self.errors(), [])

    def test_resolution_rejects_wrong_scope_stale_failed_or_untyped_results(self):
        fields = self.issue("resolved")
        for update in ({"scope": "different"}, {"symptom": "different"}, {"issueId": "another"},
                       {"checkedAt": "2026-09-20T10:01:00Z"}, {"checkedAt": "2026-09-20T11:00:00Z"},
                       {"observed": {"timeouts": 1}},
                       {"runtimeRevision": "UNVERIFIED"}, {"expected": True, "observed": 1},
                       {"expected": None, "observed": None}):
            with self.subTest(update=update):
                fields.update(self.resolution(fields, **update))
                self.record("research/issue.md", "wks.issue", fields)
                self.assert_error_contains("post-change resolution proof")

    def test_evidence_paths_cannot_read_private_or_linked_files(self):
        fields = self.issue()
        secret = self.write("ops/private.txt", "synthetic private fixture")
        (self.root / "evidence/link.txt").symlink_to(secret)
        for ref in ("ops/private.txt", "evidence/link.txt", str(secret)):
            with self.subTest(ref=ref):
                fields["evidenceRef"] = ref
                fields["evidenceSha256"] = "sha256:" + hashlib.sha256(secret.read_bytes()).hexdigest()
                self.record("research/issue.md", "wks.issue", fields)
                self.assert_error_contains("issue requires scoped evidence")
