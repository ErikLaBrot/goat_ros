"""Launch the high-level teleop-only ROS graph."""

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
    config_dir = LaunchConfiguration("config_dir")
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "config_dir",
                default_value="/etc/goat/config-bundles/teleop",
                description="External config bundle directory.",
            ),
            DeclareLaunchArgument(
                "generated_dir",
                default_value="/run/goat/generated/teleop",
                description="Generated config directory.",
            ),
            DeclareLaunchArgument(
                "profile",
                default_value="default",
                description="Selected config profile.",
            ),
            DeclareLaunchArgument(
                "laser_config_file",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("goat_ros_laser"), "config", "goat_laser.yaml"]
                ),
                description="Path to the goat_ros_laser parameter file.",
            ),
            *bag_launch_arguments(default_profile="lidar_teleop"),
            IncludeLaunchDescription(
                launch_file("vesc_driver.launch.py"),
                launch_arguments={
                    "params_file": PathJoinSubstitution(
                        [config_dir, "params", "vesc.yaml"]
                    )
                }.items(),
            ),
            IncludeLaunchDescription(
                launch_file("teleop.launch.py"),
                launch_arguments={
                    "params_file": PathJoinSubstitution(
                        [config_dir, "params", "teleop.yaml"]
                    )
                }.items(),
            ),
            IncludeLaunchDescription(
                launch_file("laser_driver.launch.py"),
                launch_arguments={
                    "params_file": LaunchConfiguration("laser_config_file")
                }.items(),
            ),
            bag_recorder_include(app_name="teleop_only"),
        ]
    )
