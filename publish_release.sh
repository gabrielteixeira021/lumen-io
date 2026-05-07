#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="$ROOT_DIR/dist"
DIST_INSTALLER_DIR="$ROOT_DIR/dist_installer"
RELEASE_NOTES_FILE="$ROOT_DIR/release_notes.generated.md"

VERSION="${1:-}"

if [[ -z "$VERSION" ]]; then
  echo "Uso: ./publish_release.sh v1.0.0"
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "Erro: GitHub CLI (gh) nao encontrado no PATH."
  echo "Instale e autentique com: gh auth login"
  exit 1
fi

if ! git -C "$ROOT_DIR" rev-parse --git-dir >/dev/null 2>&1; then
  echo "Erro: este script precisa ser executado dentro do repositorio git."
  exit 1
fi

ORIGIN_URL="$(git -C "$ROOT_DIR" remote get-url origin 2>/dev/null || true)"
if [[ -z "$ORIGIN_URL" ]]; then
  echo "Erro: remoto origin nao encontrado."
  exit 1
fi

EXPECTED_SSH_URL=""

if [[ "$ORIGIN_URL" =~ ^https://github\.com/([^/]+)/([^/]+)\.git$ ]]; then
  EXPECTED_SSH_URL="git@github.com:${BASH_REMATCH[1]}/${BASH_REMATCH[2]}.git"
elif [[ "$ORIGIN_URL" =~ ^git@github\.com:([^/]+)/([^/]+)\.git$ ]]; then
  EXPECTED_SSH_URL="$ORIGIN_URL"
fi

if [[ "$ORIGIN_URL" != git@github.com:* ]]; then
  echo "Erro: o remoto origin nao esta configurado para SSH."
  echo "Remote atual: $ORIGIN_URL"
  if [[ -n "$EXPECTED_SSH_URL" ]]; then
    echo "Ajuste com:"
    echo "git remote set-url origin $EXPECTED_SSH_URL"
  fi
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "Erro: voce nao esta autenticado no GitHub CLI."
  echo "Execute: gh auth login"
  exit 1
fi

assets=()
download_lines=()

add_asset() {
  local path="$1"
  local label="$2"

  if [[ -f "$path" ]]; then
    assets+=("$path")
    download_lines+=("- \`$(basename "$path")\`: $label")
  fi
}

find_first_match() {
  local search_dir="$1"
  shift

  if [[ ! -d "$search_dir" ]]; then
    return 1
  fi

  local pattern
  for pattern in "$@"; do
    while IFS= read -r match; do
      if [[ -n "$match" ]]; then
        echo "$match"
        return 0
      fi
    done < <(find "$search_dir" -maxdepth 1 -type f -name "$pattern" | sort)
  done

  return 1
}

WINDOWS_SETUP="$(find_first_match "$DIST_INSTALLER_DIR" "LumenConverter-Setup-Windows-x64.exe" "*.exe" || true)"
WINDOWS_PORTABLE="$(find_first_match "$DIST_DIR" "LumenConverter-Windows-x64.exe" "*.exe" || true)"
LINUX_APPIMAGE="$(find_first_match "$DIST_DIR" "LumenConverter-Linux-x64.AppImage" "*.AppImage" || true)"
LINUX_DEB="$(find_first_match "$DIST_DIR" "lumen-converter_*_amd64.deb" "*.deb" || true)"
LINUX_BINARY="$(find_first_match "$DIST_DIR" "LumenConverter-Linux-x64" "LumenConverter" || true)"

add_asset "${WINDOWS_SETUP:-}" "Instalador para Windows"
add_asset "${WINDOWS_PORTABLE:-}" "Executavel portatil para Windows"
add_asset "${LINUX_APPIMAGE:-}" "AppImage para Linux"
add_asset "${LINUX_DEB:-}" "Pacote .deb para Debian/Ubuntu"

if [[ ${#assets[@]} -eq 0 && -n "${LINUX_BINARY:-}" ]]; then
  add_asset "$LINUX_BINARY" "Executavel Linux onefile"
fi

if [[ ${#assets[@]} -eq 0 ]]; then
  echo "Erro: nenhum asset de release encontrado."
  echo "Arquivos esperados:"
  echo "- dist_installer/*.exe"
  echo "- dist/*.exe"
  echo "- dist/*.AppImage"
  echo "- dist/*.deb"
  echo "- dist/LumenConverter"
  exit 1
fi

{
  echo "# Lumen Converter $VERSION"
  echo
  echo "Release publicada automaticamente."
  echo
  echo "## Downloads"
  echo
  for line in "${download_lines[@]}"; do
    echo "$line"
  done
  echo
  echo "## Observacoes"
  echo
  echo "- Windows: prefira o arquivo com \`Setup\` no nome quando ele existir."
  echo "- Linux AppImage: talvez seja necessario rodar \`chmod +x nome-do-arquivo.AppImage\` antes de executar."
} >"$RELEASE_NOTES_FILE"

if git -C "$ROOT_DIR" rev-parse "$VERSION" >/dev/null 2>&1; then
  echo "Tag $VERSION ja existe localmente."
else
  git -C "$ROOT_DIR" tag "$VERSION"
fi

if git -C "$ROOT_DIR" ls-remote --tags origin "refs/tags/$VERSION" | grep -q "$VERSION"; then
  echo "Tag $VERSION ja existe no remoto."
else
  git -C "$ROOT_DIR" push origin "$VERSION"
fi

if gh release view "$VERSION" >/dev/null 2>&1; then
  echo "Release $VERSION ja existe. Fazendo upload dos assets."
  gh release upload "$VERSION" "${assets[@]}" --clobber
  gh release edit "$VERSION" --title "Lumen Converter $VERSION" --notes-file "$RELEASE_NOTES_FILE"
else
  gh release create "$VERSION" "${assets[@]}" \
    --title "Lumen Converter $VERSION" \
    --notes-file "$RELEASE_NOTES_FILE"
fi

echo
echo "Release publicada com sucesso:"
gh release view "$VERSION" --web
