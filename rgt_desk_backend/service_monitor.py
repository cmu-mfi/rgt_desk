"""One active call per configured service, with tmux-backed lifecycle state."""

import threading

import tmux
from process_config import service_names


class ServiceBusyError(Exception):
    pass


class ServiceMonitor:
    def __init__(self):
        self._lock = threading.Lock()

    def execute(self, name, command):
        with self._lock:
            if tmux.get_service_status(name) == "executing":
                raise ServiceBusyError(f"Service '{name}' is already executing.")
            tmux.start_service(name, command)

    def cancel(self, name):
        with self._lock:
            if tmux.get_service_status(name) == "executing":
                tmux.cancel_service(name)
            return "idle"

    def get_status(self):
        with self._lock:
            return {name: tmux.get_service_status(name) for name in service_names()}

    def get_logs(self, lines):
        with self._lock:
            return {name: tmux.get_logs(tmux.service_window_name(name), lines)
                    for name in service_names()}


service_monitor = ServiceMonitor()
