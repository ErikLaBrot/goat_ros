"""Launch GOAT's D435-backed Isaac ROS Visual SLAM sensor stack."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def _static_transform_arguments(prefix, child_frame):
    """Declare launch arguments for a static transform."""
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


def _static_transform_node(name, prefix, child_frame):
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


def generate_launch_description():
    """Build the launch description for D435-based Isaac ROS Visual SLAM."""
    launch_share_dir = get_package_share_directory("goat_ros_launch")
    default_visual_slam_config = os.path.join(
        launch_share_dir,
        "config",
        "isaac_ros",
        "goat_d435_visual_slam.yaml",
    )

    serial_number_argument = DeclareLaunchArgument(
        "serial_no",
        default_value="",
        description="Optional RealSense serial number filter.",
    )
    usb_port_id_argument = DeclareLaunchArgument(
        "usb_port_id",
        default_value="",
        description="Optional RealSense USB port filter.",
    )
    enable_imu_fusion_argument = DeclareLaunchArgument(
        "enable_imu_fusion",
        default_value="false",
        description="Enable external ESC IMU fusion in Visual SLAM.",
    )
    imu_topic_argument = DeclareLaunchArgument(
        "imu_topic",
        default_value="/imu/data_raw",
        description="ROS topic carrying the ESC IMU as sensor_msgs/msg/Imu.",
    )
    visual_slam_config_argument = DeclareLaunchArgument(
        "visual_slam_config_file",
        default_value=default_visual_slam_config,
        description="Path to the Visual SLAM parameter file.",
    )

    realsense_node = Node(
        package="realsense2_camera",
        executable="realsense2_camera_node",
        name="camera",
        namespace="camera",
        output="screen",
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

    visual_slam_node = Node(
        package="isaac_ros_visual_slam",
        executable="isaac_ros_visual_slam",
        name="visual_slam",
        output="screen",
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

    camera_static_tf = _static_transform_node(
        "camera_link_static_tf", "camera", "camera_link"
    )
    imu_static_tf = _static_transform_node(
        "esc_imu_static_tf", "imu", "esc_imu_link"
    )

    return LaunchDescription(
        [
            serial_number_argument,
            usb_port_id_argument,
            enable_imu_fusion_argument,
            imu_topic_argument,
            visual_slam_config_argument,
            *_static_transform_arguments("camera", "camera_link"),
            *_static_transform_arguments("imu", "esc_imu_link"),
            camera_static_tf,
            imu_static_tf,
            realsense_node,
            visual_slam_node,
        ]
    )
