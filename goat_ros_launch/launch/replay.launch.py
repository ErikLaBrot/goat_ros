"""Replay a GOAT rosbag through ros2 bag play."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.actions import OpaqueFunction
from launch.substitutions import LaunchConfiguration


def _is_true(value):
    """Return whether a launch argument string is truthy."""
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _play_process(context):
    """Create the rosbag play process from launch arguments."""
    bag_path = LaunchConfiguration("bag_path").perform(context).strip()
    rate = LaunchConfiguration("rate").perform(context).strip()
    publish_clock = _is_true(
        LaunchConfiguration("publish_clock").perform(context)
    )

    cmd = ["ros2", "bag", "play", "--rate", rate]
    if publish_clock:
        cmd.append("--clock")
    cmd.append(bag_path)

    return [ExecuteProcess(cmd=cmd, output="screen")]


def generate_launch_description():
    """Build the launch description for rosbag replay."""
    bag_path_argument = DeclareLaunchArgument(
        "bag_path",
        description="Path to the rosbag directory to replay.",
    )
    rate_argument = DeclareLaunchArgument(
        "rate",
        default_value="1.0",
        description="Playback rate multiplier.",
    )
    publish_clock_argument = DeclareLaunchArgument(
        "publish_clock",
        default_value="false",
        description="Pass --clock to ros2 bag play when true.",
    )

    return LaunchDescription(
        [
            bag_path_argument,
            rate_argument,
            publish_clock_argument,
            OpaqueFunction(function=_play_process),
        ]
    )
