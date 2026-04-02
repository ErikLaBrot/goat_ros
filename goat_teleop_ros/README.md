# goat_teleop

`goat_teleop` is a minimal ROS 2 Humble joystick teleop package for GOAT. It subscribes to `sensor_msgs/msg/Joy` on `/joy` and publishes `goat_vesc_ros/msg/VescControlCommand` on `cmd/vesc` for every joystick update. While the configured enable button is held it publishes scaled drive duty; otherwise it publishes a zero-duty command. This smoke-test path still only maps joystick throttle into drive duty, but it now publishes a fixed servo position alongside the drive command.

## Custom Messages

This package does not define custom messages, but it publishes `goat_vesc_ros/msg/VescControlCommand`.

## Launch Files

| Launch File | Purpose | Notes |
| --- | --- | --- |
| `launch/goat_joy.launch.py` | Starts `joy_node` plus the `goat_joy` teleop node for an Xbox smoke test. | Loads `config/goat_joy.yaml`, reads `/dev/input/js0` by default, and publishes `cmd/vesc`. |

## Example Startup

Update `config/goat_joy.yaml` if you need different joystick mappings, then start the node from the `goat_racer` repo root:

```bash
cd ../goat_racer
scripts/ros up
docker compose -f docker/compose.yaml exec ros-humble bash -lc \
  "source /opt/ros/humble/setup.bash && \
   source /workspace/goat_racer/ros_ws/install/setup.bash && \
   ros2 launch goat_teleop goat_joy.launch.py"
```

The default config uses:

- `throttle_axis: 1`
- `enable_button: 4`
- `command_scale: 0.10`
- `servo_position: 0.5`
- `command_topic: cmd/vesc`

You can override the joystick device or deadzone at launch time:

```bash
docker compose -f docker/compose.yaml exec ros-humble bash -lc \
  "source /opt/ros/humble/setup.bash && \
   source /workspace/goat_racer/ros_ws/install/setup.bash && \
   ros2 launch goat_teleop goat_joy.launch.py joy_dev:=/dev/input/js1 deadzone:=0.02"
```
