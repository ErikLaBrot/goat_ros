"""Tests for profile-driven bag recording helpers."""

from datetime import datetime

import pytest

from goat_ros_launch.bag_support import BagProfileError
from goat_ros_launch.bag_support import bag_directory
from goat_ros_launch.bag_support import bag_directory_name
from goat_ros_launch.bag_support import load_bag_profile
from goat_ros_launch.bag_support import record_command
from goat_ros_launch.bag_support import sanitize_name_piece


def test_load_bag_profile_reads_topics(tmp_path):
    profile = tmp_path / "profile.yaml"
    profile.write_text(
        "topics:\n"
        "  - /scan\n"
        "  - /tf\n"
        "  - /cmd/vesc\n",
        encoding="utf-8",
    )

    assert load_bag_profile(profile) == ["/scan", "/tf", "/cmd/vesc"]


def test_load_bag_profile_rejects_relative_topics(tmp_path):
    profile = tmp_path / "profile.yaml"
    profile.write_text("topics:\n  - scan\n", encoding="utf-8")

    with pytest.raises(BagProfileError):
        load_bag_profile(profile)


def test_bag_directory_name_sanitizes_parts():
    now = datetime(2026, 5, 26, 14, 30, 12)
    expected = (
        "2026-05-26_143012_goat_racer_orange_teleop_only_lidar_teleop_"
        "garage_test"
    )

    assert bag_directory_name(
        robot_name="GOAT Racer Orange",
        app_name="teleop_only",
        bag_profile="lidar_teleop",
        bag_note="Garage Test!",
        now=now,
    ) == expected


def test_bag_directory_omits_duplicate_profile():
    now = datetime(2026, 5, 26, 14, 30, 12)

    assert bag_directory(
        "/bags",
        robot_name="goat-racer",
        app_name="vslam",
        bag_profile="vslam",
        now=now,
    ) == "/bags/2026-05-26_143012_goat-racer_vslam"


def test_record_command_uses_mcap_storage():
    assert record_command(["/scan", "/tf"], "/bags/run1") == [
        "ros2",
        "bag",
        "record",
        "-s",
        "mcap",
        "-o",
        "/bags/run1",
        "/scan",
        "/tf",
    ]


def test_sanitize_name_piece_default():
    assert sanitize_name_piece(" ! ", "fallback") == "fallback"
