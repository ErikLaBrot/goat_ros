"""Launch the GOAT joystick teleop capability."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "params_file",
                default_value="/etc/goat/config-bundles/teleop/params/teleop.yaml",
                description="Path to the goat_teleop parameter file.",
            ),
            DeclareLaunchArgument(
                "joy_dev",
                default_value="/dev/input/js0",
                description="Joystick device passed to joy_node.",
            ),
            DeclareLaunchArgument(
                "deadzone",
                default_value="0.05",
                description="Joystick deadzone passed to joy_node.",
            ),
            Node(
                package="joy",
                executable="joy_node",
                name="joy_node",
                output="screen",
                parameters=[
                    {
                        "dev": LaunchConfiguration("joy_dev"),
                        "deadzone": ParameterValue(
                            LaunchConfiguration("deadzone"),
                            value_type=float,
                        ),
                    }
                ],
            ),
            Node(
                package="goat_teleop",
                executable="goat_joy",
                name="goat_joy",
                output="screen",
                parameters=[LaunchConfiguration("params_file")],
            ),
        ]
    )
