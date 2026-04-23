"""Launch full local GOAT bench bringup with joystick teleop.

Purpose:
    Preserve the historical bench-debug workflow by composing robot-side
    bringup with local bench teleop on the same machine.

Inputs:
    Robot-side launch arguments from `robot.launch.py` plus teleop-specific
    `teleop_config_file`, `joy_dev`, and `deadzone`.

Outputs:
    Starts the sensor stack, VESC node, optional recording, local `joy_node`,
    and the `goat_joy` teleop mapper.
"""

from datetime import datetime
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """Build the launch description for full local bench teleop bringup."""
    launch_share_dir = get_package_share_directory("goat_ros_launch")
    teleop_share_dir = get_package_share_directory("goat_teleop")
    default_teleop_config = os.path.join(
        teleop_share_dir,
        "config",
        "goat_joy.yaml",
    )
    default_bag_name = datetime.now().strftime("goat_%Y%m%d_%H%M%S")

    sensor_launch_file_argument = DeclareLaunchArgument(
        "sensor_launch_file",
        default_value="",
        description="Optional path to a sensor-stack launch file.",
    )
    sensor_launch_arguments_argument = DeclareLaunchArgument(
        "sensor_launch_arguments",
        default_value="",
        description=(
            "Optional space-separated name:=value pairs forwarded to "
            "sensor_launch_file."
        ),
    )
    teleop_config_argument = DeclareLaunchArgument(
        "teleop_config_file",
        default_value=default_teleop_config,
        description="Path to the goat_joy parameter file.",
    )
    vesc_config_argument = DeclareLaunchArgument(
        "vesc_config_file",
        default_value=os.path.join(
            get_package_share_directory("goat_vesc_ros"),
            "config",
            "goat_vesc.yaml",
        ),
        description="Path to the goat_vesc_ros parameter file.",
    )
    joy_dev_argument = DeclareLaunchArgument(
        "joy_dev",
        default_value="/dev/input/js0",
        description="Joystick device passed to joy_node.",
    )
    deadzone_argument = DeclareLaunchArgument(
        "deadzone",
        default_value="0.05",
        description="Joystick deadzone passed to joy_node.",
    )
    record_argument = DeclareLaunchArgument(
        "record",
        default_value="false",
        description="Start rosbag recording when true.",
    )
    record_profile_argument = DeclareLaunchArgument(
        "record_profile",
        default_value="core",
        description="Rosbag topic profile name from config/rosbag/profiles.",
    )
    bag_dir_argument = DeclareLaunchArgument(
        "bag_dir",
        default_value="~/.ros/goat/bags",
        description="Directory where rosbag output directories are created.",
    )
    bag_name_argument = DeclareLaunchArgument(
        "bag_name",
        default_value=default_bag_name,
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
            "sensor_launch_file": LaunchConfiguration("sensor_launch_file"),
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
    teleop_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_share_dir, "launch", "teleop.launch.py")
        ),
        launch_arguments={
            "config_file": LaunchConfiguration("teleop_config_file"),
            "joy_dev": LaunchConfiguration("joy_dev"),
            "deadzone": LaunchConfiguration("deadzone"),
        }.items(),
    )

    return LaunchDescription(
        [
            sensor_launch_file_argument,
            sensor_launch_arguments_argument,
            teleop_config_argument,
            vesc_config_argument,
            joy_dev_argument,
            deadzone_argument,
            record_argument,
            record_profile_argument,
            bag_dir_argument,
            bag_name_argument,
            storage_id_argument,
            storage_preset_argument,
            robot_launch,
            teleop_launch,
        ]
    )
