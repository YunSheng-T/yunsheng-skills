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
| `otlg search <type> <query>` | Full-text search within indexed properties | `otlg search Patient "张伟" --limit 5` |
| `otlg aggregate <type> <field> --func <fn>` | Aggregate: count/sum/avg/min/max | `otlg aggregate Transaction amount --func sum` |
| `otlg links-of <type> <pk>` | Show linked objects for an instance | `otlg links-of Supplier SUP001` |

## Action Commands

Execute an action type with dynamic parameters. Parameters are passed as `key=value` pairs, matched against the action's defined parameters.

```bash
otlg action <action_name> key1=value1 key2=value2 ...
```

| Example | Description |
|---------|-------------|
| `otlg action createPurchaseOrder supplier_id=SUP001 items=PRD001 items=PRD002` | Create purchase order (array param via repeated key) |
| `otlg action processTransaction from_account=ACC001 to_account=ACC002 amount=1000.50 type=转账` | Process a transaction |
| `otlg action approveLoan loan_id=LN001 approved=true` | Approve a loan |

**Array parameters:** Repeat the key for each value — `items=PRD001 items=PRD002 items=PRD003` produces `["PRD001", "PRD002", "PRD003"]`. Non-array parameters with repeated values will error.

Parameters are automatically type-coerced based on the action definition (`string`, `integer`, `decimal`, `boolean`). Missing required parameters or unknown parameters produce clear error messages.

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
otlg search Patient "糖尿病" --limit 5
otlg search EcomProduct "蓝牙" --limit 10
```

### "Execute an action"
```bash
otlg action createPurchaseOrder supplier_id=SUP001 items="100x LED模组"
otlg action processTransaction from_account=ACC001 to_account=ACC002 amount=1000.50 type=转账
```
