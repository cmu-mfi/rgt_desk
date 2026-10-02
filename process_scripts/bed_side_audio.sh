#!/bin/bash

/home/mfi/repos/ros2_ws/src/sounddevice_ros/.venv/bin/python3 /home/mfi/repos/ros2_ws/src/sounddevice_ros/sounddevice_ros/sounddevice_ros_publisher_node.py --namespace bed_side_audio --ros-args -p device:=5
