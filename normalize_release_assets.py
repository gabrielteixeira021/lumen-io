import platform
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DIST_DIR = ROOT / "dist"
APP_NAME = "LumenConverter"


def normalized_arch():
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        return "x64"
    if machine in {"aarch64", "arm64"}:
        return "arm64"
    return platform.machine()


def rename_first_match(patterns, target_name):
    for pattern in patterns:
        matches = sorted(DIST_DIR.glob(pattern))
        for match in matches:
            if match.name == target_name:
                return match
            target = DIST_DIR / target_name
            if target.exists():
                target.unlink()
            match.rename(target)
            return target
    return None


def main():
    arch = normalized_arch()

    renamed = []

    appimage_target = f"{APP_NAME}-Linux-{arch}.AppImage"
    appimage = rename_first_match(
        ["*.AppImage"],
        appimage_target,
    )
    if appimage is not None:
        renamed.append(appimage.name)

    if renamed:
        print("Assets normalizados:")
        for item in renamed:
            print(f"- {item}")
    else:
        print("Nenhum asset para normalizar foi encontrado em dist/.")


if __name__ == "__main__":
    main()
