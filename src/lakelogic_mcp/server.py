"""The MCP server: the tools over stdio. Local only: no network, no account, no telemetry.

    lakelogic-mcp                 # serve the current folder
    lakelogic-mcp --root <folder> # serve another folder
"""

from __future__ import annotations

import argparse
from typing import Any, Dict, Optional

try:  # MCP SDK 2.x
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # MCP SDK 1.x
    from mcp.server.fastmcp import FastMCP as _Server
from mcp.types import ToolAnnotations

from lakelogic_mcp import tools

#: Writes files inside the project and runs code on them; never touches a platform.
_LOCAL_WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False)

#: These tools only read and checks: clients may call them without asking each time.
_READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)

mcp = _Server(
    "lakelogic",
    instructions=(
        "Tools for Open Lakehouse Contracts (OLC). After writing or changing a contract, call "
        "validate_contract (is it legal OLC?) and then lint_contract (is it a good one?), and fix what "
        "they report before showing it. Use explain_rule to learn why a lint rule exists, and "
        "contract_reference to read how a part of the contract is written. To show a contract working, "
        "call generate_test_data and then run_contract on the file it wrote."
    ),
)


def _call(fn, *args, **kwargs) -> Dict[str, Any]:
    try:
        return fn(*args, **kwargs)
    except tools.ToolError as exc:
        return {"error": str(exc)}


@mcp.tool(annotations=_READ_ONLY)
def validate_contract(path: Optional[str] = None, contract_yaml: Optional[str] = None) -> Dict[str, Any]:
    """Check whether a contract is LEGAL Open Lakehouse Contract (OLC): known keys, right shapes, required
    fields. Use it after writing or editing a contract. Give `path` (a file in this project) or
    `contract_yaml` (the text). Returns `valid` and, if not, each error's location and problem."""
    return _call(tools.validate_contract, path=path, contract_yaml=contract_yaml)


@mcp.tool(annotations=_READ_ONLY)
def lint_contract(path: Optional[str] = None, contract_yaml: Optional[str] = None) -> Dict[str, Any]:
    """Check whether a contract is a GOOD one: governance gaps such as a merge with no key, unordered
    deduplication, untagged personal data, a step no engine runs. Use it after validate_contract passes.
    Returns `clean` and findings, each with its rule code, severity and fix."""
    return _call(tools.lint_contract, path=path, contract_yaml=contract_yaml)


@mcp.tool(annotations=_READ_ONLY)
def explain_rule(code: str) -> Dict[str, Any]:
    """Explain one lint rule (e.g. KEY-002): what it checks, why it matters, a failing contract and the
    fixed contract. Use it when a lint finding is unclear."""
    return _call(tools.explain_rule, code)


@mcp.tool(annotations=_READ_ONLY)
def contract_reference(topic: str) -> Dict[str, Any]:
    """Read the OLC reference for one part of a contract. Topics include anatomy (every key),
    quality, transformation, materialization, ingestion, security, slo, execution-order."""
    return _call(tools.contract_reference, topic)


@mcp.tool(annotations=_READ_ONLY)
def export_odcs(path: str) -> Dict[str, Any]:
    """Convert a contract file in this project to an Open Data Contract Standard (ODCS) document."""
    return _call(tools.export_odcs, path)


@mcp.tool(annotations=_LOCAL_WRITE)
def generate_test_data(
    path: str, rows: int = 100, invalid_ratio: float = 0.1, seed: Optional[int] = None, output: Optional[str] = None
) -> Dict[str, Any]:
    """Write synthetic test data for a contract (default test_data/<contract>.csv): right types,
    accepted values and ranges, with `invalid_ratio` of rows deliberately breaking the quality rules
    so a run shows quarantine working. Follow with run_contract."""
    return _call(tools.generate_test_data, path, rows=rows, invalid_ratio=invalid_ratio, seed=seed, output=output)


@mcp.tool(annotations=_LOCAL_WRITE)
def run_contract(
    path: str, source: str, engine: str = "polars", sample: int = 10, write_outputs: bool = False
) -> Dict[str, Any]:
    """Run a contract on a local data file (CSV/Parquet) with Polars or DuckDB: good rows,
    quarantined rows, and each quarantine reason with its count. Writes nothing to the contract's
    target. `write_outputs` saves good/bad rows under runs/."""
    return _call(tools.run_contract, path, source, engine=engine, sample=sample, write_outputs=write_outputs)


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(prog="lakelogic-mcp")
    parser.add_argument("--root", help="the project folder tools may read (default: the current folder)")
    args = parser.parse_args(argv)
    if args.root:
        tools.set_root(args.root)
    mcp.run()  # stdio


if __name__ == "__main__":
    main()
