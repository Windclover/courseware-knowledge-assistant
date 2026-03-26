#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$ROOT_DIR/tmp/demo_videos"
DEFAULT_URL="http://127.0.0.1:5173"

DURATION_SECONDS="${1:-90}"
OUTPUT_NAME="${2:-demo-$(date +%Y%m%d-%H%M%S).mov}"

if [[ "$OUTPUT_NAME" != *.mov ]]; then
  OUTPUT_NAME="${OUTPUT_NAME}.mov"
fi

TARGET_URL="${DEMO_URL:-$DEFAULT_URL}"
DISPLAY_ID="${DISPLAY_ID:-1}"
COUNTDOWN_SECONDS="${COUNTDOWN_SECONDS:-5}"
OPEN_BROWSER="${OPEN_BROWSER:-1}"

mkdir -p "$OUTPUT_DIR"
OUTPUT_PATH="$OUTPUT_DIR/$OUTPUT_NAME"

if ! command -v screencapture >/dev/null 2>&1; then
  echo "[error] 当前系统没有 screencapture，无法录屏。"
  exit 1
fi

echo "[info] 输出文件: $OUTPUT_PATH"
echo "[info] 录制时长: ${DURATION_SECONDS}s"
echo "[info] 录制屏幕: 主屏幕 ${DISPLAY_ID}"

if [[ "$OPEN_BROWSER" == "1" ]]; then
  echo "[info] 打开项目页面: $TARGET_URL"
  open "$TARGET_URL" || true
fi

echo "[info] ${COUNTDOWN_SECONDS} 秒后开始录制，请把浏览器和项目界面准备好。"
for ((i=COUNTDOWN_SECONDS; i>=1; i--)); do
  echo "  ${i}..."
  sleep 1
done

echo "[info] 开始录制。请现在演示项目功能。"
screencapture -D"$DISPLAY_ID" -v -k -V"$DURATION_SECONDS" "$OUTPUT_PATH"
echo "[done] 录制完成: $OUTPUT_PATH"
