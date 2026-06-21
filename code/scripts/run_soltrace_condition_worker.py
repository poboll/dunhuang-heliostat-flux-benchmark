#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_csv(text: str, cast=str) -> list:
    values = []
    for part in text.split(","):
        part = part.strip()
        if part:
            values.append(cast(part))
    return values


def fmt_hour(hour: float) -> str:
    if abs(hour - round(hour)) < 1e-9:
        return str(int(round(hour)))
    return str(hour).replace(".", "p")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run selected reduced PySolTrace condition directories without aggregating the full matrix."
    )
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "server_full.json")
    parser.add_argument("--pysoltrace-dir", type=Path, required=True)
    parser.add_argument("--layout-ids", required=True)
    parser.add_argument("--days", required=True)
    parser.add_argument("--hours", default="10,12,14")
    parser.add_argument("--strategies", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-heliostats", type=int, default=6000)
    parser.add_argument("--rays", type=int, default=60000)
    parser.add_argument("--threads", type=int, default=16)
    parser.add_argument("--receiver-panels", type=int, default=18)
    parser.add_argument("--receiver-nx", type=int, default=20)
    parser.add_argument("--receiver-ny", type=int, default=60)
    parser.add_argument("--seed", type=int, default=2026052301)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    args = parse_args()
    run = resolve(args.run)
    config = resolve(args.config)
    out = resolve(args.out)
    out.mkdir(parents=True, exist_ok=True)
    days = parse_csv(args.days, int)
    hours = parse_csv(args.hours, float)

    for day in days:
        for hour in hours:
            tag = f"d{day}_h{fmt_hour(hour)}"
            condition_dir = out / tag
            summary_path = condition_dir / "tables" / "soltrace_aimpoint_summary.csv"
            if summary_path.exists() and not args.force:
                print(f"skip existing {tag}: {summary_path}", flush=True)
                continue
            condition_seed = args.seed + day * 100 + int(round(hour * 10))
            cmd = [
                sys.executable,
                str(ROOT / "scripts" / "run_soltrace_aimpoint_pilot.py"),
                "--run",
                str(run),
                "--config",
                str(config),
                "--pysoltrace-dir",
                str(args.pysoltrace_dir),
                "--layout-ids",
                args.layout_ids,
                "--out",
                str(condition_dir),
                "--max-heliostats",
                str(args.max_heliostats),
                "--rays",
                str(args.rays),
                "--threads",
                str(args.threads),
                "--receiver-panels",
                str(args.receiver_panels),
                "--receiver-nx",
                str(args.receiver_nx),
                "--receiver-ny",
                str(args.receiver_ny),
                "--sun-day",
                str(day),
                "--sun-hour",
                str(hour),
                "--seed",
                str(condition_seed),
                "--strategies",
                args.strategies,
            ]
            print("running", tag, "seed", condition_seed, flush=True)
            subprocess.run(cmd, cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
