#include "goat_teleop/input_conditioning.hpp"

#include <gtest/gtest.h>

namespace {

using goat_teleop::input_conditioning::applyDeadband;
using goat_teleop::input_conditioning::conditionAxis;

TEST(InputConditioningTest, DeadbandZerosCenteredNoise) {
  EXPECT_DOUBLE_EQ(applyDeadband(0.04, 0.05), 0.0);
  EXPECT_DOUBLE_EQ(applyDeadband(-0.05, 0.05), 0.0);
}

TEST(InputConditioningTest, DeadbandPreservesValuesOutsideThreshold) {
  EXPECT_DOUBLE_EQ(applyDeadband(0.051, 0.05), 0.051);
  EXPECT_DOUBLE_EQ(applyDeadband(-0.2, 0.05), -0.2);
}

TEST(InputConditioningTest, ConditionAxisAppliesExpectedEmaResponse) {
  EXPECT_NEAR(conditionAxis(1.0, 0.0, 0.18, 0.0, 0.02), 0.1, 1e-9);
}

TEST(InputConditioningTest, ConditionAxisSkipsEmaWhenTauIsZero) {
  EXPECT_DOUBLE_EQ(conditionAxis(0.75, 0.1, 0.0, 0.0, 0.02), 0.75);
}

TEST(InputConditioningTest, ConditionAxisAppliesPositiveSlewLimit) {
  EXPECT_NEAR(conditionAxis(1.0, 0.0, 0.0, 2.0, 0.02), 0.04, 1e-9);
}

TEST(InputConditioningTest, ConditionAxisAppliesNegativeSlewLimit) {
  EXPECT_NEAR(conditionAxis(-1.0, 0.0, 0.0, 3.0, 0.02), -0.06, 1e-9);
}

TEST(InputConditioningTest, ConditionAxisCombinesEmaAndSlewLimit) {
  EXPECT_NEAR(conditionAxis(1.0, 0.0, 0.18, 2.0, 0.02), 0.04, 1e-9);
}

} // namespace
