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

- **`stopped`** — idle, or explicitly stopped through `/stop_process`. This remains idle even if a matching external ROS node is visible.
- **`started`** — set immediately by `/start_process`; waits for the matching ROS node to appear.
- **`running`** — the matching ROS node is visible on the DDS domain.
- **`error`** — a node that was previously visible has disappeared. This persists until the node returns (`running`), the process is explicitly stopped (`stopped`), or a new launch is made (`started`).

Node names are matched exactly, in any namespace. Each process's `node_name` in `config.json` selects the ROS node to watch; if omitted, it defaults to the process key. For example, `ur20` watches `ur_robot_manager`, `nex10` watches `ynx_robot_manager`, and `bed_side_cam` watches `cam_watch`. No robot status topics are subscribed to.

Existing tmux windows are adopted on backend startup. Once a process has been started, losing its tmux window does not reset it to idle; its state follows the node lifecycle until an explicit Stop. A process whose node has never appeared stays `started` (there is no startup timeout). Repeated Start requests for an existing window leave its current state unchanged. Lifecycle history is kept in memory and resets on backend restart.

## Config-driven commands

`config.json` holds one `command` template per process/service; `process_config.py` fills its `{placeholder}`s with the request's params:

```json
"nex10": {
  "node_name": "ynx_robot_manager",
  "command": "../process_scripts/nex10.sh {use_mock_hardware} {use_ft_sensor}"
}
```

- Values are stringified then `shlex.quote`d: `true` → `"True"`, numbers as-is.
- An optional `"coerce"` map forces `"float"` (`str(float(v))`) or `"int"` — use `float` where a script needs a decimal literal for a ros2 double param (JSON/JS does not distinguish `100` from `100.0`).
- A process's optional `"node_name"` selects the exact ROS node name used for status checks, without a namespace. It defaults to the process key and does not rename the launched node.
- The config is read at startup — restart the backend to apply changes.
- The module is stdlib-only (no ROS imports), so command construction can be tested anywhere.

## Adding a process or service

No Python changes needed. Process name = tmux window name = status key = frontend id = `config.json` key:

1. `process_scripts/<name>.sh` (or `service_scripts/<name>.sh`) — `chmod +x`
2. `rgt_desk_backend/config.json` — entry with a `command` template and a `node_name` matching the ROS node to monitor
3. `rgt_desk_frontend/src/config/panels.json` — panel entry under the right tab; param `key`s must match the `{placeholder}`s

**Gotcha:** the configured `node_name` must match a ROS node launched by the script for status to reach `running`. If it never matches, the card stays yellow (`started`) forever.

## Verification

From `rgt_desk_backend/`, with ROS 2 Jazzy sourced and backend dependencies available:

```sh
.venv/bin/python -m unittest discover -s tests -v
```

These tests simulate ROS graph observations and tmux operations; they do not launch robot processes.

## Running locally

Source your ROS 2 environment, then run from the repository root:

```sh
./rgt_desk_backend/run.sh
```

The script changes to the backend directory, creates or reuses `.venv` with system packages visible, installs `requirements.txt`, and starts uvicorn. Defaults: `BIND_HOST=0.0.0.0`, `PORT=8000`, `ROS_DOMAIN_ID=19`; existing values are respected. Extra arguments go to uvicorn (for example `--reload`).

ROS 2 Jazzy, Python/venv, tmux, and `rclpy` must already be installed.

## Deployment

- `systemd_services/` unit files are templates; `install.sh` substitutes the invoking user, the repo path, and the ROS 2 workspace it prompts for, then writes the rendered units into `/etc/systemd/system`.
- The backend binds `192.168.19.10:8000` with `ROS_DOMAIN_ID=19`; the units run as whichever user runs `install.sh`.
- Code changes go live with:

  ```sh
  sudo systemctl restart rgt_desk_backend.service rgt_desk_frontend.service
  ```

  The frontend unit runs `npm install && npm run build` on every start (up to 120s).
