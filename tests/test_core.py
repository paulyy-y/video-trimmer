from pathlib import Path
import types

import video_trimmer.core as core


def test_trim_video_default_output_naming(tmp_path, monkeypatch):
    # Create a dummy input file
    input_file = tmp_path / "sample video.mp4"
    input_file.write_bytes(b"fake")

    called = {}

    def fake_run(cmd, check):
        called["cmd"] = cmd
        called["check"] = check
        return types.SimpleNamespace(returncode=0)

    monkeypatch.setattr(core.subprocess, "run", fake_run)

    # No output path provided -> auto naming
    out_path = core.trim_video(
        input_path=str(input_file), start_time="1", end_time="65", output_path=None
    )

    # Expect 'sample video_trim_000001-000105.mp4'
    expected_name = "sample video_trim_000001-000105.mp4"
    assert Path(out_path).name == expected_name

    # Validate ffmpeg command includes correct -ss/-to and paths
    cmd = called["cmd"]
    assert cmd[:2] == ["ffmpeg", "-y"]
    assert "-ss" in cmd and "-to" in cmd
    assert str(input_file) in cmd
    assert out_path in cmd


def test_trim_video_burn_subtitles_forces_reencode(tmp_path, monkeypatch):
    input_file = tmp_path / "movie.mp4"
    input_file.write_bytes(b"x")

    # Create sidecar subtitle
    srt = tmp_path / "movie.srt"
    srt.write_text(
        """1
00:00:01,000 --> 00:00:02,000
hi
"""
    )

    called = {}

    def fake_run(cmd, check):
        called["cmd"] = cmd
        return types.SimpleNamespace(returncode=0)

    monkeypatch.setattr(core.subprocess, "run", fake_run)

    _ = core.trim_video(
        input_path=str(input_file),
        start_time="0:01",
        end_time="0:05",
        burn_subtitles=True,
    )

    cmd = called["cmd"]
    # Should include libx264 (reencode) and -vf subtitles
    assert "-c:v" in cmd and "libx264" in cmd
    assert "-vf" in cmd
    # Should preserve timestamps and reset at output
    assert "-copyts" in cmd
    assert "-start_at_zero" in cmd
    # Verify filter references the sidecar file
    vf_idx = cmd.index("-vf")
    assert "subtitles=" in cmd[vf_idx + 1]
    assert "movie.srt" in cmd[vf_idx + 1]
