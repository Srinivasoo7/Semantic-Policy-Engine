"""Entry point: python run_validation.py [--all | --scenario <name>]"""

import sys
from pathlib import Path

# Ensure the src package directory is on the path when the script is run
# directly (e.g. `python run_validation.py --all`) without an editable install.
_src = Path(__file__).resolve().parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from semantic_policy.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
