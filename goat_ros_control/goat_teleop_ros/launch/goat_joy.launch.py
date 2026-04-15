"""Launch the GOAT joystick teleop stack.

Purpose:
    Start `joy_node` and the `goat_joy` teleop node with a shared parameter
    file for manual joystick smoke tests.

Inputs:
    `config_file`, `joy_dev`, and `deadzone` launch arguments plus the
    installed `goat_teleop` package share directory.

Outputs:
    Starts the ROS nodes and loads their launch-time parameters.

Usage:
    ros2 launch goat_teleop goat_joy.launch.py

Notes:
    Intended for operator-driven teleop tests that publish `cmd/vesc`.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    """Build the launch description for joystick teleop smoke tests."""
    default_config_file = os.path.join(
        get_package_share_directory("goat_teleop"),
        "config",
        "goat_joy.yaml",
    )

    config_file_argument = DeclareLaunchArgument(
        "config_file",
        default_value=default_config_file,
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

    joy_node = Node(
        package="joy",
        executable="joy_node",
        name="joy_node",
        output="screen",
        parameters=[
            {
                "dev": LaunchConfiguration("joy_dev"),
                "deadzone": ParameterValue(
                    LaunchConfiguration("deadzone"),
                    value_type=float,
                ),
            }
        ],
    )

    goat_joy_node = Node(
        package="goat_teleop",
        executable="goat_joy",
        name="goat_joy",
        output="screen",
        parameters=[LaunchConfiguration("config_file")],
    )

    return LaunchDescription([
        config_file_argument,
        joy_dev_argument,
        deadzone_argument,
        joy_node,
        goat_joy_node,
    ])
