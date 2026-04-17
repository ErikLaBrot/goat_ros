"""Launch the configured GOAT sensor stack."""

import shlex

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.actions import OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def _sensor_launch_arguments(argument_string):
    """Parse forwarded sensor launch arguments."""
    launch_arguments = {}
    if not argument_string:
        return launch_arguments

    for token in shlex.split(argument_string):
        if ":=" not in token:
            raise RuntimeError(
                "sensor_launch_arguments must be space-separated "
                "name:=value pairs"
            )

        name, value = token.split(":=", 1)
        if not name:
            raise RuntimeError(
                "sensor_launch_arguments contains an empty argument name"
            )

        launch_arguments[name] = value

    return launch_arguments


def _include_sensor_launch(context):
    """Include the configured sensor launch file when one is provided."""
    sensor_launch_file = LaunchConfiguration("sensor_launch_file").perform(
        context
    ).strip()
    if not sensor_launch_file:
        return []

    sensor_launch_arguments = _sensor_launch_arguments(
        LaunchConfiguration("sensor_launch_arguments").perform(context).strip()
    )

    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(sensor_launch_file),
            launch_arguments=sensor_launch_arguments.items(),
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
    sensor_launch_arguments_argument = DeclareLaunchArgument(
        "sensor_launch_arguments",
        default_value="",
        description=(
            "Optional space-separated name:=value pairs forwarded to the "
            "configured sensor launch file."
        ),
    )

    return LaunchDescription(
        [
            sensor_launch_file_argument,
            sensor_launch_arguments_argument,
            OpaqueFunction(function=_include_sensor_launch),
        ]
    )
