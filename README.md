# DocuLens Workbench

[![CI](https://github.com/ratnesh-ml/doculens-workbench/actions/workflows/test.yml/badge.svg)](https://github.com/ratnesh-ml/doculens-workbench/actions/workflows/test.yml)

I built DocuLens because I am more interested in an answer that can be inspected than an answer that only sounds confident. I wanted to learn what happens before the chat interface: loading documents cleanly, keeping source metadata, ranking useful passages, measuring retrieval quality, and admitting when the evidence is too weak.

DocuLens is a local-first document-intelligence workbench. It ingests Markdown, text, and CSV files; creates deterministic chunk identifiers; ranks passages with a small hybrid lexical scorer; and returns an explicit `abstain` response when the evidence does not clear the threshold.

> **My design choice:** I did not hide retrieval behind a chatbot in version one. Each result exposes a document id, section, source path, line range, snippet, score, and stable citation target.

## What I built

| Layer | Implementation | Why I included it |
| --- | --- | --- |
| Ingestion | Markdown, TXT, and CSV loader with deterministic chunk ids | So the source trail is stable and inspectable. |
| Retrieval | TF-IDF-like term weighting plus an exact-phrase bonus | A compact scorer I can reason about and measure. |
| Evidence | Ranked snippets with source path, line range, and score | So a user can check the support rather than trust a paraphrase. |
| Failure behaviour | Minimum-score abstention and unsupported-query tests | To make “I do not have enough evidence” part of the product. |
| Evaluation | JSONL question set with hit rate, MRR, and abstention rate | To measure retrieval instead of relying on a polished example. |
| Product surface | CLI, FastAPI JSON API, and a sample knowledge base | To practise moving beyond a notebook. |

## Try it locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

doculens ingest sample_docs --index .doculens/index.json
doculens search "How should a model report uncertainty?" --index .doculens/index.json
doculens evaluate sample_docs/eval.jsonl --index .doculens/index.json
pytest -q
```

To explore the service boundary, start the API and open the generated docs:

```bash
uvicorn doculens.api:app --reload
# Visit http://127.0.0.1:8000/docs
```

## API behaviour I care about

`GET /health` reports index status. `POST /search` accepts `{ "query": "...", "top_k": 5 }` and returns `status`, `answerable`, `evidence`, and `query_terms`. Weak queries return `status: "abstain"` and an empty evidence list; the API does not manufacture an answer from weak support.

## Why this matters to me as a student builder

I see retrieval quality, traceability, and failure behaviour as part of AI engineering—not an afterthought after a model call. This project gives me a small but real surface for practising recall, MRR, citation coverage, and abstention before I introduce embeddings, reranking, or a language-model adapter.

## What I would build next

The sample corpus is small and the scorer is lexical, so paraphrases can be missed. A future iteration would add permission-cleared documents, embeddings, a reranker, document versioning, OCR for scanned pages, and a human-labelled evaluation set. The sample content is educational and not authoritative policy.

## Verification, contribution, and license

Run `pytest -q` locally; GitHub Actions compiles the source and runs the test suite on pushes and pull requests. Contributor guidance is in [CONTRIBUTING.md](CONTRIBUTING.md). Use only synthetic or permission-cleared documents.

MIT licensed. See [LICENSE](LICENSE) and [INSPIRED_BY.md](INSPIRED_BY.md) for the clean-room inspiration note.
