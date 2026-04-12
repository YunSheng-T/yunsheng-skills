# otlg CLI Command Reference

## Metadata Queries

| Command | Description | Example |
|---------|-------------|---------|
| `otlg domains` | List all business domains | `otlg domains` |
| `otlg types` | List all object types | `otlg types --domain finance` |
| `otlg type <name>` | Show full definition of an object type | `otlg type Supplier` |
| `otlg links` | List all link types (relationships) | `otlg links --source Patient` |
| `otlg interfaces` | List interface types | `otlg interfaces` |
| `otlg actions` | List action types | `otlg actions --domain ecommerce` |

## Instance Queries

| Command | Description | Example |
|---------|-------------|---------|
| `otlg instances <type>` | List instances of an object type | `otlg instances Supplier --limit 10` |
| `otlg instance <type> <pk>` | Get a single instance by primary key | `otlg instance Supplier SUP001` |
| `otlg search <type> <query>` | Full-text search within indexed properties | `otlg search Patient "张伟"` |
| `otlg aggregate <type> <field> --func <fn>` | Aggregate: count/sum/avg/min/max | `otlg aggregate Transaction amount --func sum` |
| `otlg links-of <type> <pk>` | Show linked objects for an instance | `otlg links-of Supplier SUP001` |

## Filter Syntax

Use `--filter key=value` for instance queries. Repeatable for multiple conditions:

```bash
otlg instances Supplier --filter country=CN --limit 5
otlg instances EcomOrder --filter status=已完成 --limit 10
```

## Global Options

| Option | Description |
|--------|-------------|
| `--backend {json,rest}` | Data backend: `json` (local, default) or `rest` (API) |
| `--url URL` | REST API base URL (with `--backend rest`) |
| `--api-key KEY` | REST API key (optional, with `--backend rest`) |

## Output Format

All commands output **JSON** to stdout. Errors go to stderr.

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
otlg links-of Supplier SUP001
```

### "What's the total/average/count of something?"
```bash
otlg aggregate Transaction amount --func sum
otlg aggregate ScProduct unit_price --func avg
```

### "Find instances matching a keyword"
```bash
otlg search Patient "糖尿病"
otlg search EcomProduct "蓝牙"
```
