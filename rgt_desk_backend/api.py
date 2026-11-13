from fastapi import APIRouter, HTTPException
from typing import Dict
import tmux
from models import (
    StartProcessRequest,
    StopProcessRequest,
    RunServiceRequest,
    ProcessStartResponse,
    ProcessStopResponse,
    ServiceExecutionResponse,
)
from process_config import (
    UnknownNameError,
    MissingParamError,
    build_command,
    process_names,
)
from process_monitor import process_monitor
import subprocess

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
    `running` = tmux window AND matching ROS node visible, `started` = window
    only, `error` = process-specific fault detected (ur20/nex10 only),
    `stopped` = no window.
    """
    return process_monitor.get_status()

@router.post(
    "/start_process",
    tags=["processes"],
    summary="Start a long-running process",
    response_model=ProcessStartResponse,
    responses={
        404: {"description": "Process name not found in config.json"},
        400: {"description": "A param required by the command template is missing"},
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
    except MissingParamError as e:
        raise HTTPException(status_code=400, detail=str(e))
    tmux.start_process(req.name, command)

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
    tmux.stop_process(req.name)

    return {"status": "stopped", "name": req.name}

@router.post(
    "/execute_service",
    tags=["services"],
    summary="Run a one-shot service script",
    response_model=ServiceExecutionResponse,
    responses={
        404: {"description": "Service name not found in config.json"},
        400: {"description": "A param required by the command template is missing"},
        },
    )
def execute_service(req: RunServiceRequest):
    """Fills the service's `config.json` command template with `params` and runs it synchronously (blocks until the script exits).

    Reports `failed` if the script raises; script output is not captured.
    """
    try:
        command = build_command("service", req.name, req.params)
    except UnknownNameError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MissingParamError as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        subprocess.run(
                command,
                shell=True,
                capture_output=False,
                text=False,
                )
    except:
        return {"status": "failed", "name": req.name}

    return {"status": "executed", "name": req.name}
