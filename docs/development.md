# Development

Work on the server from a checkout, next to checkouts of
[open-lakehouse-contract](https://github.com/LakeLogic/open-lakehouse-contract) and
[LakeLogic](https://github.com/LakeLogic/LakeLogic).

```bash
cd lakelogic-mcp
uv venv .venv
uv pip install --python .venv/bin/python "mcp>=1.2" pytest -e ../open-lakehouse-contract -e ../lakelogic
uv pip install --python .venv/bin/python --no-deps -e .
.venv/bin/python -m pytest
```

On Windows use `.venv\Scripts\python.exe`.

## Use your checkout in Claude Code

From the project whose contracts you want checked:

```bash
claude mcp add lakelogic -- /path/to/lakelogic-mcp/.venv/bin/lakelogic-mcp
```

## The docs

This site is built with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) and
published to GitHub Pages on every push to `main`.

```bash
pip install -r docs-requirements.txt
mkdocs serve      # http://127.0.0.1:8012
```
