# LakeLogic for Claude Code

This plugin connects Claude Code to `lakelogic-mcp`, LakeLogic's open-source MCP server for Open
Lakehouse Contracts. With it, Claude checks the data contracts it writes using LakeLogic itself
instead of guessing.

Tools: validate a contract against the standard, lint it for governance gaps (each finding with
its fix), explain any lint rule, read the reference for any part of a contract, export to ODCS,
generate synthetic test data with deliberately invalid rows, and run a contract locally on Polars
or DuckDB to see what passes and what is quarantined, and why.

It runs on your machine over stdio, reads only the project folder it was started in, and needs no
LakeLogic account. It requires `uv` on your PATH.

Install:

```
/plugin marketplace add LakeLogic/lakelogic-mcp
/plugin install lakelogic-mcp@lakelogic-mcp
```

Docs: https://docs.lakelogic.io/ai_assistants_mcp/
