"""Entry point: python run_validation.py [--all | --scenario <name>]"""

import sys
from pathlib import Path

# Ensure src/ is on the import path when run directly (no editable install).
_src = Path(__file__).resolve().parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from opa_set_policy.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
