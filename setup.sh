#!/usr/bin/env bash
# Expt 8: EC2 bootstrap — run once on a fresh Ubuntu 22.04 instance
set -euo pipefail

echo "==> Installing Docker"
sudo apt-get update -qq
sudo apt-get install -y ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -qq
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker ubuntu

echo "==> Setting env"
cat <<'EOF' | sudo tee /etc/environment
SECRET_KEY="replace-with-strong-secret"
EOF

echo "==> Done. Re-login and run: docker pull <image> && docker run ..."