#!/usr/bin/env bash
set -e
cd "$(dirname "${BASH_SOURCE[0]}")"

python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-19}"
exec python3 -m uvicorn main:app --host "${BIND_HOST:-0.0.0.0}" --port "${PORT:-8000}" "$@"
