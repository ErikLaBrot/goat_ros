"""Launch the configured GOAT sensor stack."""

import os
import shlex

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.actions import OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
import yaml


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


def _resolve_path(path_value, package_share_dir):
    """Resolve package-relative or absolute paths."""
    if not path_value:
        return ""

    if os.path.isabs(path_value):
        return path_value

    return os.path.join(package_share_dir, path_value)


def _resolve_argument_value(name, value, package_share_dir):
    """Resolve package-relative path-like launch argument values."""
    resolved_value = "" if value is None else str(value)
    if name.endswith(("_file", "_path")):
        return _resolve_path(resolved_value, package_share_dir)

    return resolved_value


def _load_sensor_config(config_file, package_share_dir):
    """Load the default sensor wrapper configuration file."""
    if not os.path.exists(config_file):
        raise RuntimeError(
            f"Sensor config file does not exist: {config_file}"
        )

    with open(config_file, "r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream) or {}

    if not isinstance(config, dict):
        raise RuntimeError(
            f"Sensor config file must contain a mapping: {config_file}"
        )

    sensor_launch_file = config.get("sensor_launch_file", "")
    if not isinstance(sensor_launch_file, str):
        raise RuntimeError(
            "sensor_launch_file in the sensor config must be a string"
        )

    sensor_launch_arguments = config.get("sensor_launch_arguments", {})
    if not isinstance(sensor_launch_arguments, dict):
        raise RuntimeError(
            "sensor_launch_arguments in the sensor config must be a mapping"
        )

    resolved_arguments = {}
    for name, value in sensor_launch_arguments.items():
        if not isinstance(name, str):
            raise RuntimeError(
                "sensor_launch_arguments keys in the sensor config must be strings"
            )
        resolved_arguments[name] = _resolve_argument_value(
            name,
            value,
            package_share_dir,
        )

    resolved_launch_file = _resolve_path(
        sensor_launch_file.strip(),
        package_share_dir,
    )

    if resolved_launch_file and not os.path.exists(resolved_launch_file):
        raise RuntimeError(
            f"Configured sensor launch file does not exist: {resolved_launch_file}"
        )

    return {
        "sensor_launch_file": resolved_launch_file,
        "sensor_launch_arguments": resolved_arguments,
    }


def _include_sensor_launch(context):
    """Include the configured sensor launch file."""
    launch_share_dir = get_package_share_directory("goat_ros_launch")
    config_file = _resolve_path(
        LaunchConfiguration("config_file").perform(context).strip(),
        launch_share_dir,
    )
    sensor_config = _load_sensor_config(config_file, launch_share_dir)

    sensor_launch_file = _resolve_path(
        LaunchConfiguration("sensor_launch_file").perform(context).strip(),
        launch_share_dir,
    ) or sensor_config["sensor_launch_file"]
    if not sensor_launch_file:
        raise RuntimeError(
            "No sensor launch file was configured. Provide config_file or "
            "sensor_launch_file."
        )
    if not os.path.exists(sensor_launch_file):
        raise RuntimeError(
            f"Sensor launch file does not exist: {sensor_launch_file}"
        )

    sensor_launch_arguments = dict(sensor_config["sensor_launch_arguments"])
    sensor_launch_arguments.update(
        _sensor_launch_arguments(
            LaunchConfiguration("sensor_launch_arguments").perform(
                context
            ).strip()
        )
    )

    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(sensor_launch_file),
            launch_arguments=sensor_launch_arguments.items(),
        )
    ]


def generate_launch_description():
    """Build the launch description for sensor stack integration."""
    launch_share_dir = get_package_share_directory("goat_ros_launch")
    default_config_file = os.path.join(
        launch_share_dir,
        "config",
        "sensors.yaml",
    )

    config_file_argument = DeclareLaunchArgument(
        "config_file",
        default_value=default_config_file,
        description="Path to the default sensor wrapper config file.",
    )
    sensor_launch_file_argument = DeclareLaunchArgument(
        "sensor_launch_file",
        default_value="",
        description=(
            "Optional path to a sensor-stack launch file. Overrides the value "
            "from config_file when set."
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
            config_file_argument,
            sensor_launch_file_argument,
            sensor_launch_arguments_argument,
            OpaqueFunction(function=_include_sensor_launch),
        ]
    )
