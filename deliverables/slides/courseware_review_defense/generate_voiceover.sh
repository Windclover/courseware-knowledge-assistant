#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$ROOT_DIR/../../.." && pwd)"
OUTPUT_DIR="$PROJECT_ROOT/output/speech/courseware_review_defense"
SCRIPT_PATH="$ROOT_DIR/notes/courseware_review_defense_full_narration.txt"
TTS_CLI="$HOME/.codex/skills/speech/scripts/text_to_speech.py"

mkdir -p "$OUTPUT_DIR"

if [[ -f "$PROJECT_ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$PROJECT_ROOT/.env"
  set +a
fi

conda run -n assistant python "$TTS_CLI" speak \
  --input-file "$SCRIPT_PATH" \
  --voice cedar \
  --response-format wav \
  --speed 0.96 \
  --out "$OUTPUT_DIR/courseware_review_defense_full.wav" \
  --force

echo "[done] voiceover written to $OUTPUT_DIR/courseware_review_defense_full.wav"
