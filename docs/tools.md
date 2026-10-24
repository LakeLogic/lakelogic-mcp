# Tools

Seven tools. Five only **read** a contract and report; two **act locally** — one writes a test-data
file, one runs a contract on a local file. Clients may call the read-only tools without asking each
time (they are marked read-only to the client); the other two ask first in most clients.

Paths are files inside the project the server was started in. Every tool returns a JSON object.
An expected problem — a missing file, a path outside the project, a bad argument — comes back as
`{"error": "..."}`; a contract run that fails comes back as `{"ran": false, "error": "..."}`. Anything
unexpected is reported by your MCP client as a tool error.

The server also tells the assistant how to use them together: after writing or changing a contract,
**validate**, then **lint**, and fix what they report before showing it.

---

## `validate_contract`

**Does it match the OLC model?** Known keys, the right shapes, required fields.

| Input | Meaning |
|---|---|
| `path` | A contract file in the project |
| `contract_yaml` | Or the contract's text |

Returns `valid` and, if not, each error's location and problem.

## `lint_contract`

**Does it pass the lint checks?** Governance gaps such as a merge with no key, unordered deduplication,
untagged personal data, or a step no engine runs. Use after `validate_contract` passes.

| Input | Meaning |
|---|---|
| `path` | A contract file in the project |
| `contract_yaml` | Or the contract's text |

Returns `clean` and findings, each with its rule code, severity and fix.

## `explain_rule`

**Why does a lint rule exist?** What it checks, why it matters, a failing contract and the fixed one.

| Input | Meaning |
|---|---|
| `code` | A lint rule code, e.g. `KEY-002` |

## `contract_reference`

**How is one part of a contract written?** Returns the OLC reference page for that part.

| Input | Meaning |
|---|---|
| `topic` | One of: `anatomy` (every key), `execution-order`, `ingestion`, `lifecycle`, `quality`, `security`, `compliance`, `transformation`, `external-logic`, `materialization`, `server`, `lineage`, `data-products`, `slo`, `notifications`, `extraction`, `conformance`, `cli`, `schema` |

## `export_odcs`

**The contract as an [Open Data Contract Standard](https://bitol-io.github.io/open-data-contract-standard/) document.**

| Input | Meaning |
|---|---|
| `path` | A contract file in the project |

## `generate_test_data`

**Synthetic data shaped by the contract** — the right types, accepted values and ranges — with a share
of rows that deliberately break its quality rules, so a run shows quarantine working.
*Writes a file in the project.*

| Input | Default | Meaning |
|---|---|---|
| `path` | | The contract file |
| `rows` | `100` | How many rows |
| `invalid_ratio` | `0.1` | Share of rows to make break a rule (requested; the response reports `intended_invalid_rows`, and `run_contract` shows how many actually fail) |
| `seed` | random | For repeatable data |
| `output` | `test_data/<contract>.csv` | Where to write it |

## `run_contract`

**What happens when it runs?** Runs the contract on a local CSV or Parquet file with Polars or DuckDB:
how many rows pass, how many are quarantined, and each quarantine reason with its count.
*Nothing is written to the contract's target. Core does what the contract configures, including any notifications — see [Safety and privacy](safety.md).*

| Input | Default | Meaning |
|---|---|---|
| `path` | | The contract file |
| `source` | | The data file (CSV or Parquet) in the project |
| `engine` | `polars` | `polars` or `duckdb` |
| `sample` | `10` | Maximum number of **quarantined** rows to return (accepted rows are never returned) |
| `write_outputs` | `false` | Save the good and quarantined rows under `runs/` |

A typical sequence: `generate_test_data` → `run_contract` on the file it wrote. See the
[Walkthrough](walkthrough.md) for real output and how to read it.
