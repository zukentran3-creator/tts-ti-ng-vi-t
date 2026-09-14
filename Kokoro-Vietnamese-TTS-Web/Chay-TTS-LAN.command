#!/bin/bash

set -e
APP_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ ! -x "$APP_DIR/.venv/bin/python" ]; then
  echo "Hãy chạy Chay-TTS.command một lần để cài đặt trước."
  read -r -p "Nhấn Enter để đóng..."
  exit 1
fi

cd "$APP_DIR"
echo "Server đang mở cho các thiết bị trong cùng mạng Wi-Fi."
echo "Mở http://IP-CUA-MAY-TINH:8000 trên điện thoại."
echo "Nhấn Control+C để dừng."
echo
exec "$APP_DIR/.venv/bin/python" "$APP_DIR/server.py" --host 0.0.0.0
