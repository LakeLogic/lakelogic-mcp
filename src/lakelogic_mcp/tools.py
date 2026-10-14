"""The tools, as plain functions. Thin adapters over LakeLogic Core and OLC: any real logic
belongs in Core or OLC, never here.

Most tools READ and CHECK. Two act: `generate_test_data` writes a data file and `run_contract`
runs a contract on one, locally (Polars or DuckDB), so an assistant can show a contract working
before it goes near a platform. Paths are confined to the folder the server
was started in (``ROOT``), so an assistant cannot read files outside the project it was opened on.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

#: The only folder tools may read from. Set by the server at start (``--root``, default: cwd).
ROOT = Path(os.environ.get("LAKELOGIC_MCP_ROOT") or os.getcwd()).resolve()

REFERENCE_TOPICS = (
    "anatomy",
    "execution-order",
    "ingestion",
    "lifecycle",
    "quality",
    "security",
    "compliance",
    "transformation",
    "external-logic",
    "materialization",
    "server",
    "lineage",
    "data-products",
    "slo",
    "notifications",
    "extraction",
    "conformance",
    "cli",
    "schema",
)


class ToolError(ValueError):
    """A request the tool refuses, with a message the assistant can act on."""


def set_root(path: str | Path) -> Path:
    global ROOT
    ROOT = Path(path).resolve()
    return ROOT


def _resolve(path: str) -> Path:
    """``path`` inside ROOT, or a refusal. Relative paths are relative to ROOT."""
    candidate = Path(path)
    full = (candidate if candidate.is_absolute() else ROOT / candidate).resolve()
    if full != ROOT and ROOT not in full.parents:
        raise ToolError(
            f"'{path}' is outside the project folder this server was started in ({ROOT}). "
            "Only files inside it can be read."
        )
    if not full.is_file():
        raise ToolError(f"No contract file at '{path}' (looked in {full}).")
    return full


def _resolve_output(path: str) -> Path:
    """Where a tool may WRITE: inside ROOT, parent folders created."""
    candidate = Path(path)
    full = (candidate if candidate.is_absolute() else ROOT / candidate).resolve()
    if ROOT not in full.parents:
        raise ToolError(f"'{path}' is outside the project folder ({ROOT}). Files can only be written inside it.")
    full.parent.mkdir(parents=True, exist_ok=True)
    return full


def _resolve_data(path: str) -> Path:
    full = _resolve_output(path)
    if not full.is_file():
        raise ToolError(f"No data file at '{path}' (looked in {full}).")
    return full


def _parse(contract_yaml: str) -> Any:
    from olc.validate import load_contract_yaml

    try:
        doc = load_contract_yaml(contract_yaml)
    except Exception as exc:  # noqa: BLE001 - reported to the assistant as findings
        raise ToolError(f"Not valid YAML: {exc}") from None
    if not isinstance(doc, dict):
        raise ToolError("A contract is a YAML mapping (key: value pairs) at the top level.")
    return doc


def _contract_text(path: Optional[str], contract_yaml: Optional[str]) -> tuple[str, str]:
    if bool(path) == bool(contract_yaml):
        raise ToolError("Give exactly one of `path` (a contract file) or `contract_yaml` (the contract text).")
    if path:
        full = _resolve(path)
        return full.read_text(encoding="utf-8"), str(full.relative_to(ROOT))
    return contract_yaml or "", "inline contract"


# ── tools ────────────────────────────────────────────────────────────────────────────────────


def validate_contract(path: Optional[str] = None, contract_yaml: Optional[str] = None) -> Dict[str, Any]:
    """Is this a LEGAL OLC contract? Checks it against the strict OLC model."""
    from olc.models import load_strict

    text, source = _contract_text(path, contract_yaml)
    doc = _parse(text)
    try:
        load_strict(doc)
    except Exception as exc:  # noqa: BLE001 - pydantic's errors, flattened for the assistant
        errors = getattr(exc, "errors", None)
        found: List[Dict[str, str]] = []
        if callable(errors):
            for e in errors():
                found.append({"location": ".".join(str(p) for p in e.get("loc", ())) or "<root>", "problem": e.get("msg", "")})
        else:
            found.append({"location": "<root>", "problem": str(exc)})
        return {"contract": source, "valid": False, "errors": found}
    return {"contract": source, "valid": True, "errors": []}


def lint_contract(path: Optional[str] = None, contract_yaml: Optional[str] = None) -> Dict[str, Any]:
    """Is this a GOOD contract? Governance findings from `lakelogic lint`, each with its fix.

    With `path`, the contract's domain and system settings (`_domain.yaml` / `_system.yaml`
    above it) are taken into account, exactly as `lakelogic lint` does.
    """
    from lakelogic.core.contract_lint import review_contract, review_contract_dict

    if path:
        full = _resolve(path)
        findings = review_contract(full)
        source = str(full.relative_to(ROOT))
    else:
        text, source = _contract_text(None, contract_yaml)
        findings = review_contract_dict(_parse(text), "inline", None)
    rows = [
        {
            "rule": f.check_id,
            "severity": f.severity,
            "message": f.message,
            "field": f.field,
            "fix": f.suggestion,
        }
        for f in findings
    ]
    return {
        "contract": source,
        "clean": not any(r["severity"] in ("critical", "warning") for r in rows),
        "findings": rows,
    }


def explain_rule(code: str) -> Dict[str, Any]:
    """Why a lint rule exists: what it checks, why it matters, a failing and a fixed contract."""
    from lakelogic.core.contract_lint_catalogue import CATALOGUE

    entry = CATALOGUE.get(code.strip().upper())
    if entry is None:
        raise ToolError(f"No lint rule '{code}'. Known rules: {', '.join(sorted(CATALOGUE))}.")
    return {
        "rule": entry.code,
        "title": entry.title,
        "severity": entry.severity,
        "checks": entry.checks,
        "why": entry.why,
        "failing_example": entry.failing,
        "fixed_example": entry.fixed,
        "fixed_example_is_standard_olc": entry.olc_valid,
    }


def contract_reference(topic: str) -> Dict[str, Any]:
    """The OLC reference page for one part of a contract (e.g. `quality`, `materialization`)."""
    import olc

    key = topic.strip().lower().replace(" ", "-").replace("_", "-")
    if key not in REFERENCE_TOPICS:
        raise ToolError(f"No reference page '{topic}'. Topics: {', '.join(REFERENCE_TOPICS)}.")
    page = Path(olc.__file__).resolve().parent / "_bundled" / "docs" / "reference" / f"{key}.md"
    if not page.exists():
        raise ToolError(f"The installed OLC package has no '{key}' page.")
    return {"topic": key, "markdown": page.read_text(encoding="utf-8")}


def export_odcs(path: str) -> Dict[str, Any]:
    """The contract as an Open Data Contract Standard (ODCS) document."""
    from lakelogic.core.models import DataContract

    full = _resolve(path)
    try:
        document = DataContract.from_yaml(str(full)).to_odcs()
    except Exception as exc:  # noqa: BLE001
        raise ToolError(f"Could not export '{path}': {exc}") from None
    return {"contract": str(full.relative_to(ROOT)), "odcs": document}


RUN_ENGINES = ("polars", "duckdb")
ERROR_COLUMN = "_lakelogic_errors"


def generate_test_data(
    path: str, rows: int = 100, invalid_ratio: float = 0.1, seed: Optional[int] = None, output: Optional[str] = None
) -> Dict[str, Any]:
    """Synthetic data shaped by the contract: its types, nullability, accepted values and ranges.
    `invalid_ratio` of the rows deliberately break the quality rules, so a run shows quarantine working."""
    from lakelogic.core.generator import DataGenerator

    full = _resolve(path)
    if not 1 <= rows <= 100_000:
        raise ToolError("rows must be between 1 and 100000.")
    if not 0.0 <= invalid_ratio <= 1.0:
        raise ToolError("invalid_ratio must be between 0.0 and 1.0.")
    out = _resolve_output(output or f"test_data/{full.stem}.csv")
    if out.suffix.lower() not in (".csv", ".parquet"):
        raise ToolError("output must end in .csv or .parquet.")
    try:
        df = DataGenerator(full, seed=seed).generate(rows=rows, invalid_ratio=invalid_ratio, output_format="polars")
    except Exception as exc:  # noqa: BLE001
        raise ToolError(f"Could not generate data for '{path}': {exc}") from None
    df.write_csv(out) if out.suffix.lower() == ".csv" else df.write_parquet(out)
    return {
        "contract": str(full.relative_to(ROOT)),
        "data_file": str(out.relative_to(ROOT)),
        "rows": df.height,
        "columns": df.columns,
        "intended_invalid_rows": round(rows * invalid_ratio),
    }


def run_contract(
    path: str, source: str, engine: str = "polars", sample: int = 10, write_outputs: bool = False
) -> Dict[str, Any]:
    """Run the contract on a local data file: how many rows pass, how many are quarantined, and why.
    Nothing is materialized to the contract's target; `write_outputs` saves good/bad rows under runs/."""
    from lakelogic import DataProcessor

    full = _resolve(path)
    data = _resolve_data(source)
    if engine not in RUN_ENGINES:
        raise ToolError(f"engine must be one of {', '.join(RUN_ENGINES)} locally. Spark, Snowflake and BigQuery run on the platform.")
    try:
        result = DataProcessor(engine=engine, contract=str(full)).run_source(str(data))
    except Exception as exc:  # noqa: BLE001 - a failed run is the answer, not a server error
        return {"contract": str(full.relative_to(ROOT)), "ran": False, "error": f"{type(exc).__name__}: {exc}"}
    good, bad = _to_polars(result.good), _to_polars(result.bad)
    reasons: Dict[str, int] = {}
    if bad is not None and ERROR_COLUMN in bad.columns:
        for errs in bad[ERROR_COLUMN].to_list():
            for e in errs if isinstance(errs, list) else [errs]:
                if e:
                    reasons[str(e)] = reasons.get(str(e), 0) + 1
    out: Dict[str, Any] = {
        "contract": str(full.relative_to(ROOT)),
        "ran": True,
        "engine": engine,
        "good_rows": 0 if good is None else good.height,
        "quarantined_rows": 0 if bad is None else bad.height,
        "quarantine_reasons": dict(sorted(reasons.items(), key=lambda kv: -kv[1])),
        "quarantined_sample": [] if bad is None else bad.head(sample).to_dicts(),
    }
    if write_outputs:
        stem = full.stem
        for name, df in (("good", good), ("bad", bad)):
            if df is not None:
                target = _resolve_output(f"runs/{stem}_{name}.parquet")
                df.write_parquet(target)
                out[f"{name}_file"] = str(target.relative_to(ROOT))
    return out


def _to_polars(df: Any) -> Any:
    if df is None:
        return None
    import polars as pl

    if isinstance(df, pl.DataFrame):
        return df
    if hasattr(df, "pl"):  # DuckDB relation
        return df.pl()
    if hasattr(df, "to_pandas") or hasattr(df, "columns"):
        return pl.from_pandas(df) if not hasattr(df, "pl") else df.pl()
    raise ToolError(f"Unexpected result type {type(df).__name__}.")
