#!/usr/bin/env bash
set -euo pipefail

if [ ! -f docker-compose.yml ]; then
  echo "docker-compose.yml not found. Aborting."
  exit 1
fi

# Detect compose command in a portable way
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "No docker compose command found. Aborting."
  exit 1
fi

"${COMPOSE_CMD[@]}" -f docker-compose.yml down --rmi all --volumes --remove-orphans || true

# Delete any container names explicitly set in the compose file (portable for macOS/BSD)
names=$(grep -E "^[[:space:]]*container_name:" docker-compose.yml | awk -F: '{gsub(/^[ \t]+|[ \t]+$/,"",$2); print $2}') || true
if [ -n "$names" ]; then
  while IFS= read -r name; do
    if [ -n "$name" ]; then
      docker rm -f "$name" >/dev/null 2>&1 || true
    fi
  done <<< "$names"
fi

echo "Done."
