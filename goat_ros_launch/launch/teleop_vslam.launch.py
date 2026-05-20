"""Launch the all-in-one GOAT teleop and Visual SLAM app."""

from launch import LaunchDescription

from goat_ros_launch.app_nodes import common_sensor_arguments
from goat_ros_launch.app_nodes import sensor_nodes
from goat_ros_launch.app_nodes import teleop_arguments
from goat_ros_launch.app_nodes import teleop_nodes
from goat_ros_launch.app_nodes import visual_slam_arguments


def generate_launch_description():
    """Build the launch description for remote teleop plus VSLAM."""
    return LaunchDescription(
        [
            *common_sensor_arguments(),
            *visual_slam_arguments(),
            *teleop_arguments(),
            *sensor_nodes(include_visual_slam=True),
            *teleop_nodes(),
        ]
    )
