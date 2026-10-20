# AGENTS.md

Dashboard for a robotics lab: Vue 3 frontend drives a FastAPI backend that starts/stops ROS 2 (Jazzy) processes on the robot host. No tests, lint, or typecheck exist — verify frontend changes with `npm run build` in `rgt_desk_frontend/`.

## Architecture

- `rgt_desk_backend/` — FastAPI app (`main.py` → `api.py`). Long-running processes are spawned as tmux windows in session `rgt` via libtmux (`tmux.py`); one-shot actions shell out to `ros2 service call`. `process_monitor.py` is a background rclpy thread deriving status: `running` = tmux window AND matching ROS node visible, `started` = window only, `error` = only for `ur20`/`nex10` (subscribed ROS topics).
- `rgt_desk_frontend/` — Vue 3 + Vite + Tailwind 4 + Pinia. Views in `src/views/` render `<ProcessContainer>`/`<ServiceContainer>` components; all API traffic goes through `src/stores/store.js` → `src/services/api.js` (axios; polls `get_status` every 1s; base URL = page hostname + port 8000).
- `process_scripts/` — one script per long-running process (ros2 launch/run). `service_scripts/` — one script per one-shot ros2 service call. `systemd_services/` — unit files symlinked into `/etc/systemd/system` by `install.sh`.

## Adding a process or service (names must match in 4 places)

Process name = tmux window name = status key = frontend id:

1. `process_scripts/<name>.sh` (or `service_scripts/<name>.sh`)
2. `api.py` — add a branch in `start_process`/`stop_process` (or `execute_service`)
3. `process_monitor.py` — add name to the `status` dict (processes only)
4. Frontend — `configs` entry in `src/stores/store.js` (if it has params) plus a container in the relevant view

## Environment / gotchas

- Backend only works when run from inside `rgt_desk_backend/`: imports are flat and scripts are invoked as `../process_scripts/...` relative to the working directory.
- Backend imports `rclpy`, `ur_dashboard_msgs`, `controller_manager_msgs` — these come from ROS 2 Jazzy (`/opt/ros/jazzy/setup.bash` + external `~/repos/ros2_ws/install/setup.bash`), NOT `requirements.txt`. A venv built from requirements.txt alone fails to import.
- Deploy target is a specific host: unit files hardcode `User=mfi`, `/home/mfi/repos/rgt_desk`, backend binds `192.168.19.10:8000`, `ROS_DOMAIN_ID=19`. `sudo systemctl ...` only works on that machine, not on dev checkouts.
- Code changes go live via `sudo systemctl restart rgt_desk_backend.service rgt_desk_frontend.service`. The frontend unit runs `npm install && npm run build` on every service start, so manual builds aren't needed before restart (but startup takes up to 120s).
- Node engines: `^22.18.0 || >=24.12.0` (README recommends nvm 24; the frontend unit hardcodes an nvm v24.18.0 path).
