"""Compatibility wrapper for the shared GOAT bag recorder."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "output_dir",
                default_value="/workspaces/goat_data/bags/raw",
                description="Directory for raw bag output.",
            ),
            DeclareLaunchArgument(
                "bag_profile",
                default_value="lidar_teleop",
                description="Installed bag profile name from goat_ros_launch.",
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [
                        PathJoinSubstitution(
                            [
                                FindPackageShare("goat_ros_launch"),
                                "launch",
                                "bag_recorder.launch.py",
                            ]
                        )
                    ]
                ),
                launch_arguments={
                    "record_bag": "true",
                    "bag_profile": LaunchConfiguration("bag_profile"),
                    "bag_root": LaunchConfiguration("output_dir"),
                    "app_name": "manual",
                }.items(),
            ),
        ]
    )
