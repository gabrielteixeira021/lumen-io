import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def remove_if_exists(path):
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def main():
    dist_dir = ROOT / "dist"
    build_dir = ROOT / "build"
    spec_file = ROOT / "lumen_gui.spec"

    remove_if_exists(dist_dir)
    remove_if_exists(build_dir)
    remove_if_exists(spec_file)

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--windowed",
        "--name",
        "LumenConverter",
        "--onedir",
        "app_launcher.py",
    ]

    subprocess.run(command, check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
