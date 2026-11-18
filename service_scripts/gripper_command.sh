#!/usr/bin/env bash
set -eu

exec ros2 action send_goal \
  /gripper/robotiq_gripper_controller/gripper_cmd \
  control_msgs/action/ParallelGripperCommand \
  "{command: {name: ['robotiq_85_left_knuckle_joint'], position: [$1]}}"
