import threading
import subprocess
from functools import partial
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Bool
import tmux
import process_config

class ProcessMonitor():
    def __init__(self):
        self.status = {name: "stopped" for name in process_config.process_names()}
        self._ready = {name: None for name in self.status}
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
            self._setup_readiness_subscriptions(monitor_node)
            while not self.stop_event.is_set() and rclpy.ok():
                self._update_status(monitor_node)
                rclpy.spin_once(monitor_node, timeout_sec=0.1)
                self.stop_event.wait(1.0)
                
        finally:
            monitor_node.destroy_node()
            rclpy.shutdown()

    def _setup_readiness_subscriptions(self, monitor_node):
        # Match the managers' retained status so backend restarts receive the
        # current value even when readiness has not changed recently.
        qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        for name in self.status:
            topic = process_config.process_ready_topic(name)
            if topic:
                monitor_node.create_subscription(
                    Bool, topic, partial(self._readiness_callback, name), qos
                )

    def _readiness_callback(self, name, msg):
        with self._lock:
            self._ready[name] = msg.data

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
                node_name = process_config.process_node_name(process_name)
                if node_name in node_names:
                    self.status[process_name] = (
                        "error" if self._ready[process_name] is False else "running"
                    )
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
