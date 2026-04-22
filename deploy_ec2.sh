#!/bin/bash
# Deploy MedQA MLOps to AWS EC2

set -e

# Prompt for details if not provided via environment
EC2_IP=${EC2_IP:-""}
EC2_USER=${EC2_USER:-"ubuntu"}
KEY_PEM=${KEY_PEM:-""}

if [ -z "$EC2_IP" ] || [ -z "$KEY_PEM" ]; then
    echo "Usage: EC2_IP=<your_ec2_public_ip> KEY_PEM=<path_to_pem_file> ./deploy_ec2.sh"
    exit 1
fi

echo "🚀 Starting Deployment to $EC2_IP..."

# 1. SSH into the instance and set up the directory
ssh -i "$KEY_PEM" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_IP" << 'EOF'
    mkdir -p ~/mlops-healthcare
    # Ensure Docker is installed (for Ubuntu)
    if ! command -v docker &> /dev/null; then
        echo "Docker not found. Installing..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker ubuntu
        
        # Install docker compose
        sudo apt-get update
        sudo apt-get install docker-compose-plugin -y
    fi
EOF

# 2. Sync files to EC2 (Excluding venv, git, cache)
echo "📦 Transferring files to EC2..."
rsync -avz -e "ssh -i $KEY_PEM -o StrictHostKeyChecking=no" \
    --exclude '.venv' \
    --exclude '__pycache__' \
    --exclude '.git' \
    --exclude '.pytest_cache' \
    ./ "$EC2_USER@$EC2_IP:~/mlops-healthcare"

# 3. Build and run via Docker Compose
echo "🐳 Building and starting Docker containers..."
ssh -i "$KEY_PEM" "$EC2_USER@$EC2_IP" << 'EOF'
    cd ~/mlops-healthcare
    # Note: On some AWS AMIs, we might need newgrp or sudo for the first time
    sudo docker compose down || true
    sudo docker compose up --build -d
EOF

echo "✅ Deployment successful! UI is available at http://$EC2_IP:8501"
echo "✅ API Docs available at http://$EC2_IP:8000/docs"
