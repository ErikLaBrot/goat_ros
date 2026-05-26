"""Launch GOAT sensors for dev use or deployment."""

from launch import LaunchDescription

from goat_ros_launch.app_nodes import common_sensor_arguments
from goat_ros_launch.app_nodes import sensor_nodes
from goat_ros_launch.launch_bags import bag_launch_arguments
from goat_ros_launch.launch_bags import bag_recorder_include


def generate_launch_description():
    """Build the launch description for VESC plus RealSense sensors."""
    return LaunchDescription(
        [
            *common_sensor_arguments(),
            *bag_launch_arguments(default_profile="lidar_teleop"),
            *sensor_nodes(),
            bag_recorder_include(app_name="sensors"),
        ]
    )
