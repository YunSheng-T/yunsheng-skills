---
name: ontology-explorer
description: Use when exploring the platform's ontology — querying object types, link types, interface types, action types, searching instances, running aggregations, or understanding data relationships across business domains (supply chain, finance, healthcare, e-commerce). Triggered by requests like "list object types", "show me the ontology", "query instances of X", "what properties does Y have", "find relationships between types", "aggregate data", "search for instances".
---

# Ontology Explorer Skill

You help users explore the platform's ontology system using the `otlg` CLI tool. The ontology models business entities (Object Types), their relationships (Link Types), shared interfaces (Interface Types), and available operations (Action Types) across 4 domains: supply_chain, finance, healthcare, ecommerce.

## Prerequisites

`otlg` CLI must be installed and available in PATH. Check with `otlg --help`. If not found, inform the user to install it first (see `scripts/INSTALL.md` in the project repo for installation instructions).

Do NOT attempt to install otlg yourself. If the command is unavailable, tell the user and stop.

## CLI Command Reference

### Metadata Queries

| Command | Description | Example |
|---------|-------------|---------|
| `otlg types` | List all object types | `otlg types --domain finance` |
| `otlg type <name>` | Show full definition of an object type | `otlg type Supplier` |
| `otlg links` | List all link types (relationships) | `otlg links --source Patient` |
| `otlg interfaces` | List interface types | `otlg interfaces` |
| `otlg actions` | List action types | `otlg actions --domain ecommerce` |
| `otlg domains` | List all business domains | `otlg domains` |

### Instance Queries

| Command | Description | Example |
|---------|-------------|---------|
| `otlg instances <type>` | List instances of an object type | `otlg instances Supplier --limit 10` |
| `otlg instance <type> <pk>` | Get a single instance by primary key | `otlg instance Supplier SUP001` |
| `otlg search <type> <query>` | Full-text search within indexed properties | `otlg search Patient "张伟"` |
| `otlg aggregate <type> <field> --func <fn>` | Aggregate: count/sum/avg/min/max | `otlg aggregate Transaction amount --func sum` |
| `otlg links-of <type> <pk>` | Show linked objects for an instance | `otlg links-of Supplier SUP001` |

### Filter Syntax

Use `--filter key=value` for instance queries. Repeatable for multiple conditions:

```bash
otlg instances Supplier --filter country=CN --limit 5
otlg instances EcomOrder --filter status=已完成 --limit 10
```

## Exploration Workflow

Follow this sequence when exploring a domain or type for the first time:

```
1. otlg domains                         → see available domains
2. otlg types --domain <domain>         → list types in a domain
3. otlg type <type_name>                → inspect properties, links, description
4. otlg instances <type_name> --limit 5 → see sample data
5. otlg links --source <type_name>      → see relationships
6. otlg links-of <type_name> <pk>       → traverse relationships for an instance
```

## Common Query Patterns

### "What domains/types exist?"
```bash
otlg domains
otlg types
otlg types --domain supply_chain
```

### "What does type X look like?"
```bash
otlg type Supplier
# Shows: properties, links, description, instance count
```

### "Show me some data of type X"
```bash
otlg instances Supplier --limit 10
otlg instances Transaction --limit 5 --filter type=转账
```

### "How are types X and Y related?"
```bash
otlg links --source Supplier
otlg links --source Patient
# Then traverse:
otlg links-of Supplier SUP001
otlg links-of Patient PAT001
```

### "What's the total/average/count of something?"
```bash
otlg aggregate Transaction amount --func sum
otlg aggregate ScProduct unit_price --func avg
otlg aggregate EcomOrder total --func count
```

### "Find instances matching a keyword"
```bash
otlg search Patient "糖尿病"
otlg search EcomProduct "蓝牙"
otlg search Supplier "华联"
```

## Available Domains

| Domain | Description | Object Types |
|--------|-------------|-------------|
| supply_chain | 供应链管理 | Supplier, ScProduct, Warehouse, PurchaseOrder, Shipment |
| finance | 金融服务 | FiCustomer, Account, Transaction, FiProduct |
| healthcare | 医疗健康 | Patient, Provider, Diagnosis, Medication, Encounter |
| ecommerce | 电商平台 | EcomUser, Merchant, EcomProduct, EcomOrder, Review |

## Output Format

All commands output **JSON** to stdout. Parse it as needed. Errors go to stderr.

## Rules

- Always use JSON output (default) — do not attempt to reformat unless the user asks.
- When the user asks about a domain, start with `otlg types --domain <domain>` to list available types.
- When the user asks about a specific type, run `otlg type <name>` to show full details before querying instances.
- Use `--limit` to avoid flooding output with large result sets.
- For aggregation questions, identify the correct type and numeric field first via `otlg type <name>`.
