#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Helper launcher for video-trimmer on Linux/macOS.
# - Creates/uses a virtual environment at <project>/.venv
# - Installs the project if needed
# - Runs the CLI as `python -m video_trimmer` with your arguments
#
# Usage options:
#   1) Keep this script inside the repo and run it directly
#   2) Put this script somewhere on your PATH and set VIDEO_TRIMMER_DIR to the project root
#      export VIDEO_TRIMMER_DIR=/absolute/path/to/video-trimmer
#   3) Or symlink this script from a directory on PATH into this repo's scripts folder

set -euo pipefail

# Resolve project directory
: "${VIDEO_TRIMMER_DIR:=}"
if [[ -n "${VIDEO_TRIMMER_DIR}" && -f "${VIDEO_TRIMMER_DIR}/pyproject.toml" ]]; then
  PROJECT_DIR="${VIDEO_TRIMMER_DIR}"
else
  SCRIPT_SOURCE="${BASH_SOURCE[0]:-$0}"
  SCRIPT_DIR="$(cd "$(dirname "${SCRIPT_SOURCE}")" && pwd)"
  if [[ -f "${SCRIPT_DIR}/../pyproject.toml" ]]; then
    PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
  elif [[ -f "${SCRIPT_DIR}/pyproject.toml" ]]; then
    PROJECT_DIR="${SCRIPT_DIR}"
  else
    echo "Error: Could not locate project root. Set VIDEO_TRIMMER_DIR to the repo root (with pyproject.toml)." >&2
    exit 1
  fi
fi

PYTHON_BIN="${PYTHON:-python3}"
if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Error: ${PYTHON_BIN} not found in PATH" >&2
  exit 1
fi

VENV_DIR="${PROJECT_DIR}/.venv"
VENV_BIN="${VENV_DIR}/bin"

if [[ ! -d "${VENV_DIR}" ]]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

"${VENV_BIN}/python" -m pip -q install --upgrade pip >/dev/null

# Install project if not importable
if ! "${VENV_BIN}/python" - <<'PY'
import sys
try:
    import video_trimmer  # noqa: F401
except Exception:
    sys.exit(1)
sys.exit(0)
PY
then
  "${VENV_BIN}/python" -m pip install -e "${PROJECT_DIR}"
fi

exec "${VENV_BIN}/python" -m video_trimmer "$@"


