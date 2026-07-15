#!/bin/bash
cd rgt_desk_backend
rm -rf .venv __pycache__
echo "Removing backend..."
sudo systemctl stop rgt_desk_backend
sudo systemctl disable rgt_desk_backend
sudo rm /etc/systemd/system/rgt_desk_backend.service
sudo systemctl daemon-reload

cd ..

echo "Removing frontend..."
cd rgt_desk_frontend
rm -rf node_modules
rm -rf dist
sudo systemctl stop rgt_desk_frontend
sudo systemctl disable rgt_desk_frontend
sudo rm /etc/systemd/system/rgt_desk_frontend.service
sudo systemctl daemon-reload
