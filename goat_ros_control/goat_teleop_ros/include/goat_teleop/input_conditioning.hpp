/**
 * @file input_conditioning.hpp
 * @brief Internal helper functions for joystick input conditioning.
 */

#ifndef GOAT_TELEOP__INPUT_CONDITIONING_HPP_
#define GOAT_TELEOP__INPUT_CONDITIONING_HPP_

#include <algorithm>
#include <cmath>

namespace goat_teleop::input_conditioning {

/**
 * @brief Zero small joystick values inside the configured deadband.
 *
 * @param value Raw normalized joystick input.
 * @param deadband Deadband threshold in normalized joystick units.
 * @return The original value when it lies outside the deadband, otherwise
 * `0.0`.
 */
inline double applyDeadband(double value, double deadband) {
  return std::abs(value) <= deadband ? 0.0 : value;
}

/**
 * @brief Apply optional EMA filtering and slew-rate limiting to one axis.
 *
 * @param target Desired normalized joystick value after deadband.
 * @param current Previously conditioned axis value.
 * @param tau_s EMA time constant in seconds. `0.0` disables filtering.
 * @param max_rate Maximum axis change in normalized units per second.
 * `0.0` disables slew limiting.
 * @param dt_s Control loop delta time in seconds.
 * @return The next conditioned axis value.
 */
inline double conditionAxis(double target, double current, double tau_s,
                            double max_rate, double dt_s) {
  double filtered = target;
  if (tau_s > 0.0) {
    const double alpha = dt_s / (tau_s + dt_s);
    filtered = current + (alpha * (target - current));
  }

  if (max_rate <= 0.0) {
    return filtered;
  }

  const double max_delta = max_rate * dt_s;
  return std::clamp(filtered, current - max_delta, current + max_delta);
}

} // namespace goat_teleop::input_conditioning

#endif // GOAT_TELEOP__INPUT_CONDITIONING_HPP_
