#!/usr/bin/env bash
set -euo pipefail

# Defaults
TARGET_DIR=${1:-/opt/promote-ayutthaya}
SERVICE_NAME=promote-ayutthaya.service
SERVICE_PATH=/etc/systemd/system/${SERVICE_NAME}
PYTHON=${PYTHON:-/usr/bin/python3}
USER=${USER_NAME:-ubuntu}

echo "Installing to ${TARGET_DIR} as user '${USER}'"

# Create target directory and copy files
sudo mkdir -p "${TARGET_DIR}"
sudo rsync -a --delete ./ "${TARGET_DIR}/"

# Write service file with predetermined settings
cat <<EOF | sudo tee "${SERVICE_PATH}" >/dev/null
[Unit]
Description=Social distribution daemon (24/7) for multi-platform posting and analytics
After=network.target

[Service]
Type=simple
WorkingDirectory=${TARGET_DIR}
Environment=PYTHONUNBUFFERED=1
Environment=RUN_MODE=daemon
Environment=TIMEZONE=Asia/Bangkok
# AI content generation with Jasmine x Salmon persona and canonical line
Environment=GENERATE_CONTENT=true
Environment=SENDER_NAME=จัสมินชอบกินแซลมอน
Environment=CANONICAL_LINE=บีรักจัสมินชอบกินแซลมอนนะ ขอบคุณที่เคยซัพพอตกันเสมออยู่ข้างๆตลอด💖💍
# Real API mode (no simulation)
Environment=ENABLE_ADS=true
Environment=ADS_SIMULATION=false
Environment=SIMULATE_ALL_PROVIDERS=false
Environment=SIMULATE_ON_ERROR=false
# High-frequency autonomous operation
Environment=POST_INTERVAL_SECONDS=1
Environment=COLLECT_INTERVAL_MINUTES=1
# Providers list (include Mastodon)
Environment=PROVIDERS=twitter,facebook,linkedin,line,telegram,discord,instagram,reddit,tiktok,mastodon
ExecStart=${PYTHON} ${TARGET_DIR}/cli.py
Restart=always
RestartSec=10
User=${USER}

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}"
sudo systemctl restart "${SERVICE_NAME}"

echo "Installed. Check status with: sudo systemctl status ${SERVICE_NAME}"
echo "Follow logs with: journalctl -u ${SERVICE_NAME} -f"