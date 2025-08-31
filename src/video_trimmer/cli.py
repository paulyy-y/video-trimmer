import argparse
from .core import trim_video


def main():
    parser = argparse.ArgumentParser(description="Trim a video file.")
    parser.add_argument("input_path", help="Path to the input video file.")
    parser.add_argument(
        "start_time", help="Start time for the trim (SS, MM:SS, or HH:MM:SS)."
    )
    parser.add_argument(
        "end_time", help="End time for the trim (SS, MM:SS, or HH:MM:SS)."
    )
    parser.add_argument("-o", "--output", help="Path to the output video file.")
    parser.add_argument(
        "--reencode",
        action="store_true",
        help="Re-encode the video for frame-accurate trimming.",
    )

    args = parser.parse_args()

    try:
        output_file = trim_video(
            input_path=args.input_path,
            start_time=args.start_time,
            end_time=args.end_time,
            output_path=args.output,
            reencode=args.reencode,
        )
        print(f"Successfully trimmed video to {output_file}")
    except FileNotFoundError:
        print(f"Error: Input file not found at {args.input_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
