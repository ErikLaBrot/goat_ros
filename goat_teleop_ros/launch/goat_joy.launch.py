import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
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

    goat_joy_node = Node(
        package="goat_teleop",
        executable="goat_joy",
        name="goat_joy",
        output="screen",
        parameters=[LaunchConfiguration("config_file")],
    )

    return LaunchDescription([
        config_file_argument,
        goat_joy_node,
    ])
