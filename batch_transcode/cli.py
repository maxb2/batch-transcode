"""
Batch Transcode CLI
"""

import os
from pathlib import Path

import typer

from batch_transcode.transcode import (
    get_non_hevc_videos,
    get_videos,
    make_contact_sheet,
    transcode_vid,
)

from .models import TranscodeFiles, VideoFiles, HevcDiscriminantMethods

app = typer.Typer(
    help="""A cli to transcode video files and make video contact sheets.

    NOTE: currently only supports transcoding to x265. 
"""
)


@app.command(help="Transcode video file.")
def transcode(
    video_path: Path = typer.Argument(..., help="Video file to transcode."),
    delete_source: bool = typer.Option(
        False, "-d", "--delete-source", help="Delete source file after transcoding."
    ),
):
    """Transcode video file.

    Parameters
    ----------
    video_path : Path, optional
        video file to transcode
    delete_source : bool, optional
        delete source file after transcoding, by default False
    """
    result = transcode_vid(TranscodeFiles.new(video_path))

    if delete_source:
        typer.echo(f"Removing {result.files.input}...")
        os.remove(result.files.input.video)
        os.remove(result.files.input.vcs)


@app.command(help="Create video contact sheet.")
def vcs(
    video_path: Path = typer.Argument(
        ..., help="Video file or folder for which to create contact sheets."
    ),
    overwrite: bool = typer.Option(
        False, "-o", "--overwrite", help="Replace existing files."
    ),
):
    """Create video contact sheet.

    Parameters
    ----------
    video_path : Path, optional
        Video file or folder for which to create contact sheets
    overwrite : bool, optional
        Replace existing files, by default False

    Raises
    ------
    Exception
        Path or file doesn't exist
    """
    video_path = Path(video_path)

    if video_path.is_file():
        make_contact_sheet(VideoFiles.new(video_path))

    elif video_path.is_dir():
        for vid in get_videos(video_path):
            video_files = VideoFiles.new(vid)

            if not overwrite and video_files.vcs.is_file():
                continue

            make_contact_sheet(video_files)
    else:
        raise FileNotFoundError("Path or file doesn't exist: {video_path}")


@app.command(help="Batch transcoding.")
def batch(
    directory: Path = typer.Argument(
        ..., help="Directory containing videos to transcode."
    ),
    move_source: Path = typer.Option(
        None, "-m", "--move-source", help="Move source files after transcoding."
    ),
    delete_source: bool = typer.Option(
        False, "-d", "--delete-source", help="Delete source files after transcoding."
    ),
):
    """Batch Transcoding.

    Parameters
    ----------
    directory : Path, optional
        Directory containing videos to transcode
    move_source : Path, optional
        Move source files after transcoding, by default None
    delete_source : bool, optional
        Delete source files after transcoding, by default False

    Raises
    ------
    typer.Abort
        Cannot use --delete-source/-d and --move-source/-m at the same time.
    Exception
        Path doesn't exist.
    """
    if delete_source and move_source is not None:
        typer.echo(
            "Cannot use --delete-source/-d and --move-source/-m at the same time.",
            color="yellow",
            err=True,
        )
        raise typer.Abort

    if move_source is not None and not move_source.is_dir():
        raise FileNotFoundError(f"{move_source} is not an existing directory!")

    for vid_path in get_non_hevc_videos(directory):
        transcode_files = TranscodeFiles.new(vid_path)

        if transcode_files.output.video.is_file():
            # output file exists, so we skip
            continue

        transcode_result = transcode_vid(transcode_files)
        make_contact_sheet(transcode_result.files.output)

        if move_source is not None:
            typer.echo(f"Moving {transcode_result.files.input} to {move_source}...")
            # raise NotImplementedError
            moved_video = VideoFiles.new(
                move_source.joinpath(transcode_result.files.input.video.name)
            )
            os.rename(transcode_result.files.input.video, moved_video.video)
            if transcode_result.files.input.vcs.is_file():
                os.rename(transcode_result.files.input.vcs, moved_video.vcs)

        if delete_source:
            typer.echo(f"Removing {transcode_files}...")
            os.remove(transcode_result.files.input.video)
            os.remove(transcode_result.files.input.vcs)


@app.command(help="Find non-HEVC video files.")
def find(
    directory: Path = typer.Argument(...),
    method: HevcDiscriminantMethods = typer.Option(
        HevcDiscriminantMethods.FAST.value,
        help="Method for determining if the file is HEVC encoded.",
    ),
    limit: int = typer.Option(None, help="Limit the number of files to print."),
):
    """Find non-HEVC video files.

    Parameters
    ----------
    directory : Path, optional
        directory to search, by default typer.Argument(...)
    method : HevcDiscriminantMethods, optional
        Method for determining if the file is HEVC encoded, by default HevcDiscriminantMethods.FAST
    limit : int, optional
        Limit the number of files to print, by default None
    """
    vids = get_non_hevc_videos(directory, method=method)
    _iter = 1
    for vid in vids:
        if limit is not None and _iter > limit:
            break
        typer.echo(vid)
        _iter += 1


if __name__ == "__main__":
    app()
