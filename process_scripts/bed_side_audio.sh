#!/bin/bash
ros2 launch sounddevice_bringup bringup.launch.py ns:=bed_side_audio device:=5 log_level:=info
