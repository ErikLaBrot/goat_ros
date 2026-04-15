"""Launch the end-to-end GOAT controller demo.

Purpose:
    Start the VESC ROS adapter, `joy_node`, and `goat_joy` together for the
    default hardware-backed controller bringup path.

Inputs:
    `vesc_config_file`, `teleop_config_file`, `joy_dev`, and `deadzone` launch
    arguments plus the installed `goat_teleop` and `goat_vesc_ros` package
    share directories.

Outputs:
    Starts the combined ROS nodes needed for the controller demo and forwards
    their configured launch-time parameters.

Usage:
    ros2 launch goat_teleop controller_demo.launch.py

Notes:
    The selected VESC parameter file must set `device_path` for the target
    hardware.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """Build the launch description for the combined controller demo."""
    teleop_share_dir = get_package_share_directory("goat_teleop")
    vesc_share_dir = get_package_share_directory("goat_vesc_ros")
    default_teleop_config = os.path.join(
        teleop_share_dir,
        "config",
        "goat_joy.yaml",
    )
    default_vesc_config = os.path.join(
        vesc_share_dir,
        "config",
        "goat_vesc.yaml",
    )

    vesc_config_argument = DeclareLaunchArgument(
        "vesc_config_file",
        default_value=default_vesc_config,
        description="Path to the goat_vesc_ros parameter file.",
    )
    teleop_config_argument = DeclareLaunchArgument(
        "teleop_config_file",
        default_value=default_teleop_config,
        description="Path to the goat_joy parameter file.",
    )
    joy_dev_argument = DeclareLaunchArgument(
        "joy_dev",
        default_value="/dev/input/js0",
        description="Joystick device passed to joy_node.",
    )
    deadzone_argument = DeclareLaunchArgument(
        "deadzone",
        default_value="0.05",
        description="Joystick deadzone passed to joy_node.",
    )

    vesc_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(vesc_share_dir, "launch", "goat_vesc.launch.py")
        ),
        launch_arguments={
            "config_file": LaunchConfiguration("vesc_config_file"),
        }.items(),
    )
    teleop_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(teleop_share_dir, "launch", "goat_joy.launch.py")
        ),
        launch_arguments={
            "config_file": LaunchConfiguration("teleop_config_file"),
            "joy_dev": LaunchConfiguration("joy_dev"),
            "deadzone": LaunchConfiguration("deadzone"),
        }.items(),
    )

    return LaunchDescription(
        [
            vesc_config_argument,
            teleop_config_argument,
            joy_dev_argument,
            deadzone_argument,
            vesc_launch,
            teleop_launch,
        ]
    )
