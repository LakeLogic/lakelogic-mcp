# Safety and privacy

An assistant with tools can do things. This page says what these tools do, and where the limits are.

## The server

- **Local.** It talks to your MCP client over stdio. The server itself opens no network connection,
  needs no account and sends no telemetry. (Installing it with `uvx` downloads the package and its
  dependencies, like any install.)
- **Tool paths stay in your project.** Every path given to a tool is resolved inside the folder the
  server was started in (or `--root`). A path that points outside it — including through `..` — is
  refused. The `_domain.yaml` / `_system.yaml` that `lint_contract` takes into account are searched
  for only inside the project too.

## When a contract runs

`run_contract` hands the contract to [LakeLogic Core](https://lakelogic.github.io/LakeLogic/), which
does what the contract configures. Two things follow:

- **A contract can configure network calls.** If it declares notifications (for example a Slack
  webhook) or run-log delivery to a service, Core may send them during the run. Run contracts you
  trust, or remove those blocks before a test run.
- **A contract can point at other files.** Files the contract itself names — a reference dataset under
  `links:`, for example — are read by Core and are not limited to the project folder.

Nothing is written to the contract's target table either way.

## Files the tools write

These are the files the tools themselves save, all inside the project:

| Tool | Writes | Where |
|---|---|---|
| `generate_test_data` | A synthetic data file | `test_data/` (or the `output` you give) |
| `run_contract` | No file of its own, unless `write_outputs` is set; then the good and quarantined rows | `runs/` |

This is separate from what Core does **because the contract asks for it** during `run_contract`
(notifications, run-log delivery — see [When a contract runs](#when-a-contract-runs)). `write_outputs`
does not turn those on or off; a contract's own settings do.

Both tools are marked to the client as **not read-only**, so most clients ask before running them. The
five other tools are marked **read-only**.

## What reaches your AI provider

Running locally does not keep results away from the assistant. Every tool result goes into the
assistant's context, and so to whichever model provider your client uses. That includes:

- `run_contract`'s **sample of quarantined rows** (`sample`, default 10);
- **failure reasons and error messages**, which can quote values from your data;
- **the contract itself** whenever a tool reads or reports on it — field names, descriptions, rules.

Setting `sample` to `0` removes the row sample only; the rest is still returned. If a data file holds
real personal or confidential data, test with [generated data](tools.md#generate_test_data) instead.
