"""
run_phase2.py
=============
Phase 2 runner: pytest + all 3 experiment harnesses.
Writes output to run_phase2_output.txt for review.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT  = ROOT / "run_phase2_output.txt"

lines = []


def run(cmd, cwd=None):
    print(f"\n>>> {' '.join(str(c) for c in cmd)}")
    lines.append(f"\n>>> {' '.join(str(c) for c in cmd)}\n")
    result = subprocess.run(
        cmd, cwd=cwd or ROOT,
        capture_output=True, text=True
    )
    output = result.stdout + result.stderr
    print(output)
    lines.append(output)
    return result.returncode


# 1. pytest
rc = run([sys.executable, "-m", "pytest",
          "semantic-mvp/tests/",
          "opa-set-baseline/tests/",
          "opa-derived-baseline/tests/",
          "-v", "--tb=short"])
lines.append(f"\n[pytest exit code: {rc}]\n")

# 2. latency benchmark (50 iterations)
rc2 = run([sys.executable, "experiments/latency.py", "--iterations", "50"])
lines.append(f"\n[latency exit code: {rc2}]\n")

# 3. explanation quality
rc3 = run([sys.executable, "experiments/explanation_quality.py"])
lines.append(f"\n[explanation_quality exit code: {rc3}]\n")

# 4. maintainability
rc4 = run([sys.executable, "experiments/maintainability.py"])
lines.append(f"\n[maintainability exit code: {rc4}]\n")

# Read and append CSV contents
for csv_name in ("latency.csv", "explanation_quality.csv", "maintainability.csv"):
    csv_path = ROOT / "results" / "raw" / csv_name
    if csv_path.exists():
        lines.append(f"\n===== {csv_name} =====\n")
        lines.append(csv_path.read_text(encoding="utf-8"))
    else:
        lines.append(f"\n[MISSING: {csv_name}]\n")

OUT.write_text("".join(lines), encoding="utf-8")
print(f"\n[Done] Full output written to: {OUT}")
