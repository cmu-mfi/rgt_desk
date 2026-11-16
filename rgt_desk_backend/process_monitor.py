import threading
import subprocess
import rclpy
from rclpy.node import Node
import tmux
import process_config

class ProcessMonitor():
    NODE_NAMES = {
        "ur20": "ur_robot_manager",
        "nex10": "ynx_robot_manager",
    }

    def __init__(self):
        self.status = {name: "stopped" for name in process_config.process_names()}
        self.stop_event = threading.Event()
        self._lock = threading.Lock()
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self.update_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.stop_event.set()
        if self._thread:
            self._thread.join()

    def update_loop(self):
        rclpy.init()
        monitor_node = Node('rgt_desk')

        try:
            while not self.stop_event.is_set() and rclpy.ok():
                self._update_status(monitor_node)
                rclpy.spin_once(monitor_node, timeout_sec=0.1)
                self.stop_event.wait(1.0)
                
        finally:
            monitor_node.destroy_node()
            rclpy.shutdown()

    def _update_status(self, monitor_node):
        # Serialize graph snapshots with start/stop so stale observations cannot
        # undo an explicit stop or apply to a newly started process.
        with self._lock:
            windows = set(tmux.get_windows())
            node_names = {
                name for name, _ in monitor_node.get_node_names_and_namespaces()
            }
            for process_name, status in self.status.items():
                if status == "stopped":
                    if process_name not in windows:
                        continue
                    # Adopt processes already in tmux when the backend starts.
                    status = "started"
                node_name = self.NODE_NAMES.get(process_name, process_name)
                if node_name in node_names:
                    self.status[process_name] = "running"
                elif status in ("running", "error"):
                    self.status[process_name] = "error"
                else:
                    self.status[process_name] = "started"

    def start_process(self, name, command):
        with self._lock:
            already_started = name in tmux.get_windows()
            tmux.start_process(name, command)
            if not already_started or self.status[name] == "stopped":
                self.status[name] = "started"

    def stop_process(self, name):
        with self._lock:
            tmux.stop_process(name)
            self.status[name] = "stopped"

    def get_status(self):
        with self._lock:
            return self.status.copy()

    def run_command(self, command, timeout_seconds):
        try:
            result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds
                    )
            return result.stdout
        except subprocess.TimeoutExpired:
            return ""
        except:
            return ""

    def check_command_output(self, command, search_string, timeout_seconds):
        stdout = self.run_command(command, timeout_seconds)
        if search_string in stdout:
            return True
        else:
            return False

process_monitor = ProcessMonitor()
