"""Launch the GOAT LD19 lidar driver capability."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """Build the launch description for the GOAT lidar driver."""
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "params_file",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("goat_ros_laser"), "config", "goat_laser.yaml"]
                ),
                description="Path to goat_ros_laser parameters.",
            ),
            Node(
                package="goat_ros_laser",
                executable="goat_laser_node",
                name="goat_ros_laser",
                output="screen",
                parameters=[LaunchConfiguration("params_file")],
            ),
        ]
    )
