from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from panda_agent.source import (
    LinkCollector,
    SourceGateError,
    _validate_web_contract,
    compute_sphinx_snapshot_hash,
    resolve_manifest_repository_path,
    sha256_file,
)


class SourceTests(unittest.TestCase):
    def test_repository_path_prefers_canonical_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            canonical = (
                project_root / "data" / "sources" / "repos" / "example" / "abc123"
            )
            canonical.mkdir(parents=True)
            entry = {
                "repo_id": "example",
                "commit_sha": "abc123",
                "path": str(project_root / "stale" / "snapshot"),
            }

            self.assertEqual(
                resolve_manifest_repository_path(entry, project_root),
                canonical.resolve(),
            )

    def test_repository_path_allows_safe_manifest_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            fallback = (
                project_root
                / "data"
                / "sources"
                / "repos"
                / "legacy"
                / "snapshot"
            )
            fallback.mkdir(parents=True)
            entry = {
                "repo_id": "example",
                "commit_sha": "abc123",
                "path": str(fallback),
            }

            self.assertEqual(
                resolve_manifest_repository_path(entry, project_root),
                fallback.resolve(),
            )

    def test_repository_path_rejects_external_manifest_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory) / "project"
            project_root.mkdir()
            external = Path(directory) / "external"
            external.mkdir()
            entry = {
                "repo_id": "example",
                "commit_sha": "abc123",
                "path": str(external),
            }

            with self.assertRaises(SourceGateError):
                resolve_manifest_repository_path(entry, project_root)

    def test_repository_path_rejects_identity_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            entry = {
                "repo_id": "../outside",
                "commit_sha": "abc123",
                "path": "unused",
            }

            with self.assertRaises(SourceGateError):
                resolve_manifest_repository_path(entry, project_root)

    def test_sha256_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "value.txt"
            path.write_bytes(b"panda")
            self.assertEqual(sha256_file(path), hashlib.sha256(b"panda").hexdigest())

    def test_link_collector_reads_href_and_src(self) -> None:
        parser = LinkCollector()
        parser.feed('<a href="next.html">N</a><img src="_static/a.png">')
        self.assertEqual(parser.links, ["next.html", "_static/a.png"])

    def test_snapshot_contract_rejects_configured_hash_mismatch(self) -> None:
        records = [{
            "url": "https://example.test/docs/index.html",
            "final_url": "https://example.test/docs/index.html",
            "status": 200,
            "content_type": "text/html; charset=utf-8",
            "sha256": "a" * 64,
        }]
        snapshot = {
            "records": records,
            "snapshot_hash": compute_sphinx_snapshot_hash(records),
            "failures": [],
        }
        doc = SimpleNamespace(
            doc_id="docs",
            url=records[0]["url"],
            expected_snapshot_hash="b" * 64,
            expected_html_page_count=1,
            expected_asset_count=0,
            required_paths=["docs/index.html"],
        )
        self.assertTrue(
            any("snapshot hash" in error for error in _validate_web_contract(snapshot, doc))
        )

    def test_snapshot_hash_covers_status_and_content_type(self) -> None:
        base = [{
            "url": "https://example.test/docs/index.html",
            "final_url": "https://example.test/docs/index.html",
            "status": 200,
            "content_type": "text/html",
            "sha256": "a" * 64,
        }]
        changed = [dict(base[0], status=206)]
        self.assertNotEqual(
            compute_sphinx_snapshot_hash(base), compute_sphinx_snapshot_hash(changed)
        )


if __name__ == "__main__":
    unittest.main()
