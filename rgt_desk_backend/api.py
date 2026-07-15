from fastapi import APIRouter, HTTPException
import tmux
from models import StartProcessRequest, StopProcessRequest, RunServiceRequest
from process_monitor import process_monitor
import subprocess

router = APIRouter()

@router.get("/get_status")
def get_status():
    process_status = process_monitor.get_status()
    return process_status

@router.post("/start_process")
def start_process(req: StartProcessRequest):
    if req.name == "ur20":
        use_mock_hardware = bool((req.params or {}).get("use_mock_hardware", False))
        command = f"../process_scripts/ur20.sh {use_mock_hardware}"
        tmux.start_process(req.name, command)
    elif req.name == "nex10":
        use_mock_hardware = bool((req.params or {}).get("use_mock_hardware", False))
        use_ft_sensor = bool((req.params or {}).get("use_ft_sensor", False))
        command = f"../process_scripts/nex10.sh {use_mock_hardware} {use_ft_sensor}"
        tmux.start_process(req.name, command)
    elif req.name == "rgt_manager":
        command = "../process_scripts/rgt_manager.sh"
        tmux.start_process(req.name, command)
    elif req.name == "foxglove_bridge":
        command = "../process_scripts/foxglove_bridge.sh"
        tmux.start_process(req.name, command)
    elif req.name == "spacemouse":
        command = f"../process_scripts/spacemouse.sh {req.params['ns']}"
        tmux.start_process(req.name, command)
    elif req.name == "bed_side_cam":
        command = "../process_scripts/bed_side_cam.sh"
        tmux.start_process(req.name, command)
    elif req.name == "bed_side_thermal":
        command = "../process_scripts/bed_side_thermal.sh"
        tmux.start_process(req.name, command)
    elif req.name == "bed_side_audio":
        command = "../process_scripts/bed_side_audio.sh"
        tmux.start_process(req.name, command)
    elif req.name == "panda":
        command = "../process_scripts/panda.sh"
        tmux.start_process(req.name, command)
    elif req.name == "space_panda_link":
        command = "../process_scripts/space_panda_link.sh"
        tmux.start_process(req.name, command)
    else:
        raise HTTPException(status_code=404, detail=f"Process '{req.name}' is not recognized.")

    return {"status": "started", "name": req.name}

@router.post("/stop_process")
def stop_process(req: StopProcessRequest):
    if req.name == "ur20":
        tmux.stop_process(req.name)
    elif req.name == "nex10":
        tmux.stop_process(req.name)
    elif req.name == "rgt_manager":
        tmux.stop_process(req.name)
    elif req.name == "foxglove_bridge":
        tmux.stop_process(req.name)
    elif req.name == "spacemouse":
        tmux.stop_process(req.name)
    elif req.name == "bed_side_cam":
        tmux.stop_process(req.name)
    elif req.name == "bed_side_thermal":
        tmux.stop_process(req.name)
    elif req.name == "bed_side_audio":
        tmux.stop_process(req.name)
    elif req.name == "panda":
        tmux.stop_process(req.name)
    elif req.name == "space_panda_link":
        tmux.stop_process(req.name)
    else:
        raise HTTPException(status_code=404, detail=f"Process '{req.name}' is not recognized.")

    return {"status": "stopped", "name": req.name}

@router.post("/execute_service")
def execute_service(req: RunServiceRequest):
    if req.name == "home":
        command = f"../service_scripts/home.sh {req.params['ns']} {req.params['speed']}"
        try:
            subprocess.run(
                    command,
                    shell=True,
                    capture_output=False,
                    text=False,
                    )
        except:
            return {"status": "failed", "name": req.name}
    elif req.name == "park":
        command = f"../service_scripts/park.sh {req.params['ns']} {req.params['speed']}"
        try:
            subprocess.run(
                    command,
                    shell=True,
                    capture_output=False,
                    text=False,
                    )
        except:
            return {"status": "failed", "name": req.name}
    elif req.name == "change_tool":
        command = f"../service_scripts/change_tool.sh {req.params['robot']} {req.params['tool']}"
        try:
            subprocess.run(
                    command,
                    shell=True,
                    capture_output=False,
                    text=False,
                    )
        except:
            return {"status": "failed", "name": req.name}
    elif req.name == "override_tool_location":
        command = f"../service_scripts/override_tool_location.sh {req.params['tool']} {req.params['location']}"
        try:
            subprocess.run(
                    command,
                    shell=True,
                    capture_output=False,
                    text=False,
                    )
        except:
            return {"status": "failed", "name": req.name}
    elif req.name == "space_panda_link_parameters":
        command = f"../service_scripts/space_panda_link_parameters.sh {str(float(req.params['mimicing_scale']))} {str(float(req.params['wrench_passthrough_force_scale']))} {str(float(req.params['wrench_passthrough_torque_scale']))} {str(float(req.params['damping_value']))} {req.params['mimicing_enabled']} {req.params['wrench_passthrough_enabled']} {req.params['damping_enabled']}"
        print(command)
        try:
            subprocess.run(
                    command,
                    shell=True,
                    capture_output=False,
                    text=False,
                    )
        except:
            return {"status": "failed", "name": req.name}
    elif req.name == "set_io":
        command = f"../service_scripts/set_io.sh {req.params['robot']} {req.params['pin']} {req.params['state']}"
        try:
            subprocess.run(
                    command,
                    shell=True,
                    capture_output=False,
                    text=False,
                    )
        except:
            return {"status": "failed", "name": req.name}
    else:
        raise HTTPException(status_code=404, detail=f"Service '{req.name}' is not recognized.")

    return {"status": "executed", "name": req.name}
