"""Launch the GOAT VESC ROS adapter node.

Purpose:
    Start `goat_vesc_ros` with a parameter file that points the node at the
    expected VESC device and telemetry settings.

Inputs:
    The `config_file` launch argument and the installed `goat_vesc_ros` package
    share directory.

Outputs:
    Starts the `goat_vesc_ros` node and loads its configured ROS parameters.

Usage:
    ros2 launch goat_vesc_ros goat_vesc.launch.py

Notes:
    The selected parameter file must set `device_path` for the target VESC.
"""

# Copyright 2026 GOAT Maintainers

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Build the launch description for the VESC ROS adapter node."""
    default_config_file = os.path.join(
        get_package_share_directory("goat_vesc_ros"),
        "config",
        "goat_vesc.yaml",
    )

    config_file_argument = DeclareLaunchArgument(
        "config_file",
        default_value=default_config_file,
        description="Path to the goat_vesc_ros parameter file.",
    )

    return LaunchDescription(
        [
            config_file_argument,
            Node(
                package="goat_vesc_ros",
                executable="vesc_node",
                name="goat_vesc_ros",
                output="screen",
                parameters=[LaunchConfiguration("config_file")],
            )
        ]
    )
