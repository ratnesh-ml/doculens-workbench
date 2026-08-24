from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9'_-]*", re.I)
NEWLINE = chr(10)


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source: str
    section: str
    start_line: int
    end_line: int
    text: str


@dataclass(frozen=True)
class SearchResult:
    chunk_id: str
    source: str
    section: str
    start_line: int
    end_line: int
    snippet: str
    score: float

    def to_dict(self):
        return asdict(self)


@dataclass
class Index:
    chunks: list[Chunk]
    document_frequency: dict[str, int]
    total_documents: int

    def to_json(self):
        return {"chunks": [asdict(c) for c in self.chunks], "document_frequency": self.document_frequency, "total_documents": self.total_documents}

    @classmethod
    def from_json(cls, payload):
        return cls([Chunk(**row) for row in payload["chunks"]], payload["document_frequency"], payload["total_documents"])


def tokens(text: str) -> list[str]:
    return [x.lower() for x in TOKEN_RE.findall(text)]


def chunk_text(text: str, source: str, max_chars: int = 700) -> list[Chunk]:
    lines = text.splitlines()
    out: list[Chunk] = []
    current: list[str] = []
    current_start = 1
    section = "document"

    def flush(end_line: int):
        nonlocal current, current_start
        body = NEWLINE.join(current).strip()
        if body:
            number = len(out) + 1
            out.append(Chunk(f"{Path(source).stem}-{number:03d}", source, section, current_start, end_line, body))
        current = []

    for line_no, line in enumerate(lines, 1):
        if line.startswith('#'):
            if current:
                flush(line_no - 1)
            section = line.lstrip('#').strip() or "document"
            current_start = line_no
            current.append(line)
            continue
        if current and sum(len(x) + 1 for x in current) + len(line) > max_chars:
            flush(line_no - 1)
            current_start = line_no
        current.append(line)
    if current:
        flush(len(lines))
    return out


def load_documents(folder: str | Path) -> list[Chunk]:
    folder = Path(folder)
    chunks: list[Chunk] = []
    for path in sorted(folder.rglob('*')):
        if not path.is_file() or path.name.startswith('.'):
            continue
        if path.suffix.lower() in {'.md', '.txt'}:
            chunks.extend(chunk_text(path.read_text(encoding='utf-8'), str(path), 700))
        elif path.suffix.lower() == '.csv':
            with path.open(newline='', encoding='utf-8') as handle:
                rows = list(csv.DictReader(handle))
            text = NEWLINE.join(' | '.join(f'{k}: {v}' for k, v in row.items()) for row in rows)
            chunks.extend(chunk_text(text, str(path), 700))
    return chunks


def build_index(chunks: Iterable[Chunk]) -> Index:
    chunks = list(chunks)
    df: dict[str, int] = {}
    for chunk in chunks:
        for term in set(tokens(chunk.text)):
            df[term] = df.get(term, 0) + 1
    return Index(chunks, df, len(chunks))


def _score(query_terms: list[str], chunk: Chunk, index: Index) -> float:
    body_terms = tokens(chunk.text)
    if not body_terms:
        return 0.0
    counts = {term: body_terms.count(term) for term in set(body_terms)}
    score = 0.0
    for term in query_terms:
        if term not in counts:
            continue
        idf = math.log((1 + index.total_documents) / (1 + index.document_frequency.get(term, 0))) + 1
        score += (counts[term] / len(body_terms)) * idf
    phrase = ' '.join(query_terms)
    if phrase and phrase in chunk.text.lower():
        score += 0.15
    return score


def search(index: Index, query: str, top_k: int = 5, min_score: float = 0.035) -> dict:
    query_terms = tokens(query)
    ranked = []
    for chunk in index.chunks:
        score = _score(query_terms, chunk, index)
        if score > 0:
            ranked.append(SearchResult(chunk.chunk_id, chunk.source, chunk.section, chunk.start_line, chunk.end_line, chunk.text[:360].replace(NEWLINE, ' '), round(score, 4)))
    ranked.sort(key=lambda row: (-row.score, row.chunk_id))
    evidence = ranked[:max(1, top_k)] if ranked and ranked[0].score >= min_score else []
    return {"status": "supported" if evidence else "abstain", "answerable": bool(evidence), "query_terms": query_terms, "evidence": [row.to_dict() for row in evidence]}


def evaluate(index: Index, records: Iterable[dict], top_k: int = 5) -> dict:
    rows = list(records)
    hits = 0
    reciprocal = 0.0
    abstains = 0
    for row in rows:
        result = search(index, row["query"], top_k)
        if not result["evidence"]:
            abstains += 1
        ids = [item["chunk_id"] for item in result["evidence"]]
        expected = set(row.get("relevant", []))
        positions = [i + 1 for i, item_id in enumerate(ids) if item_id in expected]
        if positions:
            hits += 1
            reciprocal += 1 / positions[0]
    total = len(rows) or 1
    return {"queries": len(rows), "hit_rate": round(hits / total, 4), "mrr": round(reciprocal / total, 4), "abstention_rate": round(abstains / total, 4)}


def save_index(index: Index, path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index.to_json(), indent=2), encoding='utf-8')


def load_index(path: str | Path) -> Index:
    return Index.from_json(json.loads(Path(path).read_text(encoding='utf-8')))
