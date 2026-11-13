# RGT Desk Backend

FastAPI backend for the RGT desk dashboard. It drives ROS 2 (Jazzy) on the robot host from a Vue 3 frontend:

- **Processes** — long-running `ros2 launch`/`ros2 run` scripts, spawned as windows in the `rgt` tmux session (via libtmux). One window per process, named after the process.
- **Services** — one-shot `ros2 service call` scripts that block until they exit.
- **Status** — a background rclpy thread (`process_monitor.py`) derives each process's lifecycle status, which the frontend polls every second.

Interactive API docs: **`/docs`** (Swagger UI), `/redoc`, and the machine-readable `/openapi.json`.

## API

| Endpoint | Method | Purpose |
|---|---|---|
| `/get_status` | GET | Map of process name → status (`running` / `started` / `error` / `stopped`) |
| `/start_process` | POST | Build the process's command from its template and open a tmux window |
| `/stop_process` | POST | Ctrl-C + kill the process's tmux window |
| `/execute_service` | POST | Run the service script synchronously; reports `executed` or `failed` |

```sh
curl http://localhost:8000/get_status
curl -X POST http://localhost:8000/start_process \
  -H 'Content-Type: application/json' \
  -d '{"name": "nex10", "params": {"use_mock_hardware": false, "use_ft_sensor": true}}'
curl -X POST http://localhost:8000/stop_process \
  -H 'Content-Type: application/json' \
  -d '{"name": "ur20"}'
curl -X POST http://localhost:8000/execute_service \
  -H 'Content-Type: application/json' \
  -d '{"name": "set_io", "params": {"robot": "ur20", "pin": 0, "state": 1}}'
```

Errors: an unknown name returns **404**; a param missing from the command template returns **400**. The frontend always sends every param with defaults filled in (derived from `panels.json`), so 400s only affect hand-rolled requests.

## Status derivation

`process_monitor.py` runs a 1s loop and sets each configured process to:

- **`running`** — tmux window exists **and** a ROS node named like the process is visible on the DDS domain
- **`started`** — window exists but no matching ROS node (still booting, crashed, or *node name ≠ process name* — see the gotcha below)
- **`error`** — only for `ur20` (safety mode) and `nex10` (controller manager hardware state), via dedicated topic subscriptions
- **`stopped`** — no window

## Config-driven commands

`config.json` holds one `command` template per process/service; `process_config.py` fills its `{placeholder}`s with the request's params:

```json
"nex10": { "command": "../process_scripts/nex10.sh {use_mock_hardware} {use_ft_sensor}" }
```

- Values are stringified then `shlex.quote`d: `true` → `"True"`, numbers as-is.
- An optional `"coerce"` map forces `"float"` (`str(float(v))`) or `"int"` — use `float` where a script needs a decimal literal for a ros2 double param (JSON/JS does not distinguish `100` from `100.0`).
- The config is read at startup — restart the backend to apply changes.
- The module is stdlib-only (no ROS imports), so command construction can be tested anywhere.

## Adding a process or service

No Python changes needed. Process name = tmux window name = status key = frontend id = `config.json` key:

1. `process_scripts/<name>.sh` (or `service_scripts/<name>.sh`) — `chmod +x`
2. `rgt_desk_backend/config.json` — entry with a `command` template
3. `rgt_desk_frontend/src/config/panels.json` — panel entry under the right tab; param `key`s must match the `{placeholder}`s

**Gotcha:** for status to reach `running`, the ROS node launched by the script must be *named* like the process (tmux window name). If it never matches, the card stays yellow (`started`) forever.

## Running locally

The backend must run from inside `rgt_desk_backend/`: imports are flat and commands invoke `../process_scripts/...` relative to the working directory.

```sh
source /opt/ros/jazzy/setup.bash
source ~/repos/ros2_ws/install/setup.bash   # ur_dashboard_msgs, controller_manager_msgs
cd rgt_desk_backend
source .venv/bin/activate                   # created by ./install.sh
uvicorn main:app --host 0.0.0.0 --port 8000
```

`requirements.txt` (fastapi, uvicorn, libtmux) is not enough on its own — `rclpy`, `ur_dashboard_msgs`, and `controller_manager_msgs` come from the ROS 2 installation.

## Deployment

- `systemd_services/` unit files are symlinked into `/etc/systemd/system` by `install.sh`.
- The backend binds `192.168.19.10:8000` with `ROS_DOMAIN_ID=19`; unit files assume `/home/mfi/repos/rgt_desk` and `User=mfi`.
- Code changes go live with:

  ```sh
  sudo systemctl restart rgt_desk_backend.service rgt_desk_frontend.service
  ```

  The frontend unit runs `npm install && npm run build` on every start (up to 120s).
