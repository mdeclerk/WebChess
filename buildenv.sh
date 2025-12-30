#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="webchess-dev"

usage() {
  cat <<'USAGE'
Usage: ./buildenv.sh <command>

Commands:
  init       Build the Docker image
  start      Run Uvicorn in Docker (foreground)
  stop       Stop running containers based on the image
  test       Run pytest in Docker
  bash       Start an interactive shell in Docker
USAGE
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

case "$1" in
  init)
    if docker image inspect "${IMAGE_NAME}" >/dev/null 2>&1; then
      echo "Docker image ${IMAGE_NAME} already exists."
      exit 0
    fi
    docker build -t "${IMAGE_NAME}" .
    ;;
  start)
    docker run --rm -p 8000:8000 -v "${ROOT_DIR}:/app" -w /app "${IMAGE_NAME}" \
      uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ;;
  stop)
    docker ps -q --filter ancestor="${IMAGE_NAME}" | xargs -r docker stop
    ;;
  test)
    docker run --rm -v "${ROOT_DIR}:/app" -w /app "${IMAGE_NAME}" python -m pytest -q
    ;;
  bash)
    docker run --rm -it -v "${ROOT_DIR}:/app" -w /app "${IMAGE_NAME}" bash
    ;;
  *)
    usage
    exit 1
    ;;
esac
