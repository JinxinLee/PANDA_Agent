"""M1 source acquisition and offline corpus-lock verification."""

from __future__ import annotations

import hashlib
import json
import mimetypes
import platform
import re
import shutil
import subprocess
import time
import uuid
from collections import deque
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urldefrag, urljoin, urlparse

import requests

from panda_agent.config import CorporaConfig, corpora_config_hash


class SourceGateError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


SNAPSHOT_HASH_ALGORITHM = "url-final_url-status-content_type-file_hash-v2"


def _normalized_content_type(value: str) -> str:
    return value.split(";", 1)[0].strip().lower()


def compute_sphinx_snapshot_hash(records: list[dict[str, Any]]) -> str:
    """Compute the one canonical aggregate identity for a Sphinx snapshot."""
    digest = hashlib.sha256()
    for item in sorted(records, key=lambda value: value["url"]):
        digest.update(
            (
                f"{item['url']}\x1f{item['final_url']}\x1f{item['status']}\x1f"
                f"{_normalized_content_type(item['content_type'])}\x1f{item['sha256']}\n"
            ).encode("utf-8")
        )
    return digest.hexdigest()


def _validate_web_contract(snapshot: dict[str, Any], doc: Any) -> list[str]:
    errors: list[str] = []
    records = snapshot.get("records", [])
    aggregate = compute_sphinx_snapshot_hash(records)
    html_count = sum(
        _normalized_content_type(item.get("content_type", "")) == "text/html"
        for item in records
    )
    asset_count = len(records) - html_count
    if aggregate != doc.expected_snapshot_hash:
        errors.append(
            f"{doc.doc_id} snapshot hash {aggregate} != {doc.expected_snapshot_hash}"
        )
    if snapshot.get("snapshot_hash") != aggregate:
        errors.append(f"{doc.doc_id} manifest snapshot hash is not canonical")
    if html_count != doc.expected_html_page_count:
        errors.append(
            f"{doc.doc_id} HTML count {html_count} != {doc.expected_html_page_count}"
        )
    if asset_count != doc.expected_asset_count:
        errors.append(
            f"{doc.doc_id} asset count {asset_count} != {doc.expected_asset_count}"
        )
    final_paths = [urlparse(item.get("final_url", "")).path for item in records]
    for required in doc.required_paths:
        if not any(path.endswith(required) for path in final_paths):
            errors.append(f"{doc.doc_id} required path missing: {required}")
    entry = next(
        (item for item in records if item.get("url") == doc.url),
        None,
    )
    if not entry or entry.get("status") != 200:
        errors.append(f"{doc.doc_id} entry URL is missing or not HTTP 200")
    if any(item.get("required") for item in snapshot.get("failures", [])):
        errors.append(f"{doc.doc_id} contains required crawl failures")
    return errors


def run_git(args: list[str], cwd: Path | None = None) -> str:
    command = ["git"]
    if cwd is not None:
        command.extend(["-c", f"safe.directory={cwd.resolve()}"])
    result = subprocess.run(
        [*command, *args], cwd=cwd, text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise SourceGateError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def acquire_repository(repo: Any, root: Path) -> dict[str, Any]:
    if not repo.commit_sha:
        raise SourceGateError(f"repository {repo.repo_id} has no pinned commit_sha")
    destination = root / repo.repo_id / repo.commit_sha
    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        run_git(["clone", "--filter=blob:none", "--no-checkout", repo.url, str(destination)])
        run_git(["config", "core.longpaths", "true"], cwd=destination)
        run_git(["fetch", "origin", repo.commit_sha], cwd=destination)
        run_git(["checkout", "--detach", repo.commit_sha], cwd=destination)
    head = run_git(["rev-parse", "HEAD"], cwd=destination)
    remote = run_git(["remote", "get-url", "origin"], cwd=destination)
    dirty = run_git(["status", "--porcelain"], cwd=destination)
    if head != repo.commit_sha:
        raise SourceGateError(f"{repo.repo_id} HEAD {head} != {repo.commit_sha}")
    if remote.rstrip("/") != repo.url.rstrip("/"):
        raise SourceGateError(f"{repo.repo_id} remote URL mismatch")
    if dirty:
        raise SourceGateError(f"{repo.repo_id} worktree is dirty")
    readmes = sorted(
        str(path.relative_to(destination)).replace("\\", "/")
        for path in destination.glob("README*")
    )
    if not readmes:
        raise SourceGateError(f"{repo.repo_id} has no root README")
    return {
        "repo_id": repo.repo_id,
        "url": repo.url,
        "ref": repo.ref,
        "commit_sha": head,
        "path": str(destination.resolve()),
        "readmes": readmes,
    }


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for key in ("href", "src"):
            if values.get(key):
                self.links.append(values[key] or "")


def _local_web_path(raw_root: Path, url: str, content_type: str) -> Path:
    parsed = urlparse(url)
    path = unquote(parsed.path).lstrip("/")
    if not path or path.endswith("/"):
        path += "index.html"
    if "text/html" in content_type and not Path(path).suffix:
        path += ".html"
    safe_parts = [part for part in Path(path).parts if part not in ("..", ".")]
    return raw_root.joinpath(*safe_parts)


def crawl_sphinx(doc: Any, root: Path, retries: int = 3) -> dict[str, Any]:
    parsed_root = urlparse(doc.url)
    allowed_prefix = parsed_root.path.rsplit("/", 1)[0] + "/"
    raw_root = root / doc.doc_id / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "PANDA-QA-Corpus-Snapshot/1.0"
    queue: deque[str] = deque([doc.url])
    seen: set[str] = set()
    records: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    while queue:
        url = urldefrag(queue.popleft())[0]
        if url in seen:
            continue
        seen.add(url)
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or parsed.netloc != parsed_root.netloc:
            continue
        if not parsed.path.startswith(allowed_prefix):
            continue
        response = None
        error = ""
        for attempt in range(retries):
            try:
                response = session.get(url, timeout=45, allow_redirects=True)
                response.raise_for_status()
                final = urlparse(response.url)
                if final.netloc != parsed_root.netloc or not final.path.startswith(allowed_prefix):
                    raise SourceGateError(f"redirect escaped allowed prefix: {response.url}")
                break
            except Exception as exc:
                error = str(exc)
                response = None
                if attempt + 1 < retries:
                    time.sleep(0.5 * (attempt + 1))
        if response is None:
            optional_sphinx_indexes = {"py-modindex.html"}
            required = (
                parsed.path.endswith((".html", "/")) or not Path(parsed.path).suffix
            ) and Path(parsed.path).name not in optional_sphinx_indexes
            failures.append({"url": url, "required": required, "error": error})
            continue
        content_type = response.headers.get(
            "Content-Type", mimetypes.guess_type(url)[0] or ""
        )
        target = _local_web_path(raw_root, response.url, content_type)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(response.content)
        record = {
            "url": url,
            "final_url": response.url,
            "status": response.status_code,
            "content_type": content_type,
            "bytes": len(response.content),
            "sha256": sha256_file(target),
            "path": str(target.relative_to(root)).replace("\\", "/"),
        }
        records.append(record)
        if "text/html" in content_type:
            parser = LinkCollector()
            parser.feed(response.text)
            for link in parser.links:
                if not link.startswith(("mailto:", "javascript:", "data:")):
                    queue.append(urldefrag(urljoin(response.url, link))[0])
    required_failures = [item for item in failures if item["required"]]
    if required_failures:
        raise SourceGateError(f"required Sphinx pages failed: {required_failures[:5]}")
    if not records or records[0]["status"] != 200:
        raise SourceGateError("Sphinx entry page was not captured")
    return {
        "doc_id": doc.doc_id,
        "entry_url": doc.url,
        "captured_at": datetime.now(UTC).isoformat(),
        "snapshot_hash": compute_sphinx_snapshot_hash(records),
        "page_count": sum("text/html" in item["content_type"] for item in records),
        "asset_count": sum("text/html" not in item["content_type"] for item in records),
        "records": sorted(records, key=lambda value: value["url"]),
        "failures": failures,
    }


def pdf_page_count(path: Path) -> int:
    try:
        import fitz

        with fitz.open(path) as document:
            return document.page_count
    except ImportError:
        pass
    executable = shutil.which("pdfinfo")
    if executable:
        result = subprocess.run(
            [executable, str(path)], text=True, capture_output=True, check=False
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("Pages:"):
                    return int(line.split(":", 1)[1].strip())
    # M1 only needs a stable gate value. M2 replaces this with PyMuPDF's parsed count.
    count = len(re.findall(rb"/Type\s*/Page(?!s)\b", path.read_bytes()))
    if count:
        return count
    raise SourceGateError(f"unable to determine PDF page count for {path}")


def build_manifest(config: CorporaConfig, project_root: Path) -> dict[str, Any]:
    repo_root = project_root / "data" / "sources" / "repos"
    web_root = project_root / "data" / "sources" / "web"
    repositories = [acquire_repository(repo, repo_root) for repo in config.repositories]
    papers = []
    for paper in config.papers:
        path = project_root / paper.path
        actual_hash = sha256_file(path)
        if not paper.sha256 or actual_hash != paper.sha256:
            raise SourceGateError(f"PDF hash mismatch for {paper.doc_id}: {actual_hash}")
        papers.append(
            {
                "doc_id": paper.doc_id,
                "path": paper.path,
                "bytes": path.stat().st_size,
                "sha256": actual_hash,
                "page_count": pdf_page_count(path),
            }
        )
    staging_root = web_root / ".staging" / str(uuid.uuid4())
    web_documents = [crawl_sphinx(doc, staging_root) for doc in config.web_documents]
    contract_errors = [
        error
        for snapshot, doc in zip(web_documents, config.web_documents)
        for error in _validate_web_contract(snapshot, doc)
    ]
    if contract_errors:
        raise SourceGateError(f"Sphinx snapshot contract failed: {contract_errors}")
    for snapshot in web_documents:
        source = staging_root / snapshot["doc_id"]
        destination = web_root / snapshot["doc_id"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination, dirs_exist_ok=True)
    manifest = {
        "schema_version": "1.0",
        "created_at": datetime.now(UTC).isoformat(),
        "corpus_locked": True,
        "corpora_config_hash": corpora_config_hash(config),
        "snapshot_hash_algorithm": SNAPSHOT_HASH_ALGORITHM,
        "tool_versions": {
            "python": platform.python_version(),
            "git": subprocess.run(["git", "--version"], text=True, capture_output=True, check=True).stdout.strip(),
            "requests": requests.__version__,
            "pymupdf": getattr(__import__("fitz"), "__version__", "unknown"),
        },
        "repositories": repositories,
        "papers": papers,
        "web_documents": web_documents,
    }
    output = project_root / "data" / "manifests" / "source_manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def verify_manifest(
    path: Path, project_root: Path, config: CorporaConfig
) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if manifest.get("corpora_config_hash") != corpora_config_hash(config):
        errors.append("manifest corpus configuration hash mismatch")
    if manifest.get("snapshot_hash_algorithm") != SNAPSHOT_HASH_ALGORITHM:
        errors.append("manifest snapshot hash algorithm mismatch")
    if not manifest.get("tool_versions"):
        errors.append("manifest tool_versions missing")
    configured_repos = {item.repo_id: item for item in config.repositories}
    if set(configured_repos) != {item["repo_id"] for item in manifest["repositories"]}:
        errors.append("manifest repository set differs from corpus configuration")
    repo_base = (project_root / "data" / "sources" / "repos").resolve()
    for repo in manifest["repositories"]:
        repo_path = Path(repo["path"])
        try:
            configured = configured_repos.get(repo["repo_id"])
            if configured is None or (
                repo["url"] != configured.url
                or repo["ref"] != configured.ref
                or repo["commit_sha"] != configured.commit_sha
            ):
                errors.append(f"repo configuration mismatch: {repo['repo_id']}")
            if not repo_path.resolve().is_relative_to(repo_base):
                errors.append(f"repo path escaped source root: {repo['repo_id']}")
            if run_git(["rev-parse", "HEAD"], cwd=repo_path) != repo["commit_sha"]:
                errors.append(f"repo SHA mismatch: {repo['repo_id']}")
            if run_git(["remote", "get-url", "origin"], cwd=repo_path) != repo["url"]:
                errors.append(f"repo remote mismatch: {repo['repo_id']}")
            if run_git(["status", "--porcelain"], cwd=repo_path):
                errors.append(f"dirty repo: {repo['repo_id']}")
            if not repo.get("readmes") or any(not (repo_path / item).is_file() for item in repo["readmes"]):
                errors.append(f"repo README missing: {repo['repo_id']}")
        except Exception as exc:
            errors.append(f"repo verification failed {repo['repo_id']}: {exc}")
    configured_papers = {item.doc_id: item for item in config.papers}
    if set(configured_papers) != {item["doc_id"] for item in manifest["papers"]}:
        errors.append("manifest paper set differs from corpus configuration")
    for paper in manifest["papers"]:
        target = project_root / paper["path"]
        configured = configured_papers.get(paper["doc_id"])
        if (
            configured is None
            or paper["path"] != configured.path
            or paper["sha256"] != configured.sha256
            or not target.is_file()
            or sha256_file(target) != paper["sha256"]
            or target.stat().st_size != paper.get("bytes")
            or pdf_page_count(target) != paper.get("page_count")
        ):
            errors.append(f"PDF mismatch: {paper['doc_id']}")
    web_root = project_root / "data" / "sources" / "web"
    configured_web = {item.doc_id: item for item in config.web_documents}
    if set(configured_web) != {item["doc_id"] for item in manifest["web_documents"]}:
        errors.append("manifest web-document set differs from corpus configuration")
    for web in manifest["web_documents"]:
        configured = configured_web.get(web["doc_id"])
        for record in web["records"]:
            target = web_root / record["path"]
            if (
                not target.resolve().is_relative_to(web_root.resolve())
                or not target.is_file()
                or sha256_file(target) != record["sha256"]
            ):
                errors.append(f"web snapshot mismatch: {record['url']}")
        if configured is None:
            errors.append(f"unknown web document: {web['doc_id']}")
        else:
            errors.extend(_validate_web_contract(web, configured))
    locked = bool(manifest.get("corpus_locked")) and not errors
    return {"corpus_locked": locked, "errors": errors}


def migrate_manifest_contract(
    path: Path, project_root: Path, config: CorporaConfig
) -> dict[str, Any]:
    """Upgrade identity metadata without changing any locked corpus file."""
    manifest = json.loads(path.read_text(encoding="utf-8"))
    web_by_id = {item.doc_id: item for item in config.web_documents}
    for web in manifest["web_documents"]:
        web["snapshot_hash"] = compute_sphinx_snapshot_hash(web["records"])
        configured = web_by_id[web["doc_id"]]
        errors = _validate_web_contract(web, configured)
        if errors:
            raise SourceGateError(f"cannot migrate invalid web snapshot: {errors}")
    manifest["corpora_config_hash"] = corpora_config_hash(config)
    manifest["snapshot_hash_algorithm"] = SNAPSHOT_HASH_ALGORITHM
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return verify_manifest(path, project_root, config)
