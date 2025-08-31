import argparse
import os
import subprocess
from pathlib import Path

from .core import trim_video

__all__ = ["main", "list_video_files"]


VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".mov",
    ".avi",
    ".webm",
    ".flv",
    ".wmv",
    ".m4v",
}


def list_video_files(root_directory: str) -> list[str]:
    """
    Recursively collect video files beneath root_directory.
    Returns absolute paths as strings, sorted case-insensitively.
    """
    root = Path(root_directory)
    files: list[str] = []
    if not root.exists():
        return files
    for dirpath, _dirnames, filenames in os.walk(root):
        for filename in filenames:
            ext = Path(filename).suffix.lower()
            if ext in VIDEO_EXTENSIONS:
                files.append(str(Path(dirpath) / filename))
    files.sort(key=lambda p: p.lower())
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Trim a video from a given start time to a given end time."
    )
    parser.add_argument("-i", "--input", help="The video file to trim.")
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        default=None,
        help=(
            "Optional output filename. If omitted, will use '<input>_trim_<start>-<end><ext>'."
        ),
    )
    parser.add_argument(
        "-s",
        "--start",
        required=True,
        help="The start time of the trim (in seconds or hh:mm:ss format).",
    )
    parser.add_argument(
        "-e",
        "--end",
        required=True,
        help="The end time of the trim (in seconds or hh:mm:ss format).",
    )
    parser.add_argument(
        "-d",
        "--directory",
        default=os.getcwd(),
        help="The directory to browse for the video file. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--reencode",
        action="store_true",
        help="Re-encode the video for frame-accurate trimming.",
    )

    args = parser.parse_args()

    input_path = args.input
    if not input_path:
        # Lazy import interactive dependencies only when needed
        from InquirerPy import inquirer
        from InquirerPy.validator import PathValidator

        # Try fuzzy file picking first
        try:
            base_dir = args.directory or os.getcwd()
            files = list_video_files(base_dir)
            if files:
                # Show relative names for readability, keep absolute as value
                base_dir_path = Path(base_dir)
                choices = []
                for f in files:
                    fp = Path(f)
                    try:
                        name = str(fp.relative_to(base_dir_path))
                    except ValueError:
                        name = f
                    choices.append({"name": name, "value": f})
                input_path = inquirer.fuzzy(
                    message="Type to fuzzy-search your video file:",
                    choices=choices,
                    default=None,
                    max_height="70%",
                ).execute()
            else:
                # Fallback to path picker if no files discovered
                input_path = inquirer.filepath(
                    message="Select a video file to trim:",
                    default=base_dir,
                    validate=PathValidator(
                        is_file=True, message="Input must be a file"
                    ),
                    only_files=False,
                ).execute()
        except (ImportError, OSError, RuntimeError):
            # If fuzzy prompt not available, fallback to path picker
            input_path = inquirer.filepath(
                message="Select a video file to trim:",
                default=args.directory,
                validate=PathValidator(is_file=True, message="Input must be a file"),
                only_files=False,
            ).execute()

    if not input_path or not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
        return

    try:
        output_file = trim_video(
            input_path=input_path,
            output_path=args.output,
            start_time=args.start,
            end_time=args.end,
            reencode=args.reencode,
        )
        print(f"Successfully trimmed video to {output_file}")
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
    except (ValueError, subprocess.CalledProcessError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
