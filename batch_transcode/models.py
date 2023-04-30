"""
Models
"""

from pathlib import Path
from dataclasses import dataclass
from subprocess import CompletedProcess
from enum import Enum


@dataclass
class VideoFiles:
    """Video Files"""

    video: Path
    vcs: Path

    @staticmethod
    def new(video: Path) -> "VideoFiles":
        """Create new VideoFiles with sane defaults.

        Parameters
        ----------
        video : Path
            video file path

        Returns
        -------
        VideoFiles
            video files
        """
        video = Path(video)
        return VideoFiles(video=video, vcs=Path(f"{video}.jpg"))


@dataclass
class TranscodeFiles:
    """Transcoding Files"""

    input: VideoFiles
    output: VideoFiles

    @staticmethod
    def new(video_in: Path) -> "TranscodeFiles":
        """Create new TranscodeFiles with sane defaults.

        Parameters
        ----------
        video_in : Path
            input video path

        Returns
        -------
        TranscodeFiles
            transcode files
        """
        video_in = Path(video_in)
        video_out = video_in.with_suffix(".x265.mp4")
        return TranscodeFiles(
            input=VideoFiles.new(video_in), output=VideoFiles.new(video_out)
        )


@dataclass
class AbstractResult:
    """Abstract Result"""

    result: CompletedProcess

    def is_ok(self) -> bool:
        """Check if process was successful.

        Returns
        -------
        bool
            whether process succeeded
        """
        return self.result.returncode == 0


@dataclass
class TranscodeResult(AbstractResult):
    """Transcoding process result"""

    files: TranscodeFiles


@dataclass
class VcsResult(AbstractResult):
    """Video contact sheet process result"""

    video: VideoFiles


class HevcDiscriminantMethods(Enum):
    """HEVC Discrimination Methods"""

    FAST = "fast"
    ACCURATE = "accurate"
    SEMI_ACCURATE = "semi-accurate"


class HevcDiscriminantMethodException(Exception):
    """HevcDiscriminantMethodException"""
