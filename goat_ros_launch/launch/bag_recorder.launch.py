"""Launch the shared GOAT rosbag recorder."""

import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import ExecuteProcess
from launch.actions import LogInfo
from launch.actions import OpaqueFunction
from launch.substitutions import LaunchConfiguration

from goat_ros_launch.bag_support import bag_directory
from goat_ros_launch.bag_support import is_truthy
from goat_ros_launch.bag_support import load_bag_profile
from goat_ros_launch.bag_support import record_command


def recorder_actions(context):
    """Build recorder actions after launch substitutions are available."""
    if not is_truthy(LaunchConfiguration("record_bag").perform(context)):
        return []

    bag_profile = LaunchConfiguration("bag_profile").perform(context)
    bag_root = LaunchConfiguration("bag_root").perform(context)
    bag_note = LaunchConfiguration("bag_note").perform(context)
    robot_name = LaunchConfiguration("robot_name").perform(context)
    app_name = LaunchConfiguration("app_name").perform(context)

    profile_path = (
        Path(get_package_share_directory("goat_ros_launch"))
        / "config"
        / "bag_profiles"
        / f"{bag_profile}.yaml"
    )
    topics = load_bag_profile(profile_path)
    os.makedirs(bag_root, exist_ok=True)
    output_dir = bag_directory(
        bag_root=bag_root,
        robot_name=robot_name,
        app_name=app_name,
        bag_profile=bag_profile,
        bag_note=bag_note,
    )
    return [
        LogInfo(msg=f"Recording GOAT bag to {output_dir} with profile {bag_profile}"),
        ExecuteProcess(
            cmd=record_command(topics, output_dir),
            output="screen",
        ),
    ]


def generate_launch_description():
    """Build the shared bag recorder launch description."""
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "record_bag",
                default_value="false",
                description="Start ros2 bag recording.",
            ),
            DeclareLaunchArgument(
                "bag_profile",
                default_value="lidar_teleop",
                description="Installed bag profile name from goat_ros_launch.",
            ),
            DeclareLaunchArgument(
                "bag_note",
                default_value="",
                description="Optional note appended to the bag directory name.",
            ),
            DeclareLaunchArgument(
                "bag_root",
                default_value="/workspaces/goat_data/bags/raw",
                description="Persistent directory for raw bag recordings.",
            ),
            DeclareLaunchArgument(
                "robot_name",
                default_value="goat-racer",
                description="Robot name included in bag directory names.",
            ),
            DeclareLaunchArgument(
                "app_name",
                default_value="app",
                description="App name included in bag directory names.",
            ),
            OpaqueFunction(function=recorder_actions),
        ]
    )
