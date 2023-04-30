import os
from glob import iglob
from pathlib import Path
from subprocess import run, CompletedProcess
from typing import Generator

from dataclasses import dataclass
from enum import Enum

from pymediainfo import MediaInfo

NICE_BIN = "/usr/bin/nice"
FFMPEG_BIN = os.environ.get("FFMPEG_BIN", "/usr/bin/ffmpeg")


@dataclass
class VideoFiles:
    video: Path
    vcs: Path

    @staticmethod
    def new(video: Path) -> "VideoFiles":
        video = Path(video)
        return VideoFiles(video=video, vcs=video.with_suffix(".jpg"))


@dataclass
class TranscodeFiles:
    input: VideoFiles
    output: VideoFiles

    @staticmethod
    def new(video_in: Path) -> "TranscodeFiles":
        video_in = Path(video_in)
        video_out = video_in.with_suffix(".x265.mp4")
        return TranscodeFiles(
            input=VideoFiles.new(video_in), output=VideoFiles.new(video_out)
        )


@dataclass
class TranscodeResult:
    files: TranscodeFiles
    result: CompletedProcess

    def is_ok(self) -> bool:
        return self.result.returncode == 0


@dataclass
class VcsResult:
    video: VideoFiles
    result: CompletedProcess

    def is_ok(self) -> bool:
        return self.result.returncode == 0


def get_videos(directory: Path, recursive=False) -> Generator:
    """Get all video files in a directory

    Parameters
    ----------
    directory : Path
        input directory
    recursive : bool, optional
        recurse sub-directories, by default False

    Yields
    ------
    Generator
        generator of video files
    """

    # TODO: support more file extensions, case insensitivity
    pattern = f"{directory}/**/*.mp4"

    return iglob(pattern, recursive=recursive)


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


class HevcDiscriminantMethods(Enum):
    FAST = "fast"
    ACCURATE = "accurate"
    SEMI_ACCURATE = "semi-accurate"


def get_non_hevc_videos(
    dir: Path,
    recursive=False,
    method: HevcDiscriminantMethods = HevcDiscriminantMethods.FAST,
) -> Generator:
    """Generate paths to non-HEVC files.

    Parameters
    ----------
    dir : str
        directory to search
    recursive : bool, optional
        recurse sub-directories, by default False
    method : HevcDiscriminantMethods, optional
        method to determine encoding, by default HevcDiscriminantMethods.FAST

    Yields
    ------
    Generator
        generator of non-hevc files
    """

    def fast(gen: Generator) -> Generator:
        return (f for f in gen if not f.endswith("x265.mp4"))

    def accurate(gen: Generator) -> Generator:
        return (f for f in gen if not is_hevc(f))

    all_vids = get_videos(dir, recursive=recursive)

    if method == HevcDiscriminantMethods.FAST:
        return fast(all_vids)
    elif method == HevcDiscriminantMethods.ACCURATE:
        return accurate(all_vids)
    elif method == HevcDiscriminantMethods.SEMI_ACCURATE:
        return accurate(fast(all_vids))
    else:
        raise Exception(f"Got a bad value for method: '{method}'")


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
    return TranscodeResult(files, result)


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
    return VcsResult(video, result)
