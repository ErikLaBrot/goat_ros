"""Replay a GOAT rosbag through ROS launch."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration

from goat_ros_launch.bag_support import is_truthy


def replay_actions(context):
    """Build ros2 bag play actions after substitutions are available."""
    bag_path = LaunchConfiguration("bag_path").perform(context).strip()
    if not bag_path:
        raise RuntimeError("bag_path must be provided")
    command = ["ros2", "bag", "play", bag_path]
    if is_truthy(LaunchConfiguration("use_clock").perform(context)):
        command.append("--clock")
    return [ExecuteProcess(cmd=command, output="screen")]


def generate_launch_description():
    """Build the bag replay launch description."""
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "bag_path",
                default_value="",
                description="Path to a rosbag directory or bag metadata file.",
            ),
            DeclareLaunchArgument(
                "use_clock",
                default_value="true",
                description="Replay with /clock for use_sim_time consumers.",
            ),
            OpaqueFunction(function=replay_actions),
        ]
    )
