"""This script contains metadata for the bspssepy package."""
# bspssepy/meta.py
from datetime import datetime

VER_NUM = "0.5"
BUILD_NUM = 1


def current_timestamp():
    """Returns the current timestamp in the format YYYY-MM-DD HH:MM:SS."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
