from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router
from process_monitor import process_monitor

@asynccontextmanager
async def lifespan(app: FastAPI):
    process_monitor.start()
    yield
    process_monitor.stop()

app = FastAPI(
    lifespan=lifespan,
    title="RGT Desk Backend",
    description="""Dashboard backend for the robotics lab. Drives ROS 2 (Jazzy) on the robot host.

- **Processes** are long-running `ros2 launch`/`ros2 run` scripts, spawned as windows in the `rgt` tmux session.
- **Services** are one-shot `ros2 service call` scripts that block until they exit.

The command for every process/service comes from a `{placeholder}` template in `config.json`, filled with the request's params. Process status is derived by a background monitor from tmux windows and visible ROS nodes — see `process_monitor.py` and `README.md`.""",
    version="1.0.0",
    openapi_tags=[
        {"name": "status", "description": "Read-only process status. The frontend polls this every second."},
        {"name": "processes", "description": "Start/stop long-running processes (tmux windows in session `rgt`)."},
        {"name": "services", "description": "One-shot actions that run a service script synchronously and return when it exits."},
        ],
    )

# CORS setup for Vue frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the API endpoints
app.include_router(router)
