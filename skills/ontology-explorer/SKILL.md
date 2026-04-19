---
name: ontology-explorer
description: Use when exploring the platform's ontology — querying object types, link types, interface types, action types, searching instances, running aggregations, or understanding data relationships across business domains (supply chain, finance, healthcare, e-commerce). Triggered by requests like "list object types", "show me the ontology", "query instances of X", "what properties does Y have", "find relationships between types", "aggregate data", "search for instances".
compatibility: Requires otlg CLI (bundled or pre-installed). Python 3.8+ for pip install.
metadata:
  version: "0.1.0"
allowed-tools: Bash(otlg:*) Bash(which:*) Bash(pip:*) Bash(python:*) Bash(python3:*) Bash(uv:*) Bash(bash:*)
---

# Ontology Explorer Skill

You help users explore the platform's ontology system using the `otlg` CLI tool.

## Prerequisites

Check if `otlg` is available:

```bash
bash scripts/check_otlg.sh
```

If the script returns `{"status": "not_found"}`, inform the user that `otlg` is not installed. Show the options from `references/INSTALL.md` in this skill directory. Ask the user if they want help installing it. If the user agrees, run:

```bash
pip install git+https://github.com/YunSheng-T/yunsheng-skills.git
```

If the user declines or installation fails, stop.

## Exploration Workflow

Follow this sequence when exploring a domain or type for the first time:

```
1. otlg domains                         → see available domains
2. otlg types --domain <domain>         → list types in a domain
3. otlg type <type_name>                → inspect properties, links, description
4. otlg instances <type_name> --limit 5 → see sample data
5. otlg links --source <type_name>      → see relationships
6. otlg links-of <type_name> <pk>       → traverse relationships for an instance
7. otlg actions --domain <domain>       → see available actions
```

## Capability Discovery

When the user asks about **what can be done** with an object (e.g., "can we expedite delivery?", "can we approve this loan?", "is there a way to update status?"), you must check both data AND actions:

1. **Check actions on the target type:** `otlg actions --domain <domain>` — find actions where `targetObjectType` matches the relevant type.
2. **Check actions on linked types:** Use `otlg links --source <type>` to find related types, then check if any actions target those types.
3. **Report available capabilities:** Tell the user which actions exist, their parameters (required vs optional), and whether the current data satisfies preconditions.

Do NOT answer capability questions by guessing — always verify via `otlg actions`.

For full command details, filters, and query patterns, see `references/CLI.md`.
For domain and type listings, see `references/DOMAINS.md`.

## Rules

- Always use JSON output (default) — do not attempt to reformat unless the user asks.
- When the user asks about a domain, start with `otlg types --domain <domain>` to list available types.
- When the user asks about a specific type, run `otlg type <name>` to show full details before querying instances.
- Use `--limit` to avoid flooding output with large result sets.
- For aggregation questions, identify the correct type and numeric field first via `otlg type <name>`.

## Ontology Reasoning Constraints

The ontology's semantics and relationships are authoritative — they define how data is structured and connected. When reasoning about data:

- **Follow defined relationships only.** Use `otlg links --source <type>` and `otlg links-of <type> <pk>` to discover real connections. Do not assume relationships that are not defined in the ontology.
- **Only reference types present in the current context.** Do not speculate about object types, properties, or links that have not been observed via `otlg type`, `otlg types`, or `otlg links` output. If a type is not in the explored domain, it does not exist in that context.
- **Respect property types and constraints.** When filtering or aggregating, use the property's declared type (`string`, `integer`, `decimal`, `boolean`, `timestamp`) as shown by `otlg type <name>`. Do not treat properties as having types they were not declared with.
- **Infer via links, not assumptions.** If a user asks "which patients had this diagnosis?", traverse `patient_diagnoses` link via `otlg links-of`. Do not guess field names or join logic — the link definition is the only valid traversal path.
- **Cross-domain connections require explicit links.** Types from different domains (e.g., `Patient` and `Supplier`) are unrelated unless a link type connects them. Never assume cross-domain relationships without verifying via `otlg links`.
