<img src="assets/lakelogic_mcp_banner_dark.png#only-dark" width="100%" alt="LakeLogic MCP: check and test data contracts with your AI assistant. A local MCP server for validating, linting and test-running OLC contracts."><img src="assets/lakelogic_mcp_banner_light.png#only-light" width="100%" alt="LakeLogic MCP: check and test data contracts with your AI assistant. A local MCP server for validating, linting and test-running OLC contracts.">

# LakeLogic MCP

**Help AI assistants check and test data contracts locally.**

Validate [Open Lakehouse Contracts (OLC)](https://lakelogic.github.io/open-lakehouse-contract/), find
governance gaps, explain rules and generate sample data. Test-run contracts with
[LakeLogic Core](https://lakelogic.github.io/LakeLogic/) using Polars or DuckDB, then inspect accepted
rows, failed rows and the reasons they failed.

Works with MCP-compatible assistants — Claude Code, Claude Desktop, Cursor and others. No LakeLogic
account required.

> **OLC defines the contract. Core executes it. MCP gives your assistant access to those tools.**

## Example

> *"Check orders.yaml, explain any findings, generate sample data and test it locally."*

The assistant validates the contract, lints it, explains each finding, writes test data shaped by the
contract, runs it, and reports which rows passed and why the others failed — real results from
LakeLogic, not plausible-looking YAML.

## The tools

| Ask | Tool |
|---|---|
| Does it match the OLC model? | [`validate_contract`](tools.md#validate_contract) |
| Does it pass the lint checks? | [`lint_contract`](tools.md#lint_contract) |
| Why is this rule flagged? | [`explain_rule`](tools.md#explain_rule) |
| How is this part of a contract written? | [`contract_reference`](tools.md#contract_reference) |
| Give me the ODCS version | [`export_odcs`](tools.md#export_odcs) |
| Make me test data for it | [`generate_test_data`](tools.md#generate_test_data) |
| What happens when it runs? | [`run_contract`](tools.md#run_contract) |

## Quick start

```bash
claude mcp add lakelogic -- uvx lakelogic-mcp
```

Start your assistant in the project that holds your contracts, then try the [Walkthrough](walkthrough.md). Other clients: see [Install](install.md).
Before running contracts on real data, read [Safety and privacy](safety.md).
