#!/bin/bash
set -euo pipefail

# Repo root = the directory containing this script, so the install works
# from any working directory and any clone location.
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# The services must run as the invoking user. If the script itself was
# launched with sudo, SUDO_USER holds the real user (USER would be root).
if [ "$(id -u)" -eq 0 ] && [ -z "${SUDO_USER:-}" ]; then
    echo "Do not run this script as root. Run it as the user who will own the" >&2
    echo "services; it invokes sudo itself where needed." >&2
    exit 1
fi
INSTALL_USER="${SUDO_USER:-${USER:-$(id -un)}}"
INSTALL_HOME="$(getent passwd "$INSTALL_USER" | cut -d: -f6)"
INSTALL_GROUP="$(id -gn "$INSTALL_USER")"
if [ -z "$INSTALL_HOME" ]; then
    echo "Could not determine the home directory of user '$INSTALL_USER'." >&2
    exit 1
fi

echo "Installing RGT Desk for user '$INSTALL_USER' (repo: $REPO_DIR)"

# The ROS 2 workspace is machine-specific, so ask for it. A bare Enter
# accepts the default. Reject paths without a built install tree.
DEFAULT_WS="$INSTALL_HOME/repos/ros2_ws"
ROS2_WS=""
while [ -z "$ROS2_WS" ]; do
    read -rp "Path to your ROS 2 workspace [$DEFAULT_WS]: " ROS2_WS
    ROS2_WS="${ROS2_WS:-$DEFAULT_WS}"
    ROS2_WS="${ROS2_WS/#\~/$INSTALL_HOME}"
    if [ ! -f "$ROS2_WS/install/setup.bash" ]; then
        echo "  No install/setup.bash in '$ROS2_WS' — is it built? Try again." >&2
        ROS2_WS=""
    fi
done
echo "Using ROS 2 workspace: $ROS2_WS"

# Render a unit template into /etc/systemd/system by substituting the
# @PLACEHOLDER@s. FASTRTPS_LINE is dropped unless the user has a Fast DDS
# profile at ~/.ros/fastdds.xml. Uses '|' as the sed delimiter because the
# substituted values are filesystem paths.
install_unit() {
    local template="$1" out="$2" fastdds="$3"
    local fastdds_line=""
    [ -f "$fastdds" ] && fastdds_line="Environment=FASTRTPS_DEFAULT_PROFILES_FILE=$fastdds"
    sed -e "s|@USER@|$INSTALL_USER|g" \
        -e "s|@GROUP@|$INSTALL_GROUP|g" \
        -e "s|@REPO_DIR@|$REPO_DIR|g" \
        -e "s|@ROS2_WS@|$ROS2_WS|g" \
        -e "s|@HOME@|$INSTALL_HOME|g" \
        -e "s|@FASTRTPS_LINE@|$fastdds_line|" \
        "$REPO_DIR/systemd_services/$template" | sudo tee "$out" >/dev/null
}

# Backend
echo "Setting up Backend..."
cd "$REPO_DIR/rgt_desk_backend"
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

install_unit rgt_desk_backend.service.template /etc/systemd/system/rgt_desk_backend.service "$INSTALL_HOME/.ros/fastdds.xml"
sudo systemctl daemon-reload
sudo systemctl enable rgt_desk_backend
sudo systemctl start rgt_desk_backend
echo "Backend installation complete!"

# Frontend
echo "Setting up Frontend..."
# Link the active node and npm into /usr/local/bin so the systemd unit can
# launch them regardless of how node is installed (nvm version, system package)
NODE_BIN="$(command -v node)"
sudo ln -sf "$NODE_BIN" /usr/local/bin/node
sudo ln -sf "$(dirname "$NODE_BIN")/npm" /usr/local/bin/npm
cd "$REPO_DIR/rgt_desk_frontend"
npm install
npm run build
install_unit rgt_desk_frontend.service.template /etc/systemd/system/rgt_desk_frontend.service ""
sudo systemctl daemon-reload
sudo systemctl enable rgt_desk_frontend
sudo systemctl start rgt_desk_frontend
echo "Frontend installation complete!"
