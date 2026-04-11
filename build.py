#!/usr/bin/env python3
"""Build otlg binary using PyInstaller."""

import subprocess
import sys
from pathlib import Path


def main():
    project_dir = Path(__file__).parent
    spec_file = project_dir / "otlg.spec"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file),
    ]

    print(f"Building otlg binary...")
    print(f"Command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(project_dir))

    if result.returncode == 0:
        dist_dir = project_dir / "dist"
        binary = dist_dir / "otlg"
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
