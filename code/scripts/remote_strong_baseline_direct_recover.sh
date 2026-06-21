#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE="${REMOTE:-kk@10.3.36.15}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/paper_server_ed25519}"
REMOTE_ROOT="${REMOTE_ROOT:-/home/kk/projects/paper/dunhuang-heliostat-rebuild-sci2}"
REMOTE_CONDA="${REMOTE_CONDA:-/home/kk/projects/3d/envs/miniforge3/bin/conda}"
REMOTE_ENV="${REMOTE_ENV:-uu}"
OUT_REL="server_outputs/strong_baseline_direct_promotion_queue_20260523/soltrace_core_27cond_20260524"
SSH_OPTS=(-i "$SSH_KEY" -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=90 -o ConnectionAttempts=1)

rsync -az -e "ssh ${SSH_OPTS[*]}" \
  "$ROOT/scripts/build_strong_baseline_direct_soltrace_report.py" \
  "$REMOTE:$REMOTE_ROOT/scripts/build_strong_baseline_direct_soltrace_report.py"

ssh "${SSH_OPTS[@]}" "$REMOTE" "cd '$REMOTE_ROOT' && \
  OUT='$OUT_REL' && \
  echo '[remote] host='\"\$(hostname)\"' cwd='\"\$(pwd)\" && \
  echo '[remote] completed='\"\$(find \"\$OUT\" -path '*/tables/soltrace_aimpoint_summary.csv' 2>/dev/null | wc -l)\"'/27' && \
  find \"\$OUT\" -path '*/tables/soltrace_aimpoint_summary.csv' 2>/dev/null | sort && \
  \"$REMOTE_CONDA\" run --no-capture-output -n '$REMOTE_ENV' python scripts/build_strong_baseline_direct_soltrace_report.py \
    --out \"\$OUT/analysis\" && \
  sed -n '1,120p' \"\$OUT/analysis/STRONG_BASELINE_DIRECT_SOLTRACE_AUDIT.md\" && \
  echo '[remote] tmux sessions' && tmux list-sessions 2>/dev/null | grep dhf_strong || true && \
  echo '[remote] resources' && free -h && uptime"
