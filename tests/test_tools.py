"""Each tool against real contracts, and the one boundary that matters: nothing outside the project."""

from pathlib import Path

import pytest

from lakelogic_mcp import tools

GOOD = """version: 1.0.0
info: { title: Trips, table_name: trips }
model:
  fields:
    - { name: trip_id, type: string, required: true }
    - { name: updated_at, type: timestamp }
primary_key: [trip_id]
transformations:
  - deduplicate: { on: [trip_id], sort_by: [updated_at], order: desc }
"""

# Valid OLC, but the dedup sorts by its own key: KEY-002 (only caught once `on:` is read as a
# field name, not the boolean YAML 1.1 makes of it).
SORTED_BY_KEY = GOOD.replace("sort_by: [updated_at]", "sort_by: [trip_id]")

INVALID = """version: 1.0.0
info: { title: Trips }
model:
  fields:
    - { name: trip_id, type: string }
materialization:
  primary_key: [trip_id]
"""


@pytest.fixture()
def project(tmp_path):
    tools.set_root(tmp_path)
    (tmp_path / "contracts").mkdir()
    (tmp_path / "contracts" / "good.yaml").write_text(GOOD, encoding="utf-8")
    (tmp_path / "contracts" / "sorted_by_key.yaml").write_text(SORTED_BY_KEY, encoding="utf-8")
    (tmp_path / "contracts" / "invalid.yaml").write_text(INVALID, encoding="utf-8")
    yield tmp_path


def test_validate_accepts_a_legal_contract(project):
    assert tools.validate_contract(path="contracts/good.yaml") == {
        "contract": str(Path("contracts/good.yaml")), "valid": True, "errors": []
    }


def test_validate_names_where_an_illegal_contract_is_wrong(project):
    result = tools.validate_contract(path="contracts/invalid.yaml")
    assert result["valid"] is False
    assert any("primary_key" in e["problem"] or "primary_key" in e["location"] for e in result["errors"])


def test_validate_takes_inline_text_too(project):
    assert tools.validate_contract(contract_yaml=GOOD)["valid"] is True


def test_lint_is_clean_for_a_good_contract_and_names_the_rule_otherwise(project):
    assert tools.lint_contract(path="contracts/good.yaml") == {
        "contract": str(Path("contracts/good.yaml")), "clean": True, "findings": []
    }
    result = tools.lint_contract(path="contracts/sorted_by_key.yaml")
    assert result["clean"] is False
    assert [f["rule"] for f in result["findings"]] == ["KEY-002"]
    assert result["findings"][0]["fix"]


def test_explain_rule_returns_the_catalogue_entry(project):
    entry = tools.explain_rule("key-002")
    assert entry["rule"] == "KEY-002" and entry["why"] and "sort_by" in entry["failing_example"]


def test_explain_rule_lists_the_rules_when_the_code_is_unknown(project):
    with pytest.raises(tools.ToolError, match="Known rules: .*KEY-002"):
        tools.explain_rule("NOPE-001")


def test_contract_reference_reads_the_bundled_page(project):
    page = tools.contract_reference("Quality")
    assert page["topic"] == "quality" and len(page["markdown"]) > 200


def test_export_odcs(project):
    out = tools.export_odcs("contracts/good.yaml")
    assert out["odcs"]


@pytest.mark.parametrize("path", ["../outside.yaml", "C:/Windows/win.ini", "/etc/passwd"])
def test_nothing_outside_the_project_can_be_read(project, path):
    (project.parent / "outside.yaml").write_text(GOOD, encoding="utf-8")
    with pytest.raises(tools.ToolError, match="outside the project folder|No contract file"):
        tools.validate_contract(path=path)


def test_exactly_one_input(project):
    with pytest.raises(tools.ToolError, match="exactly one"):
        tools.validate_contract()
    with pytest.raises(tools.ToolError, match="exactly one"):
        tools.validate_contract(path="contracts/good.yaml", contract_yaml=GOOD)


ORDERS = """version: 1.0.0
info: { title: Orders, table_name: orders }
model:
  fields:
    - { name: order_id, type: string, required: true }
    - { name: amount, type: double, min: 0 }
quality:
  row_rules:
    - { name: amount_positive, sql: "amount >= 0" }
"""


@pytest.mark.parametrize("engine", ["polars", "duckdb"])
def test_generate_then_run_quarantines_the_broken_rows(project, engine):
    (project / "orders.yaml").write_text(ORDERS, encoding="utf-8")
    made = tools.generate_test_data("orders.yaml", rows=40, invalid_ratio=0.25, seed=7)
    assert made["rows"] == 40 and (project / made["data_file"]).is_file()

    run = tools.run_contract("orders.yaml", made["data_file"], engine=engine, write_outputs=True)
    assert run["ran"] is True
    assert run["good_rows"] + run["quarantined_rows"] == 40
    assert run["quarantined_rows"] > 0 and run["quarantine_reasons"]
    assert (project / run["bad_file"]).is_file()


def test_run_refuses_platform_engines_and_outside_paths(project):
    (project / "orders.yaml").write_text(ORDERS, encoding="utf-8")
    (project / "d.csv").write_text("order_id,amount\na,1\n", encoding="utf-8")
    with pytest.raises(tools.ToolError, match="engine must be"):
        tools.run_contract("orders.yaml", "d.csv", engine="spark")
    with pytest.raises(tools.ToolError, match="outside the project folder"):
        tools.generate_test_data("orders.yaml", output="../escape.csv")
