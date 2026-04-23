#include "goat_teleop/goat_joy.hpp"

#include <chrono>
#include <cstdint>
#include <condition_variable>
#include <cstddef>
#include <memory>
#include <mutex>
#include <optional>
#include <string>
#include <thread>
#include <utility>
#include <vector>

#include <gtest/gtest.h>

#include "goat_vesc_ros/msg/vesc_control_command.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/joy.hpp"

namespace {

using goat_vesc_ros::msg::VescControlCommand;
using sensor_msgs::msg::Joy;
using namespace std::chrono_literals;

class CommandCapture {
public:
  void callback(const VescControlCommand::SharedPtr message) {
    {
      std::lock_guard<std::mutex> lock(mutex_);
      last_message_ = *message;
      ++message_count_;
    }
    condition_.notify_all();
  }

  bool waitForCount(std::size_t expected_count, std::chrono::milliseconds timeout,
                    VescControlCommand &message) {
    std::unique_lock<std::mutex> lock(mutex_);
    const bool ready = condition_.wait_for(lock, timeout, [&]() {
      return message_count_ >= expected_count;
    });
    if (!ready || !last_message_.has_value()) {
      return false;
    }

    message = *last_message_;
    return true;
  }

private:
  std::mutex mutex_;
  std::condition_variable condition_;
  std::optional<VescControlCommand> last_message_;
  std::size_t message_count_{0};
};

class GoatJoyTest : public ::testing::Test {
protected:
  static void SetUpTestSuite() {
    int argc = 0;
    char **argv = nullptr;
    rclcpp::init(argc, argv);
  }

  static void TearDownTestSuite() { rclcpp::shutdown(); }

  void SetUp() override {
    control_node_ = std::make_shared<goat_teleop::GoatJoy>(makeNodeOptions());
    test_node_ = std::make_shared<rclcpp::Node>("goat_joy_test_node");

    command_subscription_ =
        test_node_->create_subscription<VescControlCommand>(
            command_topic_, rclcpp::QoS(10),
            [this](const VescControlCommand::SharedPtr message) {
              capture_.callback(message);
            });
    joy_publisher_ =
        test_node_->create_publisher<Joy>("/joy", rclcpp::SensorDataQoS());

    executor_.add_node(control_node_);
    executor_.add_node(test_node_);
  }

  void TearDown() override {
    executor_.cancel();
    executor_.remove_node(control_node_);
    executor_.remove_node(test_node_);
    command_subscription_.reset();
    joy_publisher_.reset();
    test_node_.reset();
    control_node_.reset();
  }

  rclcpp::NodeOptions makeNodeOptions() const {
    std::vector<rclcpp::Parameter> parameters{
        {"throttle_axis", 2},
        {"steering_axis", 0},
        {"enable_button", 1},
        {"command_scale", 0.30},
        {"invert_throttle", true},
        {"invert_steering", false},
        {"servo_center", 0.5},
        {"servo_amplitude", 0.2},
        {"deadband", 0.0},
        {"steer_tau_s", 0.0},
        {"throttle_tau_s", 0.0},
        {"max_steer_rate", 0.0},
        {"max_throttle_rate", 0.0},
        {"publish_epsilon", 0.0},
        {"control_rate_hz", 100.0},
        {"command_topic", command_topic_},
    };
    return rclcpp::NodeOptions().parameter_overrides(parameters);
  }

  void publishJoy(const std::vector<float> &axes, const std::vector<int32_t> &buttons) {
    Joy message;
    message.axes = axes;
    message.buttons = buttons;
    joy_publisher_->publish(message);
  }

  bool waitForMessage(std::size_t expected_count, VescControlCommand &message,
                      std::chrono::milliseconds timeout = 500ms) {
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    while (std::chrono::steady_clock::now() < deadline) {
      executor_.spin_some();
      if (capture_.waitForCount(expected_count, 10ms, message)) {
        return true;
      }
      std::this_thread::sleep_for(5ms);
    }
    return false;
  }

  const std::string command_topic_{"/test/cmd/vesc"};
  CommandCapture capture_;
  rclcpp::executors::SingleThreadedExecutor executor_;
  std::shared_ptr<goat_teleop::GoatJoy> control_node_;
  rclcpp::Node::SharedPtr test_node_;
  rclcpp::Publisher<Joy>::SharedPtr joy_publisher_;
  rclcpp::Subscription<VescControlCommand>::SharedPtr command_subscription_;
};

TEST_F(GoatJoyTest, PublishesConfiguredAxesAndScalesWhenEnabled) {
  publishJoy({0.5F, 0.0F, -0.4F}, {0, 1});

  VescControlCommand message;
  ASSERT_TRUE(waitForMessage(1, message));
  EXPECT_EQ(message.drive_mode, VescControlCommand::MODE_DUTY);
  EXPECT_FLOAT_EQ(message.drive_value, 0.12F);
  EXPECT_FLOAT_EQ(message.servo_position, 0.6F);
}

TEST_F(GoatJoyTest, ReleasingDeadmanPublishesNeutralCommand) {
  publishJoy({0.5F, 0.0F, -0.4F}, {0, 1});

  VescControlCommand enabled_message;
  ASSERT_TRUE(waitForMessage(1, enabled_message));
  EXPECT_FLOAT_EQ(enabled_message.drive_value, 0.12F);
  EXPECT_FLOAT_EQ(enabled_message.servo_position, 0.6F);

  publishJoy({0.5F, 0.0F, -0.4F}, {0, 0});

  VescControlCommand disabled_message;
  ASSERT_TRUE(waitForMessage(2, disabled_message));
  EXPECT_FLOAT_EQ(disabled_message.drive_value, 0.0F);
  EXPECT_FLOAT_EQ(disabled_message.servo_position, 0.5F);
}

TEST_F(GoatJoyTest, PublishesOnConfiguredCommandTopic) {
  publishJoy({-0.25F, 0.0F, 0.8F}, {0, 1});

  VescControlCommand message;
  ASSERT_TRUE(waitForMessage(1, message));
  EXPECT_FLOAT_EQ(message.drive_value, -0.24F);
  EXPECT_FLOAT_EQ(message.servo_position, 0.45F);
}

} // namespace
