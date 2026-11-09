"""Offline learning assessment fails closed on ambiguous review metadata."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.learning_gate import assess, candidate_hash, candidate_set_hash, validate_candidate


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "learning_gate.py"


def candidate(learning_id="first", **updates):
    item = {"learningId": learning_id, "kind": "system-fact", "scope": "Source: Spear",
            "content": "Spear exports require owner-scoped capture.",
            "rationale": "Avoid mixed-owner evidence in future reads.",
            "sourceRef": "evidence/spear-receipt", "sourceSha256": "sha256:" + "a" * 64,
            "sourceKind": "artifact"}
    item.update(updates)
    return item


def review_for(items):
    return {"reviewerId": "reviewer", "candidateSetHash": candidate_set_hash(items),
            "verdicts": [{"learningId": item["learningId"],
                          "candidateHash": candidate_hash(item), "decision": "ACCEPT",
                          "reason": "Evidence and scope checked"} for item in items]}


def decisions(items, review=None, existing=()):
    if review is None:
        review = review_for(items)
    return assess(items, review, generator_id="generator", existing=list(existing))["decisions"]


class LearningGateTests(unittest.TestCase):
    def test_exact_acceptance_and_replay_metadata(self):
        item = candidate()
        review = review_for([item])
        receipt = assess([item], json.dumps(review), generator_id="generator", existing=[])
        self.assertEqual(receipt["schemaVersion"], 1)
        self.assertEqual(receipt["generatorId"], "generator")
        self.assertEqual(receipt["reviewerId"], "reviewer")
        self.assertEqual(receipt["candidateSetHash"], candidate_set_hash([item]))
        self.assertEqual(receipt["candidates"], [item])
        self.assertEqual(receipt["existing"], [])
        self.assertEqual(receipt["review"], review)
        self.assertEqual(receipt["decisions"], [{"learningId": "first", "candidateHash": candidate_hash(item),
                                                  "decision": "accepted", "reason": "Evidence and scope checked"}])

    def test_canonical_hash_and_order_independence(self):
        first = candidate()
        second = candidate("second", content="A different fact")
        self.assertEqual(candidate_hash(first), candidate_hash(dict(reversed(list(first.items())))))
        self.assertEqual(candidate_set_hash([first, second]), candidate_set_hash([second, first]))
        self.assertNotEqual(candidate_hash(first), candidate_hash(second))
        self.assertTrue(candidate_hash(first).startswith("sha256:"))

    def test_empty_list_needs_no_review(self):
        receipt = assess([], "not JSON", generator_id="generator")
        self.assertEqual(receipt["decisions"], [])
        self.assertIsNone(receipt["review"])
        self.assertIsNone(receipt["reviewerId"])

    def test_malformed_and_nonobject_review_reject_everything(self):
        items = [candidate()]
        for review in ("```json\n{}\n```", "bad json", "[]", {},
                       {"reviewerId": "reviewer", "candidateSetHash": candidate_set_hash(items)},
                       '{"reviewerId":"a","reviewerId":"b"}'):
            with self.subTest(review=review):
                self.assertEqual(decisions(items, review)[0]["decision"], "rejected")

    def test_self_review_and_stale_set_hash_reject_all(self):
        items = [candidate(), candidate("second", content="Other fact")]
        for change in ({"reviewerId": "generator"}, {"reviewerId": "GENERATOR"},
                       {"reviewerId": " generator "},
                       {"candidateSetHash": "sha256:" + "0" * 64},
                       {"verdicts": []}, {"unexpected": "field"}):
            with self.subTest(change=change):
                review = review_for(items)
                review.update(change)
                result = decisions(items, review)
                if change == {"verdicts": []}:
                    self.assertEqual([r["decision"] for r in result], ["rejected", "rejected"])
                else:
                    self.assertTrue(all(r["decision"] == "rejected" for r in result))

    def test_mutated_candidate_and_ambiguous_or_bad_verdicts_reject_affected(self):
        items = [candidate(), candidate("second", content="Other fact")]
        for defect in ("mutation", "duplicate", "missing", "unknown", "blank reason", "extra field"):
            with self.subTest(defect=defect):
                review = review_for(items)
                if defect == "mutation":
                    changed = copy.deepcopy(items[0])
                    changed["content"] = "Mutated after review"
                    review["candidateSetHash"] = candidate_set_hash([changed, items[1]])
                    # A current set hash cannot authorize a stale candidate hash.
                    review["verdicts"][0]["candidateHash"] = candidate_hash(items[0])
                    assessed = [changed, items[1]]
                else:
                    assessed = items
                    if defect == "duplicate":
                        review["verdicts"].append(copy.deepcopy(review["verdicts"][0]))
                    if defect == "missing":
                        review["verdicts"].pop(0)
                    if defect == "unknown":
                        review["verdicts"][0]["decision"] = "MAYBE"
                    if defect == "blank reason":
                        review["verdicts"][0]["reason"] = " "
                    if defect == "extra field":
                        review["verdicts"][0]["suggestions"] = "unrecognized"
                self.assertEqual([r["decision"] for r in decisions(assessed, review)],
                                 ["rejected", "accepted"])

    def test_explicit_reject_and_case_sensitive_decisions(self):
        item = candidate()
        review = review_for([item])
        review["verdicts"][0].update(decision="REJECT", reason="Too vague")
        self.assertEqual(decisions([item], review)[0]["reason"], "Too vague")
        review["verdicts"][0]["decision"] = "accept"
        self.assertEqual(decisions([item], review)[0]["decision"], "rejected")

    def test_duplicate_ids_and_existing_scoped_content(self):
        first = candidate()
        same_id = candidate(content="Distinct content")
        items = [first, same_id]
        self.assertEqual([r["decision"] for r in decisions(items)], ["rejected", "rejected"])
        existing = [candidate("previous", content="  spear   EXPORTS require OWNER-scoped capture.  ")]
        receipt = assess([first], review_for([first]), generator_id="generator", existing=existing)
        self.assertEqual(receipt["decisions"][0]["decision"], "rejected")
        existing[0]["content"] = "modified after assessment"
        self.assertNotEqual(receipt["existing"], existing)
        different_scope = candidate("previous", scope="Source: Another")
        self.assertEqual(decisions([first], existing=[different_scope])[0]["decision"], "accepted")
        self.assertEqual(decisions([first], existing=[candidate("first", content="Other")])[0]["decision"], "rejected")

    def test_invalid_unhashable_id_rejects_without_exception(self):
        for learning_id in ({"nested": "id"}, ["nested", "id"], " first "):
            with self.subTest(learning_id=learning_id):
                item = candidate(learning_id)
                review = {"reviewerId": "reviewer", "candidateSetHash": candidate_set_hash([item]),
                          "verdicts": []}
                self.assertEqual(decisions([item], review)[0]["decision"], "rejected")
                with self.assertRaises(ValueError):
                    validate_candidate(item)

    def test_unknown_verdict_id_does_not_authorize_or_disqualify_known_item(self):
        item = candidate()
        review = review_for([item])
        review["verdicts"].append({"learningId": "unknown", "candidateHash": "irrelevant",
                                   "decision": "ACCEPT", "reason": "irrelevant"})
        self.assertEqual(decisions([item], review)[0]["decision"], "accepted")

    def test_deep_or_nonfinite_review_rejects_and_cli_sanitizes_recursion(self):
        item = candidate()
        self.assertEqual(decisions([item], '[' * 1100)[0]["decision"], "rejected")
        self.assertEqual(decisions([item], {"reviewerId": float("nan")})[0]["decision"], "rejected")
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "deep.json"
            source.write_text('[' * 1100 + ']' * 1100)
            run = subprocess.run([sys.executable, str(SCRIPT), "--input", str(source)],
                                 capture_output=True, text=True, check=False)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(run.stdout, "")
            self.assertEqual(run.stderr.strip(), "Invalid learning gate input")

    def test_candidate_shape_source_and_nonfinite_fail_closed(self):
        for updates in ({"kind": "maybe"}, {"sourceKind": "unknown"},
                        {"sourceSha256": "bad"}, {"sourceRef": "UNVERIFIED"},
                        {"sourceRef": "[NEED: citation]"}, {"content": "x" * 301},
                        {"scope": " "}, {"extra": "field"}):
            with self.subTest(updates=updates):
                item = candidate(**updates)
                self.assertEqual(decisions([item])[0]["decision"], "rejected")
        with self.assertRaises(ValueError):
            candidate_hash(candidate(content=float("nan")))
        with self.assertRaises(ValueError):
            assess([candidate(content=float("inf"))], None, generator_id="generator")
        validate_candidate(candidate())

    def test_cli_stdout_only_receipt_and_no_side_effects(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "request.json"
            item = candidate()
            source.write_text(json.dumps({"candidates": [item], "review": review_for([item]),
                                          "generatorId": "generator", "existing": []}))
            before = source.read_bytes()
            run = subprocess.run([sys.executable, str(SCRIPT), "--input", str(source)],
                                 capture_output=True, text=True, check=False)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(run.stderr, "")
            self.assertEqual(json.loads(run.stdout)["decisions"][0]["decision"], "accepted")
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual({p.name for p in Path(directory).iterdir()}, {source.name})

    def test_cli_sanitizes_invalid_and_bounded_input(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "request.json"
            for body in ('{"secret":"PRIVATE_MARKER","candidates":[NaN]}',
                         '{"x":"' + "a" * (1024 * 1024) + '"}',
                         '{"candidates":[],"review":null,"generatorId":"x","generatorId":"y"}'):
                with self.subTest(body=body[:50]):
                    source.write_text(body)
                    run = subprocess.run([sys.executable, str(SCRIPT), "--input", str(source)],
                                         capture_output=True, text=True, check=False)
                    self.assertEqual(run.returncode, 2)
                    self.assertEqual(run.stdout, "")
                    self.assertEqual(run.stderr.strip(), "Invalid learning gate input")


if __name__ == "__main__":
    unittest.main()
