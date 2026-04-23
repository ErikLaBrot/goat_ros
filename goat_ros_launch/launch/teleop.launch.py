"""Launch the GOAT local bench teleop integration."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """Build the launch description for explicit bench teleop."""
    teleop_share_dir = get_package_share_directory("goat_teleop")
    default_config_file = os.path.join(
        teleop_share_dir,
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

    teleop_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(teleop_share_dir, "launch", "bench_teleop.launch.py")
        ),
        launch_arguments={
            "config_file": LaunchConfiguration("config_file"),
            "joy_dev": LaunchConfiguration("joy_dev"),
            "deadzone": LaunchConfiguration("deadzone"),
        }.items(),
    )

    return LaunchDescription(
        [
            config_file_argument,
            joy_dev_argument,
            deadzone_argument,
            teleop_launch,
        ]
    )
