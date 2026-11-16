#!/usr/bin/env bash
set -e
cd "$(dirname "${BASH_SOURCE[0]}")"

npm ci --include=dev
npm run build
exec npm run preview -- --host "${BIND_HOST:-0.0.0.0}" --port "${PORT:-5173}" --strictPort "$@"
