"""Launch the GOAT VESC driver capability."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "params_file",
                default_value="/etc/goat/config-bundles/teleop/params/vesc.yaml",
                description="Path to the goat_vesc_ros parameter file.",
            ),
            Node(
                package="goat_vesc_ros",
                executable="vesc_node",
                name="goat_vesc_ros",
                output="screen",
                parameters=[LaunchConfiguration("params_file")],
            ),
        ]
    )

