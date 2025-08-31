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
