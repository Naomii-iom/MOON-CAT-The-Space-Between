#!/bin/bash
set -euo pipefail
art_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
project_python="$art_dir/../.venv/bin/python"
if [[ ! -x "$project_python" ]]; then
    echo "未找到项目 Python：$project_python"
    echo "请把 mooncat_art_playtest 整个目录放在现有 mooncat 项目中。"
    exit 1
fi
cd "$art_dir"
exec "$project_python" main.py
