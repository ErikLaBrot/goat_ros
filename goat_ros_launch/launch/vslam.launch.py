"""Launch GOAT sensors with composable Isaac ROS Visual SLAM."""

from launch import LaunchDescription

from goat_ros_launch.app_nodes import common_sensor_arguments
from goat_ros_launch.app_nodes import sensor_nodes
from goat_ros_launch.app_nodes import visual_slam_arguments
from goat_ros_launch.launch_bags import bag_launch_arguments
from goat_ros_launch.launch_bags import bag_recorder_include


def generate_launch_description():
    """Build the launch description for VESC, RealSense, and VSLAM."""
    return LaunchDescription(
        [
            *common_sensor_arguments(),
            *visual_slam_arguments(),
            *bag_launch_arguments(default_profile="vslam"),
            *sensor_nodes(include_visual_slam=True),
            bag_recorder_include(app_name="vslam"),
        ]
    )
