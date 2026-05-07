import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_NAME = "LumenConverter"
INTERNAL_BUILD_NAME = APP_NAME


def normalized_system():
    system = platform.system().lower()
    if system == "windows":
        return "Windows"
    if system == "linux":
        return "Linux"
    if system == "darwin":
        return "macOS"
    return platform.system()


def normalized_arch():
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        return "x64"
    if machine in {"aarch64", "arm64"}:
        return "arm64"
    return platform.machine()


def release_filename():
    system = normalized_system()
    arch = normalized_arch()
    suffix = ".exe" if system == "Windows" else ""
    return f"{APP_NAME}-{system}-{arch}{suffix}"


def remove_if_exists(path):
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def build_onefile():
    dist_dir = ROOT / "dist"
    build_dir = ROOT / "build"
    spec_file = ROOT / f"{APP_NAME}.spec"

    remove_if_exists(dist_dir)
    remove_if_exists(build_dir)
    remove_if_exists(spec_file)

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--onefile",
        "--name",
        INTERNAL_BUILD_NAME,
        "app_launcher.py",
    ]

    subprocess.run(command, check=True, cwd=ROOT)

    built_asset = ROOT / "dist" / (
        f"{INTERNAL_BUILD_NAME}.exe"
        if normalized_system() == "Windows"
        else INTERNAL_BUILD_NAME
    )
    renamed_asset = ROOT / "dist" / release_filename()
    built_asset.rename(renamed_asset)


def print_result():
    output = ROOT / "dist" / release_filename()
    print(f"Build final gerado em: {output}")


def main():
    build_onefile()
    print_result()


if __name__ == "__main__":
    main()
