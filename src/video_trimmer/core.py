import subprocess
from pathlib import Path

__all__ = ["to_hhmmss", "trim_video"]


def to_hhmmss(t: str) -> str:
    """
    Accepts 'SS', 'MM:SS', or 'HH:MM:SS' and normalizes to HH:MM:SS.
    """
    parts = t.split(":")
    if len(parts) == 1:
        s = int(parts[0])
        return f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}"
    if len(parts) == 2:
        m, s = map(int, parts)
        return f"{m//60:02d}:{m%60:02d}:{s:02d}"
    if len(parts) == 3:
        h, m, s = map(int, parts)
        return f"{h:02d}:{m:02d}:{s:02d}"
    raise ValueError("Time format must be 'SS', 'MM:SS', or 'HH:MM:SS'")


def trim_video(
    input_path: str,
    start_time: str,
    end_time: str,
    output_path: str | None = None,
    reencode: bool = False,
) -> str:
    """
    Trim video to [start_time, end_time). Times accept 'SS', 'MM:SS', 'HH:MM:SS'.

    If reencode=False, uses stream copy (fast, keyframe-limited precision).
    If reencode=True, re-encodes (slower but frame-accurate).
    """
    inp = Path(input_path)
    if not inp.exists():
        raise FileNotFoundError(inp)

    ss = to_hhmmss(start_time)
    to = to_hhmmss(end_time)

    if output_path is None:
        out = inp.with_name(
            f"{inp.stem}_trim_{ss.replace(':','')}-{to.replace(':','')}{inp.suffix}"
        )
    else:
        out = Path(output_path)

    # Build ffmpeg command
    # -ss before -i is fast seek; -to sets absolute end time (not duration).
    # For copy mode: -c copy. For reencode: pick sane codecs (libx264/aac).
    cmd = ["ffmpeg", "-y", "-ss", ss, "-to", to, "-i", str(inp)]
    if reencode:
        cmd += ["-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart"]
    else:
        cmd += ["-c", "copy"]
    cmd.append(str(out))

    # Run
    subprocess.run(cmd, check=True)
    return str(out)
