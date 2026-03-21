from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    scripts_dir = Path(__file__).resolve().parent
    script_names = [
        "generate_aziatskie_tigry.py",
        "generate_globalizatsiya.py",
        "generate_neft_v_mirovoy_ekonomike.py",
        "generate_neftedollar.py",
        "generate_panamskiy_kanal.py",
        "generate_plan_marshalla.py",
    ]
    for name in script_names:
        subprocess.check_call([sys.executable, str(scripts_dir / name)])


if __name__ == "__main__":
    main()
