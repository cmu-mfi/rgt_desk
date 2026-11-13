#!/bin/bash
REPO_DIR=$(pwd)
# Backend
echo "Setting up Backend..."
cd rgt_desk_backend
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

sudo ln -sf "$REPO_DIR/systemd_services/rgt_desk_backend.service" /etc/systemd/system/rgt_desk_backend.service
sudo systemctl daemon-reload
sudo systemctl enable rgt_desk_backend
sudo systemctl start rgt_desk_backend
echo "Backend installation complete!"

cd ..
# Frontend
echo "Setting up Frontend..."
# Link the active node and npm into /usr/local/bin so the systemd unit can
# launch them regardless of how node is installed (nvm version, system package)
NODE_BIN=$(command -v node)
sudo ln -sf "$NODE_BIN" /usr/local/bin/node
sudo ln -sf "$(dirname "$NODE_BIN")/npm" /usr/local/bin/npm
cd rgt_desk_frontend
npm install
npm run build
sudo ln -sf "$REPO_DIR/systemd_services/rgt_desk_frontend.service" /etc/systemd/system/rgt_desk_frontend.service
sudo systemctl daemon-reload
sudo systemctl enable rgt_desk_frontend
sudo systemctl start rgt_desk_frontend
echo "Frontend installation complete!"
