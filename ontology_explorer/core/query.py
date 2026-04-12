"""Query engine for ontology metadata and instance data.

Acts as a thin proxy: metadata queries build from the loaded ontology,
instance queries delegate to the store backend (JSON in-memory or REST server-side).
"""

from __future__ import annotations

from typing import Any

from .models import LinkType, ObjectType, OntologyDefinition
from .store import JsonOntologyStore, OntologyStore


class OntologyQuery:
    """Query interface for ontology exploration."""

    def __init__(self, store: OntologyStore | None = None) -> None:
        self._store = store or JsonOntologyStore()
        self._ontology: OntologyDefinition | None = None

    @property
    def ontology(self) -> OntologyDefinition:
        if self._ontology is None:
            self._ontology = self._store.load_ontology()
        return self._ontology

    def reload(self) -> None:
        """Force reload from store."""
        self._ontology = None
        self._store.reload()

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
                result["links"] = self._get_links_for_type(api_name)
                # Delegate instance count to store (cheap for JSON with PK index)
                try:
                    probe = self._store.query_instances(api_name, limit=1)
                    result["instanceCount"] = probe.get("total", 0)
                except Exception:
                    result["instanceCount"] = 0
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

    # ── Instance queries (delegated to store) ─────────────────────────

    def query_instances(
        self,
        type_api_name: str,
        filters: dict[str, Any] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        return self._store.query_instances(
            type_api_name, filters=filters, limit=limit, offset=offset
        )

    def get_instance(self, type_api_name: str, primary_key: str) -> dict[str, Any] | None:
        return self._store.get_instance(type_api_name, primary_key)

    def search(self, type_api_name: str, query: str, limit: int = 50) -> list[dict[str, Any]]:
        return self._store.search_instances(type_api_name, query, limit=limit)

    def aggregate(
        self, type_api_name: str, field: str, func: str
    ) -> dict[str, Any]:
        return self._store.aggregate(type_api_name, field, func)

    def follow_link(
        self, type_api_name: str, primary_key: str, link_api_name: str
    ) -> list[dict[str, Any]]:
        """Traverse a link from an instance to related instances."""
        inst = self.get_instance(type_api_name, primary_key)
        if not inst:
            return []

        link_def = self._find_link(link_api_name)
        if not link_def:
            return []

        fk_field = link_def.foreign_key_property

        if link_def.source.object_api_name == type_api_name:
            # We are at the source side of the link
            target_type = link_def.target.object_api_name

            if fk_field and fk_field in inst:
                # FK is on the source instance (e.g. source has target_id)
                fk_value = inst[fk_field]
                target_inst = self._store.get_instance(target_type, str(fk_value))
                if target_inst:
                    return [target_inst]
                return []

            # FK is on the target side (target has source_id)
            # Find all target instances whose FK matches our PK
            source_type_def = self._find_object_type(type_api_name)
            if source_type_def and fk_field:
                source_pk = source_type_def.primary_key_property_api_name
                source_pk_val = inst.get(source_pk)
                if source_pk_val is not None:
                    result = self._store.query_instances(
                        target_type, filters={fk_field: str(source_pk_val)}, limit=500
                    )
                    return result.get("instances", [])

        elif link_def.target.object_api_name == type_api_name:
            # We are at the target side of the link
            source_type = link_def.source.object_api_name

            if fk_field and fk_field in inst:
                # FK is on our instance — look up source by PK
                fk_value = inst[fk_field]
                source_inst = self._store.get_instance(source_type, str(fk_value))
                if source_inst:
                    return [source_inst]
                return []

            # FK is on the source side (reverse lookup)
            target_type_def = self._find_object_type(type_api_name)
            if target_type_def and fk_field:
                target_pk = target_type_def.primary_key_property_api_name
                target_pk_val = inst.get(target_pk)
                if target_pk_val is not None:
                    result = self._store.query_instances(
                        source_type, filters={fk_field: str(target_pk_val)}, limit=500
                    )
                    return result.get("instances", [])

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
