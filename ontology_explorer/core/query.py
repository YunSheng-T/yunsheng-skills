"""Query engine for ontology metadata and instance data."""

from __future__ import annotations

import statistics
from typing import Any

from .models import LinkType, ObjectType, OntologyDefinition
from .store import OntologyStore


class OntologyQuery:
    """Query interface for ontology exploration."""

    def __init__(self, store: OntologyStore | None = None) -> None:
        self._store = store or OntologyStore()
        self._ontology: OntologyDefinition | None = None
        self._instances: dict[str, list[dict[str, Any]]] | None = None

    @property
    def ontology(self) -> OntologyDefinition:
        if self._ontology is None:
            self._ontology = self._store.load_ontology()
        return self._ontology

    @property
    def instances(self) -> dict[str, list[dict[str, Any]]]:
        if self._instances is None:
            self._instances = self._store.load_all_instances()
        return self._instances

    def reload(self) -> None:
        """Force reload from disk."""
        self._ontology = None
        self._instances = None

    # ── Metadata queries ─────────────────────────────────────────────

    def list_object_types(self, domain: str | None = None) -> list[dict[str, Any]]:
        types = self.ontology.object_types
        if domain:
            types = [t for t in types if t.domain == domain]
        return [
            {
                "apiName": t.api_name,
                "displayName": t.display_name,
                "pluralDisplayName": t.plural_display_name,
                "description": t.description,
                "domain": t.domain,
                "status": t.status,
                "propertyCount": len(t.properties),
            }
            for t in types
        ]

    def get_object_type(self, api_name: str) -> dict[str, Any] | None:
        for t in self.ontology.object_types:
            if t.api_name == api_name:
                result = t.to_dict()
                # Enrich with link information
                result["links"] = self._get_links_for_type(api_name)
                result["instanceCount"] = len(self.instances.get(api_name, []))
                return result
        return None

    def _get_links_for_type(self, api_name: str) -> list[dict[str, Any]]:
        links = []
        for link in self.ontology.link_types:
            if link.source.object_api_name == api_name:
                links.append({
                    "apiName": link.api_name,
                    "direction": "outgoing",
                    "cardinality": link.cardinality,
                    "relatedObject": link.target.object_api_name,
                    "relatedDisplayName": link.target.display_name or link.target.api_name,
                    "foreignKeyProperty": link.foreign_key_property,
                })
            elif link.target.object_api_name == api_name:
                links.append({
                    "apiName": link.api_name,
                    "direction": "incoming",
                    "cardinality": link.cardinality,
                    "relatedObject": link.source.object_api_name,
                    "relatedDisplayName": link.source.display_name or link.source.api_name,
                })
        return links

    def list_link_types(self, source_type: str | None = None) -> list[dict[str, Any]]:
        links = self.ontology.link_types
        if source_type:
            links = [
                l for l in links
                if l.source.object_api_name == source_type or l.target.object_api_name == source_type
            ]
        return [l.to_dict() for l in links]

    def list_interface_types(self) -> list[dict[str, Any]]:
        return [i.to_dict() for i in self.ontology.interface_types]

    def list_action_types(self, domain: str | None = None) -> list[dict[str, Any]]:
        actions = self.ontology.action_types
        if domain:
            actions = [a for a in actions if a.domain == domain]
        return [a.to_dict() for a in actions]

    def list_domains(self) -> list[dict[str, str]]:
        domains: dict[str, str] = {}
        for t in self.ontology.object_types:
            if t.domain and t.domain not in domains:
                domains[t.domain] = t.domain.replace("_", " ").title()
        return [{"apiName": k, "displayName": v} for k, v in domains.items()]

    # ── Instance queries ─────────────────────────────────────────────

    def query_instances(
        self,
        type_api_name: str,
        filters: dict[str, Any] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        data = self.instances.get(type_api_name, [])

        # Apply filters
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
        type_def = self._find_object_type(type_api_name)
        if not type_def:
            return None

        pk_field = type_def.primary_key_property_api_name
        for inst in self.instances.get(type_api_name, []):
            if str(inst.get(pk_field)) == str(primary_key):
                return inst
        return None

    def search(self, type_api_name: str, query: str) -> list[dict[str, Any]]:
        type_def = self._find_object_type(type_api_name)
        if not type_def:
            return []

        # Search across indexed (string) properties
        searchable_fields = [
            p.api_name for p in type_def.properties
            if p.indexed_for_search and p.type == "string"
        ]
        # Fallback: search all string properties if none are indexed
        if not searchable_fields:
            searchable_fields = [
                p.api_name for p in type_def.properties if p.type == "string"
            ]

        q = query.lower()
        results = []
        for inst in self.instances.get(type_api_name, []):
            for field_name in searchable_fields:
                val = inst.get(field_name)
                if isinstance(val, str) and q in val.lower():
                    results.append(inst)
                    break
        return results

    def aggregate(
        self, type_api_name: str, field: str, func: str
    ) -> dict[str, Any]:
        data = self.instances.get(type_api_name, [])
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

    def follow_link(
        self, type_api_name: str, primary_key: str, link_api_name: str
    ) -> list[dict[str, Any]]:
        inst = self.get_instance(type_api_name, primary_key)
        if not inst:
            return []

        link_def = self._find_link(link_api_name)
        if not link_def:
            return []

        # Determine traversal direction
        if link_def.source.object_api_name == type_api_name:
            target_type = link_def.target.object_api_name
            fk_field = link_def.foreign_key_property
            if fk_field and fk_field in inst:
                # Source side: look up target by FK value in source instance
                fk_value = inst[fk_field]
                target_type_def = self._find_object_type(target_type)
                if target_type_def:
                    target_pk = target_type_def.primary_key_property_api_name
                    return [
                        t for t in self.instances.get(target_type, [])
                        if t.get(target_pk) == fk_value
                    ]
            # Reverse: target has FK pointing to source
            source_pk_field = self._find_object_type(type_api_name)
            if source_pk_field:
                source_pk = source_pk_field.primary_key_property_api_name
                source_pk_val = inst.get(source_pk)
                return [
                    t for t in self.instances.get(target_type, [])
                    if t.get(fk_field) == source_pk_val
                ]

        elif link_def.target.object_api_name == type_api_name:
            source_type = link_def.source.object_api_name
            fk_field = link_def.foreign_key_property
            pk_val = inst.get(self._find_object_type(type_api_name).primary_key_property_api_name)
            return [
                s for s in self.instances.get(source_type, [])
                if s.get(fk_field) == pk_val
            ]

        return []

    # ── Helpers ──────────────────────────────────────────────────────

    def _find_object_type(self, api_name: str) -> ObjectType | None:
        for t in self.ontology.object_types:
            if t.api_name == api_name:
                return t
        return None

    def _find_link(self, api_name: str) -> LinkType | None:
        for l in self.ontology.link_types:
            if l.api_name == api_name:
                return l
        return None
