#!/usr/bin/env python3
"""Create or verify the shared pinned Python runtime for asset extraction."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def runtime_python(root: Path) -> Path:
    return root / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def check(python: Path) -> bool:
    if not python.is_file():
        return False
    result = subprocess.run(
        [str(python), "-c", "import PIL, numpy, rembg; print(PIL.__version__, numpy.__version__, rembg.__version__)"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        print(f"versions:{result.stdout.strip()}")
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    default_cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    parser.add_argument("--runtime-root", type=Path, default=default_cache / "playdrop/make-2d-asset-pack/venv-v1")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.runtime_root.expanduser().resolve()
    python = runtime_python(root)
    if check(python):
        print(f"runtime_python:{python}")
        return
    if args.check:
        raise SystemExit(f"asset_pack_runtime_not_ready:{root}")
    root.parent.mkdir(parents=True, exist_ok=True)
    if not python.is_file():
        subprocess.run([sys.executable, "-m", "venv", str(root)], check=True)
    requirements = Path(__file__).resolve().parents[1] / "references" / "requirements-rembg.txt"
    subprocess.run(
        [str(python), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(requirements)],
        check=True,
    )
    if not check(python):
        raise SystemExit(f"asset_pack_runtime_install_failed:{root}")
    print(f"runtime_python:{python}")


if __name__ == "__main__":
    main()
