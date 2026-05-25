"""Launch the GOAT STL-19P lidar node."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Build the standalone STL-19P launch description."""
    default_config = os.path.join(
        get_package_share_directory("goat_ros_laser"),
        "config",
        "goat_laser.yaml",
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "laser_config_file",
                default_value=default_config,
                description="Path to the goat_ros_laser parameter file.",
            ),
            Node(
                package="goat_ros_laser",
                executable="goat_laser_node",
                name="goat_ros_laser",
                output="screen",
                parameters=[LaunchConfiguration("laser_config_file")],
            ),
        ]
    )
