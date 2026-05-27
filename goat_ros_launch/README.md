# goat_ros_launch

## Purpose

`goat_ros_launch` owns the public GOAT launch app surface. Each launch file is
intended to work both as a dev-container tool with `ros2 launch` and as a
deployable app target selected by `config/deploy/robot_app.yaml` in
`goat-racer`.

## Launch Apps

- `sensors.launch.py`: Starts `goat_vesc_ros` plus the D435 RealSense camera in
  a multithreaded component container.
- `teleop.launch.py`: Starts the workstation-side joystick client with
  `joy_node` and `goat_teleop`, publishing `cmd/vesc` over ROS.
- `teleop_only.launch.py`: Starts VESC command reception, joystick teleop, and
  the LD19 lidar for manual lidar/teleop runs.
- `lidar_bag_demo.launch.py`: Starts only the LD19 lidar plus optional bag
  recording for quick RViz and bag download demos.
- `vslam.launch.py`: Starts sensors plus composable Isaac ROS Visual SLAM in
  the same NVIDIA component container.
- `laser_driver.launch.py`: Starts the GOAT LD19 lidar driver.
- `teleop_vslam.launch.py`: Starts the robot-side remote teleop target plus
  VSLAM. The robot runs VESC command reception, RealSense, and Visual SLAM;
  the joystick client runs separately on the workstation.

## Runtime Shape

NVIDIA-related runtime nodes are composed into `component_container_mt`:

- `/camera/camera` from `realsense2_camera::RealSenseNodeFactory`
- `/visual_slam` from `nvidia::isaac_ros::visual_slam::VisualSlamNode`

Robot-side control keeps the external node and topic names expected by deploy
health checks:

- `/goat_vesc_ros`
- `/cmd/vesc`
- `/stereo/left/image_rect`
- `/stereo/left/camera_info`
- `/stereo/right/image_rect`
- `/stereo/right/camera_info`

## Launch Arguments

Sensor and VSLAM apps accept:

- `serial_no`: Optional RealSense serial number filter.
- `usb_port_id`: Optional RealSense USB port filter.
- `vesc_config_file`: Path to the `goat_vesc_ros` parameter file.
- `camera_{x,y,z,roll,pitch,yaw}`: Static `base_link -> camera_link`
  transform values.
- `imu_{x,y,z,roll,pitch,yaw}`: Static `base_link -> esc_imu_link` transform
  values.
- `enable_imu_fusion`: Enable external ESC IMU fusion in Visual SLAM.
- `imu_topic`: Topic carrying the ESC IMU as `sensor_msgs/msg/Imu`.
- `visual_slam_config_file`: Path to the Isaac ROS Visual SLAM parameter file.

The workstation teleop client accepts:

- `teleop_config_file`: Path to the `goat_teleop` parameter file.
- `joy_dev`: Joystick device passed to `joy_node`.
- `deadzone`: Joystick deadzone passed to `joy_node`.

Recordable app launch files accept:

- `record_bag`: Set to `true` to start `ros2 bag record` with the app.
- `bag_profile`: Installed profile in `config/bag_profiles`.
- `bag_note`: Optional note appended to the bag directory name.
- `bag_root`: Persistent bag root, defaulting to `/workspaces/goat_data/bags/raw`.
- `robot_name`: Robot name included in bag directory names.

## Example Usage

```bash
ros2 launch goat_ros_launch sensors.launch.py
ros2 launch goat_ros_launch teleop.launch.py
ros2 launch goat_ros_launch vslam.launch.py
ros2 launch goat_ros_launch teleop_vslam.launch.py
```

For remote manual control, run `teleop_vslam.launch.py` on the robot and run
the teleop client on the workstation:

```bash
ros2 launch goat_ros_launch teleop.launch.py
```

Enable external ESC IMU fusion in the VSLAM app:

```bash
ros2 launch goat_ros_launch vslam.launch.py enable_imu_fusion:=true
```

Select a specific camera or measured transform:

```bash
ros2 launch goat_ros_launch vslam.launch.py \
  serial_no:=_0123456789 \
  camera_x:=0.10 camera_z:=0.22 camera_yaw:=1.57
```

Record a teleop/lidar run:

```bash
ros2 launch goat_ros_launch teleop_only.launch.py \
  record_bag:=true \
  bag_profile:=lidar_teleop \
  bag_note:=garage_test \
  robot_name:=goat-racer-orange
```

Run the lidar-only bag demo:

```bash
ros2 launch goat_ros_launch lidar_bag_demo.launch.py \
  record_bag:=true \
  bag_profile:=lidar_demo \
  bag_note:=show_and_tell
```

Replay a recorded bag with `/clock`:

```bash
ros2 launch goat_ros_launch replay_bag.launch.py \
  bag_path:=/data/goat/bags/raw/<bag-directory> \
  use_clock:=true
```

## Rules

- Keep this package launch/config only.
- Treat launch files in this package as app entrypoints, not private wrappers.
- Keep NVIDIA RealSense and Visual SLAM nodes composable.
- Keep deploy wiring generic: select one launch file plus launch arguments.
- Keep recording profile-driven so launch files do not duplicate topic lists.
