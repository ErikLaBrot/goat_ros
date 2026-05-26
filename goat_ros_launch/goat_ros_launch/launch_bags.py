"""Shared launch helpers for optional GOAT bag recording."""

from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def bag_launch_arguments(default_profile: str) -> list[DeclareLaunchArgument]:
    """Return launch arguments shared by recordable GOAT apps."""
    return [
        DeclareLaunchArgument(
            "record_bag",
            default_value="false",
            description="Start ros2 bag recording with this app.",
        ),
        DeclareLaunchArgument(
            "bag_profile",
            default_value=default_profile,
            description="Installed bag profile name from goat_ros_launch.",
        ),
        DeclareLaunchArgument(
            "bag_note",
            default_value="",
            description="Optional note appended to the bag directory name.",
        ),
        DeclareLaunchArgument(
            "bag_root",
            default_value="/workspaces/goat_data/bags/raw",
            description="Persistent directory for raw bag recordings.",
        ),
        DeclareLaunchArgument(
            "robot_name",
            default_value="goat-racer",
            description="Robot name included in bag directory names.",
        ),
    ]


def bag_recorder_include(app_name: str) -> IncludeLaunchDescription:
    """Include the common bag recorder launch file for an app."""
    return IncludeLaunchDescription(
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
            "record_bag": LaunchConfiguration("record_bag"),
            "bag_profile": LaunchConfiguration("bag_profile"),
            "bag_note": LaunchConfiguration("bag_note"),
            "bag_root": LaunchConfiguration("bag_root"),
            "robot_name": LaunchConfiguration("robot_name"),
            "app_name": app_name,
        }.items(),
    )
