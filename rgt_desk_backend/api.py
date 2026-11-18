from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Literal
import tmux
from models import (
    StartProcessRequest,
    StopProcessRequest,
    RunServiceRequest,
    ProcessStartResponse,
    ProcessStopResponse,
    ServiceExecutionResponse,
    CancelServiceRequest,
    ServiceStatusResponse,
)
from process_config import (
    UnknownNameError,
    MissingParamError,
    InvalidParamError,
    build_command,
    process_names,
    service_names,
)
from process_monitor import process_monitor
from service_monitor import ServiceBusyError, service_monitor

router = APIRouter()

@router.get(
    "/get_status",
    tags=["status"],
    summary="Status of every configured process",
    response_model=Dict[str, str],
    )
def get_status():
    """Map of process name -> lifecycle status, one entry per configured process.

    Derived by the background monitor (`process_monitor.py`):
    `stopped` = idle or explicitly stopped, `started` = launched and waiting
    for its ROS node, `running` = matching ROS node visible, `error` = a
    previously visible node disappeared or a robot's ready topic is false.
    UR20/NEX10 match `ur_robot_manager`
    and `ynx_robot_manager`; all other processes match their own node name.
    """
    return process_monitor.get_status()

@router.get(
    "/get_logs",
    tags=["processes"],
    summary="Recent terminal output of every configured process",
    response_model=Dict[str, List[str]],
    )
def get_logs(lines: int = 100):
    """Map of process name -> last `lines` lines of its tmux pane history.

    Empty list for processes without a tmux window (stopped). Captured via
    libtmux `capture-pane` as plain, wrapped text. Service output is available
    separately at `/get_service_logs`.
    """
    return {name: tmux.get_logs(name, lines) for name in process_names()}


@router.get("/get_service_status", tags=["services"], response_model=Dict[str, Literal["idle", "executing"]])
def get_service_status():
    """Services are executing while their tmux pane is active, otherwise idle.

    Terminal logs are available only while the service window exists.
    """
    return service_monitor.get_status()


@router.get("/get_service_logs", tags=["services"], response_model=Dict[str, List[str]])
def get_service_logs(lines: int = Query(default=100, ge=1, le=1000)):
    """Live service terminal output; empty once the window closes."""
    return service_monitor.get_logs(lines)

@router.post(
    "/start_process",
    tags=["processes"],
    summary="Start a long-running process",
    response_model=ProcessStartResponse,
    responses={
        404: {"description": "Process name not found in config.json"},
        400: {"description": "A required param is missing or invalid"},
        },
    )
def start_process(req: StartProcessRequest):
    """Fills the process's `config.json` command template with `params` and opens a tmux window named after the process.

    Reports `started` even if the window already exists (the start is a no-op then).
    """
    try:
        command = build_command("process", req.name, req.params)
    except UnknownNameError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (MissingParamError, InvalidParamError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    process_monitor.start_process(req.name, command)

    return {"status": "started", "name": req.name}

@router.post(
    "/stop_process",
    tags=["processes"],
    summary="Stop a long-running process",
    response_model=ProcessStopResponse,
    responses={
        404: {"description": "Process name not found in config.json"},
        },
    )
def stop_process(req: StopProcessRequest):
    """Sends Ctrl-C to the process's tmux window, waits a second, then kills it."""
    if req.name not in process_names():
        raise HTTPException(status_code=404, detail=f"Process '{req.name}' is not recognized.")
    process_monitor.stop_process(req.name)

    return {"status": "stopped", "name": req.name}

@router.post(
    "/execute_service",
    tags=["services"],
    summary="Run a one-shot service script",
    response_model=ServiceExecutionResponse,
    status_code=202,
    responses={
        404: {"description": "Service name not found in config.json"},
        400: {"description": "A required param is missing or invalid"},
        409: {"description": "This service already has an active call"},
        },
    )
def execute_service(req: RunServiceRequest):
    """Start the service script in its own `service-<name>` tmux window.

    Returns immediately; poll `/get_service_status` and `/get_service_logs`.
    Only one call per service id can run at a time, regardless of params.
    """
    try:
        command = build_command("service", req.name, req.params)
    except UnknownNameError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (MissingParamError, InvalidParamError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        service_monitor.execute(req.name, command)
    except ServiceBusyError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return {"status": "executing", "name": req.name}


@router.post("/cancel_service", tags=["services"], response_model=ServiceStatusResponse)
def cancel_service(req: CancelServiceRequest):
    """Stop the local CLI call. This does not cancel work on the ROS server.

    Sends Ctrl-C, waits up to one second, removes the window and its output.
    """
    if req.name not in service_names():
        raise HTTPException(status_code=404, detail=f"Service '{req.name}' is not recognized.")
    return {"status": service_monitor.cancel(req.name), "name": req.name}
