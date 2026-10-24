<picture>
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/LakeLogic/lakelogic-mcp/main/docs/assets/lakelogic_mcp_banner_light.png">
  <img src="https://raw.githubusercontent.com/LakeLogic/lakelogic-mcp/main/docs/assets/lakelogic_mcp_banner_dark.png" width="100%" alt="LakeLogic MCP: check and test data contracts with your AI assistant. A local MCP server for validating, linting and test-running OLC contracts. Your AI assistant talks to the LakeLogic MCP local server, which uses LakeLogic Core with Polars or DuckDB for contract checks (validate, lint, explain) and test runs (sample data, results, failure reasons). No LakeLogic account required.">
</picture>

# LakeLogic MCP

<!-- Ownership check for the official MCP Registry (registry.modelcontextprotocol.io). -->
mcp-name: io.github.LakeLogic/lakelogic-mcp

**Help AI assistants check and test data contracts locally.**

Validate [Open Lakehouse Contracts (OLC)](https://lakelogic.github.io/open-lakehouse-contract/), find
governance gaps, explain rules and generate sample data. Test-run contracts with
[LakeLogic Core](https://lakelogic.github.io/LakeLogic/) using Polars or DuckDB, then inspect accepted
rows, failed rows and the reasons they failed.

Works with MCP-compatible assistants — Claude Code, Claude Desktop, Cursor and others. No LakeLogic
account required.

**OLC defines the contract. Core executes it. MCP gives your assistant access to those tools.**

📖 **Documentation:** <https://lakelogic.github.io/lakelogic-mcp/>

## Example

> *"Check orders.yaml, explain any findings, generate sample data and test it locally."*

The assistant validates the contract, lints it, explains each finding, writes test data shaped by the
contract, runs it, and reports which rows passed and why the others failed — real results from
LakeLogic, not plausible-looking YAML.

## Tools

| Tool | Answers |
|---|---|
| `validate_contract` | Does it match the OLC model? Each error's location and problem |
| `lint_contract` | Does it pass the lint checks? Governance findings, each with its fix |
| `explain_rule` | Why does a lint rule exist? What it checks, why it matters, a failing and a fixed contract |
| `contract_reference` | How is one part of a contract written? (`anatomy`, `quality`, `materialization`, …) |
| `export_odcs` | The contract as an Open Data Contract Standard document |
| `generate_test_data` | Synthetic data shaped by the contract, with a share of rows that deliberately break its rules |
| `run_contract` | How many rows pass, how many fail, and why (Polars or DuckDB, on a local file) |

Details and inputs: [Tools](https://lakelogic.github.io/lakelogic-mcp/tools.html). A first run, start to finish:
[Walkthrough](https://lakelogic.github.io/lakelogic-mcp/walkthrough.html).

## Install

All clients need [`uv`](https://docs.astral.sh/uv/) on your PATH. Start your assistant in the project
that holds your contracts (or pass `--root <folder>`).

**Claude Code** — as a plugin:

```text
/plugin marketplace add LakeLogic/lakelogic-mcp
/plugin install lakelogic-mcp@lakelogic-mcp
```

or directly: `claude mcp add lakelogic -- uvx lakelogic-mcp`

**Cursor:** [Add to Cursor](cursor://anysphere.cursor-deeplink/mcp/install?name=lakelogic&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJsYWtlbG9naWMtbWNwIl19)

**Claude Desktop, VS Code and other MCP clients** — add to the client's MCP settings:

```json
{
  "mcpServers": {
    "lakelogic": {
      "command": "uvx",
      "args": ["lakelogic-mcp", "--root", "/path/to/your/contracts/project"]
    }
  }
}
```

It is listed in the official [MCP Registry](https://registry.modelcontextprotocol.io) as
`io.github.LakeLogic/lakelogic-mcp`.

## Safety and privacy

- **Local.** The server talks to your client over stdio; it opens no network connection itself, needs
  no account and sends no telemetry. (Installing with `uvx` downloads the package, as any install does.)
- **Tool paths stay in your project.** Every path you give a tool, and the `_domain.yaml` /
  `_system.yaml` that lint takes into account, must be inside the project folder. Files a contract
  itself names (a `links:` dataset, for example) are read by Core as written.
- **Running a contract does what the contract configures.** If a contract declares notifications or
  run-log delivery, LakeLogic Core may send them during `run_contract`. Nothing is written to the
  contract's target.
- **Results reach your AI provider.** Tool results go into the assistant's context: quarantined sample
  rows, failure reasons (which can quote your data) and the contract itself. `sample: 0` removes only
  the rows, so test with generated data if a file holds personal or confidential data.

More: [Safety and privacy](https://lakelogic.github.io/lakelogic-mcp/safety.html).

## Contributing

To work on the server from a checkout, see
[Development](https://lakelogic.github.io/lakelogic-mcp/development.html).
