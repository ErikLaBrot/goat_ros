"""Launch the Isaac ROS Visual SLAM capability."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "params_file",
                default_value="/etc/goat/config-bundles/teleop-vslam/params/vslam.yaml",
                description="Path to Visual SLAM parameters.",
            ),
            DeclareLaunchArgument(
                "enable_imu_fusion",
                default_value="false",
                description="Enable external ESC IMU fusion.",
            ),
            DeclareLaunchArgument(
                "imu_topic",
                default_value="/imu/data_raw",
                description="Topic carrying IMU messages.",
            ),
            ComposableNodeContainer(
                package="rclcpp_components",
                executable="component_container_mt",
                name="goat_visual_slam_container",
                namespace="",
                output="screen",
                emulate_tty=True,
                composable_node_descriptions=[
                    ComposableNode(
                        package="isaac_ros_visual_slam",
                        plugin="nvidia::isaac_ros::visual_slam::VisualSlamNode",
                        name="visual_slam",
                        parameters=[
                            LaunchConfiguration("params_file"),
                            {
                                "enable_imu_fusion": ParameterValue(
                                    LaunchConfiguration("enable_imu_fusion"),
                                    value_type=bool,
                                )
                            },
                        ],
                        remappings=[
                            ("visual_slam/image_0", "/stereo/left/image_rect"),
                            ("visual_slam/camera_info_0", "/stereo/left/camera_info"),
                            ("visual_slam/image_1", "/stereo/right/image_rect"),
                            ("visual_slam/camera_info_1", "/stereo/right/camera_info"),
                            ("visual_slam/imu", LaunchConfiguration("imu_topic")),
                        ],
                    )
                ],
            ),
        ]
    )

