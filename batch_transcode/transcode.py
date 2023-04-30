"""
Transcoding.
"""

from pathlib import Path
from subprocess import run
from typing import Generator

from pymediainfo import MediaInfo

from .const import FFMPEG_BIN, NICE_BIN, VIDEO_FILE_EXTENSIONS
from .models import (
    VcsResult,
    VideoFiles,
    TranscodeFiles,
    TranscodeResult,
    HevcDiscriminantMethods,
    HevcDiscriminantMethodException,
)


def get_videos(directory: Path) -> Generator:
    """Get all video files in a directory

    Parameters
    ----------
    directory : Path
        input directory

    Yields
    ------
    Generator
        generator of video files
    """

    return (
        f
        for f in Path(directory).glob("**/*")
        if f.suffix.lower() in VIDEO_FILE_EXTENSIONS
    )


def is_hevc(media_file: Path) -> bool:
    """Whether media file is HEVC encoded.

    Parameters
    ----------
    media_file : Path
        media file to check

    Returns
    -------
    bool
        whether file is HEVC
    """
    return MediaInfo.parse(media_file).video_tracks[0].codec_id in ["hev1", "hvc1"]


def get_non_hevc_videos(
    directory: Path,
    method: HevcDiscriminantMethods = HevcDiscriminantMethods.FAST,
) -> Generator:
    """Generate paths to non-HEVC files.

    Parameters
    ----------
    directory : Path
        directory to search
    method : HevcDiscriminantMethods, optional
        method to determine encoding, by default HevcDiscriminantMethods.FAST

    Yields
    ------
    Generator
        generator of non-hevc files
    """

    def fast(gen: Generator) -> Generator:
        return (f for f in gen if not str(f).endswith("x265.mp4"))

    def accurate(gen: Generator) -> Generator:
        return (f for f in gen if not is_hevc(f))

    all_vids = get_videos(directory)

    if method == HevcDiscriminantMethods.FAST:
        return fast(all_vids)
    if method == HevcDiscriminantMethods.ACCURATE:
        return accurate(all_vids)
    if method == HevcDiscriminantMethods.SEMI_ACCURATE:
        return accurate(fast(all_vids))

    raise HevcDiscriminantMethodException(f"Got a bad value for method: '{method}'")


def transcode_vid(files: TranscodeFiles, run_check=True) -> TranscodeResult:
    """Transcode video using FFMpeg

    Parameters
    ----------
    files : TranscodeFiles
        file to transcode

    Returns
    -------
    TranscodeResult
        transcode results
    """

    cmd = [
        NICE_BIN,
        "--adjustment=20",
        FFMPEG_BIN,
        "-hide_banner",
        "-n",
        "-i",
        str(files.input.video),
        "-c:v",
        "libx265",
        "-c:a",
        "aac",
        "-strict",
        "-2",
        str(files.output.video),
    ]

    result = run(cmd, check=run_check, capture_output=False)
    return TranscodeResult(files=files, result=result)


def make_contact_sheet(video: VideoFiles, run_check: bool = True) -> VcsResult:
    """Make contact sheet for video file.

    Parameters
    ----------
    video : VideoFiles
        video files

    Returns
    -------
    VcsResult
        vcs result
    """
    cmd = f'nice --adjustment=20 vcsi "{video.video}" -t -w 850 -g 3x5 -o "{video.vcs}"'
    result = run(cmd, shell=True, check=run_check)
    return VcsResult(video=video, result=result)
