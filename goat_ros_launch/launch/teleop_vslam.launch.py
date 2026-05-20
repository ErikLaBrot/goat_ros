"""Launch the robot-side GOAT remote teleop and Visual SLAM app."""

from launch import LaunchDescription

from goat_ros_launch.app_nodes import common_sensor_arguments
from goat_ros_launch.app_nodes import sensor_nodes
from goat_ros_launch.app_nodes import visual_slam_arguments


def generate_launch_description():
    """Build the launch description for remote command reception plus VSLAM."""
    return LaunchDescription(
        [
            *common_sensor_arguments(),
            *visual_slam_arguments(),
            *sensor_nodes(include_visual_slam=True),
        ]
    )
