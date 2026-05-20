"""Launch GOAT sensors for dev use or deployment."""

from launch import LaunchDescription

from goat_ros_launch.app_nodes import common_sensor_arguments
from goat_ros_launch.app_nodes import sensor_nodes


def generate_launch_description():
    """Build the launch description for VESC plus RealSense sensors."""
    return LaunchDescription(
        [
            *common_sensor_arguments(),
            *sensor_nodes(),
        ]
    )
