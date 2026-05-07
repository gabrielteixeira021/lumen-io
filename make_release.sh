#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="${1:-}"
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/.venv/bin/python}"

if [[ -z "$VERSION" ]]; then
  echo "Uso: ./make_release.sh v1.0.0"
  exit 1
fi

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Erro: Python do ambiente virtual nao encontrado em $PYTHON_BIN"
  echo "Defina manualmente, se necessario:"
  echo "PYTHON_BIN=/c/caminho/python.exe ./make_release.sh v1.0.0"
  exit 1
fi

if ! git -C "$ROOT_DIR" rev-parse --git-dir >/dev/null 2>&1; then
  echo "Erro: este script precisa ser executado dentro de um repositorio git."
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
    echo "Corrija com:"
    echo "git remote set-url origin $EXPECTED_SSH_URL"
  fi
  exit 1
fi

run_step() {
  echo
  echo "==> $1"
}

run_step "Gerando build onefile"
"$PYTHON_BIN" "$ROOT_DIR/release_build.py"

run_step "Normalizando nomes de assets"
"$PYTHON_BIN" "$ROOT_DIR/normalize_release_assets.py"

SYSTEM_NAME="$("$PYTHON_BIN" -c 'import platform; print(platform.system().lower())')"

if [[ "$SYSTEM_NAME" == "windows" ]]; then
  run_step "Tentando gerar instalador Windows"

  if command -v ISCC >/dev/null 2>&1; then
    ISCC "$ROOT_DIR/installer_windows.iss"
  else
    echo "ISCC nao encontrado no PATH. Pulando instalador Windows."
    echo "Instale o Inno Setup e exponha o comando ISCC para gerar o Setup automaticamente."
  fi
else
  run_step "Sistema atual nao e Windows"
  echo "Pulando geracao de instalador Windows nesta maquina."
fi

run_step "Publicando release no GitHub"
"$ROOT_DIR/publish_release.sh" "$VERSION"
