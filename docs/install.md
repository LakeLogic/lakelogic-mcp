# Install

Every client starts the server with [`uv`](https://docs.astral.sh/uv/), so `uv` must be on your
PATH. The server works on the folder it is started in: start your client from the project that holds
your contracts, or pass `--root`.

=== "Claude Code"

    As a plugin:

    ```
    /plugin marketplace add LakeLogic/lakelogic-mcp
    /plugin install lakelogic-mcp@lakelogic-mcp
    ```

    Or directly:

    ```bash
    claude mcp add lakelogic -- uvx lakelogic-mcp
    ```

=== "Cursor"

    [Add to Cursor](cursor://anysphere.cursor-deeplink/mcp/install?name=lakelogic&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJsYWtlbG9naWMtbWNwIl19)

    Or add it to Cursor's `mcp.json` as below.

=== "Claude Desktop, VS Code and others"

    Add to the client's MCP settings (`claude_desktop_config.json`, `mcp.json`, …):

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

It is also listed in the official [MCP Registry](https://registry.modelcontextprotocol.io) as
`io.github.LakeLogic/lakelogic-mcp`.

## Options

| Option | Meaning |
|---|---|
| `--root <folder>` | The project folder the tools may read and write. Default: the folder the server starts in. |
| `LAKELOGIC_MCP_ROOT` | The same, as an environment variable. |

## Check it works

Ask your assistant: *"List the LakeLogic tools you have."* It should name the seven tools on the
[Tools](tools.md) page. Then: *"Validate the contracts in this folder."*
