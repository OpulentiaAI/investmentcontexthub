"""Offline contracts for the disabled learning and issue review drafts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.knowledge_contracts import check_records
from scripts.learning_gate import assess, candidate_hash, candidate_set_hash


ROOT = Path(__file__).resolve().parents[1]


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


class LearningReviewFlow(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "evidence").mkdir()
        source = b"Sanitized direct statement about the exact job.\n"
        (self.root / "evidence" / "statement.txt").write_bytes(source)
        self.candidate = {
            "learningId": "specific-job-pattern", "kind": "operating-practice",
            "scope": "Job: specific-job", "content": "Filter the job check by its exact error.",
            "rationale": "Makes future investigations comparable.",
            "sourceRef": "evidence/statement.txt", "sourceSha256": digest(source),
            "sourceKind": "human",
        }

    def review(self, candidates=None, verdicts=None, reviewer="independent"):
        candidates = [self.candidate] if candidates is None else candidates
        verdicts = ([{"learningId": c["learningId"],
                     "candidateHash": candidate_hash(c), "decision": "ACCEPT",
                     "reason": "Direct, scoped and useful"} for c in candidates]
                    if verdicts is None else verdicts)
        return {"reviewerId": reviewer, "candidateSetHash": candidate_set_hash(candidates),
                "verdicts": verdicts}

    def assess(self, candidates=None, review=None, existing=None):
        candidates = [self.candidate] if candidates is None else candidates
        return assess(candidates, self.review(candidates) if review is None else review,
                      generator_id="generator", existing=existing or [])

    def test_zero_candidates_produce_no_review_and_no_decisions(self):
        result = assess([], None, generator_id="generator")
        self.assertEqual(result["decisions"], [])
        self.assertIsNone(result["review"])

    def test_one_review_covers_all_exact_candidate_hashes(self):
        second = {**self.candidate, "learningId": "other-pattern", "scope": "Job: other"}
        result = self.assess([self.candidate, second])
        self.assertEqual([d["decision"] for d in result["decisions"]],
                         ["accepted", "accepted"])
        self.assertEqual(result["candidateSetHash"],
                         candidate_set_hash([second, self.candidate]))

    def test_missing_duplicate_malformed_timed_out_or_changed_review_rejects(self):
        valid = self.review()["verdicts"][0]
        bad_reviews = (
            {**self.review(), "verdicts": []},
            {**self.review(), "verdicts": [valid, valid]},
            "not JSON",
            None,
            {**self.review(), "verdicts": [{**valid, "candidateHash": "sha256:" + "0" * 64}]},
            {**self.review(), "verdicts": [{**valid, "decision": "accept"}]},
            {**self.review(), "candidateSetHash": "sha256:" + "0" * 64},
            self.review(reviewer="generator"),
        )
        for review in bad_reviews:
            with self.subTest(review=review):
                result = assess([self.candidate], review, generator_id="generator")
                self.assertEqual(result["decisions"][0]["decision"], "rejected")

    def test_duplicate_id_or_same_scope_content_rejects_without_force(self):
        duplicate = {**self.candidate, "learningId": "second"}
        result = self.assess([self.candidate, duplicate])
        self.assertTrue(all(d["decision"] == "rejected" for d in result["decisions"]))
        result = self.assess(existing=[{"learningId": "old", "scope": self.candidate["scope"],
                                        "content": self.candidate["content"]}])
        self.assertEqual(result["decisions"][0]["decision"], "rejected")

    def test_accepted_record_requires_replayable_receipt_and_source_hash(self):
        receipt = self.assess()
        encoded = json.dumps(receipt).encode()
        (self.root / "evidence" / "review.json").write_bytes(encoded)
        record = {"type": "wks.learning", **self.candidate, "decision": "accepted",
                  "reviewReceipt": "evidence/review.json", "reviewReceiptSha256": digest(encoded)}
        path = self.root / "learning.md"
        self.assertEqual(check_records(self.root, [(path, record)]), [])
        self.assertTrue(check_records(self.root, [(path, {**record, "sourceSha256": digest(b"other")})]))
        self.assertTrue(check_records(self.root, [(path, {**record, "reviewReceiptSha256": digest(b"other")})]))
        self.assertTrue(check_records(self.root, [(path, {**record, "sourceRef": "ops/private.txt"})]))
        self.assertTrue(check_records(self.root, [(path, {**record, "sourceRef": "../private.txt"})]))


class IssueInvestigationFlow(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "evidence").mkdir()
        evidence = b"Sanitized exact error observations.\n"
        self.write("symptom.txt", evidence)
        self.issue = {
            "type": "wks.issue", "issueId": "job-failure", "scope": "Job: specific-job",
            "symptom": "TimeoutError in specific-job", "phase": "investigating",
            "windowStart": "2026-09-27T12:00:00+00:00",
            "windowEnd": "2026-09-27T13:00:00+00:00",
            "runtimeRevision": "adapter:revision-1",
            "evidenceRef": "evidence/symptom.txt", "evidenceSha256": digest(evidence),
            "baselineStatus": "unavailable", "limitation": "Prior exact-error logs expired",
            "conclusion": "inconclusive",
        }

    def write(self, name, data):
        raw = json.dumps(data).encode() if isinstance(data, dict) else data
        (self.root / "evidence" / name).write_bytes(raw)
        return "evidence/" + name, digest(raw)

    def errors(self, **updates):
        return check_records(self.root, [(self.root / "issue.md", {**self.issue, **updates})])

    def baseline(self, **updates):
        baseline = {
            "scope": self.issue["scope"], "symptom": self.issue["symptom"],
            "windowStart": "2026-09-27T10:00:00+00:00",
            "windowEnd": "2026-09-27T11:00:00+00:00",
            "query": "job=specific-job error=TimeoutError", "observed": 0,
            **updates,
        }
        ref, sha = self.write("baseline.json", baseline)
        return {"baselineStatus": "available", "baselineRef": ref,
                "baselineSha256": sha, "limitation": "", "conclusion": "inconclusive"}

    def test_missing_baseline_stays_inconclusive_and_zero_observations_are_valid(self):
        self.assertEqual(self.errors(), [])
        self.assertTrue(self.errors(conclusion="confirmed", mechanism="foo", alternatives="bar",
                                    causeObservedAt="2026-09-27T11:55:00+00:00"))
        self.assertEqual(self.errors(**self.baseline()), [])

    def test_baseline_must_match_exact_scope_symptom_and_duration(self):
        for modified in ({"symptom": "any error"}, {"scope": "Job: other"},
                         {"windowStart": "2026-09-27T09:00:00+00:00"},
                         {"windowEnd": "2026-09-27T12:10:00+00:00"},
                         {"query": " "}, {"observed": None}):
            with self.subTest(modified=modified):
                self.assertTrue(self.errors(**self.baseline(**modified)))

    def test_confirmed_cause_requires_runtime_timing_mechanism_alternatives(self):
        baseline = self.baseline()
        confirmed = {**baseline, "conclusion": "confirmed",
                     "causeObservedAt": "2026-09-27T11:55:00+00:00",
                     "mechanism": "Revision changed timeout path", "alternatives": "Traffic unchanged"}
        self.assertEqual(self.errors(**confirmed), [])
        for updates in ({"runtimeRevision": ""}, {"causeObservedAt": "2026-09-27T12:01:00+00:00"},
                        {"mechanism": ""}, {"alternatives": ""}):
            with self.subTest(updates=updates):
                self.assertTrue(self.errors(**{**confirmed, **updates}))

    def test_resolution_requires_post_change_same_symptom_typed_observation(self):
        base = {**self.baseline(), "phase": "resolved", "changeRef": "fix-1",
                "changeAppliedAt": "2026-09-27T14:00:00+00:00"}
        self.assertTrue(self.errors(**base))
        verification = {"schemaVersion": 1, "issueId": self.issue["issueId"],
                        "scope": self.issue["scope"], "symptom": self.issue["symptom"],
                        "changeRef": "fix-1", "runtimeRevision": "adapter:revision-2",
                        "checkedAt": "2026-09-27T15:00:00+00:00",
                        "check": "Exact TimeoutError count in the post-change hour",
                        "expected": {"count": 0}, "observed": {"count": 0}}
        ref, sha = self.write("verification.json", verification)
        resolved = {**base, "verificationRef": ref, "verificationSha256": sha}
        self.assertEqual(self.errors(**resolved), [])
        for modified in ({"symptom": "any error"}, {"checkedAt": "2026-09-27T13:00:00+00:00"},
                         {"checkedAt": "2026-09-27T15:00:00"}, {"observed": {"count": 1}},
                         {"observed": True, "expected": 1}, {"runtimeRevision": ""},
                         {"check": ""}):
            with self.subTest(modified=modified):
                ref, sha = self.write("verification.json", {**verification, **modified})
                self.assertTrue(self.errors(**{**resolved, "verificationRef": ref,
                                               "verificationSha256": sha}))


class DisabledAutomationContract(unittest.TestCase):
    def test_operating_entrypoints_use_the_typed_review_loop(self):
        inject = (ROOT / "inject/hub-inject.md").read_text()
        operating = (ROOT / "runbooks/operate-the-hub.md").read_text()
        self.assertIn("[[learning-and-issue-review]]", inject)
        self.assertIn("[[learning-and-issue-review]]", operating)
        self.assertIn("`wks.learning`", operating)
        self.assertIn("`wks.issue`", operating)
        self.assertIn("separately approved hub patch", operating)
        self.assertIn("not resolution without a hashed post-change check", operating)

    def test_original_schedule_and_disable_guards_are_unchanged(self):
        specs = {
            "source-manifest-review.md": 'expression: "0 8 * * 1"',
            "connector-health-check.md": 'expression: "0 9 * * 1-5"',
            "historical-ingest-heartbeat.md": 'expression: "0 7 * * 1-5"',
            "portfolio-research-pass.md": 'expression: "0 10 * * 1"',
            "forecast-review.md": 'expression: "0 11 * * 1"',
            "critical-investor-modeling.md": 'expression: "0 14 * * 1"',
        }
        for name, schedule in specs.items():
            with self.subTest(spec=name):
                text = (ROOT / "automations" / name).read_text()
                for required in (schedule, 'enabled: "no"', 'firstOpenChecked: "no"',
                                 "# Forbidden Actions", "[[learning-and-issue-review]]"):
                    self.assertIn(required, text)


if __name__ == "__main__":
    unittest.main()
