import threading
import subprocess
import time
import rclpy
from rclpy.node import Node
import tmux
from ur_dashboard_msgs.msg import SafetyMode
from controller_manager_msgs.msg import ControllerManagerActivity

class ProcessMonitor():
    def __init__(self):
        self.status = {
                "ur20": "stopped",
                "nex10": "stopped",
                "rgt_manager": "stopped",
                "foxglove_bridge": "stopped",
                "bed_side_cam": "stopped",
                "bed_side_thermal": "stopped",
                "bed_side_audio": "stopped",
                "spacemouse": "stopped",
                "panda": "stopped",
                "space_panda_link": "stopped",
                }
        self.stop_event = threading.Event()
        self.ur20_error = False
        self.nex10_error = False 
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

        # UR20 Error Monitor
        def ur20_error_monitor_callback(msg):
            if msg.mode != 1:
                self.ur20_error = True
            else:
                self.ur20_error = False
        monitor_node.create_subscription(
            SafetyMode,
            '/ur20/io_and_status_controller/safety_mode',
            ur20_error_monitor_callback,
            10
        )
        
        # Nex10 Error Monitor
        def nex10_error_monitor_callback(msg):
            for hardware_component in msg.hardware_components:
                if hardware_component.name == "nex10":
                    if hardware_component.state.label == "unconfigured":
                        self.nex10_error = True
                    else:
                        self.nex10_error = False
        monitor_node.create_subscription(
            ControllerManagerActivity,
            '/nex10/controller_manager/activity',
            nex10_error_monitor_callback,
            10
        )
        
        try:
            while not self.stop_event.is_set() and rclpy.ok():
                # get windows
                windows = tmux.get_windows()
                # get nodes list
                names_and_namespaces = monitor_node.get_node_names_and_namespaces()
                node_paths = []
                for name, ns in names_and_namespaces:
                    if ns == '/':
                        node_paths.append(f"/{name}")
                    else:
                        node_paths.append(f"{ns}/{name}")
                node_list = "\n".join(node_paths)
                # set status accordingly
                for process_name in self.status:
                    if process_name in windows and process_name in node_list:
                        self.status[process_name] = "running"
                    elif process_name in windows and process_name not in node_list:
                        self.status[process_name] = "started"
                    else:
                        self.status[process_name] = "stopped"
                # UR20 Error Check
                if "ur20" in windows and self.ur20_error:
                    self.status["ur20"] = "error"
                # Nex10 Error Check
                if "nex10" in windows and self.nex10_error:
                    self.status["nex10"] = "error"
                # Process all incoming callbacks
                rclpy.spin_once(monitor_node, timeout_sec=0.1)
                time.sleep(1.0)
                
        finally:
            monitor_node.destroy_node()
            rclpy.shutdown()

    def get_status(self):
        return self.status

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
