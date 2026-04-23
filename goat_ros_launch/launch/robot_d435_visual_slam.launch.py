"""Launch GOAT robot bringup with the D435 Visual SLAM sensor stack."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """Build the launch description for robot bringup with stereo VSLAM."""
    launch_share_dir = get_package_share_directory("goat_ros_launch")
    default_sensor_launch = os.path.join(
        launch_share_dir,
        "launch",
        "goat_d435_visual_slam.launch.py",
    )
    default_vesc_config = os.path.join(
        get_package_share_directory("goat_vesc_ros"),
        "config",
        "goat_vesc.yaml",
    )

    sensor_launch_arguments_argument = DeclareLaunchArgument(
        "sensor_launch_arguments",
        default_value="",
        description=(
            "Optional space-separated name:=value pairs forwarded to the "
            "D435 Visual SLAM sensor launch."
        ),
    )
    vesc_config_argument = DeclareLaunchArgument(
        "vesc_config_file",
        default_value=default_vesc_config,
        description="Path to the goat_vesc_ros parameter file.",
    )
    record_argument = DeclareLaunchArgument(
        "record",
        default_value="false",
        description="Start rosbag recording when true.",
    )
    record_profile_argument = DeclareLaunchArgument(
        "record_profile",
        default_value="slam",
        description="Rosbag topic profile name from config/rosbag/profiles.",
    )
    bag_dir_argument = DeclareLaunchArgument(
        "bag_dir",
        default_value="~/.ros/goat/bags",
        description="Directory where rosbag output directories are created.",
    )
    bag_name_argument = DeclareLaunchArgument(
        "bag_name",
        default_value="",
        description="Rosbag output directory name.",
    )
    storage_id_argument = DeclareLaunchArgument(
        "storage_id",
        default_value="mcap",
        description="rosbag2 storage plugin id.",
    )
    storage_preset_argument = DeclareLaunchArgument(
        "storage_preset",
        default_value="zstd_fast",
        description="rosbag2 storage preset profile.",
    )

    robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_share_dir, "launch", "robot.launch.py")
        ),
        launch_arguments={
            "sensor_launch_file": default_sensor_launch,
            "sensor_launch_arguments": LaunchConfiguration(
                "sensor_launch_arguments"
            ),
            "vesc_config_file": LaunchConfiguration("vesc_config_file"),
            "record": LaunchConfiguration("record"),
            "record_profile": LaunchConfiguration("record_profile"),
            "bag_dir": LaunchConfiguration("bag_dir"),
            "bag_name": LaunchConfiguration("bag_name"),
            "storage_id": LaunchConfiguration("storage_id"),
            "storage_preset": LaunchConfiguration("storage_preset"),
        }.items(),
    )

    return LaunchDescription(
        [
            sensor_launch_arguments_argument,
            vesc_config_argument,
            record_argument,
            record_profile_argument,
            bag_dir_argument,
            bag_name_argument,
            storage_id_argument,
            storage_preset_argument,
            robot_launch,
        ]
    )
