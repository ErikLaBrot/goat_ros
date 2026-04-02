import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory("goat_vesc_ros")
    default_config_file = os.path.join(package_share, "config", "goat_vesc.yaml")
    default_smoke_config_file = os.path.join(
        package_share,
        "config",
        "goat_vesc_duty_smoke.yaml",
    )

    config_file_argument = DeclareLaunchArgument(
        "config_file",
        default_value=default_config_file,
        description="Path to the base goat_vesc_ros parameter file.",
    )
    smoke_config_file_argument = DeclareLaunchArgument(
        "smoke_config_file",
        default_value=default_smoke_config_file,
        description="Path to the duty-mode smoke-test parameter overlay.",
    )

    return LaunchDescription(
        [
            config_file_argument,
            smoke_config_file_argument,
            Node(
                package="goat_vesc_ros",
                executable="vesc_node",
                name="goat_vesc_ros",
                output="screen",
                parameters=[
                    LaunchConfiguration("config_file"),
                    LaunchConfiguration("smoke_config_file"),
                ],
            ),
        ]
    )
