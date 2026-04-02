# goat_vesc_ros

`goat_vesc_ros` is a thin ROS 2 Humble wrapper around the core `goat_vesc` library. It owns one `goat_vesc::VescClient`, connects to the controller, publishes VESC telemetry into ROS topics, and accepts a single scalar command topic for current, duty-cycle, or RPM control.

## Custom Messages

| Message | Purpose | Fields |
| --- | --- | --- |
| `goat_vesc_ros/msg/VescMotorState` | Publishes the latest decoded motor-state telemetry from the VESC. | `header`, `rpm`, `current_motor`, `current_in`, `duty_cycle`, `vin`, `temp_motor`, `temp_fet`, `tachometer`, `tachometer_abs`, `fault_code` |

## Launch Files

| Launch File | Purpose | Notes |
| --- | --- | --- |
| `launch/goat_vesc.launch.py` | Starts the `vesc_node` ROS node with the package default parameter file. | Loads `config/goat_vesc.yaml` and runs the node as `goat_vesc_ros`. |
| `launch/goat_vesc_duty_smoke.launch.py` | Starts the `vesc_node` ROS node with the default config plus a duty-mode smoke-test overlay. | Loads `config/goat_vesc.yaml` first, then `config/goat_vesc_duty_smoke.yaml`. |

## Example Startup

Update `config/goat_vesc.yaml` so `device_path` points at the correct VESC serial device, then start the node from the `goat_racer` repo root:

```bash
cd ../goat_racer
scripts/ros up
docker compose -f docker/compose.yaml exec ros-humble bash -lc \
  "source /opt/ros/humble/setup.bash && \
   source /workspace/goat_racer/ros_ws/install/setup.bash && \
   ros2 launch goat_vesc_ros goat_vesc.launch.py"
```

For the Xbox duty-mode smoke test, keep the real serial `device_path` in `config/goat_vesc.yaml` and use the dedicated smoke launch:

```bash
docker compose -f docker/compose.yaml exec ros-humble bash -lc \
  "source /opt/ros/humble/setup.bash && \
   source /workspace/goat_racer/ros_ws/install/setup.bash && \
   ros2 launch goat_vesc_ros goat_vesc_duty_smoke.launch.py"
```
