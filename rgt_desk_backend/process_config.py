"""Config-driven command construction for processes and services.

Commands live as `{placeholder}` templates in config.json, next to this file.
The config is read once at import time -- restart the backend service to pick
up changes. Adding a process or service therefore never requires touching
Python code.

This module is deliberately stdlib-only (no rclpy / ROS imports) so it can be
imported and verified on any machine.

Placeholder values are stringified with these rules:
- default: `str(value)` (Python bools become "True"/"False", which is what
  the ros2 CLI expects for flag arguments)
- `"float"` coerce: `str(float(value))` -- where a script needs a decimal
  literal for a ros2 double parameter (JSON/JS does not distinguish 100 from
  100.0, so the config re-asserts it)
- `"int"` coerce: `str(int(value))`

Every value is then `shlex.quote()`d so shell metacharacters stay literal;
empty strings are left empty, matching the previous hand-written behavior.
"""

import json
import re
import shlex
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"

_LABELS = {"process": "Process", "service": "Service"}


class UnknownNameError(Exception):
    """The requested name is not present in config.json."""


class MissingParamError(Exception):
    """The command template needs a param the request did not provide."""


def _load_config(path):
    with open(path) as f:
        return json.load(f)


_CONFIG = _load_config(CONFIG_PATH)
_PROCESS_COMMANDS = _CONFIG.get("processes", {})
_SERVICE_COMMANDS = _CONFIG.get("services", {})


def _coerce(value, kind):
    if kind == "float":
        return str(float(value))
    if kind == "int":
        return str(int(value))
    return str(value)


def build_command(kind, name, params):
    """Build the shell command for a process/service from its template.

    `kind` is "process" or "service", `name` the configured id, `params` the
    request's param dict (or None). Raises UnknownNameError for an
    unconfigured name and MissingParamError when a {placeholder} in the
    template has no matching param.
    """
    entries = _PROCESS_COMMANDS if kind == "process" else _SERVICE_COMMANDS
    entry = entries.get(name)
    if entry is None:
        raise UnknownNameError(f"{_LABELS[kind]} '{name}' is not recognized.")
    params = params or {}
    coerce = entry.get("coerce", {})
    values = {}
    for key in re.findall(r"{(\w+)}", entry["command"]):
        if key not in params:
            raise MissingParamError(
                    f"{_LABELS[kind]} '{name}' is missing param '{key}'."
                    )
        s = _coerce(params[key], coerce.get(key))
        values[key] = shlex.quote(s) if s else s
    return entry["command"].format(**values)


def process_names():
    """Names of all configured processes (tmux window / status keys)."""
    return list(_PROCESS_COMMANDS)
