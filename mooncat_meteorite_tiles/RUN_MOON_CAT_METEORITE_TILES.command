#!/bin/bash
set -euo pipefail

meteorite_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
project_python="$meteorite_dir/../.venv/bin/python"

if [[ ! -x "$project_python" ]]; then
    echo "MOON CAT's Python environment was not found: $project_python"
    echo "Keep this folder inside the mooncat project directory."
    read -r -p "Press Enter to close..."
    exit 1
fi

cd "$meteorite_dir"
exec "$project_python" main.py
