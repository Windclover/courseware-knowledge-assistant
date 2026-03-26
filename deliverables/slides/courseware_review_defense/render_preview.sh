#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REVIEW_DIR="$ROOT_DIR/review"
PPTX_FILE="$ROOT_DIR/courseware_review_defense.pptx"

mkdir -p "$REVIEW_DIR"

if ! command -v qlmanage >/dev/null 2>&1; then
  echo "[error] qlmanage not found."
  exit 1
fi

qlmanage -t -s 1800 -o "$REVIEW_DIR" "$PPTX_FILE" >/dev/null 2>&1 || true
echo "[done] preview generated under: $REVIEW_DIR"
