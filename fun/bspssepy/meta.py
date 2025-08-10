"""This script contains metadata for the bspssepy package."""

# bspssepy/meta.py
from datetime import datetime

ver_num = "0.6"
build_num = 1


def current_timestamp():
    """Returns the current timestamp in the format YYYY-MM-DD HH:MM:SS."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
