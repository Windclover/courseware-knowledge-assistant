#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -d "$ROOT_DIR/node_modules/pptxgenjs" ]]; then
  npm install --no-save pptxgenjs@4.0.1 setimmediate@1.0.5 lie@3.3.0 pako@1.0.11 readable-stream@2.3.8
fi

node "$ROOT_DIR/courseware_review_defense.js"
echo "[done] deck built: $ROOT_DIR/courseware_review_defense.pptx"
