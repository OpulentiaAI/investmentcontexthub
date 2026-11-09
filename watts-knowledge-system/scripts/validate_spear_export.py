#!/usr/bin/env python3
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPORT = ROOT / "ops" / "spear-live-export-2026-09-22"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


manifest = json.loads((EXPORT / "DELIVERABLE-MANIFEST.json").read_text())
checksums = json.loads((EXPORT / "CHECKSUMS.json").read_text())["files"]

for relative, expected in checksums.items():
    path = EXPORT / relative
    if not path.is_file():
        fail(f"missing checksum member: {relative}")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        fail(f"checksum mismatch: {relative}")

entity_files = sorted((EXPORT / "entities").glob("*.json"))
if len(entity_files) != manifest["sourceEntityTypes"]:
    fail("entity file count does not match the manifest")

row_count = 0
for path in entity_files:
    rows = json.loads(path.read_text())
    expected = manifest["entityCounts"].get(path.stem)
    if expected is None or len(rows) != expected:
        fail(f"entity row count mismatch: {path.name}")
    row_count += len(rows)

if row_count != manifest["committedRows"]:
    fail("aggregate entity row count does not match the manifest")

profile_id = manifest["profileId"]
for row in json.loads((EXPORT / "entities" / "user.json").read_text()):
    if row.get("profile_id") != profile_id:
        fail("secondary profile row found in user.json")

campaign_dir = EXPORT / "read-surfaces" / "campaigns"
for index in range(manifest["campaignIcpPairs"]):
    for suffix in ("details", "icp"):
        if not (campaign_dir / f"{index:02d}-{suffix}.json").is_file():
            fail(f"missing campaign receipt: {index:02d}-{suffix}")

request_manifest = json.loads(
    (EXPORT / "manifests" / "REQUEST-SPECIFIC-MANIFEST.json").read_text()
)
for document in request_manifest["documents"]:
    path = EXPORT / document["path"]
    if not path.is_file():
        fail(f"missing document: {document['documentId']}")
    if hashlib.sha256(path.read_bytes()).hexdigest() != document["sha256"]:
        fail(f"document checksum mismatch: {document['documentId']}")

secret_patterns = {
    "bearer token": re.compile(rb"Bearer\s+[A-Za-z0-9._~+/=-]{12,}", re.I),
    "JWT": re.compile(rb"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    "GitHub token": re.compile(rb"(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{20,}"),
    "Slack token": re.compile(rb"xox[baprs]-[A-Za-z0-9-]{10,}"),
    "OpenAI key": re.compile(rb"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
    "AWS access key": re.compile(rb"(?:AKIA|ASIA)[A-Z0-9]{16}"),
    "signed URL": re.compile(rb"X-Amz-Signature|X-Goog-Signature|[?&](?:access_token|code|sig)=", re.I),
}

for path in EXPORT.rglob("*"):
    if not path.is_file() or path.name == "CHECKSUMS.json":
        continue
    data = path.read_bytes()
    for label, pattern in secret_patterns.items():
        if pattern.search(data):
            fail(f"{label} pattern found: {path.relative_to(EXPORT)}")

if manifest["signedUrlsPersisted"] or manifest["credentialsPersisted"]:
    fail("manifest reports persisted credentials")

print(
    f"OK: {len(entity_files)} entities, {row_count} rows, "
    f"{len(checksums)} checksums, {manifest['documentCount']} documents"
)
