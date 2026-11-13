#!/usr/bin/env python3
"""Record grinding data to a rosbag. Python port of grinding_rosbag.sh."""

import argparse
import os
import shutil
from datetime import datetime

SENSOR_TOPICS = [
    "/bed_side_audio/audio/raw",
    "/bed_side_cam/cam_watch/color/camera_info",
    "/bed_side_cam/cam_watch/color/image_raw",
    "/bed_side_cam/cam_watch/infra1/camera_info",
    "/bed_side_cam/cam_watch/infra1/image_rect_raw",
    "/bed_side_cam/cam_watch/infra2/camera_info",
    "/bed_side_cam/cam_watch/infra2/image_rect_raw",
    "/bed_side_cam/cam_watch/point_cloud/cloud_registered",
    "/bed_side_cam/cam_watch/transform_igev_points",
    "/bed_side_cam/cam_watch/extrinsics/depth_to_color",
    "/bed_side_cam/cam_watch/extrinsics/depth_to_depth",
    "/bed_side_cam/cam_watch/extrinsics/depth_to_infra1",
    "/bed_side_cam/cam_watch/extrinsics/depth_to_infra2",
    "/bed_side_thermal/image_raw",
]

ROBOT_TOPICS = [
    "/robot/position_error",
    "/robot/rotation_error",
    "/robot/skill_status",
    "/ur20/dynamic_joint_states",
    "/ur20/ee_accel",
    "/ur20/ee_pose",
    "/ur20/ee_twist",
    "/ur20/force_torque_sensor_broadcaster/wrench",
    "/ur20/force_torque_sensor_broadcaster/wrench_filtered",
    "/ur20/joint_states",
    "/ur20/wrench",
    "/nex10/dynamic_joint_states",
    "/nex10/ee_accel",
    "/nex10/ee_pose",
    "/nex10/ee_twist",
    "/nex10/force_torque_sensor_broadcaster/wrench",
    "/nex10/force_torque_sensor_broadcaster/wrench_filtered",
    "/nex10/joint_states",
    "/nex10/wrench",
]

FRAME_TOPICS = [
    "/tf",
    "/tf_static",
]

# Operator-marked events (contact start/end, safe stop) published by
# record_with_events.py. Must stay listed here or ros2 bag record will
# silently never subscribe to it, even though the publisher is running.
EVENT_TOPICS = [
    "/data_collection/events",
g

TOPICS = SENSOR_TOPICS + ROBOT_TOPICS + FRAME_TOPICS + EVENT_TOPICS

def main():
    parser = argparse.ArgumentParser(description="Record grinding data to a rosbag.")
    parser.add_argument("output_root", nargs="?", default=os.path.join(os.getcwd(), "rosbags"),
                        help="root directory for rosbags (default: ./rosbags)")
    parser.add_argument("-n", "--name", default="",
                        help="optional name appended after the timestamp, "
                             "e.g. grinding_20260824_111039_<name>")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bag_name = f"mfirgt_{timestamp}"
    if args.name:
        bag_name += f"_{args.name}"
    output_root = args.output_root
    output_dir = os.path.join(output_root.rstrip("/"), bag_name)

    os.makedirs(output_root, exist_ok=True)

    print(f"Recording {len(TOPICS)} topics to: {output_dir}")
    for topic in TOPICS:
        print(f"  {topic}")

    cmd = ["ros2", "bag", "record", "-o", output_dir] + TOPICS

    if shutil.which("ros2"):
        os.execvp(cmd[0], cmd)
    else:
        # ros2 not on PATH: source the ROS environment first, like the .sh did
        bash_cmd = "source /opt/ros/jazzy/setup.bash && exec " + " ".join(cmd)
        os.execvp("bash", ["bash", "-c", bash_cmd])


if __name__ == "__main__":
    main()
