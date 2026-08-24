# DocuLens Workbench

DocuLens is a local-first document intelligence app for people who want to
inspect evidence instead of trusting a fluent answer. It ingests Markdown,
text, and CSV files; preserves source metadata; ranks passages with a small
hybrid lexical scorer; and returns an explicit `abstain` response when the
evidence score is too weak.

> **Design choice:** the first version does not hide retrieval behind a
> chatbot. Every result exposes the document id, section, snippet, score,
> and a stable citation target.

## What makes it a substantial project

| Layer | Implementation |
| --- | --- |
| Ingestion | Markdown/TXT/CSV loader with deterministic chunk ids |
| Retrieval | TF-IDF-like term weighting plus exact phrase bonus |
| Evidence | Ranked snippets with source path, line range, and score |
| Safety | Minimum-score abstention and unsupported-query tests |
| Evaluation | JSONL question set with hit-rate, MRR, and abstention rate |
| Product surface | CLI, FastAPI JSON API, and sample knowledge base |

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
doculens ingest sample_docs --index .doculens/index.json
doculens search "How should a model report uncertainty?" --index .doculens/index.json
doculens evaluate sample_docs/eval.jsonl --index .doculens/index.json
pytest -q
```

Start the API with `uvicorn doculens.api:app --reload` and open
`http://127.0.0.1:8000/docs`.

## API contract

`GET /health` reports the index status. `POST /search` accepts
`{ "query": "...", "top_k": 5 }` and returns `status`, `answerable`,
`evidence`, and `query_terms`. The API never fabricates an answer; a weak
query returns `status: "abstain"` and an empty evidence list.

## Why this is relevant in 2026

Modern AI applications are judged by retrieval quality, traceability, and
failure behaviour as much as by the model call. DocuLens gives a student a
small but real surface for measuring recall, MRR, citation coverage, and
abstention before adding an optional language-model adapter.

## Limitations and next experiments

The corpus is small and the scorer is lexical, so paraphrases can be missed.
The next iteration would add embeddings, a reranker, document versioning,
OCR for scanned pages, and a human-labelled evaluation set. The sample data
is educational and should not be treated as authoritative policy.

## License

MIT. See [LICENSE](LICENSE). See [INSPIRED_BY.md](INSPIRED_BY.md) for the
license-safe inspiration and clean-room implementation note.
