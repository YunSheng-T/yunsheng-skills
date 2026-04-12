"""REST API backend for ontology data."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import OntologyDefinition
from .store import OntologyStore


class RestOntologyStore(OntologyStore):
    """Read ontology definitions and instance data from a REST API."""

    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key

    def _request(self, path: str) -> Any:
        url = f"{self._base_url}{path}"
        headers = {"Accept": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        req = Request(url, headers=headers)
        try:
            with urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            raise RuntimeError(f"API request failed: {e.code} {e.reason} — {url}") from e
        except URLError as e:
            raise RuntimeError(f"Cannot connect to API: {e.reason} — {url}") from e

    def load_ontology(self) -> OntologyDefinition:
        data = self._request("/ontology")
        return OntologyDefinition.from_dict(data)

    def load_all_instances(self) -> dict[str, list[dict[str, Any]]]:
        data = self._request("/instances")
        if not isinstance(data, dict):
            raise RuntimeError(f"Unexpected /instances response type: {type(data)}")
        return data
