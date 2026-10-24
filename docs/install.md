# Install

You need:

- **[`uv`](https://docs.astral.sh/uv/)** on your PATH. Every client starts the server with `uvx`,
  which downloads and runs it — no separate install.
- **Python 3.10 or later** (uv can provide it).

The server works on **one project folder**: where your contracts are. Terminal clients start it in the
folder you run them from; desktop apps do not, so give them `--root`.

## Claude Code

As a plugin:

```text
/plugin marketplace add LakeLogic/lakelogic-mcp
/plugin install lakelogic-mcp@lakelogic-mcp
```

Or directly, from your project folder:

```bash
claude mcp add lakelogic -- uvx lakelogic-mcp
```

## Claude Desktop

Edit `claude_desktop_config.json` (Settings → Developer → Edit Config). It lives in
`%APPDATA%\Claude\` on Windows and `~/Library/Application Support/Claude/` on macOS.

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

Restart Claude Desktop after saving.

## Cursor

[Add to Cursor](cursor://anysphere.cursor-deeplink/mcp/install?name=lakelogic&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJsYWtlbG9naWMtbWNwIl19),
or edit `.cursor/mcp.json` in your project (or `~/.cursor/mcp.json` for every project):

```json
{
  "mcpServers": {
    "lakelogic": {
      "command": "uvx",
      "args": ["lakelogic-mcp"]
    }
  }
}
```

## VS Code

Edit `.vscode/mcp.json` in your project. VS Code's format differs: the top key is `servers` and each
server names its `type`.

```json
{
  "servers": {
    "lakelogic": {
      "type": "stdio",
      "command": "uvx",
      "args": ["lakelogic-mcp"]
    }
  }
}
```

## Other MCP clients

Run `uvx lakelogic-mcp` as a **stdio** server, with `--root <folder>` if the client does not start it
in your project. Check your client's documentation for where its MCP settings go.

The server is also listed in the official [MCP Registry](https://registry.modelcontextprotocol.io) as
`io.github.LakeLogic/lakelogic-mcp`.

## Options

| Option | Meaning |
|---|---|
| `--root <folder>` | The project folder the tools work in. Default: the folder the server starts in. |
| `LAKELOGIC_MCP_ROOT` | The same, as an environment variable. |

## Check it works

Ask your assistant *"List the LakeLogic tools you have."* It should name the seven tools on the
[Tools](tools.md) page. Then try the [Walkthrough](walkthrough.md).

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| The client says it cannot start the server, or `uvx` is not found | `uv` is not installed or not on the PATH the client sees. Install uv, then restart the client. On Windows a desktop app may need a sign-out to pick up a new PATH; or give the full path to `uvx` as the `command`. |
| A tool says a file is outside the project, or cannot find your contract | The server is working in a different folder. Set `--root` to the folder that holds your contracts (paths are relative to it). |
| The assistant does not list the LakeLogic tools | The server did not start, or the client was not restarted after the settings change. Restart the client and check its MCP log; in Claude Code, run `claude mcp list`. |
| The first start is slow | `uvx` downloads the package and its dependencies the first time. Later starts use the cache. |
