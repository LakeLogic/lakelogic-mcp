"""End to end: start the real server as a subprocess and talk to it over MCP (stdio), as a client
such as Claude Code does."""

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

EXPECTED_TOOLS = {
    "validate_contract", "lint_contract", "explain_rule", "contract_reference", "export_odcs",
    "generate_test_data", "run_contract",
}

CONTRACT = """version: 1.0.0
info: { title: Trips, table_name: trips }
model:
  fields:
    - { name: trip_id, type: string }
primary_key: [trip_id]
materialization: { strategy: scd2, format: delta }
"""


async def _session_run(root: Path):
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "lakelogic_mcp.server", "--root", str(root)]
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listed = await session.list_tools()
            lint = await session.call_tool("lint_contract", {"path": "trips.yaml"})
            outside = await session.call_tool("validate_contract", {"path": "../elsewhere.yaml"})
            return listed, lint, outside


def _payload(result):
    return json.loads(result.content[0].text)


def test_the_server_lists_its_tools_and_answers_over_mcp(tmp_path):
    (tmp_path / "trips.yaml").write_text(CONTRACT, encoding="utf-8")
    listed, lint, outside = asyncio.run(_session_run(tmp_path))

    tools = {t.name: t for t in listed.tools}
    assert set(tools) == EXPECTED_TOOLS
    assert all(t.description for t in tools.values())

    found = _payload(lint)
    assert found["clean"] is False and [f["rule"] for f in found["findings"]] == ["SCD-001"]

    assert "outside the project folder" in _payload(outside)["error"]
