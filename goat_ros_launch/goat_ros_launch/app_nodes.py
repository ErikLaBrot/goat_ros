"""Shared node builders for deployable GOAT launch apps."""

import os

from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import ComposableNodeContainer
from launch_ros.actions import Node
from launch_ros.descriptions import ComposableNode
from launch_ros.parameter_descriptions import ParameterValue


def common_sensor_arguments():
    """Return launch arguments shared by RealSense and VESC apps."""
    return [
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
        DeclareLaunchArgument(
            "vesc_config_file",
            default_value=os.path.join(
                get_package_share_directory("goat_vesc_ros"),
                "config",
                "goat_vesc.yaml",
            ),
            description="Path to the goat_vesc_ros parameter file.",
        ),
        *static_transform_arguments("camera", "camera_link"),
        *static_transform_arguments("imu", "esc_imu_link"),
    ]


def visual_slam_arguments():
    """Return launch arguments for the Isaac ROS Visual SLAM component."""
    return [
        DeclareLaunchArgument(
            "enable_imu_fusion",
            default_value="false",
            description="Enable external ESC IMU fusion in Visual SLAM.",
        ),
        DeclareLaunchArgument(
            "imu_topic",
            default_value="/imu/data_raw",
            description="ROS topic carrying the ESC IMU as sensor_msgs/msg/Imu.",
        ),
        DeclareLaunchArgument(
            "visual_slam_config_file",
            default_value=os.path.join(
                get_package_share_directory("goat_ros_launch"),
                "config",
                "isaac_ros",
                "goat_d435_visual_slam.yaml",
            ),
            description="Path to the Visual SLAM parameter file.",
        ),
    ]


def teleop_arguments():
    """Return launch arguments for the remote teleop app."""
    return [
        DeclareLaunchArgument(
            "teleop_config_file",
            default_value=os.path.join(
                get_package_share_directory("goat_teleop"),
                "config",
                "goat_joy.yaml",
            ),
            description="Path to the goat_joy parameter file.",
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
    ]


def static_transform_arguments(prefix, child_frame):
    """Declare launch arguments for a static transform from base_link."""
    return [
        DeclareLaunchArgument(
            f"{prefix}_x",
            default_value="0.0",
            description=f"{child_frame} X offset from base_link in meters.",
        ),
        DeclareLaunchArgument(
            f"{prefix}_y",
            default_value="0.0",
            description=f"{child_frame} Y offset from base_link in meters.",
        ),
        DeclareLaunchArgument(
            f"{prefix}_z",
            default_value="0.0",
            description=f"{child_frame} Z offset from base_link in meters.",
        ),
        DeclareLaunchArgument(
            f"{prefix}_roll",
            default_value="0.0",
            description=f"{child_frame} roll from base_link in radians.",
        ),
        DeclareLaunchArgument(
            f"{prefix}_pitch",
            default_value="0.0",
            description=f"{child_frame} pitch from base_link in radians.",
        ),
        DeclareLaunchArgument(
            f"{prefix}_yaw",
            default_value="0.0",
            description=f"{child_frame} yaw from base_link in radians.",
        ),
    ]


def static_transform_node(name, prefix, child_frame):
    """Build a static transform publisher node."""
    return Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name=name,
        arguments=[
            "--x",
            LaunchConfiguration(f"{prefix}_x"),
            "--y",
            LaunchConfiguration(f"{prefix}_y"),
            "--z",
            LaunchConfiguration(f"{prefix}_z"),
            "--roll",
            LaunchConfiguration(f"{prefix}_roll"),
            "--pitch",
            LaunchConfiguration(f"{prefix}_pitch"),
            "--yaw",
            LaunchConfiguration(f"{prefix}_yaw"),
            "--frame-id",
            "base_link",
            "--child-frame-id",
            child_frame,
        ],
    )


def vesc_node():
    """Build the GOAT VESC adapter node."""
    return Node(
        package="goat_vesc_ros",
        executable="vesc_node",
        name="goat_vesc_ros",
        output="screen",
        parameters=[LaunchConfiguration("vesc_config_file")],
    )


def teleop_nodes():
    """Build remote joystick and GOAT command mapper nodes."""
    return [
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
            parameters=[LaunchConfiguration("teleop_config_file")],
        ),
    ]


def realsense_component():
    """Build the composable RealSense camera node."""
    return ComposableNode(
        package="realsense2_camera",
        plugin="realsense2_camera::RealSenseNodeFactory",
        name="camera",
        namespace="camera",
        parameters=[
            {
                "serial_no": LaunchConfiguration("serial_no"),
                "usb_port_id": LaunchConfiguration("usb_port_id"),
                "enable_infra1": True,
                "enable_infra2": True,
                "enable_color": False,
                "enable_depth": False,
                "enable_gyro": False,
                "enable_accel": False,
                "depth_module.emitter_enabled": 0,
                "depth_module.emitter_on_off": False,
                "depth_module.profile": "640x360x90",
                "depth_qos": "SYSTEM_DEFAULT",
            }
        ],
        remappings=[
            ("infra1/image_rect_raw", "/stereo/left/image_rect"),
            ("infra1/camera_info", "/stereo/left/camera_info"),
            ("infra2/image_rect_raw", "/stereo/right/image_rect"),
            ("infra2/camera_info", "/stereo/right/camera_info"),
        ],
    )


def visual_slam_component():
    """Build the composable Isaac ROS Visual SLAM node."""
    return ComposableNode(
        package="isaac_ros_visual_slam",
        plugin="nvidia::isaac_ros::visual_slam::VisualSlamNode",
        name="visual_slam",
        parameters=[
            LaunchConfiguration("visual_slam_config_file"),
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


def isaac_container(components):
    """Build the shared NVIDIA component container."""
    return ComposableNodeContainer(
        package="rclcpp_components",
        executable="component_container_mt",
        name="goat_isaac_container",
        namespace="",
        composable_node_descriptions=components,
        output="screen",
        emulate_tty=True,
    )


def sensor_nodes(include_visual_slam=False):
    """Build sensor-side nodes for GOAT apps."""
    components = [realsense_component()]
    if include_visual_slam:
        components.append(visual_slam_component())

    return [
        vesc_node(),
        static_transform_node(
            "camera_link_static_tf", "camera", "camera_link"
        ),
        static_transform_node("esc_imu_static_tf", "imu", "esc_imu_link"),
        isaac_container(components),
    ]
