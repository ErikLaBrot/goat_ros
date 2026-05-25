"""Launch a simple rosbag recorder capability."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "output_dir",
                default_value="/var/lib/goat/bags",
                description="Directory for bag output.",
            ),
            ExecuteProcess(
                cmd=["ros2", "bag", "record", "-a", "-o", LaunchConfiguration("output_dir")],
                output="screen",
            ),
        ]
    )

