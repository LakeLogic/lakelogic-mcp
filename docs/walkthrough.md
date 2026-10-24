# Walkthrough: your first contract

One small contract, start to finish: validate it, lint it, generate test data, run it, and read the
result. The output below was **captured from this exact example** (lakelogic-mcp 0.1.3, `seed=42`).
With another seed the IDs, and how the failures split between rules, will differ.

You can ask your assistant to do all of it in one go — *"Check orders.yaml, generate 200 rows of test
data with seed 42, run it and explain the result"* — or call the tools one at a time as below.

## 1. The contract

Save this as `orders.yaml` in your project:

```yaml
version: 1.0.0
dataset: orders
info:
  title: Orders
  owner: sales-data@example.com
  target_layer: silver
primary_key: [order_id]
model:
  fields:
    - {name: order_id, type: string, required: true}
    - {name: customer_id, type: string, required: true}
    - {name: status, type: string, required: true}
    - {name: amount, type: double, required: true}
quality:
  row_rules:
    - accepted_values: {field: status, values: [placed, shipped, delivered, cancelled]}
    - range: {field: amount, min: 0, max: 10000}
```

## 2. Validate — does it match the OLC model?

`validate_contract(path="orders.yaml")`

```json
{ "contract": "orders.yaml", "valid": true, "errors": [] }
```

## 3. Lint — does it pass the lint checks?

`lint_contract(path="orders.yaml")`

```json
{
  "contract": "orders.yaml",
  "clean": true,
  "findings": [
    {
      "rule": "VOL-001",
      "severity": "info",
      "message": "silver table has no freshness or volume SLO (contract or domain) — blind to stalled feeds / missing data.",
      "fix": "Add contract `service_levels.freshness`/`row_count`, or an `slo.*` block at the domain."
    }
  ]
}
```

`clean` is `true` because the only finding is `info`: worth knowing, not a problem. `explain_rule(code="VOL-001")`
says why the rule exists and shows a fixed contract.

## 4. Generate test data

`generate_test_data(path="orders.yaml", rows=200, invalid_ratio=0.1, seed=42)`

```json
{
  "contract": "orders.yaml",
  "data_file": "test_data/orders.csv",
  "rows": 200,
  "columns": ["order_id", "customer_id", "status", "amount", "_is_invalid", "_test_case_types"],
  "intended_invalid_rows": 20
}
```

`invalid_ratio` is a **request**: 20 of the 200 rows were made to break a rule. The two extra columns
mark which rows, and how they were broken; they are test-data markers, not part of your contract.

## 5. Run it

`run_contract(path="orders.yaml", source="test_data/orders.csv", sample=2)`

```json
{
  "contract": "orders.yaml",
  "ran": true,
  "engine": "polars",
  "good_rows": 180,
  "quarantined_rows": 20,
  "quarantine_reasons": {
    "Rule failed: status_accepted_values (\"status\" IN ('placed', 'shipped', 'delivered', 'cancelled'))": 10,
    "Rule failed: status_required (\"status\" IS NOT NULL)": 5,
    "Rule failed: customer_id_required (\"customer_id\" IS NOT NULL)": 4,
    "Rule failed: amount_range (\"amount\" >= 0 AND \"amount\" <= 10000)": 4,
    "Rule failed: order_id_required (\"order_id\" IS NOT NULL)": 2,
    "Rule failed: amount_required (\"amount\" IS NOT NULL)": 2
  },
  "quarantined_sample": [
    {
      "order_id": "ORD-658766", "customer_id": null, "status": "placed", "amount": 18.43,
      "_test_case_types": "NOT_NULL_VIOLATION",
      "_lakelogic_errors": ["Rule failed: customer_id_required (\"customer_id\" IS NOT NULL)"]
    },
    {
      "order_id": "ORD-556640", "customer_id": "CUST-526170", "status": "UNKNOWN_VGV", "amount": 28.19,
      "_test_case_types": "ACCEPTED_VALUE_VIOLATION",
      "_lakelogic_errors": ["Rule failed: status_accepted_values (\"status\" IN ('placed', 'shipped', 'delivered', 'cancelled'))"]
    }
  ]
}
```

(The sample rows are shortened here; the real response carries every column.)

## Reading the result

- **180 + 20 = 200.** Every row is accounted for: none was dropped silently.
- **The 20 quarantined rows are the 20 that were made bad** — the rules caught each one.
- **The reasons add up to 27, not 20.** A row can break more than one rule (a row with no `status`
  fails both `status_required` and `status_accepted_values`), and each rule it breaks is counted.
- **`quarantined_sample`** holds up to `sample` of the quarantined rows, each with the rules it broke.
  Accepted rows are never returned.
- **`required: true` is a rule too.** The `*_required` reasons come from the fields, not the
  `quality` block.

Nothing was written to the contract's target. To keep the rows, run again with `write_outputs=true`:
they are saved under `runs/` in your project.
