"""CLI entry point for ontology explorer — registered as 'otlg' command."""

from __future__ import annotations

import argparse
import sys

from . import commands


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="otlg",
        description="Ontology Explorer CLI — query ontology metadata and instance data",
    )
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

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
