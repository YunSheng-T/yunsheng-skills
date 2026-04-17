"""CLI entry point for ontology explorer — registered as 'otlg' command."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from . import commands


_CONFIG_DIR = Path.home() / ".otlg"
_CONFIG_FILE = _CONFIG_DIR / "config.json"


def _load_config() -> dict:
    """Load config from ~/.otlg/config.json if it exists."""
    if _CONFIG_FILE.exists():
        with open(_CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="otlg",
        description="Ontology Explorer CLI — query ontology metadata and instance data",
    )

    # ── Global backend options ────────────────────────────────────────
    parser.add_argument(
        "--backend", choices=["json", "rest"],
        help="Data backend: 'json' (local files, default) or 'rest' (API)",
    )
    parser.add_argument("--url", help="REST API base URL (used with --backend rest)")
    parser.add_argument("--api-key", help="REST API key (optional, used with --backend rest)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ── types ────────────────────────────────────────────────────────
    p_types = subparsers.add_parser("types", help="List all object types")
    p_types.add_argument("--domain", help="Filter by domain (supply_chain, finance, healthcare, ecommerce)")
    p_types.set_defaults(func=commands.cmd_types)

    # ── type ─────────────────────────────────────────────────────────
    p_type = subparsers.add_parser("type", help="Show details of an object type")
    p_type.add_argument("api_name", help="Object type API name (e.g. Supplier)")
    p_type.set_defaults(func=commands.cmd_type)

    # ── links ────────────────────────────────────────────────────────
    p_links = subparsers.add_parser("links", help="List link types")
    p_links.add_argument("--source", help="Filter by source or target object type")
    p_links.set_defaults(func=commands.cmd_links)

    # ── interfaces ───────────────────────────────────────────────────
    p_interfaces = subparsers.add_parser("interfaces", help="List interface types")
    p_interfaces.set_defaults(func=commands.cmd_interfaces)

    # ── actions ──────────────────────────────────────────────────────
    p_actions = subparsers.add_parser("actions", help="List action types")
    p_actions.add_argument("--domain", help="Filter by domain")
    p_actions.set_defaults(func=commands.cmd_actions)

    # ── domains ──────────────────────────────────────────────────────
    p_domains = subparsers.add_parser("domains", help="List all domains")
    p_domains.set_defaults(func=commands.cmd_domains)

    # ── instances ────────────────────────────────────────────────────
    p_instances = subparsers.add_parser("instances", help="Query instances of an object type")
    p_instances.add_argument("type_api_name", help="Object type API name")
    p_instances.add_argument("--filter", action="append", help="Filter: key=value (repeatable)")
    p_instances.add_argument("--limit", type=int, default=50, help="Max results (default: 50)")
    p_instances.add_argument("--offset", type=int, default=0, help="Offset (default: 0)")
    p_instances.set_defaults(func=commands.cmd_instances)

    # ── instance ─────────────────────────────────────────────────────
    p_inst = subparsers.add_parser("instance", help="Get a single instance by primary key")
    p_inst.add_argument("type_api_name", help="Object type API name")
    p_inst.add_argument("primary_key", help="Primary key value")
    p_inst.set_defaults(func=commands.cmd_instance)

    # ── search ───────────────────────────────────────────────────────
    p_search = subparsers.add_parser("search", help="Search instances by text query")
    p_search.add_argument("type_api_name", help="Object type API name")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", type=int, default=50, help="Max results (default: 50)")
    p_search.set_defaults(func=commands.cmd_search)

    # ── aggregate ────────────────────────────────────────────────────
    p_agg = subparsers.add_parser("aggregate", help="Aggregate instances")
    p_agg.add_argument("type_api_name", help="Object type API name")
    p_agg.add_argument("field", help="Field to aggregate")
    p_agg.add_argument("--func", required=True, dest="agg_func",
                       choices=["count", "sum", "avg", "min", "max"],
                       help="Aggregation function")
    p_agg.set_defaults(func=commands.cmd_aggregate)

    # ── links-of ─────────────────────────────────────────────────────
    p_links_of = subparsers.add_parser("links-of", help="Show linked objects for an instance")
    p_links_of.add_argument("type_api_name", help="Object type API name")
    p_links_of.add_argument("primary_key", help="Primary key value")
    p_links_of.set_defaults(func=commands.cmd_links_of)

    # ── action ──────────────────────────────────────────────────────
    p_action = subparsers.add_parser("action", help="Execute an action type with parameters")
    p_action.add_argument("action_name", help="Action type API name (e.g. createPurchaseOrder)")
    p_action.add_argument("params", nargs="*", help="Action parameters as key=value pairs")
    p_action.set_defaults(func=commands.cmd_action)

    return parser


def _resolve_backend(args: argparse.Namespace):
    """Resolve the store backend from args > env vars > config file > default."""
    config = _load_config()

    backend = args.backend or os.environ.get("OTLG_BACKEND") or config.get("backend", "json")

    if backend == "rest":
        url = args.url or os.environ.get("OTLG_API_URL") or config.get("api_url")
        if not url:
            print("Error: REST backend requires --url, OTLG_API_URL, or api_url in ~/.otlg/config.json",
                  file=sys.stderr)
            sys.exit(1)
        api_key = args.api_key or os.environ.get("OTLG_API_KEY") or config.get("api_key")

        from ..core.rest_store import RestOntologyStore
        return RestOntologyStore(base_url=url, api_key=api_key)

    # Default: JSON backend
    from ..core.store import JsonOntologyStore
    return JsonOntologyStore()


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        store = _resolve_backend(args)
        args._store = store
        args.func(args)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
