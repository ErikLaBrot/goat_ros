"""Helpers for profile-driven GOAT rosbag recording."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re


TRUTHY_VALUES = {"1", "true", "yes", "on"}


class BagProfileError(ValueError):
    """Raised when a bag profile cannot be used."""


def is_truthy(value: str) -> bool:
    """Return whether a launch-style string value is truthy."""
    return str(value).strip().lower() in TRUTHY_VALUES


def load_bag_profile(path: str | Path) -> list[str]:
    """Load topic names from a simple bag profile YAML file."""
    profile_path = Path(path)
    topics: list[str] = []
    in_topics = False
    for raw_line in profile_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "topics:":
            in_topics = True
            continue
        if in_topics and stripped.startswith("- "):
            topics.append(stripped[2:].strip().strip("\"'"))
            continue
        if in_topics and not line.startswith((" ", "\t")):
            in_topics = False

    validate_topics(topics, profile_path)
    return topics


def validate_topics(topics: list[str], source: Path | str = "profile") -> None:
    """Validate topic list loaded from a bag profile."""
    if not topics:
        raise BagProfileError(f"{source}: bag profile must define at least one topic")
    invalid = [topic for topic in topics if not topic.startswith("/")]
    if invalid:
        invalid_topics = ", ".join(invalid)
        raise BagProfileError(f"{source}: topics must be absolute: {invalid_topics}")


def sanitize_name_piece(value: str, default: str = "unnamed") -> str:
    """Sanitize a bag directory name component."""
    candidate = re.sub(r"[^A-Za-z0-9_-]+", "_", str(value).strip()).strip("_")
    candidate = re.sub(r"_+", "_", candidate).lower()
    return candidate or default


def bag_timestamp(now: datetime | None = None) -> str:
    """Return the timestamp prefix used for bag directories."""
    return (now or datetime.now()).strftime("%Y-%m-%d_%H%M%S")


def bag_directory_name(
    robot_name: str,
    app_name: str,
    bag_profile: str,
    bag_note: str = "",
    now: datetime | None = None,
) -> str:
    """Build the deterministic bag directory name."""
    app_piece = sanitize_name_piece(app_name, "app")
    profile_piece = sanitize_name_piece(bag_profile, "")
    pieces = [
        bag_timestamp(now),
        sanitize_name_piece(robot_name, "robot"),
        app_piece,
    ]
    if profile_piece and profile_piece != app_piece:
        pieces.append(profile_piece)
    if bag_note:
        pieces.append(sanitize_name_piece(bag_note, "note"))
    return "_".join(pieces)


def bag_directory(
    bag_root: str | Path,
    robot_name: str,
    app_name: str,
    bag_profile: str,
    bag_note: str = "",
    now: datetime | None = None,
) -> str:
    """Build the full bag output directory path."""
    return str(
        Path(str(bag_root)).expanduser()
        / bag_directory_name(robot_name, app_name, bag_profile, bag_note, now)
    )


def record_command(topics: list[str], bag_dir: str) -> list[str]:
    """Build the ros2 bag record command for a profile."""
    validate_topics(topics)
    return ["ros2", "bag", "record", "-s", "mcap", "-o", bag_dir, *topics]
