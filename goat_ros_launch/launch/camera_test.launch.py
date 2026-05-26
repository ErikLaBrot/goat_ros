"""Launch the high-level camera test ROS graph."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

from goat_ros_launch.launch_bags import bag_launch_arguments
from goat_ros_launch.launch_bags import bag_recorder_include


def generate_launch_description():
    config_dir = LaunchConfiguration("config_dir")
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "config_dir",
                default_value="/etc/goat/config-bundles/teleop-vslam",
                description="External config bundle directory.",
            ),
            DeclareLaunchArgument(
                "generated_dir",
                default_value="/run/goat/generated/camera-test",
                description="Generated config directory.",
            ),
            DeclareLaunchArgument(
                "profile",
                default_value="default",
                description="Selected config profile.",
            ),
            *bag_launch_arguments(default_profile="camera_test"),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [
                        PathJoinSubstitution(
                            [
                                FindPackageShare("goat_ros_launch"),
                                "launch",
                                "realsense.launch.py",
                            ]
                        )
                    ]
                ),
                launch_arguments={
                    "params_file": PathJoinSubstitution(
                        [config_dir, "params", "realsense.yaml"]
                    )
                }.items(),
            ),
            bag_recorder_include(app_name="camera_test"),
        ]
    )
