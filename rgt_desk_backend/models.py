from typing import Any, Dict, Optional
from pydantic import BaseModel

class StartProcessRequest(BaseModel):
    name: str
    params: Optional[Dict[str, Any]] = None

class StopProcessRequest(BaseModel):
    name: str

class RunServiceRequest(BaseModel):
    name: str
    params: Optional[Dict[str, Any]] = None
