#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def find_project_root(script_dir: Path) -> Path:
    for candidate in [script_dir, *script_dir.parents]:
        if (
            (candidate / "server_outputs").is_dir()
            and (candidate / "paper_submission").is_dir()
            and (candidate / "scripts").is_dir()
        ):
            return candidate
    for candidate in [script_dir, *script_dir.parents]:
        if (
            (candidate / "supplementary_data").is_dir()
            and (candidate / "latex").is_dir()
            and (candidate / "code").is_dir()
        ):
            return candidate
    return script_dir.parents[1]


ROOT = find_project_root(Path(__file__).resolve().parent)
DEFAULT_PACKAGE = (
    ROOT / "paper_submission" / "solar_energy_elsarticle_v5_soltrace_matrix"
    if (ROOT / "paper_submission").is_dir()
    else ROOT
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a checksum manifest for the Dunhuang benchmark package.")
    parser.add_argument(
        "--run",
        type=Path,
        default=ROOT / "server_outputs" / "streamed_fullfield_20260511_205252",
        help="Run directory to manifest.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output directory. Defaults to <run>/reproducibility_manifest.",
    )
    parser.add_argument(
        "--package",
        type=Path,
        default=DEFAULT_PACKAGE,
        help="Submission package directory to include in the manifest.",
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path, root: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def collect_files(run: Path, package: Path) -> list[Path]:
    include_dirs = [
        run / "layouts",
        run / "tables",
        run / "aiming_proxy",
        run / "aiming_sensitivity",
        run / "aiming_sensitivity_deep_20260512",
        run / "deformation_ablation" / "tables",
        run / "deformation_ablation" / "solarpilot_ablation_quick" / "tables",
        run / "weather_dni_sensitivity",
        run / "soltrace_allphase_27cond_20260512" / "publication_allphase",
        run / "soltrace_allphase_27cond_20260512" / "tables",
        run / "soltrace_v9_confirm_highsample_20260512" / "publication_v9_confirmation",
        run / "soltrace_v9_confirm_highsample_20260512" / "tables",
        run / "soltrace_v10_seed_replicate_20260513" / "publication_v10_seed_replicate",
        run / "soltrace_v10_seed_replicate_20260513" / "tables",
        run / "soltrace_v11_convergence_audit_20260514",
        package / "supplementary_data" / "soltrace_allphase_tables",
        package / "supplementary_data" / "soltrace_v9_confirmation_tables",
        package / "supplementary_data" / "soltrace_v10_seed_replicate_tables",
        package / "supplementary_data" / "soltrace_v11_convergence_tables",
        package / "supplementary_data" / "soltrace_v12_seed240k_tables",
        package / "supplementary_data" / "aiming_sensitivity_tables",
        package / "supplementary_data" / "baseline_strengthening_tables",
        package / "supplementary_data" / "same_anchor_strong_baseline_tables",
        package / "supplementary_data" / "strong_baseline_direct_promotion_queue",
        package / "supplementary_data" / "strong_baseline_direct_soltrace_tables",
        package / "supplementary_data" / "geometry_explainability_advantage",
        package / "supplementary_data" / "fast_annual_proxy_sanity",
        package / "supplementary_data" / "multiyear_annual_proxy_gate",
        package / "supplementary_data" / "flux_resolution_gate",
        package / "supplementary_data" / "baseline_direct_soltrace_tables",
        package / "supplementary_data" / "joint_layout_aiming_optimizer",
        package / "supplementary_data" / "joint_solarpilot_default_tables",
        package / "supplementary_data" / "joint_direct_soltrace_tables",
        package / "supplementary_data" / "joint_system_summary",
        package / "supplementary_data" / "missing20_geometry_sensitivity",
        package / "code",
        package / "latex" / "figures",
        package / "citations",
        package / "submission_materials",
        package / "reproducibility_config",
        package / "output",
    ]
    include_dirs.extend(path for path in run.glob("solarpilot_*") if path.is_dir())
    include_dirs.extend(path for path in run.glob("publication_summary*") if path.is_dir())
    include_dirs.extend(path for path in run.glob("publication_com_style*") if path.is_dir())
    include_files = [
        run / "FULLFIELD_REPORT.md",
        run / "run_config.json",
        run / "deformation_ablation" / "DEFORMATION_ABLATION_REPORT.md",
        ROOT / "configs" / "server_full.json",
        ROOT / "scripts" / "run_fullfield_deformation.py",
        ROOT / "scripts" / "run_aiming_proxy.py",
        ROOT / "scripts" / "run_aiming_sensitivity.py",
        ROOT / "scripts" / "run_solarpilot_validation.py",
        ROOT / "scripts" / "run_baseline_comparison.py",
        ROOT / "scripts" / "build_same_anchor_strong_baselines.py",
        ROOT / "scripts" / "build_strong_baseline_direct_queue.py",
        ROOT / "scripts" / "build_geometry_explainability_and_advantage.py",
        ROOT / "scripts" / "build_fast_annual_proxy_and_sanity.py",
        ROOT / "scripts" / "build_multi_year_annual_proxy_gate.py",
        ROOT / "scripts" / "build_flux_resolution_gate.py",
        ROOT / "scripts" / "build_baseline_direct_soltrace_report.py",
        ROOT / "scripts" / "build_baseline_direct_holdout_report.py",
        ROOT / "scripts" / "build_missing20_geometry_sensitivity.py",
        ROOT / "scripts" / "run_joint_layout_aiming_optimizer.py",
        ROOT / "scripts" / "build_joint_system_summary.py",
        ROOT / "scripts" / "build_joint_direct_soltrace_report.py",
        ROOT / "scripts" / "run_soltrace_condition_worker.py",
        ROOT / "scripts" / "run_soltrace_aimpoint_pilot.py",
        ROOT / "scripts" / "run_soltrace_sensitivity_matrix.py",
        ROOT / "scripts" / "run_deformation_ablation.py",
        ROOT / "scripts" / "build_weather_dni_sensitivity.py",
        ROOT / "scripts" / "build_sci2_com_style_figures.py",
        ROOT / "scripts" / "build_soltrace_publication_figures.py",
        ROOT / "scripts" / "build_allphase_soltrace_figures.py",
        ROOT / "scripts" / "build_graphical_abstract.py",
        ROOT / "scripts" / "build_v9_confirmation_report.py",
        ROOT / "scripts" / "build_v10_seed_replicate_report.py",
        ROOT / "scripts" / "build_v11_soltrace_convergence_audit.py",
        ROOT / "data" / "terrain" / "dunhuang_srtm90m_grid.csv",
        ROOT / "data" / "terrain" / "dunhuang_srtm90m_metadata.json",
        ROOT / "data" / "weather" / "dunhuang_nasa_power_2023_sam.csv",
        ROOT / "data" / "weather" / "dunhuang_nasa_power_2020_sam.csv",
        ROOT / "data" / "weather" / "dunhuang_nasa_power_2021_sam.csv",
        ROOT / "data" / "weather" / "dunhuang_nasa_power_2022_sam.csv",
        ROOT / "data" / "weather" / "dunhuang_nasa_power_2024_sam.csv",
        ROOT / "data" / "weather" / "dunhuang_nasa_power_2025_sam.csv",
        ROOT / "docs" / "STREAMED_FULLFIELD_HIGHRES_RUN_20260511.md",
        ROOT / "docs" / "V8_ALLPHASE_DIRECT_SOLTRACE_RUN_20260512.md",
        ROOT / "docs" / "V9_HIGHSAMPLE_CONFIRMATION_SOLTRACE_RUN_20260512.md",
        ROOT / "docs" / "V10_INDEPENDENT_SEED_SOLTRACE_RUN_20260513.md",
        ROOT / "docs" / "V11_SOLTRACE_CONVERGENCE_AUDIT_20260514.md",
        ROOT / "docs" / "V12_SEED240K_SOLTRACE_RUN_20260516.md",
        ROOT / "docs" / "REVIEWER_RISK_MATRIX_AND_RESPONSE_PLAN_20260511.md",
        package / "README.md",
        package / "JOURNAL_SELECTION_CAS2_AUDIT_20260512.md",
        package / "JOURNAL_TARGET_AND_TEMPLATE.md",
        package / "FIGURE_STYLE_GUIDE.md",
        package / "FIGURE_TABLE_FONT_REFERENCE_AUDIT_20260515.md",
        package / "SUBMISSION_STRATEGY_AND_REVIEWER_AUDIT_20260512.md",
        package / "NEXT_STRENGTHENING_PLAN_20260512.md",
        package / "VERSION_RESTORATION_AUDIT_20260514.md",
        package / "STRICT_REVIEW_RESPONSE_20260522.md",
        package / "latex" / "main.tex",
        package / "latex" / "main.pdf",
        package / "papers" / "paper_notes.jsonl",
    ]

    files: list[Path] = []
    for directory in include_dirs:
        if directory.is_dir():
            files.extend(path for path in directory.rglob("*") if path.is_file())
    files.extend(path for path in include_files if path.is_file())
    return sorted(set(files))


def write_markdown(payload: dict[str, object], out: Path) -> None:
    records = payload["files"]
    assert isinstance(records, list)
    lines = [
        "# Reproducibility Manifest",
        "",
        f"Generated at: `{payload['generated_at']}`",
        f"Run directory: `{payload['run_directory']}`",
        "",
        "This manifest is intended for reviewers. It records checksums for the layouts, terrain/weather inputs, SolarPILOT numerical-check tables, aiming-proxy tables, reduced SolTrace custom-aimpoint outputs, and manuscript-facing figures used in the current draft.",
        "",
        "| File | Bytes | SHA-256 |",
        "| --- | ---: | --- |",
    ]
    for record in records:
        assert isinstance(record, dict)
        lines.append(f"| `{record['path']}` | {record['bytes']} | `{record['sha256']}` |")
    (out / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    run = args.run if args.run.is_absolute() else ROOT / args.run
    package = args.package if args.package.is_absolute() else ROOT / args.package
    out = args.out or (run / "reproducibility_manifest")
    out = out if out.is_absolute() else ROOT / out
    out.mkdir(parents=True, exist_ok=True)

    files = collect_files(run, package)
    payload: dict[str, object] = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_directory": str(run),
        "submission_package": str(package),
        "project_root": str(ROOT),
        "file_count": len(files),
        "files": [file_record(path, ROOT) for path in files],
    }
    (out / "manifest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(payload, out)
    print(f"Wrote reproducibility manifest with {len(files)} files to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
