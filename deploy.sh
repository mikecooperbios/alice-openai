#!/usr/bin/env bash
# Run this script on VPS 109.234.35.217 to deploy the ChatGPT Alice skill.
# Prerequisites:
#   - Docker and docker-compose installed
#   - .env file with OPENAI_API_KEY present in ~/chatgpt-alice/
#   - DNS A record gpt.d-scribe.ru -> 109.234.35.217 already propagated
#   - nginx-gpt.conf already placed and SSL obtained via certbot

set -euo pipefail

DEPLOY_DIR="$HOME/chatgpt-alice"
REPO_URL="https://github.com/mikecooperbios/alice-openai.git"
BRANCH="main"

echo "==> Setting up $DEPLOY_DIR"
if [ ! -d "$DEPLOY_DIR/.git" ]; then
    git clone --branch "$BRANCH" "$REPO_URL" "$DEPLOY_DIR"
else
    git -C "$DEPLOY_DIR" fetch origin "$BRANCH"
    git -C "$DEPLOY_DIR" checkout "$BRANCH"
    git -C "$DEPLOY_DIR" pull origin "$BRANCH"
fi

cd "$DEPLOY_DIR"

if [ ! -f .env ]; then
    echo "ERROR: .env file missing. Create $DEPLOY_DIR/.env with OPENAI_API_KEY=<your-key>"
    exit 1
fi

echo "==> Stopping existing containers (if any)"
docker-compose down || true

echo "==> Building and starting containers"
docker-compose up -d --build

echo "==> Container status"
docker-compose ps

echo ""
echo "Done. Test with:"
echo "  curl http://127.0.0.1:8001/health"
echo "  curl https://gpt.d-scribe.ru/health"

# --- nginx setup (run once, requires sudo) ---
# sudo cp nginx-gpt.conf /etc/nginx/sites-available/gpt.d-scribe.ru
# sudo ln -sf /etc/nginx/sites-available/gpt.d-scribe.ru /etc/nginx/sites-enabled/gpt.d-scribe.ru
# sudo nginx -t && sudo systemctl reload nginx
# LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 sudo certbot --nginx -d gpt.d-scribe.ru
# sudo nginx -t && sudo systemctl reload nginx
