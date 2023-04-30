import os
from glob import iglob
from pathlib import Path
from subprocess import run

from pymediainfo import MediaInfo

NICE_BIN = "/usr/bin/nice"
FFMPEG_BIN = os.environ.get("FFMPEG_BIN", "/usr/bin/ffmpeg")


def is_hevc(media_file: Path):
    return MediaInfo.parse(media_file).video_tracks[0].codec_id in ["hev1", "hvc1"]


def get_non_hevc_mp4(pattern: str):
    return (
        ff
        for ff in (
            f for f in iglob(pattern, recursive=True) if not f.endswith("x265.mp4")
        )
        if not is_hevc(ff)
    )


def transcode_vid(infile: Path) -> Path:
    outfile = Path(infile).with_suffix(".x265.mp4")
    cmd = [
        NICE_BIN,
        "--adjustment=20",
        FFMPEG_BIN,
        "-hide_banner",
        "-n",
        "-i",
        str(infile),
        "-c:v",
        "libx265",
        "-c:a",
        "aac",
        "-strict",
        "-2",
        str(outfile),
    ]

    run(cmd, check=True, capture_output=False)
    return outfile

def make_contact_sheet(infile: Path) -> Path:
    outfile = Path(infile).with_suffix(".jpg")
    cmd = f'nice --adjustment=20 vcsi "{infile}" -t -w 850 -g 3x5 -o "{outfile}"'
    run(cmd, shell=True, check=True)
    return outfile


if __name__ == "__main__":
    pass