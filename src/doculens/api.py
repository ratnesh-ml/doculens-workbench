from fastapi import FastAPI
from pydantic import BaseModel, Field

from .core import build_index, load_documents, search

app = FastAPI(title='DocuLens Workbench', version='0.1.0')
_index = build_index(load_documents('sample_docs'))


class SearchRequest(BaseModel):
    query: str = Field(min_length=2)
    top_k: int = Field(default=5, ge=1, le=20)


@app.get('/health')
def health():
    return {'status': 'ok', 'chunks': len(_index.chunks), 'version': '0.1.0'}


@app.post('/search')
def search_endpoint(request: SearchRequest):
    return search(_index, request.query, request.top_k)
