#!/bin/bash

set -e

show_error() {
  echo
  echo "Cài đặt hoặc khởi động thất bại. Xem lỗi ở phía trên."
  read -r -p "Nhấn Enter để đóng..."
}
trap show_error ERR

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$APP_DIR/.venv"

cd "$APP_DIR"

echo "=========================================="
echo "  KOKORO VIETNAMESE TTS"
echo "=========================================="
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "Không tìm thấy Python 3. Hãy cài Python 3.11 từ https://www.python.org/downloads/"
  exit 1
fi

if ! python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'; then
  echo "Cần Python 3.10 trở lên; khuyên dùng Python 3.11."
  exit 1
fi

if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "[1/3] Đang tạo môi trường Python..."
  python3 -m venv "$VENV_DIR"
fi

if ! "$VENV_DIR/bin/python" -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'; then
  echo "Môi trường .venv đang dùng Python quá cũ. Hãy xóa .venv rồi chạy lại."
  exit 1
fi

if [ ! -f "$VENV_DIR/.kokoro-deps-v2" ] || ! "$VENV_DIR/bin/python" -c "import huggingface_hub, numpy, onnxruntime, soundfile, torch, vig2p" >/dev/null 2>&1; then
  echo "[2/3] Đang cài Kokoro Vietnamese..."
  echo "Lần đầu có thể mất vài phút. Vui lòng giữ cửa sổ này mở."
  "$VENV_DIR/bin/python" -m pip install --upgrade pip
  "$VENV_DIR/bin/python" -m pip install -r "$APP_DIR/requirements.txt"
  touch "$VENV_DIR/.kokoro-deps-v2"
else
  echo "[2/3] Kokoro Vietnamese đã được cài."
fi

echo "[3/3] Đang chạy server..."
echo
echo "Mở trình duyệt tại: http://127.0.0.1:8000"
echo "Nhấn Control+C để dừng server."
echo

if command -v open >/dev/null 2>&1; then
  (sleep 1; open "http://127.0.0.1:8000") &
fi

exec "$VENV_DIR/bin/python" "$APP_DIR/server.py"
