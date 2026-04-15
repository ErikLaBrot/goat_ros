"""Launch the configured GOAT sensor stack."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.actions import OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def _include_sensor_launch(context):
    """Include the configured sensor launch file when one is provided."""
    sensor_launch_file = LaunchConfiguration("sensor_launch_file").perform(
        context
    ).strip()
    if not sensor_launch_file:
        return []

    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(sensor_launch_file)
        )
    ]


def generate_launch_description():
    """Build the launch description for sensor stack integration."""
    sensor_launch_file_argument = DeclareLaunchArgument(
        "sensor_launch_file",
        default_value="",
        description=(
            "Optional path to a sensor-stack launch file. Empty leaves sensor "
            "bringup to packages outside goat_ros_launch."
        ),
    )

    return LaunchDescription(
        [
            sensor_launch_file_argument,
            OpaqueFunction(function=_include_sensor_launch),
        ]
    )
