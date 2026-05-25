"""Launch the RealSense camera capability."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "params_file",
                default_value="/etc/goat/config-bundles/teleop-vslam/params/realsense.yaml",
                description="Path to RealSense parameters.",
            ),
            DeclareLaunchArgument(
                "serial_no",
                default_value="",
                description="Optional RealSense serial number filter.",
            ),
            DeclareLaunchArgument(
                "usb_port_id",
                default_value="",
                description="Optional RealSense USB port filter.",
            ),
            ComposableNodeContainer(
                package="rclcpp_components",
                executable="component_container_mt",
                name="goat_realsense_container",
                namespace="",
                output="screen",
                emulate_tty=True,
                composable_node_descriptions=[
                    ComposableNode(
                        package="realsense2_camera",
                        plugin="realsense2_camera::RealSenseNodeFactory",
                        name="camera",
                        namespace="camera",
                        parameters=[
                            LaunchConfiguration("params_file"),
                            {
                                "serial_no": LaunchConfiguration("serial_no"),
                                "usb_port_id": LaunchConfiguration("usb_port_id"),
                            },
                        ],
                        remappings=[
                            ("infra1/image_rect_raw", "/stereo/left/image_rect"),
                            ("infra1/camera_info", "/stereo/left/camera_info"),
                            ("infra2/image_rect_raw", "/stereo/right/image_rect"),
                            ("infra2/camera_info", "/stereo/right/camera_info"),
                        ],
                    )
                ],
            ),
        ]
    )

