"""lint_contract reads domain/system settings only from inside the project (2026-10-24).

Core's own lint walks up to eight folders for `_domain.yaml` / `_system.yaml`, so linting a
contract read those files from above the project the server was opened on.
"""
from pathlib import Path

import pytest

from lakelogic_mcp import tools

CONTRACT = "version: 1.0.0\ndataset: orders\ninfo: {title: Orders, target_layer: silver}\n" \
           "model:\n  fields:\n    - {name: order_id, type: string}\n"


@pytest.fixture
def layout(tmp_path, monkeypatch):
    outer = tmp_path / "outer"
    project = outer / "project"
    (project / "sales").mkdir(parents=True)
    (outer / "_domain.yaml").write_text("domain: outside\n", encoding="utf-8")
    (project / "sales" / "orders.yaml").write_text(CONTRACT, encoding="utf-8")
    monkeypatch.setattr(tools, "ROOT", project.resolve())
    from lakelogic.core import contract_lint

    read = []
    real = contract_lint._load_yaml
    monkeypatch.setattr(contract_lint, "_load_yaml", lambda p: (read.append(Path(p).resolve()), real(p))[1])
    return outer, project, read


def test_files_above_the_project_are_not_read(layout):
    outer, _project, read = layout
    out = tools.lint_contract(path="sales/orders.yaml")
    assert "findings" in out
    assert (outer / "_domain.yaml").resolve() not in read


def test_domain_and_system_files_inside_the_project_are_used(layout):
    _outer, project, read = layout
    (project / "_domain.yaml").write_text("domain: sales\n", encoding="utf-8")
    (project / "sales" / "_system.yaml").write_text("system: shop\n", encoding="utf-8")
    tools.lint_contract(path="sales/orders.yaml")
    assert (project / "_domain.yaml").resolve() in read
    assert (project / "sales" / "_system.yaml").resolve() in read
