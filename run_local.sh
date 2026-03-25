#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
ENV_NAME="assistant"
BACKEND_HOST="127.0.0.1"
BACKEND_PORT="8000"
FRONTEND_PORT=""
NPM_CACHE_DIR="$FRONTEND_DIR/.npm-cache"
BACKEND_PID=""
FRONTEND_CANDIDATE_PORTS=(5173 5174 5175 5176 5177)

cleanup() {
  if [[ -n "${BACKEND_PID}" ]] && kill -0 "${BACKEND_PID}" >/dev/null 2>&1; then
    echo ""
    echo "[cleanup] 正在停止后端服务..."
    kill "${BACKEND_PID}" >/dev/null 2>&1 || true
    wait "${BACKEND_PID}" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

require_command() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "[error] 未找到命令：${cmd}"
    exit 1
  fi
}

print_hint() {
  echo ""
  echo "后端地址: http://${BACKEND_HOST}:${BACKEND_PORT}"
  echo "前端地址: http://${BACKEND_HOST}:${FRONTEND_PORT}"
  echo "健康检查: http://${BACKEND_HOST}:${BACKEND_PORT}/api/health"
  echo ""
}

pick_frontend_port() {
  local port
  for port in "${FRONTEND_CANDIDATE_PORTS[@]}"; do
    if ! lsof -iTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1; then
      FRONTEND_PORT="${port}"
      return
    fi
  done

  echo "[error] 5173-5177 端口都被占用了，请先释放一个前端端口。"
  exit 1
}

require_command conda
require_command npm
require_command lsof

pick_frontend_port

if ! conda env list | awk '{print $1}' | grep -Fxq "${ENV_NAME}"; then
  echo "[error] 未找到 conda 环境：${ENV_NAME}"
  echo "请先执行：conda create -n ${ENV_NAME} python=3.11"
  exit 1
fi

if [[ ! -f "$ROOT_DIR/.env" ]]; then
  cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
  echo "[info] 已自动创建 .env，请先补充 QWEN_API_KEY：$ROOT_DIR/.env"
fi

if ! grep -Eq '^QWEN_API_KEY=.+$' "$ROOT_DIR/.env"; then
  echo "[warn] .env 中还没有填写 QWEN_API_KEY，界面可以打开，但上传生成会失败。"
fi

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  echo "[info] 正在安装前端依赖..."
  (cd "$FRONTEND_DIR" && npm install --cache "$NPM_CACHE_DIR")
fi

echo "[info] 正在启动后端..."
cd "$ROOT_DIR"
conda run -n "$ENV_NAME" uvicorn backend.app.main:app --host "$BACKEND_HOST" --port "$BACKEND_PORT" --reload &
BACKEND_PID=$!

sleep 2
if ! kill -0 "${BACKEND_PID}" >/dev/null 2>&1; then
  echo "[error] 后端启动失败，请检查终端输出。"
  exit 1
fi

print_hint
echo "[info] 正在启动前端..."
cd "$FRONTEND_DIR"
npm run dev -- --host "$BACKEND_HOST" --port "$FRONTEND_PORT" --strictPort
