"""Launch a lidar-only bag recording demo."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

from goat_ros_launch.launch_bags import bag_launch_arguments
from goat_ros_launch.launch_bags import bag_recorder_include


def launch_file(name):
    return PythonLaunchDescriptionSource(
        [PathJoinSubstitution([FindPackageShare("goat_ros_launch"), "launch", name])]
    )


def generate_launch_description():
    """Build the launch description for a lidar-only rosbag demo."""
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "laser_config_file",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("goat_ros_laser"), "config", "goat_laser.yaml"]
                ),
                description="Path to the goat_ros_laser parameter file.",
            ),
            *bag_launch_arguments(default_profile="lidar_demo"),
            IncludeLaunchDescription(
                launch_file("laser_driver.launch.py"),
                launch_arguments={
                    "params_file": LaunchConfiguration("laser_config_file")
                }.items(),
            ),
            bag_recorder_include(app_name="lidar_bag_demo"),
        ]
    )
