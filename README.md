# lakelogic-mcp

A **local** MCP server that lets AI assistants (Claude Code, Claude Desktop, Cursor and any MCP client)
check the Open Lakehouse Contracts (OLC) they write, using LakeLogic itself instead of guessing.

- Runs on your machine over stdio. **No network, no account, no telemetry.**
- **Never touches a platform.** Two tools act locally: `generate_test_data` writes a data file and
  `run_contract` runs a contract on it with Polars or DuckDB. Nothing is written to a contract's target.
- Reads and writes only inside the project folder it was started in.

## Tools

| Tool | Answers |
|---|---|
| `validate_contract` | Is this a legal OLC contract? Each error's location and problem |
| `lint_contract` | Is it a good one? Governance findings from `lakelogic lint`, each with its fix |
| `explain_rule` | Why does a lint rule exist? What it checks, why it matters, a failing and a fixed contract |
| `contract_reference` | How is one part of a contract written? (`anatomy`, `quality`, `materialization`, …) |
| `export_odcs` | The contract as an Open Data Contract Standard document |
| `generate_test_data` | Synthetic data shaped by the contract, with a share of rows that deliberately break its rules |
| `run_contract` | How many rows pass, how many are quarantined, and why (Polars or DuckDB, local only) |

## Install

```bash
claude mcp add lakelogic -- uvx lakelogic-mcp
```

## Try it locally (development checkout)

```bash
cd C:\_Personal\_SaaS\lakelogic-mcp
uv venv .venv
uv pip install --python .venv\Scripts\python.exe "mcp>=1.2" pytest -e ..\open-lakehouse-contract -e ..\lakelogic
uv pip install --python .venv\Scripts\python.exe --no-deps -e .
.venv\Scripts\python.exe -m pytest
```

### Register it with Claude Code

From the project whose contracts you want checked:

```bash
claude mcp add lakelogic -- C:\_Personal\_SaaS\lakelogic-mcp\.venv\Scripts\lakelogic-mcp.exe
```

Then ask, for example:

- "Lint the contracts in this folder and fix what you find."
- "Why is KEY-002 flagged on silver_trips.yaml?"
- "Write a silver contract for orders and check it before you show me."

### Claude Desktop / Cursor

Add to the client's MCP settings (`claude_desktop_config.json`, or Cursor's `mcp.json`):

```json
{
  "mcpServers": {
    "lakelogic": {
      "command": "C:\\_Personal\\_SaaS\\lakelogic-mcp\\.venv\\Scripts\\lakelogic-mcp.exe",
      "args": ["--root", "C:\\path\\to\\your\\contracts\\project"]
    }
  }
}
```

## Once published

```bash
uvx lakelogic-mcp            # Claude Code: claude mcp add lakelogic -- uvx lakelogic-mcp
```
