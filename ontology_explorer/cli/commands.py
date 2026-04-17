"""CLI subcommand implementations."""

from __future__ import annotations

import json
import sys
from typing import Any

from ..core.query import OntologyQuery


def _get_query(args: Any) -> OntologyQuery:
    """Create OntologyQuery using the store resolved by __main__.py."""
    store = getattr(args, "_store", None)
    return OntologyQuery(store=store)


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
    q = _get_query(args)
    result = q.list_object_types(domain=args.domain)
    _output(result)


def cmd_type(args: Any) -> None:
    q = _get_query(args)
    result = q.get_object_type(args.api_name)
    if result is None:
        print(f"Error: object type '{args.api_name}' not found", file=sys.stderr)
        sys.exit(1)
    _output(result)


def cmd_links(args: Any) -> None:
    q = _get_query(args)
    result = q.list_link_types(source_type=args.source)
    _output(result)


def cmd_interfaces(args: Any) -> None:
    q = _get_query(args)
    result = q.list_interface_types()
    _output(result)


def cmd_actions(args: Any) -> None:
    q = _get_query(args)
    result = q.list_action_types(domain=args.domain)
    _output(result)


def cmd_domains(args: Any) -> None:
    q = _get_query(args)
    result = q.list_domains()
    _output(result)


def cmd_instances(args: Any) -> None:
    q = _get_query(args)
    filters = _parse_filters(args.filter)
    result = q.query_instances(
        args.type_api_name,
        filters=filters,
        limit=args.limit,
        offset=args.offset,
    )
    _output(result)


def cmd_instance(args: Any) -> None:
    q = _get_query(args)
    result = q.get_instance(args.type_api_name, args.primary_key)
    if result is None:
        print(f"Error: instance '{args.primary_key}' of type '{args.type_api_name}' not found", file=sys.stderr)
        sys.exit(1)
    _output(result)


def cmd_search(args: Any) -> None:
    q = _get_query(args)
    results = q.search(args.type_api_name, args.query, limit=args.limit)
    _output(results)


def cmd_aggregate(args: Any) -> None:
    q = _get_query(args)
    result = q.aggregate(args.type_api_name, args.field, args.agg_func)
    _output(result)


def cmd_links_of(args: Any) -> None:
    q = _get_query(args)
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
                "instances": related[:10],
            }
    _output(result)


def cmd_action(args: Any) -> None:
    q = _get_query(args)

    # Find the action definition
    action_def = None
    for a in q.ontology.action_types:
        if a.api_name == args.action_name:
            action_def = a
            break
    if action_def is None:
        print(f"Error: action '{args.action_name}' not found", file=sys.stderr)
        sys.exit(1)

    # Parse dynamic key=value parameters
    # Support repeated keys for arrays: items=a items=b → {"items": ["a", "b"]}
    params: dict[str, list[str]] = {}
    for item in args.params:
        if "=" not in item:
            print(f"Error: invalid parameter format '{item}', expected key=value", file=sys.stderr)
            sys.exit(1)
        k, v = item.split("=", 1)
        params.setdefault(k, []).append(v)

    # Validate required parameters
    missing = [
        p.api_name for p in action_def.parameters
        if p.required and p.api_name not in params
    ]
    if missing:
        print(f"Error: missing required parameters: {', '.join(missing)}", file=sys.stderr)
        print(f"Required parameters for '{args.action_name}':", file=sys.stderr)
        for p in action_def.parameters:
            req = "required" if p.required else "optional"
            arr = "[]" if p.array else ""
            print(f"  {p.api_name} ({p.type}{arr}, {req}) — {p.display_name}", file=sys.stderr)
        sys.exit(1)

    # Validate unknown parameters
    valid_keys = {p.api_name for p in action_def.parameters}
    unknown = set(params.keys()) - valid_keys
    if unknown:
        print(f"Error: unknown parameters: {', '.join(unknown)}", file=sys.stderr)
        print(f"Valid parameters for '{args.action_name}': {', '.join(valid_keys)}", file=sys.stderr)
        sys.exit(1)

    # Type coercion based on action parameter definitions
    typed_params: dict[str, Any] = {}
    param_defs = {p.api_name: p for p in action_def.parameters}
    for k, values in params.items():
        pdef = param_defs[k]
        coerced = [_coerce_value(v, pdef.type) for v in values]
        # If param is array type, keep as list; otherwise take single value
        if pdef.array:
            typed_params[k] = coerced
        else:
            if len(coerced) > 1:
                print(f"Error: parameter '{k}' is not an array, got {len(coerced)} values", file=sys.stderr)
                sys.exit(1)
            typed_params[k] = coerced[0]

    result = {
        "actionApiName": action_def.api_name,
        "displayName": action_def.display_name,
        "targetObjectType": action_def.target_object_type,
        "parameters": typed_params,
        "status": "submitted",
    }
    _output(result)


def _coerce_value(v: str, ptype: str) -> Any:
    """Coerce a string value to the declared parameter type."""
    if ptype == "integer":
        return int(v)
    elif ptype == "decimal":
        return float(v)
    elif ptype == "boolean":
        return v.lower() in ("true", "1", "yes")
    return v
