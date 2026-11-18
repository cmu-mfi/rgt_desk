import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from fastapi import HTTPException

import api
from models import RunServiceRequest
from process_config import build_command


class GripperCommandTests(unittest.TestCase):
    def test_valid_positions_launch_command(self):
        for position in (0, 0.37, 1):
            with self.subTest(position=position), patch.object(api.service_monitor, "execute") as execute:
                result = api.execute_service(RunServiceRequest(
                    name="gripper_command", params={"position": position}
                ))
                self.assertEqual(result, {"name": "gripper_command", "status": "executing"})
                execute.assert_called_once_with(
                    "gripper_command", f"../service_scripts/gripper_command.sh {float(position)}"
                )

    def test_invalid_positions_never_launch(self):
        invalid = (-0.01, 1.01, "nan", "inf", "-inf", "bad", "0; echo injected", None, True, [], {})
        for position in invalid:
            with self.subTest(position=position), patch.object(api.service_monitor, "execute") as execute:
                with self.assertRaises(HTTPException) as raised:
                    api.execute_service(RunServiceRequest(
                        name="gripper_command", params={"position": position}
                    ))
                self.assertEqual(raised.exception.status_code, 400)
                execute.assert_not_called()
        with patch.object(api.service_monitor, "execute") as execute:
            with self.assertRaises(HTTPException) as raised:
                api.execute_service(RunServiceRequest(name="gripper_command"))
            self.assertEqual(raised.exception.status_code, 400)
            execute.assert_not_called()

    def test_script_sends_exact_action_arguments_without_ros(self):
        # A fake ros2 executable captures argv; no ROS graph or hardware access.
        with tempfile.TemporaryDirectory() as directory:
            ros2 = Path(directory) / "ros2"
            ros2.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\nexit 7\n')
            ros2.chmod(0o755)
            environment = dict(os.environ, PATH=f"{directory}:{os.environ['PATH']}")
            for position in (0, 0.37, 1):
                command = build_command("service", "gripper_command", {"position": position})
                result = subprocess.run(shlex.split(command), env=environment, capture_output=True, text=True)
                self.assertEqual(result.returncode, 7)
                self.assertEqual(result.stdout.splitlines(), [
                    "action", "send_goal",
                    "/gripper/robotiq_gripper_controller/gripper_cmd",
                    "control_msgs/action/ParallelGripperCommand",
                    "{command: {name: ['robotiq_85_left_knuckle_joint'], "
                    f"position: [{float(position)}]}}}}",
                ])

    def test_utilities_slider_matches_backend(self):
        path = Path(__file__).resolve().parents[2] / "rgt_desk_frontend/src/config/panels.json"
        panels = json.loads(path.read_text())["tabs"]["utilities"]["panels"]
        panel = next(panel for panel in panels if panel["id"] == "gripper_command")
        self.assertEqual(panel["type"], "service")
        position, = panel["params"]
        self.assertEqual((position["key"], position["min"], position["max"]), ("position", 0, 1))


if __name__ == "__main__":
    unittest.main()
