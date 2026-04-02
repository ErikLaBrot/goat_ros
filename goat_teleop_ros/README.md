# goat_teleop

`goat_teleop` is a minimal ROS 2 Humble joystick teleop package for GOAT. It subscribes to `sensor_msgs/msg/Joy` on `/joy` and publishes `geometry_msgs/msg/Twist` on `/cmd_vel`, mapping `linear.x` to throttle and `angular.z` to steering while the configured enable button is held.

## Custom Messages

This package does not define any custom messages.

## Launch Files

| Launch File | Purpose | Notes |
| --- | --- | --- |
| `launch/goat_joy.launch.py` | Starts the `goat_joy` teleop node with the package default parameter file. | Loads `config/goat_joy.yaml` and runs the node as `goat_joy`. |

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
