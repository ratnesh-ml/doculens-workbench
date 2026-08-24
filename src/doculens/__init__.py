"""DocuLens: small, inspectable evidence retrieval primitives."""
from .core import Index, SearchResult, build_index, search

__all__ = ["Index", "SearchResult", "build_index", "search"]
