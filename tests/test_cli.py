import sys
from pathlib import Path

import video_trimmer.cli as cli


def test_cli_auto_output_omitted(monkeypatch, tmp_path, capsys):
    # Create a dummy input file to satisfy existence check
    input_file = tmp_path / "clip.mkv"
    input_file.write_bytes(b"fake")

    # Stub trim_video to capture arguments and return a deterministic path
    captured = {}

    def fake_trim_video(
        input_path, output_path, start_time, end_time, reencode, burn_subtitles=False
    ):
        captured.update(
            {
                "input_path": input_path,
                "output_path": output_path,
                "start_time": start_time,
                "end_time": end_time,
                "reencode": reencode,
                "burn_subtitles": burn_subtitles,
            }
        )
        return str(Path(input_path).with_name("result.mkv"))

    monkeypatch.setattr(cli, "trim_video", fake_trim_video)

    argv = [
        "video-trimmer",
        "-i",
        str(input_file),
        "-s",
        "2",
        "-e",
        "9",
    ]

    monkeypatch.setattr(sys, "argv", argv)

    cli.main()

    # No output provided; CLI should pass None to core
    assert captured["output_path"] is None
    assert captured["input_path"] == str(input_file)
    assert captured["start_time"] == "2"
    assert captured["end_time"] == "9"

    out = capsys.readouterr().out
    assert "Successfully trimmed video to" in out
    assert "result.mkv" in out


def test_cli_upload_stream_only_deletes_local(monkeypatch, tmp_path, capsys):
    input_file = tmp_path / "clip.mkv"
    input_file.write_bytes(b"fake")

    # Create a fake trimmed output in same dir
    trimmed = tmp_path / "result.mkv"
    trimmed.write_bytes(b"x")

    def fake_trim_video(
        input_path, output_path, start_time, end_time, reencode, burn_subtitles=False
    ):
        return str(trimmed)

    class DummyPayload(dict):
        pass

    def fake_upload_to_stream(file_path, name=None):
        assert Path(file_path) == trimmed
        return {"success": True, "result": {"uid": "uid123"}}

    monkeypatch.setattr(cli, "trim_video", fake_trim_video)
    monkeypatch.setattr(cli, "upload_to_cloudflare_stream", fake_upload_to_stream)

    argv = [
        "video-trimmer",
        "-i",
        str(input_file),
        "-s",
        "0:02",
        "-e",
        "0:09",
        "--upload-stream-only",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    cli.main()

    # Local file should be removed after upload
    assert not trimmed.exists()


def test_list_video_files_filters_and_sorts(tmp_path):
    v1 = tmp_path / "B.mp4"
    v2 = tmp_path / "a.MKV"
    n1 = tmp_path / "notes.txt"
    sub = tmp_path / "sub"
    sub.mkdir()
    v3 = sub / "c.webm"

    for p in [v1, v2, n1, v3]:
        p.write_bytes(b"x")

    list_video_files = getattr(cli, "list_video_files")
    results = list_video_files(str(tmp_path))
    # Should include only video files, sorted case-insensitively
    assert [Path(r).name for r in results] == ["a.MKV", "B.mp4", "c.webm"]
