"""
Constants

Note: please don't allow code that can raise exceptions in this file.
"""

import os


NICE_BIN = "/usr/bin/nice"
FFMPEG_BIN = os.environ.get("FFMPEG_BIN", "/usr/bin/ffmpeg")

VIDEO_FILE_EXTENSIONS = frozenset(
    {
        ".mp4",
        ".webm",
        ".mkv",
        ".flv",
        ".vob",
        ".ogv",
        ".drc",
        ".gifv",
        ".mng",
        ".avi",
        ".mts",
        ".m2ts",
        ".ts",
        ".mov",
        ".qt",
        ".wmv",
        ".yuv",
        ".rm",
        ".rmvb",
        ".viv",
        ".asf",
        ".amv",
        ".m4p",
        ".m4v",
        ".mpg",
        ".mp2",
        ".mpeg",
        ".mpe",
        ".mpv",
        ".m2v",
        ".svi",
        ".3gp",
        ".3g2",
        ".mxf",
        ".roq",
        ".nsv",
        ".f4v",
        ".f4p",
        ".f4a",
        ".f4b",
        ".divx",
        ".ogx",
        ".evo",
        ".m2p",
        ".ps",
        ".mk3d",
        ".movie",
    }
)
