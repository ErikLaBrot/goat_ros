import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
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
