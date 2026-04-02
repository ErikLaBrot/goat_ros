#pragma once

#include <atomic>
#include <cstdint>
#include <memory>
#include <mutex>
#include <optional>
#include <string>

#include "builtin_interfaces/msg/time.hpp"
#include "goat_vesc/types.hpp"
#include "goat_vesc/vesc_client.hpp"
#include "goat_vesc_ros/msg/vesc_motor_state.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include "std_msgs/msg/float32.hpp"

namespace goat_vesc_ros {

class VescNode : public rclcpp::Node {
public:
  explicit VescNode(const rclcpp::NodeOptions& options = rclcpp::NodeOptions());
  ~VescNode() override;

private:
  enum class CommandMode { Current, Duty, Rpm };

  struct Parameters {
    std::string device_path;
    int baud{115200};
    bool auto_connect{true};
    bool auto_reconnect{true};
    int reconnect_period_ms{1000};
    int imu_poll_interval_ms{10};
    int motor_poll_interval_ms{50};
    int poll_response_timeout_ms{20};
    int query_guard_window_ms{5};
    int command_watchdog_timeout_ms{0};
    std::string command_watchdog_action{"disabled"};
    double max_brake_current{0.0};
    double command_watchdog_brake_current{0.0};
    bool publish_imu{true};
    bool publish_motor_state{true};
    std::string frame_id{"base_link"};
    std::string imu_frame_id;
    std::string command_topic{"cmd/vesc"};
    std::string command_mode{"current"};
  };

  void declare_parameters();
  Parameters load_parameters();
  void validate_parameters(const Parameters& params) const;
  static CommandMode parse_command_mode(const std::string& value);
  static goat_vesc::ControlWatchdogAction parse_watchdog_action(const std::string& value);

  void log_parameter_summary() const;
  void create_interfaces();
  void attempt_initial_connect();
  void reconnect_timer_callback();
  bool sync_connected_state();
  bool attempt_connect(const char* reason, bool throttled);
  void reset_post_connect_state();

  void handle_command(const std_msgs::msg::Float32::SharedPtr message);
  void handle_imu_sample(const goat_vesc::VescIMUData& sample);
  void handle_motor_state_sample(const goat_vesc::VescMotorState& sample);

  sensor_msgs::msg::Imu to_imu_message(const goat_vesc::VescIMUData& sample) const;
  goat_vesc_ros::msg::VescMotorState
  to_motor_state_message(const goat_vesc::VescMotorState& sample) const;
  builtin_interfaces::msg::Time stamp_from_ns(std::uint64_t stamp_ns) const;
  const std::string& resolved_imu_frame_id() const;

  Parameters params_;
  CommandMode command_mode_{CommandMode::Current};

  std::unique_ptr<goat_vesc::VescClient> client_;
  goat_vesc::VescClient::SubscriptionHandle imu_subscription_;
  goat_vesc::VescClient::SubscriptionHandle motor_state_subscription_;

  rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr imu_publisher_;
  rclcpp::Publisher<goat_vesc_ros::msg::VescMotorState>::SharedPtr motor_state_publisher_;
  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr command_subscription_;
  rclcpp::TimerBase::SharedPtr reconnect_timer_;

  mutable std::mutex state_mutex_;
  std::optional<goat_vesc::VescIMUData> latest_imu_;
  std::optional<goat_vesc::VescMotorState> latest_motor_state_;
  std::optional<rclcpp::Time> last_imu_receipt_time_;
  std::optional<rclcpp::Time> last_motor_state_receipt_time_;

  std::atomic_bool connected_{false};
  std::atomic_bool saw_first_imu_{false};
  std::atomic_bool saw_first_motor_state_{false};
};

} // namespace goat_vesc_ros
