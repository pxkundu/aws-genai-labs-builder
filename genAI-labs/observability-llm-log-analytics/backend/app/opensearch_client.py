"""OpenSearch helper functions for querying log data."""

from __future__ import annotations

import os
from typing import Any, Dict, List

from opensearchpy import OpenSearch, RequestsHttpConnection

OS_HOST = os.getenv("OPENSEARCH_HOST", "localhost")
OS_PORT = int(os.getenv("OPENSEARCH_PORT", "9200"))
OS_INDEX = os.getenv("OPENSEARCH_LOG_INDEX", "logs-genai-*")
OS_USERNAME = os.getenv("OPENSEARCH_USERNAME")
OS_PASSWORD = os.getenv("OPENSEARCH_PASSWORD")


def get_client() -> OpenSearch:
    auth = None
    if OS_USERNAME and OS_PASSWORD:
        auth = (OS_USERNAME, OS_PASSWORD)
    return OpenSearch(
        hosts=[{"host": OS_HOST, "port": OS_PORT}],
        http_auth=auth,
        use_ssl=OS_HOST not in {"localhost", "127.0.0.1"},
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )


def fetch_logs(query: Dict[str, Any], size: int = 100) -> List[Dict[str, Any]]:
    client = get_client()
    body = {
        "size": size,
        "query": query,
        "sort": [{"@timestamp": {"order": "desc"}}],
    }
    resp = client.search(index=OS_INDEX, body=body)
    hits = resp.get("hits", {}).get("hits", [])
    return [hit.get("_source", {}) for hit in hits]
