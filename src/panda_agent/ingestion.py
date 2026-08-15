"""M2 deterministic parsing of the locked PANDA corpus."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator
from urllib.parse import urljoin

import fitz
from bs4 import BeautifulSoup

from panda_agent.models import (
    AuthorityLevel,
    CreationMethod,
    IngestionReport,
    KnowledgeAlias,
    KnowledgeObject,
    RelationCandidate,
    RelationEdge,
    ResolutionStatus,
    ReviewStatus,
    SourceLocator,
    WorkflowStep,
    stable_id,
)
from panda_agent.config import (
    load_aliases,
    load_corpora,
    load_knowledge_schema,
    load_relation_ontology,
    load_seed_objects,
    load_seed_relations,
    validate_seed_predicates,
)
from panda_agent.source import sha256_file, verify_manifest
from panda_agent.chunking import ChunkingPolicy, DEFAULT_CHUNKING_POLICY


TEXT_EXTENSIONS = {
    ".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".C",
    ".py", ".sh", ".bash", ".cmake", ".md", ".rst", ".txt", ".yml", ".yaml",
}
EXCLUDED_PARTS = {".git", "build", "__pycache__", ".cache", "third_party", "external"}


def _token_count(text: str) -> int:
    return DEFAULT_CHUNKING_POLICY.token_count(text)


def _represented_end_line(text: str) -> int:
    """Return the inclusive final line represented by ``text``.

    A trailing newline terminates the preceding line; it does not make an
    otherwise unrepresented following blank line part of a truncated object.
    This deliberately counts ``\n`` so it gives the same line semantics for
    LF and CRLF source text.
    """
    if not text:
        return 1
    return text.count("\n", 0, len(text) - 1) + 1


def _truncated_file_locator(path: str, text: str, limit: int) -> SourceLocator:
    """Locate exactly the prefix stored on a bounded file-level object."""
    represented = text[:limit]
    return SourceLocator(
        path=path,
        start_line=1,
        end_line=_represented_end_line(represented),
    )


def _derived_chunk_locator(
    parent: SourceLocator,
    parent_text: str,
    start_offset: int,
    end_offset: int,
) -> SourceLocator:
    """Copy a parent locator and narrow it from deterministic text offsets.

    The offsets are produced while splitting the parent text from left to
    right.  They are intentionally not reconstructed from chunk text: a
    repeated paragraph must never select an earlier equal occurrence.
    """
    if parent.start_line is None or parent.end_line is None or end_offset <= start_offset:
        return parent
    start_line = parent.start_line + parent_text.count("\n", 0, start_offset)
    end_line = parent.start_line + parent_text.count("\n", 0, end_offset - 1)
    start_line = min(max(start_line, parent.start_line), parent.end_line)
    end_line = min(max(end_line, start_line), parent.end_line)
    return parent.model_copy(update={"start_line": start_line, "end_line": end_line})


def _without_nul(value: Any) -> Any:
    if isinstance(value,str): return value.replace("\x00","\ufffd")
    if isinstance(value,list): return [_without_nul(item) for item in value]
    if isinstance(value,dict): return {key:_without_nul(item) for key,item in value.items()}
    return value


def _object(
    *, object_type: str, source_id: str, version: str, title: str, text: str,
    locator: SourceLocator, canonical: str, authority: AuthorityLevel = AuthorityLevel.PRIMARY,
    parent: str | None = None, metadata: dict[str, Any] | None = None,
) -> KnowledgeObject:
    text = _without_nul(text); title = _without_nul(title); metadata = _without_nul(metadata or {})
    return KnowledgeObject(
        object_id=stable_id(version, object_type, canonical, prefix="object"),
        object_type=object_type, source_id=source_id, source_version_id=version,
        title=title, text=text, authority_level=authority, locator=locator,
        parent_object_id=parent, canonical_locator=canonical, chunk_parent_id=parent,
        token_count=_token_count(text), metadata=metadata,
    )


def _relation_candidate(
    *,
    subject_id: str,
    predicate: str,
    raw_target: str,
    version: str,
    resolution_scope: str,
    confidence: float,
    metadata: dict[str, Any] | None = None,
) -> RelationCandidate:
    return RelationCandidate(
        candidate_id=stable_id(
            subject_id, predicate, raw_target, resolution_scope, prefix="candidate"
        ),
        subject_id=subject_id,
        predicate=predicate,
        raw_target=raw_target,
        source_version_ids=[version],
        resolution_scope=resolution_scope,
        confidence=confidence,
        metadata=_without_nul(metadata or {}),
    )


def _walk(node: Any) -> Iterable[Any]:
    yield node
    for child in node.children:
        yield from _walk(child)


def _node_name(node: Any, data: bytes) -> str:
    scope = node
    if node.type == "function_definition":
        scope = next((item for item in _walk(node) if item.type == "function_declarator"), node)
    candidates = [item for item in _walk(scope) if item.type in {"identifier", "field_identifier", "type_identifier", "operator_name", "destructor_name"}]
    selected = candidates[0] if node.type == "function_definition" else (candidates[-1] if candidates else None)
    return data[selected.start_byte:selected.end_byte].decode("utf-8", "replace") if selected else "anonymous"


def _meaningful_gap(text: str) -> bool:
    return bool(re.search(r"[A-Za-z0-9_#]", text))


def _region_object(
    *,
    parent: KnowledgeObject,
    text: str,
    start: int,
    end: int,
    index: int,
    object_type: str,
    source_id: str,
    version: str,
    language: str,
    region_kind: str,
) -> KnowledgeObject:
    """One deterministic, parent-bounded source region object."""
    locator = _derived_chunk_locator(parent.locator, text, start, end)
    line = locator.start_line or 1
    return _object(
        object_type=object_type,
        source_id=source_id,
        version=version,
        title=f"{parent.title} [top-level region {index}]",
        text=text[start:end],
        parent=parent.object_id,
        canonical=f"{parent.canonical_locator or parent.object_id}:top-level-gap:{line}:{index}",
        authority=parent.authority_level,
        locator=locator,
        metadata={
            "language": language,
            "region_kind": region_kind,
            "b5_source_gap": True,
            "parent_source_file": parent.object_id,
        },
    )


def _text_gap_objects(
    *,
    parent: KnowledgeObject,
    text: str,
    covered: list[tuple[int, int]],
    object_type: str,
    source_id: str,
    version: str,
    language: str,
    region_kind: str,
) -> list[KnowledgeObject]:
    """Represent non-symbol source spans without copying symbol bodies."""
    merged: list[tuple[int, int]] = []
    for start, end in sorted(covered):
        start, end = max(0, start), min(len(text), end)
        if start >= end:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    gaps: list[tuple[int, int]] = []
    cursor = 0
    for start, end in merged:
        gap_start, gap_end = _trim_span(text, cursor, start)
        if gap_start < gap_end and _meaningful_gap(text[gap_start:gap_end]):
            gaps.append((gap_start, gap_end))
        cursor = end
    gap_start, gap_end = _trim_span(text, cursor, len(text))
    if gap_start < gap_end and _meaningful_gap(text[gap_start:gap_end]):
        gaps.append((gap_start, gap_end))
    return [
        _region_object(
            parent=parent, text=text, start=start, end=end, index=index,
            object_type=object_type, source_id=source_id, version=version,
            language=language, region_kind=region_kind,
        )
        for index, (start, end) in enumerate(gaps, 1)
    ]


def _paragraph_region_objects(
    *,
    parent: KnowledgeObject,
    text: str,
    source_id: str,
    version: str,
    language: str,
    region_kind: str,
) -> list[KnowledgeObject]:
    """Represent blank-line paragraph blocks of a generic text/config file."""
    spans: list[tuple[int, int]] = []
    cursor = 0
    for separator in re.finditer(r"\n\s*\n", text):
        start, end = _trim_span(text, cursor, separator.start())
        if start < end and _meaningful_gap(text[start:end]):
            spans.append((start, end))
        cursor = separator.end()
    start, end = _trim_span(text, cursor, len(text))
    if start < end and _meaningful_gap(text[start:end]):
        spans.append((start, end))
    return [
        _region_object(
            parent=parent, text=text, start=start, end=end, index=index,
            object_type="source_file_chunk", source_id=source_id, version=version,
            language=language, region_kind=region_kind,
        )
        for index, (start, end) in enumerate(spans, 1)
    ]


def parse_cpp(path: Path, relative: str, source_id: str, version: str, *, full_source: bool = False) -> tuple[list[KnowledgeObject], list[RelationCandidate]]:
    from tree_sitter import Language, Parser
    import tree_sitter_cpp

    data = path.read_bytes()
    parser = Parser(Language(tree_sitter_cpp.language()))
    tree = parser.parse(data)
    objects: list[KnowledgeObject] = []
    relations: list[RelationCandidate] = []
    file_text = data.decode("utf-8", "replace")
    file_obj = _object(
        object_type="source_file", source_id=source_id, version=version,
        title=relative, text=file_text if full_source else file_text[:20000],
        locator=(SourceLocator(path=relative, start_line=1, end_line=_represented_end_line(file_text))
                 if full_source else _truncated_file_locator(relative, file_text, 20000)),
        canonical=relative, metadata={"language": "cpp"},
    )
    objects.append(file_obj)
    covered_spans: list[tuple[int, int]] = []
    for node in _walk(tree.root_node):
        type_map = {"function_definition": "function", "class_specifier": "class", "struct_specifier": "class"}
        if node.type not in type_map:
            continue
        covered_spans.append((node.start_byte, node.end_byte))
        name = _node_name(node, data)
        text = data[node.start_byte:node.end_byte].decode("utf-8", "replace")
        canonical = f"{relative}:{name}:{node.start_point.row + 1}"
        symbol_obj=_object(
            object_type=type_map[node.type], source_id=source_id, version=version,
            title=name, text=text, parent=file_obj.object_id, canonical=canonical,
            locator=SourceLocator(path=relative, symbol=name, start_line=node.start_point.row + 1, end_line=node.end_point.row + 1),
            metadata={"language": "cpp", "has_parse_error": node.has_error},
        )
        objects.append(symbol_obj)
        if node.type == "function_definition":
            for call in (item for item in _walk(node) if item.type == "call_expression"):
                target=data[call.children[0].start_byte:call.children[0].end_byte].decode("utf-8","replace") if call.children else ""
                if target and len(target)<200:
                    relations.append(_relation_candidate(
                        subject_id=symbol_obj.object_id, predicate="CALLS", raw_target=target,
                        version=version, resolution_scope="symbol", confidence=0.8,
                        metadata={"subject_path": relative},
                    ))
        elif node.type in {"class_specifier","struct_specifier"}:
            for base in (item for item in _walk(node) if item.type == "base_class_clause"):
                target=data[base.start_byte:base.end_byte].decode("utf-8","replace").lstrip(": ")
                if target:
                    relations.append(_relation_candidate(
                        subject_id=symbol_obj.object_id, predicate="INHERITS", raw_target=target,
                        version=version, resolution_scope="symbol", confidence=0.9,
                        metadata={"subject_path": relative},
                    ))
    # The byte spans are converted after decoding only for the overwhelmingly
    # UTF-8 source corpus. Parser-native line locators remain authoritative.
    character_spans = [
        (len(data[:start].decode("utf-8", "replace")), len(data[:end].decode("utf-8", "replace")))
        for start, end in covered_spans
    ]
    objects.extend(_text_gap_objects(
        parent=file_obj, text=file_text, covered=character_spans,
        object_type="source_file_chunk", source_id=source_id, version=version,
        language="cpp", region_kind="cpp_top_level_gap",
    ))
    for include in re.finditer(r'^\s*#\s*include\s*[<"]([^>"]+)[>"]', file_text, re.MULTILINE):
        target = include.group(1)
        relations.append(_relation_candidate(
            subject_id=file_obj.object_id, predicate="INCLUDES", raw_target=target,
            version=version, resolution_scope="include", confidence=1.0,
            metadata={"relation_subtype": "INCLUDES", "line": file_text[:include.start()].count("\n") + 1, "subject_path": relative},
        ))
    for match in re.finditer(r'(?:(?:Get|Register|Fill|Find)Object|TClonesArray)\s*\(\s*"([^"]+)"', file_text):
        branch = match.group(1)
        relations.append(_relation_candidate(
            subject_id=file_obj.object_id, predicate="READS", raw_target=branch,
            version=version, resolution_scope="root_branch", confidence=0.9,
            metadata={"relation_subtype": "ROOT_BRANCH", "subject_path": relative},
        ))
    for match in re.finditer(r'(?:getenv|Getenv)\s*\(\s*"([A-Za-z_][A-Za-z0-9_]*)"',file_text):
        name=match.group(1); relations.append(_relation_candidate(
            subject_id=file_obj.object_id, predicate="READS", raw_target=name,
            version=version, resolution_scope="environment_variable", confidence=1.0,
            metadata={"relation_subtype":"ENVIRONMENT_VARIABLE", "subject_path": relative},
        ))
    for match in re.finditer(r'AddTask\s*\([^;\n]*?(Pnd[A-Za-z0-9_]+)',file_text):
        task=match.group(1); relations.append(_relation_candidate(
            subject_id=file_obj.object_id, predicate="CONFIGURES", raw_target=task,
            version=version, resolution_scope="symbol", confidence=0.9,
            metadata={"relation_subtype":"FAIRROOT_TASK", "subject_path": relative},
        ))
    return objects, relations


def parse_python(path: Path, relative: str, source_id: str, version: str, *, full_source: bool = False) -> tuple[list[KnowledgeObject], list[RelationCandidate], list[WorkflowStep]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    file_obj = _object(object_type="python_script", source_id=source_id, version=version, title=relative, text=text if full_source else text[:20000],
        locator=(SourceLocator(path=relative, start_line=1, end_line=_represented_end_line(text)) if full_source else _truncated_file_locator(relative, text, 20000)), canonical=relative, metadata={"language": "python"})
    objects = [file_obj]
    try:
        tree = ast.parse(text)
        lines = text.splitlines(keepends=True)
        offsets = [0]
        for line in lines:
            offsets.append(offsets[-1] + len(line))
        covered: list[tuple[int, int]] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                kind = "class" if isinstance(node, ast.ClassDef) else "function"
                segment = ast.get_source_segment(text, node) or node.name
                objects.append(_object(object_type=kind, source_id=source_id, version=version, title=node.name, text=segment,
                    parent=file_obj.object_id, canonical=f"{relative}:{node.name}:{node.lineno}",
                    locator=SourceLocator(path=relative, symbol=node.name, start_line=node.lineno, end_line=getattr(node, "end_lineno", node.lineno)), metadata={"language": "python"}))
                end_line = getattr(node, "end_lineno", node.lineno)
                end_column = getattr(node, "end_col_offset", 0)
                covered.append((offsets[node.lineno - 1] + node.col_offset, offsets[end_line - 1] + end_column))
        objects.extend(_text_gap_objects(
            parent=file_obj, text=text, covered=covered,
            object_type="python_script_chunk", source_id=source_id, version=version,
            language="python", region_kind="python_module_gap",
        ))
    except SyntaxError:
        pass
    inputs = sorted(set(re.findall(r'["\']([^"\']+\.(?:root|json|txt|yaml))["\']', text)))
    workflows = [WorkflowStep(workflow_id=f"script.{source_id}", step_id=file_obj.object_id, name=relative, entrypoint_object_id=file_obj.object_id, inputs=inputs)] if inputs else []
    return objects, [], workflows


def parse_generic(path: Path, relative: str, source_id: str, version: str, *, full_source: bool = False) -> tuple[list[KnowledgeObject], list[RelationCandidate], list[WorkflowStep]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    kind = "readme_section" if path.name.lower().startswith("readme") else ("cmake_target" if path.name == "CMakeLists.txt" or path.suffix == ".cmake" else "source_file")
    obj = _object(object_type=kind, source_id=source_id, version=version, title=relative, text=text if full_source else text[:30000],
        locator=(SourceLocator(path=relative, start_line=1, end_line=_represented_end_line(text)) if full_source else _truncated_file_locator(relative, text, 30000)), canonical=relative,
        authority=AuthorityLevel.OPERATIONAL if kind == "readme_section" else AuthorityLevel.PRIMARY)
    objects=[obj]
    if kind=="readme_section":
        matches=list(re.finditer(r'(?m)^(#{1,6})\s+(.+?)\s*$',text))
        heading_stack: list[tuple[int, str]] = []
        for index,match in enumerate(matches):
            end=matches[index+1].start() if index+1<len(matches) else len(text); section=text[match.start():end].strip()
            if section:
                line=text[:match.start()].count("\n")+1; title=match.group(2).strip(); level=len(match.group(1))
                while heading_stack and heading_stack[-1][0] >= level:
                    heading_stack.pop()
                section_path=[item[1] for item in heading_stack] + [title]
                heading_stack.append((level, title))
                objects.append(_object(object_type="readme_section",source_id=source_id,version=version,title=title,text=section,parent=obj.object_id,canonical=f"{relative}#{title}:{line}",locator=SourceLocator(path=relative,start_line=line,end_line=line+section.count("\n"),section_path=section_path),authority=AuthorityLevel.OPERATIONAL))
    else:
        # B5: close the generic text/config source-file coverage hole with
        # deterministic blank-line paragraph regions.  The parent stays a
        # non-embedding-eligible provenance container when oversized.
        objects.extend(_paragraph_region_objects(
            parent=obj, text=text, source_id=source_id, version=version,
            language=path.suffix.lstrip(".").lower() or "text",
            region_kind="generic_text_block",
        ))
    return objects, [], []


def parse_cmake(path:Path,relative:str,source_id:str,version:str)->tuple[list[KnowledgeObject],list[RelationCandidate],list[WorkflowStep]]:
    text=path.read_text(encoding="utf-8",errors="replace"); objects=[]; relations=[]
    file_obj=_object(object_type="source_file",source_id=source_id,version=version,title=relative,text=text,locator=SourceLocator(path=relative,start_line=1,end_line=max(1,text.count("\n")+1)),canonical=relative,metadata={"language":"cmake"}); objects.append(file_obj)
    pattern=re.compile(r'(?ims)^\s*(add_library|add_executable|target_link_libraries|add_subdirectory)\s*\((.*?)\)')
    covered: list[tuple[int, int]] = []
    for match in pattern.finditer(text):
        covered.append((match.start(), match.end()))
        args=re.findall(r'[^\s"\']+|"[^"]*"|\'[^\']*\'',match.group(2));
        if not args: continue
        command,target=match.group(1).lower(),args[0].strip("\"'"); line=text[:match.start()].count("\n")+1
        obj=_object(object_type="cmake_target",source_id=source_id,version=version,title=target,text=match.group(0),parent=file_obj.object_id,canonical=f"{relative}:{command}:{target}:{line}",locator=SourceLocator(path=relative,symbol=target,start_line=line,end_line=line+match.group(0).count("\n")),metadata={"command":command,"arguments":args}); objects.append(obj)
        if command=="target_link_libraries":
            for dependency in args[1:]: relations.append(_relation_candidate(
                subject_id=obj.object_id, predicate="DEPENDS_ON", raw_target=dependency,
                version=version, resolution_scope="cmake_target", confidence=1.0,
                metadata={"subject_path": relative},
            ))
    objects.extend(_text_gap_objects(
        parent=file_obj, text=text, covered=covered,
        object_type="source_file_chunk", source_id=source_id, version=version,
        language="cmake", region_kind="cmake_configuration_gap",
    ))
    return objects,relations,[]


def parse_shell(path:Path,relative:str,source_id:str,version:str)->tuple[list[KnowledgeObject],list[RelationCandidate],list[WorkflowStep]]:
    from tree_sitter import Language,Parser
    import tree_sitter_bash
    data=path.read_bytes(); tree=Parser(Language(tree_sitter_bash.language())).parse(data); text=data.decode("utf-8","replace")
    obj=_object(object_type="shell_script",source_id=source_id,version=version,title=relative,text=text,locator=SourceLocator(path=relative,start_line=1,end_line=max(1,text.count("\n")+1)),canonical=relative,metadata={"language":"bash","has_parse_error":tree.root_node.has_error})
    files=sorted(set(re.findall(r'[^\s"\']+\.(?:root|json|txt|yaml|yml)',text))); workflow=WorkflowStep(workflow_id=f"script.{source_id}",step_id=obj.object_id,name=relative,entrypoint_object_id=obj.object_id,inputs=files,metadata={"command_count":sum(1 for node in _walk(tree.root_node) if node.type=="command")})
    return [obj],[],[workflow]


def parse_repository(
    repo: dict[str, Any],
    *,
    candidate_sink: Callable[[Iterable[RelationCandidate]], None] | None = None,
) -> tuple[list[KnowledgeObject], list[RelationCandidate], list[WorkflowStep], list[dict[str, Any]]]:
    root = Path(repo["path"]); source_id = repo["repo_id"]; version = f"{source_id}@{repo['commit_sha']}"
    objects: list[KnowledgeObject] = []; relations: list[RelationCandidate] = []; workflows: list[WorkflowStep] = []; errors: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part.lower() in EXCLUDED_PARTS for part in path.relative_to(root).parts):
            continue
        if path.suffix not in TEXT_EXTENSIONS and path.name != "CMakeLists.txt":
            continue
        relative = str(path.relative_to(root)).replace("\\", "/")
        try:
            if path.suffix.lower() in {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"} or path.suffix == ".C":
                o, r = parse_cpp(path, relative, source_id, version, full_source=True); w = []
            elif path.suffix == ".py":
                o, r, w = parse_python(path, relative, source_id, version, full_source=True)
            elif path.suffix.lower() in {".sh",".bash"}:
                o,r,w=parse_shell(path,relative,source_id,version)
            elif path.name == "CMakeLists.txt" or path.suffix == ".cmake":
                o,r,w=parse_cmake(path,relative,source_id,version)
            else:
                o, r, w = parse_generic(path, relative, source_id, version, full_source=True)
            objects.extend(o)
            if candidate_sink is None:
                relations.extend(r)
            else:
                candidate_sink(r)
            workflows.extend(w)
        except Exception as exc:
            errors.append({"source": source_id, "path": relative, "error": str(exc)})
    return objects, relations, workflows, errors


class RelationCandidateSpool:
    """Disk-backed, deterministically ordered relation-candidate buffer."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.connection = sqlite3.connect(path)
        self.connection.execute(
            "CREATE TABLE candidates(candidate_id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
        )

    def add(self, candidates: Iterable[RelationCandidate]) -> None:
        rows = (
            (
                item.candidate_id,
                json.dumps(item.model_dump(mode="json"), ensure_ascii=False, sort_keys=True),
            )
            for item in candidates
        )
        self.connection.executemany(
            "INSERT OR REPLACE INTO candidates(candidate_id,payload) VALUES(?,?)", rows
        )
        self.connection.commit()

    def __iter__(self) -> Iterator[RelationCandidate]:
        cursor = self.connection.execute(
            "SELECT payload FROM candidates ORDER BY candidate_id"
        )
        for (payload,) in cursor:
            yield RelationCandidate.model_validate_json(payload)

    def count(self) -> int:
        return int(self.connection.execute("SELECT count(1) FROM candidates").fetchone()[0])

    def close(self) -> None:
        self.connection.close()


def parse_pdf(paper: dict[str, Any], project_root: Path) -> tuple[list[KnowledgeObject], list[dict[str, Any]]]:
    path = project_root / paper["path"]; source_id = paper["doc_id"]; version = f"{source_id}@{paper['sha256']}"
    objects: list[KnowledgeObject] = []; errors: list[dict[str, Any]] = []
    docling_items: dict[int, list[dict[str, Any]]] = {}
    try:
        cache = project_root / "data" / "cache" / "docling" / f"{paper['sha256']}.json"
        failure = cache.with_suffix(".failure.json")
        if failure.is_file():
            raise RuntimeError(json.loads(failure.read_text(encoding="utf-8"))["error"])
        if not cache.is_file():
            cache.parent.mkdir(parents=True, exist_ok=True)
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "panda_agent.docling_worker", str(path), str(cache)],
                    text=True, capture_output=True, timeout=300, check=False,
                    env={**__import__("os").environ, "OMP_NUM_THREADS": "2", "MKL_NUM_THREADS": "2"},
                )
            except subprocess.TimeoutExpired as exc:
                failure.write_text(json.dumps({"error":"Docling timeout after 300 seconds"}),encoding="utf-8")
                raise RuntimeError("Docling timeout after 300 seconds") from exc
            if result.returncode:
                message=f"Docling exited {result.returncode}"
                failure.write_text(json.dumps({"error":message}),encoding="utf-8")
                raise RuntimeError(message)
        exported = json.loads(cache.read_text(encoding="utf-8"))
        for item in exported.get("texts", []):
            for prov in item.get("prov", []) or []:
                page = int(prov.get("page_no", 1)); docling_items.setdefault(page, []).append(item)
    except Exception as exc:
        errors.append({"source": source_id, "parser": "docling", "error": str(exc), "fallback": "pymupdf"})
    current_section = "Document body"
    with fitz.open(path) as document:
        for page_index, page in enumerate(document, start=1):
            items = docling_items.get(page_index, [])
            text = "\n".join(str(item.get("text", "")) for item in items if item.get("text"))
            parser_name = "docling"
            if not text.strip():
                text = page.get_text("text"); parser_name = "pymupdf"
            if not text.strip():
                continue
            lines=[line.strip() for line in text.splitlines() if line.strip()]
            heading=next((line for line in lines[:12] if re.match(r"^(?:chapter\s+\d+|\d+(?:\.\d+)*\s+[A-Z][^.!?]{2,100})$",line,re.IGNORECASE)),None)
            if heading: current_section=heading
            blocks=[{"bbox":[round(value,2) for value in block[:4]],"text":block[4][:500]} for block in page.get_text("blocks") if str(block[4]).strip()]
            canonical = f"pdf:{source_id}:page:{page_index}"
            objects.append(_object(object_type="thesis_section", source_id=source_id, version=version,
                title=f"{source_id} PDF page {page_index}", text=text, canonical=canonical,
                locator=SourceLocator(path=paper["path"], pdf_page=page_index, section_path=[current_section]),
                metadata={"parser": parser_name, "pdf_page": page_index, "blocks":blocks}))
    return objects, errors



def parse_web(web: dict[str, Any], project_root: Path) -> list[KnowledgeObject]:
    source_id = web["doc_id"]; version = f"{source_id}@{web['snapshot_hash']}"; root = project_root / "data" / "sources" / "web"
    objects: list[KnowledgeObject] = []
    for record in web["records"]:
        if "text/html" not in record["content_type"]:
            continue
        path = root / record["path"]; soup = BeautifulSoup(path.read_bytes(), "html.parser")
        for tag in soup(["script", "style", "nav"]): tag.decompose()
        headings = [tag.get_text(" ", strip=True) for tag in soup.find_all(re.compile("^h[1-6]$"))]
        text = soup.get_text("\n", strip=True)
        page_obj=_object(object_type="sphinx_page", source_id=source_id, version=version,
            title=soup.title.get_text(" ", strip=True) if soup.title else record["url"], text=text, canonical=record["url"],
            authority=AuthorityLevel.OPERATIONAL,
            locator=SourceLocator(path=record["path"], url=record["url"], snapshot_date=web["captured_at"][:10]),
            metadata={"snapshot_hash": web["snapshot_hash"], "headings": headings, "links": [urljoin(record["url"], a.get("href")) for a in soup.find_all("a", href=True)]})
        objects.append(page_obj)
        seen_sections=set()

        def section_heading(container: Any) -> Any | None:
            return container.find(re.compile("^h[1-6]$"), recursive=False) or container.find(re.compile("^h[1-6]$"))

        def section_path(container: Any, heading: Any) -> list[str]:
            ancestors = [
                item
                for item in reversed(container.find_parents())
                if item.name == "section" or (item.name == "div" and "section" in (item.get("class") or []))
            ]
            path: list[str] = []
            for item in [*ancestors, container]:
                item_heading = heading if item is container else section_heading(item)
                if item_heading:
                    path.append(item_heading.get_text(" ", strip=True))
            return path

        for index,container in enumerate(soup.select("section, div.section")):
            heading=section_heading(container)
            if not heading: continue
            title=heading.get_text(" ",strip=True); explicit_anchor=container.get("id") or heading.get("id"); anchor=explicit_anchor or f"section-{index}"
            if anchor in seen_sections: continue
            seen_sections.add(anchor); section_text=container.get_text("\n",strip=True)
            if not section_text: continue
            locator_url=f"{record['url']}#{anchor}" if explicit_anchor else record["url"]
            objects.append(_object(object_type="sphinx_section",source_id=source_id,version=version,title=title,text=section_text,parent=page_obj.object_id,canonical=f"{record['url']}#{anchor}",authority=AuthorityLevel.OPERATIONAL,locator=SourceLocator(path=record["path"],url=locator_url,snapshot_date=web["captured_at"][:10],section_path=section_path(container, heading)),metadata={"snapshot_hash":web["snapshot_hash"],"anchor":anchor}))
    return objects


def _normalize_symbol(value: str) -> str:
    value = re.sub(r"\b(?:public|protected|private|virtual)\b", "", value)
    value = re.sub(r"<[^<>]*>", "", value)
    value = value.strip().lstrip(":")
    value = value.replace("this->", "")
    return re.sub(r"\s+", "", value)


def _symbol_keys(value: str) -> list[str]:
    normalized = _normalize_symbol(value)
    values = [normalized]
    for separator in ("->", ".", "::"):
        if separator in normalized:
            values.append(normalized.rsplit(separator, 1)[-1])
    return list(dict.fromkeys(item for item in values if item))


def materialize_reference_entities(
    objects: list[KnowledgeObject], candidates: list[RelationCandidate]
) -> list[KnowledgeObject]:
    """Create real graph nodes for deterministic non-symbol references."""
    object_map = {item.object_id: item for item in objects}
    entities: dict[str, KnowledgeObject] = {}
    scope_types = {
        "root_branch": "root_branch",
        "environment_variable": "environment_variable",
    }
    for candidate in candidates:
        object_type = scope_types.get(candidate.resolution_scope)
        subject = object_map.get(candidate.subject_id)
        if not object_type or subject is None:
            continue
        canonical = f"{object_type}:{candidate.raw_target}"
        entity = _object(
            object_type=object_type,
            source_id=subject.source_id,
            version=subject.source_version_id,
            title=candidate.raw_target,
            text=(
                f"{object_type.replace('_', ' ')} {candidate.raw_target} referenced by "
                f"{subject.locator.path or subject.title}."
            ),
            locator=SourceLocator(symbol=candidate.raw_target),
            canonical=canonical,
            authority=AuthorityLevel.DERIVED,
            metadata={"reference_entity": True},
        ).model_copy(update={"embedding_eligible": False})
        entities[entity.object_id] = entity
    return sorted(entities.values(), key=lambda item: item.object_id)


def seed_knowledge_objects(project_root: Path) -> list[KnowledgeObject]:
    result: list[KnowledgeObject] = []
    for item in load_seed_objects(project_root / "configs" / "seed_objects.yaml").objects:
        result.append(
            KnowledgeObject(
                object_id=item.object_id,
                object_type=item.object_type,
                source_id=item.source_id,
                source_version_id=item.source_version_id,
                title=item.title,
                text=item.text,
                authority_level=AuthorityLevel(item.authority_level),
                locator=SourceLocator(),
                canonical_locator=item.object_id,
                token_count=_token_count(item.text),
                embedding_eligible=item.embedding_eligible,
                metadata={"curated_seed": True},
            )
        )
    return result


def seed_knowledge_aliases(
    project_root: Path, objects: Iterable[KnowledgeObject]
) -> list[KnowledgeAlias]:
    """Resolve curated aliases to canonical objects and real provenance objects."""
    object_list = list(objects)
    object_ids = {item.object_id for item in object_list}
    aliases: list[KnowledgeAlias] = []
    for item in load_aliases(project_root / "configs" / "aliases.yaml").aliases:
        if item.target_object_id not in object_ids:
            raise ValueError(f"alias target does not exist: {item.target_object_id}")
        wanted = {path.replace("\\", "/") for path in item.provenance_paths}
        provenance = sorted(
            {
                obj.object_id
                for obj in object_list
                if obj.source_id == item.source_id
                and (obj.locator.path or "").replace("\\", "/") in wanted
            }
        )
        if not provenance:
            raise ValueError(f"alias has no resolved provenance: {item.alias_text}")
        normalized = item.alias_text.strip().casefold()
        aliases.append(
            KnowledgeAlias(
                alias_id=stable_id(item.source_version_id, normalized, prefix="alias"),
                alias_text=item.alias_text,
                normalized_alias=normalized,
                target_object_id=item.target_object_id,
                alias_kind=item.alias_kind,
                source_version_id=item.source_version_id,
                review_status=ReviewStatus(item.review_status),
                provenance_object_ids=provenance,
                correction_message=item.correction_message,
                metadata={"creation_method": "curated"},
            )
        )
    return aliases


class RelationResolver:
    """Reusable resolver whose indexes are built once per ingestion run."""

    def __init__(self, objects: Iterable[KnowledgeObject]) -> None:
        # B5 coverage gaps are evidence only; they must not alter the B4
        # entity-resolution candidate set or relation identities.
        objects = [item for item in objects if not item.metadata.get("b5_source_gap")]
        self.object_map = {item.object_id: item for item in objects}
        self.by_title: dict[tuple[str, str, str], list[str]] = {}
        self.by_path: dict[tuple[str, str], list[str]] = {}
        for item in objects:
            normalized = _normalize_symbol(item.title)
            self.by_title.setdefault(
                (item.source_version_id, item.object_type, normalized), []
            ).append(item.object_id)
            if item.locator.path:
                path = item.locator.path.replace("\\", "/")
                self.by_path.setdefault((item.source_version_id, path), []).append(item.object_id)

    def resolve(self, candidate: RelationCandidate) -> tuple[RelationEdge | None, RelationCandidate]:
        object_map = self.object_map
        by_title = self.by_title
        by_path = self.by_path
        subject = object_map.get(candidate.subject_id)
        matches: list[str] = []
        symbol_types = ("function", "class", "method", "macro", "source_file")
        if subject is not None:
            version = subject.source_version_id
            scope = candidate.resolution_scope
            if scope == "include":
                raw_path = candidate.raw_target.replace("\\", "/")
                for (item_version, item_path), ids in by_path.items():
                    if item_version == version and (
                        item_path == raw_path or item_path.endswith("/" + raw_path)
                    ):
                        matches.extend(ids)
            elif scope == "cmake_target":
                matches.extend(by_title.get((version, "cmake_target", _normalize_symbol(candidate.raw_target)), []))
            elif scope in {"root_branch", "environment_variable"}:
                matches.extend(by_title.get((version, scope, _normalize_symbol(candidate.raw_target)), []))
            else:
                for key in _symbol_keys(candidate.raw_target):
                    for object_type in symbol_types:
                        matches.extend(by_title.get((version, object_type, key), []))
                matches = list(dict.fromkeys(matches))
                subject_path = candidate.metadata.get("subject_path")
                same_file = [
                    object_id for object_id in matches
                    if subject_path and object_map[object_id].locator.path == subject_path
                ]
                if len(same_file) == 1:
                    matches = same_file
        matches = sorted(set(matches))
        edge = None
        if len(matches) == 1:
            status = ResolutionStatus.RESOLVED
            target_id = matches[0]
            edge = RelationEdge(
                edge_id=stable_id(candidate.subject_id, candidate.predicate, target_id, prefix="edge"),
                subject_id=candidate.subject_id,
                predicate=candidate.predicate,
                object_id=target_id,
                source_version_ids=candidate.source_version_ids,
                confidence=candidate.confidence,
                creation_method=candidate.creation_method,
                review_status=ReviewStatus.ACCEPTED,
                evidence_object_ids=[candidate.subject_id],
                metadata={**candidate.metadata, "candidate_id": candidate.candidate_id, "resolution_method": "unique_same_version"},
            )
        elif matches:
            status = ResolutionStatus.AMBIGUOUS
        elif candidate.resolution_scope in {"include", "cmake_target"} or candidate.raw_target.startswith("std::"):
            status = ResolutionStatus.UNRESOLVED_EXTERNAL
        else:
            status = ResolutionStatus.UNRESOLVED_INTERNAL
        audited = candidate.model_copy(update={
            "candidate_object_ids": matches[:20],
            "resolution_status": status,
            "metadata": {**candidate.metadata, "candidate_match_count": len(matches), "candidate_list_truncated": len(matches) > 20},
        })
        return edge, audited


def resolve_relation_candidates(
    objects: list[KnowledgeObject], candidates: list[RelationCandidate]
) -> tuple[list[RelationEdge], list[RelationCandidate]]:
    """Compatibility wrapper for fixtures and small in-memory callers."""
    resolver = RelationResolver(objects)
    edges: list[RelationEdge] = []
    audited: list[RelationCandidate] = []
    for candidate in candidates:
        edge, audit = resolver.resolve(candidate)
        if edge is not None:
            edges.append(edge)
        audited.append(audit)
    return edges, audited


def validate_relation_integrity(
    objects: Iterable[KnowledgeObject], relations: Iterable[RelationEdge]
) -> None:
    object_ids = {item.object_id for item in objects}
    orphaned = [
        item.edge_id
        for item in relations
        if item.subject_id not in object_ids or item.object_id not in object_ids
    ]
    if orphaned:
        raise ValueError(f"accepted relations contain orphan endpoints: {orphaned[:10]}")


def validate_ingestion_contract(
    project_root: Path,
    objects: Iterable[KnowledgeObject],
    candidates: Iterable[RelationCandidate],
    relations: Iterable[RelationEdge],
) -> None:
    schema = load_knowledge_schema(project_root / "configs" / "knowledge_schema.yaml")
    ontology = load_relation_ontology(project_root / "configs" / "relation_ontology.yaml")
    allowed_types = {value for group in schema.object_types.values() for value in group}
    unknown_types = sorted(
        {
            item.object_type
            for item in objects
            if item.object_type not in allowed_types
            and not any(item.object_type.endswith(suffix) for suffix in schema.derived_type_suffixes)
        }
    )
    if unknown_types:
        raise ValueError(f"unknown knowledge object types: {unknown_types}")
    allowed_predicates = {item.name for item in ontology.predicates}
    unknown_predicates = sorted(
        ({item.predicate for item in candidates} | {item.predicate for item in relations})
        - allowed_predicates
    )
    if unknown_predicates:
        raise ValueError(f"unknown relation predicates: {unknown_predicates}")
    validate_relation_integrity(objects, relations)


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
            stream.write("\n")
    return sha256_file(path)


def _legacy_expand_embedding_chunks(objects: list[KnowledgeObject], max_chars: int) -> list[KnowledgeObject]:
    """Retain B4's explicit-size fixture behavior outside the production path."""
    expanded=[]
    for item in objects:
        if len(item.title)+1+len(item.text)<=max_chars:
            expanded.append(item); continue
        expanded.append(item.model_copy(update={"embedding_eligible":False}))
        if item.object_type=="source_file":
            continue
        paragraphs=[]; cursor=0
        for separator in re.finditer(r"\n\s*\n", item.text):
            paragraphs.append((item.text[cursor:separator.start()], cursor))
            cursor=separator.end()
        paragraphs.append((item.text[cursor:], cursor))
        chunks: list[tuple[str, int, int]]=[]; current=""; current_start=0; current_end=0
        for paragraph, paragraph_start in paragraphs:
            pieces=[(paragraph[index:index+max_chars], paragraph_start+index) for index in range(0,len(paragraph),max_chars)] or [("", paragraph_start)]
            for piece, piece_start in pieces:
                piece_end=piece_start+len(piece)
                candidate=(current+"\n\n"+piece).strip() if current else piece
                if current and len(candidate)>max_chars:
                    chunks.append((current, current_start, current_end)); current=piece; current_start=piece_start; current_end=piece_end
                else:
                    if not current:
                        current_start=piece_start; current_end=piece_end
                    else:
                        if current.strip():
                            current_start += len(current) - len(current.lstrip())
                        else:
                            current_start = piece_start + len(piece) - len(piece.lstrip())
                        if piece.strip():
                            current_end = piece_end - (len(piece) - len(piece.rstrip()))
                        else:
                            current_end -= len(current) - len(current.rstrip())
                    current=candidate
        if current: chunks.append((current, current_start, current_end))
        for index,(text,start_offset,end_offset) in enumerate(chunks,1):
            expanded.append(_object(object_type=f"{item.object_type}_chunk",source_id=item.source_id,version=item.source_version_id,title=f"{item.title} [{index}/{len(chunks)}]",text=text,parent=item.object_id,canonical=f"{item.canonical_locator or item.object_id}:chunk:{index}",authority=item.authority_level,locator=_derived_chunk_locator(item.locator, item.text, start_offset, end_offset),metadata={"derived_from":item.object_id,"chunk_index":index,"chunk_count":len(chunks)}))
    return expanded


def _trim_span(text: str, start: int, end: int) -> tuple[int, int]:
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    return start, end


def _hard_split_span(
    title: str, text: str, start: int, end: int, policy: ChunkingPolicy
) -> list[tuple[int, int]]:
    """Last-resort source-ordered splitting for one pathological line/block."""
    result: list[tuple[int, int]] = []
    cursor = start
    maximum = policy.max_text_chars(title)
    while cursor < end:
        candidate_end = min(end, cursor + maximum)
        while candidate_end > cursor and not policy.embedding_input_is_valid(
            title, text[cursor:candidate_end]
        ):
            candidate_end -= 1
        if candidate_end == cursor:
            # A single token can exceed the input ceiling. Preserve it only on
            # the non-eligible parent; no invalid child may be emitted.
            return result
        result.append((cursor, candidate_end))
        cursor = candidate_end
    return result


def _line_or_hard_spans(
    title: str, text: str, start: int, end: int, policy: ChunkingPolicy
) -> list[tuple[int, int]]:
    """Split an oversized block at source lines before the hard fallback."""
    spans: list[tuple[int, int]] = []
    line_starts = [start]
    line_starts.extend(index + 1 for index in range(start, end) if text[index] == "\n")
    line_starts.append(end)
    current_start: int | None = None
    current_end: int | None = None
    for line_start, line_end in zip(line_starts, line_starts[1:]):
        candidate_start = line_start if current_start is None else current_start
        candidate_end = line_end
        if policy.embedding_input_is_valid(title, text[candidate_start:candidate_end]):
            current_start, current_end = candidate_start, candidate_end
            continue
        if current_start is not None:
            spans.append((current_start, current_end or current_start))
            current_start = None
            current_end = None
        line_start, line_end = _trim_span(text, line_start, line_end)
        if line_start >= line_end:
            continue
        if policy.embedding_input_is_valid(title, text[line_start:line_end]):
            current_start, current_end = line_start, line_end
        else:
            spans.extend(_hard_split_span(title, text, line_start, line_end, policy))
    if current_start is not None:
        spans.append((current_start, current_end or current_start))
    return spans


def _structure_first_spans(title: str, text: str, policy: ChunkingPolicy) -> list[tuple[int, int]]:
    """Prefer paragraph/block boundaries, then source lines, then hard pieces."""
    blocks: list[tuple[int, int]] = []
    cursor = 0
    for separator in re.finditer(r"\n\s*\n", text):
        start, end = _trim_span(text, cursor, separator.start())
        if start < end:
            blocks.append((start, end))
        cursor = separator.end()
    start, end = _trim_span(text, cursor, len(text))
    if start < end:
        blocks.append((start, end))

    atoms: list[tuple[int, int]] = []
    for start, end in blocks:
        if policy.embedding_input_is_valid(title, text[start:end]):
            atoms.append((start, end))
        else:
            atoms.extend(_line_or_hard_spans(title, text, start, end, policy))

    chunks: list[tuple[int, int]] = []
    current_start: int | None = None
    current_end: int | None = None
    for start, end in atoms:
        candidate_start = start if current_start is None else current_start
        candidate_end = end
        if policy.embedding_input_is_valid(title, text[candidate_start:candidate_end]):
            current_start, current_end = candidate_start, candidate_end
        else:
            if current_start is not None:
                chunks.append((current_start, current_end or current_start))
            current_start, current_end = start, end
    if current_start is not None:
        chunks.append((current_start, current_end or current_start))
    return chunks


def expand_embedding_chunks(
    objects: list[KnowledgeObject],
    max_chars: int | None = None,
    *,
    policy: ChunkingPolicy = DEFAULT_CHUNKING_POLICY,
) -> list[KnowledgeObject]:
    """Produce only embedding-eligible children that satisfy ``policy``.

    ``max_chars`` is retained solely for pre-B5 locator fixtures. Production
    ingestion calls this function without it and therefore has one shared
    token/input contract with indexing.
    """
    if max_chars is not None:
        return _legacy_expand_embedding_chunks(objects, max_chars)
    expanded: list[KnowledgeObject] = []
    for item in objects:
        token_count = policy.token_count(item.text)
        valid = policy.embedding_input_is_valid(item.title, item.text, token_count)
        normalized = item.model_copy(update={
            "token_count": token_count,
            "embedding_eligible": valid,
        })
        if valid:
            expanded.append(normalized)
            continue
        expanded.append(normalized)
        if token_count < policy.min_tokens or item.object_type == "source_file":
            continue
        span_title = f"{item.title} [9999/9999]"
        spans = _structure_first_spans(span_title, item.text, policy)
        eligible_spans = [
            span for span in spans
            if policy.embedding_input_is_valid(span_title, item.text[span[0]:span[1]])
        ]
        for index, (start, end) in enumerate(eligible_spans, 1):
            chunk_text = item.text[start:end]
            title = f"{item.title} [{index}/{len(eligible_spans)}]"
            # The title is part of the authoritative input; shrink no further
            # only when the structural span already remains valid with it.
            if not policy.embedding_input_is_valid(title, chunk_text):
                continue
            expanded.append(_object(
                object_type=f"{item.object_type}_chunk",
                source_id=item.source_id,
                version=item.source_version_id,
                title=title,
                text=chunk_text,
                parent=item.object_id,
                canonical=f"{item.canonical_locator or item.object_id}:chunk:{index}",
                authority=item.authority_level,
                locator=_derived_chunk_locator(item.locator, item.text, start, end),
                metadata={
                    "derived_from": item.object_id,
                    "chunk_index": index,
                    "chunk_count": len(eligible_spans),
                    "chunking_policy": policy.version,
                },
            ).model_copy(update={
                "token_count": policy.token_count(chunk_text),
                "embedding_eligible": True,
            }))
    return expanded


def ingest(project_root: Path) -> IngestionReport:
    manifest_path = project_root / "data" / "manifests" / "source_manifest.json"
    gate = verify_manifest(
        manifest_path,
        project_root,
        load_corpora(project_root / "configs" / "corpora.yaml"),
    )
    if not gate["corpus_locked"]:
        raise RuntimeError(f"M1 corpus gate failed: {gate['errors']}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")); manifest_hash = sha256_file(manifest_path)
    objects: list[KnowledgeObject] = []
    workflows: list[WorkflowStep] = []
    errors: list[dict[str, Any]] = []
    output = project_root / "data" / "normalized" / manifest_hash
    output.mkdir(parents=True, exist_ok=True)
    temporary_root = project_root / "data" / "tmp" / "ingestion"
    temporary_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=temporary_root) as temporary:
        spool = RelationCandidateSpool(Path(temporary) / "relation_candidates.sqlite3")
        try:
            for repo in manifest["repositories"]:
                o, _, w, e = parse_repository(repo, candidate_sink=spool.add)
                objects.extend(o); workflows.extend(w); errors.extend(e)
            for paper in manifest["papers"]:
                o, e = parse_pdf(paper, project_root); objects.extend(o); errors.extend(e)
            for web in manifest["web_documents"]:
                objects.extend(parse_web(web, project_root))
            objects.extend(seed_knowledge_objects(project_root))
            objects.extend(materialize_reference_entities(objects, spool))
            aliases = seed_knowledge_aliases(project_root, objects)
            resolver = RelationResolver(objects)
            relations: list[RelationEdge] = []
            candidate_predicates: set[str] = set()

            def audited_records() -> Iterator[dict[str, Any]]:
                for candidate in spool:
                    candidate_predicates.add(candidate.predicate)
                    edge, audited = resolver.resolve(candidate)
                    if edge is not None:
                        relations.append(edge)
                    yield audited.model_dump(mode="json")

            candidate_hash = write_jsonl(
                output / "relation_candidates.jsonl", audited_records()
            )
            relation_candidate_count = spool.count()
        finally:
            spool.close()
    seed_relations = load_seed_relations(project_root / "configs" / "seed_relations.yaml")
    ontology = load_relation_ontology(project_root / "configs" / "relation_ontology.yaml")
    validate_seed_predicates(seed_relations, ontology)
    for seed in seed_relations.relations:
        relations.append(RelationEdge(
            edge_id=stable_id(seed.subject_id,seed.predicate,seed.object_id,prefix="edge"), subject_id=seed.subject_id,
            predicate=seed.predicate, object_id=seed.object_id, confidence=seed.confidence,
            creation_method=CreationMethod.CURATED, review_status=ReviewStatus.ACCEPTED,
            metadata={"evidence_note":seed.evidence_note},
        ))
    objects=expand_embedding_chunks(objects)
    unique_objects = {item.object_id: item for item in objects}
    unique_relations = {item.edge_id: item for item in relations}
    unique_aliases = {item.alias_id: item for item in aliases}
    unique_workflows = {item.step_id: item for item in workflows}
    validate_ingestion_contract(
        project_root,
        unique_objects.values(),
        (),
        unique_relations.values(),
    )
    allowed_predicates = {
        item.name
        for item in load_relation_ontology(
            project_root / "configs" / "relation_ontology.yaml"
        ).predicates
    }
    unknown_candidate_predicates = sorted(candidate_predicates - allowed_predicates)
    if unknown_candidate_predicates:
        raise ValueError(f"unknown relation predicates: {unknown_candidate_predicates}")
    hashes = {
        "objects": write_jsonl(output / "knowledge_objects.jsonl", (item.model_dump(mode="json") for item in sorted(unique_objects.values(), key=lambda value: value.object_id))),
        "relations": write_jsonl(output / "relation_edges.jsonl", (item.model_dump(mode="json") for item in sorted(unique_relations.values(), key=lambda value: value.edge_id))),
        "relation_candidates": candidate_hash,
        "aliases": write_jsonl(output / "knowledge_aliases.jsonl", (item.model_dump(mode="json") for item in sorted(unique_aliases.values(), key=lambda value: value.alias_id))),
        "workflows": write_jsonl(output / "workflow_steps.jsonl", (item.model_dump(mode="json") for item in sorted(unique_workflows.values(), key=lambda value: value.step_id))),
        "errors": write_jsonl(output / "parse_errors.jsonl", sorted(errors, key=lambda value: json.dumps(value, sort_keys=True))),
    }
    report = IngestionReport(manifest_hash=manifest_hash, object_count=len(unique_objects), relation_count=len(unique_relations), relation_candidate_count=relation_candidate_count, alias_count=len(unique_aliases), workflow_count=len(unique_workflows), parse_errors=errors, output_hashes=hashes)
    (output / "ingestion_report.json").write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return report
