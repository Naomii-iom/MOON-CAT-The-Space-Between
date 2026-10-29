#!/bin/bash
set -euo pipefail

visual_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
project_python="$visual_dir/../.venv/bin/python"

if [[ ! -x "$project_python" ]]; then
    echo "找不到 MOON CAT 项目的 Python 环境：$project_python"
    echo "请确认本文件夹仍放在 mooncat 项目目录内。"
    read -r -p "按 Enter 关闭…"
    exit 1
fi

cd "$visual_dir"
exec "$project_python" main.py
