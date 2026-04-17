"""Launch the canonical GOAT robot bringup entrypoint."""

from datetime import datetime
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.actions import IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def _is_true(value):
    """Return whether a launch argument string is truthy."""
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _profile_topics(profile_name):
    """Load the explicit rosbag topic allowlist for a recording profile."""
    if not profile_name or profile_name != os.path.basename(profile_name):
        raise RuntimeError(
            "record_profile must be a profile name from config/rosbag/profiles"
        )

    launch_share_dir = get_package_share_directory("goat_ros_launch")
    profile_file = os.path.join(
        launch_share_dir,
        "config",
        "rosbag",
        "profiles",
        f"{profile_name}.txt",
    )
    if not os.path.exists(profile_file):
        raise RuntimeError(f"Unknown rosbag record_profile: {profile_name}")

    with open(profile_file, "r", encoding="utf-8") as profile:
        topics = [
            line.strip()
            for line in profile
            if line.strip() and not line.lstrip().startswith("#")
        ]

    if not topics:
        raise RuntimeError(f"Rosbag profile has no topics: {profile_file}")

    return topics


def _record_process(context):
    """Create the rosbag recorder process only when recording is enabled."""
    if not _is_true(LaunchConfiguration("record").perform(context)):
        return []

    bag_dir = os.path.expanduser(
        LaunchConfiguration("bag_dir").perform(context)
    )
    bag_name = LaunchConfiguration("bag_name").perform(context).strip()
    if not bag_name:
        bag_name = datetime.now().strftime("goat_%Y%m%d_%H%M%S")

    os.makedirs(bag_dir, exist_ok=True)
    bag_path = os.path.join(bag_dir, bag_name)
    storage_id = LaunchConfiguration("storage_id").perform(context).strip()
    storage_preset = LaunchConfiguration("storage_preset").perform(
        context
    ).strip()
    topics = _profile_topics(
        LaunchConfiguration("record_profile").perform(context).strip()
    )

    cmd = [
        "ros2",
        "bag",
        "record",
        "-o",
        bag_path,
        "--storage",
        storage_id,
    ]
    if storage_preset:
        cmd.extend(["--storage-preset-profile", storage_preset])
    cmd.extend(topics)

    return [ExecuteProcess(cmd=cmd, output="screen")]


def generate_launch_description():
    """Build the launch description for full robot bringup."""
    launch_share_dir = get_package_share_directory("goat_ros_launch")
    teleop_share_dir = get_package_share_directory("goat_teleop")
    vesc_share_dir = get_package_share_directory("goat_vesc_ros")

    default_teleop_config = os.path.join(
        teleop_share_dir,
        "config",
        "goat_joy.yaml",
    )
    default_vesc_config = os.path.join(
        vesc_share_dir,
        "config",
        "goat_vesc.yaml",
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
        default_value=default_vesc_config,
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

    sensors_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_share_dir, "launch", "sensors.launch.py")
        ),
        launch_arguments={
            "sensor_launch_file": LaunchConfiguration("sensor_launch_file"),
            "sensor_launch_arguments": LaunchConfiguration(
                "sensor_launch_arguments"
            ),
        }.items(),
    )
    vesc_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(vesc_share_dir, "launch", "goat_vesc.launch.py")
        ),
        launch_arguments={
            "config_file": LaunchConfiguration("vesc_config_file"),
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
            sensors_launch,
            vesc_launch,
            teleop_launch,
            OpaqueFunction(function=_record_process),
        ]
    )
