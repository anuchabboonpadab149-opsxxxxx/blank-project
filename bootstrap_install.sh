#!/usr/bin/env bash
# Bootstrap installer for autonomous posting system (Ubuntu/Debian)
# - Installs Docker & Compose
# - Builds and runs the stack
# - Zero-config: simulation enabled for all providers by default
set -euo pipefail

echo "[*] Detecting OS..."
if ! command -v apt-get >/dev/null 2>&1; then
  echo "This bootstrap targets Debian/Ubuntu (apt-based). Please install Docker manually on your distro."
  exit 1
fi

echo "[*] Installing Docker..."
sudo apt-get update -y
curl -fsSL https://get.docker.com | sudo sh

echo "[*] Verifying Docker and Compose plugin..."
docker --version
if ! docker compose version >/dev/null 2>&1; then
  # On some systems Compose plugin is not auto-installed; install via apt
  sudo apt-get install -y docker-compose-plugin || true
fi
docker compose version || true

echo "[*] Ensuring .env exists..."
if [ ! -f .env ]; then
  echo "No .env found. Creating .env with zero-config safe defaults..."
  cat > .env <<'EOF'
RUN_MODE=daemon
TIMEZONE=Asia/Bangkok

WEB_DASHBOARD=true
WEB_PORT=8000

POST_INTERVAL_SECONDS=1
COLLECT_INTERVAL_MINUTES=1

PROVIDERS=twitter,facebook,linkedin,line,telegram,discord,instagram,reddit,tiktok,mastodon
DISTRIBUTE_ALL=true

# Zero-config defaults (simulate providers, safe for first run)
SIMULATE_ALL_PROVIDERS=true
SIMULATE_ON_ERROR=true

CONTENT_MODE=generate
GENERATE_CONTENT=true
SENDER_NAME=จัสมินชอบกินแซลมอน
CANONICAL_LINE=บีรักจัสมินชอบกินแซลมอนนะ ขอบคุณที่เคยซัพพอตกันเสมออยู่ข้างๆตลอด💖💍
EOF
fi

echo "[*] Opening firewall for port 8000 (if ufw present)..."
if command -v ufw >/dev/null 2>&1; then
  sudo ufw allow 8000/tcp || true
fi

echo "[*] Building and starting services..."
docker compose up -d --build

echo "[*] Waiting for health..."
for i in $(seq 1 30); do
  sleep 1
  if curl -fsS http://127.0.0.1:8000/healthz >/dev/null 2>&1; then
    echo "OK"
    break
  fi
  echo -n "."
done
echo

echo "[*] Done."
echo "Open dashboard on:"
ip -o -4 addr show | awk '{print $4}' | cut -d/ -f1 | while read -r ip; do
  echo "  - http://${ip}:8000"
done
echo "Credentials UI (to add real keys later): /credentials"