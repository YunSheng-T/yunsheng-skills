"""Ontology data models aligned with Palantir Foundry Ontology concepts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PropertyType:
    """A property definition within an object type."""

    api_name: str
    display_name: str
    type: str  # string, integer, decimal, boolean, timestamp, date, geopoint
    description: str = ""
    indexed_for_search: bool = False
    array: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "apiName": self.api_name,
            "displayName": self.display_name,
            "type": self.type,
            "description": self.description,
            "indexedForSearch": self.indexed_for_search,
            "array": self.array,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PropertyType:
        return cls(
            api_name=data["apiName"],
            display_name=data["displayName"],
            type=data["type"],
            description=data.get("description", ""),
            indexed_for_search=data.get("indexedForSearch", False),
            array=data.get("array", False),
        )


@dataclass
class ObjectType:
    """An object type definition in the ontology."""

    api_name: str
    display_name: str
    plural_display_name: str
    primary_key_property_api_name: str
    title_property_api_name: str
    properties: list[PropertyType] = field(default_factory=list)
    description: str = ""
    icon: str = "cube"
    icon_color: str = "#4C90F0"
    status: str = "active"
    domain: str = ""
    implements_interfaces: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "apiName": self.api_name,
            "displayName": self.display_name,
            "pluralDisplayName": self.plural_display_name,
            "primaryKeyPropertyApiName": self.primary_key_property_api_name,
            "titlePropertyApiName": self.title_property_api_name,
            "properties": [p.to_dict() for p in self.properties],
            "description": self.description,
            "icon": {"locator": self.icon, "color": self.icon_color},
            "status": self.status,
            "domain": self.domain,
            "implementsInterfaces": self.implements_interfaces,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectType:
        icon_data = data.get("icon", {})
        return cls(
            api_name=data["apiName"],
            display_name=data["displayName"],
            plural_display_name=data["pluralDisplayName"],
            primary_key_property_api_name=data["primaryKeyPropertyApiName"],
            title_property_api_name=data["titlePropertyApiName"],
            properties=[PropertyType.from_dict(p) for p in data.get("properties", [])],
            description=data.get("description", ""),
            icon=icon_data.get("locator", "cube") if isinstance(icon_data, dict) else str(icon_data),
            icon_color=icon_data.get("color", "#4C90F0") if isinstance(icon_data, dict) else "#4C90F0",
            status=data.get("status", "active"),
            domain=data.get("domain", ""),
            implements_interfaces=data.get("implementsInterfaces", []),
        )


@dataclass
class LinkTypeSide:
    """Metadata for one side of a link type."""

    object_api_name: str
    api_name: str
    display_name: str = ""
    plural_display_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "objectApiName": self.object_api_name,
            "apiName": self.api_name,
            "displayName": self.display_name,
            "pluralDisplayName": self.plural_display_name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LinkTypeSide:
        return cls(
            object_api_name=data["objectApiName"],
            api_name=data["apiName"],
            display_name=data.get("displayName", ""),
            plural_display_name=data.get("pluralDisplayName", ""),
        )


@dataclass
class LinkType:
    """A link type defining relationships between object types."""

    api_name: str
    cardinality: str  # OneToMany, ManyToMany, OneToOne
    source: LinkTypeSide = field(default_factory=lambda: LinkTypeSide("", ""))
    target: LinkTypeSide = field(default_factory=lambda: LinkTypeSide("", ""))
    foreign_key_property: str = ""
    status: str = "active"

    def to_dict(self) -> dict[str, Any]:
        return {
            "apiName": self.api_name,
            "cardinality": self.cardinality,
            "source": self.source.to_dict(),
            "target": self.target.to_dict(),
            "foreignKeyProperty": self.foreign_key_property,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LinkType:
        return cls(
            api_name=data["apiName"],
            cardinality=data["cardinality"],
            source=LinkTypeSide.from_dict(data["source"]),
            target=LinkTypeSide.from_dict(data["target"]),
            foreign_key_property=data.get("foreignKeyProperty", ""),
            status=data.get("status", "active"),
        )


@dataclass
class InterfaceProperty:
    """A shared property within an interface type."""

    api_name: str
    display_name: str
    type: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "apiName": self.api_name,
            "displayName": self.display_name,
            "type": self.type,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InterfaceProperty:
        return cls(
            api_name=data["apiName"],
            display_name=data["displayName"],
            type=data["type"],
        )


@dataclass
class InterfaceType:
    """An interface type grouping shared properties."""

    api_name: str
    display_name: str
    description: str = ""
    properties: list[InterfaceProperty] = field(default_factory=list)
    extends_interfaces: list[str] = field(default_factory=list)
    status: str = "active"

    def to_dict(self) -> dict[str, Any]:
        return {
            "apiName": self.api_name,
            "displayName": self.display_name,
            "description": self.description,
            "properties": [p.to_dict() for p in self.properties],
            "extendsInterfaces": self.extends_interfaces,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InterfaceType:
        return cls(
            api_name=data["apiName"],
            display_name=data["displayName"],
            description=data.get("description", ""),
            properties=[InterfaceProperty.from_dict(p) for p in data.get("properties", [])],
            extends_interfaces=data.get("extendsInterfaces", []),
            status=data.get("status", "active"),
        )


@dataclass
class ActionParameter:
    """A parameter definition for an action type."""

    api_name: str
    display_name: str
    type: str
    description: str = ""
    required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "apiName": self.api_name,
            "displayName": self.display_name,
            "type": self.type,
            "description": self.description,
            "required": self.required,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ActionParameter:
        return cls(
            api_name=data["apiName"],
            display_name=data["displayName"],
            type=data["type"],
            description=data.get("description", ""),
            required=data.get("required", True),
        )


@dataclass
class ActionType:
    """An action type defining operations on objects."""

    api_name: str
    display_name: str
    description: str = ""
    parameters: list[ActionParameter] = field(default_factory=list)
    target_object_type: str = ""
    domain: str = ""
    status: str = "active"

    def to_dict(self) -> dict[str, Any]:
        return {
            "apiName": self.api_name,
            "displayName": self.display_name,
            "description": self.description,
            "parameters": [p.to_dict() for p in self.parameters],
            "targetObjectType": self.target_object_type,
            "domain": self.domain,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ActionType:
        return cls(
            api_name=data["apiName"],
            display_name=data["displayName"],
            description=data.get("description", ""),
            parameters=[ActionParameter.from_dict(p) for p in data.get("parameters", [])],
            target_object_type=data.get("targetObjectType", ""),
            domain=data.get("domain", ""),
            status=data.get("status", "active"),
        )


@dataclass
class OntologyDefinition:
    """Top-level ontology definition containing all entity types."""

    object_types: list[ObjectType] = field(default_factory=list)
    link_types: list[LinkType] = field(default_factory=list)
    interface_types: list[InterfaceType] = field(default_factory=list)
    action_types: list[ActionType] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "objectTypes": [t.to_dict() for t in self.object_types],
            "linkTypes": [l.to_dict() for l in self.link_types],
            "interfaceTypes": [i.to_dict() for i in self.interface_types],
            "actionTypes": [a.to_dict() for a in self.action_types],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OntologyDefinition:
        return cls(
            object_types=[ObjectType.from_dict(t) for t in data.get("objectTypes", [])],
            link_types=[LinkType.from_dict(l) for l in data.get("linkTypes", [])],
            interface_types=[InterfaceType.from_dict(i) for i in data.get("interfaceTypes", [])],
            action_types=[ActionType.from_dict(a) for a in data.get("actionTypes", [])],
        )
