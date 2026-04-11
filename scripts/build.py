#!/usr/bin/env python3
"""Build otlg binary using PyInstaller.

Usage:
    uv run scripts/build.py
"""

import subprocess
import sys
from pathlib import Path


def main():
    scripts_dir = Path(__file__).parent
    project_dir = scripts_dir.parent
    spec_file = scripts_dir / "otlg.spec"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "--distpath", str(project_dir / "dist"),
        "--workpath", str(project_dir / "build"),
        str(spec_file),
    ]

    print(f"Building otlg binary...")
    print(f"Command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(project_dir))

    if result.returncode == 0:
        dist_dir = project_dir / "dist"
        binary_name = "otlg.exe" if sys.platform == "win32" else "otlg"
        binary = dist_dir / binary_name
        if binary.exists():
            size_mb = binary.stat().st_size / (1024 * 1024)
            print(f"\nBuild successful!")
            print(f"Binary: {binary} ({size_mb:.1f} MB)")
        else:
            print(f"\nBuild completed. Check {dist_dir}/ for output.")
    else:
        print(f"\nBuild failed with exit code {result.returncode}")
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
