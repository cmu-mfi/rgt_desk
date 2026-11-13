from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field


class StartProcessRequest(BaseModel):
    name: str = Field(
            ...,
            description="Process id to start — must match a key in config.json's `processes` (and the panel id in panels.json).",
            )
    params: Optional[Dict[str, Any]] = Field(
            None,
            description="Param values keyed by the panel's param `key`s from panels.json: toggles arrive as booleans, sliders as numbers, selects as strings.",
            )
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"name": "nex10", "params": {"use_mock_hardware": False, "use_ft_sensor": True}},
                {"name": "spacemouse", "params": {"ns": "ur20"}},
                ]
            }
        }


class StopProcessRequest(BaseModel):
    name: str = Field(
            ...,
            description="Process id to stop — must match a key in config.json's `processes`.",
            )
    model_config = {
        "json_schema_extra": {
            "examples": [{"name": "ur20"}]
            }
        }


class RunServiceRequest(BaseModel):
    name: str = Field(
            ...,
            description="Service id — must match a key in config.json's `services`.",
            )
    params: Optional[Dict[str, Any]] = Field(
            None,
            description="Param values keyed by the panel's param `key`s from panels.json.",
            )
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"name": "set_io", "params": {"robot": "ur20", "pin": 0, "state": 1}},
                {"name": "home", "params": {"ns": "ur20", "speed": 0.1}},
                ]
            }
        }


class ProcessStartResponse(BaseModel):
    status: Literal["started"]
    name: str


class ProcessStopResponse(BaseModel):
    status: Literal["stopped"]
    name: str


class ServiceExecutionResponse(BaseModel):
    status: Literal["executed", "failed"]
    name: str
