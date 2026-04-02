from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    config = PathJoinSubstitution(
        [FindPackageShare("goat_vesc_ros"), "config", "goat_vesc.yaml"]
    )

    return LaunchDescription(
        [
            Node(
                package="goat_vesc_ros",
                executable="vesc_node",
                name="goat_vesc_ros",
                output="screen",
                parameters=[config],
            )
        ]
    )
