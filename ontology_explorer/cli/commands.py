"""CLI subcommand implementations."""

from __future__ import annotations

import json
import sys
from typing import Any

from ..core.query import OntologyQuery
from ..core.store import OntologyStore


def _output(data: Any) -> None:
    """Print JSON output to stdout."""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _parse_filters(raw: list[str] | None) -> dict[str, str] | None:
    """Parse --filter key=value pairs."""
    if not raw:
        return None
    filters: dict[str, str] = {}
    for item in raw:
        if "=" not in item:
            print(f"Error: invalid filter format '{item}', expected key=value", file=sys.stderr)
            sys.exit(1)
        k, v = item.split("=", 1)
        filters[k] = v
    return filters


def cmd_types(args: Any) -> None:
    q = OntologyQuery()
    result = q.list_object_types(domain=args.domain)
    _output(result)


def cmd_type(args: Any) -> None:
    q = OntologyQuery()
    result = q.get_object_type(args.api_name)
    if result is None:
        print(f"Error: object type '{args.api_name}' not found", file=sys.stderr)
        sys.exit(1)
    _output(result)


def cmd_links(args: Any) -> None:
    q = OntologyQuery()
    result = q.list_link_types(source_type=args.source)
    _output(result)


def cmd_interfaces(args: Any) -> None:
    q = OntologyQuery()
    result = q.list_interface_types()
    _output(result)


def cmd_actions(args: Any) -> None:
    q = OntologyQuery()
    result = q.list_action_types(domain=args.domain)
    _output(result)


def cmd_domains(args: Any) -> None:
    q = OntologyQuery()
    result = q.list_domains()
    _output(result)


def cmd_instances(args: Any) -> None:
    q = OntologyQuery()
    filters = _parse_filters(args.filter)
    result = q.query_instances(
        args.type_api_name,
        filters=filters,
        limit=args.limit,
        offset=args.offset,
    )
    _output(result)


def cmd_instance(args: Any) -> None:
    q = OntologyQuery()
    result = q.get_instance(args.type_api_name, args.primary_key)
    if result is None:
        print(f"Error: instance '{args.primary_key}' of type '{args.type_api_name}' not found", file=sys.stderr)
        sys.exit(1)
    _output(result)


def cmd_search(args: Any) -> None:
    q = OntologyQuery()
    results = q.search(args.type_api_name, args.query)
    _output(results)


def cmd_aggregate(args: Any) -> None:
    q = OntologyQuery()
    result = q.aggregate(args.type_api_name, args.field, args.agg_func)
    _output(result)


def cmd_links_of(args: Any) -> None:
    q = OntologyQuery()
    type_def = q.get_object_type(args.type_api_name)
    if type_def is None:
        print(f"Error: object type '{args.type_api_name}' not found", file=sys.stderr)
        sys.exit(1)

    links = type_def.get("links", [])
    inst = q.get_instance(args.type_api_name, args.primary_key)
    if inst is None:
        print(f"Error: instance '{args.primary_key}' not found", file=sys.stderr)
        sys.exit(1)

    # For each outgoing link, try to follow it
    result = {
        "instance": inst,
        "linkedObjects": {},
    }
    for link in links:
        if link["direction"] == "outgoing":
            related = q.follow_link(args.type_api_name, args.primary_key, link["apiName"])
            result["linkedObjects"][link["apiName"]] = {
                "targetType": link["relatedObject"],
                "displayName": link["relatedDisplayName"],
                "count": len(related),
                "instances": related[:10],  # Limit to first 10
            }
    _output(result)
