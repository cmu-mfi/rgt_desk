from fastapi import APIRouter, HTTPException
import tmux
from models import StartProcessRequest, StopProcessRequest, RunServiceRequest
from process_config import (
    UnknownNameError,
    MissingParamError,
    build_command,
    process_names,
)
from process_monitor import process_monitor
import subprocess

router = APIRouter()

@router.get("/get_status")
def get_status():
    return process_monitor.get_status()

@router.post("/start_process")
def start_process(req: StartProcessRequest):
    try:
        command = build_command("process", req.name, req.params)
    except UnknownNameError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MissingParamError as e:
        raise HTTPException(status_code=400, detail=str(e))
    tmux.start_process(req.name, command)

    return {"status": "started", "name": req.name}

@router.post("/stop_process")
def stop_process(req: StopProcessRequest):
    if req.name not in process_names():
        raise HTTPException(status_code=404, detail=f"Process '{req.name}' is not recognized.")
    tmux.stop_process(req.name)

    return {"status": "stopped", "name": req.name}

@router.post("/execute_service")
def execute_service(req: RunServiceRequest):
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
