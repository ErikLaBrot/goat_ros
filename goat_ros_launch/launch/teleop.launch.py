"""Launch the remote GOAT joystick teleop app."""

from launch import LaunchDescription

from goat_ros_launch.app_nodes import teleop_arguments
from goat_ros_launch.app_nodes import teleop_nodes


def generate_launch_description():
    """Build the launch description for remote operator teleop."""
    return LaunchDescription(
        [
            *teleop_arguments(),
            *teleop_nodes(),
        ]
    )
