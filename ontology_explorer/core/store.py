"""Pluggable storage layer for ontology data.

Provides an abstract base class (OntologyStore) and concrete implementations:
- JsonOntologyStore: reads from local JSON files
- RestOntologyStore: reads from a REST API (in rest_store.py)
"""

from __future__ import annotations

import json
import statistics
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .models import OntologyDefinition


# ── Abstract base ───────────────────────────────────────────────────────────

class OntologyStore(ABC):
    """Abstract interface for ontology data storage."""

    @abstractmethod
    def load_ontology(self) -> OntologyDefinition:
        """Load the full ontology definition."""
        ...

    @abstractmethod
    def load_all_instances(self) -> dict[str, list[dict[str, Any]]]:
        """Load all instance data, keyed by object type apiName.

        Deprecated: prefer query_instances / get_instance for targeted access.
        """
        ...

    def reload(self) -> None:
        """Clear any caches. Subclasses can override for custom cache behavior."""
        pass

    # ── Instance query methods ──────────────────────────────────────────
    # Default implementations use load_all_instances() as fallback.
    # REST backends should override these to use server-side filtering.

    def query_instances(
        self,
        type_api_name: str,
        filters: dict[str, Any] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Query instances with optional filters and pagination.

        Returns dict with: typeApiName, total, limit, offset, instances.
        """
        data = self.load_all_instances().get(type_api_name, [])

        if filters:
            filtered = []
            for inst in data:
                match = True
                for key, value in filters.items():
                    inst_val = inst.get(key)
                    if isinstance(value, str) and isinstance(inst_val, str):
                        if value.lower() not in inst_val.lower():
                            match = False
                            break
                    elif inst_val != value:
                        match = False
                        break
                if match:
                    filtered.append(inst)
            data = filtered

        total = len(data)
        page = data[offset : offset + limit]
        return {
            "typeApiName": type_api_name,
            "total": total,
            "limit": limit,
            "offset": offset,
            "instances": page,
        }

    def get_instance(self, type_api_name: str, primary_key: str) -> dict[str, Any] | None:
        """Get a single instance by primary key."""
        data = self.load_all_instances().get(type_api_name, [])
        # Try to determine PK field from ontology
        pk_field = self._resolve_pk_field(type_api_name)
        if pk_field:
            for inst in data:
                if str(inst.get(pk_field)) == str(primary_key):
                    return inst
        return None

    def search_instances(
        self, type_api_name: str, query: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Full-text search within indexed properties.

        Returns up to `limit` matching instances.
        """
        data = self.load_all_instances().get(type_api_name, [])
        q = query.lower()

        searchable_fields = self._resolve_searchable_fields(type_api_name)
        if not searchable_fields:
            # Fallback: search all string properties from first instance
            if data:
                searchable_fields = [
                    k for k, v in data[0].items() if isinstance(v, str)
                ]

        results = []
        for inst in data:
            for field_name in searchable_fields:
                val = inst.get(field_name)
                if isinstance(val, str) and q in val.lower():
                    results.append(inst)
                    break
            if len(results) >= limit:
                break
        return results

    def aggregate(self, type_api_name: str, field: str, func: str) -> dict[str, Any]:
        """Aggregate a numeric field: count/sum/avg/min/max."""
        data = self.load_all_instances().get(type_api_name, [])
        values = [inst.get(field) for inst in data if inst.get(field) is not None]
        numeric_values = [v for v in values if isinstance(v, (int, float))]

        result: dict[str, Any] = {
            "typeApiName": type_api_name,
            "field": field,
            "function": func,
            "totalInstances": len(data),
            "nonNullValues": len(values),
        }

        if func == "count":
            result["value"] = len(values)
        elif func == "sum":
            result["value"] = sum(numeric_values) if numeric_values else 0
        elif func == "avg":
            result["value"] = statistics.mean(numeric_values) if numeric_values else 0
        elif func == "min":
            result["value"] = min(numeric_values) if numeric_values else None
        elif func == "max":
            result["value"] = max(numeric_values) if numeric_values else None
        else:
            result["value"] = None
            result["error"] = f"Unknown function: {func}"

        return result

    def get_actions_for_type(self, type_api_name: str) -> list[dict[str, Any]]:
        """Get actions targeting a specific object type.

        Default implementation filters from loaded ontology.
        REST backends may override to call a dedicated endpoint.
        """
        try:
            ontology = self.load_ontology()
        except Exception:
            return []

        actions = []
        for action in ontology.action_types:
            if action.target_object_type == type_api_name:
                actions.append({
                    "apiName": action.api_name,
                    "displayName": action.display_name,
                    "description": action.description,
                    "parameters": [
                        {
                            "apiName": p.api_name,
                            "displayName": p.display_name,
                            "type": p.type,
                            "required": p.required,
                            "array": p.array,
                        }
                        for p in action.parameters
                    ],
                    "domain": action.domain,
                })
        return actions

    # ── Helpers for default implementations ─────────────────────────────

    def _resolve_pk_field(self, type_api_name: str) -> str | None:
        """Try to find the primary key field name from the ontology."""
        try:
            ontology = self.load_ontology()
            for t in ontology.object_types:
                if t.api_name == type_api_name:
                    return t.primary_key_property_api_name
        except Exception:
            pass
        return None

    def _resolve_searchable_fields(self, type_api_name: str) -> list[str]:
        """Find indexed-for-search string fields from the ontology."""
        try:
            ontology = self.load_ontology()
            for t in ontology.object_types:
                if t.api_name == type_api_name:
                    fields = [
                        p.api_name for p in t.properties
                        if p.indexed_for_search and p.type == "string"
                    ]
                    if fields:
                        return fields
                    # Fallback: all string properties
                    return [p.api_name for p in t.properties if p.type == "string"]
        except Exception:
            pass
        return []


# ── JSON file backend ───────────────────────────────────────────────────────

# Resolve data directory relative to the package root
_PACKAGE_DIR = Path(__file__).resolve().parent.parent
_DATA_DIR = _PACKAGE_DIR / "data"


class JsonOntologyStore(OntologyStore):
    """Read/write ontology definitions and instance data from JSON files."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or _DATA_DIR
        self._pk_index: dict[str, dict[str, dict[str, Any]]] = {}

    @property
    def data_dir(self) -> Path:
        return self._data_dir

    def load_ontology(self) -> OntologyDefinition:
        path = self._data_dir / "ontology.json"
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return OntologyDefinition.from_dict(data)

    def save_ontology(self, ontology: OntologyDefinition) -> None:
        path = self._data_dir / "ontology.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(ontology.to_dict(), f, ensure_ascii=False, indent=2)

    def load_instances(self, domain: str) -> dict[str, list[dict[str, Any]]]:
        """Load instances for a domain. Returns {type_api_name: [instances]}."""
        path = self._instance_file(domain)
        if not path.exists():
            return {}
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def load_all_instances(self) -> dict[str, list[dict[str, Any]]]:
        instances_dir = self._data_dir / "instances"
        if not instances_dir.exists():
            return {}
        result: dict[str, list[dict[str, Any]]] = {}
        for path in sorted(instances_dir.glob("*.json")):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            result.update(data)
        return result

    def save_instances(self, domain: str, data: dict[str, list[dict[str, Any]]]) -> None:
        path = self._instance_file(domain)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_instance(self, type_api_name: str, primary_key: str) -> dict[str, Any] | None:
        """O(1) lookup using PK index."""
        # Build index on first call for this type
        if type_api_name not in self._pk_index:
            self._build_pk_index(type_api_name)

        return self._pk_index.get(type_api_name, {}).get(str(primary_key))

    def reload(self) -> None:
        """Clear PK index on reload."""
        self._pk_index.clear()

    def _build_pk_index(self, type_api_name: str) -> None:
        """Build a {pk_value: instance} index for a type."""
        pk_field = self._resolve_pk_field(type_api_name)
        data = self.load_all_instances().get(type_api_name, [])

        index: dict[str, dict[str, Any]] = {}
        if pk_field:
            for inst in data:
                pk_val = inst.get(pk_field)
                if pk_val is not None:
                    index[str(pk_val)] = inst
        self._pk_index[type_api_name] = index

    def _instance_file(self, domain: str) -> Path:
        return self._data_dir / "instances" / f"{domain}.json"
