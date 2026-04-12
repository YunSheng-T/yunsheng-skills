"""Pluggable storage layer for ontology data.

Provides an abstract base class (OntologyStore) and concrete implementations:
- JsonOntologyStore: reads from local JSON files
- RestOntologyStore: reads from a REST API (in rest_store.py)
"""

from __future__ import annotations

import json
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
        """Load all instance data, keyed by object type apiName."""
        ...

    def reload(self) -> None:
        """Clear any caches. Subclasses can override for custom cache behavior."""
        pass


# ── JSON file backend ───────────────────────────────────────────────────────

# Resolve data directory relative to the package root
_PACKAGE_DIR = Path(__file__).resolve().parent.parent
_DATA_DIR = _PACKAGE_DIR / "data"


class JsonOntologyStore(OntologyStore):
    """Read/write ontology definitions and instance data from JSON files."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or _DATA_DIR

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

    def _instance_file(self, domain: str) -> Path:
        return self._data_dir / "instances" / f"{domain}.json"
