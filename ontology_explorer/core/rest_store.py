"""REST API backend for ontology data.

Implements OntologyStore by calling the fine-grained REST API endpoints
defined in API.md. Server-side filtering, pagination, and aggregation
are used wherever possible.
"""

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
        self._ontology: OntologyDefinition | None = None

    def _request(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self._base_url}{path}"
        if params:
            # Build query string, handling repeated filter params
            query_parts = []
            for key, value in params.items():
                if isinstance(value, list):
                    for v in value:
                        query_parts.append(f"{key}={v}")
                else:
                    query_parts.append(f"{key}={value}")
            url = f"{url}?{'&'.join(query_parts)}"

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

    # ── Ontology metadata ───────────────────────────────────────────────

    def load_ontology(self) -> OntologyDefinition:
        """Build OntologyDefinition from fine-grained API endpoints.

        Calls: GET /types (detail), GET /links, GET /interfaces, GET /actions.
        Falls back to GET /ontology if fine-grained calls aren't available.
        """
        if self._ontology is not None:
            return self._ontology

        try:
            # Try fine-grained approach: get full type definitions
            types_data = self._request("/types")
            links_data = self._request("/links")
            interfaces_data = self._request("/interfaces")

            # For actions, we need to fetch per-domain or use a combined endpoint
            actions_data = self._try_get_actions()

            # If /types returns summaries (with propertyCount), we need
            # to fetch full definitions via /types/{type}
            object_types = []
            for t in types_data:
                if "properties" not in t:
                    # Summary only — fetch full definition
                    full = self._request(f"/types/{t['apiName']}")
                    object_types.append(full)
                else:
                    object_types.append(t)

            raw = {
                "objectTypes": object_types,
                "linkTypes": links_data,
                "interfaceTypes": interfaces_data,
                "actionTypes": actions_data,
            }
            self._ontology = OntologyDefinition.from_dict(raw)
        except RuntimeError:
            # Fallback: try legacy bulk endpoint
            data = self._request("/ontology")
            self._ontology = OntologyDefinition.from_dict(data)

        return self._ontology

    def _try_get_actions(self) -> list[dict[str, Any]]:
        """Try to fetch all actions. Attempts /actions first, then per-domain."""
        try:
            return self._request("/actions")
        except RuntimeError:
            pass

        # Fallback: fetch per-domain
        actions = []
        try:
            domains = self._request("/domains")
            for d in domains:
                try:
                    domain_actions = self._request(f"/domains/{d['apiName']}/actions")
                    actions.extend(domain_actions)
                except RuntimeError:
                    pass
        except RuntimeError:
            pass
        return actions

    def list_domains(self) -> list[dict[str, str]]:
        return self._request("/domains")

    def list_types_by_domain(self, domain: str) -> list[dict[str, Any]]:
        return self._request(f"/domains/{domain}/types")

    # ── Instance queries (server-side) ──────────────────────────────────

    def load_all_instances(self) -> dict[str, list[dict[str, Any]]]:
        """Load all instances via bulk endpoint (fallback only).

        Deprecated: prefer query_instances() which uses server-side pagination.
        """
        data = self._request("/instances")
        if not isinstance(data, dict):
            raise RuntimeError(f"Unexpected /instances response type: {type(data)}")
        return data

    def query_instances(
        self,
        type_api_name: str,
        filters: dict[str, Any] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if filters:
            filter_list = [f"{k}={v}" for k, v in filters.items()]
            params["filter"] = filter_list

        return self._request(f"/types/{type_api_name}/instances", params=params)

    def get_instance(self, type_api_name: str, primary_key: str) -> dict[str, Any] | None:
        try:
            return self._request(f"/types/{type_api_name}/instances/{primary_key}")
        except RuntimeError:
            return None

    def search_instances(
        self, type_api_name: str, query: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"q": query, "limit": limit}
        return self._request(f"/types/{type_api_name}/search", params=params)

    def aggregate(self, type_api_name: str, field: str, func: str) -> dict[str, Any]:
        params: dict[str, Any] = {"func": func}
        return self._request(f"/types/{type_api_name}/aggregate/{field}", params=params)
