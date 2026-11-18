# RGT Desk Backend

FastAPI backend for the RGT desk dashboard. It drives ROS 2 (Jazzy) on the robot host from a Vue 3 frontend:

- **Processes** — long-running `ros2 launch`/`ros2 run` scripts, spawned as windows in the `rgt` tmux session (via libtmux). One window per process, named after the process.
- **Services** — one-shot ROS service/action scripts, spawned as `service-<name>` windows in the same tmux session. Calls return immediately and can be monitored or cancelled from the dashboard.
- **Status** — a background rclpy thread (`process_monitor.py`) derives each process's lifecycle status, which the frontend polls every second.

Interactive API docs: **`/docs`** (Swagger UI), `/redoc`, and the machine-readable `/openapi.json`.

## API

| Endpoint | Method | Purpose |
|---|---|---|
| `/get_status` | GET | Map of process name → status (`running` / `started` / `error` / `stopped`) |
| `/get_logs` | GET | Map of process name → recent terminal lines |
| `/start_process` | POST | Build the process's command from its template and open a tmux window |
| `/stop_process` | POST | Ctrl-C + kill the process's tmux window |
| `/execute_service` | POST | Start the service script; returns HTTP 202 with `executing` |
| `/get_service_status` | GET | Map of service name → `idle` / `executing` |
| `/get_service_logs` | GET | Map of service name → recent terminal lines (`lines=100`, allowed 1–1000) |
| `/cancel_service` | POST | Cancel the local service-call client; body: `{"name": "home"}` |

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

Errors: an unknown name returns **404**; a missing or invalid param returns **400**. The frontend sends defaults derived from `panels.json`.

The Utilities tab's **Gripper Command** pane sends `control_msgs/action/ParallelGripperCommand` to `/gripper/robotiq_gripper_controller/gripper_cmd` for `robotiq_85_left_knuckle_joint`. Its position slider ranges from 0 to 1 in steps of 0.01 and defaults to 0. Sending requires clicking **Command gripper**. Start the gripper controller before sending commands. The same backend call is:

```sh
curl -X POST http://localhost:8000/execute_service \
  -H 'Content-Type: application/json' \
  -d '{"name": "gripper_command", "params": {"position": 1.0}}'
```

The backend rejects nonnumeric, nonfinite, and out-of-range positions. The action uses the existing service status/log/cancel endpoints; **Cancel call** stops the local action client and may leave an accepted gripper motion running.

## Service lifecycle and cancellation

`/execute_service` is asynchronous: its `executing` response acknowledges the launch, and callers must poll `/get_service_status` for completion. Only one call per configured service id may run at once, including calls with different robot params; a duplicate returns **409**. Different service ids can run concurrently.

Services have only two states: `executing` while their tmux pane is active, and `idle` otherwise. Exiting, cancellation, and external window removal all return the service to `idle` immediately, with no completion timer. Inspect the terminal output for the ROS server's response or errors.

Service windows close automatically when their command exits, even without dashboard polling. Logs come directly from the live tmux pane and are deleted with the window; no output is cached. Running calls are adopted after a backend restart.

Cancel sends Ctrl-C to the local client, waits up to one second and removes the window whether the client exited normally or needed to be killed. **Stopping a local ROS service call does not cancel work already accepted by the ROS server**, including robot motion. Use the server's action cancellation or robot controls where applicable.

Use each service card's **Logs** section to follow output and **Cancel call** to interrupt it. **Expand all logs** includes both process and service cards. All lifecycle state shown on service cards comes from the backend, so opening another browser also shows active calls.

## Status derivation

`process_monitor.py` runs a 1s loop and sets each configured process to:

- **`stopped`** — idle, or explicitly stopped through `/stop_process`. This remains idle even if a matching external ROS node is visible.
- **`started`** — set immediately by `/start_process`; waits for the matching ROS node to appear.
- **`running`** — the matching ROS node is visible on the DDS domain and its optional readiness topic has not reported `false`.
- **`error`** — a node that was previously visible has disappeared, or a visible robot manager's readiness topic reports `false`. Recovery requires the node to be visible and readiness to permit running; explicit Stop still sets `stopped`.

Node names are matched exactly, in any namespace. Each process's `node_name` in `config.json` selects the ROS node to watch; if omitted, it defaults to the process key. For example, `ur20` watches `ur_robot_manager`, `nex10` watches `ynx_robot_manager`, and `bed_side_cam` watches `cam_watch`.

The robot processes also configure `ready_topic`: `/ur20/ready` and `/nex10/ready` respectively (`std_msgs/msg/Bool`). A `false` value overrides node visibility with `error`; `true` allows `running` only while the manager node is visible. Subscriptions use reliable, transient-local QoS to receive the retained value after a backend restart. Before any readiness message arrives, status follows the existing node checks. Readiness messages do not override an explicitly stopped process.

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
- An optional `"bounds"` map, e.g. `"bounds": {"position": {"min": 0, "max": 1}}`, requires finite numeric values within inclusive limits. Booleans are rejected.
- A process's optional `"node_name"` selects the exact ROS node name used for status checks, without a namespace. It defaults to the process key and does not rename the launched node.
- A process's optional `"ready_topic"` subscribes to a `std_msgs/msg/Bool` topic; `false` changes a visible node's status to `error`.
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

Process tests simulate ROS graph observations and tmux operations. Service tests run harmless shell commands in tmux servers on private sockets and cover completion, failures, cancellation, duplicate requests, and restart adoption. They do not call robot services or launch robot processes. Service integration tests are skipped if tmux is unavailable.

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
